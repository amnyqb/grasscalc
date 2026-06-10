#!/usr/bin/env python3
"""Charts built ONLY from the data we actually have (no fabrication, no time
series). Two figures:
  1) Evidence-base composition (from evidence_matrix.csv + extraction_table.csv)
  2) Smoking-prevalence sensitivity (from smoking_sensitivity_output.csv) vs the
     observed 5.69x crude lung contrast.
These visualize the descriptive summary statistics and the one computed dataset.
"""
import csv, os, re
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

DATA = "data"; OUT = "analysis/descriptive/charts"; os.makedirs(OUT, exist_ok=True)
def rows(p): return list(csv.DictReader(open(p, encoding="utf-8")))
from collections import Counter

matrix = rows(f"{DATA}/evidence_matrix.csv")
extr   = rows(f"{DATA}/extraction_table.csv")
sens   = rows(f"{DATA}/smoking_sensitivity_output.csv")

def primary_grade(g):
    g=g.strip()
    if g.startswith("Ecological"): return "Ecological"
    m=re.match(r'[A-F]', g); return m.group(0) if m else g
def metric_family(s):
    s=s.lower()
    for key,lab in [("err/gy","ERR/Gy"),("err/sv","ERR/Sv"),("rr/hr","RR/HR"),
        ("mortality ratio","Mortality ratio"),("irr","IRR"),("asir","ASIR change"),
        ("crude","Crude-rate ratio"),("model","Modeled risk"),("policy","Policy list"),
        ("survey","Survey ratio"),("immature","No incidence yet")]:
        if key in s: return lab
    if s.startswith("rr"): return "Relative risk"
    return "Other"

# ---------- Figure 1: evidence-base composition (2x2) ------------------------
def barpanel(ax, counter, title, color):
    items=counter.most_common()
    labels=[k for k,_ in items]; vals=[v for _,v in items]
    y=np.arange(len(labels))
    ax.barh(y, vals, color=color, edgecolor="white")
    ax.set_yticks(y); ax.set_yticklabels(labels, fontsize=8)
    ax.invert_yaxis(); ax.set_title(title, fontsize=10, fontweight="bold")
    ax.set_xlabel("number of comparator populations", fontsize=8)
    for i,v in enumerate(vals): ax.text(v+0.05, i, str(v), va="center", fontsize=8)
    ax.tick_params(labelsize=8); ax.grid(axis="x", alpha=0.25)

fig, axes = plt.subplots(2,2, figsize=(12,8))
barpanel(axes[0,0], Counter(primary_grade(r["evidence_grade"]) for r in matrix),
         "By evidence grade (primary)", "#4C72B0")
barpanel(axes[0,1], Counter(r["exposure_category"] for r in matrix),
         "By exposure category", "#55A868")
barpanel(axes[1,0], Counter(metric_family(r["reported_metric_native_units"]) for r in matrix),
         "By effect-metric family (NOT pooled)", "#C44E52")
barpanel(axes[1,1], Counter(r["smoking_confounder_control"] for r in extr),
         "By smoking / confounder control", "#8172B3")
fig.suptitle("Evidence-base composition (n=13 comparator populations)  —  real data, descriptive only",
             fontsize=13, fontweight="bold")
fig.tight_layout(rect=[0,0,1,0.96])
fig.savefig(f"{OUT}/fig_evidence_composition.png", dpi=300, bbox_inches="tight")
fig.savefig(f"{OUT}/fig_evidence_composition.pdf", bbox_inches="tight")
print("[written]", f"{OUT}/fig_evidence_composition.png")

# ---------- Figure 2: smoking-sensitivity vs observed ------------------------
scen=[r["scenario"] for r in sens]
rr10=[float(r["rate_ratio_RR10"]) for r in sens]
rr15=[float(r["rate_ratio_RR15"]) for r in sens]
rr20=[float(r["rate_ratio_RR20"]) for r in sens]
x=np.arange(len(scen)); w=0.25
fig,ax=plt.subplots(figsize=(10,5.5))
ax.bar(x-w, rr10, w, label="RR=10", color="#a6cee3")
ax.bar(x,   rr15, w, label="RR=15", color="#1f78b4")
ax.bar(x+w, rr20, w, label="RR=20", color="#08519c")
ax.axhline(5.69, color="red", ls="--", lw=2, label="Observed EP:Jazan = 5.69x (crude)")
ax.set_xticks(x); ax.set_xticklabels(scen, fontsize=9)
ax.set_ylabel("implied lung-cancer rate ratio (smoking-only)", fontsize=10)
ax.set_title("Can regional smoking differences ALONE reproduce the 5.69x contrast?  (No.)",
             fontsize=12, fontweight="bold")
for xi,vs in zip(x,[ (rr10[i],rr15[i],rr20[i]) for i in range(len(scen))]):
    for dx,v in zip((-w,0,w),vs): ax.text(xi+dx, v+0.05, f"{v:.1f}", ha="center", fontsize=7)
ax.legend(fontsize=9); ax.grid(axis="y", alpha=0.3)
ax.text(0.5,-0.16,"Source: smoking_sensitivity.py (GATS 2019 inputs). Even a large gap reaches only ~2.7x; "
        "only an implausible gap nears 5.7x. Claim ceiling: Compatible.",
        transform=ax.transAxes, ha="center", fontsize=8, style="italic", color="dimgray")
fig.tight_layout()
fig.savefig(f"{OUT}/fig_smoking_sensitivity.png", dpi=300, bbox_inches="tight")
fig.savefig(f"{OUT}/fig_smoking_sensitivity.pdf", bbox_inches="tight")
print("[written]", f"{OUT}/fig_smoking_sensitivity.png")
