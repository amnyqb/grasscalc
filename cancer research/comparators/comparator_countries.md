# Comparator countries — decision aid (with a hard harmonization guard)

**Question:** which country offers a *comparable* setting **and** a *rich, analyzable*
dataset for the Saudi petrochemical/industrial cancer question? **This directory
is additive — no original file is modified.**

> ## ⚠️ Governing rule: HARMONIZE-THEN-BENCHMARK — never concatenate
> Do **not** merge these datasets into one analytic table. Same-named columns are
> **not** the same measurement across registries. Each country stays a **separate,
> side-by-side series**, compared only **after** reconciling definitions and a
> single standard population. This is the cross-registry extension of the
> manuscript's metric-separation rule. The field-by-field map is in
> `registry_field_crosswalk.csv` / `.json`.

## The candidates

| Country / dataset | Data richness / linkage | Access | Exposure-analog & proven method | Epi. comparability to Saudi |
|---|---|---|---|---|
| **Taiwan** — NHIRD + Taiwan Cancer Registry (HWDC) | Very high; individual linkage incl. staging, residence, occupation | Application + **on-site secure** env. (gated) | ★★★ **Mailiao / No.6 Naphtha Cracker** studies = your design, already published | Industrialization arc analog; case-mix differs (high liver/lung) |
| **Korea** — KCCR + NHIS, unified via **K-CURE / CPLD** | Very high; registry + claims + death, ~50M | Application via NHIS/K-CURE secure env. (gated) | ★★ industrial-complex cancer literature (Ulsan/Yeosu) | Industrialization arc analog; case-mix differs |
| **US** — SEER (incl. **Louisiana**) | High, case-level; less individual linkage | **Open, free, ~2-day DUA** | ★★★ "Cancer Alley" petrochemical corridor | Low (older, high lung/smoking) |
| **Kuwait / Gulf** — KCR / QNCR / GCCR | Low / closed | Gated like Saudi | ★★ shares the 1991 oil-fire exposure | ★★★ best case-mix twin |

## Recommendation (by role, not "one winner")
- **Taiwan = methodological template.** The Mailiao petrochemical-complex studies
  (residence-proximity + latency + pre/post incidence) are essentially a built,
  peer-reviewed version of the §5 design — cite them as the proven precedent.
- **SEER-Louisiana = the openly reproducible build.** Only option you can analyze
  *now* without a gated application; petrochemical-exposure analog already in the
  evidence map. Best for developing and publishing the pipeline.
- **Korea (K-CURE/CPLD) = richest linkage** if a secure-environment application is
  feasible (registry + claims + smoking from health exams → a never-smoker
  sub-analysis becomes possible, unlike SCR aggregate).
- **Kuwait/Gulf = epidemiological benchmark** (shares exposure + case-mix; closed data).

No country is a demographic twin *with* open data — so use them in these distinct
roles rather than pooling them.

## The six fields that are NOT directly comparable (must be harmonized first)
From `registry_field_crosswalk.csv`:
1. **Rate type** — never compare a **crude** rate (our Saudi anchor) with an **ASR**. Age-standardize everything.
2. **ASR standard population** — US-2000 vs World/Segi vs Korea-2000 give **different numbers for the same data**. Recompute all to **one** standard (World/Segi) or use **CI5** as the pre-harmonized layer.
3. **Multiple-primary rules** — **SEER ≠ IARC/IACR** counting → changes case counts. Pick one rule; note the residual gap.
4. **Claims vs registry** — NHIRD/NHIS **claims-defined** cancer ≠ **registry** incidence. Use the registry (TCR/KCCR/SCR) for incidence.
5. **Geography unit** — registry **catchment** ≠ administrative **region** ≠ **residence at diagnosis**. Define explicitly.
6. **Exposure ascertainment & smoking/covariates** — "exposed" labels and smoking availability differ by country; never treat them as equivalent.

## Safe workflow
1. Keep each country in its **own** file/series.
2. Map sites to **ICD-O-3 + one common grouping**; re-bin ages to a common structure.
3. Recompute **all** rates to a **single standard population** (or take them from **CI5**, which IARC already harmonized to World).
4. Present **side-by-side** (effect-direction / SWiM style) — **never** a single pooled estimate or merged table.
5. Treat each comparator as an **independent replication/benchmark**, not as added sample size.

## Files
- `comparator_countries.md` — this brief
- `registry_field_crosswalk.csv` / `.json` — field-by-field comparability map + harmonization actions

> Datasets, custodians, and access routes for these are also in
> `../analysis/raw_data_sources.*` (acquisition register). Method citations
> (Taiwan Mailiao, NHIRD/KCCR profiles) should be added to the reference register
> and verified — no Crossref/PubMed in this build environment.
