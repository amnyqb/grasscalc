# `methodology/` — standard-methods cross-walk (additive, non-destructive)

This directory anchors the manuscript's approach to **established, proven
methodologies** and identifies the few adjustments needed. **It modifies no
existing files** — `../manuscript/`, `../data/`, `../analysis/` are untouched. The
manuscript's evidence grades, causal-language levels, crude-rate characterization,
and scientific content are unchanged; everything here is interpretive/additive.

## Read in this order
1. **`methodology_crosswalk.md`** — every analysis step → its standard method +
   reporting guideline, and the three adjustments (name SWiM; cross-walk A–F;
   relabel the §5 design honestly).
2. **`grade_crosswalk.csv` / `.json`** — A–F ↔ GRADE / Navigation Guide / OHAT /
   ROBINS-E / Bradford Hill (A–F labels preserved).
3. **`iarc_agent_classification.csv`** — agent-level IARC groups (9/12 are Group 1
   — context for the "Established" claim level).
4. **`proposed_manuscript_edits.md`** — suggested §2.1/§2.6/§5 wording, **as
   proposals, not applied**.
5. **`methods_references.bib`** — citations for every standard named (UNVERIFIED —
   confirm before use; no Crossref/PubMed in the build environment).

## The headline
Nothing here requires inventing a methodology. The approach already maps to
PRISMA-ScR + SWiM (synthesis), GRADE/Navigation Guide/OHAT + ROBINS-E (grading),
Bradford Hill/IARC (causal interpretation), and — for the confirmatory study —
panel fixed-effects Poisson/NB + joinpoint + age-period-cohort + spatial scan,
framed as target-trial emulation and reported per STROBE. The one substantive
correction: the §5 design is **not** a textbook interrupted-time-series/DiD
(no pre-1991 baseline), so those labels should be dropped in favour of the
controlled panel design above.
