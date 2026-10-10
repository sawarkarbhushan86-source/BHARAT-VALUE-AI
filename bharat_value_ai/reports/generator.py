"""Institutional Equity Research Report Generator (ReportLab PDF & CSV Exports)."""
import os
import datetime
from pathlib import Path
from typing import Dict, Any

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether, HRFlowable
)

from bharat_value_ai.data.universe import find_company_by_symbol
from bharat_value_ai.data.market_provider import market_provider
from bharat_value_ai.analysis.fundamentals import fundamentals_engine
from bharat_value_ai.analysis.fair_value import fair_value_engine
from bharat_value_ai.analysis.quality_growth import quality_engine
from bharat_value_ai.analysis.risk_governance import risk_engine

REPORTS_DIR = Path("./data/reports")
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

class ResearchReportGenerator:
    """Generates institutional PDF and CSV equity research reports."""

    def generate_pdf_report(self, symbol: str) -> str:
        sym = symbol.upper().replace(".NS", "").replace(".BO", "")
        comp = find_company_by_symbol(sym)
        company_name = comp.get("name", sym)
        sector = comp.get("sector", "Diversified")
        
        quote = market_provider.get_quote(sym)
        fund = fundamentals_engine.get_company_fundamentals(sym)
        val = fair_value_engine.evaluate_valuation(sym)
        qual = quality_engine.evaluate_company(sym)
        risks = risk_engine.evaluate_risks(sym)

        now_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"BharatValue_Report_{sym}_{now_str}.pdf"
        file_path = REPORTS_DIR / filename

        doc = SimpleDocTemplate(
            str(file_path),
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36
        )

        styles = getSampleStyleSheet()
        
        # Custom Styles
        title_style = ParagraphStyle(
            "ReportTitle",
            parent=styles["Heading1"],
            fontSize=22,
            leading=26,
            textColor=colors.HexColor("#0f172a"),
            fontName="Helvetica-Bold"
        )
        subtitle_style = ParagraphStyle(
            "ReportSubTitle",
            parent=styles["Normal"],
            fontSize=11,
            leading=15,
            textColor=colors.HexColor("#475569")
        )
        h2_style = ParagraphStyle(
            "SectionH2",
            parent=styles["Heading2"],
            fontSize=13,
            leading=17,
            textColor=colors.HexColor("#1e293b"),
            spaceBefore=10,
            spaceAfter=4,
            fontName="Helvetica-Bold"
        )
        body_style = ParagraphStyle(
            "BodyDark",
            parent=styles["Normal"],
            fontSize=9,
            leading=13,
            textColor=colors.HexColor("#334155")
        )

        elements = []

        # 1. Header Banner
        header_text = (
            f"<b>BHARAT VALUE AI — INSTITUTIONAL EQUITY RESEARCH</b><br/>"
            f"<font size=8 color='#64748b'>Decision-Support & Quantitative Valuation Platform | NSE India</font>"
        )
        elements.append(Paragraph(header_text, subtitle_style))
        elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#3b82f6"), spaceAfter=10))

        # Title Block
        elements.append(Paragraph(f"{company_name} ({sym}.NS)", title_style))
        elements.append(Paragraph(f"Sector: <b>{sector}</b> | Industry: <b>{comp.get('industry', 'N/A')}</b> | Market Cap Category: <b>{comp.get('market_cap_category', 'Smallcap')}</b>", subtitle_style))
        elements.append(Spacer(1, 10))

        # Summary Metrics Table
        metric_data = [
            ["Current Market Price", f"₹{quote.get('price', 0.0):,.2f}", "Composite Fair Value", f"₹{val.composite_fair_value:,.2f}"],
            ["52-Week Range", f"₹{quote.get('week_52_low', 0):,.2f} - ₹{quote.get('week_52_high', 0):,.2f}", "Margin of Safety", f"{val.margin_of_safety_pct:+.1f}% ({val.valuation_status})"],
            ["Quality Score", f"{qual.composite_score}/100", "Compounding Tier", qual.multibagger_potential_tier],
            ["Audited ROE / ROCE", f"{fund.get('roe_pct', 0)}% / {fund.get('roce_pct', 0)}%", "Debt to Equity", f"{fund.get('debt_to_equity', 0)}x"]
        ]
        t_summary = Table(metric_data, colWidths=[130, 130, 130, 150])
        t_summary.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f8fafc")),
            ('TEXTCOLOR', (0,0), (-1,-1), colors.HexColor("#0f172a")),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
            ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
            ('FONTSIZE', (0,0), (-1,-1), 8.5),
            ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
            ('FONTNAME', (2,0), (2,-1), 'Helvetica-Bold'),
            ('PADDING', (0,0), (-1,-1), 5),
        ]))
        elements.append(t_summary)
        elements.append(Spacer(1, 12))

        # 2. Executive Summary
        elements.append(Paragraph("1. Executive Research Summary & Thesis", h2_style))
        summary_desc = (
            f"<b>{company_name}</b> demonstrates {qual.multibagger_potential_tier.lower()} characteristics "
            f"with a composite research score of <b>{qual.composite_score}/100</b>. The company reported consolidated revenue of "
            f"₹{fund.get('revenue', 0):,.0f} Cr and net profit of ₹{fund.get('net_profit', 0):,.0f} Cr, translating into a "
            f"Return on Capital Employed (ROCE) of {fund.get('roce_pct', 0)}%. Balance sheet analysis reveals a debt-to-equity ratio of "
            f"{fund.get('debt_to_equity', 0)}x and Altman Z-score of {fund.get('altman_z_score', 0)}."
        )
        elements.append(Paragraph(summary_desc, body_style))
        elements.append(Spacer(1, 10))

        # 3. Valuation & Scenario Breakdown
        elements.append(Paragraph("2. Deterministic Valuation Scenarios", h2_style))
        val_data = [
            ["Valuation Method / Scenario", "Implied Fair Value (₹)", "Current Price (₹)", "Premium / (Discount)"],
            ["Discounted Cash Flow (DCF - 5Y Explicit)", f"₹{val.dcf_fair_value:,.2f}", f"₹{quote.get('price', 0):,.2f}", f"{((quote.get('price',0)-val.dcf_fair_value)/val.dcf_fair_value*100):+.1f}%"],
            ["Relative P/E Model (25x Multiple)", f"₹{val.pe_fair_value:,.2f}", f"₹{quote.get('price', 0):,.2f}", f"{((quote.get('price',0)-val.pe_fair_value)/val.pe_fair_value*100):+.1f}%"],
            ["Enterprise Value / EBITDA Multiple", f"₹{val.ev_ebitda_fair_value:,.2f}", f"₹{quote.get('price', 0):,.2f}", f"{((quote.get('price',0)-val.ev_ebitda_fair_value)/val.ev_ebitda_fair_value*100):+.1f}%"],
            ["<b>Composite Fair Value Target</b>", f"<b>₹{val.composite_fair_value:,.2f}</b>", f"₹{quote.get('price', 0):,.2f}", f"<b>{val.margin_of_safety_pct:+.1f}% (MoS)</b>"],
            ["Bear Case Scenario (-30% growth, +1.5% WACC)", f"₹{val.bear_case_value:,.2f}", f"₹{quote.get('price', 0):,.2f}", "Downside Floor"],
            ["Bull Case Scenario (+25% growth, -1.0% WACC)", f"₹{val.bull_case_value:,.2f}", f"₹{quote.get('price', 0):,.2f}", "Upside Blue Sky"]
        ]
        t_val = Table(val_data, colWidths=[200, 110, 110, 120])
        t_val.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#0284c7")),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 8),
            ('PADDING', (0,0), (-1,-1), 4),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#f1f5f9")])
        ]))
        elements.append(t_val)
        elements.append(Spacer(1, 10))

        # 4. Risk & Governance Surveillance
        elements.append(Paragraph("3. Forensic Governance & Balance Sheet Risk Matrix", h2_style))
        if risks:
            risk_rows = [["Risk Category", "Severity", "Evidentiary Trigger", "Primary Data Source"]]
            for r in risks[:4]:
                risk_rows.append([r.category, r.severity, r.title, r.evidence_source])
            t_risk = Table(risk_rows, colWidths=[90, 60, 240, 150])
            t_risk.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#e11d48")),
                ('TEXTCOLOR', (0,0), (-1,0), colors.white),
                ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('FONTSIZE', (0,0), (-1,-1), 8),
                ('PADDING', (0,0), (-1,-1), 4),
                ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#fff1f2")])
            ]))
            elements.append(t_risk)
        else:
            elements.append(Paragraph("No critical forensic red flags identified in latest audited statutory disclosures.", body_style))
        elements.append(Spacer(1, 10))

        # 5. Regulatory Disclaimer
        elements.append(Paragraph("4. Regulatory Compliance & Disclaimers", h2_style))
        disclaimer = (
            "<b>Disclaimer:</b> Bharat Value AI is an analytical research and decision-support tool designed for informational and "
            "educational purposes only. This report does not constitute personal investment advice, research report recommendations under "
            "SEBI (Research Analysts) Regulations, or an offer to buy or sell securities. Historical backtest and model figures are simulated. "
            "Equity investments are subject to market risks. Readers must perform independent due diligence before committing capital."
        )
        elements.append(Paragraph(disclaimer, ParagraphStyle("Disc", parent=body_style, fontSize=7, leading=10, textColor=colors.HexColor("#64748b"))))

        doc.build(elements)
        return str(file_path)

    def generate_csv_report(self, symbol: str) -> str:
        sym = symbol.upper().replace(".NS", "").replace(".BO", "")
        fund = fundamentals_engine.get_company_fundamentals(sym)
        val = fair_value_engine.evaluate_valuation(sym)
        quote = market_provider.get_quote(sym)

        now_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"BharatValue_Data_{sym}_{now_str}.csv"
        file_path = REPORTS_DIR / filename

        import csv
        with open(file_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Metric", "Value", "Unit / Notes"])
            writer.writerow(["Symbol", sym, "NSE Listed"])
            writer.writerow(["Current Price", quote.get("price"), "INR"])
            writer.writerow(["DCF Fair Value", val.dcf_fair_value, "INR"])
            writer.writerow(["Composite Fair Value", val.composite_fair_value, "INR"])
            writer.writerow(["Margin of Safety", f"{val.margin_of_safety_pct}%", val.valuation_status])
            writer.writerow(["Revenue", fund.get("revenue"), "INR Crores"])
            writer.writerow(["Net Profit", fund.get("net_profit"), "INR Crores"])
            writer.writerow(["Operating Margin", f"{fund.get('operating_margin_pct')}%", "Consolidated"])
            writer.writerow(["ROE", f"{fund.get('roe_pct')}%", "Percentage"])
            writer.writerow(["ROCE", f"{fund.get('roce_pct')}%", "Percentage"])
            writer.writerow(["Debt to Equity", fund.get("debt_to_equity"), "Ratio"])
            writer.writerow(["Altman Z-Score", fund.get("altman_z_score"), "Solvency"])

        return str(file_path)

report_generator = ResearchReportGenerator()
