# Pre-registered protocol — registered search + confirmatory SCR analysis

**Study:** Non-Tobacco Environmental Carcinogenesis in Exposed Populations —
evidence map and a Saudi Eastern Province registry-analysis protocol.
**Author:** Amin Al Yaquob, Al Yaquob Advisory, Riyadh, Saudi Arabia (ORCID
0009-0006-1590-3378).
**Status:** Protocol locked prior to execution. PROSPERO does not register
scoping reviews; this protocol is to be deposited on OSF prior to running the
four-database search. *(OSF project URL: to be inserted on creation — also
insert into manuscript Methods §2.1 and the Data Availability statement.)*

This document assembles the protocol elements from the manuscript: the
registration/approach (§2.1), the locked scope (§2.7), the confirmatory study
specification (§5), and the search translations and PRISMA-ScR mapping
(Appendices A–B). The full search strings are in `search_strategy.md`.

---

## Part 1 — Evidence-map protocol (registered, not yet executed)

**Framework.** Arksey & O'Malley five-stage scoping framework, refined by Levac
et al. and JBI guidance; reported against the applicable PRISMA-ScR checklist
items (mapping in Part 3).

**Eligibility.**
- *Inclusion* — a source is eligible if it meets all three: (i) a study
  population exposed to one of seven target categories (ionizing radiation;
  wartime combustion products; wartime chemical agents; industrial solvents /
  military-associated contaminants; acute industrial chemical release; civilian
  conflict-associated exposure; chronic petrochemical / industrial pollution),
  with exposure established by direct measurement, modeled plume/dose
  reconstruction, residence/employment in a defined contaminated setting, a
  registry-defined exposure area, validated biomarker evidence, or official
  technical documentation; (ii) a reported cancer outcome (incidence, mortality,
  SIR/SMR, ERR per unit dose, validated carcinogen-exposure biomarker, or modeled
  cancer-risk estimate); and (iii) sufficient latency for the relevant tumour
  type, or explicit acknowledgement of immature latency.
- *Exclusion* — non-cancer outcomes only; exposure not meeting any operational
  criterion; non-systematic opinion without primary/secondary data; or
  duplication of a more complete analysis of the same cohort.
- *Limits* — inception to 6 June 2026. English for the database search; Arabic
  Saudi MoH/SCR sources hand-searched to mitigate language bias.

**Information sources.** MEDLINE (PubMed), Embase, Scopus, Web of Science Core
Collection. Grey literature: ATSDR; National Academies / IOM (*Gulf War and
Health*; *Veterans and Agent Orange*); UNSCEAR; IARC; Radiation Effects Research
Foundation; U.S. VA; U.S. GAO; Saudi Cancer Registry reports. Backward citation
searching of included sources.

**Selection & charting (registered step).** Formal four-database search →
de-duplication → dual independent screening of titles/abstracts and full texts
with adjudication → recorded full-text exclusion reasons → fully populated
selection flow (planned format: Supplementary Figure S1). Charting form captures
per source: exposure category; population/setting; design; exposure
ascertainment; outcome ascertainment; effect metric and value; latency adequacy;
smoking-control capacity; assigned evidence grade. (See `data/extraction_table.csv`.)

**Synthesis rules (the methodological core).**
1. *Evidence grade* — A–C and F carry internal-validity weight; D (legal/policy
   presumption) and E (modeled environmental cancer-risk estimates) are held
   *outside* the validity ladder as contextual evidence, never compared as if
   effect estimates.
2. *Metric separation* — observed incidence/mortality ratios, ERR/Sv·ERR/Gy,
   modeled lifetime air-toxics risk, policy-presumptive lists, and ecological
   crude- or age-standardized rate ratios are discussed qualitatively but never
   pooled or numerically compared.
3. *Causal-language discipline* — four claim levels: Established, Associated,
   Compatible, Hypothesis-generating.

**Scope of the current article (§2.7).** The article locks the protocol,
eligibility, full search strategy, charting form, and synthesis rules and
presents a graded map of curated primary sources. It does **not** present a
completed four-database PRISMA-ScR search; exact screened/assessed/included
counts and the populated selection flow are the registered next step.

---

## Part 2 — Confirmatory study: Saudi Cancer Registry microdata analysis (§5)

**Design.** Because the registry begins in 1994 — after the 1991 Kuwait oil-fire
event — a classical difference-in-differences with a pre-event parallel-trends
test is **not** available. The design is a **latency-stratified regional
event-study**: a region-by-year panel of incidence with calendar-year and region
fixed effects and latency-aware event-time coefficients indexed to 1991,
estimating divergence of the Eastern Province from other regions across plausible
latency windows rather than a clean pre/post contrast.

**Estimand.** Excess post-latency incidence rate in the Eastern Province relative
to other Saudi regions, net of national secular trends, age, sex, site, and
region-specific baseline differences.

**Exposure.** Primary: Eastern-Province residence during the post-1991 latency
window. Stronger: an exposure gradient from 1991 plume-intensity estimates,
distance from petrochemical facilities, and residence history (this gradient also
supports separating acute-plume from chronic-petrochemical signal). Where 1991
residence is unavailable, current residence is interpreted cautiously (migration
dilution).

**Primary outcomes (pre-specified).** Lung (with explicit smoking control),
oesophageal, brain/CNS, leukaemia, non-Hodgkin lymphoma, kidney, bladder, and
pediatric cancers. **Secondary:** colorectal. **Analysed separately as
detection-sensitive (never primary):** female breast, thyroid, prostate.

**Model.** Negative-binomial or Poisson regression with population offset,
stratified by age, sex, site, region, calendar year; region and year fixed
effects; an Eastern-Province × post-latency interaction; event-time coefficients
testing divergence in plausible windows (5–10 yr haematologic; 15–30 yr solid
tumours).

**Controls & sensitivity.** Negative controls: cancers not expected to respond to
combustion exposure, and screening-dominated sites. Positive controls: lung and
(if exposure sufficient) haematologic malignancies. Sensitivity over smoking and
passive-smoking prevalence, petrochemical employment, urbanization, SES,
healthcare access, registry completeness, nationality, migration,
age-standardization method, stage, histology, and regional screening intensity. A
never-smoker lung-cancer subcohort (if oncology-record smoking status is
available) would block the smoking path directly.

**Minimal publishable version.** Even without individual smoking data, an honest
ecological analysis using region-year-age-sex-site counts and denominators, with
pre-specified non-breast primary outcomes and event-study models, is feasible —
presented at the "Compatible" claim level.

**Claim ceiling.** "Compatible" until estimated; "Associated/Established" only if
effects survive controls.

**Ethics.** Ethics approval and secure data-use agreement required before
accessing SCR microdata.

---

## Part 3 — Reporting against PRISMA-ScR (Appendix B)

| PRISMA-ScR item | Status / location |
|---|---|
| Title; structured abstract | Completed |
| Rationale; objectives | Section 1 |
| Protocol & registration | Section 2.1 (OSF, pre-execution) |
| Eligibility criteria | Section 2.2 |
| Information sources | Section 2.3 |
| Search (full strategy) | Section 2.4, Appendix A (`search_strategy.md`) |
| Selection of sources | Registered protocol (Part 2); planned flow Suppl. Fig. S1 |
| Data charting; data items | Section 2.5; Suppl. Table S1 (`data/extraction_table.csv`) |
| Critical appraisal (grading) | Section 2.6 |
| Synthesis of results | Sections 2.6, 3 |
| Results: selection (counts/flow) | Pending registered execution (Section 2.7) |
| Results: characteristics | Section 3.2; Suppl. Table S1 |
| Results: synthesis | Sections 3.3–3.9 |
| Summary; limitations; conclusions | Sections 4.1, 4.4, 6 |
| Funding | Declarations |

---

## Open protocol items requiring the author
1. Insert the OSF project URL (here, in manuscript §2.1, and in Data Availability).
2. The four-database search (Embase/Scopus/WoS beyond the PubMed string) is
   **specified but not executed**; Supplementary Figure S1 is the *planned* flow.
   Running it requires live database access.
