"""
adapter_open_data_loader.py — Adapter for Open Data Loader PDF (Hancom, Apache 2.0).

Install:
    pip install open-data-loader-pdf
    # or: pip install odl-pdf   (verify package name on PyPI)

Runs fully offline. Has optional AI add-ons for OCR, table extraction,
and chart understanding. We test the base mode here (no AI add-ons)
and note where AI add-ons would improve things.
"""

from .base import BaseAdapter, ExtractionResult
import re


class OpenDataLoaderAdapter(BaseAdapter):
    TOOL_NAME = "open_data_loader"

    def __init__(self, use_ai_ocr: bool = False, use_ai_tables: bool = False):
        """
        use_ai_ocr    : enable the AI OCR add-on (needs internet / API key)
        use_ai_tables : enable the AI table add-on
        """
        self.use_ai_ocr    = use_ai_ocr
        self.use_ai_tables = use_ai_tables

    def _extract(self, pdf_path: str) -> ExtractionResult:
        # NOTE: The exact import path depends on the installed package version.
        # Adjust if the package name differs from what's on PyPI.
        try:
            from odl.document_loaders import PDFLoader   # try primary import
        except ImportError:
            from open_data_loader.pdf import PDFLoader   # fallback import path

        loader = PDFLoader(
            file_path     = pdf_path,
            enable_ocr    = self.use_ai_ocr,
            enable_tables = self.use_ai_tables,
        )

        # Load returns a list of Document objects (one per page typically)
        documents = loader.load()

        # ── Build page-separated text ─────────────────────────────────────
        pages_text = []
        for doc in documents:
            pages_text.append(doc.page_content)

        full_text = "\f".join(pages_text)

        # ── Headings: parse from text heuristically ───────────────────────
        # ODL doesn't expose a heading classifier out of the box,
        # so we fall back to detecting short ALL-CAPS or bold-marker lines.
        headings = _heuristic_headings(full_text)

        # ── Tables ────────────────────────────────────────────────────────
        tables = []
        for doc in documents:
            raw_tables = doc.metadata.get("tables", [])
            for t in raw_tables:
                # Each table may be a dict with "data" key or a raw grid
                if isinstance(t, dict):
                    tables.append(t.get("data", []))
                elif isinstance(t, list):
                    tables.append(t)

        return ExtractionResult(
            tool_name = self.TOOL_NAME,
            pdf_path  = pdf_path,
            text      = full_text,
            tables    = tables,
            headings  = headings,
            metadata  = {
                "n_pages":    len(documents),
                "ai_ocr":     self.use_ai_ocr,
                "ai_tables":  self.use_ai_tables,
            },
        )


def _heuristic_headings(text: str) -> list:
    """
    Simple heuristic: a heading is a line that is:
      - Shorter than 80 chars
      - Not ending with a period
      - Either starts with a digit+dot pattern (1. 1.1 etc.) or is ALL CAPS
    Returns list of (level, text).
    """
    headings = []
    for line in text.splitlines():
        s = line.strip()
        if not s or len(s) > 80 or s.endswith("."):
            continue
        # Numbered heading: "1.", "1.1", "1.1.1"
        if re.match(r"^\d+(\.\d+)*\.?\s+\S", s):
            depth = s.split()[0].count(".")
            headings.append((min(depth + 1, 6), s))
        # ALL CAPS heading
        elif s.isupper() and len(s) > 3:
            headings.append((2, s))
    return headings
