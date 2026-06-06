# Proposed manuscript edits — PROPOSALS ONLY (not applied)

These are **suggested** wording changes to anchor the manuscript to standard
methodologies. **Nothing here has been applied** — `../manuscript/` is untouched.
They cite standards only; they do **not** change evidence grades, causal-language
levels, the crude-rate characterization, or any scientific content. Citations
refer to `methods_references.bib` (UNVERIFIED — confirm before use).

---

## §2.1 — Approach and registration  (add one sentence)

> Add after the PRISMA-ScR sentence:
> *"The synthesis is conducted and reported following the Synthesis Without
> Meta-analysis (SWiM) guideline \citep{swim2020}, as the heterogeneity of effect
> measures precludes meta-analytic pooling."*

## §2.6 — Evidence grading and synthesis rules

**Rule 1 (grading) — add:**
> *"Risk of bias in the contributing exposure studies is appraised with ROBINS-E
> \citep{robinse2023}. The A–F scheme used here is retained for readability and is
> cross-walked to standard frameworks — GRADE certainty \citep{grade2008}, the
> Navigation Guide strength-of-evidence \citep{navguide2014}, and the OHAT
> approach \citep{ohat2014} — in Supplementary Table~Sx (see
> methodology/grade_crosswalk.csv). Agent-level carcinogenicity follows the IARC
> Monographs classification \citep{iarc_preamble}."*

**Rule 2 (metric separation) — add:**
> *"This metric-separation rule operationalizes the standard principle that
> incommensurable effect measures should not be statistically pooled; the
> qualitative synthesis therefore follows SWiM \citep{swim2020} and is displayed
> as an effect-direction plot (Figure~\ref{fig:benchmark}) \citep{effectdirection2013,harvest2008}."*

**Rule 3 (causal language) — add:**
> *"The four claim levels are applied in light of the Bradford Hill considerations
> \citep{hill1965}."*

## §5 — Proposed confirmatory study  (relabel the design; this is the key fix)

> Replace the implication that the design is an event-study/DiD with:
> *"Because the registry begins in 1994 — after the 1991 event — a classical
> interrupted time series or difference-in-differences analysis, both of which
> require a pre-exposure baseline, is not estimable. The design is therefore a
> controlled panel fixed-effects analysis: negative-binomial (or Poisson)
> regression with a population offset, region and calendar-year fixed effects,
> cross-region control series, and latency-indexed event-time terms relative to
> 1991. It is framed as a target-trial emulation \citep{tte2016} to make the
> estimand and its assumptions explicit. Temporal structure is examined with
> joinpoint regression \citep{joinpoint2000} and age-period-cohort models
> \citep{apc2014}; spatial clustering with the spatial scan statistic
> \citep{scan1997}. The study is reported following STROBE \citep{strobe2007}."*

> Optional (recovery/decay): *"The calendar-time profile of the event-time
> coefficients is used to distinguish a decaying acute-plume signal from a
> sustained chronic-petrochemical baseline."*

---

## If you later choose full GRADE adoption instead of the cross-walk
That would relabel A–F to GRADE certainty levels (High/Moderate/Low/Very low) and
is more defensible to methods reviewers, but it **changes your grade labels** —
which is why the cross-walk (labels preserved) is recommended here. Say the word
and I'll prepare that variant in this directory too.
