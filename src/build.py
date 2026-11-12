"""Step 2: turn the cached API pages into data/trials.csv and the Stage 1 summary.

Usage:
    .venv/bin/python src/build.py               # uses the latest pull in data/raw
    .venv/bin/python src/build.py 2026-11-12    # or a named pull date

Writes:
    data/trials.csv              included trials, one row per NCT ID
    data/excluded.csv            every pulled trial that was not included, with the reason
    outputs/summary_table.md     counts by group x phase, status, sponsor class; enrolment
    outputs/numbers.json         every number quoted in the text outputs
    outputs/review/*.csv         random sample and borderline exclusions for hand-checking
"""

import json
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from config import START_MAX, START_MIN  # noqa: E402
import rules  # noqa: E402
from rules import GROUP_LABELS, GROUPS, classify  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
OUT = ROOT / "outputs"
SEED = 20261112  # fixed seed so the review samples are reproducible

PHASE_LABELS = {
    ("EARLY_PHASE1",): "Early phase 1", ("PHASE1",): "Phase 1",
    ("PHASE1", "PHASE2"): "Phase 1/2", ("PHASE2",): "Phase 2",
    ("PHASE2", "PHASE3"): "Phase 2/3", ("PHASE3",): "Phase 3",
    ("PHASE4",): "Phase 4", ("NA",): "Not applicable",
}
PHASE_ORDER = ["Early phase 1", "Phase 1", "Phase 1/2", "Phase 2", "Phase 2/3",
               "Phase 3", "Phase 4", "Not applicable", "Missing"]
STATUS_LABELS = {
    "COMPLETED": "Completed", "RECRUITING": "Recruiting",
    "NOT_YET_RECRUITING": "Not yet recruiting", "ACTIVE_NOT_RECRUITING": "Active, not recruiting",
    "ENROLLING_BY_INVITATION": "Enrolling by invitation", "TERMINATED": "Terminated",
    "WITHDRAWN": "Withdrawn", "SUSPENDED": "Suspended", "UNKNOWN": "Unknown status",
}
SPONSOR_LABELS = {
    "INDUSTRY": "Industry", "OTHER": "Other (universities, hospitals, non-profits)",
    "NIH": "NIH", "FED": "Other US federal", "OTHER_GOV": "Other government",
    "NETWORK": "Network", "INDIV": "Individual", "AMBIG": "Ambiguous", "UNKNOWN": "Unknown",
}
GROUP_ORDER = GROUPS + ["Multiple"]


def g(d, *path):
    for p in path:
        if not isinstance(d, dict):
            return None
        d = d.get(p)
    return d


def load_pull(pull_date=None):
    days = sorted(p for p in RAW.iterdir() if (p / "pull_meta.json").exists())
    if not days:
        raise SystemExit("No cached pull found: run src/pull.py first")
    day = RAW / pull_date if pull_date else days[-1]
    meta = json.loads((day / "pull_meta.json").read_text())
    studies, hits = {}, {}
    for q in meta["queries"]:
        for f in sorted((day / q["key"]).glob("page_*.json")):
            for s in json.loads(f.read_text()).get("studies", []):
                n = s["protocolSection"]["identificationModule"]["nctId"]
                studies[n] = s
                hits.setdefault(n, []).append(q["key"])
    return meta, studies, hits


def outcomes_of(ps):
    out = []
    for level, key in (("primary", "primaryOutcomes"), ("secondary", "secondaryOutcomes")):
        for o in g(ps, "outcomesModule", key) or []:
            out.append({"level": level, "measure": o.get("measure"),
                        "description": o.get("description"), "time_frame": o.get("timeFrame")})
    return out


def in_window(date):
    """Start date (YYYY-MM or YYYY-MM-DD) inside the study window?"""
    if not date:
        return False
    d = date if len(date) == 10 else date + "-01"
    return START_MIN <= d <= START_MAX


def flatten(nct, s, hits):
    ps = s["protocolSection"]
    conds = g(ps, "conditionsModule", "conditions") or []
    titles = [t for t in (g(ps, "identificationModule", "briefTitle"),
                          g(ps, "identificationModule", "officialTitle")) if t]
    outs = outcomes_of(ps)
    elig = g(ps, "eligibilityModule", "eligibilityCriteria")
    c = classify(conds, titles, outs, elig)
    start = g(ps, "statusModule", "startDateStruct", "date")
    if not in_window(start):
        c.update(group=None, excluded="start date outside window")
    phases = tuple(g(ps, "designModule", "phases") or [])
    locs = g(ps, "contactsLocationsModule", "locations") or []
    countries = sorted({l.get("country") for l in locs if l.get("country")})
    prim = [o for o in outs if o["level"] == "primary"]
    return {
        "nct_id": nct,
        "title": titles[0] if titles else None,
        "conditions": "; ".join(conds) or None,
        "group": c["group"],
        "groups_matched": "; ".join(c["groups"]) or None,
        "phase": PHASE_LABELS.get(phases, "/".join(phases)) if phases else None,
        "overall_status": g(ps, "statusModule", "overallStatus"),
        "start_date": start,
        "start_date_type": g(ps, "statusModule", "startDateStruct", "type"),
        "primary_completion_date": g(ps, "statusModule", "primaryCompletionDateStruct", "date"),
        "primary_completion_date_type": g(ps, "statusModule", "primaryCompletionDateStruct", "type"),
        "enrollment": g(ps, "designModule", "enrollmentInfo", "count"),
        "enrollment_type": g(ps, "designModule", "enrollmentInfo", "type"),
        "lead_sponsor": g(ps, "sponsorCollaboratorsModule", "leadSponsor", "name"),
        "sponsor_class": g(ps, "sponsorCollaboratorsModule", "leadSponsor", "class"),
        "countries": "; ".join(countries) or None,
        "why_stopped": g(ps, "statusModule", "whyStopped"),
        "results_posted": "yes" if s.get("hasResults") else "no",
        "results_first_post_date": g(ps, "statusModule", "resultsFirstPostDateStruct", "date"),
        "primary_outcomes": " | ".join(
            f"{o['measure']} [time frame: {o['time_frame']}]" if o["time_frame"] else str(o["measure"])
            for o in prim) or None,
        "n_primary_outcomes": len(prim),
        "cpsp_basis": c["cpsp_basis"],
        "cpsp_outcome_level": c["cpsp_level"],
        "chronicity_from": c["chronic_from"],
        "excluded_reason": c["excluded"],
        "review_note": c["notes"],
        "matched_queries": "; ".join(hits),
        "official_title": titles[1] if len(titles) > 1 else None,
    }


def median_iqr(x):
    x = pd.Series(x).dropna()
    if x.empty:
        return None
    q1, med, q3 = x.quantile([0.25, 0.5, 0.75]).tolist()
    return {"n": int(len(x)), "median": float(med), "q1": float(q1), "q3": float(q3)}


def fmt_miqr(m):
    if not m:
        return "–"
    return f"{m['median']:,.0f} ({m['q1']:,.0f}–{m['q3']:,.0f}); n = {m['n']:,}"


def crosstab_md(df, row, rows_order, col_label):
    """Markdown table: rows = categories, columns = groups, plus a total column."""
    cols = [c for c in GROUP_ORDER if c in set(df["group"])]
    head = f"| {col_label} | " + " | ".join(cols) + " | **Total** |"
    lines = [head, "|---|" + "---:|" * (len(cols) + 1)]
    for r in rows_order:
        sub = df[df[row] == r]
        if sub.empty:
            continue
        cells = [f"{(sub['group'] == c).sum():,}" for c in cols]
        lines.append(f"| {r} | " + " | ".join(cells) + f" | **{len(sub):,}** |")
    cells = [f"**{(df['group'] == c).sum():,}**" for c in cols]
    lines.append("| **Total** | " + " | ".join(cells) + f" | **{len(df):,}** |")
    return lines


def add_labels(df):
    """Readable phase, status and sponsor-class labels (missing stays 'Missing')."""
    df = df.copy()
    df["phase_label"] = df["phase"].fillna("Missing")
    df["status_label"] = df["overall_status"].map(lambda s: STATUS_LABELS.get(s, s) if pd.notna(s) else "Missing")
    df["sponsor_label"] = df["sponsor_class"].map(lambda s: SPONSOR_LABELS.get(s, s) if pd.notna(s) else "Missing")
    return df


def enrolment_stats(df):
    out = {}
    for k in GROUP_ORDER + ["All"]:
        sub = df if k == "All" else df[df["group"] == k]
        out[k] = {
            "all_types": median_iqr(sub["enrollment"]),
            "actual_only": median_iqr(sub.loc[sub["enrollment_type"] == "ACTUAL", "enrollment"]),
            "missing": int(sub["enrollment"].isna().sum()),
            "zero_recorded": int((sub["enrollment"] == 0).sum()),
        }
    return out


def summary_tables(df, enrol):
    """Markdown sections 1-4: group x phase, status, sponsor class, enrolment."""
    L = ["## 1. Trials by group and phase", ""]
    L += crosstab_md(df, "phase_label", PHASE_ORDER, "Phase")
    L += ["", "*Missing* = no phase recorded in the registry.", "",
          "## 2. Trials by overall status", ""]
    L += crosstab_md(df, "status_label", list(STATUS_LABELS.values()) + ["Missing"], "Status")
    L += ["", "*Unknown status* is the registry's label for a trial whose record has not been "
          "verified for more than two years.", "",
          "## 3. Trials by lead sponsor class", ""]
    L += crosstab_md(df, "sponsor_label", list(SPONSOR_LABELS.values()) + ["Missing"], "Sponsor class")
    L += ["", "*Sponsor class* is the registry's own classification of the lead sponsor.", "",
          "## 4. Planned or actual enrolment by group", "",
          "| Group | Median (IQR), all recorded counts | Median (IQR), actual counts only | Missing | Recorded as 0 |",
          "|---|---:|---:|---:|---:|"]
    for k in GROUP_ORDER + ["All"]:
        e = enrol[k]
        if e["all_types"] is None and e["missing"] == 0:
            continue  # group absent from this subset
        L.append(f"| {k} | {fmt_miqr(e['all_types'])} | {fmt_miqr(e['actual_only'])} | "
                 f"{e['missing']:,} | {e['zero_recorded']:,} |")
    L += ["",
          "*All recorded counts* mixes actual enrolment (finished or stopped trials) with "
          "estimated enrolment (trials still running). Withdrawn trials are recorded as 0 "
          "actual participants and are included as such. IQR uses linear interpolation "
          "(pandas default).", ""]
    return L


def main():
    pull_date = sys.argv[1] if len(sys.argv) > 1 else None
    meta, studies, hits = load_pull(pull_date)
    # Sensitivity run: chronicity from conditions/titles only (no inclusion criteria)
    rules.USE_ELIGIBILITY_FOR_CHRONICITY = False
    strict = pd.DataFrame([flatten(n, s, hits[n]) for n, s in studies.items()])
    rules.USE_ELIGIBILITY_FOR_CHRONICITY = True
    rows = [flatten(n, s, hits[n]) for n, s in studies.items()]
    allrows = pd.DataFrame(rows).sort_values("nct_id")
    inc = allrows[allrows["group"].notna()].copy()
    exc = allrows[allrows["group"].isna()].copy()

    (ROOT / "data").mkdir(exist_ok=True)
    keep = ["nct_id", "title", "conditions", "group", "groups_matched", "phase", "overall_status",
            "start_date", "start_date_type", "primary_completion_date", "primary_completion_date_type",
            "enrollment", "enrollment_type", "lead_sponsor", "sponsor_class", "countries",
            "why_stopped", "results_posted", "results_first_post_date", "primary_outcomes",
            "n_primary_outcomes", "cpsp_basis", "cpsp_outcome_level", "chronicity_from",
            "matched_queries"]
    inc[keep].to_csv(ROOT / "data" / "trials.csv", index=False)
    exc[["nct_id", "title", "conditions", "groups_matched", "excluded_reason", "review_note",
         "cpsp_basis", "matched_queries"]].to_csv(ROOT / "data" / "excluded.csv", index=False)

    # ---------------- numbers -------------------------------------------------
    inc = add_labels(inc)
    N = {
        "pull_date": meta["pull_date"],
        "api_version": meta["api_version"],
        "data_timestamp": meta["data_timestamp"],
        "data_date": (meta["data_timestamp"] or "")[:10],  # date ClinicalTrials.gov processed the data
        "queries": {q["key"]: {"n": q["n"], "missing_start_not_pulled": q["missing_start"]}
                    for q in meta["queries"]},
        "n_queries": len(meta["queries"]),
        "pulled_sum_over_queries": sum(q["n"] for q in meta["queries"]),
        "pulled_unique": len(allrows),
        "included": len(inc),
        "excluded": len(exc),
        "excluded_by_reason": exc["excluded_reason"].value_counts().to_dict(),
        "by_group": {k: int((inc["group"] == k).sum()) for k in GROUP_ORDER},
        "groups_matched_any": {k: int(inc["groups_matched"].str.contains(k).sum()) for k in GROUPS},
        "by_phase": inc["phase_label"].value_counts().to_dict(),
        "by_status": inc["status_label"].value_counts().to_dict(),
        "by_sponsor_class": inc["sponsor_label"].value_counts().to_dict(),
        "cpsp_basis": inc.loc[inc["groups_matched"].str.contains("CPSP"), "cpsp_basis"]
                         .value_counts().to_dict(),
        "cpsp_outcome_level": inc.loc[inc["groups_matched"].str.contains("CPSP"), "cpsp_outcome_level"]
                                 .value_counts().to_dict(),
        "chronicity_from": inc["chronicity_from"].value_counts().to_dict(),
        "sensitivity_no_inclusion_criteria": {
            "included": int(strict["group"].notna().sum()),
            "by_group": {k: int((strict["group"] == k).sum()) for k in GROUP_ORDER},
        },
        "start_date_type": inc["start_date_type"].fillna("Missing").value_counts().to_dict(),
        "missing": {c: int(inc[c].isna().sum()) for c in
                    ["phase", "overall_status", "start_date", "primary_completion_date",
                     "enrollment", "enrollment_type", "lead_sponsor", "sponsor_class",
                     "countries", "primary_outcomes"]},
        "enrolment": enrolment_stats(inc),
    }
    OUT.mkdir(exist_ok=True)

    # ---------------- summary_table.md ----------------------------------------
    L = [
        "# Chronic pain trials on ClinicalTrials.gov, 2015–2025: summary tables",
        "",
        f"Data from ClinicalTrials.gov (API v2, version {N['api_version']}), pulled {N['pull_date']}. "
        f"Interventional studies with a start date from 1 Jan 2015 to 31 Dec 2025. "
        f"{N['pulled_unique']:,} unique trials were retrieved by the searches; "
        f"**{N['included']:,}** met the inclusion rules (see `src/rules.py`).",
        "",
        "Group key: " + "; ".join(f"**{k}** = {v}" for k, v in GROUP_LABELS.items()) + ".",
        "A trial matching two or more groups is counted once, under *Multiple*.",
        "",
    ]
    L += summary_tables(inc, N["enrolment"])
    (OUT / "summary_table.md").write_text("\n".join(L))

    # ---------------- review files ---------------------------------------------
    rev = OUT / "review"
    rev.mkdir(exist_ok=True)
    cols = ["nct_id", "group", "groups_matched", "cpsp_basis", "cpsp_outcome_level",
            "conditions", "title", "start_date", "phase"]
    inc.sample(30, random_state=SEED)[cols].to_csv(rev / "sample_30_included.csv", index=False)

    # Borderline exclusions: near-misses, and group matches removed by an
    # exclusion rule. A fixed quota per bucket so every kind of decision is seen.
    near = exc[(exc["groups_matched"].notna()) | (exc["review_note"].notna())].copy()
    near["bucket"] = near.apply(
        lambda r: "group matched, then excluded: " + r["excluded_reason"]
        if pd.notna(r["groups_matched"]) else r["review_note"].split("; ")[0], axis=1)
    N2 = near["bucket"].value_counts().to_dict()
    quota = {"musculoskeletal pain without evidence of chronicity": 4,
             "radiculopathy/sciatica without evidence of chronicity": 2,
             "osteoarthritis without a pain word": 2,
             "orofacial/jaw musculoskeletal pain": 1,
             "dental/orofacial trial matched CPSP": 1,
             "group matched, then excluded: headache or migraine": 3,
             "group matched, then excluded: cancer pain (incl. chemotherapy/radiotherapy-induced)": 3,
             "group matched, then excluded: cancer pain (cancer condition, non-surgical pain)": 1,
             "group matched, then excluded: acute postoperative pain": 3}
    picked = pd.concat([near[near["bucket"] == b].sample(min(k, (near["bucket"] == b).sum()),
                                                          random_state=SEED)
                        for b, k in quota.items()])
    picked[["nct_id", "bucket", "groups_matched", "conditions", "title"]].to_csv(
        rev / "borderline_20_excluded.csv", index=False)
    N["borderline_buckets"] = N2
    (OUT / "numbers.json").write_text(json.dumps(N, indent=2, default=int))

    print(f"pulled unique {N['pulled_unique']:,}; included {N['included']:,}; excluded {N['excluded']:,}")
    print("by group:", N["by_group"])
    print("excluded by reason:", N["excluded_by_reason"])
    print("borderline buckets:", N2)


if __name__ == "__main__":
    main()
