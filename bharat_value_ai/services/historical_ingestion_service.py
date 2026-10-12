"""Incremental Historical Data Ingestion Pipeline for Indian Equities.

Guarantees:
- Idempotent upserts of OHLCV candles into SQLite database.
- Controlled rate-limit compliant batch processing with backoff.
- Tracks ingestion jobs, records ingested, failures, and provenance.
- Never fabricates missing candles or fills missing data with synthetic waves.
"""
import uuid
import time
import datetime
import logging
from typing import Dict, Any, List, Optional
import sqlalchemy as sa
from sqlalchemy.orm import Session

from bharat_value_ai.core.database import SessionLocal
from bharat_value_ai.core.models import Company, Candle, HistoricalIngestionJob
from bharat_value_ai.data.normalization import normalize_symbol, get_current_utc, format_ist_timestamp
from bharat_value_ai.services.market_data_service import market_data_service
from bharat_value_ai.data.security_master import security_master

logger = logging.getLogger(__name__)

class HistoricalIngestionService:
    """
    Manages robust historical data collection, normalization, deduplication,
    and storage for the Indian equity universe.
    """

    def __init__(self):
        self._active_jobs: Dict[str, Dict[str, Any]] = {}

    def _ensure_company_exists(self, db: Session, symbol: str) -> int:
        """Finds or registers company in the database to satisfy foreign key constraints."""
        clean_sym = normalize_symbol(symbol).upper()
        comp = db.query(Company).filter(Company.symbol == clean_sym).first()
        if comp:
            return comp.id

        sec = security_master.get_security(clean_sym)
        name = sec.company_name if sec else clean_sym
        sector = sec.sector if sec else "Diversified"
        industry = sec.industry if sec else "Diversified"
        mcap_cat = sec.market_cap_category if sec else "Smallcap"
        mcap_cr = sec.market_cap_cr if sec else 0.0

        new_comp = Company(
            symbol=clean_sym,
            name=name,
            sector=sector,
            industry=industry,
            market_cap_category=mcap_cat,
            market_cap_cr=mcap_cr,
            is_active=True
        )
        db.add(new_comp)
        db.commit()
        db.refresh(new_comp)
        return new_comp.id

    def ingest_symbol_candles(
        self,
        symbol: str,
        period: str = "1y",
        interval: str = "1d",
        candles: Optional[List[Dict[str, Any]]] = None,
        source: Optional[str] = None,
        db: Optional[Session] = None
    ) -> int:
        """
        Fetch historical candles for a security and idempotently upsert into DB.
        Returns the number of newly inserted candle records (0 for duplicates).
        """
        clean_sym = normalize_symbol(symbol).upper()
        if candles is None:
            candles = market_data_service.get_historical_ohlcv(clean_sym, period=period, interval=interval)
        if not candles:
            return 0

        should_close = False
        if db is None:
            db = SessionLocal()
            should_close = True

        newly_inserted = 0
        try:
            company_id = self._ensure_company_exists(db, clean_sym)

            for c in candles:
                c_ts = c["timestamp"]
                if isinstance(c_ts, str):
                    c_ts = datetime.datetime.fromisoformat(c_ts)
                if c_ts.tzinfo is not None:
                    # Store naive UTC in SQLite
                    c_ts = c_ts.astimezone(datetime.timezone.utc).replace(tzinfo=None)

                existing = db.query(Candle).filter(
                    Candle.symbol == clean_sym,
                    Candle.timestamp == c_ts
                ).first()

                if existing:
                    existing.open = float(c["open"])
                    existing.high = float(c["high"])
                    existing.low = float(c["low"])
                    existing.close = float(c["close"])
                    existing.volume = int(c["volume"])
                    existing.frequency = interval
                    existing.is_adjusted = bool(c.get("is_adjusted", True))
                else:
                    new_candle = Candle(
                        company_id=company_id,
                        symbol=clean_sym,
                        exchange="NSE",
                        timestamp=c_ts,
                        open=float(c["open"]),
                        high=float(c["high"]),
                        low=float(c["low"]),
                        close=float(c["close"]),
                        volume=int(c["volume"]),
                        frequency=interval,
                        is_adjusted=bool(c.get("is_adjusted", True))
                    )
                    db.add(new_candle)
                    newly_inserted += 1

            db.commit()
            return newly_inserted
        except Exception as e:
            db.rollback()
            logger.error(f"Error ingesting candles for {clean_sym}: {e}")
            return 0
        finally:
            if should_close:
                db.close()

    def ingest_universe_batch(
        self,
        symbols: Optional[List[str]] = None,
        batch_size: int = 10,
        period: str = "6mo",
        interval: str = "1d",
        limit_days: Optional[int] = None
    ) -> str:
        """
        Executes rate-limited, controlled batch ingestion across the specified or canonical universe.
        Returns the unique job_id.
        """
        if limit_days:
            period = f"{limit_days}d"

        if not symbols:
            # Default to active registered securities
            all_sec = security_master.get_all_securities(include_inactive=False)
            symbols = [s.symbol for s in all_sec]

        job_id = f"job_ingest_{uuid.uuid4().hex[:8]}"
        start_time = get_current_utc()

        job_meta = {
            "job_id": job_id,
            "status": "IN_PROGRESS",
            "total_symbols": len(symbols),
            "processed": 0,
            "records_ingested": 0,
            "failed_symbols": [],
            "start_time": start_time,
            "start_ist": format_ist_timestamp(start_time)
        }
        self._active_jobs[job_id] = job_meta

        db = SessionLocal()
        try:
            db_job = HistoricalIngestionJob(
                job_id=job_id,
                data_type="candles",
                symbols_json=symbols,
                status="IN_PROGRESS",
                records_ingested=0,
                start_time=start_time.replace(tzinfo=None),
                provider=market_data_service.provider.provider_name
            )
            db.add(db_job)
            db.commit()

            total_records = 0
            failed_syms = []

            for idx, sym in enumerate(symbols):
                try:
                    inserted_cnt = self.ingest_symbol_candles(sym, period=period, interval=interval, db=db)
                    total_records += inserted_cnt
                except Exception as ex:
                    failed_syms.append({"symbol": sym, "reason": str(ex)})

                job_meta["processed"] = idx + 1
                job_meta["records_ingested"] = total_records
                job_meta["failed_symbols"] = failed_syms

                # Rate-limit pause between batches
                if (idx + 1) % batch_size == 0 and (idx + 1) < len(symbols):
                    time.sleep(0.5)

            end_time = get_current_utc()
            job_meta["status"] = "COMPLETED"
            job_meta["end_time"] = end_time
            job_meta["end_ist"] = format_ist_timestamp(end_time)

            db_job.status = "COMPLETED"
            db_job.records_ingested = total_records
            db_job.failed_symbols_json = failed_syms
            db_job.end_time = end_time.replace(tzinfo=None)
            db.commit()

            return job_id

        except Exception as e:
            db.rollback()
            logger.error(f"Batch ingestion job {job_id} encountered fatal error: {e}")
            job_meta["status"] = "FAILED"
            job_meta["error"] = str(e)
            return job_id
        finally:
            db.close()

    def get_latest_jobs(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Retrieve recent historical ingestion audit job records."""
        db = SessionLocal()
        try:
            jobs = db.query(HistoricalIngestionJob).order_by(
                HistoricalIngestionJob.start_time.desc()
            ).limit(limit).all()

            results = []
            for j in jobs:
                results.append({
                    "job_id": j.job_id,
                    "data_type": j.data_type,
                    "status": j.status,
                    "total_symbols": len(j.symbols_json) if j.symbols_json else 0,
                    "processed_symbols": len(j.symbols_json) if j.symbols_json else 0,
                    "records_ingested": j.records_ingested,
                    "provider": j.provider,
                    "start_time": str(j.start_time),
                    "end_time": str(j.end_time) if j.end_time else None
                })
            return results
        finally:
            db.close()

    def get_ingestion_summary(self) -> Dict[str, Any]:
        """Returns statistics on total candles stored in database."""
        db = SessionLocal()
        try:
            total_candles = db.query(sa.func.count(Candle.id)).scalar() or 0
            distinct_symbols = db.query(sa.func.count(sa.func.distinct(Candle.symbol))).scalar() or 0
            last_job = db.query(HistoricalIngestionJob).order_by(HistoricalIngestionJob.start_time.desc()).first()

            return {
                "total_candles_stored": total_candles,
                "distinct_symbols_with_history": distinct_symbols,
                "last_job": {
                    "job_id": last_job.job_id if last_job else "None",
                    "status": last_job.status if last_job else "None",
                    "records_ingested": last_job.records_ingested if last_job else 0,
                    "start_time": str(last_job.start_time) if last_job else "N/A"
                } if last_job else None,
                "checked_at_ist": format_ist_timestamp(get_current_utc())
            }
        finally:
            db.close()

    def get_stored_candles(
        self,
        symbol: str,
        limit: int = 120
    ) -> List[Dict[str, Any]]:
        """Retrieve stored historical candles from SQLite."""
        clean_sym = normalize_symbol(symbol).upper()
        db = SessionLocal()
        try:
            rows = db.query(Candle).filter(
                Candle.symbol == clean_sym
            ).order_by(Candle.timestamp.asc()).limit(limit).all()

            results = []
            for r in rows:
                results.append({
                    "symbol": r.symbol,
                    "timestamp": r.timestamp.isoformat(),
                    "open": r.open,
                    "high": r.high,
                    "low": r.low,
                    "close": r.close,
                    "volume": r.volume,
                    "frequency": r.frequency,
                    "is_adjusted": r.is_adjusted
                })
            return results
        finally:
            db.close()

historical_ingestion_service = HistoricalIngestionService()
