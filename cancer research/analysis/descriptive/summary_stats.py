#!/usr/bin/env python3
"""Descriptive summary statistics of the assembled evidence base.

WHAT THIS IS: a structural characterization of the charted corpus (counts and
distributions of references, comparator populations, evidence grades, effect-
metric families, study designs, confounder control, latency, geography).

WHAT THIS IS NOT: it does NOT compute central tendency of effect magnitudes.
Per the metric-separation rule, effect values from different metric families
(ERR/Gy, RR, IRR, crude-rate ratio, modeled risk, ...) are incommensurable and
are never averaged/pooled. Reported values are listed with provenance only.
"""
import csv, re, os
from collections import Counter, defaultdict

DATA = "data"; OUT = "analysis/descriptive"; os.makedirs(OUT, exist_ok=True)
def rows(p): return list(csv.DictReader(open(p, encoding="utf-8")))
def col(rs, c): return [r[c] for r in rs]
def freq(vals): return Counter(v.strip() for v in vals if str(v).strip())
def write_freq(name, counter, label):
    with open(f"{OUT}/{name}", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow([label, "n"])
        for k, n in counter.most_common(): w.writerow([k, n])

refs   = rows(f"{DATA}/references.csv")
matrix = rows(f"{DATA}/evidence_matrix.csv")
extr   = rows(f"{DATA}/extraction_table.csv")
kv     = rows(f"{DATA}/key_values.csv")
sens   = rows(f"{DATA}/smoking_sensitivity_output.csv")

L = []
def p(*a): L.append(" ".join(str(x) for x in a))

p("="*70); p("DESCRIPTIVE SUMMARY STATISTICS — assembled evidence base"); p("="*70)

# ---- A. Reference corpus -----------------------------------------------------
p("\n[A] REFERENCE CORPUS")
p(f"  Total references (N)          : {len(refs)}")
status = freq(col(refs, "status"))
for k, n in status.most_common():
    p(f"    status {k:13}: {n:2}  ({n/len(refs)*100:4.1f}%)")
p(f"  DOI present                   : {sum(1 for r in refs if r['doi'])} / {len(refs)}")
p(f"  PMID/PMCID present            : {sum(1 for r in refs if r['pmid_or_pmcid'])} / {len(refs)}")
write_freq("freq_reference_status.csv", status, "id_status")

# cited-in-text vs not (from the main .tex)
try:
    tex = open("manuscript/War_Exposure_Cancer_ScopingReview.tex", encoding="utf-8").read()
    cited = set()
    for m in re.finditer(r'\\cite[tp]?\{([^}]*)\}', tex):
        cited |= {k.strip() for k in m.group(1).split(',')}
    allkeys = set(col(refs, "cite_key"))
    p(f"  Cited in main text            : {len(cited & allkeys)} / {len(refs)}")
    p(f"  In bibliography but uncited   : {len(allkeys - cited)}  -> {sorted(allkeys-cited)}")
except FileNotFoundError:
    p("  (manuscript .tex not found for citation count)")

# ---- B. Comparator populations (evidence matrix) -----------------------------
p("\n[B] COMPARATOR POPULATIONS (evidence matrix)")
p(f"  Total comparator populations  : {len(matrix)}  (incl. the Saudi test case)")
expo = freq(col(matrix, "exposure_category"))
p(f"  Distinct exposure categories  : {len(expo)}")
for k, n in expo.most_common(): p(f"    {n:2}  {k}")
write_freq("freq_exposure_category.csv", expo, "exposure_category")

grade = freq(col(matrix, "evidence_grade"))
p(f"\n  Evidence grade (as charted)   : {len(grade)} distinct labels")
for k, n in grade.most_common(): p(f"    {n:2}  {k}")
write_freq("freq_evidence_grade.csv", grade, "evidence_grade")

# primary grade = leading letter (A/B -> A); contextual D/E and 'Ecological' kept
def primary(g):
    g = g.strip()
    if g.startswith("Ecological"): return "Ecological"
    m = re.match(r'[A-F]', g); return m.group(0) if m else g
pg = freq([primary(g) for g in col(matrix, "evidence_grade")])
p("  Collapsed to primary grade    :")
for k, n in sorted(pg.items()): p(f"    {k:11}: {n}")
write_freq("freq_primary_grade.csv", pg, "primary_grade")

role = freq(col(matrix, "synthesis_role"))
write_freq("freq_synthesis_role.csv", role, "synthesis_role")

# metric family from native-units text
def metric_family(s):
    s = s.lower()
    if "err/gy" in s: return "ERR per dose (Gy)"
    if "err/sv" in s: return "ERR per dose (Sv)"
    if "rr/hr" in s or s.startswith("dose-response"): return "Dose-response RR/HR"
    if "mortality ratio" in s: return "Mortality ratio"
    if "irr" in s: return "Incidence rate ratio"
    if "rr " in s or s.startswith("rr"): return "Relative risk"
    if "asir" in s: return "ASIR change"
    if "crude-rate" in s or "crude rate" in s: return "Crude-rate ratio"
    if "modeled" in s or "modelled" in s: return "Modeled lifetime risk"
    if "policy" in s: return "Policy-presumptive list"
    if "survey" in s: return "Community-survey ratio"
    if "immature" in s: return "No incidence yet (immature latency)"
    return "Other/unspecified"
mf = freq([metric_family(s) for s in col(matrix, "reported_metric_native_units")])
p(f"\n  Effect-metric FAMILIES        : {len(mf)} incommensurable families (NOT pooled)")
for k, n in mf.most_common(): p(f"    {n:2}  {k}")
write_freq("freq_metric_family.csv", mf, "metric_family")

# cross-tab primary grade x exposure (sparse listing)
p("\n  Cross-tab (primary grade x exposure category):")
ct = defaultdict(list)
for r in matrix:
    ct[primary(r["evidence_grade"])].append(r["exposure_category"])
for g in sorted(ct): p(f"    {g:11}: {', '.join(ct[g])}")

# ---- C. Source-level extraction ---------------------------------------------
p("\n[C] SOURCE-LEVEL EXTRACTION (charting sheet)")
p(f"  Charted source rows           : {len(extr)}")
des = freq(col(extr, "design"))
p("  Study design:")
for k, n in des.most_common(): p(f"    {n:2}  {k}")
write_freq("freq_design.csv", des, "design")

sm = freq(col(extr, "smoking_confounder_control"))
p("  Smoking / confounder control:")
for k, n in sm.most_common(): p(f"    {n:2}  {k}")
write_freq("freq_smoking_control.csv", sm, "smoking_confounder_control")

lat = freq(col(extr, "latency"))
p("  Latency (as charted):")
for k, n in lat.most_common(): p(f"    {n:2}  {k}")

# ---- D. Headline claims ------------------------------------------------------
p("\n[D] HEADLINE NUMERIC CLAIMS (key-values register)")
p(f"  Total charted claims          : {len(kv)}")
mt = freq(col(kv, "metric_type"))
p(f"  Metric types represented      : {len(mt)}")
for k, n in mt.most_common(): p(f"    {n:2}  {k}")
write_freq("freq_claim_metric_type.csv", mt, "metric_type")
nsrc = len({s.strip() for r in kv for s in re.split(r'[;,]', r['source_cite_key'])})
p(f"  Distinct sources behind claims: {nsrc}")
p("  NOTE: no mean/median of effect values is reported — the metric types above")
p("        are incommensurable (metric-separation rule). Values are listed with")
p("        provenance in ../claims_long.csv only.")

# ---- E. Smoking-sensitivity (the one computed dataset) -----------------------
p("\n[E] SMOKING-PREVALENCE SENSITIVITY (Table 3) — observed contrast 5.69x")
for r in sens:
    p(f"    {r['scenario']:24} p {r['p_high']}/{r['p_low']}  "
      f"RR10={r['rate_ratio_RR10']}  RR15={r['rate_ratio_RR15']}  RR20={r['rate_ratio_RR20']}")

open(f"{OUT}/summary_stats.txt", "w", encoding="utf-8").write("\n".join(L))
print("\n".join(L))
print(f"\n[written] {OUT}/summary_stats.txt + freq_*.csv")
