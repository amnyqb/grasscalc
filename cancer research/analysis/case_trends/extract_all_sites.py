#!/usr/bin/env python3
"""All cancer sites x sex x nationality, from Saudi Cancer Registry annual reports.

Emits a long-format table:  year, population, sex, icd_code, site, count, crude, asr, source

It auto-detects, on every page, two kinds of per-site incidence tables and reads
them by WORD COORDINATES (robust to the row-major vs column-major text-extraction
differences across report years):

  SUMMARY  ("Number, %, (CIR), ASR, Cumulative ... by Primary Site and Sex/Gender")
     - one page carries BOTH sexes; columns per sex = No, %, Crude/CIR, ASR, Cum, Cum.
     - Saudi-nationals only (the registry publishes no non-Saudi summary).
  BY-AGE   ("Age-specific (AIR), Age-standardized (ASR) ... by Primary Site and Age")
     - one page per sex; row = count(All-Ages, first cell), age-specific rates,
       Crude (2nd-last), ASR (last cell). Exists for BOTH Saudi and non-Saudi.

Population is read from the page title (normalised, so 'Non- Saudi' / 'Non-Sau-di'
all match). For Saudi years that have BOTH tables the SUMMARY is preferred (it
carries more sites + crude); the by-age table is the source for non-Saudi and for
Saudi years without a summary. The two agree where they overlap (validated:
Saudi male ASR identical across all common sites, 2008 & 2023).

INTEGRITY: only printed values; nothing modelled. ASR = World standard /100,000.
COUNTS != RATES. 2020 is a COVID registration artifact. Non-Saudi (expatriate)
rates are interpretively weak (young population; many diagnosed/treated abroad).
Image/garbled years are handled by the OCR pipeline, not guessed here.

USAGE
    python3 extract_all_sites.py /path/to/dir_with_pdfs
Outputs: data/scr_all_sites_long.csv
"""
import fitz, re, csv, sys, glob, os

NUM = re.compile(r'^-?\d[\d,]*(?:\.\d+)?$')
AGE = re.compile(r'\b0\s*-\s*4\b|\b5\s*-\s*9\b|\b10\s*-\s*14\b')

# Years whose only readable tables are OCR-derived: dense numeric OCR is not
# reliable cell-by-cell (e.g. 2014 lung female ASR mis-read 1.4 -> 14.0), so the
# all-sites TABLE data for these years is excluded. Their lung series is still
# carried separately from the low-risk OCR'd NARRATIVE (see extract_lung_series.py).
OCR_UNRELIABLE = {2013, 2014, 2017}


def norm(s):
    return re.sub(r'[\s\-]', '', s.lower())


def population(text):
    n = norm(text)
    if "nonsaudi" in n:
        return "non-Saudi"
    if "saudi" in n:
        return "Saudi"
    return None


def merge_row(words, yc, tol=3.2):
    band = sorted((w for w in words if abs((w[1] + w[3]) / 2 - yc) < tol), key=lambda w: w[0])
    merged = []
    for w in band:
        if merged and (w[0] - merged[-1][2]) < 5 and merged[-1][1].isdigit() and w[4].isdigit():
            merged[-1] = (merged[-1][0], merged[-1][1] + w[4], w[2]); continue
        merged.append((w[0], w[4], w[2]))
    return [t for _, t, _ in merged]


def site_and_nums(cells):
    """Split a row's cell-texts into (site_label, [numeric strings as-is])."""
    first = next((i for i, t in enumerate(cells)
                  if NUM.match(t.replace(',', '').replace('%', '')) and t not in ('%',)), None)
    if first is None:
        return None, []
    site = " ".join(c for c in cells[:first] if not re.match(r'^[\d.,%]+$', c)).strip()
    return site, cells[first:]


def num(x):
    return float(x.replace(',', '').replace('%', ''))


def parse_summary(page):
    """-> list of (code, site, sex, count, crude, asr) for both sexes."""
    ws = page.get_text("words")
    rows = []
    for c in [w for w in ws if re.match(r'^C\d', w[4].replace(' ', ''))]:
        code = c[4].replace(' ', '')
        cells = merge_row(ws, (c[1] + c[3]) / 2)
        site, data = site_and_nums(cells)
        if not data:
            continue
        pct = [i for i, t in enumerate(data) if "%" in t]
        try:
            if len(pct) >= 2:
                mi, fi = pct[0], pct[1]
                rows.append((code, site, "male",   int(num(data[mi - 1])), num(data[mi + 1]), num(data[mi + 2])))
                rows.append((code, site, "female", int(num(data[fi - 1])), num(data[fi + 1]), num(data[fi + 2])))
            else:
                nums = [t for t in data if NUM.match(t.replace(',', ''))]
                if len(nums) == 12:
                    rows.append((code, site, "male",   int(num(nums[0])), num(nums[2]), num(nums[3])))
                    rows.append((code, site, "female", int(num(nums[6])), num(nums[8]), num(nums[9])))
        except (ValueError, IndexError):
            continue
    return rows


def parse_byage(page, sex):
    """-> list of (code, site, sex, count, crude, asr); count=first, asr=last."""
    ws = page.get_text("words")
    rows = []
    for c in [w for w in ws if re.match(r'^C\d', w[4].replace(' ', ''))]:
        code = c[4].replace(' ', '')
        cells = merge_row(ws, (c[1] + c[3]) / 2)
        site, data = site_and_nums(cells)
        nums = [t for t in data if NUM.match(t.replace(',', ''))]
        if len(nums) >= 3:
            try:
                rows.append((code, site, sex, int(num(nums[0])), num(nums[-2]), num(nums[-1])))
            except ValueError:
                continue
    return rows


def classify(text):
    low = text.lower()
    ncode = len(re.findall(r'\bC\d{2}', text))
    if ncode < 12 or text.count(".....") > 3:
        return None
    pop = population(text)
    if pop is None:
        return None
    is_byage = bool(AGE.search(text)) and ("air" in low or "age-spe" in low or "age spe" in low
                                           or "incidence rate" in low or "standardi" in low)
    is_summary = (("crude" in low or "cir" in low) and "asr" in low and not is_byage
                  and ("primary" in low or "all sites" in low or "not c44" in low))
    if is_byage:
        sex = "female" if "female" in low else ("male" if "male" in low else None)
        return ("byage", pop, sex)
    if is_summary:
        return ("summary", pop, None)
    return None


def extract(path):
    doc = fitz.open(path)
    found = {}                                   # (pop, sex) -> (kind, rows)
    for pg in range(doc.page_count):
        page = doc[pg]; text = page.get_text()
        cl = classify(text)
        if not cl:
            continue
        kind, pop, sex = cl
        if kind == "summary":
            rows = parse_summary(page)
            for s in ("male", "female"):
                key = (pop, s)
                sub = [r for r in rows if r[2] == s]
                if len(sub) >= 5 and (key not in found or found[key][0] != "summary"):
                    found[key] = ("summary", sub)
        else:
            if sex is None:
                continue
            key = (pop, sex)
            if key in found and found[key][0] == "summary":
                continue                          # prefer summary for Saudi
            rows = parse_byage(page, sex)
            if len(rows) >= 5 and key not in found:
                found[key] = ("byage", rows)
    return found


def main(d):
    out_rows = []
    cover = {}
    for f in sorted(glob.glob(os.path.join(d, "*.pdf"))):
        year = int(re.search(r'(20\d{2}|19\d{2})', os.path.basename(f)).group(1))
        doc = fitz.open(f)
        chars = sum(len(doc[p].get_text()) for p in range(doc.page_count))
        if chars < 2000:
            print(f"{year}: image-only, skipped"); continue
        if year in OCR_UNRELIABLE:
            print(f"{year}: OCR-only tables excluded (unreliable cell-by-cell); lung via narrative"); continue
        found = extract(f)
        cover[year] = {f"{p}/{s}": (kind, len(rows)) for (p, s), (kind, rows) in found.items()}
        for (pop, sex), (kind, rows) in found.items():
            for code, site, sx, count, crude, asr in rows:
                out_rows.append(dict(year=year, population=pop, sex=sx, icd_code=code,
                                     site=site, count=count, crude=crude, asr=asr, source=kind))
    if out_rows:
        os.makedirs("data", exist_ok=True)
        path = "data/scr_all_sites_long.csv"
        with open(path, "w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=["year", "population", "sex", "icd_code",
                                               "site", "count", "crude", "asr", "source"])
            w.writeheader(); w.writerows(out_rows)
        print(f"\n[written] {path}  ({len(out_rows)} rows)")
    print("\nCoverage (population/sex -> source, n_sites):")
    for y in sorted(cover):
        print(f"  {y}: {cover[y]}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else ".")
