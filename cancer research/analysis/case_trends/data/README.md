# SCR cancer-incidence data (extracted from annual-report PDFs)

Real time series extracted from Saudi Cancer Registry (SCR) annual reports
(PDFs from shc.gov.sa). Every value is extracted from the printed tables/prose —
nothing is interpolated or modelled. Years that cannot be read cleanly are
**flagged, not guessed** (see below).

## Files

| File | What | Years | Measure |
|---|---|---|---|
| `scr_saudi_topsites_2006_2023.csv` | Most common cancers among Saudi nationals (both sexes, all ages) | 2006–2010, 2015, 2018–2023 | incident **COUNTS** |
| `scr_lung_by_sex_asr_2004_2023.csv` | Lung cancer (C33–C34) by sex: counts **and ASR** | 2004–2023 (gaps flagged) | counts **and rates** |
| `scr_lung_by_sex_2019_2023.csv` | earlier lung-by-sex counts (subset, kept for provenance) | 2019–2023 | counts |
| `scr2023_lung_intl_asr.csv` | 2023 international ASR comparison (Fig 3.7.4) | 2023 | ASR |
| `scr2023_lung_morphology.csv` | 2023 lung morphology split | 2023 | counts/% |

Charts: `scr_trend_2006_2023.*` (top-site count trend), `scr_stacked_2006_2023.*`
(stacked counts), `scr_lung_asr_trend.*` (**lung ASR by sex — the rate trend**),
`scr_lung_counts_trend.*` (lung counts by sex). Earlier 2019–2023 figures retained.

## Provenance & extraction
- **Top sites:** the "Most common cancers among Saudi nationals" table (2015, 2018–2023)
  and the older "Table 2.2 Ten Most Common Cancers among Saudis (All Ages)"
  both-sexes ranking (2006–2010). Tool: `../extract_scr_reports.py` (PyMuPDF,
  coordinate-aware). Every value printed for review.
- **Lung C33–C34 by sex + ASR:** read from TWO independent places per report and
  cross-checked — (A) the per-site×sex summary table ("Number, %, CIR/ASR, … by
  Primary Site and Sex/Gender") read by word coordinates, and (B) the Part III
  selected-site narrative ("…affected M males and F females… ASR was X for males
  and Y for females"). Tool: `../extract_lung_series.py`. Where both exist they
  **agree**; disagreements are surfaced, not hidden. **ASR = World standard, /100,000.**

## Read-with-care (important caveats)
- **2020 is a COVID artifact.** Counts and rates dip across sites in 2020, then
  rebound — pandemic disruption of diagnosis/registration, not a real fall.
- **Counts ≠ rates.** Use ASR for trends. Count drift partly reflects population
  growth + improving coverage. The top-sites file is counts only.
- **Possible ASR standardization/method change ~2021.** Lung male ASR sits at
  ~5–7 (2006–2020) then steps up to 7.5/8.8/8.5 (2021/2022/2023). This may be a
  real recent rise and/or a change in the report's standard population — described,
  **not asserted as causal**. Keep claims at the "Compatible" level.
- **No exposure data.** The registry records site, sex, age, morphology, stage —
  not smoking, occupation, or residence. It is national, not regional (does not
  isolate the Eastern Province).

## Flagged / missing years (not extracted — by design)
- **2005:** PDF not present in the local set.
- **2014, 2017:** image-only / corrupted text layer → would need OCR.
- **2013:** incidence tables are images; only the narrative ASR (5.5/1.8) is
  readable; lung counts not text-extractable.
- **2004:** lung counts OK (narrative); ASR scrambled by RTL/Arabic interleaving → omitted.
- **2015:** lung counts OK; summary-table ASR column ambiguous → ASR omitted.
- **2016:** lung ASR OK (4.4/2.0); male count cell garbled (overlapping glyphs) → count dropped.
- **2011–2012:** "Ten Most Common" table is per-sex only (no both-sexes counts) →
  excluded from the top-sites COUNT series, but lung (counts + ASR) IS captured
  from their narratives.

## Regenerate / extend
```
pip install pymupdf matplotlib
python3 ../extract_scr_reports.py  /folder/with/SCR/pdfs   # top-site counts
python3 ../extract_lung_series.py  /folder/with/SCR/pdfs   # lung counts + ASR (prints all values)
python3 ../plot_trends.py        --input scr_saudi_topsites_2006_2023.csv --out scr_trend_2006_2023 --ylabel "Incident cases (count)"
python3 ../plot_cases_by_year.py --input scr_saudi_topsites_2006_2023.csv --out scr_stacked_2006_2023
python3 ../plot_lung_asr.py       --input scr_lung_by_sex_asr_2004_2023.csv
```
