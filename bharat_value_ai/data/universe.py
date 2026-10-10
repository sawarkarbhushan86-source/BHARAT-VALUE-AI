"""Indian Stock Market Universe Master (Nifty Smallcap 100 + Benchmark Leaders)."""
from typing import Dict, Any, List

NIFTY_SMALLCAP_100_CONSTITUENTS: List[Dict[str, Any]] = [
    {
        "symbol": "CDSL",
        "name": "Central Depository Services (India) Limited",
        "bse_code": "540608",
        "isin": "INE736A01011",
        "sector": "Financial Services",
        "industry": "Capital Markets",
        "market_cap_category": "Smallcap",
        "market_cap_cr": 32800.0,
        "description": "Leading depository in India providing dematerialisation and electronic settlement services for retail and institutional investors."
    },
    {
        "symbol": "SUZLON",
        "name": "Suzlon Energy Limited",
        "bse_code": "532667",
        "isin": "INE040H01021",
        "sector": "Capital Goods",
        "industry": "Renewable Energy Equipment",
        "market_cap_category": "Smallcap",
        "market_cap_cr": 78500.0,
        "description": "Renewable energy solutions provider specializing in wind turbine generators and end-to-end solar-wind hybrid projects."
    },
    {
        "symbol": "ANGELONE",
        "name": "Angel One Limited",
        "bse_code": "543235",
        "isin": "INE732I01013",
        "sector": "Financial Services",
        "industry": "Stock Broking",
        "market_cap_category": "Smallcap",
        "market_cap_cr": 24200.0,
        "description": "Leading digital stockbroking fintech firm in India offering retail trading, mutual funds, and digital wealth management."
    },
    {
        "symbol": "BSOFT",
        "name": "Birlasoft Limited",
        "bse_code": "532400",
        "isin": "INE836A01035",
        "sector": "Information Technology",
        "industry": "IT Consulting & Software",
        "market_cap_category": "Smallcap",
        "market_cap_cr": 16400.0,
        "description": "Part of the multi-billion dollar CK Birla Group, providing cloud, digital transformation, and ERP services across enterprise verticals."
    },
    {
        "symbol": "CYIENT",
        "name": "Cyient Limited",
        "bse_code": "532175",
        "isin": "INE136B01020",
        "sector": "Information Technology",
        "industry": "Engineering & Technology Services",
        "market_cap_category": "Smallcap",
        "market_cap_cr": 21800.0,
        "description": "Global engineering, manufacturing, and digital technology solutions company serving aerospace, defense, telecom, and healthcare."
    },
    {
        "symbol": "EXIDEIND",
        "name": "Exide Industries Limited",
        "bse_code": "500086",
        "isin": "INE302A01020",
        "sector": "Automobile and Auto Components",
        "industry": "Auto Parts & Equipment",
        "market_cap_category": "Smallcap",
        "market_cap_cr": 38900.0,
        "description": "Pioneer and market leader in lead-acid storage batteries and lithium-ion gigafactory development for EV and industrial applications."
    },
    {
        "symbol": "CASTROLIND",
        "name": "Castrol India Limited",
        "bse_code": "500870",
        "isin": "INE172A01027",
        "sector": "Oil, Gas & Consumable Fuels",
        "industry": "Lubricants",
        "market_cap_category": "Smallcap",
        "market_cap_cr": 22100.0,
        "description": "Leading automotive and industrial lubricant manufacturer with premium brand equity and strong operating cash flow generation."
    },
    {
        "symbol": "KEC",
        "name": "KEC International Limited",
        "bse_code": "532714",
        "isin": "INE389H01022",
        "sector": "Capital Goods",
        "industry": "Power Transmission & EPC",
        "market_cap_category": "Smallcap",
        "market_cap_cr": 23500.0,
        "description": "Global infrastructure EPC major with presence in power transmission and distribution, railways, civil, urban infrastructure, and cables."
    },
    {
        "symbol": "MOTILALOFS",
        "name": "Motilal Oswal Financial Services Limited",
        "bse_code": "532892",
        "isin": "INE338I01027",
        "sector": "Financial Services",
        "industry": "Investment Banking & Wealth",
        "market_cap_category": "Smallcap",
        "market_cap_cr": 39500.0,
        "description": "Integrated financial services firm offering retail broking, institutional equities, asset management, private equity, and housing finance."
    },
    {
        "symbol": "RITES",
        "name": "RITES Limited",
        "bse_code": "541556",
        "isin": "INE320J01015",
        "sector": "Services",
        "industry": "Consulting Services",
        "market_cap_category": "Smallcap",
        "market_cap_cr": 15800.0,
        "description": "Government-backed engineering consultancy and project management company in railways, highways, ports, ropeways, and export rolling stock."
    },
    {
        "symbol": "HUDCO",
        "name": "Housing & Urban Development Corporation Limited",
        "bse_code": "540530",
        "isin": "INE031A01017",
        "sector": "Financial Services",
        "industry": "Financial Institution",
        "market_cap_category": "Smallcap",
        "market_cap_cr": 45200.0,
        "description": "Premier public sector undertaking providing loans and financial assistance for housing and urban infrastructure projects across India."
    },
    {
        "symbol": "IRCON",
        "name": "Ircon International Limited",
        "bse_code": "541956",
        "isin": "INE962Y01021",
        "sector": "Construction",
        "industry": "Civil Construction",
        "market_cap_category": "Smallcap",
        "market_cap_cr": 20400.0,
        "description": "Specialized railway infrastructure construction company with turnkey execution experience across complex tunnels, bridges, and electrical grids."
    },
    {
        "symbol": "NBCC",
        "name": "NBCC (India) Limited",
        "bse_code": "534309",
        "isin": "INE095N01031",
        "sector": "Construction",
        "industry": "Project Management Consultancy",
        "market_cap_category": "Smallcap",
        "market_cap_cr": 28900.0,
        "description": "Navratna CPSE executing civil engineering, re-development of government housing complexes, and smart city infrastructure."
    },
    {
        "symbol": "BLS",
        "name": "BLS International Services Limited",
        "bse_code": "540073",
        "isin": "INE153T01027",
        "sector": "Services",
        "industry": "Visa & Consular Services",
        "market_cap_category": "Smallcap",
        "market_cap_cr": 14200.0,
        "description": "Global tech-enabled services partner for governments and diplomatic missions, providing visa, passport, and citizen service delivery."
    },
    {
        "symbol": "AMBER",
        "name": "Amber Enterprises India Limited",
        "bse_code": "540902",
        "isin": "INE371P01015",
        "sector": "Consumer Durables",
        "industry": "Air Conditioner OEM/ODM",
        "market_cap_category": "Smallcap",
        "market_cap_cr": 21500.0,
        "description": "Market leader in the Indian room air conditioner OEM/ODM industry with backward integration into PCBAs, motors, and railway electronics."
    },
    {
        "symbol": "CEATLTD",
        "name": "CEAT Limited",
        "bse_code": "500878",
        "isin": "INE482A01020",
        "sector": "Automobile and Auto Components",
        "industry": "Tyres & Rubber Products",
        "market_cap_category": "Smallcap",
        "market_cap_cr": 11500.0,
        "description": "Flagship tyre company of the RPG Group manufacturing tyres for passenger vehicles, two-wheelers, trucks, and farm equipment."
    },
    {
        "symbol": "GLENMARK",
        "name": "Glenmark Pharmaceuticals Limited",
        "bse_code": "532296",
        "isin": "INE935A01035",
        "sector": "Healthcare",
        "industry": "Pharmaceuticals",
        "market_cap_category": "Smallcap",
        "market_cap_cr": 44800.0,
        "description": "Research-led global pharmaceutical firm with key focus on respiratory, dermatology, and oncology therapies across emerging and regulated markets."
    },
    {
        "symbol": "JBCHEPHARM",
        "name": "J.B. Chemicals & Pharmaceuticals Limited",
        "bse_code": "506943",
        "isin": "INE572A01028",
        "sector": "Healthcare",
        "industry": "Pharmaceuticals",
        "market_cap_category": "Smallcap",
        "market_cap_cr": 26900.0,
        "description": "Fast-growing pharma company in domestic formulations, lozenges contract manufacturing, and active pharmaceutical ingredients (APIs)."
    },
    {
        "symbol": "SONACOMS",
        "name": "Sona BLW Precision Forgings Limited",
        "bse_code": "543300",
        "isin": "INE073K01018",
        "sector": "Automobile and Auto Components",
        "industry": "Auto Components & EV Drivelines",
        "market_cap_category": "Smallcap",
        "market_cap_cr": 42100.0,
        "description": "Global automotive technology provider designing precision forged gears, differential assemblies, and traction motors for electric vehicles."
    },
    {
        "symbol": "RADICO",
        "name": "Radico Khaitan Limited",
        "bse_code": "532497",
        "isin": "INE944F01028",
        "sector": "Fast Moving Consumer Goods",
        "industry": "Alcoholic Beverages",
        "market_cap_category": "Smallcap",
        "market_cap_cr": 31000.0,
        "description": "One of India's oldest and largest liquor manufacturers, famous for premium IMFL spirits including Magic Moments, Rampur Single Malt, and Morpheus."
    },
    {
        "symbol": "CAMS",
        "name": "Computer Age Management Services Limited",
        "bse_code": "543232",
        "isin": "INE596I01012",
        "sector": "Financial Services",
        "industry": "Financial Technology & RTA",
        "market_cap_category": "Smallcap",
        "market_cap_cr": 21800.0,
        "description": "India's largest mutual fund transfer agency commanding ~68% AUM market share, with growth engines in CRA, payment aggregator, and AIF services."
    },
    {
        "symbol": "KARURVYSYA",
        "name": "The Karur Vysya Bank Limited",
        "bse_code": "590003",
        "isin": "INE036D01028",
        "sector": "Financial Services",
        "industry": "Private Sector Bank",
        "market_cap_category": "Smallcap",
        "market_cap_cr": 17800.0,
        "description": "Scheduled commercial bank with over a century of heritage, demonstrating superior asset quality, robust ROA, and strong SME franchise."
    },
    {
        "symbol": "EQUITASBNK",
        "name": "Equitas Small Finance Bank Limited",
        "bse_code": "543243",
        "isin": "INE061501017",
        "sector": "Financial Services",
        "industry": "Small Finance Bank",
        "market_cap_category": "Smallcap",
        "market_cap_cr": 10500.0,
        "description": "Small finance bank focusing on microfinance, small business loans, affordable housing, and vehicle finance across semi-urban India."
    },
    {
        "symbol": "DEEPAKFERT",
        "name": "Deepak Fertilisers and Petrochemicals Corp Ltd",
        "bse_code": "500645",
        "isin": "INE501A01019",
        "sector": "Chemicals",
        "industry": "Speciality Chemicals & Fertilisers",
        "market_cap_category": "Smallcap",
        "market_cap_cr": 13900.0,
        "description": "Leading manufacturer of industrial chemicals (Nitric Acid, Technical Ammonium Nitrate) and crop nutrition solutions."
    },
    {
        "symbol": "GNFC",
        "name": "Gujarat Narmada Valley Fertilizers & Chemicals Ltd",
        "bse_code": "500670",
        "isin": "INE113A01013",
        "sector": "Chemicals",
        "industry": "Fertilizers & Industrial Chemicals",
        "market_cap_category": "Smallcap",
        "market_cap_cr": 9800.0,
        "description": "Pioneering producer of fertilizers (Urea, Ammonium Nitro-Phosphate) and chemicals like TDI, Acetic Acid, and Formic Acid."
    },
    {
        "symbol": "HINDCOPPER",
        "name": "Hindustan Copper Limited",
        "bse_code": "513599",
        "isin": "INE531E01026",
        "sector": "Metals & Mining",
        "industry": "Non-Ferrous Metals",
        "market_cap_category": "Smallcap",
        "market_cap_cr": 27500.0,
        "description": "Only vertically integrated copper producer in India holding all active copper mining leases in the country."
    },
    {
        "symbol": "NATIONALUM",
        "name": "National Aluminium Company Limited",
        "bse_code": "532234",
        "isin": "INE139A01034",
        "sector": "Metals & Mining",
        "industry": "Aluminium",
        "market_cap_category": "Smallcap",
        "market_cap_cr": 41200.0,
        "description": "Navratna CPSE engaged in bauxite mining, alumina refining, and aluminium smelting with lowest-cost global operations."
    },
    {
        "symbol": "TATAINVEST",
        "name": "Tata Investment Corporation Limited",
        "bse_code": "501301",
        "isin": "INE672A01018",
        "sector": "Financial Services",
        "industry": "Holding Company & Investments",
        "market_cap_category": "Smallcap",
        "market_cap_cr": 35200.0,
        "description": "Non-banking financial company holding long-term strategic investments in listed and unlisted Tata Group and Indian blue-chip companies."
    },
    {
        "symbol": "TEJASNET",
        "name": "Tejas Networks Limited",
        "bse_code": "540595",
        "isin": "INE010J01012",
        "sector": "Telecommunication",
        "industry": "Telecom Equipment",
        "market_cap_category": "Smallcap",
        "market_cap_cr": 19400.0,
        "description": "Tata Group company designing and manufacturing optical transmission, broadband, and 4G/5G wireless networking gear."
    },
    {
        "symbol": "HBLPOWER",
        "name": "HBL Power Systems Limited",
        "bse_code": "517271",
        "isin": "INE292B01021",
        "sector": "Capital Goods",
        "industry": "Batteries & Railway Electronics",
        "market_cap_category": "Smallcap",
        "market_cap_cr": 14600.0,
        "description": "Manufacturer of specialized batteries and indigenous train collision avoidance systems (Kavach) for Indian Railways."
    },
    {
        "symbol": "KAYNES",
        "name": "Kaynes Technology India Limited",
        "bse_code": "543667",
        "isin": "INE918Z01012",
        "sector": "Capital Goods",
        "industry": "Electronic Manufacturing Services",
        "market_cap_category": "Smallcap",
        "market_cap_cr": 36100.0,
        "description": "End-to-end integrated electronics manufacturing player delivering conceptual design, process engineering, and printed circuit board assembly."
    },
    {
        "symbol": "APARINDS",
        "name": "Apar Industries Limited",
        "bse_code": "532259",
        "isin": "INE372A01015",
        "sector": "Capital Goods",
        "industry": "Cables, Conductors & Oils",
        "market_cap_category": "Smallcap",
        "market_cap_cr": 39800.0,
        "description": "Global leader in high-performance aluminium and alloy conductors, transformer oils, and specialty elastomeric optical cables."
    },
    {
        "symbol": "ELECON",
        "name": "Elecon Engineering Company Limited",
        "bse_code": "505700",
        "isin": "INE205B01023",
        "sector": "Capital Goods",
        "industry": "Industrial Gears & Material Handling",
        "market_cap_category": "Smallcap",
        "market_cap_cr": 14200.0,
        "description": "Pioneer in manufacturing industrial transmission gears and material handling equipment with export presence in Europe and USA."
    },
    {
        "symbol": "TRITURBINE",
        "name": "Triveni Turbine Limited",
        "bse_code": "533655",
        "isin": "INE152M01016",
        "sector": "Capital Goods",
        "industry": "Industrial Steam Turbines",
        "market_cap_category": "Smallcap",
        "market_cap_cr": 21200.0,
        "description": "Market leader in industrial steam turbines up to 100 MW with dominant market share in domestic and international biomass co-generation."
    },
    {
        "symbol": "PRAJIND",
        "name": "Praj Industries Limited",
        "bse_code": "522205",
        "isin": "INE163B01018",
        "sector": "Capital Goods",
        "industry": "Bioenergy & Process Engineering",
        "market_cap_category": "Smallcap",
        "market_cap_cr": 13700.0,
        "description": "Global biotechnology company leading in bioethanol plants, sustainable aviation fuel (SAF), and critical wastewater treatment solutions."
    },
    {
        "symbol": "GRANULES",
        "name": "Granules India Limited",
        "bse_code": "532482",
        "isin": "INE101A01026",
        "sector": "Healthcare",
        "industry": "Pharmaceuticals & APIs",
        "market_cap_category": "Smallcap",
        "market_cap_cr": 13900.0,
        "description": "Vertically integrated pharmaceutical manufacturer specializing in high-volume APIs (Paracetamol, Metformin, Ibuprofen) and finished doses."
    }
]

# Benchmark leaders (Nifty 50) for comparison and market breadth
BENCHMARK_LEADERS: List[Dict[str, Any]] = [
    {
        "symbol": "RELIANCE",
        "name": "Reliance Industries Limited",
        "bse_code": "500325",
        "isin": "INE002A01018",
        "sector": "Oil, Gas & Consumable Fuels",
        "industry": "Integrated Oil, Retail & Telecom",
        "market_cap_category": "Largecap",
        "market_cap_cr": 1950000.0,
        "description": "India's largest conglomerate spanning petrochemicals, refining, Jio digital services, and retail network."
    },
    {
        "symbol": "TCS",
        "name": "Tata Consultancy Services Limited",
        "bse_code": "532540",
        "isin": "INE467B01029",
        "sector": "Information Technology",
        "industry": "IT Services & Consulting",
        "market_cap_category": "Largecap",
        "market_cap_cr": 1520000.0,
        "description": "Global leader in IT consulting and digital transformation services."
    },
    {
        "symbol": "HDFCBANK",
        "name": "HDFC Bank Limited",
        "bse_code": "500180",
        "isin": "INE040A01034",
        "sector": "Financial Services",
        "industry": "Private Sector Bank",
        "market_cap_category": "Largecap",
        "market_cap_cr": 1280000.0,
        "description": "India's largest private sector bank with extensive retail and wholesale banking networks."
    },
    {
        "symbol": "ICICIBANK",
        "name": "ICICI Bank Limited",
        "bse_code": "532174",
        "isin": "INE090A01021",
        "sector": "Financial Services",
        "industry": "Private Sector Bank",
        "market_cap_category": "Largecap",
        "market_cap_cr": 890000.0,
        "description": "Leading Indian multinational bank and financial services company."
    },
    {
        "symbol": "LT",
        "name": "Larsen & Toubro Limited",
        "bse_code": "500510",
        "isin": "INE018A01030",
        "sector": "Construction",
        "industry": "Infrastructure & Defense EPC",
        "market_cap_category": "Largecap",
        "market_cap_cr": 490000.0,
        "description": "Indian multinational technology, engineering, construction, and manufacturing conglomerate."
    }
]

def get_complete_universe() -> List[Dict[str, Any]]:
    """Return all companies across Smallcap 100 universe and benchmark constituents."""
    return NIFTY_SMALLCAP_100_CONSTITUENTS + BENCHMARK_LEADERS

def find_company_by_symbol(symbol: str) -> Dict[str, Any]:
    """Lookup company metadata by ticker symbol."""
    sym = symbol.upper().replace(".NS", "").replace(".BO", "")
    for comp in get_complete_universe():
        if comp["symbol"] == sym:
            return comp
    return {}
