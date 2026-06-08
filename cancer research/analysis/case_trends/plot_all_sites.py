#!/usr/bin/env python3
"""Views over the all-sites dataset (data/scr_all_sites_long.csv).

Produces:
  data/scr_asr_trends_saudi.{png,pdf}      ASR by year, top sites, Saudi M/F panels
  data/scr_asr_saudi_vs_nonsaudi.{png,pdf} ASR by year, key sites, Saudi vs non-Saudi
  data/scr_asr_by_site_saudi_male.csv      wide pivot (year x site) of Saudi male ASR
  data/scr_asr_by_site_saudi_female.csv    wide pivot (year x site) of Saudi female ASR

ASR = World standard /100,000. Lines break over missing years (no interpolation).
2020 is a COVID registration artifact. Non-Saudi (expatriate) rates are based on a
young, incompletely-captured population — read with caution.
"""
import csv, os, argparse
from collections import defaultdict
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

ICD_LABEL = {  # tidy display names for the common sites
    "C50": "Breast", "C18": "Colon", "C19-C20": "Rectum", "C73": "Thyroid",
    "C82-C85;C96": "NHL", "C91": "Leukaemia", "C22": "Liver", "C33-C34": "Lung",
    "C61": "Prostate", "C67": "Bladder", "C16": "Stomach", "C54": "Corpus uteri",
    "C81": "Hodgkin", "C64": "Kidney", "C70-C72": "Brain/CNS",
}


def load(path):
    rows = list(csv.DictReader(open(path, encoding="utf-8")))
    for r in rows:
        r["year"] = int(r["year"])
        for k in ("count", "crude", "asr"):
            r[k] = float(r[k]) if r[k] not in ("", None) else None
    return rows


def series(rows, pop, sex, code):
    d = {r["year"]: r["asr"] for r in rows
         if r["population"] == pop and r["sex"] == sex and r["icd_code"] == code and r["asr"] is not None}
    return d


def segments(d):
    seg, segs = [], []
    for y in sorted(d):
        if seg and y != seg[-1][0] + 1:
            segs.append(seg); seg = []
        seg.append((y, d[y]))
    if seg: segs.append(seg)
    return segs


def top_codes(rows, pop, n=8):
    last = max(r["year"] for r in rows if r["population"] == pop)
    tot = defaultdict(float)
    for r in rows:
        if r["population"] == pop and r["year"] == last and r["count"]:
            tot[r["icd_code"]] += r["count"]
    codes = [c for c in sorted(tot, key=tot.get, reverse=True) if c in ICD_LABEL][:n]
    return codes


def plot_panels(rows, pop, codes, out, title):
    cmap = plt.get_cmap("tab10")
    colour = {c: cmap(i % 10) for i, c in enumerate(codes)}
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.8), sharey=False)
    for ax, sex in zip(axes, ("male", "female")):
        for c in codes:
            d = series(rows, pop, sex, c)
            first = True
            for seg in segments(d):
                xs = [y for y, _ in seg]; ys = [v for _, v in seg]
                ax.plot(xs, ys, marker="o", ms=3, lw=1.6, color=colour[c],
                        label=ICD_LABEL[c] if first else None); first = False
        ax.axvline(2020, color="grey", ls="--", lw=1, alpha=0.6)
        ax.set_title(f"{sex.capitalize()}", fontsize=10, fontweight="bold")
        ax.set_xlabel("Year", fontsize=9); ax.grid(alpha=0.25)
    axes[0].set_ylabel("ASR (World) per 100,000", fontsize=9)
    h, l = axes[0].get_legend_handles_labels()
    fig.legend(h, l, loc="lower center", ncol=min(len(codes), 8), fontsize=8,
               frameon=False, bbox_to_anchor=(0.5, -0.06))
    fig.suptitle(title, fontsize=12, fontweight="bold")
    fig.tight_layout(rect=[0, 0.04, 1, 0.96])
    fig.savefig(out + ".png", dpi=300, bbox_inches="tight")
    fig.savefig(out + ".pdf", bbox_inches="tight")
    print("[written]", out + ".png /", out + ".pdf")


def plot_compare(rows, codes, out, title):
    cmap = plt.get_cmap("tab10")
    colour = {c: cmap(i % 10) for i, c in enumerate(codes)}
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.8))
    for ax, pop in zip(axes, ("Saudi", "non-Saudi")):
        for c in codes:
            # both sexes combined view not available as ASR; show male
            d = series(rows, pop, "male", c)
            first = True
            for seg in segments(d):
                xs = [y for y, _ in seg]; ys = [v for _, v in seg]
                ax.plot(xs, ys, marker="o", ms=3, lw=1.6, color=colour[c],
                        label=ICD_LABEL[c] if first else None); first = False
        ax.axvline(2020, color="grey", ls="--", lw=1, alpha=0.6)
        ax.set_title(pop + " males", fontsize=10, fontweight="bold")
        ax.set_xlabel("Year", fontsize=9); ax.grid(alpha=0.25)
    axes[0].set_ylabel("ASR (World) per 100,000", fontsize=9)
    h, l = axes[0].get_legend_handles_labels()
    fig.legend(h, l, loc="lower center", ncol=min(len(codes), 8), fontsize=8,
               frameon=False, bbox_to_anchor=(0.5, -0.06))
    fig.suptitle(title, fontsize=12, fontweight="bold")
    fig.tight_layout(rect=[0, 0.04, 1, 0.96])
    fig.savefig(out + ".png", dpi=300, bbox_inches="tight")
    fig.savefig(out + ".pdf", bbox_inches="tight")
    print("[written]", out + ".png /", out + ".pdf")


def pivot(rows, pop, sex, out):
    codes = sorted({r["icd_code"] for r in rows if r["population"] == pop}, )
    years = sorted({r["year"] for r in rows if r["population"] == pop})
    lab = {c: ICD_LABEL.get(c, c) for c in codes}
    table = {(r["year"], r["icd_code"]): r["asr"] for r in rows
             if r["population"] == pop and r["sex"] == sex}
    with open(out, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["year"] + [lab[c] for c in codes])
        for y in years:
            w.writerow([y] + [table.get((y, c), "") for c in codes])
    print("[written]", out)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default="data/scr_all_sites_long.csv")
    a = ap.parse_args()
    rows = load(a.input)
    saudi_codes = top_codes(rows, "Saudi", 8)
    plot_panels(rows, "Saudi", saudi_codes, "data/scr_asr_trends_saudi",
                "Saudi nationals: ASR trend, most common sites (SCR)")
    compare_codes = [c for c in ["C50", "C18", "C73", "C33-C34", "C22"] ]
    plot_compare(rows, compare_codes, "data/scr_asr_saudi_vs_nonsaudi",
                 "ASR trend, Saudi vs non-Saudi males (SCR)")
    pivot(rows, "Saudi", "male", "data/scr_asr_by_site_saudi_male.csv")
    pivot(rows, "Saudi", "female", "data/scr_asr_by_site_saudi_female.csv")
