#!/usr/bin/env python3
"""Build a searchable PDF by rendering each page and running tesseract per page.
Bypasses ocrmypdf. NOTE: in this sandboxed environment the child `tesseract`
process can only read work files placed *flat* in /tmp, and only when the parent
runs with cwd=/tmp. So: run `cd /tmp && python3 ocr_to_pdf.py 2013 2014 2017`,
work files use a flat /tmp prefix, and output PDFs are written flat in /tmp.
The resulting PDF has a real text layer the coordinate-based extractors can read.
"""
import fitz, subprocess, sys, os, glob

WORK = "/tmp"

def ocr_pdf(src, dst, dpi=400):
    stem = os.path.splitext(os.path.basename(src))[0]
    pref = f"{WORK}/_ocr_{stem}_"
    d = fitz.open(src)
    out = fitz.open()
    opened = []
    for pg in range(d.page_count):
        png = f"{pref}{pg}.png"; base = f"{pref}{pg}"
        d[pg].get_pixmap(dpi=dpi).save(png)
        subprocess.run(["tesseract", png, base, "-l", "eng", "--psm", "6", "pdf"],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        pdfp = base + ".pdf"
        ok = False
        if os.path.exists(pdfp):
            one = fitz.open(pdfp); opened.append(one)
            if one.page_count >= 1:
                out.insert_pdf(one); ok = True
        if not ok:
            out.new_page(width=d[pg].rect.width, height=d[pg].rect.height)
        os.remove(png)
        if pg % 10 == 0:
            print(f"  {stem}: page {pg}/{d.page_count}", flush=True)
    out.save(dst, deflate=True)
    for o in opened:
        o.close()
    for p in glob.glob(pref + "*.pdf"):
        os.remove(p)
    chars = sum(len(out[p].get_text()) for p in range(out.page_count))
    print(f"[ocr] {dst}  ({out.page_count} pages, text chars={chars})")

if __name__ == "__main__":
    for y in sys.argv[1:]:
        ocr_pdf(f"/Users/amin/Documents/Research/cancer_research/Cancer_Reports/{y}.pdf",
                f"/tmp/{y}.ocr.pdf")          # flat output; tesseract needs flat cwd/paths
