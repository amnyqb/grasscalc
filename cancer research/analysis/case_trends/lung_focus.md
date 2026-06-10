# Lung cancer in Saudi nationals — what the SCR data shows about causes

Focus answer to: lung cancer in Saudi nationals, and its causes (smoking etc.).
Built from the 5 SCR annual reports (2019–2023) we extracted. **Real data; registry
records incidence, not exposures.**

## The numbers (Saudi nationals)
- **Counts by year/sex** (`scr_lung_by_sex_2019_2023.csv`): 589 → 458 (2020 COVID dip) → 535 → 623 → 666. ~2.7:1 male:female (2023: 463 M / 203 F; ratio 2.29:1).
- **Rate (2023):** ASR **8.5/100k male, 3.3/100k female** — among the **lowest internationally** (`scr2023_lung_intl_asr.csv`: China 52/30, USA 34/30, UK 32/29 vs Saudi 8.5/3.3), in the low-smoking Gulf/India band.
- **Median age at diagnosis:** 65 (M), 62 (F). **Stage:** 56.8% diagnosed *distant* (late) — poor-prognosis, public-health relevant.

## What the registry CANNOT tell us
The SCR records **site, age, sex, morphology, stage** — **NOT smoking status, occupation, or residence/exposure.** So causes cannot be read off these reports directly. Anyone attributing cause from registry counts alone is overreaching.

## But the registry DOES carry real causal clues — and they point partly AWAY from smoking
1. **Low ASR tracks low smoking.** Saudi lung ASR (8.5/3.3) is a fraction of high-smoking countries — consistent with low smoking prevalence (GATS 2019: ~27.5% men / 3.7% women) being the dominant driver of the *male* burden.
2. **Morphology is the key tell** (`scr2023_lung_morphology.csv`):
   - **Adenocarcinoma = 58% overall, 61% in women** — the subtype *least* linked to smoking and *predominant in never-smokers*.
   - **Smoking-specific subtypes (squamous + small cell) = only 16.4% overall, and just 9.9% in women.** In heavy-smoking populations these typically make up 40–50%+. This low share is a strong, registry-based signal that **a large fraction of Saudi lung cancer is not smoking-driven.**
3. **Sex ratio mismatch.** The male:female *smoking* ratio is ~7:1, but the lung-cancer ratio is only ~2.3–2.7:1. Female lung cancer is "too high" for a population where ~3.7% of women smoke → points to **non-smoking causes in women** (secondhand smoke, indoor/outdoor air pollution, environmental/occupational, genetics — EGFR-driven adenocarcinoma).
4. **Consistent with the ~43% never-smoker proportion** reported in a Saudi lung-cancer cohort (`madinah2024`) and with our smoking-sensitivity result (regional contrasts not reproducible by smoking alone).

## What the reports do NOT provide
- **No lung-by-Saudi-region breakdown.** Figure 3.7.4 is an *international* comparison, not Eastern-Province-vs-rest. The regional contrast (EP 3.36 vs Jazan 0.59) lives only in the dedicated 2015–2020 study (`scrlung2025`), not the annual reports.
- So the registry can describe national burden and subtype, but **cannot localize an environmental signal** — that needs the regional/microdata analysis (the §5 study; the never-smoker subcohort is the highest-value lever).

## Long-run lung ASR trend (NEW — full SCR series 2006–2023)
Extracted from every readable annual report (`scr_lung_by_sex_asr_2004_2023.csv`;
counts + ASR cross-checked between the per-site×sex summary table and the Part III
narrative — the two sources agree wherever both are printed). Chart:
`scr_lung_asr_trend.png`. **ASR = World standard /100,000.**

- **Male lung ASR:** 6.1 (2006) → 6.9 (2007) → 5.8 (2008) → 5.7 (2009) → 5.8 (2010)
  → 6.4 (2011) → 5.9 (2012) → 5.5 (2013) → 5.0 (2018) → 6.0 (2019) → **4.8 (2020, COVID dip)**
  → 7.5 (2021) → 8.8 (2022) → 8.5 (2023).
- **Female lung ASR:** ~1.4–2.2 across 2006–2020, rising to 3.0/2.7/3.3 in 2021–2023.
- **Counts (both sexes):** 296 (2004) → 312 (2006) → … → 504 (2018) → 589 (2019)
  → **458 (2020, COVID)** → 535 → 623 → 666 (2023).

**What's solid vs what to flag:**
- The 2006–2020 male ASR is flat-to-gently-declining (~5–7), the female ASR is low
  and roughly flat — consistent with the low-smoking picture above.
- A **step-up in 2021–2023** (male 7.5→8.8→8.5; female ~3) is real in the printed
  tables, but could reflect a change in the report's standard population/method as
  well as a genuine recent rise. **Do not over-read it; keep at "Compatible".**
- 2020 is COVID-depressed (registration disruption), not a real decline.
- Gaps (2005 missing PDF; 2014/2017 image-only; 2013 counts as images; 2004/2015
  ASR unreadable) are left blank — the line breaks rather than interpolating.

## Bottom line on causes
**Smoking is a major cause of Saudi lung cancer — especially the male burden — but demonstrably *not* the whole story.** The dominance of adenocarcinoma, the very low share of smoking-specific subtypes (esp. in women), the modest sex ratio, and the high never-smoker fraction all indicate a substantial **non-smoking / environmental** contribution. Pinning that down requires individual smoking status + exposure/residence data the registry does not hold.
