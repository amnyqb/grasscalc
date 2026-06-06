# Search strategy — registered four-database protocol

Companion to *Non-Tobacco Environmental Carcinogenesis in Exposed Populations* (Cancer Epidemiology). Concept structure: **outcome AND exposure AND epidemiologic-metric**, controlled vocabulary + free text. Limits: inception to 6 June 2026; English for the database search (Arabic-language Saudi MoH/SCR sources hand-searched). No methodological filters (scoping breadth).

> NOTE (scope): this four-database search is **specified but NOT yet executed** (manuscript Section 2.7). Supplementary Figure S1 is the *planned* PRISMA-ScR flow; screened/included counts are populated on execution.

## MEDLINE/PubMed (primary, Methods 2.4)

```
( "neoplasms"[MeSH] OR cancer*[tiab] OR carcinoma*[tiab]
  OR neoplas*[tiab] OR tumour*[tiab] OR tumor*[tiab]
  OR malignan*[tiab] OR leukaemia*[tiab]
  OR leukemia*[tiab] OR lymphoma*[tiab] )
AND
( "radiation, ionizing"[MeSH] OR "radioactive fallout"[MeSH]
  OR radiation[tiab] OR fallout[tiab]
  OR "nuclear test*"[tiab] OR "atomic bomb"[tiab]
  OR "depleted uranium"[tiab] OR "oil fire*"[tiab]
  OR "oil well fire*"[tiab] OR "burn pit*"[tiab]
  OR "combustion product*"[tiab]
  OR "polycyclic aromatic"[tiab] OR dioxin*[tiab]
  OR "Agent Orange"[tiab] OR TCDD[tiab]
  OR trichloroethylene[tiab]
  OR tetrachloroethylene[tiab]
  OR "methyl isocyanate"[tiab]
  OR "ammonium nitrate"[tiab]
  OR petrochemical*[tiab] OR "air toxics"[tiab]
  OR "volatile organic compound*"[tiab]
  OR "Gulf War"[tiab] OR "war exposure"[tiab]
  OR "military personnel"[MeSH] )
AND
( incidence[tiab] OR mortality[tiab]
  OR "standardized incidence"[tiab]
  OR "standardised incidence"[tiab]
  OR cohort[tiab] OR registry[tiab]
  OR epidemiolog*[tiab] OR "relative risk"[tiab]
  OR "excess relative risk"[tiab]
  OR "standardized mortality"[tiab] )
```

## Embase (Emtree + free text)

```
('neoplasm'/exp OR cancer:ti,ab OR carcinoma:ti,ab
   OR neoplasm:ti,ab OR tumour:ti,ab OR tumor:ti,ab
   OR leukaemia:ti,ab OR lymphoma:ti,ab)
AND
('ionizing radiation'/exp OR 'radioactive fallout'/exp
   OR fallout:ti,ab OR 'atomic bomb':ti,ab
   OR 'oil fire':ti,ab OR 'burn pit':ti,ab
   OR 'polycyclic aromatic hydrocarbon'/exp
   OR dioxin:ti,ab OR trichloroethylene:ti,ab
   OR tetrachloroethylene:ti,ab
   OR 'methyl isocyanate':ti,ab
   OR petrochemical:ti,ab OR 'volatile organic compound':ti,ab
   OR 'Gulf War':ti,ab OR 'military personnel'/exp)
AND
(incidence:ti,ab OR mortality:ti,ab OR cohort:ti,ab
   OR registry:ti,ab OR 'relative risk':ti,ab
   OR 'standardized incidence':ti,ab)
```

## Scopus (TITLE-ABS-KEY)

```
TITLE-ABS-KEY(
  (cancer OR carcinoma OR neoplasm OR tumour OR tumor
     OR leukaemia OR leukemia OR lymphoma)
  AND (radiation OR fallout OR "atomic bomb"
     OR "oil fire" OR "burn pit" OR "polycyclic aromatic"
     OR dioxin OR TCDD OR trichloroethylene
     OR tetrachloroethylene OR "methyl isocyanate"
     OR petrochemical OR "volatile organic compound"
     OR "Gulf War")
  AND (incidence OR mortality OR cohort OR registry
     OR "relative risk" OR "excess relative risk") )
```

## Web of Science Core Collection (Topic, TS=)

```
TS=( (cancer OR carcinoma OR neoplasm* OR tumo?r*
        OR leukaemia OR leukemia OR lymphoma)
   AND (radiation OR fallout OR "atomic bomb"
        OR "oil fire*" OR "burn pit*" OR "polycyclic aromatic"
        OR dioxin* OR TCDD OR trichloroethylene
        OR tetrachloroethylene OR "methyl isocyanate"
        OR petrochemical* OR "volatile organic compound*"
        OR "Gulf War")
   AND (incidence OR mortality OR cohort OR registry
        OR "relative risk" OR "excess relative risk") )
```

## Grey literature

Institution-site searches by exposure keyword: ATSDR; National Academies/IOM (*Gulf War and Health*, *Veterans and Agent Orange*); UNSCEAR; IARC monographs; Radiation Effects Research Foundation; U.S. Department of Veterans Affairs; U.S. Government Accountability Office; Saudi MoH / Saudi Cancer Registry annual reports. Backward citation searching of included sources.
