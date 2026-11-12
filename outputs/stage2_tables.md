# Stage 2 tables

Included trials: 5,050. Data from ClinicalTrials.gov, pulled 2026-11-12.

## Intervention types

From the registry's interventions field. A trial can list several types. 0 trials list none.

| Type | Trials listing it | % of trials |
|---|---:|---:|
| OTHER | 2,132 | 42.2 |
| DEVICE | 1,116 | 22.1 |
| DRUG | 1,071 | 21.2 |
| PROCEDURE | 647 | 12.8 |
| BEHAVIORAL | 641 | 12.7 |
| DIETARY_SUPPLEMENT | 75 | 1.5 |
| BIOLOGICAL | 73 | 1.4 |
| DIAGNOSTIC_TEST | 64 | 1.3 |
| COMBINATION_PRODUCT | 34 | 0.7 |
| RADIATION | 15 | 0.3 |
| GENETIC | 11 | 0.2 |

At least one drug, biological or combination product: 1,153 (22.8%); none: 3,897 (77.2%). 313 trials with phase 'Not applicable' still list a drug-type intervention.

## Why trials stopped (terminated, withdrawn and suspended trials)

n = 324. Main reason by the precedence in `src/stop_reasons.py`; 'Any mention' counts every category a reason touches.

| Main reason | Terminated | Withdrawn | Suspended | Total | % | Any mention |
|---|---:|---:|---:|---:|---:|---:|
| COVID-19 | 20 | 13 | 2 | 35 | 10.8 | 35 |
| Safety or futility | 23 | 2 | 0 | 25 | 7.7 | 25 |
| Low accrual | 76 | 34 | 1 | 111 | 34.3 | 131 |
| Funding | 19 | 21 | 1 | 41 | 12.7 | 53 |
| Sponsor or business decision | 18 | 7 | 2 | 27 | 8.3 | 44 |
| Site or investigator | 7 | 23 | 1 | 31 | 9.6 | 37 |
| Other | 14 | 30 | 3 | 47 | 14.5 | – |
| Not stated | 3 | 3 | 1 | 7 | 2.2 | – |

16 stated reasons matched no keyword and are counted as Other; they are listed in `outputs/review/stop_reasons_unclassified.csv`.

## Results posted on ClinicalTrials.gov

Completed or terminated trials whose primary completion date is on or before 2025-11-12 (12 months before the pull date). A month-only date counts as the last day of that month. 'Results posted' means a results section is posted on ClinicalTrials.gov; it is not a measure of legal compliance, because the duty to post applies only to some trials.

Overall: **468 of 2,849 (16.4%)**. 222 completed/terminated trials finished too recently to count; 1 eligible trials still show an estimated primary completion date.

| Lead sponsor class | Eligible | Results posted | % |
|---|---:|---:|---:|
| Other (universities, hospitals, non-profits) | 2,334 | 254 | 10.9 |
| Industry | 407 | 183 | 45.0 |
| Other government | 52 | 2 | 3.8 |
| Other US federal | 49 | 29 | 59.2 |
| Network | 6 | 0 | 0.0 |
| Individual | 1 | 0 | 0.0 |

| Group | Eligible | Results posted | % |
|---|---:|---:|---:|
| CPSP | 212 | 27 | 12.7 |
| Fibromyalgia | 315 | 44 | 14.0 |
| MSK | 1,792 | 275 | 15.3 |
| Neuropathic | 397 | 93 | 23.4 |
| CRPS | 32 | 7 | 21.9 |
| Multiple | 101 | 22 | 21.8 |

## Primary outcomes mapped to IMMPACT core domains

11,916 primary outcome measures from 5,050 trials. Rules in `src/immpact.py`.

| Domain | Measures | % of measures | Trials with ≥1 such primary outcome | % of trials |
|---|---:|---:|---:|---:|
| Pain intensity | 5,448 | 45.7 | 3,695 | 73.2 |
| Physical functioning | 2,805 | 23.5 | 1,796 | 35.6 |
| Emotional functioning | 837 | 7.0 | 534 | 10.6 |
| Improvement and satisfaction | 185 | 1.6 | 147 | 2.9 |
| Symptoms and adverse events | 435 | 3.7 | 280 | 5.5 |
| Participant disposition | 227 | 1.9 | 148 | 2.9 |
| *Spans several domains* | 1,170 | 9.8 | | |
| *Matches none* | 3,432 | 28.8 | 644 | 12.8 |

## Asia compared with trials sited only outside Asia

| | Trials | Industry-led % | Median enrolment, planned or actual (IQR) |
|---|---:|---:|---:|
| Any site in the nine Asian places | 420 | 18.8 | 90 (50–175) |
| All listed sites outside Asia | 4,297 | 11.3 | 54 (32–90) |

333 trials list no site country and are in neither row.
