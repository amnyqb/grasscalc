# Submission-Prep Handoff — Claude Code Brief

**Manuscript:** Non-Tobacco Environmental Carcinogenesis in Exposed Populations: Evidence Grading, Metric Separation, and a Saudi Eastern Province Registry-Analysis Protocol
**Author:** Amin Al Yaquob · Al Yaquob Advisory, Riyadh, Saudi Arabia · ORCID 0009-0006-1590-3378
**Target journal:** *Cancer Epidemiology* (Elsevier)
**Manuscript category:** Evidence-mapping review + pre-specified registry-analysis protocol (NOT a completed systematic/scoping review — this distinction is deliberate; do not reintroduce "completed scoping review" language).

This package contains the compiled manuscript, its LaTeX source and figures, and the full research-data register (datasets + metadata) needed to assemble the Elsevier submission and an OSF data deposit. Read this file first.

---

## 1. Task for Claude Code

Assemble a complete Elsevier *Cancer Epidemiology* submission package from the supplied source. Concretely:

1. **Verify and complete the reference metadata.** `data/references.csv` lists all 63 cited works as they appear in the manuscript; 61 still need DOI and PMID/PMCID. Look each up on PubMed/Crossref, fill the `doi`, `pmid_or_pmcid`, and `url` columns, set `status=OK`, and flag any that cannot be located or whose author/year/journal does not match (these need author review). Then produce a clean `references.bib` (BibTeX) keyed to the existing `cite_key` values so the manuscript can switch from the hardcoded `thebibliography` to `\bibliography{references}` with `elsarticle-num` if preferred.
2. **Split the supplementary material into a separate file.** The manuscript PDF currently embeds the supplement (Figures S1–S3, Table S1) after the references. Elsevier wants supplements as separate files. Produce a standalone supplementary PDF (or DOCX if the author later requests) containing S1–S3 and Table S1, and remove that block from the main manuscript, OR keep it but generate both forms. Keep the `S`-prefixed numbering.
3. **Export figures to Elsevier artwork spec** (see §6). Source figures are vector PDF + editable SVG in `figures/`. Produce per-figure files named `Fig1`…`Fig4` and `FigS1`…`FigS3`, as vector EPS or PDF (preferred) and/or ≥300 dpi TIFF/PNG fallback. Confirm the in-figure font is ≥7 pt at final column width (90 mm single / 190 mm double).
4. **Draft the submission paperwork:** (a) cover letter to the editor; (b) Highlights (3–5 bullets, ≤85 characters each); (c) CRediT author-contribution statement (sole author); (d) Declaration of Interest statement (none); (e) Data Availability statement (no new data; charting sheet, search strategy, protocol on OSF — see `data/`). A graphical abstract is optional.
5. **Replace the placeholder corresponding-author email** `corresponding.author@domain` in the `.tex` frontmatter with the author's real address (ASK the author for it).
6. **Build the OSF deposit folder** from `data/` (extraction sheet, evidence matrix, key-values register, search strategy, sensitivity script) plus the protocol text extracted from manuscript Section 5 and Appendices A–B.
7. **Recompile and verify**: `pdflatex` ×3, zero undefined refs/citations, no overfull boxes > 20 pt, figure/table numbering consistent (main 1–4 / Tables 1–4; supplement S1–S3 / Table S1).

Do **not** alter the scientific content, evidence grades, causal-language levels, or the crude-rate (not ASIR) characterization of the Saudi contrast.

---

## 2. Manuscript metadata

| Field | Value |
|---|---|
| Title | Non-Tobacco Environmental Carcinogenesis in Exposed Populations: Evidence Grading, Metric Separation, and a Saudi Eastern Province Registry-Analysis Protocol |
| Running idea | Evidence-map + protocol; framework = evidence grading + metric separation + causal-language discipline |
| Author / affiliation | Amin Al Yaquob, Al Yaquob Advisory, Riyadh, Saudi Arabia |
| ORCID | 0009-0006-1590-3378 |
| Corresponding email | **PLACEHOLDER — replace** (`corresponding.author@domain`) |
| Document class | `elsarticle` (`3p`, single-column, Times) |
| Abstract length | 268 words (verify against journal limit, typically 250–300) |
| Main-text length | ~6,900 words (excl. references, captions, appendices, supplement) |
| References | 63 |
| Main display items | Figures 1–4; Tables 1–4 |
| Supplementary | Figures S1–S3; Table S1 |
| Keywords | evidence-mapping review; environmental carcinogenesis; Saudi Cancer Registry; Eastern Province; Kuwait oil fires; Camp Lejeune; evidence grading; metric separation; study protocol; event-study |

**Section map:** 1 Introduction · 2 Methods (2.1 approach/registration, 2.2 eligibility, 2.3 sources, 2.4 search, 2.5 selection/charting, 2.6 grading & synthesis rules, 2.7 scope-of-this-version) · 3 Results/evidence map (3.1 selection, 3.2 matrix, 3.3 synthesis by category, 3.4 markers, 3.5 temporal/spatial, 3.6 public-health relevance, 3.7 Saudi hypothesis incl. smoking-sensitivity) · 4 Discussion · 5 Proposed confirmatory study (DAG + spec) · 6 Conclusions · Declarations · Appendix A (search translations) · Appendix B (PRISMA-ScR mapping) · Supplementary material.

**Main display items:**
- Fig 1 = `Figure2_evidence_grade_hierarchy` (evidence-grade hierarchy)
- Fig 2 = `Figure3_metric_separation` (metric-separation rule)
- Fig 3 = `Figure4_cross_cohort_benchmark` (cross-cohort qualitative benchmark)
- Fig 4 = `Figure7_proposed_DAG` (DAG for proposed analysis)
- Table 1 = evidence-grade scheme · Table 2 = evidence matrix · Table 3 = smoking-prevalence sensitivity · Table 4 = proposed-study specification
- Fig S1 = `Figure1_PRISMA_ScR_flow` (planned PRISMA-ScR flow) · Fig S2 = `Figure6_marker_site_framework` · Fig S3 = `Figure5_saudi_timeline` · Table S1 = source-level extraction table

---

## 3. Datasets & research-data register (`data/`)

This is a review/evidence-map, so the "datasets" are the bibliographic corpus and the structured data charted from it. All are machine-readable.

| File | What it is | Use in package |
|---|---|---|
| `data/references.csv` | All 63 cited works, exactly as in the manuscript, with `doi`/`pmid_or_pmcid`/`url`/`status` columns | Reference-metadata audit (Task 1); source for `references.bib` |
| `data/evidence_matrix.csv` | Table 2 — 13 comparator populations: exposure category, evidence grade, best signal, native-unit metric, synthesis role | Regenerate/verify Table 2; OSF deposit |
| `data/extraction_table.csv` | Supplementary Table S1 — source-level extraction (10 fields per source × 13 rows) | Regenerate/verify Table S1; OSF deposit (the charting sheet) |
| `data/key_values.csv` | Every headline numeric claim, its native metric type, source `cite_key`, and manuscript location | Fact-check pass; provenance for any reviewer query |
| `data/smoking_sensitivity.py` | Reproducible Table 3 computation; writes `smoking_sensitivity_output.csv` | OSF deposit; reproducibility statement |

**Provenance notes (carry into the Data Availability statement):**
- No new primary data were collected. All values are extracted from published sources listed in `references.csv`.
- The Saudi lung-cancer anchor (3.36 vs 0.59 per 100,000; ~5.7×) is a **crude regional incidence rate** from AlOmar et al. 2025 (*J Epidemiol Glob Health*, DOI 10.1007/s44197-025-00491-x; PMC12678664), **not** an age-standardized rate. This is stated as such in the manuscript and must not be relabelled ASIR.
- Saudi Cancer Registry microdata (1994–present) are **not** in this package — they are the input to the *proposed* study (Section 5), to be obtained under ethics approval.
- Camp Lejeune: the VA eight-condition presumptive list is from a **2017 VA final rule** (effective 14 Mar 2017); the **2022 Camp Lejeune Justice Act** (within the PACT Act) created a separate civil-claim pathway. Keep these distinct.
- Smoking-prevalence inputs (≈27.5% men / 3.7% women) are from Saudi GATS 2019.

---

## 4. Package contents

```
HANDOFF.md                       <- this file
manuscript/
  War_Exposure_Cancer_ScopingReview.tex   <- LaTeX source (elsarticle 3p)
  War_Exposure_Cancer_ScopingReview.pdf   <- compiled, 20 pp incl. supplement
  README.txt                              <- revision/build notes
figures/
  Figure1_PRISMA_ScR_flow.{pdf,svg}       (-> Fig S1)
  Figure2_evidence_grade_hierarchy.{pdf,svg}  (-> Fig 1)
  Figure3_metric_separation.{pdf,svg}     (-> Fig 2)
  Figure4_cross_cohort_benchmark.{pdf,svg}    (-> Fig 3)
  Figure5_saudi_timeline.{pdf,svg}        (-> Fig S3)
  Figure6_marker_site_framework.{pdf,svg} (-> Fig S2)
  Figure7_proposed_DAG.{pdf,svg}          (-> Fig 4)
data/
  references.csv          (63 refs; 61 need DOI/PMID)
  evidence_matrix.csv     (Table 2)
  extraction_table.csv    (Table S1 / charting sheet)
  key_values.csv          (numeric claims + provenance)
  smoking_sensitivity.py  (reproducible Table 3)
```

---

## 5. Reference status

`data/references.csv` `status` column: `OK` = identifier already filled; `VERIFY` = needs lookup. Two are `OK` (`scrlung2025`, `va2017`); the other 61 are `VERIFY`. For each VERIFY row: confirm authors/year/journal/volume/pages against PubMed/Crossref, fill DOI + PMID/PMCID + canonical URL, and correct any field that does not match the indexed record. Flag for author review any reference that is hard to locate; several were entered from working notes and need confirmation (e.g. `kweon`, `paci2006`, `ksacrc`, `madinah2024`, `iomvao`, `beirutpm2023`). Then emit `references.bib`.

---

## 6. Figure / artwork specifications (Elsevier)

- Preferred: vector **EPS or PDF**. We supply vector PDF + editable SVG. Convert/export to the journal's required format and name `Fig1`…`Fig4`, `FigS1`…`FigS3`.
- Minimum in-figure font **7 pt** at final print size (6 pt for sub/superscripts). All source figures were built with a 12 px floor on a ~900-unit-wide canvas, which clears 7 pt at 190 mm — re-confirm after any rescale.
- Column widths: **90 mm** (single) or **190 mm** (double). These are conceptual diagrams; place full-text-width.
- Raster fallback: ≥300 dpi (halftone), ≥500 dpi (combination), ≥1000 dpi (line art).
- Figure titles are **not** embedded in the artwork (Elsevier convention); the `\caption` is the sole label. Do not re-add titles to the SVG/PDF.

---

## 7. Paperwork to draft

- **Highlights:** 3–5 bullets, ≤85 characters each. Suggested themes: evidence-grading + metric-separation framework; radiation/solvent cohorts establish non-tobacco causation; lung contrast is crude-rate, smoking-insufficient; pre-specified SCR event-study protocol.
- **Cover letter:** state the category (evidence-map + protocol), fit with *Cancer Epidemiology* (risk factors, methodology, registry analysis), novelty (the framework + protocol), and that no part is under consideration elsewhere.
- **CRediT:** sole author — Conceptualization, Methodology, Investigation, Data curation, Writing – original draft, Writing – review & editing.
- **Declaration of Interest:** none.
- **Data Availability:** "No new data were analysed. The charting/extraction sheet, full search strategy, reference register, and the smoking-sensitivity calculation are available in the supplementary `data/` set and will be deposited on the Open Science Framework. Saudi Cancer Registry microdata for the proposed analysis are available from the Saudi Ministry of Health under ethics approval."

---

## 8. Open items requiring the author (surface these, do not invent)

1. Corresponding-author email (replace placeholder).
2. OSF project URL once created (insert into Methods 2.1 and Data Availability).
3. The **registered four-database search** (Embase/Scopus/WoS in addition to the PubMed string in Appendix A) has not been executed; Supplementary Figure S1 is the *planned* flow. If the author wants this run before submission, it requires live database access; otherwise the evidence-map + protocol framing stands as-is.
4. Any reference flagged unverifiable in Task 1.

---

## 9. Compile / environment

```
# requires TeX Live with elsarticle (texlive-publishers)
cd manuscript
pdflatex -interaction=nonstopmode War_Exposure_Cancer_ScopingReview.tex
pdflatex -interaction=nonstopmode War_Exposure_Cancer_ScopingReview.tex
pdflatex -interaction=nonstopmode War_Exposure_Cancer_ScopingReview.tex
```
Citations use numbered `\citet`/`\citep` (natbib, auto-loaded by elsarticle) against a hardcoded `thebibliography`; no `bibtex` run is needed unless you migrate to `references.bib`. The landscape Table S1 uses the `rotating` package (`sidewaystable`).
