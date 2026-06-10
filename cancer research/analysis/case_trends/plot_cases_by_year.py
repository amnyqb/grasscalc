#!/usr/bin/env python3
"""Horizontal panel of stacked bar charts: cases per year by cancer type, one
panel per country. Built to spot year-specific spikes once REAL data is supplied.

INPUT (long format CSV), columns:
    country , year , cancer_type , cases
    - country     : one panel per distinct value
    - year        : integer
    - cancer_type : harmonized category (see README; align to ICD-O-3 groups)
    - cases       : COUNT of incident cases (integer). Use counts, not rates.

USAGE
    python3 plot_cases_by_year.py --input cases.csv --out figure_cases_by_year
    python3 plot_cases_by_year.py --demo            # render the SYNTHETIC demo

IMPORTANT
    * This script does NOT contain or fetch real data. Supply your own CSV.
    * --demo generates clearly-labelled SYNTHETIC data to show the layout only.
    * Keep each country a separate panel; harmonize cancer_type + case definition
      across countries BEFORE comparing (see README). Counts are comparable only
      if case definitions match; this tool does not standardize for you.
"""
import argparse, csv, os, sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def read_long(path):
    rows = list(csv.DictReader(open(path, encoding="utf-8")))
    need = {"country", "year", "cancer_type", "cases"}
    if not rows or not need.issubset(rows[0]):
        sys.exit(f"CSV must have columns: {sorted(need)}")
    data = {}
    for r in rows:
        c = r["country"].strip()
        y = int(float(r["year"]))
        t = r["cancer_type"].strip()
        n = float(r["cases"] or 0)
        data.setdefault(c, {}).setdefault(t, {})[y] = n
    return data


def plot(data, out_prefix, title, synthetic=False):
    countries = list(data.keys())
    # global, stable ordering of cancer types -> consistent colours + stack order
    types = sorted({t for c in data.values() for t in c})
    years_all = sorted({y for c in data.values() for t in c.values() for y in t})
    cmap = plt.get_cmap("tab20")
    colour = {t: cmap(i % 20) for i, t in enumerate(types)}

    n = len(countries)
    fig, axes = plt.subplots(1, n, figsize=(max(4.2 * n, 6), 4.8), squeeze=False)
    axes = axes[0]

    for ax, country in zip(axes, countries):
        years = sorted({y for t in data[country].values() for y in t})
        bottom = np.zeros(len(years))
        for t in types:                       # stack in global order
            vals = np.array([data[country].get(t, {}).get(y, 0) for y in years])
            if vals.sum() == 0:
                continue
            ax.bar(years, vals, bottom=bottom, color=colour[t], width=0.85,
                   label=t, edgecolor="white", linewidth=0.2)
            bottom += vals
        ax.set_title(country, fontsize=10, fontweight="bold")
        ax.set_xlabel("Year", fontsize=8)
        ax.tick_params(labelsize=7)
        # show a readable subset of year ticks
        step = max(1, len(years) // 8)
        ax.set_xticks(years[::step])
        ax.set_xticklabels(years[::step], rotation=45, ha="right")
        ax.grid(axis="y", alpha=0.25, linewidth=0.5)
        if synthetic:
            ax.text(0.5, 0.5, "SYNTHETIC", transform=ax.transAxes, fontsize=22,
                    color="red", alpha=0.18, rotation=30, ha="center", va="center",
                    zorder=5, fontweight="bold")
    axes[0].set_ylabel("Incident cases (count)", fontsize=8)

    # single shared legend
    handles = [plt.Rectangle((0, 0), 1, 1, color=colour[t]) for t in types]
    fig.legend(handles, types, title="Cancer type", loc="lower center",
               ncol=min(len(types), 6), fontsize=8, title_fontsize=8,
               frameon=False, bbox_to_anchor=(0.5, -0.04))

    suptitle = title
    if synthetic:
        suptitle = "[SYNTHETIC — ILLUSTRATIVE LAYOUT, NOT REAL DATA]  " + title
    fig.suptitle(suptitle, fontsize=12, fontweight="bold",
                 color=("red" if synthetic else "black"))
    fig.text(0.5, 0.90, "Each panel = one country (kept separate). Stacks = cancer type. "
             "Harmonize cancer_type + case definition before cross-panel comparison.",
             ha="center", fontsize=7.5, style="italic", color="dimgray")
    fig.tight_layout(rect=[0, 0.06, 1, 0.9])

    png, pdf = out_prefix + ".png", out_prefix + ".pdf"
    fig.savefig(png, dpi=300, bbox_inches="tight")
    fig.savefig(pdf, bbox_inches="tight")
    print(f"[written] {png}\n[written] {pdf}")
    print(f"panels={n} countries={countries}")
    print(f"cancer_types={types}\nyears {min(years_all)}-{max(years_all)}")


def make_demo(path):
    """Clearly-synthetic data: registry-growth baseline + noise + ONE artificial
    lung spike, to demonstrate spike-spotting. NOT real. Seeded for reproducibility."""
    rng = np.random.default_rng(7)
    countries = ["Saudi Arabia (SCR)", "USA-Louisiana (SEER)", "Taiwan (TCR)", "South Korea (KCCR)"]
    types = ["Lung", "Breast", "Colorectal", "Leukaemia", "Brain/CNS", "Other"]
    years = list(range(1994, 2021))
    base = {"Lung": 80, "Breast": 120, "Colorectal": 100, "Leukaemia": 40, "Brain/CNS": 25, "Other": 150}
    scale = {"Saudi Arabia (SCR)": 1.0, "USA-Louisiana (SEER)": 2.2, "Taiwan (TCR)": 1.6, "South Korea (KCCR)": 1.8}
    rows = []
    for c in countries:
        for t in types:
            for i, y in enumerate(years):
                growth = 1 + 0.03 * i                       # registry maturation
                val = base[t] * scale[c] * growth * (1 + rng.normal(0, 0.08))
                # ONE obvious ARTIFICIAL lung spike for the Saudi panel, 2012-2015
                if c == "Saudi Arabia (SCR)" and t == "Lung" and 2012 <= y <= 2015:
                    val *= 1.9
                rows.append([c, y, t, int(max(val, 0))])
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(["country", "year", "cancer_type", "cases"]); w.writerows(rows)
    print(f"[written] {path}  (SYNTHETIC — NOT REAL DATA)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", help="long-format CSV (country,year,cancer_type,cases)")
    ap.add_argument("--out", default="figure_cases_by_year", help="output prefix")
    ap.add_argument("--title", default="Cancer incident cases per year, by type")
    ap.add_argument("--synthetic", action="store_true", help="add SYNTHETIC watermark")
    ap.add_argument("--demo", action="store_true", help="generate + plot synthetic demo")
    a = ap.parse_args()

    if a.demo:
        os.makedirs("demo", exist_ok=True)
        demo_csv = "demo/synthetic_cases_DEMO.csv"
        make_demo(demo_csv)
        plot(read_long(demo_csv), "demo/figure_cases_by_year_DEMO", a.title, synthetic=True)
        return
    if not a.input:
        sys.exit("Provide --input CSV, or use --demo. See README.")
    plot(read_long(a.input), a.out, a.title, synthetic=a.synthetic)


if __name__ == "__main__":
    main()
