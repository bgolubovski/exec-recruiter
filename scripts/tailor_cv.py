#!/usr/bin/env python3
"""Tailor a baseline CV docx to a target role.

Reads the baseline docx (default: templates/cv-baseline.docx), applies a set of
targeted text replacements derived from the role's JD + the user's pattern-match
anchors, and writes a tailored docx + PDF to the role's outreach folder.

Discipline (per config/outreach-style.yaml):
  - identity stable: name, headline scaffold, dates, education never change
  - max 2 of 6 career-highlight cells changed
  - one phrase per past role's italic context line
  - adjacency sentence at the end of executive summary lands the role-specific analogue
  - geo header swap per geo-rules.yaml conditional

Usage:
  python3 tailor_cv.py \
    --role-slug brevia-vp-product \
    --baseline /path/to/templates/cv-baseline.docx \
    --replacements /path/to/replacements.json \
    --out-dir /path/to/outreach/brevia-vp-product

The replacements.json file is a flat dict: {"old_string": "new_string", ...}.
Each old_string must appear in the docx XML; each new_string is XML-escaped if it
contains '&' (the script auto-escapes to '&amp;' for safety).

The baseline deliberately carries no tailored-for line. Pass --tailored-for to
insert one per role: a small italic gray centered paragraph placed between the
contact line and the EXECUTIVE SUMMARY heading, e.g.
  --tailored-for "Tailored for Brevia, VP Product"
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
from zipfile import ZipFile, ZIP_DEFLATED


def xml_escape_amp(s: str) -> str:
    """Escape unescaped & in a replacement string. Already-escaped entities pass through."""
    import re
    return re.sub(r'&(?!amp;|apos;|quot;|lt;|gt;|#)', '&amp;', s)


TAILORED_FOR_PARA = (
    '<w:p><w:pPr><w:spacing w:after="40"/><w:jc w:val="center"/></w:pPr>'
    '<w:r><w:rPr>'
    '<w:rFonts w:ascii="Arial" w:cs="Arial" w:eastAsia="Arial" w:hAnsi="Arial"/>'
    '<w:i/><w:iCs/><w:color w:val="808080"/><w:sz w:val="18"/><w:szCs w:val="18"/>'
    '</w:rPr><w:t xml:space="preserve">{text}</w:t></w:r></w:p>'
)


def insert_tailored_for(xml: str, tag_text: str) -> str:
    """Insert the tailored-for paragraph immediately before the paragraph that
    holds the EXECUTIVE SUMMARY heading (i.e. just after the contact line)."""
    import re
    heading_at = xml.find("EXECUTIVE SUMMARY")
    if heading_at == -1:
        raise ValueError("EXECUTIVE SUMMARY heading not found in document.xml; cannot place tailored-for line")
    para_starts = [m.start() for m in re.finditer(r"<w:p[ >]", xml[:heading_at])]
    if not para_starts:
        raise ValueError("No paragraph start found before EXECUTIVE SUMMARY heading")
    at = para_starts[-1]
    para = TAILORED_FOR_PARA.format(text=xml_escape_amp(tag_text))
    return xml[:at] + para + xml[at:]


def tailor(baseline_path: str, replacements: dict, out_path: str, tailored_for: str = None) -> dict:
    """Apply replacements to baseline docx; write to out_path. Return stats."""
    if not os.path.exists(baseline_path):
        raise FileNotFoundError(f"Baseline CV not found: {baseline_path}")

    stats = {"applied": 0, "missed": [], "out_path": out_path, "tailored_for_inserted": False}

    with ZipFile(baseline_path, "r") as src:
        names = src.namelist()
        with ZipFile(out_path, "w", ZIP_DEFLATED) as out:
            for n in names:
                data = src.read(n)
                if n == "word/document.xml":
                    text = data.decode("utf-8")
                    for old, new in replacements.items():
                        new_safe = xml_escape_amp(new)
                        if old not in text:
                            stats["missed"].append(old[:80])
                        else:
                            text = text.replace(old, new_safe)
                            stats["applied"] += 1
                    if tailored_for:
                        text = insert_tailored_for(text, tailored_for)
                        stats["tailored_for_inserted"] = True
                    data = text.encode("utf-8")
                out.writestr(n, data)
    return stats


def docx_to_pdf(docx_path: str, out_dir: str) -> str:
    """Convert docx to PDF via libreoffice. Returns the resulting PDF path."""
    binary = shutil.which("libreoffice") or shutil.which("soffice")
    if not binary:
        raise RuntimeError("Neither 'libreoffice' nor 'soffice' found on PATH")
    cmd = [
        binary, "--headless", "--convert-to", "pdf",
        "--outdir", out_dir, docx_path,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    pdf_path = docx_path.replace(".docx", ".pdf")
    if not os.path.exists(pdf_path):
        raise RuntimeError(
            f"PDF conversion failed.\nstdout: {result.stdout}\nstderr: {result.stderr}"
        )
    return pdf_path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--role-slug", required=True, help="kebab-case slug for the role")
    ap.add_argument("--baseline", required=True, help="path to baseline CV docx")
    ap.add_argument("--replacements", required=True, help="path to replacements JSON file")
    ap.add_argument("--out-dir", required=True, help="output directory (per-role outreach folder)")
    ap.add_argument(
        "--tailored-for",
        help='full tailored-for line to insert before EXECUTIVE SUMMARY, e.g. "Tailored for Brevia, VP Product"',
    )
    ap.add_argument("--no-pdf", action="store_true", help="skip PDF generation")
    args = ap.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)

    with open(args.replacements, "r", encoding="utf-8") as f:
        replacements = json.load(f)

    out_docx = os.path.join(
        args.out_dir, f"Operator-FirstName-CV-{args.role_slug}.docx"
    )
    stats = tailor(args.baseline, replacements, out_docx, tailored_for=args.tailored_for)

    print(f"docx written: {out_docx}")
    print(f"  applied:    {stats['applied']}")
    print(f"  tailored-for inserted: {stats['tailored_for_inserted']}")
    if stats["missed"]:
        print(f"  MISSED ({len(stats['missed'])}):")
        for m in stats["missed"]:
            print(f"    - {m!r}")

    if not args.no_pdf:
        try:
            pdf_path = docx_to_pdf(out_docx, args.out_dir)
            print(f"pdf  written: {pdf_path}")
        except Exception as e:
            print(f"PDF generation failed: {e}", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()
