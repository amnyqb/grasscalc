# SCR cancer-incidence data (extracted from annual-report PDFs)

**File:** `scr_saudi_topsites_2019_2023.csv` — the first **real** time series in this project.

## Provenance
- **Source:** Saudi Cancer Registry (SCR) annual reports, 2019–2023 (PDFs supplied by the author; downloaded from shc.gov.sa).
- **Table:** "Most common cancers among Saudi nationals" (each report).
- **Population/scope:** Saudi nationals, **both sexes, all ages**.
- **Measure:** **incident case COUNTS** (not rates).
- **Extraction:** `../extract_scr_reports.py` (PyMuPDF). Handles the 2019–2022 "Sites|No.|%" table and the different 2023 "Rank|Site|No.|%" layout. Every value was printed and eyeballed against the PDFs.

## What's in it
The 7 cancer sites that appear in the **top-10 of every year** (so the series is complete, with no false zeros): Breast, Colorectal, Thyroid, NHL, Leukaemia, Brain/CNS, Corpus Uteri.

## Read-with-care (important caveats)
- **2020 is a COVID artifact.** Counts dip across *all* sites in 2020 (e.g., Breast 2894→2499) then rebound — this reflects pandemic disruption of diagnosis/registration, **not** a real fall in incidence. Do not interpret the 2020 dip as a trend.
- **Counts, not rates.** The upward drift partly reflects population growth and improving registry coverage, not necessarily rising risk. For risk, age-standardized rates + denominators are needed.
- **National, not regional.** This is all-Saudi; it does **not** isolate the Eastern Province. The regional breakdown (the actual exposure question) needs the regional tables (often published as figures/images → harder) or SCR microdata.
- **Lung & Liver are not here** — they fell out of the top-10 in some years (Lung appears only 2019: 589, 2020: 458, 2023: 666). A complete Lung series needs the full per-site table (ICD-10 C33–C34) from each report — a next extraction step.
- Only 2019–2023 (5 recent years). All post-latency; this window cannot address the 1991 event. Extend with older reports (2004→) via the same script.

## Regenerate / extend
```
pip install pymupdf
python3 ../extract_scr_reports.py /folder/with/SCR/pdfs    # files named *YYYY*.pdf
python3 ../plot_trends.py        --input scr_saudi_topsites_2019_2023.csv --out scr_trend_2019_2023 --ylabel "Incident cases (count)"
python3 ../plot_cases_by_year.py --input scr_saudi_topsites_2019_2023.csv --out scr_stacked_2019_2023
```
