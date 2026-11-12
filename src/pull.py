"""Step 1: pull study records from the ClinicalTrials.gov API v2 and cache them.

Usage:
    .venv/bin/python src/pull.py            # pull today's data (re-uses today's cache)
    .venv/bin/python src/pull.py --refresh  # re-download even if cached

Raw JSON pages go to data/raw/<pull date>/<query key>/page_NNN.json (git-ignored).
The exact query strings, counts and pull date are written to data/query_log.md.
If any request fails after retries, the script stops with an error: nothing
is silently skipped.
"""

import argparse
import datetime as dt
import json
import sys
import time
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent))
from config import (API_BASE, BASE_FILTER, FIELDS, MISSING_START_FILTER,  # noqa: E402
                    PAGE_SIZE, QUERIES)

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
PAUSE = 1.3        # seconds between requests (the API allows ~50 per minute)
RETRIES = 4


def get(url, params):
    """GET with retries. Raises on persistent failure instead of working around it."""
    last = None
    for attempt in range(1, RETRIES + 1):
        try:
            r = requests.get(url, params=params, timeout=120)
            if r.status_code == 200:
                time.sleep(PAUSE)
                return r
            last = f"HTTP {r.status_code}: {r.text[:300]}"
            if r.status_code in (400, 404):
                break  # a bad query will not fix itself
        except requests.RequestException as e:
            last = repr(e)
        time.sleep(PAUSE * 2 ** attempt)
    raise RuntimeError(f"API request failed after {attempt} attempt(s): {url} {params}\n{last}")


def pull_query(key, param, expr, outdir):
    """Download every page for one query. Returns (studies on disk, totalCount)."""
    outdir.mkdir(parents=True, exist_ok=True)
    params = {
        param: expr,
        "filter.advanced": BASE_FILTER,
        "fields": "|".join(FIELDS),
        "pageSize": PAGE_SIZE,
        "countTotal": "true",
        "format": "json",
    }
    page, n, total, token = 1, 0, None, None
    while True:
        p = dict(params)
        if token:
            p["pageToken"] = token
            p.pop("countTotal")
        data = get(f"{API_BASE}/studies", p).json()
        if total is None:
            total = data.get("totalCount")
        (outdir / f"page_{page:03d}.json").write_text(json.dumps(data))
        n += len(data.get("studies", []))
        token = data.get("nextPageToken")
        if not token:
            break
        page += 1
    if total is not None and n != total:
        raise RuntimeError(f"{key}: downloaded {n} studies but the API reported {total}")
    return n, total


def count_missing_start(param, expr):
    """How many interventional studies match the query but have no start date."""
    params = {param: expr, "filter.advanced": MISSING_START_FILTER,
              "countTotal": "true", "pageSize": 1, "fields": "NCTId"}
    return get(f"{API_BASE}/studies", params).json().get("totalCount")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--refresh", action="store_true")
    args = ap.parse_args()

    pull_date = dt.date.today().isoformat()
    day_dir = RAW / pull_date
    meta_path = day_dir / "pull_meta.json"
    if meta_path.exists() and not args.refresh:
        print(f"Using cached pull in {day_dir} (use --refresh to re-download)")
        return

    version = get(f"{API_BASE}/version", {}).json()
    rows = []
    for key, (param, expr, group) in QUERIES.items():
        n, total = pull_query(key, param, expr, day_dir / key)
        missing = count_missing_start(param, expr)
        rows.append({"key": key, "group": group, "param": param, "expr": expr,
                     "n": n, "total": total, "missing_start": missing})
        print(f"{key:28s} {n:6d} studies  (no start date, not pulled: {missing})")

    meta = {
        "pull_date": pull_date,
        "pulled_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "api_version": version.get("apiVersion"),
        "data_timestamp": version.get("dataTimestamp"),
        "base_filter": BASE_FILTER,
        "missing_start_filter": MISSING_START_FILTER,
        "fields": FIELDS,
        "queries": rows,
    }
    meta_path.write_text(json.dumps(meta, indent=2))
    write_query_log(meta)


def write_query_log(meta):
    lines = [
        "# Query log",
        "",
        f"- **Pull date:** {meta['pull_date']} (UTC time {meta['pulled_at_utc']})",
        f"- **API:** ClinicalTrials.gov API v2, version {meta['api_version']}; "
        f"registry data timestamp {meta['data_timestamp']}",
        f"- **Endpoint:** `GET {API_BASE}/studies`, `pageSize={PAGE_SIZE}`, "
        "`format=json`, all pages followed via `nextPageToken`",
        f"- **Filter applied to every query** (`filter.advanced`): `{meta['base_filter']}`",
        f"- **Fields requested** (`fields`): `{'|'.join(meta['fields'])}`",
        "",
        "Each multi-word term is in quotes so the API searches the exact phrase "
        "(with its registry synonyms) rather than any one of its words. "
        "`query.cond` searches the condition, title, keyword and MeSH fields; "
        "`query.outc` searches outcome measures. These queries only cast the net: "
        "`src/rules.py` decides which trials are kept and which group they join.",
        "",
        "| Query key | Group | Parameter | Studies returned | Interventional, same query, no start date (not pulled) |",
        "|---|---|---|---:|---:|",
    ]
    for r in meta["queries"]:
        lines.append(f"| `{r['key']}` | {r['group']} | `{r['param']}` | {r['n']:,} | {r['missing_start']:,} |")
    lines += ["", "## Query strings", ""]
    for r in meta["queries"]:
        lines += [f"### `{r['key']}` ({r['param']})", "", "```", r["expr"], "```", ""]
    (ROOT / "data" / "query_log.md").write_text("\n".join(lines))


if __name__ == "__main__":
    main()
