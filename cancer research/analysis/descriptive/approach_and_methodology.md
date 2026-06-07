# Analysis approach & methodology

This documents *how* we analyze the data we have, **before** any results. It is
deliberately conservative and consistent with the framework built across the
project (metric separation, claim discipline, standard methods, keep-data-separate).

## 1. Objective of this phase
Characterize the **assembled evidence base** descriptively, and run the single
quantitative step the accessible data legitimately supports (the smoking-adjusted
residual of the Saudi contrast). This phase **describes**; it does not estimate a
causal effect.

## 2. Unit of analysis & data sources
The "data" here is an **evidence-map corpus**, not patient microdata. Three linked
levels, all in `../../data/`:
- **Reference** (n = 63) — the bibliographic corpus (`references.csv`).
- **Comparator population** (n = 13, incl. the Saudi test case) — the evidence
  matrix (`evidence_matrix.csv`).
- **Charted source row** (n = 13) — the source-level extraction
  (`extraction_table.csv`), plus **headline claims** (n = 24, `key_values.csv`)
  and the **smoking-sensitivity** output (`smoking_sensitivity_output.csv`).

## 3. What "summary statistics" means here — and what it does not
Because the corpus is overwhelmingly **categorical/structured** (grades, exposure
categories, designs, metric families), the summary statistics are **frequency
distributions and cross-tabulations** — the standard descriptive characterization
of a charted evidence base (PRISMA-ScR charting; descriptive epidemiology).

We **do not** compute means/medians of effect *magnitudes*. The reported effects
span multiple **incommensurable metric families** (ERR per dose, relative risks,
incidence-rate ratios, crude-rate ratios, modeled lifetime risk, policy lists).
Averaging across them would violate the **metric-separation rule** and produce a
meaningless number. Effect values are therefore **listed with provenance**
(`../claims_long.csv`), never aggregated. Where a range is shown, it is **within a
single metric family** and labelled as such.

## 4. Methods alignment (standard, not invented)
- **Charting / descriptive synthesis** → PRISMA-ScR; **SWiM** (Synthesis Without
  Meta-analysis) for the structured, non-pooled comparison.
- **The one quantitative step** (smoking-adjusted residual of the 5.69× crude
  contrast) → a transparent **two-category bias/sensitivity analysis**, reproduced
  in `../../accessible_analysis/ecological_residual.py`. Claim ceiling: Compatible.
- Grading vocabulary cross-walked to GRADE / Navigation Guide / OHAT (see
  `../../methodology/`); A–F labels preserved.

## 5. Explicit non-goals
- **No pooling / no meta-analysis** of the comparator effects (heterogeneous,
  incommensurable). Cross-country pooling remains a *conditional future option*
  under a federated harmonized protocol (`../../comparators/cross_country_meta_analysis.md`).
- **No causal attribution.** The Saudi signal stays at the **Compatible** level.
- **No new data invented.** Identifiers are not machine-verified (no network).

## 6. Reproducibility
`summary_stats.py` (Python standard library only) reads the CSVs in `../../data/`
and writes `summary_stats.txt` + `freq_*.csv`. Re-run:
```
python3 analysis/descriptive/summary_stats.py
```

## 7. Data limitations to keep in view
- **Identifier verification incomplete** — only 2/63 references are VERIFIED;
  the rest are best-effort/needs-lookup (no Crossref/PubMed access).
- **Heterogeneous corpus by design** — different exposures, metrics, designs,
  latency, and confounder control; this is *why* the analysis is descriptive.
- **Saudi signal is ecological** and rests on a **crude** (non-age-standardized)
  rate; the residual analysis bounds smoking, not other confounders.
