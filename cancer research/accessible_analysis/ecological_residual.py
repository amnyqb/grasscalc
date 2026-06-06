#!/usr/bin/env python3
"""Accessible-data ecological analysis (no SCR microdata required).

Extends the smoking-sensitivity bound (Table 3) by one defensible step: how much
of the observed Eastern-Province : Jazan crude lung-cancer contrast remains AFTER
crediting the largest plausible regional smoking difference. Uses ONLY values
already in the package (all published aggregate data). Claim ceiling: Compatible.

Inputs (provenance):
  EP crude lung rate 3.36 / Jazan 0.59 per 100,000  -> scrlung2025 (open access)
  smoking-only rate ratios per scenario             -> smoking_sensitivity.py (GATS 2019 inputs)
Model: population lung rate proportional to p*RR + (1-p)  [same as Table 3].
"""
import csv

EP, JAZAN = 3.36, 0.59
observed = EP / JAZAN

# smoking-only rate ratios reproduced from smoking_sensitivity_output.csv
def srr(p_high, p_low, RR):
    return (p_high*RR + (1-p_high)) / (p_low*RR + (1-p_low))

scenarios = [
    ("Realistic regional gap", 0.20, 0.10),
    ("Large gap",              0.30, 0.08),
    ("Implausible extreme",    0.45, 0.05),
]
RR = 20  # most smoking-favourable (largest current-vs-never RR in the literature range)

rows = []
print(f"Observed EP:Jazan crude lung-cancer rate ratio = {observed:.2f} "
      f"(3.36 vs 0.59 /100,000; CRUDE, not ASR)\n")
print(f"{'Smoking scenario':24} {'smoking-only RR(20)':>20} {'residual ratio':>15}")
for name, ph, pl in scenarios:
    s = srr(ph, pl, RR)
    residual = observed / s
    rows.append([name, ph, pl, RR, round(s,2), round(residual,2)])
    print(f"{name:24} {s:>20.2f} {residual:>15.2f}")

with open("ecological_residual_output.csv","w",newline="") as f:
    w = csv.writer(f)
    w.writerow(["smoking_scenario","p_high","p_low","RR","smoking_only_ratio","residual_ratio_after_smoking"])
    w.writerows(rows)

print("\nReadout (Compatible level only):")
print("- Even crediting a LARGE regional smoking gap (30% vs 8%) at the highest")
print(f"  plausible RR=20, smoking explains at most ~{srr(0.30,0.08,20):.1f}x of the contrast,")
print(f"  leaving a residual ratio of ~{observed/srr(0.30,0.08,20):.1f}x unexplained by smoking.")
print("- This residual is NOT evidence of 1991-plume causation. It remains confounded")
print("  by age structure (the rates are CRUDE), screening/diagnostic intensity,")
print("  healthcare access, urbanization, petrochemical-occupation, migration, and")
print("  registry completeness. Distinguishing these needs SCR microdata (not accessible).")
print("- Defensible statement: the contrast is unlikely to be a smoking-only artefact;")
print("  it is COMPATIBLE with a sustained environmental-exposure hypothesis and")
print("  requires the pre-specified microdata analysis to test.")
