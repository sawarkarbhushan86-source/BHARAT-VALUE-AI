"""News-to-Market Event Study Engine."""
import datetime
from typing import List, Dict, Any
from bharat_value_ai.core.schemas import EventStudyResponse
from bharat_value_ai.data.market_provider import market_provider

SAMPLE_EVENT_STUDIES = [
    {
        "event_id": "ev_01",
        "symbol": "CDSL",
        "event_date": "2024-04-18T10:30:00Z",
        "event_category": "EARNINGS_BEAT",
        "title": "CDSL reports Q4 Net Profit up 44% YoY, announces bonus issue recommendation",
        "reaction_1d_pct": 5.4,
        "reaction_5d_pct": 11.2,
        "reaction_20d_pct": 18.5,
        "benchmark_1d_pct": 0.6,
        "abnormal_return_1d_pct": 4.8,
        "volume_shock_ratio": 3.8
    },
    {
        "event_id": "ev_02",
        "symbol": "SUZLON",
        "event_date": "2024-05-12T14:15:00Z",
        "event_category": "ORDER_WIN",
        "title": "Suzlon Energy bags 402 MW wind energy order from Juniper Green Energy",
        "reaction_1d_pct": 4.9,
        "reaction_5d_pct": 8.4,
        "reaction_20d_pct": 14.2,
        "benchmark_1d_pct": -0.2,
        "abnormal_return_1d_pct": 5.1,
        "volume_shock_ratio": 2.9
    },
    {
        "event_id": "ev_03",
        "symbol": "EXIDEIND",
        "event_date": "2024-04-08T09:45:00Z",
        "event_category": "ACQUISITION_MERGER",
        "title": "Hyundai and Kia sign strategic MoU with Exide Energy for EV battery cells",
        "reaction_1d_pct": 13.2,
        "reaction_5d_pct": 21.0,
        "reaction_20d_pct": 28.4,
        "benchmark_1d_pct": 0.4,
        "abnormal_return_1d_pct": 12.8,
        "volume_shock_ratio": 6.4
    },
    {
        "event_id": "ev_04",
        "symbol": "AMBER",
        "event_date": "2024-02-14T11:00:00Z",
        "event_category": "CAPEX_EXPANSION",
        "title": "Amber Enterprises announces ₹2,000 Cr foray into high-precision electronics and PCB manufacturing",
        "reaction_1d_pct": 8.1,
        "reaction_5d_pct": 12.5,
        "reaction_20d_pct": 19.8,
        "benchmark_1d_pct": 0.1,
        "abnormal_return_1d_pct": 8.0,
        "volume_shock_ratio": 4.1
    }
]

class EventStudyEngine:
    """Measures short and medium-term price and volume abnormal reactions to corporate news events."""

    def get_event_studies(self, symbol: str = None) -> List[EventStudyResponse]:
        studies = []
        for s in SAMPLE_EVENT_STUDIES:
            if symbol and s["symbol"] != symbol.upper().replace(".NS", ""):
                continue
            studies.append(EventStudyResponse(
                event_id=s["event_id"],
                symbol=s["symbol"],
                event_date=datetime.datetime.fromisoformat(s["event_date"].replace("Z", "+00:00")),
                event_category=s["event_category"],
                title=s["title"],
                reaction_1d_pct=s["reaction_1d_pct"],
                reaction_5d_pct=s["reaction_5d_pct"],
                reaction_20d_pct=s["reaction_20d_pct"],
                benchmark_1d_pct=s["benchmark_1d_pct"],
                abnormal_return_1d_pct=s["abnormal_return_1d_pct"],
                volume_shock_ratio=s["volume_shock_ratio"]
            ))
        return studies

event_study_engine = EventStudyEngine()
