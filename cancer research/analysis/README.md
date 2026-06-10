# `analysis/` — consolidated data for further analysis

A merged, machine-readable view of the data charted in the manuscript, built for
downstream analysis. See `data_dictionary.md` for every file and column.

## Files
- `sources_master.csv` — reference corpus + identifiers + exposure/grade + charted flag (63 rows)
- `claims_long.csv` — every headline claim exploded by source, joined to metadata (29 rows)
- `evidence_matrix.csv` — Table 2 (13 comparator populations)
- `extraction_table.csv` — Table S1 / charting sheet (13 sources)
- `smoking_sensitivity_output.csv` — Table 3 (4 scenarios)
- `dataset.json` — all of the above in one nested object
- `data_dictionary.md` — schema + provenance
- `VALIDATION.md` — offline source-integrity report (see also `../REPORT.md`)
- `raw_data_sources.csv` / `.json` — **upstream raw-data acquisition register**: where each cohort's primary data lives, custodian, access route, locator (20 clusters)
- `raw_data_acquisition.md` — guide/action plan for obtaining the upstream raw datasets (what's OPEN vs application/ethics/restricted)

## Quick start (pandas)
```python
import pandas as pd, json
sources = pd.read_csv("sources_master.csv")
claims  = pd.read_csv("claims_long.csv")
# claims with verified-or-best-effort identifiers, by metric family:
claims.groupby("metric_type").size()
# join a claim to its full source record:
claims.merge(sources, left_on="source_cite_key", right_on="cite_key", how="left")
```

## Provenance & caveats
- **No new primary data.** Values are extracted from published sources.
- The Saudi lung anchor (3.36 vs 0.59 / 100,000; ≈5.7×) is a **crude** regional
  incidence rate, **not** age-standardized.
- **Metric separation:** do not pool/compare values across different `metric_type`
  families (ERR per dose vs incidence/mortality ratios vs modeled risk vs
  crude-rate ratios vs policy lists).
- **Identifiers are not machine-verified** — confirm `UNVERIFIED`/`NEEDS_LOOKUP`/
  `FLAG_AUTHOR` rows before relying on DOIs/PMIDs.
- Saudi Cancer Registry microdata are **not** included (input to the proposed study).
