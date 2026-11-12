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

- A trial joins a group when its condition list or title names the condition. Musculoskeletal and radicular pain also need evidence that the pain is chronic: the word "chronic" or "persistent", or inclusion criteria requiring pain for at least 3 months (12 weeks). Osteoarthritis counts when the condition, title or inclusion criteria mention pain (osteoarthritis pain is chronic by definition), unless the trial enrols people scheduled for surgery.
- Chronic postsurgical pain must last 3 months or more, by one of two routes. *Treatment* trials enrol people with an established postsurgical pain condition named in the condition or title (for example failed back surgery syndrome or post-mastectomy pain syndrome) and are not run around a coming operation. *Prevention* trials are run around surgery and count only if an outcome on postsurgical, chronic or persistent pain, or a pain score, is measured 12 weeks or more after surgery. Perioperative trials that measure pain only earlier are excluded as acute postoperative pain.
- Headache and migraine, cancer pain (including chemotherapy-induced neuropathy), dental and jaw pain, and acute postoperative pain are excluded, and these exclusions override group matches.
- A trial matching two or more groups is counted once, as "Multiple".
- Missing registry fields are left missing and counted, never filled in.
- Stop reasons are taken as stated in the registry and sorted by keyword rules. *Withdrawn* means stopped before anyone enrolled, *terminated* means stopped after enrolment began, and *suspended* means paused; the figure and summary use terminated and withdrawn trials only.
- Primary outcomes are mapped to the core outcome domains recommended by IMMPACT (the Initiative on Methods, Measurement, and Pain Assessment in Clinical Trials). Named composite instruments such as WOMAC, the Brief Pain Inventory and the Fibromyalgia Impact Questionnaire count for every domain they report.
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
- **Format.** Lists (conditions, countries, intervention types, primary outcomes) are joined into one cell; site countries and intervention types are de-duplicated and sorted; phase codes are turned into labels such as `Phase 1/2`; each primary outcome is written as its measure followed by its time frame; `results_posted` is the registry's own results flag written as yes or no.
- **Added by this project, not by the registry.** The condition group and every group matched, whether a postsurgical pain trial is a treatment or a prevention study and why it qualifies, where its chronicity came from, which searches found it, the stop-reason categories, the IMMPACT domains and the review notes.
- **Not changed.** All other values are copied as published, including spelling. Missing values are left blank and counted; nothing is filled in.

## Licence, data rights and credit

- **Code:** MIT licence (see `LICENSE`). The licence covers the code only, not the trial data.
- **Data:** from ClinicalTrials.gov, a United States Government database run by the National Library of Medicine. This project claims no rights in the data. Some registry content may be subject to the copyright of third parties, as the ClinicalTrials.gov terms and conditions note.
- **No endorsement:** this is an independent project. It is not endorsed by, affiliated with or reviewed by the US National Library of Medicine, the National Institutes of Health or ClinicalTrials.gov.
- **Credit:** Data from ClinicalTrials.gov, accessed 2026-11-12.
- **No warranty:** this is an analysis of registry records, not clinical guidance, and the classifications come from keyword rules that make some errors.
