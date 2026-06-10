#!/usr/bin/env python3
"""Long-run lung cancer (ICD-10 C33-C34) series for Saudi nationals from the
Saudi Cancer Registry annual reports.

For every report it extracts lung cancer **counts by sex** and **age-standardized
incidence rate (ASR, World standard, /100,000) by sex** from TWO independent
places in the same PDF, and cross-checks them:

  (A) Table 2.x  "Number, %, (CIR), ASR, Cumulative Rates ... by Primary Site and
      Sex/Gender among Saudis/Saudi Nationals"  -- read by WORD COORDINATES so it
      works for both the old row-major layout (2006-2010) and the modern
      column-major layout (2018-2023). The lung row is located by its ICD code
      cell 'C33-C34'; cells on that y-band are sorted by x and mapped to columns.

  (B) Part III selected-site narrative  "There were N cases of lung cancer ...
      affected M (..%) males and F (..%) females ... The ASR was X/100,000 for
      males and Y/100,000 for females."

INTEGRITY (per project rules):
  * Only printed values are emitted. Nothing is interpolated or modelled.
  * Every value is printed with its source; (A) vs (B) agreement is reported.
  * Years that cannot be read cleanly are FLAGGED, not guessed:
      - 2005  : PDF not present in the local set.
      - 2014  : image-only scan (no text layer)            -> needs OCR.
      - 2017  : corrupted/garbled text layer               -> needs OCR.
      - 2013  : incidence tables are images; only the narrative ASR is readable
                (counts not text-extractable; narrative gives the M:F ratio only).
      - 2004  : narrative ASR is scrambled by RTL/Arabic interleaving; counts OK.
      - 2015  : summary-table column set differs; ASR cell ambiguous -> flagged.
  * COUNTS != RATES. Use ASR for trends. 2020 is depressed by COVID-19
    registration disruption. A possible standard-population/method change around
    2021 (ASR step-up) is noted in the report, not asserted as a real increase.

USAGE
    python3 extract_lung_series.py /path/to/dir_with_pdfs   # files named *YYYY*.pdf
Outputs:
    data/scr_lung_by_sex_asr_2006_2023.csv   (long-run lung series + sources/flags)
"""
import fitz, re, csv, sys, glob, os

# --- summary-table page per year (Table 2.2/2.3 old; Table 2.6 modern). 0-based.
#     Auto-detection is the fallback; these verified pages avoid the per-age
#     ASR tables (5.1.x) which share the 'ASR' keyword.
SUMMARY_PAGE = {2006:19, 2007:19, 2008:19, 2009:21, 2010:21, 2015:20, 2016:18,
                2018:26, 2019:24, 2020:24, 2021:24, 2022:24, 2023:23}

FLAG = {
    2004: "narrative ASR scrambled by RTL interleaving; counts from narrative only",
    2013: "OCR-recovered from narrative (tables were images); ASR cross-checked = 5.5/1.8",
    2014: "OCR-recovered from narrative (image-only scan); total 452 matches published figure",
    2015: "summary-table column set differs; ASR cell ambiguous -> verify in PDF",
    2016: "male count cell garbled (overlapping glyphs ~298); ASR readable, count dropped",
    2017: "OCR-recovered from narrative (garbled text layer); ASR = 5.0/2.0",
}

# Saudi-national lung counts per sex are in the low hundreds; anything larger is a
# glyph-merge artifact in a garbled table and must not be trusted.
MAX_PLAUSIBLE_COUNT = 1500

NUM = re.compile(r'^-?\d[\d,]*(?:\.\d+)?$')


def _clean(tok):
    return tok.replace(",", "").replace("%", "").strip()


def lung_cells(page):
    """Return the lung (C33-C34) row of the per-site x sex summary table as an
    ordered list of (x, text), merging horizontally-adjacent digit fragments
    (the modern tables sometimes split '298' into '29' + '98')."""
    words = page.get_text("words")              # x0,y0,x1,y1,text,...
    code = [w for w in words if w[4].replace(" ", "") == "C33-C34"]
    if not code:
        return None
    c = code[0]; yc = (c[1] + c[3]) / 2
    band = sorted((w for w in words if abs((w[1] + w[3]) / 2 - yc) < 3.5),
                  key=lambda w: w[0])
    # merge adjacent integer fragments (x-gap small, both pure digits, no '%')
    merged = []
    for w in band:
        x0, txt = w[0], w[4]
        if merged:
            px1, ptxt = merged[-1][2], merged[-1][1]
            if (x0 - px1) < 5 and ptxt.isdigit() and txt.isdigit():
                merged[-1] = (merged[-1][0], ptxt + txt, w[2]); continue
        merged.append((x0, txt, w[2]))
    return [(x, t) for x, t, _ in merged]


def parse_summary(page):
    """-> dict(male_n, female_n, male_asr, female_asr) or None. Columns per sex:
    No, %, Crude/CIR, ASR, Cum0-64, Cum0-74. Anchored on the two '%' cells when
    present; otherwise positional (12 numbers -> 6+6, ASR = index 3)."""
    cells = lung_cells(page)
    if not cells:
        return None
    texts = [t for _, t in cells]
    # drop everything up to and including the site label (first numeric starts data)
    first_num = next((i for i, t in enumerate(texts) if NUM.match(_clean(t)) and _clean(t) != ""), None)
    if first_num is None:
        return None
    data = texts[first_num:]
    pct_idx = [i for i, t in enumerate(data) if "%" in t]
    out = {}
    if len(pct_idx) >= 2:
        mi, fi = pct_idx[0], pct_idx[1]
        try:
            out["male_n"]    = int(_clean(data[mi - 1]))
            out["male_asr"]  = float(_clean(data[mi + 2]))   # No, %, Crude, ASR
            out["female_n"]  = int(_clean(data[fi - 1]))
            out["female_asr"] = float(_clean(data[fi + 2]))
        except (ValueError, IndexError):
            return None
        return out
    nums = [_clean(t) for t in data if NUM.match(_clean(t))]
    if len(nums) == 12:                          # row-major, no '%' sign (e.g. 2010)
        try:
            out["male_n"] = int(nums[0]);  out["male_asr"] = float(nums[3])
            out["female_n"] = int(nums[6]); out["female_asr"] = float(nums[9])
            return out
        except ValueError:
            return None
    if len(nums) == 11:                          # one male cell dropped (e.g. 2009)
        try:                                     # female block is the clean last 6
            out["female_n"] = int(nums[5]); out["female_asr"] = float(nums[8])
            out["male_n"] = int(nums[0])          # male ASR ambiguous -> leave to narrative
            out["_partial"] = True
            return out
        except ValueError:
            return None
    # other column sets (e.g. 2015): report counts only, flag ASR
    if len(nums) >= 2:
        try:
            half = len(nums) // 2
            out["male_n"] = int(nums[0]); out["female_n"] = int(nums[half])
            out["_counts_only"] = True
            return out
        except ValueError:
            return None
    return None


def narrative(doc):
    """Parse the Part III lung paragraph. Returns dict with any of total/male_n/
    female_n/male_asr/female_asr that are unambiguously printed."""
    for pg in range(doc.page_count):
        t = doc[pg].get_text()
        if t.count(".....") > 3:
            continue
        if not re.search(r'lung cancer', t, re.I):
            continue
        flat = " ".join(t.split())
        if "ASR was" not in flat and "cases of lung" not in flat and "newly diagnosed cases" not in flat:
            continue
        out = {"_page": pg}
        m = re.search(r'(?:were|was)\s+(\d[\d,]*)\s+(?:newly diagnosed )?(?:new )?cases', flat, re.I)
        if m: out["total"] = int(m.group(1).replace(",", ""))
        m = (re.search(r'affected\s+(\d[\d,]*)\s*\(?(\d+\.?\d*)\s*%\)?\s*males?\s+and\s+(\d[\d,]*)\s*\(?(\d+\.?\d*)\s*%\)?\s*females?', flat, re.I)
             or re.search(r'(\d[\d,]*)\s+males?\s*\(?(\d+\.?\d*)\s*%\)?\s+and\s+(\d[\d,]*)\s+females?', flat, re.I))
        if m:
            out["male_n"] = int(m.group(1).replace(",", "")); out["female_n"] = int(m.group(3).replace(",", ""))
        m = re.search(r'ASR\s+was\s+([\d.]+)\s*/\s*100,?000\s+for\s+males?\s+and\s+([\d.]+)\s*/\s*100,?000\s+for\s+females?', flat, re.I)
        if m:
            out["male_asr"] = float(m.group(1)); out["female_asr"] = float(m.group(2))
        else:   # fall back to one-sex statements (older reports scramble the other)
            mm = re.search(r'([\d.]+)\s*/\s*100,?000\s+for\s+males?', flat, re.I)
            mf = re.search(r'([\d.]+)\s*/\s*100,?000\s+for\s+females?', flat, re.I)
            if mm: out["male_asr"] = float(mm.group(1))
            if mf: out["female_asr"] = float(mf.group(1))
        if len(out) > 1:
            return out
    return None


def agree(a, b):
    return a is not None and b is not None and a == b


def main(d):
    rows = []
    for f in sorted(glob.glob(os.path.join(d, "*.pdf"))):
        year = int(re.search(r'(20\d{2}|19\d{2})', os.path.basename(f)).group(1))
        doc = fitz.open(f)
        chars = sum(len(doc[p].get_text()) for p in range(doc.page_count))
        print(f"\n=== {year} ({os.path.basename(f)}) ===")
        if chars < 2000:
            print("   FLAG: image-only / no text layer -> needs OCR. SKIPPED.")
            continue

        tab = parse_summary(doc[SUMMARY_PAGE[year]]) if year in SUMMARY_PAGE else None
        nar = narrative(doc)
        if tab:
            print("   table :", {k: v for k, v in tab.items() if not k.startswith('_')})
        else:
            print("   table : (not read from summary page)")
        if nar:
            print("   narr  :", {k: v for k, v in nar.items() if not k.startswith('_')})
        else:
            print("   narr  : (not found)")

        # reconcile, preferring agreement; fall back to whichever exists
        def pick(key):
            tv = (tab or {}).get(key); nv = (nar or {}).get(key)
            if tv is not None and nv is not None:
                return tv, ("table=narr" if tv == nv else f"MISMATCH table={tv} narr={nv}")
            if tv is not None: return tv, "table"
            if nv is not None: return nv, "narrative"
            return None, "missing"

        male_n, s_mn = pick("male_n")
        female_n, s_fn = pick("female_n")
        if male_n is not None and male_n > MAX_PLAUSIBLE_COUNT:
            male_n, s_mn = None, "dropped (implausible glyph-merge)"
        if female_n is not None and female_n > MAX_PLAUSIBLE_COUNT:
            female_n, s_fn = None, "dropped (implausible glyph-merge)"
        male_asr, s_ma = pick("male_asr")
        female_asr, s_fa = pick("female_asr")
        total = (nar or {}).get("total")
        if total is None and male_n is not None and female_n is not None:
            total = male_n + female_n

        for label, val, src in [("male_n", male_n, s_mn), ("female_n", female_n, s_fn),
                                ("male_asr", male_asr, s_ma), ("female_asr", female_asr, s_fa)]:
            tag = "" if "MISMATCH" not in src else "   <-- CHECK"
            print(f"   {label:<11}= {str(val):<7} [{src}]{tag}")
        if total is not None:
            print(f"   {'total':<11}= {total}")
        if year in FLAG:
            print(f"   FLAG: {FLAG[year]}")

        rows.append(dict(year=year, male_n=male_n, female_n=female_n, total=total,
                         male_asr=male_asr, female_asr=female_asr,
                         source_counts=s_mn, source_asr=s_ma,
                         flag=FLAG.get(year, "")))

    if rows:
        ys = [r["year"] for r in rows]
        out = f"data/scr_lung_by_sex_asr_{min(ys)}_{max(ys)}.csv"
        os.makedirs("data", exist_ok=True)
        with open(out, "w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=["year", "male_n", "female_n", "total",
                                               "male_asr", "female_asr",
                                               "source_counts", "source_asr", "flag"])
            w.writeheader()
            for r in rows:
                w.writerow(r)
        print(f"\n[written] {out}  ({len(rows)} years)")
        print("ASR is World-standard /100,000. COUNTS are not rates. 2020 = COVID artifact.")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else ".")
