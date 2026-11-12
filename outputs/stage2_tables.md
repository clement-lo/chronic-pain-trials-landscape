# Stage 2 tables

Included trials: 5,043. Data from ClinicalTrials.gov, pulled 2026-11-12.

## Why trials stopped (terminated, withdrawn and suspended trials)

n = 327. Main reason by the precedence in `src/stop_reasons.py`; 'Any mention' counts every category a reason touches.

| Main reason | Terminated | Withdrawn | Suspended | Total | % | Any mention |
|---|---:|---:|---:|---:|---:|---:|
| COVID-19 | 19 | 13 | 2 | 34 | 10.4 | 34 |
| Safety or futility | 23 | 2 | 0 | 25 | 7.6 | 25 |
| Low accrual | 79 | 33 | 1 | 113 | 34.6 | 134 |
| Funding | 19 | 22 | 1 | 42 | 12.8 | 53 |
| Sponsor or business decision | 17 | 7 | 2 | 26 | 8.0 | 43 |
| Site or investigator | 7 | 25 | 1 | 33 | 10.1 | 41 |
| Other | 14 | 30 | 3 | 47 | 14.4 | – |
| Not stated | 2 | 4 | 1 | 7 | 2.1 | – |

16 stated reasons matched no keyword and are counted as Other; they are listed in `outputs/review/stop_reasons_unclassified.csv`.

## Results posted on ClinicalTrials.gov

Completed or terminated trials whose primary completion date is on or before 2025-11-12 (12 months before the pull date). A month-only date counts as the last day of that month. 'Results posted' means a results section is posted on ClinicalTrials.gov; it is not a measure of legal compliance, because the duty to post applies only to some trials.

Overall: **458 of 2,834 (16.2%)**. 223 completed/terminated trials finished too recently to count; 1 eligible trials still show an estimated primary completion date.

| Lead sponsor class | Eligible | Results posted | % |
|---|---:|---:|---:|
| Other (universities, hospitals, non-profits) | 2,336 | 254 | 10.9 |
| Industry | 388 | 173 | 44.6 |
| Other government | 53 | 2 | 3.8 |
| Other US federal | 50 | 29 | 58.0 |
| Network | 6 | 0 | 0.0 |
| Individual | 1 | 0 | 0.0 |

| Group | Eligible | Results posted | % |
|---|---:|---:|---:|
| CPSP | 244 | 32 | 13.1 |
| Fibromyalgia | 314 | 44 | 14.0 |
| MSK | 1,741 | 260 | 14.9 |
| Neuropathic | 397 | 90 | 22.7 |
| CRPS | 32 | 7 | 21.9 |
| Multiple | 106 | 25 | 23.6 |

## Primary outcomes mapped to IMMPACT core domains

11,855 primary outcome measures from 5,043 trials. Rules in `src/immpact.py`.

| Domain | Measures | % of measures | Trials with ≥1 such primary outcome | % of trials |
|---|---:|---:|---:|---:|
| Pain intensity | 5,064 | 42.7 | 3,542 | 70.2 |
| Physical functioning | 2,783 | 23.5 | 1,780 | 35.3 |
| Emotional functioning | 680 | 5.7 | 429 | 8.5 |
| Improvement and satisfaction | 184 | 1.6 | 146 | 2.9 |
| Symptoms and adverse events | 419 | 3.5 | 268 | 5.3 |
| Participant disposition | 225 | 1.9 | 147 | 2.9 |
| *Spans several domains* | 824 | 7.0 | | |
| *Matches none* | 3,410 | 28.8 | 659 | 13.1 |
