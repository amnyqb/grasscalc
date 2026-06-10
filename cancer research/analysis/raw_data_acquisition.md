# Upstream raw-data acquisition guide

**Goal:** obtain the *primary/raw* data underlying the cohorts and sources the
manuscript charts (the article itself reports only *published results*).

**Status: not fetched here.** Every data host needed (EPA, RERF, CDC/ATSDR, WHO,
Zenodo, Dryad, OSF, DataCite) returns `HTTP 403 — Host not in allowlist`; this
build environment can only reach PyPI. The register below (`raw_data_sources.csv`
/ `.json`) is therefore an **acquisition plan**, not the data. Locators were
recalled offline and are flagged `locator_confidence` — **confirm each before
relying on it.** Nothing was invented: where a precise link wasn't reliably
known, the custodian/portal is named instead of a guessed URL.

## How the 20 clusters break down by access route
| route | count | meaning | clusters |
|---|---|---|---|
| **OPEN** | 7 | publicly downloadable now | fallujah, beirut, cancer_alley, saudi_spatial, screening_trials, survival_benchmarks, mutation_etiology |
| **APPLICATION** | 5 | data-use agreement / research request | lss_rerf, camp_lejeune_atsdr, agent_orange, burn_pits, gats_saudi |
| **ETHICS** | 2 | ethics approval + DUA (registry microdata) | saudi_scr, kuwait |
| **RESTRICTED** | 6 | study-team/consortium only | semipalatinsk, gulfwar_us, gulfwar_uk, bhopal, saudi_plume, uranium_miners |

## Recommended order of work

**1 — Grab the OPEN data first (no gatekeeping).** In a network-enabled
environment, pull:
- **cancer_alley** — EPA AirToxScreen (ex-NATA) census-tract cancer-risk surfaces,
  EPA ECHO facility data, EJScreen; plus the Robinson 2025 *PNAS* supplement
  (measured VOC concentrations). *Highest-value open dataset here.*
- **saudi_spatial** (Al-Ahmadi 2013), **fallujah** (Busby 2010 + supplement),
  **survival_benchmarks** (CONCORD-3 appendices), **screening_trials**
  (Duffy/Gøtzsche/Paci), **mutation_etiology** (Tomasetti/Wu supplements),
  **beirut** — all in the open-access papers / supplements.

**2 — Start the APPLICATION clocks early (they take weeks–months).**
- **lss_rerf** → RERF research agreement for individual LSS + DS02R1 dosimetry
  (aggregate dose-response may be downloadable immediately).
- **camp_lejeune_atsdr** → ATSDR data request / FOIA for the cohort analytic files
  and water-distribution model outputs.
- **agent_orange** → NAS Medical Follow-up Agency for the Air Force Health Study
  (Ranch Hand) repository.
- **burn_pits** → VA Airborne Hazards & Open Burn Pit Registry research request.
- **gats_saudi** → WHO/CDC GTSS for GATS-2019 respondent-level microdata (the
  country report is already public).

**3 — The project's own key input is ETHICS-gated.**
- **saudi_scr** — Saudi Cancer Registry case-level microdata
  (region-year-age-sex-site-morphology-stage) is the input to the proposed
  event-study (§5). Aggregate annual reports are public; microdata require **Saudi
  MoH ethics approval + a data-use agreement**. Begin this in parallel — it is the
  long pole for the confirmatory analysis.
- **kuwait** — KCCC registry (ethics); the Cange 2013 thesis is openly available.

**4 — RESTRICTED clusters: contact custodians / plan collaborations.**
semipalatinsk, gulfwar_us (VA microdata; the GAO plume report is open),
gulfwar_uk (LSHTM/King's), bhopal (Sambhavna Trust/ICMR), saudi_plume (values are
in the 1994 paper), uranium_miners (PUMA consortium; BEIR VI report is public).

## Deliverables in `analysis/`
- `raw_data_sources.csv` — the register (20 clusters × 11 fields, linked to cite_keys)
- `raw_data_sources.json` — same, with an access-route legend in `meta`
- this guide

> When you next run this in an environment with an appropriate network allowlist
> (or locally), the OPEN cluster can be downloaded straight away; the
> APPLICATION/ETHICS/RESTRICTED clusters are process-gated regardless of tooling.
