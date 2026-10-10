"""Unit tests for Research Report PDF and CSV exports."""
import os
from pathlib import Path
from bharat_value_ai.reports.generator import report_generator

def test_generate_pdf_report():
    pdf_path = report_generator.generate_pdf_report("CDSL")
    assert os.path.exists(pdf_path)
    assert pdf_path.endswith(".pdf")
    # PDF must not be empty
    assert os.path.getsize(pdf_path) > 2000

def test_generate_csv_report():
    csv_path = report_generator.generate_csv_report("CDSL")
    assert os.path.exists(csv_path)
    assert csv_path.endswith(".csv")
    with open(csv_path, "r", encoding="utf-8") as f:
        content = f.read()
        assert "Metric,Value,Unit / Notes" in content
        assert "CDSL" in content
        assert "DCF Fair Value" in content
