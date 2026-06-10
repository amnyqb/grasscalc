# Cross-country meta-analysis — when it's applicable, and how (future option)

A documented, **conditional** plan for combining the Saudi result with comparator
countries (Taiwan, Korea, US-Louisiana, Gulf) *later*. **This commits to nothing**
and is additive — no original file is modified. It encodes the rule we agreed on:
**keep each country separate; harmonize-then-benchmark; pool only if applicable.**

## Decision rule (read first)

```
Do all comparator results come from the SAME harmonized protocol?
  ├─ NO  → STOP. Structured side-by-side comparison only (SWiM/effect-direction).
  │        Never report a pooled summary estimate. (Default state today.)
  └─ YES → Are the estimand, outcome def, standard population, exposure metric,
           and design the same, WITH quantified uncertainty (CI/SE)?
           ├─ NO  → STOP. Narrative comparison only.
           └─ YES → Is between-site heterogeneity assessable and not extreme?
                    ├─ NO  → Report sites separately; do not pool.
                    └─ YES → Random-effects meta-analysis of the HARMONIZED
                             site-specific estimates is applicable. Pre-specify it.
```

## Applicability checklist (all must be ✓ before any pooling)
- [ ] **Same estimand** — e.g., adjusted incidence-rate ratio per defined exposure-gradient unit (not "an effect," but the *same* effect).
- [ ] **Same outcome definition** — ICD-O-3 site/morphology, invasive-vs-in-situ rule, multiple-primary rule fixed identically.
- [ ] **Same standard population** for any rate (World/Segi, or all via CI5) — never mix US-2000 / Korea-2000 / World.
- [ ] **Registry incidence**, not claims-defined cases, in every site.
- [ ] **Same design** — the pre-specified panel fixed-effects / latency model run identically.
- [ ] **Same exposure metric** — proximity/gradient defined comparably (or explicitly flagged as not comparable).
- [ ] **Uncertainty quantified** per site (CI or SE).
- [ ] **Heterogeneity assessable** (≥ a few sites; I², τ² interpretable).
- [ ] **Pre-registered** meta-analytic plan (model, heterogeneity handling, sensitivity) — decided *before* seeing pooled results.

If any box is unchecked → **structured comparison only**, reported side-by-side,
no pooled number.

## The design that fits: federated → pool the estimates (not the data)
This respects data-separation and the gated/secure-environment reality of every
registry involved (SCR ethics; Korea K-CURE; Taiwan HWDC on-site; SEER DUA).

1. **One common protocol + shared analysis code.** Fix definitions, standard
   population, model, covariates, negative/positive controls.
2. **Run locally in each jurisdiction.** Raw records **never leave** the country.
   Each site outputs only the **harmonized estimate + CI** (and aggregate
   diagnostics).
3. **Pool the site-level estimates** with a **random-effects** model; report
   **I² / τ²** and a forest plot of the *harmonized* estimates.
4. **Sensitivity:** leave-one-out, fixed- vs random-effects, exclusion of
   higher-risk-of-bias sites, alternative standard population.

This is a standard, proven approach — individual-participant / distributed
network meta-analysis and prospective meta-analysis (the model used by pooled
registry consortia). Reporting follows **PRISMA-IPD** (for the meta-analysis) and
**STROBE** (for each site's analysis); synthesis that *doesn't* qualify for
pooling is reported under **SWiM**.

## Hard cautions
- **Meta-analysis raises precision and generalizability, not internal validity.**
  If all sites share the same confounding (e.g., ecological / age-structure bias),
  pooling yields a *precisely* biased estimate. Per-site design quality (negative
  controls, age-standardization, smoking adjustment) matters more than pooling.
- **Each country stays an independent replication**, not added sample size in a
  single merged table. No raw-data concatenation across registries — ever.
- **Claim ceiling unchanged.** Pooling does not by itself lift the claim level;
  the Saudi node remains "Compatible" until its own design survives its controls.
- A consistent signal *across* harmonized sites is **corroboration by
  replication** — valuable — but it is replication, not pooled causation.

## Status
**Future option, not active.** Today the only defensible cross-country product is
the harmonized **side-by-side comparison** (see `comparator_countries.md` and
`registry_field_crosswalk.csv`). Formal pooling is unlocked only when the
checklist above is satisfied via the federated design.
