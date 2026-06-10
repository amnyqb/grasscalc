# SCR data-access check + accessible-data analysis

**Date:** 6 June 2026. **This directory is additive — no original file was modified.**

## 1. Can we access Saudi Cancer Registry data? — checked the web

| Target | Result |
|---|---|
| SCR microdata gateway (Saudi Health Council, `shc.gov.sa`) | **Not accessible.** Returns HTTP 403 to automated access; and for a human it is a **request-and-approval** process — formal research application + confidentiality undertaking, no open download / self-serve data-use agreement, and the access process is documented as non-streamlined. |
| SCR annual-report PDF (aggregate) `shc.gov.sa/.../Cancer Incidence Report 2020.pdf` | Published, but **WebFetch returned 403** (host blocks the fetcher). |
| Open-access papers (PMC / Springer / BMC) | Exist and are open, but **WebFetch returned 403 on every host**. Only `WebSearch` snippets came through. |

**Conclusion:** case-level **SCR microdata is not accessible** (gated, by design). And in *this* environment even aggregate tables can't be reliably scraped — `WebFetch` is blocked across hosts; `WebSearch` returns only snippets, which are not a sound basis for a dataset. Web search did **corroborate** the in-package facts (Eastern Province lung 3.36/100,000 is the highest region; EP breast ASR 46.2 highest), confirming they're real and published.

So, per the instruction: *then not.* We proceed with the **published aggregate data already in the package** — which is the accessible data — at the **"Compatible"** claim ceiling.

## 2. What the accessible data supports (the honest ceiling)
The package's accessible aggregate data supports a **descriptive / ecological** analysis only — the "minimal publishable version" the manuscript already specifies (§5). It does **not** support causal attribution, which needs the microdata.

The one defensible quantitative step, executed in `ecological_residual.py`:

> The observed EP:Jazan crude lung-cancer contrast is **5.69×** (3.36 vs 0.59 /100,000, **crude**, not ASR). Crediting even a **large** regional smoking gap (30% vs 8%) at the most smoking-favourable RR=20, smoking explains at most **~2.7×**, leaving a **~2.1× residual** unexplained by smoking. Under a realistic gap the residual is **~3.4×**.

**What this means — and does not.** It means a smoking-*only* explanation is implausible. It does **not** mean 1991-plume causation: the residual is still confounded by **age structure** (the rates are crude), screening/diagnostic intensity, healthcare access, urbanization, petrochemical-occupation, migration, and registry completeness. Separating those is precisely what the (inaccessible) SCR microdata analysis would do.

**Defensible statement (Compatible level):** *the Eastern-Province lung contrast is unlikely to be a smoking-only artefact and is compatible with a sustained environmental-exposure hypothesis; testing it requires the pre-specified region-by-year microdata analysis.*

## Files
- `ecological_residual.py` — reproducible computation (stdlib only; uses only in-package published values)
- `ecological_residual_output.csv` — its output
- this note
