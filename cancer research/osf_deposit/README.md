# OSF deposit — Non-Tobacco Environmental Carcinogenesis (evidence map + protocol)

This folder is the intended Open Science Framework deposit accompanying the
*Cancer Epidemiology* submission by Amin Al Yaquob (Al Yaquob Advisory, Riyadh;
ORCID 0009-0006-1590-3378).

## Contents

| Path | Description |
|---|---|
| `protocol.md` | Full pre-registered protocol: evidence-map method (eligibility, sources, charting, grading/synthesis rules), the confirmatory SCR event-study specification (Section 5), and PRISMA-ScR mapping. |
| `search_strategy.md` | The registered four-database search: full MEDLINE/PubMed string plus Embase, Scopus, and Web of Science translations, and grey-literature sources. |
| `data/references.csv` | Reference register — all 63 cited works with identifier status (see integrity note below). |
| `data/evidence_matrix.csv` | Evidence matrix (manuscript Table 2): 13 comparator populations × grade, signal, native metric, role. |
| `data/extraction_table.csv` | Source-level charting/extraction sheet (Supplementary Table S1): 10 fields × 13 rows. |
| `data/key_values.csv` | Every headline numeric claim with native metric type, source cite_key, and manuscript location. |
| `data/smoking_sensitivity.py` | Reproducible computation of the smoking-prevalence sensitivity analysis (Table 3). |
| `data/smoking_sensitivity_output.csv` | Output of the script above (reproduces Table 3 exactly). |

## Reproducing Table 3

```
cd data && python3 smoking_sensitivity.py     # writes smoking_sensitivity_output.csv
```
Pure Python standard library; no dependencies.

## Provenance notes (carry into Data Availability)

- **No new primary data were collected.** All values are extracted from the
  published sources in `references.csv`.
- The Saudi lung-cancer anchor (3.36 vs 0.59 per 100,000; ≈5.7×) is a **crude
  regional incidence rate** from AlOmar et al. 2025 (*J Epidemiol Glob Health*,
  DOI 10.1007/s44197-025-00491-x; PMC12678664) — **not** age-standardized.
- **Saudi Cancer Registry microdata (1994–present) are NOT in this deposit** —
  they are the input to the *proposed* study, to be obtained under ethics approval.
- Camp Lejeune: the VA eight-condition presumptive list is a **2017 VA final
  rule** (effective 14 Mar 2017); the **2022 Camp Lejeune Justice Act** (within
  the PACT Act) created a separate civil-claim pathway — kept distinct.
- Smoking-prevalence inputs (≈27.5% men / 3.7% women) are from Saudi GATS 2019.

## Reference-identifier integrity note

DOIs/PMIDs in `references.csv` were **not machine-verified** (the build
environment had no Crossref/PubMed/network access). Rows marked `UNVERIFIED`
carry best-effort identifiers that must be confirmed before submission; rows
marked `NEEDS_LOOKUP`, `FLAG_AUTHOR`, or `NO_DOI` are described in the `note`
column. Only `va2017` and `scrlung2025` are `VERIFIED` (identifiers supplied in
the source package).
