"""Tests for Historical Ingestion Pipeline, SQLite Storage, and Deduplication."""
import pytest
from datetime import datetime, timezone
from sqlalchemy import func
from bharat_value_ai.core.database import SessionLocal, init_db
from bharat_value_ai.core.models import Candle, HistoricalIngestionJob
from bharat_value_ai.services.historical_ingestion_service import historical_ingestion_service


@pytest.fixture(autouse=True)
def setup_database():
    init_db()


def test_ingest_symbol_candles_and_idempotency():
    """Verify candle ingestion inserts records and repeated runs do not create duplicates."""
    symbol = "TEST_CDSL"
    mock_candles = [
        {
            "timestamp": "2026-10-08T09:15:00+05:30",
            "open": 1400.0,
            "high": 1420.0,
            "low": 1395.0,
            "close": 1415.0,
            "volume": 25000,
        },
        {
            "timestamp": "2026-10-09T09:15:00+05:30",
            "open": 1415.0,
            "high": 1435.0,
            "low": 1410.0,
            "close": 1430.0,
            "volume": 32000,
        },
    ]

    # Clean up test rows first
    db = SessionLocal()
    try:
        db.query(Candle).filter(Candle.symbol == symbol).delete()
        db.commit()
    finally:
        db.close()

    # First ingestion: should insert 2
    inserted_1 = historical_ingestion_service.ingest_symbol_candles(
        symbol=symbol,
        candles=mock_candles,
        interval="day",
        source="unit_test"
    )
    assert inserted_1 == 2

    db = SessionLocal()
    try:
        count = db.query(Candle).filter(Candle.symbol == symbol).count()
        assert count == 2
    finally:
        db.close()

    # Second ingestion with same timestamps: should insert 0 (idempotency)
    inserted_2 = historical_ingestion_service.ingest_symbol_candles(
        symbol=symbol,
        candles=mock_candles,
        interval="day",
        source="unit_test"
    )
    assert inserted_2 == 0

    db = SessionLocal()
    try:
        count_after = db.query(Candle).filter(Candle.symbol == symbol).count()
        assert count_after == 2  # No duplicate rows created
        db.query(Candle).filter(Candle.symbol == symbol).delete()
        db.commit()
    finally:
        db.close()


def test_ingest_universe_batch_creates_job_record():
    """Verify universe batch ingestion creates an audited job record with status and counts."""
    job_id = historical_ingestion_service.ingest_universe_batch(
        symbols=["CDSL", "RELIANCE"],
        interval="day",
        limit_days=3
    )
    assert job_id.startswith("job_")

    jobs = historical_ingestion_service.get_latest_jobs(limit=5)
    matched = [j for j in jobs if j["job_id"] == job_id]
    assert len(matched) == 1
    job = matched[0]
    assert job["status"] in ["COMPLETED", "FAILED"]
    assert job["total_symbols"] == 2
    assert "processed_symbols" in job
    assert "start_time" in job
