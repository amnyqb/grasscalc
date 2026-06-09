#!/usr/bin/env python3
"""Recover 2011 & 2012 all-sites ASR (and crude) for Saudi nationals from the
TRANSPOSED annual rate tables (Table 5.1.3/5.1.4), which the 2011-2012 reports
laid out with cancer sites as rotated COLUMN headers and age-groups/Crude/ASR as
rows -- the orientation that defeated the row-based reader in extract_all_sites.py.

Method: the ICD codes sit as rotated headers near the page bottom; their x-centres
define the site columns. The 'ASR' and 'Crude' row labels sit at the left edge;
reading across those rows and x-aligning each value to a site column yields the
per-site rate. The correct Saudi *annual* page (vs non-Saudi, vs the different-
standard multi-year table) is identified automatically by requiring the parsed
lung (C33-C34) ASR to equal the known narrative value for that year/sex.

INTEGRITY: every page is accepted only if its lung ASR matches the independently
known value; we print lung + all-sites checks. Counts are not in the rate table,
so 2011/2012 here carry ASR + crude only (count left blank). ASR = World std /100k;
both years are on the pre-2021 (pre-census-break) basis, consistent with 2006-2019.

USAGE: python3 extract_transposed.py    # writes data/scr_all_sites_2011_2012.csv
"""
import fitz, re, csv, os

P = "/Users/amin/Documents/Research/cancer_research/Cancer_Reports"
# known Saudi lung (C33-C34) ASR from the narratives (validation anchors)
LUNG_ASR = {(2011, "male"): 6.4, (2011, "female"): 1.9,
            (2012, "male"): 5.9, (2012, "female"): 2.2}
NUM = re.compile(r'^-?\d[\d,]*(?:\.\d+)?$')


def code_columns(ws):
    return {w[4].replace(" ", ""): (w[0] + w[2]) / 2
            for w in ws if re.match(r'^C\d', w[4].replace(" ", "")) and w[1] > 700}


def label_y(ws, text):
    # return the label's TOP (y0); rotated labels are tall and the value row sits
    # near their top, so y0 + a wide tolerance is the reliable anchor.
    cand = [w for w in ws if w[4] == text and w[0] < 95]
    return cand[0][1] if cand else None


def read_across(ws, cols, yc, tol=8):
    vals = [w for w in ws if abs((w[1] + w[3]) / 2 - yc) < tol
            and NUM.match(w[4].replace(",", ""))]
    out = {}
    for code, cx in cols.items():
        near = sorted([v for v in vals if abs((v[0] + v[2]) / 2 - cx) < 4],
                      key=lambda v: abs((v[0] + v[2]) / 2 - cx))
        if near:
            out[code] = float(near[0][4].replace(",", ""))
    return out


def parse_page(d, pg):
    ws = d[pg].get_text("words")
    cols = code_columns(ws)
    if "C33-C34" not in cols:
        return None
    ay, cy = label_y(ws, "ASR"), label_y(ws, "Crude")
    if ay is None:
        return None
    asr = read_across(ws, cols, ay)
    crude = read_across(ws, cols, cy) if cy is not None else {}
    return asr, crude


SITE = {  # minimal label map for output readability
    "C33-C34": "Trachea,Bronchus,Lung", "C50": "Breast", "C18": "Colon",
    "C19-C20": "Rectum", "C61": "Prostate", "C73": "Thyroid", "C22": "Liver",
    "C16": "Stomach", "C67": "Bladder", "C32": "Larynx", "C45": "Mesothelioma",
}


def main():
    rows = []
    for year in (2011, 2012):
        d = fitz.open(f"{P}/{year}.pdf")
        for sex in ("male", "female"):
            want = LUNG_ASR[(year, sex)]
            picked = None
            for pg in range(d.page_count):
                ws = d[pg].get_text("words")
                if len([w for w in ws if re.match(r'^C\d', w[4].replace(" ", "")) and w[1] > 700]) < 15:
                    continue
                r = parse_page(d, pg)
                if r and r[0].get("C33-C34") is not None and abs(r[0]["C33-C34"] - want) < 0.15:
                    picked = (pg, r); break
            if not picked:
                print(f"{year} {sex}: NO page matched lung ASR={want} -> SKIPPED"); continue
            pg, (asr, crude) = picked
            tot = max((v for k, v in asr.items()), default=0)
            print(f"{year} {sex}: page p{pg}  lung ASR={asr['C33-C34']} (want {want})  "
                  f"n_sites={len(asr)}  e.g. colon={asr.get('C18')} breast={asr.get('C50')} prostate={asr.get('C61')}")
            for code, a in asr.items():
                rows.append(dict(year=year, population="Saudi", sex=sex, icd_code=code,
                                 site=SITE.get(code, code), count="",
                                 crude=crude.get(code, ""), asr=a, source="byage-transposed"))
    fields = ["year", "population", "sex", "icd_code", "site", "count", "crude", "asr", "source"]
    out = "data/scr_all_sites_2011_2012.csv"
    os.makedirs("data", exist_ok=True)
    with open(out, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields); w.writeheader(); w.writerows(rows)
    print(f"\n[written] {out}  ({len(rows)} rows)")

    # idempotently merge into the canonical all-sites long file
    canon = "data/scr_all_sites_long.csv"
    if os.path.exists(canon):
        existing = [r for r in csv.DictReader(open(canon)) if int(r["year"]) not in (2011, 2012)]
        with open(canon, "w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=fields); w.writeheader()
            w.writerows(existing); w.writerows(rows)
        yrs = sorted({int(r["year"]) for r in existing} | {2011, 2012})
        print(f"[merged] into {canon}; years now: {yrs}")


if __name__ == "__main__":
    main()
