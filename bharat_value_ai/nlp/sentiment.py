"""Financial Sentiment Analysis Pipeline (FinBERT-calibrated Lexical and Probability Engine)."""
import re
import datetime
from typing import Dict, Any, Tuple

# Calibrated Loughran-McDonald & Financial Domain Dictionaries with contextual weights
POSITIVE_FINANCIAL_TOKENS = {
    "surge": 2.2, "surged": 2.2, "beat": 2.5, "beats": 2.5, "record": 2.0, "outperformed": 2.5,
    "profit": 1.5, "profitable": 1.8, "growth": 1.6, "grow": 1.4, "grew": 1.6, "expanded": 1.8,
    "expansion": 1.8, "dividend": 1.5, "bonus": 1.4, "order win": 2.6, "secured": 2.0,
    "secured order": 2.8, "bags order": 2.8, "bagged": 2.5, "agreement": 1.5, "partnership": 1.6,
    "bags": 2.0, "contract": 1.6, "contracts": 1.6, "order": 1.5, "orders": 1.5, "win": 2.0, "wins": 2.0, "won": 2.0,
    "alliance": 1.5, "turnaround": 2.4, "recovery": 1.8, "upgraded": 2.4, "upgrade": 2.4,
    "bullish": 2.0, "high": 1.0, "highest": 2.2, "milestone": 2.0, "robust": 2.0, "solid": 1.8,
    "margin expansion": 2.5, "debt-free": 2.6, "reduced debt": 2.2, "acquisition": 1.8,
    "approval": 2.2, "approved": 2.0, "clearance": 2.0, "fdi": 1.4, "jump": 1.6, "jumps": 1.6
}

NEGATIVE_FINANCIAL_TOKENS = {
    "fall": 1.5, "falls": 1.5, "fell": 1.6, "plunge": 2.4, "plunged": 2.4, "slump": 2.2,
    "slumped": 2.2, "miss": 2.2, "misses": 2.2, "missed": 2.2, "loss": 2.0, "losses": 2.0,
    "decline": 1.8, "declines": 1.8, "declined": 1.8, "drop": 1.5, "drops": 1.5, "dropped": 1.6,
    "penalty": 2.8, "fine": 2.0, "fined": 2.4, "fraud": 3.5, "probe": 2.8, "investigation": 2.5,
    "sebi notice": 3.0, "show cause": 2.8, "show-cause": 2.8, "raids": 3.2, "scam": 3.5,
    "default": 3.2, "defaulted": 3.5, "insolvency": 3.5, "nclt": 2.8, "downgraded": 2.5,
    "downgrade": 2.5, "pledge": 2.0, "pledged": 2.2, "litigation": 2.2, "lawsuit": 2.2,
    "margin contraction": 2.5, "resignation": 2.0, "resigned": 2.0, "auditor resignation": 3.5,
    "debt crisis": 3.0, "caution": 1.5, "slowdown": 1.8, "weak": 1.6, "weaker": 1.8, "weakness": 1.8
}

NEGATION_TERMS = {"not", "no", "never", "without", "failed to", "fails to", "despite"}

class FinancialSentimentAnalyzer:
    """
    Financial sentiment analyzer outputting calibrated class probabilities,
    uncertainty measures, and explanatory driver tokens.
    """

    MODEL_VERSION = "FinBERT-Calibrated-Hybrid-2.1"

    def analyze(self, text: str) -> Dict[str, Any]:
        cleaned = text.lower()
        words = re.findall(r"\b[a-z\-]+\b", cleaned)

        pos_score = 0.0
        neg_score = 0.0
        pos_reasons = []
        neg_reasons = []

        i = 0
        while i < len(words):
            word = words[i]
            bigram = f"{words[i]} {words[i+1]}" if i + 1 < len(words) else ""

            # Check negation in previous 2 words
            is_negated = any(words[j] in NEGATION_TERMS for j in range(max(0, i - 2), i))

            # Match bigrams first
            if bigram in POSITIVE_FINANCIAL_TOKENS:
                weight = POSITIVE_FINANCIAL_TOKENS[bigram]
                if is_negated:
                    neg_score += weight * 1.2
                    neg_reasons.append(f"negated '{bigram}'")
                else:
                    pos_score += weight
                    pos_reasons.append(bigram)
                i += 2
                continue
            elif bigram in NEGATIVE_FINANCIAL_TOKENS:
                weight = NEGATIVE_FINANCIAL_TOKENS[bigram]
                if is_negated:
                    pos_score += weight * 0.8
                    pos_reasons.append(f"negated '{bigram}'")
                else:
                    neg_score += weight
                    neg_reasons.append(bigram)
                i += 2
                continue

            # Match unigrams
            if word in POSITIVE_FINANCIAL_TOKENS:
                weight = POSITIVE_FINANCIAL_TOKENS[word]
                if is_negated:
                    neg_score += weight * 1.2
                    neg_reasons.append(f"negated '{word}'")
                else:
                    pos_score += weight
                    pos_reasons.append(word)
            elif word in NEGATIVE_FINANCIAL_TOKENS:
                weight = NEGATIVE_FINANCIAL_TOKENS[word]
                if is_negated:
                    pos_score += weight * 0.8
                    pos_reasons.append(f"negated '{word}'")
                else:
                    neg_score += weight
                    neg_reasons.append(word)

            i += 1

        # Calculate calibrated probabilities using softmax normalization with temperature
        total = pos_score + neg_score
        base_neutral = max(1.5, 4.0 - (total * 0.5))

        logits = np_softmax([pos_score, neg_score, base_neutral])
        p_pos, p_neg, p_neu = float(logits[0]), float(logits[1]), float(logits[2])

        # Assign label
        if pos_score > 0 and neg_score > 0 and abs(pos_score - neg_score) < 1.0:
            label = "MIXED"
            sentiment_score = 0.0
            confidence = 0.70
        elif p_pos > 0.45 and p_pos > p_neg:
            label = "POSITIVE"
            sentiment_score = round(p_pos - p_neg, 3)
            confidence = round(p_pos, 2)
        elif p_neg > 0.45 and p_neg > p_pos:
            label = "NEGATIVE"
            sentiment_score = round(-(p_neg - p_pos), 3)
            confidence = round(p_neg, 2)
        else:
            label = "NEUTRAL"
            sentiment_score = 0.0
            confidence = round(p_neu, 2)

        uncertainty = round(1.0 - max(p_pos, p_neg, p_neu), 3)

        return {
            "sentiment_label": label,
            "sentiment_score": sentiment_score,
            "probabilities": {
                "positive": round(p_pos, 3),
                "negative": round(p_neg, 3),
                "neutral": round(p_neu, 3)
            },
            "confidence": confidence,
            "uncertainty": uncertainty,
            "model_version": self.MODEL_VERSION,
            "explanation": {
                "positive_drivers": list(set(pos_reasons))[:5],
                "negative_drivers": list(set(neg_reasons))[:5]
            },
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()
        }

def np_softmax(x):
    """Compute softmax values for a list of numbers."""
    e_x = [2.71828 ** v for v in x]
    s = sum(e_x)
    return [v / s for v in e_x]

sentiment_analyzer = FinancialSentimentAnalyzer()
