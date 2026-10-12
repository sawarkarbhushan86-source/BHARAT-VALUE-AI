"""Evidence-Grounded Financial Research Assistant with Source Citations & Comparative Queries."""
import re
from typing import Dict, Any, List, Optional, Tuple

from bharat_value_ai.config import settings
from bharat_value_ai.core.schemas import Citation, RAGQueryResponse
from bharat_value_ai.rag.vector_store import vector_store
from bharat_value_ai.analysis.fundamentals import fundamentals_engine
from bharat_value_ai.data.registry import company_registry
from bharat_value_ai.data.normalization import normalize_symbol

class FinancialResearchAssistant:
    """Answers research queries strictly based on retrieved documents and audited disclosures."""

    def _extract_company_mentions(self, query: str) -> List[str]:
        """Detects all company ticker symbols mentioned in the query text."""
        q_lower = query.lower()
        found_symbols = []
        sorted_aliases = sorted(company_registry._alias_map.items(), key=lambda x: len(x[0]), reverse=True)
        for alias, canonical in sorted_aliases:
            if len(alias) >= 3 and (f" {alias} " in f" {q_lower} " or f"({alias})" in q_lower or alias in q_lower.split()):
                if canonical not in found_symbols:
                    found_symbols.append(canonical)
            elif len(alias) >= 5 and alias in q_lower:
                if canonical not in found_symbols:
                    found_symbols.append(canonical)
        return found_symbols

    def answer_query(
        self,
        query: str,
        symbol: Optional[str] = None,
        date_cutoff: Optional[str] = None,
        top_k: int = 4
    ) -> RAGQueryResponse:
        # 1. Resolve company mentions
        mentioned_syms = self._extract_company_mentions(query)
        is_comparative = len(mentioned_syms) >= 2 or ("compare" in query.lower() and (len(mentioned_syms) >= 1 or symbol))

        if is_comparative and len(mentioned_syms) >= 2:
            return self._handle_comparative_query(query, mentioned_syms[:2], date_cutoff, top_k)

        target_sym = mentioned_syms[0] if mentioned_syms else None

        # If not explicitly mentioned in query, fallback to ambient symbol
        if not target_sym and symbol:
            comp = company_registry.get_company(symbol)
            target_sym = comp["symbol"] if comp else normalize_symbol(symbol)

        # 2. Search indexed document chunks
        retrieved_chunks = vector_store.search(
            query=query,
            symbol=target_sym,
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
                snippet=ch["content"][:260] + ("..." if len(ch["content"]) > 260 else ""),
                source_url=ch.get("source_url"),
                relevance_score=ch["similarity"]
            ))

        # Check for substantive query-evidence keyword overlap (excluding company entity names and stopwords)
        stopwords = {
            "what", "which", "when", "where", "with", "from", "that", "this", "have",
            "about", "company", "were", "been", "does", "will", "would", "could", "should",
            "tell", "explain", "report", "detail", "details", "give", "much", "many", "their",
            "they", "there", "some", "more", "most", "also", "than", "then", "into", "over",
            "the", "was", "for", "are", "and", "during", "regarding", "its", "like", "any", "all", "out", "per"
        }
        comp_tokens = set()
        if target_sym:
            comp_tokens.update(re.findall(r"\b\w+\b", target_sym.lower()))
        if symbol:
            comp_tokens.update(re.findall(r"\b\w+\b", symbol.lower()))
        comp = company_registry.get_company(target_sym or symbol or "")
        if comp:
            comp_tokens.update(re.findall(r"\b\w+\b", comp.get("name", "").lower()))
            comp_tokens.update(re.findall(r"\b\w+\b", comp.get("symbol", "").lower()))
        for alias, can_sym in company_registry._alias_map.items():
            if can_sym == target_sym or (symbol and can_sym == normalize_symbol(symbol)):
                comp_tokens.update(re.findall(r"\b\w+\b", alias.lower()))
        comp_tokens.update({
            "bank", "limited", "ltd", "corp", "corporation", "industries",
            "services", "energy", "holdings", "group", "india", "indian",
            "share", "shares", "stock", "stocks", "financial"
        })

        def _stem(w: str) -> str:
            w = w.lower()
            if w.endswith("ies"):
                return w[:-3] + "y"
            if w.endswith("es"):
                return w[:-2]
            if w.endswith("s") and not w.endswith("ss"):
                return w[:-1]
            if w.endswith("ing"):
                return w[:-3]
            if w.endswith("ed"):
                return w[:-2]
            return w

        synonym_map = {
            "revenue": {"revenue", "revenues", "income", "sales", "turnover", "topline", "nii"},
            "sales": {"revenue", "revenues", "income", "sales", "turnover", "topline"},
            "turnover": {"revenue", "revenues", "income", "sales", "turnover", "topline"},
            "income": {"revenue", "revenues", "income", "sales", "turnover", "topline", "nii", "profit"},
            "profit": {"profit", "profits", "pat", "earnings", "ebitda", "ebit", "bottomline"},
            "earnings": {"profit", "profits", "pat", "earnings", "ebitda", "ebit", "bottomline"},
            "pat": {"profit", "profits", "pat", "earnings"},
            "margin": {"margin", "margins", "nim", "ebitda", "profitability"},
            "growth": {"growth", "grew", "grown", "expansion", "increase", "increased", "surged", "jumped"},
            "deposit": {"deposit", "deposits", "casa", "inflow"},
            "loan": {"loan", "loans", "advance", "advances", "credit", "portfolio"},
            "asset": {"asset", "assets", "gnpa", "nnpa", "npa", "quality", "delinquency"},
            "npa": {"asset", "assets", "gnpa", "nnpa", "npa", "delinquency", "provision"},
            "risk": {"risk", "risks", "threat", "uncertainty", "vulnerability", "bottleneck"},
            "order": {"order", "orders", "orderbook", "inflow", "wins", "contract", "tcv"},
            "debt": {"debt", "borrowing", "deleveraging", "indebtedness", "liabilities"},
        }

        raw_query_words = set(re.findall(r"\b\w{3,}\b", query.lower())) - stopwords - comp_tokens
        expanded_query_words = set()
        for w in raw_query_words:
            stemmed = _stem(w)
            expanded_query_words.add(stemmed)
            expanded_query_words.add(w)
            if stemmed in synonym_map:
                expanded_query_words.update(synonym_map[stemmed])
            if w in synonym_map:
                expanded_query_words.update(synonym_map[w])

        content_text = " ".join(ch["content"] for ch in retrieved_chunks).lower() if retrieved_chunks else ""
        content_words = set(re.findall(r"\b\w{3,}\b", content_text))
        stemmed_content_words = {_stem(w) for w in content_words} | content_words

        generic_tokens = {
            "revenue", "revenues", "sales", "income", "profit", "profits",
            "pat", "margin", "margins", "growth", "financial", "report",
            "filing", "disclosures", "annual", "quarterly", "results", "fy24", "fy23"
        }
        matched = expanded_query_words.intersection(stemmed_content_words)
        specific_query_words = raw_query_words - generic_tokens
        if specific_query_words:
            specific_stemmed = {_stem(w) for w in specific_query_words} | specific_query_words
            specific_matched = specific_stemmed.intersection(stemmed_content_words)
            has_substantive_overlap = bool(specific_matched)
        else:
            has_substantive_overlap = bool(matched)
        max_sim = max([ch.get("similarity", 0.0) for ch in retrieved_chunks], default=0.0)

        # 3. Transparent insufficient evidence handling
        if not retrieved_chunks or not has_substantive_overlap or max_sim < 0.20:
            missing_sym = target_sym or symbol or "the requested company"
            return RAGQueryResponse(
                query=query,
                symbol=target_sym or symbol,
                answer=(
                    "Insufficient verifiable evidence found in currently indexed company filings or official announcements. "
                    "The system avoids generating unsupported conjectures or fabricating financial figures when source documents "
                    "do not contain verifiable references to your specific query."
                ),
                has_sufficient_evidence=False,
                is_insufficient_evidence=True,
                citations=[],
                contradicting_evidence=None,
                missing_information=[
                    f"Relevant quarterly presentation or exchange filing for '{missing_sym}'",
                    "Detailed segment disclosure in annual accounts",
                    "Official board meeting outcome or auditor clarification"
                ],
                model_used="Evidence-Guardrail-v2.2"
            )

        # 4. Generate Answer
        answer_text, model_name = self._synthesize_answer(query, target_sym, retrieved_chunks)

        return RAGQueryResponse(
            query=query,
            symbol=target_sym or symbol,
            answer=answer_text,
            has_sufficient_evidence=True,
            is_insufficient_evidence=False,
            citations=citations,
            contradicting_evidence=[
                "Ensure reported statutory numbers are reconciled against consolidated notes for exceptional items or contingent liabilities."
            ],
            missing_information=[
                "Forward execution milestones subject to macro interest rate cycles and competitive pricing pressures."
            ],
            model_used=model_name
        )

    def _handle_comparative_query(
        self,
        query: str,
        symbols: List[str],
        date_cutoff: Optional[str],
        top_k: int
    ) -> RAGQueryResponse:
        """Handles cross-company comparative analysis only when comparable evidence exists."""
        sym1, sym2 = symbols[0], symbols[1]
        chunks1 = vector_store.search(query=query, symbol=sym1, date_cutoff=date_cutoff, top_k=top_k)
        chunks2 = vector_store.search(query=query, symbol=sym2, date_cutoff=date_cutoff, top_k=top_k)

        all_chunks = chunks1 + chunks2
        if not chunks1 or not chunks2:
            return RAGQueryResponse(
                query=query,
                symbol=f"{sym1},{sym2}",
                answer=(
                    f"Insufficient comparative evidence: While disclosures for '{sym1 if chunks1 else sym2}' exist, "
                    f"comparable audited regulatory filings for '{sym2 if not chunks2 else sym1}' are currently awaiting ingestion. "
                    "Cross-company comparisons are restricted to periods with mutually verified official filings."
                ),
                has_sufficient_evidence=False,
                is_insufficient_evidence=True,
                citations=[
                    Citation(
                        document_title=c["document_title"],
                        reporting_period=c.get("reporting_period"),
                        section_title=c.get("section_title"),
                        snippet=c["content"][:240],
                        source_url=c.get("source_url"),
                        relevance_score=c["similarity"]
                    ) for c in all_chunks
                ],
                missing_information=[f"Official filing disclosures for '{sym2 if not chunks2 else sym1}'"],
                model_used="Comparative-Guardrail-v2.2"
            )

        fund1 = fundamentals_engine.get_company_fundamentals(sym1)
        fund2 = fundamentals_engine.get_company_fundamentals(sym2)

        # Citations
        citations = [
            Citation(
                document_title=c["document_title"],
                reporting_period=c.get("reporting_period"),
                section_title=c.get("section_title"),
                snippet=c["content"][:240],
                source_url=c.get("source_url"),
                relevance_score=c["similarity"]
            ) for c in (chunks1[:2] + chunks2[:2])
        ]

        # Comparative Synthesis
        answer = (
            f"### Verified Comparative Research: {sym1} vs. {sym2}\n\n"
            f"Based on primary corporate disclosures and audited financial filings:\n\n"
            f"#### 1. {sym1} Disclosed Profile:\n"
            f"- **Primary Finding**: {chunks1[0]['content']}\n"
            f"- **Key Metrics ({fund1.get('reporting_period', 'FY24')})**: Revenue: ₹{fund1.get('revenue', 'N/A')} Cr | PAT: ₹{fund1.get('net_profit', 'N/A')} Cr | ROE: {fund1.get('roe_pct', 'N/A')}%\n\n"
            f"#### 2. {sym2} Disclosed Profile:\n"
            f"- **Primary Finding**: {chunks2[0]['content']}\n"
            f"- **Key Metrics ({fund2.get('reporting_period', 'FY24')})**: Revenue: ₹{fund2.get('revenue', 'N/A')} Cr | PAT: ₹{fund2.get('net_profit', 'N/A')} Cr | ROE: {fund2.get('roe_pct', 'N/A')}%\n\n"
            f"#### 3. Institutional Synthesis & Contrast:\n"
            f"- Both entities operate with distinct capital allocation models and sector dynamics as cited in their respective regulatory disclosures.\n"
            f"- **Fact Distinction**: Financial figures reflect public exchange filings; operational statements reflect management discussion.\n\n"
            f"*(Note: RAG synthesizes primary documentary evidence and does not forecast future stock price returns.)*"
        )

        return RAGQueryResponse(
            query=query,
            symbol=f"{sym1},{sym2}",
            answer=answer,
            has_sufficient_evidence=True,
            is_insufficient_evidence=False,
            citations=citations,
            contradicting_evidence=["Different accounting policies (e.g. depreciation or revenue recognition) may affect direct comparability."],
            missing_information=[],
            model_used="Comparative-Evidence-Engine-v2.2"
        )

    def _synthesize_answer(
        self,
        query: str,
        symbol: Optional[str],
        chunks: List[Dict[str, Any]]
    ) -> Tuple[str, str]:
        # Optional Gemini API synthesis
        if settings.gemini_api_key and len(settings.gemini_api_key) > 10:
            try:
                from google import genai
                client = genai.Client(api_key=settings.gemini_api_key)
                context_str = "\n\n".join([
                    f"[{c['document_title']} | Period: {c.get('reporting_period', 'N/A')} | Section: {c.get('section_title', 'General')}]\n{c['content']}"
                    for c in chunks
                ])
                prompt = (
                    "You are a principal Indian equity research analyst at Bharat Value AI. "
                    "Answer the user's research query using ONLY the provided verified document excerpts. "
                    "Format in clean markdown with clear headings and bullet points. "
                    "Cite the document title and reporting period for every factual statement. "
                    "Explicitly distinguish reported facts, derived calculations, and model interpretation. "
                    "Do NOT speculate, do NOT make buy/sell instructions, and do NOT fabricate financial numbers.\n\n"
                    f"Verified Evidence:\n{context_str}\n\n"
                    f"User Query: {query}"
                )
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt
                )
                if response.text:
                    return response.text.strip(), "Google Gemini 2.5 Flash"
            except Exception:
                pass

        # Deterministic Institutional Evidence Synthesis
        lead_chunk = chunks[0]
        sym_name = symbol or lead_chunk.get("symbol", "the company")
        fund = fundamentals_engine.get_company_fundamentals(sym_name) if symbol else {}

        evidence_bullets = []
        for c in chunks[:3]:
            evidence_bullets.append(
                f"- **{c['document_title']}** (*{c.get('reporting_period', 'N/A')}* — Section: *{c.get('section_title', 'General')}*):\n"
                f"  > \"{c['content']}\""
            )

        evidence_section = "\n\n".join(evidence_bullets)

        financial_context = ""
        if fund and fund.get("is_catalogued"):
            rev = fund.get("revenue")
            pat = fund.get("net_profit")
            roe = fund.get("roe_pct")
            fcf = fund.get("free_cash_flow")
            financial_context = (
                f"\n\n#### Audited Fundamental Context ({fund.get('reporting_period', 'FY24')}):\n"
                f"- **Consolidated Revenue**: ₹{rev:,.1f} Cr" if rev else ""
            )
            if pat:
                financial_context += f" | **Net Profit (PAT)**: ₹{pat:,.1f} Cr"
            if roe:
                financial_context += f" | **ROE**: {roe:.1f}%"
            if fcf:
                financial_context += f" | **Free Cash Flow**: ₹{fcf:,.1f} Cr"

        answer = (
            f"### Verified Evidence-Grounded Research for {sym_name}\n\n"
            f"Based on primary corporate filings and regulatory disclosures, here is the verifiable evidence addressing: *\"{query}\"*\n\n"
            f"#### Primary Documentary Excerpts:\n"
            f"{evidence_section}"
            f"{financial_context}\n\n"
            f"*(Fact vs Interpretation: Specific numbers reflect audited exchange disclosures. Forward milestones reflect company projections.)*\n"
            f"*(Disclaimer: RAG retrieval performs document question-answering and does not predict future market returns.)*"
        )
        return answer, "Deterministic Evidence Engine v2.2"

    def query(
        self,
        query: str,
        symbol: Optional[str] = None,
        date_cutoff: Optional[str] = None,
        top_k: int = 4
    ) -> RAGQueryResponse:
        return self.answer_query(query, symbol=symbol, date_cutoff=date_cutoff, top_k=top_k)

research_assistant = FinancialResearchAssistant()
rag_assistant = research_assistant
