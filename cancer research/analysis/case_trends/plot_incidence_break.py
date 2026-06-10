#!/usr/bin/env python3
"""Diagnostic: the 2021 discontinuity in SCR all-sites incidence (Saudi nationals).

Reads the 'All sites Total' row (counts, crude, ASR) from each annual summary
table and plots case COUNTS vs the age-standardized RATE, indexed to 2010=100,
for Saudi males. The point: counts rise gently and continuously, but the ASR sat
flat 2006-2019 then STEPS UP in 2021 — because the 2022 census revised the
population denominator (back-cast to earlier years) and COVID-deferred cases
rebounded in 2021-22. The rate's jump is largely artefactual; cancer cases did
NOT double. Pre-2020 and 2021+ rates are not directly comparable.

Sources: SCR annual reports (counts/ASR); the denominator-revision + COVID-rebound
explanation is documented in Saudi Medical Journal 46(12):1463 and the SCR breast
and lung trend papers (2025).
"""
import fitz, re, csv, os
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

P = "/Users/amin/Documents/Research/cancer_research/Cancer_Reports"
PAGES = {2006: 19, 2007: 19, 2008: 19, 2009: 21, 2010: 21,
         2018: 26, 2019: 24, 2020: 24, 2021: 24, 2022: 24, 2023: 23}
NUM = re.compile(r'^-?\d[\d,]*(?:\.\d+)?$')


def total_row(yr, pg):
    d = fitz.open(f"{P}/{yr}.pdf"); ws = d[pg].get_text("words")
    tot = [w for w in ws if w[4] == "Total"] or [w for w in ws if w[4] == "ALL"]
    if not tot:
        return None
    yc = (tot[0][1] + tot[0][3]) / 2
    band = sorted((w for w in ws if abs((w[1] + w[3]) / 2 - yc) < 3.2), key=lambda w: w[0])
    nums = [w[4].replace(",", "").replace("%", "") for w in band
            if NUM.match(w[4].replace(",", "").replace("%", ""))]
    if len(nums) < 8:
        return None
    # [maleNo, male%, maleCrude, maleASR, cum, cum, femNo, fem%, femCrude, femASR, ...]
    return dict(male_n=float(nums[0]), male_crude=float(nums[2]), male_asr=float(nums[3]),
                female_n=float(nums[6]), female_crude=float(nums[8]), female_asr=float(nums[9]))


def main():
    data = {}
    for yr, pg in PAGES.items():
        r = total_row(yr, pg)
        if r:
            data[yr] = r
    with open("data/scr_allsites_total.csv", "w", newline="") as fh:
        w = csv.writer(fh); w.writerow(["year", "sex", "count", "crude", "asr"])
        for yr in sorted(data):
            for sex in ("male", "female"):
                w.writerow([yr, sex, int(data[yr][f"{sex}_n"]), data[yr][f"{sex}_crude"], data[yr][f"{sex}_asr"]])

    yrs = sorted(data)
    base = data[2010]
    def seg(metric):
        s, segs = [], []
        for y in yrs:
            if s and y != s[-1][0] + 1:
                segs.append(s); s = []
            s.append((y, 100 * data[y][metric] / base[metric]))
        if s: segs.append(s)
        return segs

    fig, ax = plt.subplots(figsize=(9, 5))
    for metric, col, lbl in [("male_n", "#1f4e79", "Case count"),
                             ("male_crude", "#7a7a7a", "Crude rate"),
                             ("male_asr", "#c0392b", "ASR (age-standardized)")]:
        first = True
        for s in seg(metric):
            ax.plot([y for y, _ in s], [v for _, v in s], marker="o", ms=4, color=col,
                    label=lbl if first else None); first = False
    ax.axhline(100, color="k", lw=0.6, ls=":")
    ax.axvline(2020, color="grey", ls="--", lw=1, alpha=0.7); ax.text(2020, ax.get_ylim()[1]*0.98, " 2020 COVID dip", fontsize=7, color="grey", va="top")
    ax.axvline(2021, color="darkorange", ls="--", lw=1, alpha=0.8); ax.text(2021, ax.get_ylim()[1]*0.85, " 2022-census\n denominator\n revision + rebound", fontsize=7, color="darkorange", va="top")
    ax.set_xlabel("Year", fontsize=9); ax.set_ylabel("Indexed to 2010 = 100", fontsize=9)
    ax.set_title("Saudi males, all cancers: counts rise gently — the RATE jumps in 2021\n"
                 "ASR flat 2006–2019 then steps up ~60%, while counts rise only ~25% → denominator/method break, not a real doubling",
                 fontsize=10.5, fontweight="bold")
    ax.legend(fontsize=9, frameon=False); ax.grid(alpha=0.25)
    fig.tight_layout(); fig.savefig("data/fig_incidence_break.png", dpi=300, bbox_inches="tight")
    fig.savefig("data/fig_incidence_break.pdf", bbox_inches="tight")
    print("[written] data/fig_incidence_break.*  and  data/scr_allsites_total.csv")
    print("\nSaudi male all-sites (count / crude / ASR):")
    for yr in yrs:
        print(f"  {yr}: {int(data[yr]['male_n']):>5}  {data[yr]['male_crude']:>5}  {data[yr]['male_asr']:>6}")


if __name__ == "__main__":
    main()
