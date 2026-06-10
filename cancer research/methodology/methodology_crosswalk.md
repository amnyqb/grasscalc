# Methodology cross-walk — mapping the analysis to standard, proven methods

**Purpose.** Confirm that the manuscript's approach uses established methodologies
(not invented ones), name the standard for each step, and identify the few places
to adjust. **This directory is additive — it does not modify any original file**
(`../manuscript/`, `../data/`, `../analysis/` are untouched). Method citations are
in `methods_references.bib` and are **UNVERIFIED** (no Crossref/PubMed in the
build environment) — confirm at write-up.

## Summary: nothing here needs a new method

| Analysis step | Established methodology | Reporting guideline | Status |
|---|---|---|---|
| Scoping/evidence-map | Arksey & O'Malley · Levac · JBI | **PRISMA-ScR** | ✅ already used |
| Synthesis without pooling ("metric separation") | **SWiM** (Synthesis Without Meta-analysis); effect-direction / harvest plots | SWiM (Campbell 2020) | 🔧 name it SWiM |
| Evidence grading (A–F) | **GRADE** · **Navigation Guide** · **OHAT/NTP** | — | 🔧 cross-walk (labels kept) |
| Risk of bias (exposure studies) | **ROBINS-E** | — | ➕ add |
| Causal interpretation | **Bradford Hill** considerations · **IARC** (agent-level) | — | 🔧 anchor wording |
| Cross-cohort benchmark (Fig 3) | Effect-direction plot under SWiM | SWiM | ✅ already (rename) |
| Temporal registry trends | **Joinpoint regression** (SEER standard) · **age-period-cohort** | STROBE | ➕ standard tools |
| Spatial clusters | **Spatial scan statistic (SaTScan/Kulldorff)** · Moran's I | — | ✅/➕ |
| Confirmatory §5 design | Panel **fixed-effects Poisson/negative-binomial**; **target-trial emulation** framing | STROBE | 🔧 relabel (see below) |
| Breast-cancer exclusion (lead-time/overdiagnosis) | Standard screening-bias correction | — | ✅ already |

Legend: ✅ already standard · ➕ add a standard tool · 🔧 reframe/cite to an existing standard.

## The three adjustments

**1. Name the synthesis SWiM.** "Metric separation" is the author's framing of a
standard principle: incommensurable effect measures must not be statistically
pooled. That is exactly the remit of the **SWiM** reporting guideline and the
Cochrane guidance on *when not to meta-analyse*. Citing SWiM converts "metric
separation" from an apparently novel rule into a recognized standard — which
*strengthens* it. Fig 3 is, in standard terms, an **effect-direction plot**.

**2. Cross-walk the A–F grades (labels preserved).** Per your instruction the A–F
scheme is retained; `grade_crosswalk.csv`/`.json` map each grade to **GRADE**
certainty, **Navigation Guide** strength-of-evidence, **OHAT** confidence/hazard,
expected **ROBINS-E** risk-of-bias, and the **Bradford Hill** considerations it
typically satisfies. D and E remain *outside* the certainty ladder — consistent
with all frameworks (policy and risk-assessment outputs are not hazard-ID effect
estimates). `iarc_agent_classification.csv` adds the **agent-level IARC** groups:
**9 of 12 agents are IARC Group 1**, which independently supports the
"Established" claim level for radiation and solvents.

**3. Relabel the confirmatory design honestly.** A classical **interrupted time
series** or **difference-in-differences / event-study** *requires a pre-exposure
baseline*. The SCR begins in 1994, after the 1991 event — so those labels would
overclaim a standard the data can't meet. What legitimately applies:
- **Panel fixed-effects Poisson / negative-binomial regression** with population
  offset, region + year fixed effects, cross-region controls, and latency-indexed
  event-time terms (the design exploits cross-region variation + latency timing,
  not a clean pre/post contrast);
- **Joinpoint regression** and **age-period-cohort** models for temporal structure;
- **Spatial scan statistic** for clustering;
- framed as a **target-trial emulation** (Hernán & Robins) to discipline the
  causal question, and reported per **STROBE**.

The "long-horizon / bird's-eye benchmark" idea is, in standard terms, **descriptive
comparison under SWiM** (event-time–aligned effect-direction display) — not a new
method. The recovery/decay question = the calendar-time behaviour of the
event-time coefficients in the panel model above.

## What stays unchanged
Evidence grades (A–F labels), causal-language levels, the crude-rate
characterization, and all scientific content. This cross-walk is interpretive and
additive only.

## Files in this directory
- `grade_crosswalk.csv` / `.json` — A–F ↔ GRADE / Navigation Guide / OHAT / ROBINS-E / Bradford Hill
- `iarc_agent_classification.csv` — agent-level IARC groups (context for "Established")
- `proposed_manuscript_edits.md` — suggested §2.1/§2.6/§5 wording, **as proposals (not applied)**
- `methods_references.bib` — citations for every standard named above (UNVERIFIED)
