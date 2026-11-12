# Chronic pain trials landscape

A reproducible map of interventional chronic pain trials registered on ClinicalTrials.gov with a start date from 2015-01-01 to 2025-12-31, in 5 condition groups: chronic postsurgical pain, fibromyalgia, chronic low back and other musculoskeletal pain, neuropathic pain, and complex regional pain syndrome. Headache and migraine, cancer pain and acute postoperative pain are excluded.

Data from ClinicalTrials.gov, accessed 2026-11-12; the registry data are as processed by ClinicalTrials.gov on 2026-11-10. This is a snapshot: ClinicalTrials.gov is updated daily, so rerun the pipeline for current data.

The one-page results are in [outputs/summary.md](outputs/summary.md).

## How the pipeline works

- **Pull** (`src/pull.py`). Sends 11 searches to the ClinicalTrials.gov API v2, each limited to interventional studies that started in the date window. Every page of every response is saved unchanged in `data/raw/<pull date>/`, and the exact search strings, counts and pull date are written to `data/query_log.md`. If a request fails, the script stops rather than skipping it.
- **Build** (`src/build.py`). Merges the searches, keeps one record per NCT ID, and applies the rules in `src/rules.py` to decide whether each trial is in scope and which group it joins. Writes `data/trials.csv`, `data/excluded.csv` (with the reason for every exclusion), `outputs/summary_table.md` and review samples in `outputs/review/`.
- **Analyse** (`src/analyse.py`). Adds the HK/Asia subset, sorts the stated reasons for stopping (`src/stop_reasons.py`), works out the share of finished trials with results posted, and maps each primary outcome to the IMMPACT core domains (`src/immpact.py`).
- **Figures** (`src/figures.py`). Draws the two figures as PNG (300 dpi) and SVG in colour-blind-safe colours.
- **Report** (`src/report.py`). Fills `templates/summary.md.tmpl` and `templates/README.md.tmpl` with values from `outputs/numbers.json`, so the text cannot drift from the data. To change the wording, edit the templates, not the generated files.
- **Check** (`tests/check_numbers.py`). Confirms that every number in `outputs/summary.md` and this README appears in `outputs/numbers.json`, that both files match their templates, that the summary stays within 450 words, and that both figures exist.

## The rules in brief

- A trial joins a group when its condition list or title names the condition. Musculoskeletal and radicular pain also need evidence that the pain is chronic: the word "chronic" or "persistent", a diagnosis of osteoarthritis, or inclusion criteria requiring pain for at least 3 months (12 weeks).
- A surgical trial counts as chronic postsurgical pain only when its condition or an outcome refers to chronic or persistent pain, or it measures pain at a follow-up 12 weeks or more after surgery.
- Headache and migraine, cancer pain (including chemotherapy-induced neuropathy), dental and jaw pain, and acute postoperative pain are excluded, and these exclusions override group matches.
- A trial matching two or more groups is counted once, as "Multiple".
- Missing registry fields are left missing and counted, never filled in.
- Stop reasons and outcome domains are sorted with keyword rules; reasons and measures that match nothing are listed in `outputs/review/` rather than forced into a category.

## How to rerun

You need Python (tested with `python3.12`) and an internet connection for a fresh pull.

```bash
python3.12 -m venv .venv
.venv/bin/pip install -r requirements.txt
./run_pipeline.sh                # pull today's data, then rebuild everything
./run_pipeline.sh 2026-11-12     # rebuild from a pull already saved in data/raw/
```

The registry changes every day, so a new pull gives slightly different numbers. Raw downloads are not committed to git; keep `data/raw/<pull date>/` to reproduce a given pull exactly.

## Outputs

- `data/trials.csv`: included trials, one row per NCT ID.
- `data/excluded.csv`: every retrieved trial that was not included, with the reason.
- `data/query_log.md`: search strings, counts and pull date.
- `outputs/summary.md`: the one-page summary.
- `outputs/summary_table.md` and `outputs/summary_table_asia.md`: counts by group, phase, status and sponsor class, and enrolment.
- `outputs/stage2_tables.md`: stop reasons, results posted and IMMPACT tables.
- `outputs/hk_trials.md`: every included trial with a Hong Kong site.
- `outputs/stop_reasons.csv` and `outputs/immpact_mapping.csv`: the classification of every stopped trial and every primary outcome.
- `outputs/fig1_trials_per_year` and `outputs/fig2_stop_reasons`: the figures, as PNG and SVG.
- `outputs/numbers.json`: every number quoted in the text.

## How the registry data were modified

ClinicalTrials.gov asks anyone who redistributes its data to describe their changes. The files in `data/` and `outputs/` differ from the registry as follows.

- **Selection.** Only interventional studies with a start date in the window, retrieved by the searches in `data/query_log.md` and kept by the rules in `src/rules.py`. Every retrieved study that was not kept is listed in `data/excluded.csv` with the reason.
- **Fields.** Only the fields named in `data/query_log.md` were requested, and `data/trials.csv` keeps a subset of them.
- **Format.** Lists (conditions, countries, primary outcomes) are joined into one cell; site countries are de-duplicated and sorted; phase codes are turned into labels such as `Phase 1/2`; each primary outcome is written as its measure followed by its time frame; `results_posted` is the registry's own results flag written as yes or no.
- **Added by this project, not by the registry.** The condition group and every group matched, why a trial counts as chronic postsurgical pain, where its chronicity came from, which searches found it, the stop-reason categories, the IMMPACT domains and the review notes.
- **Not changed.** All other values are copied as published, including spelling. Missing values are left blank and counted; nothing is filled in.

## Licence, data rights and credit

- **Code:** MIT licence (see `LICENSE`). The licence covers the code only, not the trial data.
- **Data:** from ClinicalTrials.gov, a United States Government database run by the National Library of Medicine. This project claims no rights in the data. Some registry content may be subject to the copyright of third parties, as the ClinicalTrials.gov terms and conditions note.
- **Credit:** Data from ClinicalTrials.gov, accessed 2026-11-12.
- **No warranty:** this is an analysis of registry records, not clinical guidance, and the classifications come from keyword rules that make some errors.
