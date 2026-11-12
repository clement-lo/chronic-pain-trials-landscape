"""Step 3: Stage 2 analyses on the included trials.

Usage:
    .venv/bin/python src/analyse.py

Reads data/trials.csv, the cached raw pull (for individual outcome measures)
and outputs/numbers.json (written by build.py), then adds:
  * HK/Asia subset         -> outputs/summary_table_asia.md, outputs/hk_trials.md
  * why trials stopped     -> outputs/stop_reasons.csv, outputs/review/stop_reasons_unclassified.csv
  * results posted         -> section in outputs/stage2_tables.md
  * IMMPACT mapping        -> outputs/immpact_mapping.csv, outputs/review/immpact_30.csv
  * trials per start year  -> used by src/figures.py
and writes every number back into outputs/numbers.json.
"""

import json
import sys
from pathlib import Path

import pandas as pd
from dateutil.relativedelta import relativedelta

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build import (GROUP_ORDER, SPONSOR_LABELS, STATUS_LABELS, add_labels,  # noqa: E402
                   enrolment_stats, load_pull, outcomes_of, summary_tables)
from config import START_MAX, START_MIN  # noqa: E402
from immpact import DOMAINS, map_measure  # noqa: E402
from rules import GROUP_LABELS, GROUPS, MIN_CHRONIC_DAYS  # noqa: E402
from stop_reasons import ORDER as STOP_ORDER, classify_stop  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"
SEED = 20261112

# Sites counted for the HK/Asia subset (country names as the registry spells them;
# Macau is listed under both spellings, though no included trial has a site there)
ASIA = ["Hong Kong", "China", "Macao", "Macau", "Taiwan", "Japan", "South Korea",
        "Korea, Republic of", "Singapore", "Malaysia", "Thailand"]
ASIA_LABELS = {"China": "Mainland China", "Korea, Republic of": "South Korea", "Macao": "Macau"}
RESULTS_LAG_MONTHS = 12


def pct(a, b):
    return round(100 * a / b, 1) if b else None


def end_of_period(date):
    """Latest day a partial date can mean: YYYY -> 31 Dec, YYYY-MM -> month end."""
    if not isinstance(date, str) or not date:
        return None
    if len(date) == 4:
        return pd.Timestamp(f"{date}-12-31")
    if len(date) == 7:
        return pd.Timestamp(f"{date}-01") + pd.offsets.MonthEnd(0)
    return pd.Timestamp(date)


def countries_of(s):
    return s.split("; ") if isinstance(s, str) else []


def main():
    N = json.loads((OUT / "numbers.json").read_text())
    trials = add_labels(pd.read_csv(ROOT / "data" / "trials.csv"))
    meta, studies, _ = load_pull(N["pull_date"])
    pull = pd.Timestamp(N["pull_date"])
    T = len(trials)
    tables = ["# Stage 2 tables", "",
              f"Included trials: {T:,}. Data from ClinicalTrials.gov, pulled {N['pull_date']}.", ""]

    # ------------------------------------------------------------------ parameters
    N["parameters"] = {
        "start_min": START_MIN, "start_max": START_MAX,
        "start_year_min": int(START_MIN[:4]), "start_year_max": int(START_MAX[:4]),
        "n_groups": len(GROUPS), "n_immpact_domains": len(DOMAINS),
        "chronic_min_weeks": MIN_CHRONIC_DAYS // 7, "chronic_min_months": 3,
        "results_lag_months": RESULTS_LAG_MONTHS,
        "results_cutoff_date": (pull - relativedelta(months=RESULTS_LAG_MONTHS)).date().isoformat(),
        "n_asia_places": len(set(ASIA_LABELS.get(c, c) for c in ASIA)),
        "figure_dpi": 300, "summary_max_words": 450, "review_sample": 30,
    }
    N["derived"] = {
        "pct_msk": pct(N["by_group"]["MSK"], T),
        "pct_phase_not_applicable": pct(N["by_phase"].get("Not applicable", 0), T),
        "n_drug_phase": T - N["by_phase"].get("Not applicable", 0) - N["by_phase"].get("Missing", 0),
        "pct_industry": pct(N["by_sponsor_class"].get("Industry", 0), T),
        "pct_other_sponsor": pct(N["by_sponsor_class"].get(SPONSOR_LABELS["OTHER"], 0), T),
        "pct_unknown_status": pct(N["by_status"].get("Unknown status", 0), T),
        "n_multiple": N["by_group"]["Multiple"],
    }

    # ------------------------------------------------------------ start year
    trials["start_year"] = trials["start_date"].str[:4].astype(int)
    years = list(range(int(START_MIN[:4]), int(START_MAX[:4]) + 1))
    N["by_start_year"] = {
        g: {str(y): int(((trials["group"] == g) & (trials["start_year"] == y)).sum()) for y in years}
        for g in GROUP_ORDER}
    N["by_start_year"]["All"] = {str(y): int((trials["start_year"] == y).sum()) for y in years}

    # ------------------------------------------------------------- HK / Asia
    trials["asia_sites"] = trials["countries"].map(
        lambda s: sorted({ASIA_LABELS.get(c, c) for c in countries_of(s) if c in ASIA}))
    asia = trials[trials["asia_sites"].str.len() > 0].copy()
    hk = trials[trials["countries"].map(lambda s: "Hong Kong" in countries_of(s))].copy()
    by_place = {}
    for c in ASIA:
        lab = ASIA_LABELS.get(c, c)
        by_place[lab] = int(trials["countries"].map(lambda s, c=c: c in countries_of(s)).sum()) + by_place.get(lab, 0)
    N["asia"] = {
        "n": len(asia), "pct_of_included": pct(len(asia), T),
        "n_no_country": int(trials["countries"].isna().sum()),
        "by_place": dict(sorted(by_place.items(), key=lambda kv: -kv[1])),
        "by_group": {g: int((asia["group"] == g).sum()) for g in GROUP_ORDER},
        "by_sponsor_class": asia["sponsor_label"].value_counts().to_dict(),
        "pct_industry": pct(int((asia["sponsor_class"] == "INDUSTRY").sum()), len(asia)),
        "enrolment": enrolment_stats(asia),
        "hong_kong": {
            "n": len(hk),
            "pct_of_asia": pct(len(hk), len(asia)),
            "by_group": {g: int((hk["group"] == g).sum()) for g in GROUP_ORDER},
            "by_sponsor_class": hk["sponsor_label"].value_counts().to_dict(),
            "by_status": hk["status_label"].value_counts().to_dict(),
            "lead_sponsors": hk["lead_sponsor"].value_counts().to_dict(),
            "hk_only_sites": int(hk["countries"].map(lambda s: countries_of(s) == ["Hong Kong"]).sum()),
        },
    }
    A = ["# HK/Asia subset: summary tables", "",
         f"Trials with at least one site in Hong Kong, mainland China, Macau, Taiwan, Japan, "
         f"South Korea, Singapore, Malaysia or Thailand: **{len(asia):,}** of {T:,} included trials. "
         f"{N['asia']['n_no_country']:,} included trials list no site country and cannot be placed. "
         f"Hong Kong: **{len(hk):,}** trials.", "",
         "## Trials by place (a trial can have sites in several places)", "",
         "| Place | Trials |", "|---|---:|"]
    A += [f"| {k} | {v:,} |" for k, v in N["asia"]["by_place"].items()]
    A += [""] + summary_tables(asia, N["asia"]["enrolment"])
    (OUT / "summary_table_asia.md").write_text("\n".join(A))

    H = ["# Trials with a site in Hong Kong", "",
         f"{len(hk):,} included trials; {N['asia']['hong_kong']['hk_only_sites']:,} have sites only in Hong Kong.", "",
         "| NCT ID | Group | Lead sponsor | Status | Start | Title |", "|---|---|---|---|---|---|"]
    for _, r in hk.sort_values("start_date").iterrows():
        H.append(f"| {r.nct_id} | {r.group} | {r.lead_sponsor} | {r.status_label} | "
                 f"{r.start_date} | {str(r.title).replace('|', '/')} |")
    (OUT / "hk_trials.md").write_text("\n".join(H) + "\n")

    # --------------------------------------------------------- why trials stop
    stopped = trials[trials["overall_status"].isin(["TERMINATED", "WITHDRAWN", "SUSPENDED"])].copy()
    res = stopped["why_stopped"].map(classify_stop)
    stopped["stop_reason"] = res.str[0]
    stopped["stop_categories"] = res.str[1].map("; ".join)
    stopped["unclassified"] = res.str[2]
    stopped[["nct_id", "group", "overall_status", "stop_reason", "stop_categories", "unclassified",
             "why_stopped"]].to_csv(OUT / "stop_reasons.csv", index=False)
    (OUT / "review").mkdir(exist_ok=True)
    stopped[stopped["unclassified"]][["nct_id", "overall_status", "why_stopped"]].to_csv(
        OUT / "review" / "stop_reasons_unclassified.csv", index=False)
    tw = stopped[stopped["overall_status"].isin(["TERMINATED", "WITHDRAWN"])]
    N["stop_reasons"] = {
        "n_stopped": len(stopped),
        "by_status": stopped["overall_status"].value_counts().to_dict(),
        "main_reason": {c: int((stopped["stop_reason"] == c).sum()) for c in STOP_ORDER},
        "main_reason_pct": {c: pct(int((stopped["stop_reason"] == c).sum()), len(stopped)) for c in STOP_ORDER},
        "terminated_withdrawn": {
            s: {c: int(((tw["overall_status"] == s) & (tw["stop_reason"] == c)).sum()) for c in STOP_ORDER}
            for s in ["TERMINATED", "WITHDRAWN"]},
        "n_terminated_withdrawn": len(tw),
        "n_multiple_categories": int((res.str[1].str.len() > 1).sum()),
        "n_unclassified": int(stopped["unclassified"].sum()),
        "n_not_stated": int((stopped["stop_reason"] == "Not stated").sum()),
        "any_mention": {c: int(stopped["stop_categories"].str.contains(c, regex=False).sum())
                        for c in STOP_ORDER[:-2]},
    }
    tables += ["## Why trials stopped (terminated, withdrawn and suspended trials)", "",
               f"n = {len(stopped):,}. Main reason by the precedence in `src/stop_reasons.py`; "
               "'Any mention' counts every category a reason touches.", "",
               "| Main reason | Terminated | Withdrawn | Suspended | Total | % | Any mention |",
               "|---|---:|---:|---:|---:|---:|---:|"]
    for c in STOP_ORDER:
        cnt = [int(((stopped["overall_status"] == s) & (stopped["stop_reason"] == c)).sum())
               for s in ["TERMINATED", "WITHDRAWN", "SUSPENDED"]]
        anym = N["stop_reasons"]["any_mention"].get(c, "–")
        tables.append(f"| {c} | {cnt[0]} | {cnt[1]} | {cnt[2]} | {sum(cnt)} | "
                      f"{N['stop_reasons']['main_reason_pct'][c]} | {anym} |")
    tables += ["", f"{N['stop_reasons']['n_unclassified']} stated reasons matched no keyword and are "
               "counted as Other; they are listed in `outputs/review/stop_reasons_unclassified.csv`.", ""]

    # ----------------------------------------------------------- results posted
    cutoff = pull - relativedelta(months=RESULTS_LAG_MONTHS)
    trials["pcd_end"] = trials["primary_completion_date"].map(end_of_period)
    elig_status = trials["overall_status"].isin(["COMPLETED", "TERMINATED"])
    elig = trials[elig_status & trials["pcd_end"].notna() & (trials["pcd_end"] <= cutoff)].copy()
    posted = elig["results_posted"] == "yes"
    def share(df):
        p = int((df["results_posted"] == "yes").sum())
        return {"n": len(df), "posted": p, "pct": pct(p, len(df))}
    N["results_posted"] = {
        "cutoff_date": cutoff.date().isoformat(),
        "eligible": len(elig), "posted": int(posted.sum()), "pct": pct(int(posted.sum()), len(elig)),
        "excluded_completion_too_recent": int((elig_status & trials["pcd_end"].notna()
                                               & (trials["pcd_end"] > cutoff)).sum()),
        "excluded_no_pcd": int((elig_status & trials["pcd_end"].isna()).sum()),
        "pcd_estimated_among_eligible": int((elig["primary_completion_date_type"] == "ESTIMATED").sum()),
        "by_sponsor_class": {lab: share(elig[elig["sponsor_label"] == lab])
                             for lab in elig["sponsor_label"].value_counts().index},
        "by_group": {g: share(elig[elig["group"] == g]) for g in GROUP_ORDER},
        "by_status": {s: share(elig[elig["overall_status"] == s]) for s in ["COMPLETED", "TERMINATED"]},
        "asia": share(elig[elig["asia_sites"].str.len() > 0]),
        "hong_kong": share(elig[elig["countries"].map(lambda s: "Hong Kong" in countries_of(s))]),
    }
    R = N["results_posted"]
    tables += ["## Results posted on ClinicalTrials.gov", "",
               f"Completed or terminated trials whose primary completion date is on or before "
               f"{R['cutoff_date']} ({RESULTS_LAG_MONTHS} months before the pull date). A month-only date "
               f"counts as the last day of that month. 'Results posted' means a results section is "
               f"posted on ClinicalTrials.gov; it is not a measure of legal compliance, because the "
               f"duty to post applies only to some trials.", "",
               f"Overall: **{R['posted']:,} of {R['eligible']:,} ({R['pct']}%)**. "
               f"{R['excluded_completion_too_recent']:,} completed/terminated trials finished too "
               f"recently to count; {R['pcd_estimated_among_eligible']:,} eligible trials still show "
               f"an estimated primary completion date.", "",
               "| Lead sponsor class | Eligible | Results posted | % |", "|---|---:|---:|---:|"]
    for lab, v in R["by_sponsor_class"].items():
        tables.append(f"| {lab} | {v['n']:,} | {v['posted']:,} | {v['pct']} |")
    tables += ["", "| Group | Eligible | Results posted | % |", "|---|---:|---:|---:|"]
    for g, v in R["by_group"].items():
        tables.append(f"| {g} | {v['n']:,} | {v['posted']:,} | {v['pct']} |")
    tables.append("")

    # ---------------------------------------------------------------- IMMPACT
    rows = []
    groups = dict(zip(trials["nct_id"], trials["group"]))
    for n in trials["nct_id"]:
        for o in outcomes_of(studies[n]["protocolSection"]):
            if o["level"] != "primary":
                continue
            d, on = map_measure(o["measure"], o["description"])
            rows.append({"nct_id": n, "group": groups[n], "measure": o["measure"],
                         "time_frame": o["time_frame"], "domains": "; ".join(d),
                         "n_domains": len(d), "matched_on": on})
    im = pd.DataFrame(rows)
    im.to_csv(OUT / "immpact_mapping.csv", index=False)
    M = len(im)
    per_trial = im.groupby("nct_id")["domains"].apply(lambda s: set("; ".join(s).split("; ")) - {""})
    N["immpact"] = {
        "n_measures": M,
        "n_trials": int(im["nct_id"].nunique()),
        "matched_on": im["matched_on"].value_counts().to_dict(),
        "measures_by_domain": {d: int(im["domains"].str.contains(d, regex=False).sum()) for d in DOMAINS},
        "measures_by_domain_pct": {d: pct(int(im["domains"].str.contains(d, regex=False).sum()), M) for d in DOMAINS},
        "measures_multi_domain": int((im["n_domains"] > 1).sum()),
        "measures_multi_domain_pct": pct(int((im["n_domains"] > 1).sum()), M),
        "measures_none": int((im["n_domains"] == 0).sum()),
        "measures_none_pct": pct(int((im["n_domains"] == 0).sum()), M),
        "trials_with_domain": {d: int(per_trial.map(lambda s, d=d: d in s).sum()) for d in DOMAINS},
        "trials_with_domain_pct": {d: pct(int(per_trial.map(lambda s, d=d: d in s).sum()), T) for d in DOMAINS},
        "trials_no_domain": int(per_trial.map(len).eq(0).sum()),
        "trials_no_domain_pct": pct(int(per_trial.map(len).eq(0).sum()), T),
        "trials_pain_intensity_pct_by_group": {
            g: pct(int(per_trial[per_trial.index.isin(trials.loc[trials["group"] == g, "nct_id"])]
                       .map(lambda s: "Pain intensity" in s).sum()), int((trials["group"] == g).sum()))
            for g in GROUP_ORDER},
    }
    I = N["immpact"]
    tables += ["## Primary outcomes mapped to IMMPACT core domains", "",
               f"{M:,} primary outcome measures from {I['n_trials']:,} trials. Rules in `src/immpact.py`.", "",
               "| Domain | Measures | % of measures | Trials with ≥1 such primary outcome | % of trials |",
               "|---|---:|---:|---:|---:|"]
    for d in DOMAINS:
        tables.append(f"| {d} | {I['measures_by_domain'][d]:,} | {I['measures_by_domain_pct'][d]} | "
                      f"{I['trials_with_domain'][d]:,} | {I['trials_with_domain_pct'][d]} |")
    tables += [f"| *Spans several domains* | {I['measures_multi_domain']:,} | {I['measures_multi_domain_pct']} | | |",
               f"| *Matches none* | {I['measures_none']:,} | {I['measures_none_pct']} | "
               f"{I['trials_no_domain']:,} | {I['trials_no_domain_pct']} |", ""]
    # 30 for checking: 10 single-domain, 10 multi-domain, 10 none (fixed seed)
    pick = pd.concat([im[im["n_domains"] == 1].sample(10, random_state=SEED),
                      im[im["n_domains"] > 1].sample(10, random_state=SEED),
                      im[im["n_domains"] == 0].sample(10, random_state=SEED)])
    pick.to_csv(OUT / "review" / "immpact_30.csv", index=False)

    # ------------------------------------------- text-ready values for the report
    y0, y1 = str(years[0]), str(years[-1])
    e_all = N["enrolment"]["All"]["all_types"]
    e_asia = N["asia"]["enrolment"]["All"]["all_types"]
    hk_sp = hk["lead_sponsor"].fillna("")
    sr, rp, td = N["stop_reasons"], N["results_posted"]["by_sponsor_class"], I["trials_with_domain_pct"]
    N["text"] = {
        "starts_first_year": N["by_start_year"]["All"][y0],
        "starts_last_year": N["by_start_year"]["All"][y1],
        "enrol_median": round(e_all["median"]), "enrol_q1": round(e_all["q1"]), "enrol_q3": round(e_all["q3"]),
        "asia_enrol_median": round(e_asia["median"]),
        "stop_low_accrual": sr["main_reason"]["Low accrual"], "stop_low_accrual_pct": sr["main_reason_pct"]["Low accrual"],
        "stop_funding": sr["main_reason"]["Funding"], "stop_funding_pct": sr["main_reason_pct"]["Funding"],
        "stop_covid": sr["main_reason"]["COVID-19"], "stop_covid_pct": sr["main_reason_pct"]["COVID-19"],
        "results_pct_industry": rp.get("Industry", {}).get("pct"),
        "results_pct_other": rp.get(SPONSOR_LABELS["OTHER"], {}).get("pct"),
        "immpact_pain_pct": td["Pain intensity"], "immpact_physical_pct": td["Physical functioning"],
        "immpact_emotional_pct": td["Emotional functioning"],
        "immpact_global_pct": td["Improvement and satisfaction"],
        "immpact_adverse_pct": td["Symptoms and adverse events"],
        "immpact_disposition_pct": td["Participant disposition"],
        "asia_china": N["asia"]["by_place"].get("Mainland China", 0),
        "asia_korea": N["asia"]["by_place"].get("South Korea", 0),
        "asia_taiwan": N["asia"]["by_place"].get("Taiwan", 0),
        "hk_msk": N["asia"]["hong_kong"]["by_group"]["MSK"],
        "hk_cpsp": N["asia"]["hong_kong"]["by_group"]["CPSP"],
        "hk_academic": N["asia"]["hong_kong"]["by_sponsor_class"].get(SPONSOR_LABELS["OTHER"], 0),
        "hk_polyu": int(hk_sp.str.contains("Polytechnic").sum()),
        "hk_hku": int((hk_sp.str.contains("University of Hong Kong") & ~hk_sp.str.contains("Chinese")).sum()),
        "hk_cuhk": int(hk_sp.str.contains("Chinese University of Hong Kong").sum()),
    }

    (OUT / "stage2_tables.md").write_text("\n".join(tables))
    (OUT / "numbers.json").write_text(json.dumps(N, indent=2, default=int))

    print(f"Asia {len(asia)}  HK {len(hk)}")
    print("stop main:", N["stop_reasons"]["main_reason"], "unclassified", N["stop_reasons"]["n_unclassified"])
    print("results posted:", R["posted"], "/", R["eligible"], R["pct"])
    print("IMMPACT trials %:", I["trials_with_domain_pct"], "none", I["measures_none_pct"])


if __name__ == "__main__":
    main()
