"""Financial Event Classification Pipeline (16 Financial Event Categories)."""
import re
from typing import Dict, Any, List

EVENT_RULES = [
    (
        "EARNINGS_BEAT",
        [r"profit\s+(surges?|jumps?|up|rises?|beats?)", r"q[1-4]\s+net\s+(up|rises?|jumps?)", r"ebitda\s+(beats?|up)"],
        "Company reported quarterly earnings or revenue exceeding consensus expectations."
    ),
    (
        "EARNINGS_MISS",
        [r"profit\s+(falls?|slumps?|drops?|misses?|down)", r"net\s+loss", r"q[1-4]\s+profit\s+declines?"],
        "Reported net profit or operating margin declined or missed market estimates."
    ),
    (
        "ORDER_WIN",
        [
            r"bags?.*?(order|contract|deal|mw)",
            r"secures?.*?(order|contract|deal|mw)",
            r"awarded.*?(contract|order|deal)",
            r"wins?.*?(order|contract|deal|₹|\$)"
        ],
        "Secured a commercial or government contract, expanding the order book."
    ),
    (
        "CAPEX_EXPANSION",
        [r"capacity\s+expansion", r"gigafactory", r"sets?\s+up\s+plant", r"capex\s+of", r"invests?\s+₹?\d+\s+cr"],
        "Announced capital expenditure or capacity expansion to drive future production volume."
    ),
    (
        "ACQUISITION_MERGER",
        [r"acquires?", r"acquisition", r"merger", r"buys?\s+stake", r"takeover"],
        "Strategic inorganic growth through mergers, acquisitions, or controlling stake purchase."
    ),
    (
        "REGULATORY_ACTION",
        [r"sebi", r"rbi", r"show\s*cause", r"penalty", r"fine\s+imposed", r"regulatory\s+ban"],
        "Regulatory inspection, penalty, or show-cause notice from statutory bodies (SEBI, RBI, etc.)."
    ),
    (
        "LITIGATION_LEGAL",
        [r"court", r"nclt", r"lawsuit", r"litigation", r"tribunal", r"dispute"],
        "Legal dispute, NCLT proceedings, or court hearings with potential balance-sheet impact."
    ),
    (
        "FRAUD_ACCOUNTING",
        [r"fraud", r"forgery", r"scam", r"raids?", r"forensic\s+audit", r"sfo"],
        "Allegations of financial irregularities, forensic audit, or governance concerns."
    ),
    (
        "MANAGEMENT_CHANGE",
        [r"ceo\s+resigns?", r"md\s+resigns?", r"new\s+ceo", r"steps?\s+down", r"management\s+reshuffle"],
        "Leadership transition, executive departure, or board composition change."
    ),
    (
        "FUNDRAISING_DILUTION",
        [r"qip", r"rights\s+issue", r"preferential\s+allotment", r"raises?\s+capital", r"fundraising"],
        "Capital raising through equity dilution (QIP, rights issue) or warrant issuance."
    ),
    (
        "PROMOTER_PLEDGE",
        [r"pledges?\s+shares", r"promoter\s+pledge", r"revocation\s+of\s+pledge", r"encumbered\s+shares"],
        "Creation or release of promoter share pledge affecting risk exposure."
    ),
    (
        "DEBT_RESTRUCTURING",
        [r"default", r"debt\s+restructuring", r"ots", r"one\s+time\s+settlement", r"prepays?\s+debt"],
        "Debt default, loan prepayment, or lender debt restructuring scheme."
    ),
    (
        "PRODUCT_LAUNCH",
        [r"launches?", r"unveils?", r"rolls?\s+out", r"new\s+product", r"patent\s+granted"],
        "Commercial rollout of a new product, formulation, or proprietary technology."
    ),
    (
        "DIVIDEND_BUYBACK",
        [r"dividend", r"share\s+buyback", r"bonus\s+issue", r"interim\s+dividend"],
        "Shareholder wealth distribution via cash dividend, bonus shares, or tender buyback."
    ),
    (
        "INDUSTRY_POLICY",
        [r"policy", r"gst\s+rate", r"import\s+duty", r"customs\s+duty", r"pli\s+scheme"],
        "Government policy shift, PLI scheme incentive, or tariff alteration affecting sector dynamics."
    )
]

class EventClassifier:
    """Classifies news articles and disclosures into 16 standardized institutional event types."""

    def classify(self, text: str) -> Dict[str, Any]:
        text_lower = text.lower()
        matched_category = "GENERAL_MARKET"
        description = "General financial market news, commentary, or price movement report."
        confidence = 0.65

        for category, patterns, desc in EVENT_RULES:
            for pat in patterns:
                if re.search(pat, text_lower):
                    matched_category = category
                    description = desc
                    confidence = 0.92
                    return {
                        "event_category": matched_category,
                        "description": description,
                        "confidence": confidence,
                        "trigger_pattern": pat
                    }

        return {
            "event_category": matched_category,
            "description": description,
            "confidence": confidence,
            "trigger_pattern": "none"
        }

event_classifier = EventClassifier()
