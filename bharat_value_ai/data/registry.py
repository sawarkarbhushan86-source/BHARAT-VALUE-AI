"""Master Company & Financial Sector Registry."""
from typing import Dict, Any, List, Optional
from bharat_value_ai.data.universe import get_complete_universe
from bharat_value_ai.data.normalization import normalize_symbol

# Financial sector industries where debt is an operating asset (Banks & NBFCs)
FINANCIAL_SECTOR_INDUSTRIES = {
    "Private Sector Bank",
    "Public Sector Bank",
    "Housing Finance",
    "Non Banking Financial Company (NBFC)",
    "Microfinance",
}

class CompanyRegistry:
    """Master registry connecting canonical IDs, exchange symbols, and sector classifications."""

    def __init__(self):
        self._by_symbol: Dict[str, Dict[str, Any]] = {}
        self._alias_map: Dict[str, str] = {}
        self._build_registry()

    def _build_registry(self):
        raw_universe = get_complete_universe()
        for item in raw_universe:
            sym = item["symbol"].upper()
            industry = item.get("industry", "")
            sector = item.get("sector", "")
            is_financial = (
                industry in FINANCIAL_SECTOR_INDUSTRIES or
                "Bank" in item.get("name", "") or
                sym in {"ICICIBANK", "HDFCBANK", "SBIN", "KOTAKBANK", "AXISBANK", "IDFCFIRSTB", "CREDITACC", "MANAPPURAM", "BAJFINANCE"}
            )

            canonical_entry = {
                "canonical_id": f"NSE:{sym}",
                "symbol": sym,
                "name": item.get("name", sym),
                "nse_symbol": sym,
                "bse_code": item.get("bse_code", ""),
                "isin": item.get("isin", ""),
                "sector": sector,
                "industry": industry,
                "is_financial": is_financial,
                "market_cap_category": item.get("market_cap_category", "Smallcap"),
                "market_cap_cr": item.get("market_cap_cr", 0.0),
                "description": item.get("description", "")
            }
            self._by_symbol[sym] = canonical_entry

            # Register standard aliases
            self._alias_map[sym.lower()] = sym
            self._alias_map[item.get("name", "").lower()] = sym
            if item.get("bse_code"):
                self._alias_map[item["bse_code"]] = sym
            if item.get("isin"):
                self._alias_map[item["isin"].lower()] = sym

        # Add common market shorthand aliases
        extra_aliases = {
            "hdfc": "HDFCBANK",
            "hdfc bank": "HDFCBANK",
            "icici": "ICICIBANK",
            "icici bank": "ICICIBANK",
            "reliance": "RELIANCE",
            "ril": "RELIANCE",
            "tcs": "TCS",
            "tata consultancy": "TCS",
            "l&t": "LT",
            "larsen": "LT",
            "larsen & toubro": "LT",
            "angel one": "ANGELONE",
            "angel": "ANGELONE",
            "suzlon": "SUZLON",
            "cdsl": "CDSL",
            "birlasoft": "BSOFT"
        }
        for alias, target in extra_aliases.items():
            self._alias_map[alias.lower()] = target

    def get_company(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Lookup by symbol or alias."""
        if not symbol:
            return None
        from bharat_value_ai.data.canonical_resolver import resolve_canonical_symbol
        norm = resolve_canonical_symbol(symbol).upper()
        if norm in self._by_symbol:
            return self._by_symbol[norm].copy()

        # Check alias
        lookup = symbol.strip().lower()
        if lookup in self._alias_map:
            target_sym = self._alias_map[lookup]
            return self._by_symbol.get(target_sym, {}).copy()

        return None

    def is_financial_institution(self, symbol: str) -> bool:
        """Determines if the company is a Bank, NBFC, or financial utility requiring equity/PB valuation."""
        comp = self.get_company(symbol)
        if comp:
            return bool(comp.get("is_financial", False))
        return False

    def get_all_companies(self) -> List[Dict[str, Any]]:
        """Return list of all registered companies."""
        return list(self._by_symbol.values())

company_registry = CompanyRegistry()
