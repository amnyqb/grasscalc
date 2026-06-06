# Cancer Epidemiology submission package

Submission-prep workspace for **"Non-Tobacco Environmental Carcinogenesis in
Exposed Populations: Evidence Grading, Metric Separation, and a Saudi Eastern
Province Registry-Analysis Protocol"** (Amin Al Yaquob; target journal: *Cancer
Epidemiology*, Elsevier).

**Start with [`REPORT.md`](REPORT.md)** — it has the task-by-task status, what was
completed in this environment, the reference-verification breakdown, and the open
items for the author.

## Layout

```
HANDOFF.md            Original brief (record).
REPORT.md             Status, blockers, author action items. READ FIRST.
manuscript/
  War_Exposure_Cancer_ScopingReview.tex   Main (supplement split out; email set;
                                          figures repointed to exports).
  War_Exposure_Cancer_ScopingReview.pdf   Original supplied PDF (pre-split).
  supplementary.tex                       Standalone supplement (S1-S3, Table S1).
  references.bib                          BibTeX keyed to manuscript cite_keys.
  build.sh                                Compile main + supplement; check log.
  README.txt                              Build notes / change log.
figures/
  Figure1..7.{pdf,svg}                     Originals.
  exported/  Fig1..Fig4, FigS1..FigS3      Elsevier-named PDF + 600 dpi PNG,
             figure_mapping.csv, font_check.txt
data/
  references.csv         63 refs + identifier status/notes (Task 1 output).
  evidence_matrix.csv    Table 2.
  extraction_table.csv   Table S1 / charting sheet.
  key_values.csv         Headline numeric claims + provenance.
  smoking_sensitivity.py + .csv   Reproducible Table 3.
submission/
  cover_letter.md  highlights.md  credit_statement.md
  declaration_of_interest.md  data_availability.md  title_page.md
osf_deposit/
  protocol.md  search_strategy.md  README.md  data/
```

## Reproduce / build

```
cd manuscript && ./build.sh                 # needs TeX Live + elsarticle (not in this env)
cd data && python3 smoking_sensitivity.py   # reproduces Table 3 (stdlib only)
```

> Identifiers in `data/references.csv` were not machine-verified (no network in
> the build environment). See `REPORT.md` before submitting.
