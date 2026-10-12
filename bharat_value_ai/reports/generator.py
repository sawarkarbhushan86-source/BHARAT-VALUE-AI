"""Institutional Equity Research Report Generator (ReportLab PDF & CSV Exports) with Strict Snapshot Parity."""
import os
import datetime
import csv
from pathlib import Path
from typing import Dict, Any

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether, HRFlowable
)

from bharat_value_ai.services.snapshot_service import snapshot_service, UnifiedCompanySnapshot
from bharat_value_ai.analysis.risk_governance import risk_engine

REPORTS_DIR = Path("./data/reports")
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

class ResearchReportGenerator:
    """Generates institutional PDF and CSV equity research reports tied directly to verified company snapshots."""

    def generate_pdf_report(self, symbol: str) -> str:
        snapshot: UnifiedCompanySnapshot = snapshot_service.get_snapshot(symbol)
        sym = snapshot.symbol
        company_name = snapshot.company_name
        sector = snapshot.sector
        fund = snapshot.fundamentals
        val = snapshot.valuation
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
            fontSize=10,
            leading=14,
            textColor=colors.HexColor("#475569")
        )
        h2_style = ParagraphStyle(
            "SectionH2",
            parent=styles["Heading2"],
            fontSize=12,
            leading=16,
            textColor=colors.HexColor("#1e293b"),
            spaceBefore=8,
            spaceAfter=4,
            fontName="Helvetica-Bold"
        )
        body_style = ParagraphStyle(
            "ReportBody",
            parent=styles["Normal"],
            fontSize=9,
            leading=13,
            textColor=colors.HexColor("#334155")
        )

        elements = []

        # Header Title
        elements.append(Paragraph(f"BHARAT VALUE AI — INSTITUTIONAL EQUITY RESEARCH", ParagraphStyle("HeaderSub", parent=subtitle_style, fontSize=8, textColor=colors.HexColor("#2563eb"), fontName="Helvetica-Bold")))
        elements.append(Spacer(1, 4))
        elements.append(Paragraph(f"{company_name} ({sym})", title_style))
        elements.append(Paragraph(
            f"Sector: <b>{sector}</b> | Industry: <b>{snapshot.industry}</b> | Exchange: <b>NSE / BSE</b><br/>"
            f"Snapshot ID: <code>{snapshot.snapshot_id}</code> | Generated: <b>{snapshot.created_at_ist}</b> | Quote Status: <b>{snapshot.price_status}</b>",
            subtitle_style
        ))
        elements.append(Spacer(1, 8))
        elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#2563eb"), spaceAfter=10))

        # 1. Executive Snapshot Card Table
        card_data = [
            [
                Paragraph("<b>Verified Market Price</b>", body_style),
                Paragraph(f"<b>₹{snapshot.current_price:,.2f}</b>", body_style),
                Paragraph("<b>Modeled Fair Value</b>", body_style),
                Paragraph(f"<b>₹{snapshot.fair_value:,.2f}</b>", body_style),
            ],
            [
                Paragraph("<b>Margin of Safety</b>", body_style),
                Paragraph(f"<b>{snapshot.margin_of_safety_pct:+.1f}%</b> ({snapshot.valuation_status})", body_style),
                Paragraph("<b>Model Architecture</b>", body_style),
                Paragraph(f"<b>{snapshot.valuation_model_type}</b>", body_style)
            ],
            [
                Paragraph("<b>Quality Score</b>", body_style),
                Paragraph(f"<b>{snapshot.quality_score:.1f} / 100</b>", body_style),
                Paragraph("<b>Compounding Tier</b>", body_style),
                Paragraph(f"<b>{snapshot.compounding_tier}</b>", body_style)
            ]
        ]
        t_card = Table(card_data, colWidths=[130, 140, 130, 140])
        t_card.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f8fafc")),
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#cbd5e1")),
            ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
            ('PADDING', (0,0), (-1,-1), 5),
            ('FONTSIZE', (0,0), (-1,-1), 9),
        ]))
        elements.append(t_card)
        elements.append(Spacer(1, 10))

        # 2. Financial Fundamentals Table
        elements.append(Paragraph(f"1. Audited Financial Statements ({snapshot.reporting_period} — {snapshot.filing_type})", h2_style))
        fund_table_data = [
            ["Metric", "Consolidated Value", "Benchmark Context / Notes"],
            ["Total Revenue", f"₹{fund.get('revenue', 'N/A'):,} Cr" if fund.get('revenue') else "N/A", "Operating Top-Line"],
            ["Operating EBITDA", f"₹{fund.get('operating_profit', 'N/A'):,} Cr" if fund.get('operating_profit') else "N/A", f"Margin: {fund.get('operating_margin_pct', 'N/A')}%"],
            ["Net Profit (PAT)", f"₹{fund.get('net_profit', 'N/A'):,} Cr" if fund.get('net_profit') else "N/A", f"Margin: {fund.get('net_margin_pct', 'N/A')}%"],
            ["Earnings Per Share (EPS)", f"₹{fund.get('eps', 'N/A')}" if fund.get('eps') else "N/A", f"P/E Ratio: {fund.get('pe_ratio', 'N/A')}x"],
            ["Return on Equity (ROE)", f"{fund.get('roe_pct', 'N/A')}%", "Net Profit / Shareholder Equity"],
            ["Return on Capital (ROCE)", f"{fund.get('roce_pct', 'N/A')}%" if fund.get('roce_pct') is not None else "N/A (BFSI)", "EBIT / Capital Employed"],
            ["Debt to Equity Ratio", f"{fund.get('debt_to_equity', 'N/A')}x" if fund.get('debt_to_equity') is not None else "N/A (Bank/NBFC)", "Solvency Balance Sheet Metric"],
            ["Free Cash Flow (FCF)", f"₹{fund.get('free_cash_flow', 'N/A'):,} Cr" if fund.get('free_cash_flow') else "N/A", "Operating Cash - Capex"],
            ["DuPont Driver Summary", snapshot.dupont_drivers[:40] + "...", "Three-Stage ROE Breakdown"]
        ]
        t_fund = Table(fund_table_data, colWidths=[160, 160, 220])
        t_fund.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1e293b")),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 8),
            ('PADDING', (0,0), (-1,-1), 4),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#f8fafc")])
        ]))
        elements.append(t_fund)
        elements.append(Spacer(1, 10))

        # 3. Valuation & Scenarios
        elements.append(Paragraph("2. Intrinsic Valuation & Scenario Matrix", h2_style))
        val_table_data = [
            ["Scenario", "Modeled Value (INR)", "Primary Underlying Assumptions"],
            ["Bear Case", f"₹{val.get('bear_case_value', 0):,.2f}", "Macro deceleration / compressed margin / elevated discount rate"],
            ["Base Case (Composite)", f"₹{snapshot.fair_value:,.2f}", f"Sector model: {snapshot.valuation_model_type}"],
            ["Bull Case", f"₹{val.get('bull_case_value', 0):,.2f}", "Accelerated demand / margin expansion / normalized cost of capital"]
        ]
        t_val = Table(val_table_data, colWidths=[140, 140, 260])
        t_val.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1e293b")),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 8),
            ('PADDING', (0,0), (-1,-1), 4),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#f8fafc")])
        ]))
        elements.append(t_val)
        elements.append(Spacer(1, 10))

        # 4. Forensic & Governance Risks
        elements.append(Paragraph(f"3. Forensic Risk Indicators (Detected: {snapshot.active_risk_flags_count})", h2_style))
        if risks:
            risk_table_data = [["Flag Severity", "Risk Title", "Forensic Indicator Context"]]
            for r in risks[:4]:
                risk_table_data.append([r.severity, r.title[:35], r.description[:55] + "..."])
            t_risk = Table(risk_table_data, colWidths=[90, 180, 270])
            t_risk.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#dc2626")),
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
            "<b>Disclaimer:</b> Bharat Value AI is an analytical research and decision-support platform designed for informational and "
            "educational purposes only. This report does not constitute personal investment advice or research analyst recommendations under "
            "SEBI (Research Analysts) Regulations. Modeled figures are mathematical estimates. "
            "Equity investments are subject to market risks. Readers must perform independent due diligence before committing capital."
        )
        elements.append(Paragraph(disclaimer, ParagraphStyle("Disc", parent=body_style, fontSize=7, leading=10, textColor=colors.HexColor("#64748b"))))

        doc.build(elements)
        return str(file_path)

    def generate_csv_report(self, symbol: str) -> str:
        snapshot: UnifiedCompanySnapshot = snapshot_service.get_snapshot(symbol)
        sym = snapshot.symbol
        fund = snapshot.fundamentals
        val = snapshot.valuation

        now_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"BharatValue_Data_{sym}_{now_str}.csv"
        file_path = REPORTS_DIR / filename

        with open(file_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Metric", "Value", "Unit / Notes"])
            writer.writerow(["Snapshot ID", snapshot.snapshot_id, "Unique Audit Identifier"])
            writer.writerow(["Symbol", sym, "NSE Canonical Identifier"])
            writer.writerow(["Company Name", snapshot.company_name, "Registered Name"])
            writer.writerow(["Sector", snapshot.sector, "Industry Classification"])
            writer.writerow(["Current Price", snapshot.current_price, "INR per share"])
            writer.writerow(["Quote Status", snapshot.price_status, "LIVE / DELAYED / LAST AVAILABLE"])
            writer.writerow(["Quote Timestamp", snapshot.price_timestamp_ist, "IST Observation Time"])
            writer.writerow(["DCF Fair Value", val.get("dcf_fair_value", snapshot.fair_value), "INR per share"])
            writer.writerow(["Composite Fair Value", snapshot.fair_value, "INR per share"])
            writer.writerow(["Margin of Safety", f"{snapshot.margin_of_safety_pct}%", snapshot.valuation_status])
            writer.writerow(["Valuation Model", snapshot.valuation_model_type, "Sector Architecture"])
            writer.writerow(["Bear Case Fair Value", val.get("bear_case_value"), "INR per share"])
            writer.writerow(["Bull Case Fair Value", val.get("bull_case_value"), "INR per share"])
            writer.writerow(["Revenue", fund.get("revenue"), "INR Crores"])
            writer.writerow(["Net Profit (PAT)", fund.get("net_profit"), "INR Crores"])
            writer.writerow(["Operating Margin", f"{fund.get('operating_margin_pct')}%", "Consolidated"])
            writer.writerow(["ROE", f"{fund.get('roe_pct')}%", "Percentage"])
            writer.writerow(["ROCE", f"{fund.get('roce_pct')}%", "Percentage"])
            writer.writerow(["Debt to Equity", fund.get("debt_to_equity"), "Ratio"])
            writer.writerow(["Quality Score", f"{snapshot.quality_score}/100", snapshot.compounding_tier])
            writer.writerow(["Active Risk Flags", snapshot.active_risk_flags_count, "Forensic Scanner Count"])
            writer.writerow(["Reporting Period", snapshot.reporting_period, snapshot.filing_type])

        return str(file_path)

report_generator = ResearchReportGenerator()
