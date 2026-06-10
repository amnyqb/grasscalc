#!/usr/bin/env bash
# Build the main manuscript and the standalone supplement.
# Requires TeX Live with elsarticle (texlive-publishers) and the rotating package.
# Figures are read from ../figures/exported (Elsevier-named Fig1..Fig4, FigS1..FigS3).
set -euo pipefail
cd "$(dirname "$0")"

MAIN=War_Exposure_Cancer_ScopingReview
SUPP=supplementary

# Make the exported figures resolvable from this directory.
ln -sfn ../figures figures

echo ">> Building main manuscript ($MAIN)…"
for i in 1 2 3; do
  pdflatex -interaction=nonstopmode -halt-on-error "$MAIN.tex" >/dev/null
done

echo ">> Building supplement ($SUPP)…"
for i in 1 2; do
  pdflatex -interaction=nonstopmode -halt-on-error "$SUPP.tex" >/dev/null
done

echo ">> Done: $MAIN.pdf, $SUPP.pdf"
echo ">> Checking the log for undefined references/citations and overfull boxes:"
grep -nE "undefined (reference|citation)|There were undefined" "$MAIN.log" || echo "   none."
grep -nE "Overfull \\\\hbox \([0-9.]+pt" "$MAIN.log" | awk -F'[()]' '{print $2, $0}' \
  | awk '$1+0 > 20 {print "   OVERFULL >20pt:", $0}' || true

# --- Optional: migrate to BibTeX (references.bib) -----------------------------
# To switch from the hardcoded thebibliography to the .bib:
#   1) delete the thebibliography block in $MAIN.tex
#   2) add before \end{document}:
#         \bibliographystyle{elsarticle-num}
#         \bibliography{references}
#   3) (optional) keep all 63 refs even though only 53 are cited in-text:
#         \nocite{alhajj2021,basudan2023,beir1999,beirutpm2023,grosche2011,
#                 iom2005,ksacrc,madinah2024,puma2023,whittemore1983}
#   4) build:  pdflatex; bibtex $MAIN; pdflatex; pdflatex
