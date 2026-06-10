#!/usr/bin/env python3
"""Phase 1 review visualizations, from the features.py outputs.

  data/fig_apc_forest.*        APC (annual % change of ASR) per site, Saudi M/F,
                               ranked, with 95% CI; colour = rising/flat/declining.
  data/fig_sex_ratio.*         M:F ASR ratio by site (recent mean), log axis.
  data/fig_saudi_nonsaudi.*    Saudi/non-Saudi ASR ratio by site (recent mean).
  data/fig_smoking_bundle.*    tobacco-associated bundle vs other ASR over time.

All ecological; ASR = World std /100k; 2020 = COVID artifact. Descriptive only.
"""
import csv, os
from collections import defaultdict
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

# vague/non-biological groupings to keep out of the headline charts
NOISE = {"C95", "C76", "C77-C80", "C26", "C39", "C48", "C97", "C80", "OTHER", "C75", "C88"}


def lab(site):
    p = site.split(None, 1)
    return p[1] if len(p) == 2 and p[0].startswith("C") else site


def recent_mean(rows, key, val, years=(2018, 2019, 2020, 2021, 2022, 2023)):
    acc = defaultdict(list)
    for r in rows:
        if int(r["year"]) in years and r[val] not in ("", None):
            acc[r[key]].append(float(r[val]))
    return {k: float(np.mean(v)) for k, v in acc.items() if v}


def apc_forest():
    # Use the PRE-2020 trend (before the 2021 census/denominator break) so the
    # ranking reflects real biology, not the artefactual 2021 step.
    rows = [r for r in csv.DictReader(open("data/scr_apc_summary.csv"))
            if r["population"] == "Saudi" and r["icd_code"] not in NOISE
            and r["apc_pre2020"] not in ("", None) and r["pre2020_lo"] not in ("", None)]
    fig, axes = plt.subplots(1, 2, figsize=(13, 7), sharex=True)
    for ax, sex in zip(axes, ("male", "female")):
        sub = sorted([r for r in rows if r["sex"] == sex], key=lambda r: float(r["apc_pre2020"]))
        y = range(len(sub))
        for i, r in enumerate(sub):
            a, lo, hi = float(r["apc_pre2020"]), float(r["pre2020_lo"]), float(r["pre2020_hi"])
            c = "#c0392b" if lo > 0 else ("#1f7a1f" if hi < 0 else "#888")
            ax.plot([lo, hi], [i, i], color=c, lw=1.5, alpha=0.8, zorder=1)
            ax.scatter([a], [i], color=c, s=22, zorder=2)
        ax.axvline(0, color="k", lw=0.8)
        ax.set_yticks(list(y)); ax.set_yticklabels([lab(r["site"])[:24] for r in sub], fontsize=7)
        ax.set_title(f"Saudi {sex}s", fontsize=11, fontweight="bold")
        ax.set_xlabel("Annual % change in ASR (95% CI)", fontsize=9); ax.grid(axis="x", alpha=0.25)
    fig.suptitle("Cancer incidence trend by site, Saudi nationals (SCR, ~2006–2019, PRE-break)\n"
                 "ASR APC before the 2021 census/denominator break — red = rising, green = declining, grey = flat",
                 fontsize=12, fontweight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    fig.savefig("data/fig_apc_forest.png", dpi=300, bbox_inches="tight")
    fig.savefig("data/fig_apc_forest.pdf", bbox_inches="tight"); print("[written] data/fig_apc_forest.*")


def sex_ratio():
    rows = [r for r in csv.DictReader(open("data/scr_sex_ratio.csv"))
            if r["population"] == "Saudi" and r["asr_ratio_mf"] not in ("", None) and r["icd_code"] not in NOISE]
    sites = {r["icd_code"]: r["site"] for r in rows}
    rm = recent_mean(rows, "icd_code", "asr_ratio_mf")
    rm = {k: v for k, v in rm.items() if 0 < v < 100}
    order = sorted(rm, key=rm.get)
    fig, ax = plt.subplots(figsize=(8, 9))
    for i, c in enumerate(order):
        ax.plot([1, rm[c]], [i, i], color="#bbb", lw=1, zorder=1)
        col = "#1f4e79" if rm[c] >= 1 else "#c0392b"
        ax.scatter([rm[c]], [i], color=col, s=24, zorder=2)
    ax.axvline(1, color="k", lw=0.8, label="parity (1:1)")
    ax.axvline(7, color="orange", ls="--", lw=1, label="~male:female smoking ratio (GATS)")
    ax.set_xscale("log"); ax.set_xticks([0.2, 0.5, 1, 2, 5, 10]); ax.set_xticklabels(["0.2", "0.5", "1", "2", "5", "10"])
    ax.set_yticks(range(len(order))); ax.set_yticklabels([lab(sites[c])[:24] for c in order], fontsize=7)
    ax.set_xlabel("Male : Female ASR ratio (mean 2018–2023, log scale)", fontsize=9)
    ax.set_title("Sex ratio of cancer incidence, Saudi nationals\n"
                 "lung sits far below the smoking sex-ratio — a non-smoking signal", fontsize=11, fontweight="bold")
    ax.legend(fontsize=8, frameon=False); ax.grid(axis="x", alpha=0.25)
    fig.tight_layout(); fig.savefig("data/fig_sex_ratio.png", dpi=300, bbox_inches="tight")
    fig.savefig("data/fig_sex_ratio.pdf", bbox_inches="tight"); print("[written] data/fig_sex_ratio.*")


def saudi_nonsaudi():
    rows = [r for r in csv.DictReader(open("data/scr_saudi_nonsaudi_ratio.csv"))
            if r["sex"] == "male" and r["icd_code"] not in NOISE]
    sites = {r["icd_code"]: r["site"] for r in rows}
    rm = recent_mean(rows, "icd_code", "ratio_saudi_over_nonsaudi")
    rm = {k: v for k, v in rm.items() if 0 < v < 100}
    order = sorted(rm, key=rm.get)
    fig, ax = plt.subplots(figsize=(8, 9))
    for i, c in enumerate(order):
        ax.plot([1, rm[c]], [i, i], color="#bbb", lw=1, zorder=1)
        col = "#1f4e79" if rm[c] >= 1 else "#c0392b"
        ax.scatter([rm[c]], [i], color=col, s=24, zorder=2)
    ax.axvline(1, color="k", lw=0.8)
    ax.set_xscale("log"); ax.set_xticks([0.2, 0.5, 1, 2, 5, 10]); ax.set_xticklabels(["0.2", "0.5", "1", "2", "5", "10"])
    ax.set_yticks(range(len(order))); ax.set_yticklabels([lab(sites[c])[:24] for c in order], fontsize=7)
    ax.set_xlabel("Saudi : non-Saudi male ASR ratio (mean 2018–2023, log scale)", fontsize=9)
    ax.set_title("Saudi vs non-Saudi (expatriate) males — the natural experiment\n"
                 "red (ratio < 1) = higher in expatriates → occupational/origin hypotheses", fontsize=11, fontweight="bold")
    ax.grid(axis="x", alpha=0.25)
    fig.tight_layout(); fig.savefig("data/fig_saudi_nonsaudi.png", dpi=300, bbox_inches="tight")
    fig.savefig("data/fig_saudi_nonsaudi.pdf", bbox_inches="tight"); print("[written] data/fig_saudi_nonsaudi.*")


def smoking_bundle():
    rows = [r for r in csv.DictReader(open("data/scr_smoking_bundle.csv"))
            if r["population"] == "Saudi" and int(r.get("n_sites", 0)) >= 20]  # drop incomplete 2015

    def seg(sub, key):
        s, segs = [], []
        for r in sorted(sub, key=lambda r: int(r["year"])):
            y = int(r["year"])
            if s and y != s[-1][0] + 1:
                segs.append(s); s = []
            s.append((y, float(r[key])))
        if s: segs.append(s)
        return segs

    fig, axes = plt.subplots(1, 2, figsize=(12.5, 4.8))
    # left: absolute summed ASR, males
    male = [r for r in rows if r["sex"] == "male"]
    for key, col, lbl in [("asr_smoking_bundle", "#c0392b", "Tobacco-associated bundle"),
                           ("asr_other", "#1f4e79", "All other sites")]:
        first = True
        for s in seg(male, key):
            axes[0].plot([y for y, _ in s], [v for _, v in s], marker="o", ms=3, color=col,
                         label=lbl if first else None); first = False
    axes[0].axvline(2020, color="grey", ls="--", lw=1, alpha=0.6)
    axes[0].set_title("Saudi males — absolute summed ASR", fontsize=10, fontweight="bold")
    axes[0].set_ylabel("Summed ASR /100,000", fontsize=9); axes[0].set_xlabel("Year", fontsize=9)
    axes[0].grid(alpha=0.25); axes[0].legend(fontsize=8, frameon=False)
    # right: bundle share, both sexes
    for sex, col in [("male", "#1f4e79"), ("female", "#c0392b")]:
        first = True
        for s in seg([r for r in rows if r["sex"] == sex], "bundle_share"):
            axes[1].plot([y for y, _ in s], [v * 100 for _, v in s], marker="o", ms=3, color=col,
                         label=f"Saudi {sex}s" if first else None); first = False
    axes[1].axvline(2020, color="grey", ls="--", lw=1, alpha=0.6)
    axes[1].set_title("Bundle as % of total cancer ASR", fontsize=10, fontweight="bold")
    axes[1].set_ylabel("Tobacco-bundle share (%)", fontsize=9); axes[1].set_xlabel("Year", fontsize=9)
    axes[1].set_ylim(0, 35); axes[1].grid(alpha=0.25); axes[1].legend(fontsize=8, frameon=False)
    fig.suptitle("Tobacco-associated cancers, Saudi nationals — bundle = lung, larynx, oral/pharynx, "
                 "oesophagus, bladder, pancreas (IARC 100E)\nabsolute ASR roughly doubles, but the SHARE is "
                 "stable (~27% M) — the rise is not disproportionately non-tobacco at the aggregate level",
                 fontsize=10.5, fontweight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.92]); fig.savefig("data/fig_smoking_bundle.png", dpi=300, bbox_inches="tight")
    fig.savefig("data/fig_smoking_bundle.pdf", bbox_inches="tight"); print("[written] data/fig_smoking_bundle.*")


if __name__ == "__main__":
    apc_forest(); sex_ratio(); saudi_nonsaudi(); smoking_bundle()
