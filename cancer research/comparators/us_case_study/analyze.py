#!/usr/bin/env python3
"""Smoking-adjusted, population-weighted ecological models of cancer incidence on
industrial (point-source) air-toxic exposure, per sentinel site, US counties.

For each sentinel site s:
    z(incidence_s) ~ z(industrial_pollution) + z(smoking) + urban(RUCC)
weighted by county population, with heteroskedasticity-robust (HC0) SEs.
Predictors and outcome are z-scored per site so the industrial-pollution
coefficient is a comparable standardized partial effect across sites.

Reads  data/us_county_merged.csv  (from pull_data.py --states all)
Writes data/us_models_coeffs.csv  and  data/fig_pollution_forest.{png,pdf}

The thesis-relevant pattern: the smoking-adjusted pollution effect is ~null for
smoking-saturated lung and for the melanoma negative control, but positive for
benzene/solvent sentinels (leukaemia, NHL, bladder, kidney). ECOLOGICAL, modeled
exposure, cross-sectional -> association, not causation.
"""
import csv, os
import numpy as np
from scipy import stats
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

SRC = "data/us_county_merged.csv"


def load():
    by = {}
    for r in csv.DictReader(open(SRC)):
        try:
            rec = dict(fips=r["fips"], site=r["site"],
                       inc=float(r["incidence"]), smoke=float(r["smoking_pct"]),
                       poll=float(r["ind_pollution"]), pop=float(r["population"]),
                       urban=1.0 if "Urban" in r["rucc"] else (0.0 if "Rural" in r["rucc"] else np.nan))
        except (ValueError, KeyError):
            continue
        by.setdefault(r["site"], []).append(rec)
    return by


def z(a):
    a = np.asarray(a, float); s = a.std()
    return (a - a.mean()) / s if s > 0 else a * 0


def wls_robust(y, X, w):
    XtW = X.T * w
    XtWXinv = np.linalg.inv(XtW @ X)
    beta = XtWXinv @ (XtW @ y)
    resid = y - X @ beta
    meat = (X.T * (w ** 2 * resid ** 2)) @ X         # HC0 sandwich meat for WLS
    cov = XtWXinv @ meat @ XtWXinv
    se = np.sqrt(np.diag(cov))
    ss_tot = np.sum(w * (y - np.average(y, weights=w)) ** 2)
    r2 = 1 - np.sum(w * resid ** 2) / ss_tot
    return beta, se, r2


def fit(recs):
    recs = [r for r in recs if np.isfinite(r["urban"])]
    if len(recs) < 30:
        return None
    y = z([r["inc"] for r in recs])
    poll = z([r["poll"] for r in recs]); smoke = z([r["smoke"] for r in recs])
    urban = np.array([r["urban"] for r in recs]); w = np.array([r["pop"] for r in recs])
    n = len(recs)
    # adjusted model
    X = np.column_stack([np.ones(n), poll, smoke, urban])
    b, se, r2 = wls_robust(y, X, w)
    # crude (pollution only)
    Xc = np.column_stack([np.ones(n), poll])
    bc, sec, _ = wls_robust(y, Xc, w)
    zc = b[1] / se[1]
    return dict(n=n, poll_adj=b[1], poll_adj_se=se[1],
                poll_adj_lo=b[1] - 1.96 * se[1], poll_adj_hi=b[1] + 1.96 * se[1],
                p=2 * stats.norm.sf(abs(zc)), smoke_adj=b[2], smoke_se=se[2],
                poll_crude=bc[1], r2=r2)


ORDER = ["Leukaemia", "NHL", "Bladder", "Kidney", "Liver", "Lung", "Melanoma(negctrl)"]


def main():
    by = load()
    res = {}
    for site, recs in by.items():
        f = fit(recs)
        if f:
            res[site] = f
    with open("data/us_models_coeffs.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["site", "n_counties", "poll_crude_beta", "poll_adj_beta",
                    "poll_adj_lo", "poll_adj_hi", "p_value", "smoking_beta", "r2"])
        for site in sorted(res, key=lambda s: ORDER.index(s) if s in ORDER else 99):
            d = res[site]
            w.writerow([site, d["n"], f"{d['poll_crude']:.3f}", f"{d['poll_adj']:.3f}",
                        f"{d['poll_adj_lo']:.3f}", f"{d['poll_adj_hi']:.3f}",
                        f"{d['p']:.4f}", f"{d['smoke_adj']:.3f}", f"{d['r2']:.3f}"])
    print(f"{'site':<20}{'n':>5}{'pollβ crude':>12}{'pollβ adj':>11}{'95% CI':>16}{'smokeβ':>9}")
    for site in sorted(res, key=lambda s: ORDER.index(s) if s in ORDER else 99):
        d = res[site]
        print(f"{site:<20}{d['n']:>5}{d['poll_crude']:>12.2f}{d['poll_adj']:>11.2f}"
              f"  [{d['poll_adj_lo']:>5.2f},{d['poll_adj_hi']:>5.2f}]{d['smoke_adj']:>9.2f}")

    # forest plot of smoking-adjusted pollution effect
    sites = [s for s in ORDER if s in res]
    fig, ax = plt.subplots(figsize=(8.5, 5.5))
    for i, s in enumerate(sites):
        d = res[s]
        sig = d["poll_adj_lo"] > 0 or d["poll_adj_hi"] < 0
        col = ("#c0392b" if d["poll_adj"] > 0 else "#1f7a1f") if sig else "#888"
        ax.plot([d["poll_adj_lo"], d["poll_adj_hi"]], [i, i], color=col, lw=2, alpha=.8)
        ax.scatter([d["poll_adj"]], [i], color=col, s=40, zorder=3)
    ax.axvline(0, color="k", lw=.8)
    ax.set_yticks(range(len(sites)))
    ax.set_yticklabels([s.replace("(negctrl)", " (neg. control)") for s in sites])
    ax.invert_yaxis()
    ax.set_xlabel("Smoking-adjusted industrial-pollution effect on incidence\n"
                  "(standardized β per 1-SD point-source air-toxic risk; pop-weighted, HC-robust)", fontsize=9)
    ax.set_title("Does industrial air pollution predict cancer once smoking is held constant?\n"
                 "US counties — red = positive, green = negative, grey = null",
                 fontsize=11, fontweight="bold")
    ax.grid(axis="x", alpha=.25)
    fig.tight_layout()
    fig.savefig("data/fig_pollution_forest.png", dpi=300, bbox_inches="tight")
    fig.savefig("data/fig_pollution_forest.pdf", bbox_inches="tight")
    print("\n[written] data/us_models_coeffs.csv, data/fig_pollution_forest.*")


if __name__ == "__main__":
    main()
