#!/usr/bin/env python3
"""Time-trend line charts: a value per year, plotted as trend lines, faceted by
country, one line per cancer type. This is the 'trend chart with time' tool.

It needs a real annual series as input (we have none in the package):
    country , year , cancer_type , value
      value = annual incident COUNT or annual RATE (ASR/crude) -- say which via --ylabel
Where to get an openly-downloadable annual series:
  * CI5plus (IARC)            -> annual incidence RATES by registry, site, sex, year
  * GBD / GHDx (IHME)         -> Saudi national annual incidence 1990-2021 by cancer
  * SEER (incl. Louisiana)    -> annual US counts/rates by site (free DUA)
Harmonize cancer_type + (if rates) the standard population before cross-country reading.

USAGE
    python3 plot_trends.py --input annual.csv --ylabel "Age-standardized rate /100k"
"""
import argparse, csv, sys, os
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

def read(path):
    rs = list(csv.DictReader(open(path, encoding="utf-8")))
    need = {"country","year","cancer_type","value"}
    if not rs or not need.issubset(rs[0]): sys.exit(f"CSV needs columns {sorted(need)}")
    d={}
    for r in rs:
        d.setdefault(r["country"].strip(),{}).setdefault(r["cancer_type"].strip(),{})[int(float(r["year"]))]=float(r["value"] or 0)
    return d

def plot(d, out, ylabel, title, events=None):
    countries=list(d); types=sorted({t for c in d.values() for t in c})
    cmap=plt.get_cmap("tab10"); colour={t:cmap(i%10) for i,t in enumerate(types)}
    n=len(countries)
    fig,axes=plt.subplots(1,n,figsize=(max(4.5*n,6),4.8),squeeze=False); axes=axes[0]
    for ax,c in zip(axes,countries):
        for t in types:
            if t not in d[c]: continue
            ys=sorted(d[c][t]); ax.plot(ys,[d[c][t][y] for y in ys],marker="o",ms=3,lw=1.5,color=colour[t],label=t)
        if events:
            for ev_year,ev_lab in events:
                ax.axvline(ev_year,color="red",ls="--",lw=1,alpha=0.7)
                ax.text(ev_year,ax.get_ylim()[1],f" {ev_lab}",color="red",fontsize=7,va="top",rotation=90)
        ax.set_title(c,fontsize=10,fontweight="bold"); ax.set_xlabel("Year",fontsize=8)
        ax.grid(alpha=0.25); ax.tick_params(labelsize=7)
    axes[0].set_ylabel(ylabel,fontsize=9)
    h=[plt.Line2D([],[],color=colour[t],marker="o",ms=4,lw=1.5) for t in types]
    fig.legend(h,types,title="Cancer type",loc="lower center",ncol=min(len(types),6),fontsize=8,frameon=False,bbox_to_anchor=(0.5,-0.04))
    fig.suptitle(title,fontsize=12,fontweight="bold"); fig.tight_layout(rect=[0,0.05,1,0.95])
    fig.savefig(out+".png",dpi=300,bbox_inches="tight"); fig.savefig(out+".pdf",bbox_inches="tight")
    print("[written]",out+".png /",out+".pdf")

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--input",required=True); ap.add_argument("--out",default="figure_trends")
    ap.add_argument("--ylabel",default="Annual incident cases (count)")
    ap.add_argument("--title",default="Cancer incidence trend by type")
    a=ap.parse_args()
    plot(read(a.input),a.out,a.ylabel,a.title,events=[(1991,"1991 oil fires")])
