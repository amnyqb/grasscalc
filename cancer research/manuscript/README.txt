Non-Tobacco Environmental Carcinogenesis — Elsevier submission package
======================================================================
Target journal : Cancer Epidemiology (Elsevier)
Category       : Evidence-mapping review + pre-specified registry-analysis protocol
Document class : elsarticle (3p, single-column)
Author         : Amin Al Yaquob, Al Yaquob Advisory, Riyadh (amin@alyaquob.com)

Files in this directory
-----------------------
  War_Exposure_Cancer_ScopingReview.tex   Main manuscript (supplement split out).
  War_Exposure_Cancer_ScopingReview.pdf   Original compiled PDF as supplied
                                           (STILL EMBEDS the supplement; rebuild
                                           with build.sh once a TeX toolchain is
                                           available to regenerate the split PDFs).
  supplementary.tex                        Standalone supplement (Figs S1-S3, Table S1).
  references.bib                           BibTeX keyed to the manuscript cite_keys.
  build.sh                                 Compiles main + supplement; checks the log.

What changed vs. the supplied source (this revision)
----------------------------------------------------
  - Corresponding-author email set to amin@alyaquob.com (was a placeholder).
  - Supplementary block (Figures S1-S3, Table S1) MOVED OUT of the main .tex into
    supplementary.tex, per Elsevier's separate-supplement requirement. The main
    .tex now ends after the bibliography with a pointer comment.
  - Figure \includegraphics repointed to Elsevier-named exports in
    ../figures/exported (Fig1..Fig4 in the main; FigS1..FigS3 in the supplement).
  - references.bib added (optional migration path; see build.sh footer).
  - No scientific content, evidence grades, causal-language levels, or the
    crude-rate (not ASIR) characterization were altered.

Figure name mapping (see ../figures/exported/figure_mapping.csv)
----------------------------------------------------------------
  Fig1  = Figure2_evidence_grade_hierarchy     FigS1 = Figure1_PRISMA_ScR_flow
  Fig2  = Figure3_metric_separation            FigS2 = Figure6_marker_site_framework
  Fig3  = Figure4_cross_cohort_benchmark       FigS3 = Figure5_saudi_timeline
  Fig4  = Figure7_proposed_DAG

Compile
-------
  ./build.sh
  # or manually:
  pdflatex War_Exposure_Cancer_ScopingReview.tex   (x3)
  pdflatex supplementary.tex                        (x2)

Citations use numbered \citet/\citep (natbib, auto-loaded by elsarticle) against
the hardcoded thebibliography; no bibtex run is needed unless you migrate to
references.bib (instructions in build.sh).

NOTE (could not be done in the build environment): the PDFs were NOT recompiled
here — no TeX toolchain and no network to install one. The supplied .pdf is the
pre-split version. Run build.sh in a TeX Live environment to produce the final
split main + supplement PDFs and to confirm zero undefined refs/citations and no
overfull boxes > 20 pt. See ../REPORT.md for the full status.

Open items before submission
-----------------------------
  - Insert the OSF project URL (Methods 2.1 and Data Availability).
  - Confirm reference identifiers flagged UNVERIFIED/NEEDS_LOOKUP/FLAG_AUTHOR
    in ../data/references.csv (no Crossref/PubMed access in build env).
  - Decide whether to cite or drop the 10 currently-uncited references if you
    migrate to \bibliography (see ../REPORT.md).
  - Optionally run the registered four-database search to populate Suppl. Fig S1.
