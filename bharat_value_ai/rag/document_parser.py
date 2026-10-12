"""Document Ingestion, Chunking, Deduplication, and Knowledge Base Seeding."""
import hashlib
import re
from typing import List, Dict, Any, Optional

from bharat_value_ai.rag.vector_store import vector_store
from bharat_value_ai.data.registry import company_registry

CURATED_ANNUAL_REPORT_CHUNKS: List[Dict[str, Any]] = [
    # ------------------ CDSL ------------------
    {
        "symbol": "CDSL",
        "document_title": "CDSL Annual Report FY2024",
        "reporting_period": "FY2023-24",
        "publication_date": "2024-06-25",
        "section_title": "Management Discussion & Market Position",
        "source_url": "https://www.cdslindia.com/downloads/annualreports/AnnualReport2024.pdf",
        "page_or_section": "MD&A, Pages 42-45",
        "content": "Central Depository Services (India) Limited crossed the historic milestone of 115 million active Demat accounts in FY24, maintaining market share of over 77% in incremental Demat account additions. Operating revenue grew by 48% YoY driven by market buoyancy, annual issuer charges, transaction fees, and online KYC services through subsidiary CVL."
    },
    {
        "symbol": "CDSL",
        "document_title": "CDSL Q4 FY24 Financial Results & Disclosures",
        "reporting_period": "Q4 FY2023-24",
        "publication_date": "2024-04-20",
        "section_title": "Quarterly Performance & Growth Drivers",
        "source_url": "https://www.cdslindia.com/investors/transcripts.html",
        "page_or_section": "Investor Release, Page 3",
        "content": "In Q4 FY24, CDSL recorded total revenue of ₹241 crore (up 86% YoY) and Net Profit of ₹129 crore (up 44% YoY). Future growth drivers include mandatory dematerialization for private unlisted companies under MCA rules, electronic insurance policies (eIA), and expanded account aggregator linkages."
    },
    {
        "symbol": "CDSL",
        "document_title": "CDSL Annual Report FY2024 — Risk Management",
        "reporting_period": "FY2023-24",
        "publication_date": "2024-06-25",
        "section_title": "Principal Disclosed Risk Factors",
        "source_url": "https://www.cdslindia.com/downloads/annualreports/AnnualReport2024.pdf",
        "page_or_section": "Statutory Disclosures, Page 68",
        "content": "Key disclosed risks include cybersecurity vulnerabilities and operational resilience in High-Frequency Trading settlement networks; regulatory changes in tariff structures mandated by SEBI; and cyclicality in retail trading volumes impacting variable settlement and IPO corporate action fee revenue."
    },
    {
        "symbol": "CDSL",
        "document_title": "CDSL Historical Revenue Trajectory FY21-FY24",
        "reporting_period": "FY2021-FY2024",
        "publication_date": "2024-06-25",
        "section_title": "Financial Highlights & Multi-Period Trend",
        "source_url": "https://www.cdslindia.com/downloads/annualreports/AnnualReport2024.pdf",
        "page_or_section": "Financial Highlights, Page 8",
        "content": "Consolidated operating revenue expanded from ₹343 crore in FY21 to ₹551 crore in FY22, ₹555 crore in FY23, and ₹905 crore in FY24, representing a 3-year CAGR of 38.2%. Net Profit rose in tandem from ₹201 crore in FY21 to ₹420 crore in FY24, driven by recurring issuer fees."
    },

    # ------------------ CAMS ------------------
    {
        "symbol": "CAMS",
        "document_title": "CAMS Limited Annual Report FY2024",
        "reporting_period": "FY2023-24",
        "publication_date": "2024-06-18",
        "section_title": "Mutual Fund RTA Market Leadership & Non-MF Scaling",
        "source_url": "https://www.camsonline.com/about-cams/investor-relations",
        "page_or_section": "MD&A, Pages 28-31",
        "content": "CAMS services approximately 68% of India's mutual fund industry AUM. Non-mutual fund revenue engines, including Alternative Investment Fund (AIF) administration, Central Recordkeeping Agency (CRA) for NPS, and Account Aggregator services, contributed 13% of consolidated top-line. Consolidated revenue stood at ₹1,136 crore with EBITDA margin of 44.8%."
    },
    {
        "symbol": "CAMS",
        "document_title": "CAMS Q4 FY24 Investor Presentation",
        "reporting_period": "Q4 FY2023-24",
        "publication_date": "2024-05-08",
        "section_title": "Quarterly Financial Performance & SIP Inflows",
        "source_url": "https://www.camsonline.com/investor-relations",
        "page_or_section": "Investor Presentation, Page 6",
        "content": "Q4 FY24 revenue grew 24.6% YoY to ₹312 crore with profit after tax rising 38.7% YoY to ₹103 crore. Monthly SIP registrations processed reached 4.1 million, reflecting high financialization of household savings."
    },

    # ------------------ SUZLON ENERGY ------------------
    {
        "symbol": "SUZLON",
        "document_title": "Suzlon Energy Ltd FY2024 Integrated Annual Report",
        "reporting_period": "FY2023-24",
        "publication_date": "2024-07-15",
        "section_title": "Balance Sheet Turnaround & Debt Deleveraging",
        "source_url": "https://www.suzlon.com/in-en/investor-relations",
        "page_or_section": "Financial Overview, Page 14",
        "content": "Suzlon completed a comprehensive balance sheet turnaround, transforming from high indebtedness to a net cash positive balance sheet with cash equivalents exceeding ₹1,150 crore. The order book stands at a record 3.8 GW, supported by marquee PSU customers like NTPC Green Energy, SJVN, and commercial C&I clients."
    },
    {
        "symbol": "SUZLON",
        "document_title": "Suzlon Energy Q4 FY24 Earnings Disclosures",
        "reporting_period": "Q4 FY2023-24",
        "publication_date": "2024-05-24",
        "section_title": "Quarterly Deliveries & Future Growth Drivers",
        "source_url": "https://www.suzlon.com/in-en/investor-relations",
        "page_or_section": "Earnings Transcript, Page 5",
        "content": "Q4 FY24 deliveries jumped to 268 MW compared to 157 MW in Q4 FY23. Future growth drivers include commercialization of the 3.15 MW S144 wind turbine generator series, captive hybrid wind-solar EPC tenders, and India's national mandate of 500 GW non-fossil capacity by 2030."
    },
    {
        "symbol": "SUZLON",
        "document_title": "Suzlon Energy FY2024 Risk Disclosures",
        "reporting_period": "FY2023-24",
        "publication_date": "2024-07-15",
        "section_title": "Key Risk Factors & Operational Challenges",
        "source_url": "https://www.suzlon.com/in-en/investor-relations",
        "page_or_section": "Enterprise Risk Management, Page 52",
        "content": "Key operational risks include land acquisition bottlenecks in high-wind states (Gujarat, Tamil Nadu, Karnataka); grid evacuation infrastructure delays from CTU/STU substations; and volatility in raw material commodity prices (structural steel and copper) impacting turbine manufacturing margins."
    },

    # ------------------ EXIDE INDUSTRIES ------------------
    {
        "symbol": "EXIDEIND",
        "document_title": "Exide Industries Limited FY2024 Annual Report",
        "reporting_period": "FY2023-24",
        "publication_date": "2024-07-02",
        "section_title": "Lithium-Ion Gigafactory Investment",
        "source_url": "https://www.exideindustries.com/investors",
        "page_or_section": "Strategic Report, Page 22",
        "content": "Exide Energy Solutions Limited (EESL), a wholly owned subsidiary, is constructing a multi-gigawatt lithium-ion cell manufacturing plant in Bengaluru. Total planned capex across Phase 1 is ₹4,000 crore, funded via internal accruals and parent equity infusions. Strategic agreements have been executed with Hyundai Motor Company and Kia Corporation for localized EV cells."
    },

    # ------------------ HDFC BANK ------------------
    {
        "symbol": "HDFCBANK",
        "document_title": "HDFC Bank Limited Audited Financial Results FY2023-24",
        "reporting_period": "FY2023-24",
        "publication_date": "2024-04-20",
        "section_title": "Audited Financial Statement & Revenue Performance",
        "source_url": "https://www.hdfcbank.com/personal/about-us/investor-relations/financial-results",
        "page_or_section": "Audited Financials, Press Release Page 1",
        "content": "For the full fiscal year FY2023-24, HDFC Bank reported consolidated net revenue of ₹1,57,770 crore, a 51.6% YoY growth driven by mortgage integration. Total gross income stood at ₹2,85,600 crore. Standalone Net Interest Income (NII) for FY24 increased to ₹1,08,532 crore compared to ₹86,842 crore in the previous year. Consolidated Profit After Tax (PAT) reached ₹64,060 crore with basic EPS of ₹84.5 per share. Standalone net profit was ₹60,810 crore."
    },
    {
        "symbol": "HDFCBANK",
        "document_title": "HDFC Bank Limited Annual Report FY2023-24",
        "reporting_period": "FY2023-24",
        "publication_date": "2024-07-10",
        "section_title": "Merger Integration, Total Deposits & Balance Sheet Scale",
        "source_url": "https://www.hdfcbank.com/personal/about-us/investor-relations/annual-reports",
        "page_or_section": "Directors' Report, Pages 50-54",
        "content": "Following the transformational merger with parent mortgage entity HDFC Limited effective July 1, 2023, HDFC Bank expanded its customer base to over 93 million. Consolidated advances reached ₹25,07,800 crore, while total deposits expanded to ₹23,79,800 crore with a healthy CASA ratio of 38.2%. Net Interest Margin (NIM) stood at 3.45% and Return on Assets (RoA) remained industry-leading at 1.95%."
    },
    {
        "symbol": "HDFCBANK",
        "document_title": "HDFC Bank Q4 FY24 Investor Presentation & Earnings Release",
        "reporting_period": "Q4 FY2023-24",
        "publication_date": "2024-04-20",
        "section_title": "Asset Quality, Non-Performing Loans & Branch Expansion",
        "source_url": "https://www.hdfcbank.com/personal/about-us/investor-relations/quarterly-results",
        "page_or_section": "Investor Deck, Page 12",
        "content": "Gross Non-Performing Assets (GNPA) stood at 1.24% with Net NPA at 0.33%, demonstrating resilient underwriting across wholesale and retail portfolios. The Bank added 912 branches during the fiscal year, expanding its branch network to 8,735 branches across semi-urban and rural geographies to mobilize granular retail deposits and normalize the credit-deposit (CD) ratio."
    },
    {
        "symbol": "HDFCBANK",
        "document_title": "HDFC Bank FY2024 Disclosed Risk Factors",
        "reporting_period": "FY2023-24",
        "publication_date": "2024-07-10",
        "section_title": "Financial & Regulatory Risk Factors",
        "source_url": "https://www.hdfcbank.com/personal/about-us/investor-relations/annual-reports",
        "page_or_section": "Risk Architecture, Page 92",
        "content": "Disclosed banking risks highlight credit-deposit ratio recalibration post-merger; deposit repricing pressures amid systemic liquidity tightening; interest rate sensitivity impacting treasury yields; and regulatory changes in risk weights on unsecured consumer loans by the Reserve Bank of India."
    },

    # ------------------ ICICI BANK ------------------
    {
        "symbol": "ICICIBANK",
        "document_title": "ICICI Bank Limited Annual Report FY2023-24",
        "reporting_period": "FY2023-24",
        "publication_date": "2024-07-22",
        "section_title": "Core Operating Profitability & Digital Banking",
        "source_url": "https://www.icicibank.com/about-us/annual-reports",
        "page_or_section": "Performance Review, Page 18",
        "content": "ICICI Bank reported core operating profit growth of 18.3% YoY to ₹58,100 crore and profit after tax of ₹40,888 crore. Domestic loan portfolio grew by 16.8% YoY driven by business banking, retail mortgages, and rural loans. Return on Equity (ROE) expanded to 18.5% with Net NPA improving to 0.42%."
    },
    {
        "symbol": "ICICIBANK",
        "document_title": "ICICI Bank Q4 FY24 Investor Presentation",
        "reporting_period": "Q4 FY2023-24",
        "publication_date": "2024-04-27",
        "section_title": "Quarterly NII, Margins & Asset Quality",
        "source_url": "https://www.icicibank.com/about-us/annual-reports",
        "page_or_section": "Q4 Presentation, Page 8",
        "content": "In Q4 FY24, Net Interest Income grew 8.1% YoY to ₹19,093 crore. Net Interest Margin (NIM) was 4.40% compared to 4.43% in Q3. Gross NPA was 2.16% and Net NPA was 0.42%. Provision coverage ratio (excluding technical write-offs) stood robust at 80.3%."
    },
    {
        "symbol": "ICICIBANK",
        "document_title": "ICICI Bank FY24 Risk Management Disclosures",
        "reporting_period": "FY2023-24",
        "publication_date": "2024-07-22",
        "section_title": "Credit, Market & Operational Risks",
        "source_url": "https://www.icicibank.com/about-us/annual-reports",
        "page_or_section": "Pillar 3 Disclosures, Page 114",
        "content": "Principal risks include unsecured retail lending delinquencies; cybersecurity and digital channel fraud prevention across iMobile Pay; and potential margin compression if competitive deposit acquisition intensifies across the Indian banking sector."
    },

    # ------------------ RELIANCE INDUSTRIES ------------------
    {
        "symbol": "RELIANCE",
        "document_title": "Reliance Industries Limited Integrated Annual Report 2023-24",
        "reporting_period": "FY2023-24",
        "publication_date": "2024-08-05",
        "section_title": "Jio Platforms 5G & Retail Network Scale",
        "source_url": "https://www.ril.com/investor-relations",
        "page_or_section": "Chairman's Statement, Page 12",
        "content": "Reliance Industries achieved consolidated revenue of ₹8,99,000 crore and EBITDA of ₹1,78,650 crore. Jio 5G True5G network rollout was completed nationwide, amassing over 108 million 5G subscribers and carrying 85% of India's 5G data traffic. Reliance Retail crossed 300 million registered customers across 18,774 physical stores."
    },

    # ------------------ TATA CONSULTANCY SERVICES ------------------
    {
        "symbol": "TCS",
        "document_title": "Tata Consultancy Services Annual Report 2023-24",
        "reporting_period": "FY2023-24",
        "publication_date": "2024-06-12",
        "section_title": "AI Cloud Transformation, Margins & Deal Wins",
        "source_url": "https://www.tcs.com/investor-relations/financial-results",
        "page_or_section": "MD&A, Page 35",
        "content": "TCS achieved consolidated revenues of ₹2,40,893 crore, delivering operating margin of 25.7% and net margin of 19.3%. The company trained over 350,000 employees in foundational Generative AI skills and expanded its AI & Cloud transformation pipeline to a record Total Contract Value (TCV) of $42.7 billion."
    },

    # ------------------ LARSEN & TOUBRO ------------------
    {
        "symbol": "LT",
        "document_title": "Larsen & Toubro Limited Annual Report FY2023-24",
        "reporting_period": "FY2023-24",
        "publication_date": "2024-07-05",
        "section_title": "Consolidated Order Inflow & Energy Transition EPC",
        "source_url": "https://www.larsentoubro.com/investors/annual-reports",
        "page_or_section": "Business Review, Page 20",
        "content": "L&T recorded highest-ever consolidated order inflow of ₹3,02,812 crore, taking the consolidated order book to ₹4,75,809 crore with international orders constituting 38%. Major wins spanned Middle East clean energy, green hydrogen plants, high-speed rail, and semiconductor packaging facilities."
    },

    # ------------------ STATE BANK OF INDIA ------------------
    {
        "symbol": "SBIN",
        "document_title": "State Bank of India Annual Report FY2023-24",
        "reporting_period": "FY2023-24",
        "publication_date": "2024-06-15",
        "section_title": "Consolidated Financial Performance & Revenue Highlights",
        "source_url": "https://sbi.co.in/web/investor-relations/annual-reports",
        "page_or_section": "Financial Highlights, Page 12",
        "content": "State Bank of India (SBI) reported consolidated total revenue of ₹4,69,184 crore for FY2023-24, compared to ₹3,68,715 crore in FY23. Operating profit grew by 12.0% to ₹93,889 crore, while standalone net profit reached an all-time record of ₹61,077 crore, marking a 21.6% YoY growth. Net Interest Income (NII) expanded to ₹1,59,876 crore with whole-bank NIM of 3.28% and domestic NIM of 3.43%."
    },

    # ------------------ INFOSYS ------------------
    {
        "symbol": "INFY",
        "document_title": "Infosys Limited Integrated Annual Report 2023-24",
        "reporting_period": "FY2023-24",
        "publication_date": "2024-05-28",
        "section_title": "Audited Consolidated Financials & AI Strategy",
        "source_url": "https://www.infosys.com/investors/reports.html",
        "page_or_section": "Financial Overview, Page 22",
        "content": "Infosys reported consolidated revenues of ₹1,53,670 crore ($18.6 billion) for FY2023-24 with operating margin of 20.7% and net profit of ₹26,233 crore. Free cash flow generation stood at ₹20,100 crore, up 13.7% YoY. Digital revenue accounted for 62.5% of total revenue. Large deal TCV reached an all-time record of $17.7 billion."
    }
]

class DocumentParserService:
    """Parses, deduplicates, and indexes regulatory filings with document hashes and versioning."""

    @staticmethod
    def compute_document_hash(content: str, title: str, period: str) -> str:
        raw = f"{title}_{period}_{content.strip()}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    @staticmethod
    def chunk_text(text: str, max_chunk_size: int = 600) -> List[str]:
        paragraphs = text.split("\n\n")
        chunks = []
        current = ""
        for p in paragraphs:
            p_clean = p.strip()
            if not p_clean:
                continue
            if len(current) + len(p_clean) < max_chunk_size:
                current += (" " + p_clean if current else p_clean)
            else:
                if current:
                    chunks.append(current)
                current = p_clean
        if current:
            chunks.append(current)
        return chunks

    def seed_initial_knowledge_base(self):
        """Index curated audited annual report passages with SHA-256 deduplication and section tracking."""
        seen_hashes = set()
        for idx, doc in enumerate(CURATED_ANNUAL_REPORT_CHUNKS):
            d_hash = self.compute_document_hash(doc["content"], doc["document_title"], doc["reporting_period"])
            if d_hash in seen_hashes:
                continue
            seen_hashes.add(d_hash)

            chunk_id = f"chunk_{doc['symbol']}_{idx+1:03d}"
            sec_label = doc.get("section_title", "General")
            if doc.get("page_or_section"):
                sec_label += f" ({doc['page_or_section']})"

            vector_store.add_document_chunk(
                chunk_id=chunk_id,
                symbol=doc["symbol"],
                document_title=doc["document_title"],
                reporting_period=doc["reporting_period"],
                publication_date=doc["publication_date"],
                section_title=sec_label,
                content=doc["content"],
                source_url=doc["source_url"]
            )

doc_parser_service = DocumentParserService()
