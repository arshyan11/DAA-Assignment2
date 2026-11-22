"""make_submission.py - zip code, outputs, and report PDF into submission.zip."""

import shutil
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).parent.resolve()


def main():
    out_zip = ROOT / "submission.zip"
    parent_zip = ROOT.parent / "submission.zip"

    exclude_dirs = {".git", "__pycache__", ".pytest_cache", "venv", ".venv", "env"}
    exclude_ext = {".pyc", ".pyo", ".md"}
    exclude_names = {"README.md", ".gitignore", "submission.zip"}

    include_dirs = [
        ROOT / "src",
        ROOT / "tests",
        ROOT / "output",
    ]

    include_files = [
        ROOT / "arshyan_tahir_assignment2_daa.pdf",
        ROOT / "DAA_CLO4_Evaluation_Report.pdf",
        ROOT / "run_all.py",
        ROOT / "generate_pdf_report.py",
        ROOT / "make_submission.py",
        ROOT / "requirements.txt",
        ROOT / "__init__.py",
    ]

    # Ensure arshyan_tahir_assignment2_daa.pdf is copied into algo_eval if present in parent
    parent_pdf = ROOT.parent / "arshyan_tahir_assignment2_daa.pdf"
    local_pdf = ROOT / "arshyan_tahir_assignment2_daa.pdf"
    if parent_pdf.exists() and not local_pdf.exists():
        shutil.copy2(parent_pdf, local_pdf)

    added = 0
    seen_arcnames = set()

    with zipfile.ZipFile(out_zip, "w", zipfile.ZIP_DEFLATED) as zf:
        # 1. Add primary report at root of zip for immediate visibility
        if parent_pdf.exists():
            arcname = "arshyan_tahir_assignment2_daa.pdf"
            zf.write(parent_pdf, arcname)
            seen_arcnames.add(arcname)
            added += 1

        # 2. Add files from include_dirs
        for d in include_dirs:
            if not d.exists():
                continue
            for f in sorted(d.rglob("*")):
                if f.is_file() and f.suffix.lower() not in exclude_ext and f.name not in exclude_names:
                    if not any(part in exclude_dirs for part in f.parts):
                        arcname = str(f.relative_to(ROOT.parent)).replace("\\", "/")
                        if arcname not in seen_arcnames:
                            zf.write(f, arcname)
                            seen_arcnames.add(arcname)
                            added += 1

        # 3. Add root files
        for f in include_files:
            if f.exists() and f.is_file() and f.suffix.lower() not in exclude_ext and f.name not in exclude_names:
                arcname = str(f.relative_to(ROOT.parent)).replace("\\", "/")
                if arcname not in seen_arcnames:
                    zf.write(f, arcname)
                    seen_arcnames.add(arcname)
                    added += 1

    # Copy zip to workspace root as well
    if parent_zip != out_zip:
        shutil.copy2(out_zip, parent_zip)

    size_mb = out_zip.stat().st_size / (1024 * 1024)
    print(f"Created {out_zip} and {parent_zip} ({size_mb:.2f} MB, {added} files)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
