"""
run_all.py — Run every adapter on every PDF and save results.

Usage:
    python scripts/run_all.py

Outputs for each (tool, pdf) pair:
    outputs/<tool_name>/<pdf_stem>/text.md
    outputs/<tool_name>/<pdf_stem>/tables/table_N.csv
    outputs/<tool_name>/<pdf_stem>/meta.json
"""

import json, csv, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from adapters import ALL_ADAPTERS

CORPUS_DIR = ROOT / "corpus"
OUTPUT_DIR = ROOT / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)

pdf_files = sorted(CORPUS_DIR.glob("*.pdf"))
if not pdf_files:
    print(f"No PDFs found in {CORPUS_DIR}. Add your 5 PDFs and re-run.")
    sys.exit(1)

print(f"Found {len(pdf_files)} PDFs and {len(ALL_ADAPTERS)} adapters.")
print(f"Total runs: {len(pdf_files) * len(ALL_ADAPTERS)}\n")

summary_rows = []

for adapter in ALL_ADAPTERS:
    for pdf_path in pdf_files:
        print(f"Running [{adapter.TOOL_NAME}] {pdf_path.name} ...", end=" ", flush=True)
        result = adapter.extract(pdf_path)
        print(f"{'OK' if result.succeeded() else 'ERROR'} | {result.elapsed_sec:.1f}s | {result.peak_mb:.0f}MB")

        out_dir = OUTPUT_DIR / adapter.TOOL_NAME / pdf_path.stem
        out_dir.mkdir(parents=True, exist_ok=True)

        (out_dir / "text.md").write_text(result.text, encoding="utf-8")

        tables_dir = out_dir / "tables"
        tables_dir.mkdir(exist_ok=True)
        for i, table in enumerate(result.tables):
            with open(tables_dir / f"table_{i+1:02d}.csv", "w", newline="", encoding="utf-8") as f:
                csv.writer(f).writerows(table)

        meta = {
            "tool": result.tool_name, "pdf": pdf_path.name,
            "elapsed_sec": round(result.elapsed_sec, 2),
            "peak_mb": round(result.peak_mb, 1),
            "cost_usd": round(result.cost_usd, 4),
            "n_tables": len(result.tables),
            "n_headings": len(result.headings),
            "error": result.error,
            **result.metadata,
        }
        (out_dir / "meta.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False))

        summary_rows.append({
            "tool": adapter.TOOL_NAME, "pdf": pdf_path.name,
            "status": "OK" if result.succeeded() else "ERROR",
            "elapsed_s": round(result.elapsed_sec, 2),
            "peak_mb": round(result.peak_mb, 1),
            "cost_usd": round(result.cost_usd, 4),
            "n_tables": len(result.tables),
            "n_headings": len(result.headings),
            "error": (result.error or "")[:120],
        })

summary_csv = OUTPUT_DIR / "run_summary.csv"
with open(summary_csv, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=list(summary_rows[0].keys()))
    writer.writeheader()
    writer.writerows(summary_rows)

print(f"\nDone. Summary: {summary_csv}")
ok = sum(1 for r in summary_rows if r['status'] == 'OK')
print(f"Successful runs: {ok} / {len(summary_rows)}")
