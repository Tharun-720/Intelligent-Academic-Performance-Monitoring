"""Institutional PDF report generator package for TREKVERSE."""
import sys
from pathlib import Path

# Ensure root package import
_pkg_root = Path(__file__).resolve().parent.parent
if str(_pkg_root) not in sys.path:
    sys.path.insert(0, str(_pkg_root))

from reports.report_generator import generate_student_pdf_report

__all__ = ["generate_student_pdf_report"]

