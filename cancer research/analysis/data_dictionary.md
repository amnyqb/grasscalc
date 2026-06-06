# Data dictionary — `analysis/`

Consolidated, analysis-ready view of the data charted in the manuscript. **No new
primary data**: every value is extracted from a published source. Identifiers were
**not machine-verified** in the build environment (no Crossref/PubMed) — treat
`UNVERIFIED`/`NEEDS_LOOKUP`/`FLAG_AUTHOR` rows accordingly (see `id_status`).

## `sources_master.csv` — one row per reference (n = 63)
| column | description |
|---|---|
| `cite_key` | manuscript citation key (join key everywhere) |
| `citation` | full citation as in the manuscript |
| `doi` | DOI (best-effort; see `id_status`) |
| `pmid_or_pmcid` | PubMed ID or PMCID |
| `url` | canonical URL where available |
| `id_status` | `VERIFIED` / `UNVERIFIED` / `NEEDS_LOOKUP` / `FLAG_AUTHOR` / `NO_DOI` |
| `exposure_category` | exposure setting (from the extraction table; blank if not a charted comparator) |
| `evidence_grade` | assigned grade A–F / contextual (from the extraction table) |
| `charted_in_data` | `yes` if the source feeds the matrix/extraction/key-values; else `no` (narrative/method citation) |
| `note` | identifier/verification note |

## `claims_long.csv` — one row per (headline claim × source) (n = 29)
| column | description |
|---|---|
| `claim` | the headline numeric/qualitative claim |
| `value` | reported value (native units, kept separate per the metric-separation rule) |
| `metric_type` | metric family (e.g. `ERR/Gy`, `ERR/Sv`, `mortality ratio`, `crude incidence rate`, `count`, `derived`) |
| `source_cite_key` | source (join to `sources_master.cite_key`) |
| `doi`, `pmid_or_pmcid`, `id_status` | source identifiers, joined in |
| `manuscript_location` | section/table where the claim appears |

> Metric-separation reminder: values across different `metric_type` families are
> **not** numerically comparable and must not be pooled.

## `evidence_matrix.csv` — manuscript Table 2 (n = 13 comparator populations)
`comparator_population, exposure_category, evidence_grade, best_supported_signal,
reported_metric_native_units, synthesis_role`.

## `extraction_table.csv` — Supplementary Table S1 / charting sheet (n = 13)
`source_cite_keys, setting_exposure, population_country, design,
exposure_ascertainment, outcome_ascertainment, smoking_confounder_control,
key_sites, latency, metric_result_grade`.

## `smoking_sensitivity_output.csv` — Table 3 (n = 4 scenarios)
Implied between-region lung-cancer rate ratio from current-smoking-prevalence
differences alone, under rate ∝ `p·RR + (1−p)`.
`scenario, p_high, p_low, rate_ratio_RR10, rate_ratio_RR15, rate_ratio_RR20`.
Regenerate with `../data/smoking_sensitivity.py`.

## `dataset.json` — everything above in one nested object
Top-level keys: `meta`, `references`, `key_values`, `evidence_matrix`,
`extraction_table`, `smoking_sensitivity`. Convenient for programmatic analysis
(pandas: `pd.json_normalize(json.load(open('dataset.json'))['references'])`).

## What is NOT here
- **Saudi Cancer Registry microdata (1994–present)** — the input to the *proposed*
  study (manuscript §5); obtained from the Saudi MoH under ethics approval.
- **Upstream primary datasets** of the cited cohorts (LSS dose tables, ATSDR cohort
  files, etc.) — these live with their originating institutions; this package
  charts their *published* results, not their raw records.
