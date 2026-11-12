# Chronic pain trials on ClinicalTrials.gov, 2015–2025

**The question.** Which interventional trials in five chronic pain conditions started between 2015-01-01 and 2025-12-31, who runs them, why do they stop, are results posted, and do outcomes cover the IMMPACT core domains (an expert consensus on what pain trials should measure)?

**Data and method**
- ClinicalTrials.gov API v2 (version 2.0.5), pulled 2026-11-12 (registry data dated 2026-11-10): 11 searches, 12,413 unique trials.
- Keyword rules on registry text kept 5,050 trials in 5 groups, excluding headache, cancer pain and acute postoperative pain.
- Percentages are of all 5,050 trials unless stated; every number comes from `outputs/numbers.json`.

**Five key findings**
- **Musculoskeletal pain dominates.** Chronic low back and other musculoskeletal pain makes up 60.5% (3,054); complex regional pain syndrome only 71; chronic postsurgical pain 528, of which 397 are prevention studies. Starts rose from 291 in 2015 to 678 in 2025, including planned starts ([figure](fig1_trials_per_year.png)).
- **Mostly small, academic, non-drug trials.** Only 22.8% list a drug or biological; the rest test devices, procedures, exercise or psychological care. Universities, hospitals or non-profits lead 84.2%, industry 12.0%. Median planned or actual enrolment is 57 (interquartile range, the middle half: 33–99).
- **Low accrual is the commonest stated reason to stop.** Of 313 trials stopped early (180 terminated after enrolment began, 133 withdrawn before it), 110 (35.1%) cite low accrual (too few recruits), 40 (12.8%) funding and 33 (10.5%) COVID-19; reasons as stated, sorted by keyword rules ([figure](fig2_stop_reasons.png)).
- **Results are rarely posted.** Of 2,849 completed or terminated trials with primary completion at least 12 months before the pull, 16.4% have results posted: 45.0% of 407 industry-led and 10.9% of 2,334 academic-led trials. Not a compliance rate: the legal duty covers only some trials.
- **Primary outcomes centre on pain intensity.** 73.2% of trials have a pain-intensity primary outcome and 35.6% physical functioning, but only 10.6% emotional functioning and 2.9% participant ratings of improvement or satisfaction. Of 11,916 primary outcome measures, 28.8% fit no IMMPACT domain (e.g. opioid use).

**HK/Asia.** 420 trials (8.3%) have a site in the nine Asian places in scope, led by mainland China (174), South Korea (89) and Taiwan (65). Hong Kong has 41: 31 musculoskeletal, 7 postsurgical; 35 academic-led (PolyU 17, HKU 7, CUHK 7). Compared with 4,297 trials sited only outside Asia, they are larger (median enrolment 90 vs 54) and more often industry-led (18.8% vs 11.3%).

**Limitations.** Registry data only (publications not checked); many mainland Chinese trials register only on ChiCTR, so China is under-counted; inconsistent coding means keyword rules misclassify some trials; fields are self-reported and often stale (18.7% have "unknown" status); data are as of 2026-11-12.

**Next steps.** Add ChiCTR and WHO registry data; hand-check a random sample to measure rule accuracy; link trials to publications.
