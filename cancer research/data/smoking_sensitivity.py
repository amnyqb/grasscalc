#!/usr/bin/env python3
"""
Smoking-prevalence sensitivity analysis (Manuscript Table 3).

Question: can regional differences in current-smoking prevalence ALONE
reproduce the observed ~5.7-fold Eastern-Province : Jazan crude lung-cancer
rate contrast (3.36 vs 0.59 per 100,000; AlOmar et al. 2025, SCR 2015-2020)?

Model (transparent two-category bias analysis, NOT a fitted model):
    population lung-cancer rate  proportional to  p * RR + (1 - p)
where
    p  = current-smoking prevalence in the region
    RR = lung-cancer relative risk, current smoker vs never smoker
The implied between-region rate ratio is the ratio of these two quantities.

Provenance of inputs:
    p ranges          -> Saudi GATS 2019 (national ~27.5% men / 3.7% women;
                         Eastern Province not markedly above national)
    RR (10/15/20)     -> literature range for current-smoker vs never-smoker
                         lung-cancer relative risk
This script reproduces the manuscript table exactly.
"""
import csv

def rate_ratio(p_high, p_low, RR):
    return (p_high * RR + (1 - p_high)) / (p_low * RR + (1 - p_low))

scenarios = [
    ("Realistic regional gap", 0.20, 0.10),
    ("Large gap",              0.30, 0.08),
    ("Implausible extreme",    0.45, 0.05),
    ("Required to reach 5.7",  0.50, 0.04),
]
RRs = [10, 15, 20]
OBSERVED = 5.7

rows = []
print(f"{'Scenario':28} {'p_high':>6} {'p_low':>6} " + "  ".join(f"RR={r}" for r in RRs))
for name, ph, pl in scenarios:
    vals = [rate_ratio(ph, pl, r) for r in RRs]
    print(f"{name:28} {ph:6.2f} {pl:6.2f} " + "  ".join(f"{v:5.2f}" for v in vals))
    rows.append([name, ph, pl] + [round(v, 2) for v in vals])

with open("smoking_sensitivity_output.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["scenario", "p_high", "p_low"] + [f"rate_ratio_RR{r}" for r in RRs])
    w.writerows(rows)

print(f"\nObserved crude-rate contrast = {OBSERVED}x")
print("Interpretation: realistic regional smoking gaps yield ~1.5x; even a large "
      "gap reaches only ~2.5x; only an implausible 50% vs 4% gap with RR=20 "
      "approaches the observed value. A smoking-only explanation is therefore "
      "implausible as the sole driver. NOTE: this does not address the crude "
      "(non-age-standardized) nature of the source rates, which the formal "
      "study must handle via age standardization.")
