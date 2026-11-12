# Chronic pain trials on ClinicalTrials.gov, 2015–2025

**The question.** Which interventional trials in five chronic pain conditions started between 2015-01-01 and 2025-12-31, who runs them, why do they stop, are their results posted, and do their primary outcomes match the IMMPACT core domains?

**Data and method**
- ClinicalTrials.gov API v2 (version 2.0.5), pulled 2026-11-12 (registry data dated 2026-11-10): 11 searches, 12,413 unique trials.
- Keyword rules on conditions, titles, outcomes and inclusion criteria kept 5,043 trials in 5 groups; headache, cancer pain and acute postoperative pain were excluded.
- Every number below is written by the code to `outputs/numbers.json`.

**Five key findings**
- **Musculoskeletal pain dominates.** Chronic low back and other musculoskeletal pain makes up 59.0% of trials (2,975); complex regional pain syndrome only 71. Starts rose from 291 in 2015 to 676 in 2025, a count that includes planned starts ([figure](fig1_trials_per_year.png)).
- **Small, academic, mostly non-drug trials.** 81.3% have no drug phase (devices, procedures, exercise, psychological care); 84.7% are led by universities, hospitals or non-profits and 11.4% by industry. Median enrolment is 58 (IQR 33–99).
- **Low accrual is the commonest reason to stop.** Of 327 terminated, withdrawn or suspended trials, 113 (34.6%) stopped mainly for low accrual, 42 (12.8%) for funding and 34 (10.4%) for COVID-19 ([figure](fig2_stop_reasons.png)).
- **Results are rarely posted.** Of 2,834 completed or terminated trials whose primary completion was at least 12 months before the pull, 16.2% have results posted: 44.6% for industry and 10.9% for universities, hospitals and non-profits. This is not a compliance rate: the legal duty to post covers only some trials.
- **Primary outcomes centre on pain intensity.** 70.2% of trials have a pain-intensity primary outcome and 35.3% physical functioning, but only 8.5% emotional functioning and 2.9% participant ratings of improvement or satisfaction. 28.8% of primary outcome measures fit no core domain (e.g. pressure pain thresholds, opioid use).

**HK/Asia.** 424 trials (8.4%) have a site in Hong Kong, mainland China, Macau, Taiwan, Japan, South Korea, Singapore, Malaysia or Thailand, led by mainland China (181), South Korea (88) and Taiwan (66). Hong Kong has 39: 28 musculoskeletal and 8 postsurgical; 34 are university- or hospital-led (PolyU 16, HKU 7, CUHK 7). Asian trials are larger (median enrolment 90 against 58) and more often industry-led (17.9% against 11.4%).

**Limitations**
- Registry data only; publications were not checked.
- Many mainland Chinese trials register only on ChiCTR, so China is under-counted.
- Condition coding is inconsistent, so keyword rules misclassify some trials (borderline cases are listed).
- Fields are self-reported and often stale: 19.0% have "unknown" status.
- Data are as of 2026-11-12.

**Next steps.** Add ChiCTR and the WHO registry platform; hand-check a random sample to measure rule accuracy; link completed trials to publications.
