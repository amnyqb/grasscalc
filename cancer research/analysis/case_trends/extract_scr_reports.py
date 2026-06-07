#!/usr/bin/env python3
"""Extract "Most common cancers among Saudi nationals" (site -> case count) from
Saudi Cancer Registry annual-report PDFs, and emit the long-format CSV that
plot_trends.py / plot_cases_by_year.py consume.

Handles BOTH report layouts seen so far:
  * 2019-2022: a "Sites | No. | %" table (PyMuPDF find_tables; column cells are
    newline-joined -> split + zip).
  * 2023+    : a "Rank | Site | No. | %" ranking with Both sexes / Males /
    Females stacked vertically -> extract by y-band using word coordinates.

USAGE
    pip install pymupdf
    python3 extract_scr_reports.py /path/to/dir_with_pdfs   # files named *YYYY*.pdf
Outputs: data/scr_saudi_topsites_<minY>_<maxY>.csv  (country,year,cancer_type,cases,value)

INTEGRITY: extracts only the printed counts; prints every value for review.
Population = Saudi nationals, both sexes, all ages (the table's own definition).
These are COUNTS, not rates (affected by population growth + registry coverage).
"""
import fitz, re, csv, sys, glob, os

def parse_sites_table(page):
    for t in page.find_tables().tables:
        rows=t.extract()
        if rows and (rows[0][0] or "").strip()=="Sites" and len(rows)>1:
            cell=rows[1]
            sites=[s.strip() for s in (cell[0] or "").split("\n") if s.strip()]
            nums=[n.strip() for n in (cell[1] or "").split("\n") if n.strip()]
            out={}
            for s,n in zip(sites,nums):
                n2=n.replace(",","")
                if n2.isdigit(): out[s]=int(n2)
            if len(out)>=5: return out
    return None

def parse_ranking(page):  # 2023 style
    words=page.get_text("words")
    def hy(name):
        ys=[w[1] for w in words if w[4]==name]; return min(ys) if ys else None
    yb,ym=hy("sexes"),hy("Males")
    if yb is None or ym is None: return None
    lines={}
    for w in words:
        if yb<w[1]<ym: lines.setdefault(round(w[1]/2)*2,[]).append((w[0],w[4]))
    out={}
    for y in sorted(lines):
        line=" ".join(t for _,t in sorted(lines[y]))
        m=re.search(r'([A-Za-z][A-Za-z,\'’\s/]+?)\s+(\d[\d,]{1,6})\s+\d+\.\d+', line)
        if m:
            n=m.group(2).replace(",","")
            if n.isdigit(): out[m.group(1).strip()]=int(n)
    return out or None

def parse_table22(page):
    """2006-2010 layout: 'Table 2.2 Ten Most Common Cancers among Saudis, YYYY
    (All Ages)' -- a BOTH-SEXES ranking 'Cancer | No. | %'. The both-sexes block
    sits above the caption; the per-sex figure below it uses '%' signs on its
    rate cells, so a row whose last cell is a plain decimal (no '%') is a
    both-sexes row. Read by word coordinates (row = y-band)."""
    txt=page.get_text()
    if "Most Common Cancers among Saudis" not in txt or "All Ages" not in txt:
        return None
    words=page.get_text("words")
    def yrow(pred):
        ys=[(w[1]+w[3])/2 for w in words if pred(w[4])]; return min(ys) if ys else None
    y_hdr=yrow(lambda t:t=="Cancer")
    y_cap=yrow(lambda t:t=="Ages)") or yrow(lambda t:t=="(All")
    if y_hdr is None or y_cap is None: return None
    from collections import defaultdict
    rows=defaultdict(list)
    for w in words:
        yc=(w[1]+w[3])/2
        if y_hdr+2 < yc < y_cap-2: rows[round(yc/2)*2].append(w)
    out={}
    for y in sorted(rows):
        cells=[w[4] for w in sorted(rows[y],key=lambda w:w[0])]
        if any("%" in c for c in cells): continue          # per-sex block, skip
        nums=[c for c in cells if c.replace(",","").isdigit()]
        site=" ".join(c for c in cells if not re.match(r'^[\d.,%]+$',c)).strip()
        if site and nums and len(out)<10:
            out[site]=int(nums[0].replace(",",""))
    return out if len(out)>=5 else None

def extract(path):
    d=fitz.open(path)
    for pg in range(d.page_count):
        page=d[pg]; txt=page.get_text()
        if "Most common cancers among Saudi nationals" in txt:
            r=parse_sites_table(page)
            if r: return r
    for pg in range(d.page_count):       # 2006-2010 both-sexes Table 2.2
        page=d[pg]
        if "Most Common Cancers among Saudis" in page.get_text() and "All Ages" in page.get_text():
            r=parse_table22(page)
            if r: return r
    for pg in range(d.page_count):       # 2023 fallback
        page=d[pg]
        if "Both sexes" in page.get_text():
            r=parse_ranking(page)
            if r: return r
    return None

NORM={"Leukemia":"Leukaemia","Brain,CNS":"Brain/CNS","Brain, CNS":"Brain/CNS",
      "Hodgkin' lymphoma":"Hodgkin lymphoma","Hodgkin’s lymphoma":"Hodgkin lymphoma",
      "Hodgkin's lymphoma":"Hodgkin lymphoma",
      "Colo-rectal":"Colorectal","Hodgkin disease":"Hodgkin lymphoma",
      "Hodgkin Disease":"Hodgkin lymphoma","Corpus uteri":"Corpus Uteri",
      "Breast female":"Breast","Breast Female":"Breast"}

def main(d):
    rows=[]
    for f in sorted(glob.glob(os.path.join(d,"*.pdf"))):
        m=re.search(r'(20\d2|19\d2|20\d{2})', os.path.basename(f)) or re.search(r'(20\d{2})', os.path.basename(f))
        year=int(re.search(r'(20\d{2}|19\d{2})', os.path.basename(f)).group(1))
        res=extract(f)
        if not res: print(f"{year}: NOT EXTRACTED (check format)"); continue
        print(f"\n{year} ({os.path.basename(f)}):")
        for s,n in res.items():
            site=NORM.get(s,s); print(f"   {site:<20} {n}")
            rows.append((year,site,n))
    if rows:
        ys=[r[0] for r in rows]
        out=f"data/scr_saudi_topsites_{min(ys)}_{max(ys)}.csv"; os.makedirs("data",exist_ok=True)
        with open(out,"w",newline="") as fh:
            w=csv.writer(fh); w.writerow(["country","year","cancer_type","cases","value"])
            for y,s,n in rows: w.writerow(["Saudi Arabia (SCR, Saudi nationals)",y,s,n,n])
        print(f"\n[written] {out}  ({len(rows)} rows)")

if __name__=="__main__":
    main(sys.argv[1] if len(sys.argv)>1 else ".")
