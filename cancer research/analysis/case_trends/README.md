# Case-trend panels — cases/year by cancer type, per country

Produces the figure you asked for: a **horizontal panel** (one panel per country)
of **stacked bar charts** showing **incident cases per year by cancer type** — to
locate year-specific spikes. **Additive; no original file modified.**

## ⚠️ We do not have this data yet — and nothing here is fabricated
No year × cancer-type × country **case counts** exist in this package, and none
could be fetched here (SCR microdata is access-gated; SEER/Korea/Taiwan weren't
downloaded and `WebFetch` is blocked in this environment). So this directory ships
a **tool + a clearly-labelled SYNTHETIC demo**, not real findings. Drop real data
in and the same tool produces the real figure.

## Files
- `plot_cases_by_year.py` — the chart tool (matplotlib).
- `data_template.csv` — the input schema (header only; add your rows).
- `demo/synthetic_cases_DEMO.csv` — **SYNTHETIC, NOT REAL** data (seeded).
- `demo/figure_cases_by_year_DEMO.png/.pdf` — the demo render (red "SYNTHETIC" watermark; the Saudi lung "spike" in 2012–2015 is artificial, to show spike-spotting).

## Input schema (long format)
```
country,year,cancer_type,cases
Saudi Arabia (SCR),2015,Lung,123
Saudi Arabia (SCR),2015,Breast,210
USA-Louisiana (SEER),2015,Lung,1450
...
```
- `cases` = **integer count of incident cases** (not a rate).
- `cancer_type` = a **harmonized** category (see below).

## Run
```
python3 plot_cases_by_year.py --input your_data.csv --out figure_cases_by_year
python3 plot_cases_by_year.py --demo          # synthetic demo (watermarked)
```

## Where to get the real data (see ../raw_data_sources.* and ../../comparators/)
- **USA — SEER** (openly downloadable; Louisiana registry): incident counts by year × site × registry. Easiest real input.
- **CI5 / GBD** for harmonized national series (CI5 = registry counts/rates; GBD = modeled).
- **Saudi — SCR** annual reports (aggregate) or microdata (ethics-gated).
- **Taiwan TCR / Korea KCCR** (secure-environment application).

## Harmonization — required before any cross-panel reading (your rule)
- Keep each country a **separate panel** (the tool does this). Do **not** merge.
- Map `cancer_type` to **ICD-O-3 groups** with the **same case definition**
  (invasive-only?) and **same multiple-primary rule** across countries — otherwise
  the stacks aren't comparable. The tool does **not** standardize for you.

## Interpreting spikes — a spike is a LEAD, not a cause
This chart shows **raw counts**, which rise with **population growth** and
**registry maturation** regardless of risk. A visible "spike" can also be
screening rollout, a coding/classification change, or improved ascertainment.
So:
- For risk (not volume), switch to **age-standardized rates** with denominators.
- Treat any spike as **hypothesis-locating only** — confirm with the pre-specified
  design (latency timing, negative/positive controls, smoking adjustment) before
  attributing it. Claim ceiling stays **Compatible**.
