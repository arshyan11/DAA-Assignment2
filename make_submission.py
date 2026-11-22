"""make_submission.py - zip code, outputs, and README into submission.zip."""

import zipfile
import sys
from pathlib import Path

ROOT = Path(__file__).parent


def main():
    out_zip = ROOT / "submission.zip"
    exclude_dirs = {".git", "__pycache__", ".pytest_cache", "venv", ".venv", "env"}
    exclude_ext = {".pyc", ".pyo"}

    include_dirs = [
        ROOT / "src",
        ROOT / "tests",
        ROOT / "report_templates",
        ROOT / "output" / "figures",
        ROOT / "output" / "tables",
    ]
    include_files = [
        ROOT / "run_all.py",
        ROOT / "generate_pdf_report.py",
        ROOT / "make_submission.py",
        ROOT / "requirements.txt",
        ROOT / "README.md",
        ROOT / "__init__.py",
        ROOT / "output" / "DAA_CLO4_Evaluation_Report.pdf",
        ROOT / "output" / "complexity_table.csv",
        ROOT / "output" / "summary_sorting.csv",
        ROOT / "output" / "summary_graph.csv",
        ROOT / "output" / "scores_sorting.csv",
        ROOT / "output" / "scores_graph.csv",
        ROOT / "output" / "fit_results.csv",
        ROOT / "output" / "environment.json",
        ROOT / "output" / "correctness_and_stability_report.txt",
        ROOT / "output" / "dijkstra_negative_weight_failures.csv",
    ]

    added = 0
    with zipfile.ZipFile(out_zip, "w", zipfile.ZIP_DEFLATED) as zf:
        for d in include_dirs:
            if not d.exists():
                continue
            for f in d.rglob("*"):
                if f.is_file() and f.suffix not in exclude_ext:
                    if not any(part in exclude_dirs for part in f.parts):
                        arcname = f.relative_to(ROOT.parent)
                        zf.write(f, arcname)
                        added += 1

        for f in include_files:
            if f.exists() and f.is_file():
                arcname = f.relative_to(ROOT.parent)
                zf.write(f, arcname)
                added += 1

    size_mb = out_zip.stat().st_size / (1024 * 1024)
    print(f"Created {out_zip} ({size_mb:.2f} MB, {added} files)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
