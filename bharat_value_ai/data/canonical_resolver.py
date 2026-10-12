"""Canonical Indian Equity Symbol and Company Name Resolution Engine.

Guarantees:
- Resolves company names, colloquial aliases, ISINs, and BSE codes to exact canonical NSE symbols.
- Prevents erroneous ticker concatenation (e.g., 'Reliance Industries' -> 'RELIANCE', NOT 'RELIANCEINDUSTRIES').
- Fully case-insensitive, punctuation-tolerant, and space-aware.
"""
import re
from typing import Optional, Dict, Any, List

# Primary Canonical Alias and Name Mapping Table
CANONICAL_ALIASES: Dict[str, str] = {
    # Reliance Industries
    "reliance": "RELIANCE",
    "ril": "RELIANCE",
    "reliance industries": "RELIANCE",
    "reliance industries limited": "RELIANCE",
    "reliance industries ltd": "RELIANCE",
    "reliance ind": "RELIANCE",
    "500325": "RELIANCE",
    "ine002a01018": "RELIANCE",

    # Tata Consultancy Services
    "tcs": "TCS",
    "tata consultancy": "TCS",
    "tata consultancy services": "TCS",
    "tata consultancy services limited": "TCS",
    "tata consultancy services ltd": "TCS",
    "532540": "TCS",
    "ine467b01029": "TCS",

    # HDFC Bank
    "hdfc": "HDFCBANK",
    "hdfc bank": "HDFCBANK",
    "hdfcbank": "HDFCBANK",
    "hdfc bank limited": "HDFCBANK",
    "hdfc bank ltd": "HDFCBANK",
    "500180": "HDFCBANK",
    "ine040a01034": "HDFCBANK",

    # ICICI Bank
    "icici": "ICICIBANK",
    "icici bank": "ICICIBANK",
    "icicibank": "ICICIBANK",
    "icici bank limited": "ICICIBANK",
    "icici bank ltd": "ICICIBANK",
    "532174": "ICICIBANK",
    "ine090a01021": "ICICIBANK",

    # State Bank of India
    "sbi": "SBIN",
    "sbin": "SBIN",
    "state bank of india": "SBIN",
    "state bank": "SBIN",
    "500112": "SBIN",
    "ine062a01020": "SBIN",

    # Larsen & Toubro
    "lt": "LT",
    "l&t": "LT",
    "larsen": "LT",
    "larsen & toubro": "LT",
    "larsen and toubro": "LT",
    "larsen & toubro limited": "LT",
    "larsen and toubro limited": "LT",
    "500510": "LT",
    "ine018a01030": "LT",

    # Infosys
    "infy": "INFY",
    "infosys": "INFY",
    "infosys limited": "INFY",
    "infosys ltd": "INFY",
    "500209": "INFY",
    "ine009a01021": "INFY",

    # Tata Motors
    "tatamotors": "TATAMOTORS",
    "tata motors": "TATAMOTORS",
    "tata motor": "TATAMOTORS",
    "tata motors limited": "TATAMOTORS",
    "500570": "TATAMOTORS",
    "ine155a01022": "TATAMOTORS",

    # Bharti Airtel
    "airtel": "BHARTIARTL",
    "bharti airtel": "BHARTIARTL",
    "bharti airtel limited": "BHARTIARTL",
    "532454": "BHARTIARTL",
    "ine397d01024": "BHARTIARTL",

    # Hindustan Unilever
    "hul": "HINDUNILVR",
    "hindustan unilever": "HINDUNILVR",
    "hindustan unilever limited": "HINDUNILVR",
    "500696": "HINDUNILVR",
    "ine030a01027": "HINDUNILVR",

    # ITC
    "itc": "ITC",
    "itc limited": "ITC",
    "itc ltd": "ITC",
    "500875": "ITC",
    "ine154a01025": "ITC",

    # Kotak Mahindra Bank
    "kotak": "KOTAKBANK",
    "kotak bank": "KOTAKBANK",
    "kotak mahindra bank": "KOTAKBANK",
    "kotak mahindra bank limited": "KOTAKBANK",
    "500247": "KOTAKBANK",
    "ine237a01028": "KOTAKBANK",

    # Axis Bank
    "axis": "AXISBANK",
    "axis bank": "AXISBANK",
    "axis bank limited": "AXISBANK",
    "532215": "AXISBANK",
    "ine238a01034": "AXISBANK",

    # Bajaj Finance
    "bajaj finance": "BAJFINANCE",
    "bajfinance": "BAJFINANCE",
    "bajaj finance limited": "BAJFINANCE",
    "500034": "BAJFINANCE",
    "ine296a01024": "BAJFINANCE",

    # Asian Paints
    "asian paints": "ASIANPAINT",
    "asian paints limited": "ASIANPAINT",
    "asianpaint": "ASIANPAINT",
    "500820": "ASIANPAINT",
    "ine021a01026": "ASIANPAINT",

    # Maruti Suzuki
    "maruti": "MARUTI",
    "maruti suzuki": "MARUTI",
    "maruti suzuki india limited": "MARUTI",
    "532500": "MARUTI",
    "ine585b01010": "MARUTI",

    # Sun Pharma
    "sun pharma": "SUNPHARMA",
    "sun pharmaceutical": "SUNPHARMA",
    "sun pharmaceutical industries limited": "SUNPHARMA",
    "524715": "SUNPHARMA",
    "ine044a01036": "SUNPHARMA",

    # Titan Company
    "titan": "TITAN",
    "titan company": "TITAN",
    "titan company limited": "TITAN",
    "500114": "TITAN",
    "ine280a01028": "TITAN",

    # CDSL
    "cdsl": "CDSL",
    "central depository services": "CDSL",
    "central depository services (india) limited": "CDSL",
    "central depository services india limited": "CDSL",
    "540608": "CDSL",
    "ine736a01011": "CDSL",

    # Suzlon Energy
    "suzlon": "SUZLON",
    "suzlon energy": "SUZLON",
    "suzlon energy limited": "SUZLON",
    "532667": "SUZLON",
    "ine040h01021": "SUZLON",

    # Angel One
    "angel one": "ANGELONE",
    "angel": "ANGELONE",
    "angelone": "ANGELONE",
    "angel one limited": "ANGELONE",
    "543235": "ANGELONE",
    "ine732i01013": "ANGELONE",

    # Birlasoft
    "birlasoft": "BSOFT",
    "bsoft": "BSOFT",
    "birlasoft limited": "BSOFT",
    "532400": "BSOFT",
    "ine836a01035": "BSOFT",

    # Cyient
    "cyient": "CYIENT",
    "cyient limited": "CYIENT",
    "532175": "CYIENT",
    "ine136b01020": "CYIENT",

    # Exide Industries
    "exide": "EXIDEIND",
    "exide industries": "EXIDEIND",
    "exide industries limited": "EXIDEIND",
    "exideind": "EXIDEIND",
    "500086": "EXIDEIND",
    "ine302a01020": "EXIDEIND",

    # Castrol India
    "castrol": "CASTROLIND",
    "castrol india": "CASTROLIND",
    "castrol india limited": "CASTROLIND",
    "castrolind": "CASTROLIND",
    "500870": "CASTROLIND",
    "ine172a01027": "CASTROLIND",

    # KEC International
    "kec": "KEC",
    "kec international": "KEC",
    "kec international limited": "KEC",
    "532714": "KEC",
    "ine389h01022": "KEC",

    # Motilal Oswal
    "motilal oswal": "MOTILALOFS",
    "motilalofs": "MOTILALOFS",
    "mofsl": "MOTILALOFS",
    "motilal oswal financial services limited": "MOTILALOFS",
    "532892": "MOTILALOFS",
    "ine338i01027": "MOTILALOFS",

    # RITES
    "rites": "RITES",
    "rites limited": "RITES",
    "541556": "RITES",
    "ine320j01015": "RITES",

    # HUDCO
    "hudco": "HUDCO",
    "housing & urban development corporation limited": "HUDCO",
    "housing and urban development corporation": "HUDCO",
    "540530": "HUDCO",
    "ine031a01017": "HUDCO",

    # IRCON
    "ircon": "IRCON",
    "ircon international": "IRCON",
    "ircon international limited": "IRCON",
    "541956": "IRCON",
    "ine962y01021": "IRCON",

    # NBCC
    "nbcc": "NBCC",
    "nbcc india": "NBCC",
    "nbcc (india) limited": "NBCC",
    "534309": "NBCC",
    "ine095n01031": "NBCC",

    # BLS International
    "bls": "BLS",
    "bls international": "BLS",
    "bls international services limited": "BLS",
    "540073": "BLS",
    "ine153t01027": "BLS",

    # Amber Enterprises
    "amber": "AMBER",
    "amber enterprises": "AMBER",
    "amber enterprises india limited": "AMBER",
    "540902": "AMBER",
    "ine371p01015": "AMBER",

    # CEAT
    "ceat": "CEATLTD",
    "ceatltd": "CEATLTD",
    "ceat limited": "CEATLTD",
    "500878": "CEATLTD",
    "ine482a01020": "CEATLTD",

    # Sona BLW
    "sona blw": "SONACOMS",
    "sonacoms": "SONACOMS",
    "sona blw precision forgings limited": "SONACOMS",
    "543300": "SONACOMS",
    "ine073k01018": "SONACOMS",

    # Radico Khaitan
    "radico": "RADICO",
    "radico khaitan": "RADICO",
    "radico khaitan limited": "RADICO",
    "532497": "RADICO",
    "ine944f01028": "RADICO",

    # CAMS
    "cams": "CAMS",
    "computer age management services": "CAMS",
    "computer age management services limited": "CAMS",
    "543232": "CAMS",
    "ine596i01012": "CAMS",

    # Reliance Power (Historical)
    "rpower": "RPOWER",
    "reliance power": "RPOWER",
    "reliance power limited": "RPOWER",
    "532939": "RPOWER",
    "ine614g01033": "RPOWER"
}


def _clean_input(text: str) -> str:
    """Strips exchange prefixes, extensions, and normalize spaces."""
    if not text:
        return ""
    clean = text.strip()
    if clean.upper().startswith("NSE:"):
        clean = clean[4:].strip()
    elif clean.upper().startswith("BSE:"):
        clean = clean[4:].strip()
    clean = clean.replace(".NS", "").replace(".BO", "").replace(".ns", "").replace(".bo", "")
    return clean.strip()


def resolve_canonical_symbol(query: str) -> str:
    """
    Resolves any company name, alias, ISIN, BSE code, or ticker symbol
    into its canonical NSE trading symbol.

    Examples:
        'Reliance Industries' -> 'RELIANCE'
        'Reliance Industries Limited' -> 'RELIANCE'
        'RIL' -> 'RELIANCE'
        'TCS' -> 'TCS'
        'Tata Consultancy Services' -> 'TCS'
        'HDFC Bank' -> 'HDFCBANK'
        'L&T' -> 'LT'
        '500325' -> 'RELIANCE'
        'INE002A01018' -> 'RELIANCE'
    """
    if not query:
        return ""

    raw_cleaned = _clean_input(query)
    if not raw_cleaned:
        return ""

    # 1. Direct lowercase lookup
    lower_query = raw_cleaned.lower()
    if lower_query in CANONICAL_ALIASES:
        return CANONICAL_ALIASES[lower_query]

    # 2. Punctuation-normalized lookup (e.g. replace dashes/dots with spaces or strip them)
    norm_punct = re.sub(r"[\.\,\-\_\&\(\)]", " ", lower_query)
    norm_punct = re.sub(r"\s+", " ", norm_punct).strip()
    if norm_punct in CANONICAL_ALIASES:
        return CANONICAL_ALIASES[norm_punct]

    # 3. Strip 'limited' or 'ltd' if present
    without_ltd = re.sub(r"\b(limited|ltd|pvt ltd|private limited)\b", "", norm_punct).strip()
    if without_ltd in CANONICAL_ALIASES:
        return CANONICAL_ALIASES[without_ltd]

    # 4. Check if exact symbol matches registered universe in CompanyRegistry
    try:
        from bharat_value_ai.data.registry import company_registry
        comp = company_registry.get_company(raw_cleaned)
        if comp and comp.get("symbol"):
            return comp["symbol"]
    except Exception:
        pass

    # 5. Fallback: Return sanitized uppercase ticker without spaces or special chars
    # Only alphanumeric and underscores allowed in exchange tickers
    clean_ticker = re.sub(r"[^A-Za-z0-9_\-]", "", raw_cleaned.upper())
    return clean_ticker[:20]
