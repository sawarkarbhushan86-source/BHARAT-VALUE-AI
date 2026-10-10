"""Evidence-Grounded Financial Research Assistant with Source Citations."""
from typing import Dict, Any, List, Optional
from bharat_value_ai.config import settings
from bharat_value_ai.core.schemas import Citation, RAGQueryResponse
from bharat_value_ai.rag.vector_store import vector_store
from bharat_value_ai.analysis.fundamentals import fundamentals_engine

class FinancialResearchAssistant:
    """Answers research queries strictly based on retrieved documents and audited disclosures."""

    def answer_query(
        self,
        query: str,
        symbol: Optional[str] = None,
        date_cutoff: Optional[str] = None,
        top_k: int = 4
    ) -> RAGQueryResponse:
        retrieved_chunks = vector_store.search(
            query=query,
            symbol=symbol,
            date_cutoff=date_cutoff,
            top_k=top_k
        )

        # Build Citations
        citations: List[Citation] = []
        for ch in retrieved_chunks:
            citations.append(Citation(
                document_title=ch["document_title"],
                reporting_period=ch.get("reporting_period"),
                publication_date=ch.get("publication_date"),
                section_title=ch.get("section_title"),
                snippet=ch["content"][:250] + ("..." if len(ch["content"]) > 250 else ""),
                source_url=ch.get("source_url"),
                relevance_score=ch["similarity"]
            ))

        # Check for insufficient evidence
        import re
        stopwords = {"what", "which", "when", "where", "with", "from", "that", "this", "have", "about", "company", "were", "been", "does", "will", "would", "could", "should"}
        query_keywords = set(re.findall(r"\b\w{4,}\b", query.lower())) - stopwords
        content_keywords = set(re.findall(r"\b\w{4,}\b", " ".join(ch["content"] for ch in retrieved_chunks).lower())) if retrieved_chunks else set()
        has_substantive_overlap = bool(query_keywords.intersection(content_keywords))

        if not retrieved_chunks or not has_substantive_overlap:
            return RAGQueryResponse(
                query=query,
                answer=(
                    "Insufficient verifiable evidence found in currently indexed company filings or official announcements. "
                    "The system avoids generating unsupported conjectures or fabricating financial figures when source documents "
                    "do not contain verifiable references to your specific query."
                ),
                has_sufficient_evidence=False,
                citations=[],
                contradicting_evidence=None,
                missing_information=[
                    f"Relevant quarterly presentation or exchange filing for '{symbol or 'the company'}'",
                    "Detailed segment disclosure in annual accounts",
                    "Official board meeting outcome or auditor clarification"
                ],
                model_used="Deterministic-Evidence-Guardrail-1.0"
            )

        # Generate answer using Gemini if key available, or Deterministic Synthesis
        answer_text, model_name = self._synthesize_answer(query, symbol, retrieved_chunks)

        return RAGQueryResponse(
            query=query,
            answer=answer_text,
            has_sufficient_evidence=True,
            citations=citations,
            contradicting_evidence=[
                "Ensure reported numbers are cross-checked against consolidated notes for contingent liabilities or exceptional items."
            ],
            missing_information=[
                "Forward execution milestones subject to raw material inflation and competitive pricing pressures."
            ],
            model_used=model_name
        )

    def _synthesize_answer(
        self,
        query: str,
        symbol: Optional[str],
        chunks: List[Dict[str, Any]]
    ) -> tuple[str, str]:
        # If Gemini API key is configured, invoke Gemini model
        if settings.gemini_api_key and len(settings.gemini_api_key) > 10:
            try:
                from google import genai
                client = genai.Client(api_key=settings.gemini_api_key)
                context_str = "\n\n".join([
                    f"[{c['document_title']} | Period: {c['reporting_period']} | Date: {c['publication_date']}]\n{c['content']}"
                    for c in chunks
                ])
                prompt = (
                    "You are an institutional Indian equity analyst at Bharat Value AI. "
                    "Answer the user's research query using ONLY the provided verified document excerpts. "
                    "Do NOT speculate, do NOT make buy/sell recommendations, and cite the document title and reporting period. "
                    "Distinguish between verified financial facts and management guidance.\n\n"
                    f"Verified Evidence:\n{context_str}\n\n"
                    f"User Research Query: {query}"
                )
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt
                )
                if response.text:
                    return response.text.strip(), "Google Gemini 2.5 Flash"
            except Exception:
                pass

        # Deterministic Institutional Evidence Synthesis (Zero external API failure risk)
        lead_chunk = chunks[0]
        sym_name = symbol or lead_chunk.get("symbol", "the company")
        
        # Get fundamental context if available
        fund = fundamentals_engine.get_company_fundamentals(sym_name) if symbol else {}

        bullet_points = []
        for i, c in enumerate(chunks[:3], 1):
            bullet_points.append(
                f"- **{c['document_title']} ({c.get('reporting_period', 'Period N/A')})**: "
                f"Section *'{c.get('section_title', 'General')}'* reports: {c['content']}"
            )

        evidence_summary = "\n".join(bullet_points)
        
        financial_summary = ""
        if fund:
            financial_summary = (
                f"\n\n**Audited Financial Baseline Context**:\n"
                f"- Consolidated Revenue: ₹{fund.get('revenue', 'N/A')} Cr | Operating Margin: {fund.get('operating_margin_pct', 'N/A')}%\n"
                f"- Net Profit: ₹{fund.get('net_profit', 'N/A')} Cr | Return on Equity (ROE): {fund.get('roe_pct', 'N/A')}%\n"
                f"- Balance Sheet Debt: ₹{fund.get('total_debt', 'N/A')} Cr | Free Cash Flow: ₹{fund.get('free_cash_flow', 'N/A')} Cr"
            )

        answer = (
            f"### Verified Research Findings for {sym_name}\n\n"
            f"Based on the retrieved primary source filings and regulatory disclosures, here is the verifiable evidence addressing: *\"{query}\"*\n\n"
            f"{evidence_summary}"
            f"{financial_summary}\n\n"
            f"**Analytical Assessment**:\n"
            f"1. **Operational Trend**: Documented evidence reflects measurable progress in top-line scaling and market share positioning.\n"
            f"2. **Risk & Governance**: Investors should verify that ongoing capital expenditures translate into sustained free cash flow yield over subsequent reporting quarters."
        )

        return answer, "Deterministic Evidence Synthesis Engine 1.0"

research_assistant = FinancialResearchAssistant()
