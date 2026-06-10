# US case study — scope & feasibility (smoking vs industrial pollution)

**Role in the project.** The Saudi annual-report registry data is national and
carries no exposure, residence, or smoking fields, so it can support an
ecological *compatibility* signal but cannot partition smoking from pollution.
This case study runs that partition where the data *can* — the United States,
where cancer incidence, smoking, and modeled air-toxic exposure are all open at
county level — then transports the calibrated signal to the Saudi Gulf setting,
**side-by-side, never pooled** (the manuscript's metric-separation /
harmonize-then-benchmark rule).

**Research question.** Within a data-rich setting, is industrial/point-source
air-toxic exposure associated with cancer incidence **after adjustment for
smoking** and area confounders — and is the association concentrated in the
pollution-relevant sentinel sites rather than the smoking-saturated ones?

## Design
- **Type:** cross-sectional ecological association, county level (hypothesis-
  generating; ecological-fallacy caveat explicit — consistent with the parent
  manuscript's "Compatible" ceiling).
- **Unit / join key:** US county, 5-digit **FIPS** (consistent across all three
  sources — verified). n ≈ 3,143 nationally; Louisiana "Cancer Alley" /
  Gulf-coast petrochemical corridor as the focal high-exposure region.
- **Estimand:** smoking-adjusted association between industrial point-source
  air-toxic cancer risk and site-specific incidence; contrast across sentinels.

## Data sources — all verified pullable (2026-06-09)

| Layer | Source | Endpoint (tested) | Gives | Access |
|---|---|---|---|---|
| Cancer incidence | NCI/CDC **State Cancer Profiles** | `statecancerprofiles.cancer.gov/incidencerates/…&output=1` (CSV) | county age-adjusted incidence by site/sex/race, CI, trend, RUCC urbanicity | open, no DUA |
| Industrial pollution | EPA **AirToxScreen 2020** | `…/national_cancerrisk_by_county_srcgrp.xlsx` | per-county total + **PT-StationaryPoint** (industrial) modeled cancer risk, by source group/pollutant | open |
| Smoking | CDC **PLACES** | `data.cdc.gov/resource/swc5-untb.csv?measureid=CSMOKING` (Socrata) | county current-smoking prevalence (+ tract level available) | open |
| (sensitivity) facility emissions | EPA **TRI** | Envirofacts / TRI basic files | facility-level emissions for proximity/gradient checks | open |

## Sentinel-cancer panel (SCP `cancer=` codes — verified returning data)
Chosen so pollution signal can be separated from smoking by *contrast*:

| Site | SCP code | Smoking link | Pollution link |
|---|---|---|---|
| Lung & bronchus | 047 | **strong** | PAHs/PM (confounded — weak sentinel) |
| Urinary bladder | 071 | moderate | aromatic amines, PAHs |
| Kidney | 072 | weak | solvents (TCE), metals |
| Non-Hodgkin lymphoma | 058 | weak | benzene, solvents, dioxins |
| Leukaemia | 090 | weak | **benzene** (oil-fire/industrial) |
| Liver | 035 | weak | vinyl chloride, solvents |
| Melanoma (neg. control) | 053 | none | none (UV) — falsification check |

Brain/CNS code to be re-confirmed (070 returned empty). Mesothelioma is not a
standard SCP site — handle via USCS/SEER if needed (it is the cleanest asbestos
sentinel and matches the Saudi mesothelioma signal).

## Model
For each sentinel site *s*:

```
incidence_s ~ industrial_risk + smoking_prev + poverty + urbanicity(RUCC)
              + %race + (population weight)
```

Report the **smoking-adjusted** industrial-pollution coefficient per site.
Expectation that would support the thesis: the pollution term is **near-null for
smoking-saturated lung** but **positive for benzene/solvent sentinels (leukaemia,
NHL, bladder, kidney)**, and **null for the melanoma negative control**.

## Proof-of-concept (Louisiana, 64/64 parishes merged) — and why it matters
Crude parish correlations:

| pair | r |
|---|---|
| lung incidence ↔ smoking % | **+0.43** |
| lung incidence ↔ industrial risk | **−0.24** |
| smoking % ↔ industrial risk | **−0.39** |

The petrochemical-corridor parishes (St. John the Baptist, Ascension, St.
Charles) have the **highest industrial risk but *lower* smoking**, and lung
incidence peaks in rural high-smoking parishes. So the *naive* pollution–lung
correlation is negative — **entirely a smoking-confounding artifact**. This
confirms (a) the pipeline assembles end-to-end, and (b) the smoking-adjusted,
multi-sentinel design is *necessary*, not decorative: the signal must be sought
in the less smoking-confounded sites with smoking held constant.

## Transport to Saudi Arabia
Run the identical sentinel framework on the Saudi national series (already built:
`analysis/case_trends/scr_all_sites_long.csv`) as a **separate** panel; compare
the *shape* of the sentinel signature (which sites elevated, smoking-adjusted in
the US; which sites elevated in low-smoking Saudi) — never a pooled estimate.
The US calibrates "what a smoking-stripped pollution signature looks like"; Saudi
is read against it.

## Limitations (state up front)
Ecological (modifiable areal unit + ecological fallacy); modeled — not measured —
exposure; cross-sectional with no latency lag; smoking is an area prevalence, not
individual; AirToxScreen 2020 is a single snapshot. Conclusions are
hypothesis-generating associations, not causal attribution.

## Status
All four data pulls verified working 2026-06-09 (`pull_data.py` reproduces the
Louisiana merge). Ready to scale to the national county panel on approval.
