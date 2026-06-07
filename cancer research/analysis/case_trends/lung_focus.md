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

## Bottom line on causes
**Smoking is a major cause of Saudi lung cancer — especially the male burden — but demonstrably *not* the whole story.** The dominance of adenocarcinoma, the very low share of smoking-specific subtypes (esp. in women), the modest sex ratio, and the high never-smoker fraction all indicate a substantial **non-smoking / environmental** contribution. Pinning that down requires individual smoking status + exposure/residence data the registry does not hold.
