#!/usr/bin/env python3
"""Long-run lung cancer (C33-C34) trend for Saudi nationals: age-standardized
incidence rate (ASR, World standard, /100,000) by sex, plus annual counts.

Input : data/scr_lung_by_sex_asr_<minY>_<maxY>.csv  (from extract_lung_series.py)
        columns: year, male_n, female_n, total, male_asr, female_asr, ...
Output: data/scr_lung_asr_trend.{png,pdf}  (ASR by sex, the rate trend)
        data/scr_lung_counts_trend.{png,pdf} (counts by sex, for reference)

Reading notes baked into the figure:
  * 2020 is depressed by COVID-19 registration disruption (dashed marker).
  * ASR (rate) is the trend to read; counts rise partly with population growth.
  * Gaps (2004/2014/2015/2017) are missing/flagged years -- the line breaks there
    rather than interpolating (no fabricated points).
"""
import argparse, csv, os
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt


def read(path):
    rows = list(csv.DictReader(open(path, encoding="utf-8")))
    def col(name):
        out = []
        for r in rows:
            y = int(r["year"]); v = r.get(name, "").strip()
            out.append((y, float(v) if v else None))
        return out
    return col


def _series(pairs):
    """Split into contiguous segments at None so the line breaks over gaps."""
    seg, segs = [], []
    for y, v in pairs:
        if v is None:
            if seg: segs.append(seg); seg = []
        else:
            seg.append((y, v))
    if seg: segs.append(seg)
    return segs


def plot(col, out, ycol_m, ycol_f, ylabel, title):
    m, f = col(ycol_m), col(ycol_f)
    fig, ax = plt.subplots(figsize=(8.2, 4.8))
    for pairs, colour, lab in [(m, "#1f4e79", "Male"), (f, "#c0392b", "Female")]:
        first = True
        for seg in _series(pairs):
            xs = [y for y, _ in seg]; ys = [v for _, v in seg]
            ax.plot(xs, ys, marker="o", ms=4, lw=1.8, color=colour,
                    label=lab if first else None); first = False
    # COVID marker
    ax.axvline(2020, color="grey", ls="--", lw=1, alpha=0.7)
    ax.text(2020, ax.get_ylim()[1], " 2020 COVID\n registration dip",
            color="grey", fontsize=7, va="top", ha="left")
    ax.set_xlabel("Year", fontsize=9); ax.set_ylabel(ylabel, fontsize=9)
    ax.set_title(title, fontsize=12, fontweight="bold")
    ax.grid(alpha=0.25); ax.legend(frameon=False, fontsize=9)
    ax.margins(x=0.02)
    fig.tight_layout()
    fig.savefig(out + ".png", dpi=300, bbox_inches="tight")
    fig.savefig(out + ".pdf", bbox_inches="tight")
    print("[written]", out + ".png /", out + ".pdf")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default="data/scr_lung_by_sex_asr_2004_2023.csv")
    a = ap.parse_args()
    col = read(a.input)
    plot(col, "data/scr_lung_asr_trend", "male_asr", "female_asr",
         "Age-standardized rate (World) per 100,000",
         "Saudi nationals: lung cancer (C33–C34) ASR by sex, SCR 2006–2023")
    plot(col, "data/scr_lung_counts_trend", "male_n", "female_n",
         "Annual incident cases (count)",
         "Saudi nationals: lung cancer (C33–C34) incident cases by sex, SCR")
