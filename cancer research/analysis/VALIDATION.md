# Source validation report

**Scope of this validation.** This is an **offline integrity/consistency** check.
It does **not** confirm that a DOI resolves or that author/year/journal match the
indexed record — the build environment has no access to Crossref, PubMed, or
doi.org (network allowlist = PyPI only). External verification remains an open
author action item (see `../REPORT.md`).

Reproduce: `python3 /tmp/validate.py` (script logic also summarized below).

## Result: PASS (no structural/consistency issues)

| check | result |
|---|---|
| Duplicate `cite_key` | none |
| Duplicate DOI | none |
| Duplicate citation string | none |
| DOI syntax (`^10\.\d{4,9}/…`) on all 28 present DOIs | all valid |
| PMID/PMCID syntax on all 28 present IDs | all valid |
| `cite_key` year vs year in citation string | no mismatches |
| Charted `cite_key`s (key_values, extraction) resolve to a reference | all resolve |

## Inventory
- References: **63**
- Identifier status: `UNVERIFIED` 29 · `NEEDS_LOOKUP` 13 · `NO_DOI` 13 · `FLAG_AUTHOR` 6 · `VERIFIED` 2
- DOIs present: **28** · PMID/PMCID present: **28**
- References feeding the structured data tables: **33 of 63** (the other 30 are
  narrative/methodological citations — expected for an evidence map)

## What still requires online verification (not possible here)
- Confirm each `UNVERIFIED` DOI/PMID resolves to the cited work.
- Resolve `NEEDS_LOOKUP` (13) and `FLAG_AUTHOR` (6) rows.
- Confirm author/year/journal/volume/pages against the indexed record.

These can be completed in any environment with Crossref/PubMed access, or by the
author at proof stage.
