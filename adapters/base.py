"""
base.py — Abstract base class for all PDF extraction adapters.
This guarantees a uniform input/output contract so the scoring 
scripts can treat all tools identically.

"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional
import time
import tracemalloc
import traceback


# Output contract
@dataclass
class ExtractionResult:
    # Everything an adapter must return after processing one PDF.
    tool_name:   str
    pdf_path:    str
    text:        str                        = ""
    tables:      list                       = field(default_factory=list)
    headings:    list                       = field(default_factory=list)
    metadata:    dict                       = field(default_factory=dict)
    elapsed_sec: float                      = 0.0
    peak_mb:     float                      = 0.0
    cost_usd:    float                      = 0.0
    error:       Optional[str]              = None

    def pages(self):
        """Return text split by page (form-feed separator)."""
        return self.text.split("\f")

    def page(self, n: int) -> str:
        """Return text of page n (0-indexed)."""
        pages = self.pages()
        return pages[n] if n < len(pages) else ""

    def succeeded(self) -> bool:
        return self.error is None

    def summary(self) -> str:
        status = "OK" if self.succeeded() else f"ERROR: {self.error[:60]}"
        return (
            f"[{self.tool_name}] {Path(self.pdf_path).name} | "
            f"{status} | {self.elapsed_sec:.1f}s | "
            f"{self.peak_mb:.0f} MB | ${self.cost_usd:.4f}"
        )

# Abstract base adapter

class BaseAdapter(ABC):

    TOOL_NAME: str = "unnamed"  # override in each subclass

    def extract(self, pdf_path) -> ExtractionResult:
        """
        Public entry point. Wraps _extract() with:
          - wall-clock timing
          - peak RAM tracking (tracemalloc)
          - exception catching (so one crash doesn't stop the whole run)
        """
        pdf_path = str(pdf_path)

        tracemalloc.start()
        t0 = time.perf_counter()

        try:
            result = self._extract(pdf_path)
            result.tool_name = self.TOOL_NAME
            result.pdf_path  = pdf_path
        except Exception:
            result = ExtractionResult(
                tool_name = self.TOOL_NAME,
                pdf_path  = pdf_path,
                error     = traceback.format_exc(),
            )

        result.elapsed_sec = time.perf_counter() - t0
        _, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        result.peak_mb = peak / 1_048_576   # bytes -> MB

        return result

    @abstractmethod
    def _extract(self, pdf_path: str) -> ExtractionResult:
        # Implement the actual extraction here.
        ...

    def __repr__(self) -> str:
        return f"<Adapter: {self.TOOL_NAME}>"