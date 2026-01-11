# Makefile for grasscalc paper
#
# Usage:
#   make          - Build the PDF
#   make pdf      - Build the PDF
#   make experiments - Run experiments and generate tables
#   make clean    - Remove build artifacts
#   make all      - Run experiments and build PDF

PAPER = grasscalc_paper
LATEX = pdflatex
BIBTEX = bibtex

.PHONY: all pdf experiments clean

all: experiments pdf

pdf: $(PAPER).pdf

$(PAPER).pdf: $(PAPER).tex
	$(LATEX) $(PAPER)
	$(LATEX) $(PAPER)
	@echo "PDF generated: $(PAPER).pdf"

experiments:
	@echo "Running experiments..."
	cd experiments && python run_experiments.py --output ../results
	@echo "Experiments complete. Results in results/"

clean:
	rm -f $(PAPER).aux $(PAPER).log $(PAPER).out $(PAPER).toc
	rm -f $(PAPER).bbl $(PAPER).blg $(PAPER).pdf
	rm -rf results/
	@echo "Cleaned build artifacts"

# Quick experiments for testing
quick-experiments:
	cd experiments && python run_experiments.py --quick --output ../results

# Watch for changes and rebuild (requires entr)
watch:
	ls $(PAPER).tex | entr -c make pdf
