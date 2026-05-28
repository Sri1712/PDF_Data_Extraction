"""
adapter_pymupdf4llm.py — Adapter for PyMuPDF4LLM (simplest baseline).

Install:
    pip install pymupdf4llm

PyMuPDF4LLM converts a PDF to Markdown using PyMuPDF's built-in parser.
It is fast, needs no GPU, and works entirely offline.
"""

import re
from .base import BaseAdapter, ExtractionResult


class PyMuPDF4LLMAdapter(BaseAdapter):
    TOOL_NAME = "pymupdf4llm"

    def _extract(self, pdf_path: str) -> ExtractionResult:

        import pymupdf4llm   
        import fitz          

        # Text extraction 
        md_text = pymupdf4llm.to_markdown(pdf_path)
        pages_text = re.split(r"\n-{3,}\n", md_text)
        full_text  = "\f".join(pages_text)

        # Heading extraction 
        headings = []
        for line in md_text.splitlines():
            m = re.match(r"^(#{1,6})\s+(.*)", line)
            if m:
                level = len(m.group(1))
                title = m.group(2).strip()
                headings.append((level, title))

        # Table extraction 
        tables = _parse_markdown_tables(md_text)

        # Page count metadata
        doc = fitz.open(pdf_path)
        n_pages = doc.page_count
        doc.close()

        return ExtractionResult(
            tool_name = self.TOOL_NAME,
            pdf_path  = pdf_path,
            text      = full_text,
            tables    = tables,
            headings  = headings,
            metadata  = {"n_pages": n_pages, "format": "markdown"},
        )


# Helper: parse Markdown pipe tables into list[list[str]]
def _parse_markdown_tables(md: str) -> list:
    """
    Find all Markdown pipe tables in `md` and return them as
    list-of-lists (rows × cols). Separator rows (|---|---|) are skipped.
    """
    tables  = []
    current = []

    for line in md.splitlines():
        stripped = line.strip()
        if stripped.startswith("|") and stripped.endswith("|"):
            # Skip pure separator rows like |---|---|
            cells = [c.strip() for c in stripped.strip("|").split("|")]
            if all(re.match(r"^[-:]+$", c) for c in cells if c):
                continue
            current.append(cells)
        else:
            if current:
                tables.append(current)
                current = []

    if current:
        tables.append(current)

    return tables