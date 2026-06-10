# Submission-prep report — status, what was done, and open items

**Manuscript:** Non-Tobacco Environmental Carcinogenesis in Exposed Populations
(*Cancer Epidemiology*, Elsevier). **Author:** Amin Al Yaquob.
**Prepared:** 6 June 2026.

This package was assembled in a sandboxed build environment with **no TeX
toolchain and a PyPI-only network allowlist** (no Crossref, PubMed, doi.org, or
apt access). That constraint determined what could be completed here versus what
is handed back for the author to finish. Read this alongside `HANDOFF.md`.

## Task-by-task status

| # | Task | Status | Notes |
|---|---|---|---|
| 1 | Verify reference metadata; emit `references.bib` | **Partial** | `references.bib` (63 entries, keyed to cite_keys) + updated `data/references.csv` produced. DOIs/PMIDs could **not** be machine-verified (no network). Best-effort identifiers added per your instruction, all tagged. See breakdown below. |
| 2 | Split supplement into a separate file | **Done (source)** | `manuscript/supplementary.tex` = standalone S1–S3 + Table S1; block removed from main `.tex`. PDF not built here (no TeX). |
| 3 | Export figures to Elsevier spec | **Done** | 7 figures → vector **PDF** + **600 dpi PNG** in `figures/exported/`, named `Fig1–4`, `FigS1–3`. Font check + mapping included. EPS not generated (no ghostscript/inkscape); vector PDF is an accepted preferred format. |
| 4 | Draft submission paperwork | **Done** | `submission/`: cover letter, highlights, CRediT, declaration of interest, data availability, title page. |
| 5 | Replace placeholder email | **Done** | Set to `amin@alyaquob.com` in the `.tex` frontmatter (per your answer). |
| 6 | Build OSF deposit folder | **Done** | `osf_deposit/`: protocol, search strategy, data files, README. |
| 7 | Recompile + verify | **Partial** | No `pdflatex`/`elsarticle` and no install path here. Static checks done (citations, figure refs, counts). `build.sh` provided to recompile + auto-check the log where TeX is available. |

## Reference identifier breakdown (Task 1)

All 63 references are in `references.bib` and `data/references.csv` (now with a
`status` and `note` column). **None were machine-verified** — confirm before
submission.

| status | count | meaning |
|---|---|---|
| `VERIFIED` | 2 | identifier supplied in the source package (`va2017`, `scrlung2025`) |
| `UNVERIFIED` | 29 | best-effort DOI/PMID recalled here; **must confirm** |
| `NEEDS_LOOKUP` | 13 | journal article; DOI/PMID not reliably recalled — look up |
| `FLAG_AUTHOR` | 6 | citation entered from working notes; author/year/journal not confidently identifiable offline |
| `NO_DOI` | 13 | book / agency report / statute / thesis / grey lit (typically no DOI) |

`FLAG_AUTHOR` (need your confirmation of the work itself): `iomvao` (cite a
specific *Veterans and Agent Orange* update volume, not the series), `beirutpm2023`,
`kweon`, `paci2006`, `ksacrc`, `madinah2024` — these match the items the handoff
itself flagged as entered from working notes.

## Important finding — uncited references

Only **53 of the 63** references are actually `\cite`d in the text. These 10 are
in the bibliography but have **no in-text citation**:

`alhajj2021, basudan2023, beir1999, beirutpm2023, grosche2011, iom2005, ksacrc,
madinah2024, puma2023, whittemore1983`

With the current hardcoded `thebibliography` all 63 still print. **But if you
migrate to `\bibliography{references}` (elsarticle-num), these 10 will silently
drop** and the list becomes 53. Decide whether to (a) add in-text citations,
(b) drop them, or (c) keep them via the `\nocite{…}` line already provided
(commented) in `manuscript/build.sh`. Several (radon/uranium-miner and Gulf War
items) look like they were meant to be cited.

## Static verification performed (in lieu of a compile)

- Every `\cite` key resolves to both a `\bibitem` and a `references.bib` entry —
  **no missing citations.**
- `\bibitem` keys ↔ `references.bib` keys ↔ `references.csv` keys: **exact match,
  63 each.**
- Figure `\includegraphics` repointed and present: main uses `Fig1–4`, supplement
  uses `FigS1–3`; all exist in `figures/exported/`.
- In-figure fonts: min 12 canvas-units on a 900-unit canvas → **7.18 pt at 190 mm**
  (clears the 7 pt floor). At 90 mm single-column they would not — place
  full-text-width, as the brief specifies. (`figures/exported/font_check.txt`.)
- `smoking_sensitivity.py` runs and **reproduces** `smoking_sensitivity_output.csv`
  and Table 3 exactly.

## What still needs a TeX environment (run `manuscript/build.sh`)

- Recompile the **split** main + supplement PDFs (the supplied `.pdf` still embeds
  the supplement).
- Confirm **zero** undefined refs/citations and **no overfull boxes > 20 pt**
  (the script greps the log for both).
- Confirm figure/table numbering: main Figures 1–4 / Tables 1–4; supplement S1–S3
  / Table S1.

## Open items requiring the author (from the handoff, plus what surfaced here)

1. **OSF project URL** — create the project, then insert the URL into manuscript
   §2.1 and the Data Availability statement (placeholders noted in those files).
2. **Reference confirmation** — verify all `UNVERIFIED` identifiers and resolve
   `NEEDS_LOOKUP`/`FLAG_AUTHOR` rows in `data/references.csv` before submission.
3. **Uncited references** — decide the disposition of the 10 listed above.
4. **Four-database search** — Embase/Scopus/WoS beyond the PubMed string is
   specified but **not executed**; Suppl. Fig S1 is the planned flow. Running it
   needs live database access.
5. **EPS** — if *Cancer Epidemiology* insists on EPS over PDF, regenerate from the
   SVGs with Inkscape/Ghostscript (not available here).

## Build-environment constraints (why 1 and 7 are partial)

- Network allowlist = **PyPI only**: Crossref, PubMed/NCBI, doi.org, Semantic
  Scholar, and apt mirrors all returned `403 Host not in allowlist`. Reference
  verification therefore could not run, and TeX Live could not be installed.
- No `pdflatex`, `elsarticle`, `ghostscript`, `inkscape`, or `rsvg-convert`
  present. Figure rasterization used `cairosvg` (pure-Python, installable from
  PyPI); vector PDF is produced directly from the SVG.
