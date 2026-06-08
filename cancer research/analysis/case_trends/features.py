#!/usr/bin/env python3
"""Phase 1 feature engineering over data/scr_all_sites_long.csv.

Derived, defensible, registry-only metrics (all ecological; no individual
exposure data). Writes:

  data/scr_apc_summary.csv          per (population, sex, site): annual % change
                                    (APC) of ASR via log-linear OLS, 95% CI, R2,
                                    and an APC computed with 2020 (COVID) dropped.
  data/scr_sex_ratio.csv            per (population, year, site): M:F of ASR & count.
  data/scr_saudi_nonsaudi_ratio.csv per (sex, year, site): Saudi/non-Saudi ASR.
  data/scr_smoking_bundle.csv       per (population, sex, year): summed ASR of a
                                    strongly tobacco-associated bundle vs all-other.
  data/scr_features_long.csv        the long table + within-year burden_share.

Notes / integrity
  * ASR = World standard /100,000. 2020 is a COVID registration artifact (hence the
    drop-2020 APC variant). Saudi all-sites covers 2006-2010/2015-2016/2018-2023
    with a 2011-2014 & 2017 gap; APC is fit on available years and n is reported.
  * The "smoking bundle" is the set of sites with the highest tobacco
    attributable fraction (IARC Monograph 100E): lung, larynx, oral cavity &
    pharynx, oesophagus, bladder, pancreas. It is a descriptive grouping, NOT an
    attribution — the registry has no smoking data.
  * Aggregate rows ("all sites but C44") are excluded from per-site features.
"""
import csv, os
import numpy as np

SRC = "data/scr_all_sites_long.csv"

# strongly tobacco-associated sites (IARC 100E) -> ICD-10 codes present in the data
SMOKING_CODES = {
    "C33-C34",                              # lung
    "C32",                                  # larynx
    "C00", "C01-C02", "C03-C06", "C07-C08", "C09", "C10", "C11", "C12-C13", "C14",  # oral cavity & pharynx
    "C15",                                  # oesophagus
    "C67",                                  # bladder
    "C25",                                  # pancreas
}
EXCLUDE = {"C44"}  # this code = "all sites but C44" aggregate, not a site


def load():
    rows = []
    for r in csv.DictReader(open(SRC, encoding="utf-8")):
        if r["icd_code"] in EXCLUDE or "all sites" in r["site"].lower():
            continue
        r["year"] = int(r["year"])
        for k in ("count", "crude", "asr"):
            r[k] = float(r[k]) if r[k] not in ("", None) else None
        rows.append(r)
    return rows


def clean_site(s):
    # drop a leading repeated ICD code if present, tidy whitespace
    return " ".join(s.replace("ﬁ", "fi").split())


def apc(years, vals):
    """Log-linear annual percent change with 95% CI (normal approx) and R^2."""
    xy = [(y, v) for y, v in zip(years, vals) if v and v > 0]
    if len(xy) < 5:
        return None
    x = np.array([a for a, _ in xy], float)
    y = np.log(np.array([b for _, b in xy], float))
    X = np.vstack([np.ones_like(x), x]).T
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    resid = y - X @ beta
    dof = len(x) - 2
    sigma2 = (resid @ resid) / dof if dof > 0 else 0.0
    se = np.sqrt(np.diag(sigma2 * np.linalg.inv(X.T @ X)))[1]
    ss_tot = ((y - y.mean()) ** 2).sum()
    r2 = 1 - (resid @ resid) / ss_tot if ss_tot > 0 else float("nan")
    return dict(apc=100 * (np.expm1(beta[1])),
                lo=100 * (np.expm1(beta[1] - 1.96 * se)),
                hi=100 * (np.expm1(beta[1] + 1.96 * se)),
                n=len(xy), r2=r2)


def main():
    rows = load()
    sites = {r["icd_code"]: clean_site(r["site"]) for r in rows}
    by = {}  # (pop, sex, code) -> {year: row}
    for r in rows:
        by.setdefault((r["population"], r["sex"], r["icd_code"]), {})[r["year"]] = r

    # --- APC summary ---
    with open("data/scr_apc_summary.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["population", "sex", "icd_code", "site", "n_years",
                    "apc_pct", "ci_lo", "ci_hi", "r2",
                    "apc_excl2020", "first_year", "last_year",
                    "asr_first", "asr_last"])
        for (pop, sex, code), d in sorted(by.items()):
            yrs = sorted(d)
            vals = [d[y]["asr"] for y in yrs]
            a = apc(yrs, vals)
            if not a:
                continue
            a2 = apc([y for y in yrs if y != 2020], [d[y]["asr"] for y in yrs if y != 2020])
            fy, ly = yrs[0], yrs[-1]
            w.writerow([pop, sex, code, sites.get(code, ""), a["n"],
                        f"{a['apc']:.2f}", f"{a['lo']:.2f}", f"{a['hi']:.2f}", f"{a['r2']:.3f}",
                        f"{a2['apc']:.2f}" if a2 else "",
                        fy, ly, d[fy]["asr"], d[ly]["asr"]])

    # --- sex ratio (M:F) ---
    with open("data/scr_sex_ratio.csv", "w", newline="") as fh:
        w = csv.writer(fh); w.writerow(["population", "year", "icd_code", "site",
                                        "asr_ratio_mf", "count_ratio_mf", "asr_m", "asr_f"])
        codes = sorted({r["icd_code"] for r in rows})
        for pop in ("Saudi", "non-Saudi"):
            for yr in sorted({r["year"] for r in rows if r["population"] == pop}):
                for code in codes:
                    m = by.get((pop, "male", code), {}).get(yr)
                    f = by.get((pop, "female", code), {}).get(yr)
                    if not m or not f:
                        continue
                    ar = (m["asr"] / f["asr"]) if (m["asr"] and f["asr"]) else ""
                    cr = (m["count"] / f["count"]) if (m["count"] and f["count"]) else ""
                    w.writerow([pop, yr, code, sites.get(code, ""),
                                f"{ar:.2f}" if ar != "" else "", f"{cr:.2f}" if cr != "" else "",
                                m["asr"], f["asr"]])

    # --- Saudi / non-Saudi ASR ratio ---
    with open("data/scr_saudi_nonsaudi_ratio.csv", "w", newline="") as fh:
        w = csv.writer(fh); w.writerow(["sex", "year", "icd_code", "site",
                                        "asr_saudi", "asr_nonsaudi", "ratio_saudi_over_nonsaudi"])
        for sex in ("male", "female"):
            for yr in sorted({r["year"] for r in rows if r["population"] == "non-Saudi"}):
                for code in sorted({r["icd_code"] for r in rows}):
                    s = by.get(("Saudi", sex, code), {}).get(yr)
                    n = by.get(("non-Saudi", sex, code), {}).get(yr)
                    if not s or not n or not s["asr"] or not n["asr"]:
                        continue
                    w.writerow([sex, yr, code, sites.get(code, ""),
                                s["asr"], n["asr"], f"{s['asr']/n['asr']:.2f}"])

    # --- smoking bundle vs other (summed ASR) ---
    with open("data/scr_smoking_bundle.csv", "w", newline="") as fh:
        w = csv.writer(fh); w.writerow(["population", "sex", "year",
                                        "asr_smoking_bundle", "asr_other", "bundle_share", "n_sites"])
        all_codes = sorted({r["icd_code"] for r in rows})
        for (pop, sex) in sorted({(r["population"], r["sex"]) for r in rows}):
            for yr in sorted({r["year"] for r in rows if r["population"] == pop}):
                bundle = other = 0.0; n = 0
                for code in all_codes:
                    rr = by.get((pop, sex, code), {}).get(yr)
                    if not rr or not rr["asr"]:
                        continue
                    n += 1
                    if code in SMOKING_CODES:
                        bundle += rr["asr"]
                    else:
                        other += rr["asr"]
                tot = bundle + other
                if tot > 0:
                    # n_sites lets the plot drop years with incomplete site coverage
                    # (e.g. 2015, where only ~9 sites were machine-readable).
                    w.writerow([pop, sex, yr, f"{bundle:.2f}", f"{other:.2f}", f"{bundle/tot:.3f}", n])

    # --- enriched long with burden share ---
    tot = {}
    for r in rows:
        if r["count"]:
            tot[(r["population"], r["sex"], r["year"])] = tot.get((r["population"], r["sex"], r["year"]), 0) + r["count"]
    with open("data/scr_features_long.csv", "w", newline="") as fh:
        w = csv.writer(fh); w.writerow(["year", "population", "sex", "icd_code", "site",
                                        "count", "crude", "asr", "burden_share", "crude_asr_ratio"])
        for r in rows:
            t = tot.get((r["population"], r["sex"], r["year"]))
            bs = (r["count"] / t) if (r["count"] and t) else ""
            car = (r["crude"] / r["asr"]) if (r["crude"] and r["asr"]) else ""
            w.writerow([r["year"], r["population"], r["sex"], r["icd_code"], clean_site(r["site"]),
                        r["count"], r["crude"], r["asr"],
                        f"{bs:.4f}" if bs != "" else "", f"{car:.3f}" if car != "" else ""])

    print("[written] data/scr_apc_summary.csv, scr_sex_ratio.csv, "
          "scr_saudi_nonsaudi_ratio.csv, scr_smoking_bundle.csv, scr_features_long.csv")


if __name__ == "__main__":
    main()
