"""Financial Named Entity Recognition (NER) and Quantitative Value Extraction."""
import re
from typing import Dict, Any, List

REGULATORS = ["SEBI", "RBI", "CCI", "NCLT", "ED", "IT DEPT", "SFIO", "GOVERNMENT OF INDIA", "MINISTRY OF POWER", "NTPC"]

class FinancialEntityExtractor:
    """Extracts financial entities, monetary values, percentages, and institutions from text."""

    def extract(self, text: str) -> Dict[str, Any]:
        entities: Dict[str, List[str]] = {
            "monetary_values": [],
            "percentages": [],
            "regulators": [],
            "executives": [],
            "counterparties": []
        }

        # 1. Monetary figures (e.g. ₹1,200 crore, $50 million, Rs 850 cr)
        money_matches = re.findall(
            r"(?:₹|rs\.?|inr|\$)\s*[\d,]+(?:\.\d+)?\s*(?:crore|cr|lakh|mn|billion|million)?",
            text,
            flags=re.IGNORECASE
        )
        entities["monetary_values"] = [m.strip() for m in money_matches[:5]]

        # 2. Percentages (e.g. 15.5%, 48 pct)
        pct_matches = re.findall(r"[\d]+(?:\.\d+)?\s*(?:%|percent|pct)", text, flags=re.IGNORECASE)
        entities["percentages"] = [p.strip() for p in pct_matches[:5]]

        # 3. Regulators and agencies
        text_upper = text.upper()
        for reg in REGULATORS:
            if re.search(rf"\b{reg}\b", text_upper):
                entities["regulators"].append(reg)

        # 4. Common executive titles
        exec_matches = re.findall(r"(?:ceo|md|cfo|chairman|director)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)", text)
        entities["executives"] = [e.strip() for e in exec_matches[:3]]

        # 5. Counterparties (partners, clients)
        counter_matches = re.findall(r"(?:partnership with|order from|agreement with|supplies to)\s+([A-Z][a-zA-Z0-9\s&]+?)(?:\.|,|\s+for|\s+to)", text)
        entities["counterparties"] = [c.strip() for c in counter_matches[:3]]

        return entities

entity_extractor = FinancialEntityExtractor()
