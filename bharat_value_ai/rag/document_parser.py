"""Document Ingestion, Chunking, and Knowledge Base Seeding."""
import re
from typing import List, Dict, Any
from bharat_value_ai.rag.vector_store import vector_store

CURATED_ANNUAL_REPORT_CHUNKS = [
    {
        "symbol": "CDSL",
        "document_title": "CDSL Annual Report FY2024",
        "reporting_period": "FY2023-24",
        "publication_date": "2024-06-25",
        "section_title": "Management Discussion & Market Position",
        "source_url": "https://www.cdslindia.com/downloads/annualreports/AnnualReport2024.pdf",
        "content": "Central Depository Services (India) Limited crossed the historic milestone of 115 million active Demat accounts in FY24, maintaining market share of over 77% in incremental Demat account additions. Operating revenue grew by 48% YoY driven by market buoyancy, annual issuer charges, transaction fees, and online KYC services through subsidiary CVL."
    },
    {
        "symbol": "CDSL",
        "document_title": "CDSL Q3 FY24 Earnings Conference Call",
        "reporting_period": "Q3 FY2023-24",
        "publication_date": "2024-02-04",
        "section_title": "Capital Expenditure & Cybersecurity",
        "source_url": "https://www.cdslindia.com/investors/transcripts.html",
        "content": "Management highlighted that capital expenditures remained light at ₹35 crore for technology and cyber-resilience enhancements. Operating margin expanded to 61% reflecting operating leverage inherent in digital market infrastructure utilities. The company has zero bank debt and liquid investments of ₹850 crore."
    },
    {
        "symbol": "SUZLON",
        "document_title": "Suzlon Energy Ltd FY2024 Integrated Annual Report",
        "reporting_period": "FY2023-24",
        "publication_date": "2024-07-15",
        "section_title": "Balance Sheet Turnaround & Debt Deleveraging",
        "source_url": "https://www.suzlon.com/in-en/investor-relations",
        "content": "Suzlon completed a comprehensive balance sheet turnaround, transforming from high indebtedness to a net cash positive balance sheet with cash equivalents exceeding ₹1,150 crore. The order book stands at a record 3.8 GW, supported by marquee PSU customers like NTPC Green Energy, SJVN, and commercial C&I clients."
    },
    {
        "symbol": "EXIDEIND",
        "document_title": "Exide Industries Limited FY2024 Annual Report",
        "reporting_period": "FY2023-24",
        "publication_date": "2024-07-02",
        "section_title": "Lithium-Ion Gigafactory Investment",
        "source_url": "https://www.exideindustries.com/investors",
        "content": "Exide Energy Solutions Limited (EESL), a wholly owned subsidiary, is constructing a multi-gigawatt lithium-ion cell manufacturing plant in Bengaluru. Total planned capex across Phase 1 is ₹4,000 crore, funded via internal accruals and parent equity infusions. Strategic agreements have been executed with Hyundai Motor Company and Kia Corporation for localized EV cells."
    },
    {
        "symbol": "ANGELONE",
        "document_title": "Angel One Limited Annual Report FY2024",
        "reporting_period": "FY2023-24",
        "publication_date": "2024-06-20",
        "section_title": "Client Acquisition & FinTech Platform Scale",
        "source_url": "https://www.angelone.in/investor-relations",
        "content": "Angel One's client base expanded to 24.2 million accounts with Average Daily Turnover (ADTO) surpassing ₹44 lakh crore. Return on Equity (ROE) stood at 41.2% while client funding book expanded to ₹2,800 crore generating stable financing net interest income."
    },
    {
        "symbol": "CAMS",
        "document_title": "CAMS Limited Annual Report FY2024",
        "reporting_period": "FY2023-24",
        "publication_date": "2024-06-18",
        "section_title": "Mutual Fund RTA Market Leadership & Non-MF Scaling",
        "source_url": "https://www.camsonline.com/about-cams/investor-relations",
        "content": "CAMS services approximately 68% of India's mutual fund industry AUM. Non-mutual fund revenue engines, including Alternative Investment Fund (AIF) administration, Central Recordkeeping Agency (CRA) for NPS, and Account Aggregator services, contributed 13% of consolidated top-line."
    }
]

class DocumentParserService:
    """Parses and indexes filings, annual reports, and investor communications."""

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
        """Index curated audited annual report passages into vector store."""
        for idx, doc in enumerate(CURATED_ANNUAL_REPORT_CHUNKS):
            chunk_id = f"chunk_{doc['symbol']}_{idx+1:03d}"
            vector_store.add_document_chunk(
                chunk_id=chunk_id,
                symbol=doc["symbol"],
                document_title=doc["document_title"],
                reporting_period=doc["reporting_period"],
                publication_date=doc["publication_date"],
                section_title=doc["section_title"],
                content=doc["content"],
                source_url=doc["source_url"]
            )

doc_parser_service = DocumentParserService()
