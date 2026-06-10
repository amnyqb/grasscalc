#!/usr/bin/env python3
"""Pull + merge the three open US layers into one county analytic table:
cancer incidence (NCI/CDC State Cancer Profiles) x smoking (CDC PLACES) x
industrial air-toxic risk (EPA AirToxScreen), joined on 5-digit county FIPS.

Verified working 2026-06-09 on Louisiana (64/64 parishes). Defaults to Louisiana
(stateFIPS=22); pass --states to widen, or "all" for the national panel. No DUA.

USAGE
    pip install openpyxl
    python3 pull_data.py                 # Louisiana, full sentinel panel
    python3 pull_data.py --states 22,48  # LA + TX
Outputs: data/us_county_merged.csv  (one row per county x sentinel site)
"""
import csv, io, os, sys, urllib.request, argparse

SCP = "https://statecancerprofiles.cancer.gov/incidencerates/index.php"
ATS = "https://www.epa.gov/system/files/documents/2025-01/national_cancerrisk_by_county_srcgrp.xlsx"
PLACES = "https://data.cdc.gov/resource/swc5-untb.csv"
SENTINELS = {"047": "Lung", "071": "Bladder", "072": "Kidney", "058": "NHL",
             "090": "Leukaemia", "035": "Liver", "053": "Melanoma(negctrl)"}


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 research"})
    return urllib.request.urlopen(req, timeout=90).read()


def scp_incidence(state_fips, cancer):
    url = (f"{SCP}?stateFIPS={state_fips}&areatype=county&cancer={cancer}&race=00"
           f"&sex=0&age=001&stage=999&year=0&type=incd&output=1")
    out = {}
    for r in csv.reader(io.StringIO(get(url).decode("utf-8", "replace"))):
        if len(r) > 3 and r[1].isdigit() and len(r[1]) == 5 and not r[1].endswith("000"):
            try:
                out[r[1]] = (float(r[3]), r[0].split("(")[0].strip())
            except ValueError:
                pass
    return out


def places_smoking(state_abbr):
    url = (f"{PLACES}?stateabbr={state_abbr}&measureid=CSMOKING"
           f"&data_value_type=Crude%20prevalence&$limit=5000&$select=locationid,data_value")
    out = {}
    for r in csv.DictReader(io.StringIO(get(url).decode("utf-8", "replace"))):
        try:
            out[r["locationid"]] = float(r["data_value"])
        except (ValueError, KeyError):
            pass
    return out


def airtoxscreen(path="/tmp/ats_county.xlsx"):
    import openpyxl
    if not os.path.exists(path):
        open(path, "wb").write(get(ATS))
    wb = openpyxl.load_workbook(path, read_only=True); ws = wb.active
    hdr = [str(c.value).strip().lower() for c in next(ws.iter_rows(min_row=1, max_row=1))]
    ci = lambda s: next(i for i, h in enumerate(hdr) if s in h)
    i_f, i_t, i_p = ci("fips"), ci("total cancer risk"), ci("pt-stationarypoint")
    out = {}
    for row in ws.iter_rows(min_row=2, values_only=True):
        try:
            out[str(row[i_f]).zfill(5)] = (float(row[i_t]), float(row[i_p]))
        except (ValueError, TypeError):
            pass
    return out


# minimal state FIPS<->abbr for the layers that key differently
ST = {"22": "LA", "48": "TX", "06": "CA", "36": "NY", "12": "FL", "01": "AL",
      "28": "MS", "21": "KY", "47": "TN", "13": "GA"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--states", default="22", help="comma FIPS, or 'all'")
    a = ap.parse_args()
    states = list(ST) if a.states == "all" else a.states.split(",")
    pol = airtoxscreen()
    rows = []
    for sf in states:
        abbr = ST.get(sf)
        if not abbr:
            print(f"skip {sf} (add to ST map)"); continue
        smk = places_smoking(abbr)
        for code, site in SENTINELS.items():
            inc = scp_incidence(sf, code)
            for fips, (rate, name) in inc.items():
                if fips in smk and fips in pol:
                    rows.append(dict(fips=fips, county=name, state=abbr, site=site,
                                     incidence=rate, smoking_pct=smk[fips],
                                     ind_pollution=pol[fips][1], total_pollution=pol[fips][0]))
        print(f"{abbr}: merged {len([r for r in rows if r['state']==abbr])} county-site rows")
    os.makedirs("data", exist_ok=True)
    with open("data/us_county_merged.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["fips", "county", "state", "site",
                                           "incidence", "smoking_pct", "ind_pollution", "total_pollution"])
        w.writeheader(); w.writerows(rows)
    print(f"[written] data/us_county_merged.csv ({len(rows)} rows)")


if __name__ == "__main__":
    main()
