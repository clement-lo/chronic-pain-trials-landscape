# Chronic pain trials on ClinicalTrials.gov, 2015–2025: summary tables

Data from ClinicalTrials.gov (API v2, version 2.0.5), pulled 2026-11-12. Interventional studies with a start date from 1 Jan 2015 to 31 Dec 2025. 12,413 unique trials were retrieved by the searches; **5,043** met the inclusion rules (see `src/rules.py`).

Group key: **CPSP** = Chronic postsurgical pain; **Fibromyalgia** = Fibromyalgia; **MSK** = Chronic low back & other musculoskeletal pain; **Neuropathic** = Neuropathic pain; **CRPS** = Complex regional pain syndrome; **Multiple** = Multiple groups.
A trial matching two or more groups is counted once, under *Multiple*.

## 1. Trials by group and phase

| Phase | CPSP | Fibromyalgia | MSK | Neuropathic | CRPS | Multiple | **Total** |
|---|---:|---:|---:|---:|---:|---:|---:|
| Early phase 1 | 8 | 5 | 18 | 8 | 2 | 5 | **46** |
| Phase 1 | 4 | 5 | 58 | 46 | 1 | 6 | **120** |
| Phase 1/2 | 1 | 3 | 25 | 15 | 0 | 3 | **47** |
| Phase 2 | 15 | 22 | 99 | 100 | 2 | 12 | **250** |
| Phase 2/3 | 12 | 5 | 24 | 10 | 1 | 3 | **55** |
| Phase 3 | 33 | 15 | 91 | 49 | 6 | 3 | **197** |
| Phase 4 | 83 | 11 | 79 | 31 | 4 | 15 | **223** |
| Not applicable | 350 | 452 | 2,577 | 501 | 55 | 165 | **4,100** |
| Missing | 0 | 0 | 4 | 1 | 0 | 0 | **5** |
| **Total** | **506** | **518** | **2,975** | **761** | **71** | **212** | **5,043** |

*Missing* = no phase recorded in the registry.

## 2. Trials by overall status

| Status | CPSP | Fibromyalgia | MSK | Neuropathic | CRPS | Multiple | **Total** |
|---|---:|---:|---:|---:|---:|---:|---:|
| Completed | 236 | 316 | 1,812 | 374 | 31 | 108 | **2,877** |
| Recruiting | 71 | 53 | 267 | 110 | 11 | 27 | **539** |
| Not yet recruiting | 11 | 8 | 77 | 19 | 3 | 4 | **122** |
| Active, not recruiting | 21 | 16 | 103 | 24 | 1 | 9 | **174** |
| Enrolling by invitation | 3 | 6 | 28 | 7 | 2 | 2 | **48** |
| Terminated | 28 | 14 | 74 | 52 | 5 | 7 | **180** |
| Withdrawn | 17 | 10 | 63 | 32 | 2 | 12 | **136** |
| Suspended | 0 | 3 | 4 | 4 | 0 | 0 | **11** |
| Unknown status | 119 | 92 | 547 | 139 | 16 | 43 | **956** |
| **Total** | **506** | **518** | **2,975** | **761** | **71** | **212** | **5,043** |

*Unknown status* is the registry's label for a trial whose record has not been verified for more than two years.

## 3. Trials by lead sponsor class

| Sponsor class | CPSP | Fibromyalgia | MSK | Neuropathic | CRPS | Multiple | **Total** |
|---|---:|---:|---:|---:|---:|---:|---:|
| Industry | 10 | 34 | 357 | 155 | 6 | 15 | **577** |
| Other (universities, hospitals, non-profits) | 472 | 464 | 2,518 | 573 | 60 | 185 | **4,272** |
| Other US federal | 5 | 7 | 50 | 7 | 1 | 6 | **76** |
| Other government | 18 | 12 | 45 | 21 | 3 | 5 | **104** |
| Network | 1 | 1 | 4 | 3 | 1 | 0 | **10** |
| Individual | 0 | 0 | 1 | 2 | 0 | 1 | **4** |
| **Total** | **506** | **518** | **2,975** | **761** | **71** | **212** | **5,043** |

*Sponsor class* is the registry's own classification of the lead sponsor.

## 4. Planned or actual enrolment by group

| Group | Median (IQR), all recorded counts | Median (IQR), actual counts only | Missing | Recorded as 0 |
|---|---:|---:|---:|---:|
| CPSP | 80 (50–148); n = 505 | 64 (36–117); n = 295 | 1 | 17 |
| Fibromyalgia | 60 (36–99); n = 518 | 54 (34–90); n = 355 | 0 | 10 |
| MSK | 56 (36–90); n = 2,975 | 51 (32–86); n = 2,014 | 0 | 63 |
| Neuropathic | 48 (23–90); n = 761 | 40 (15–83); n = 481 | 0 | 32 |
| CRPS | 40 (24–61); n = 71 | 35 (14–62); n = 40 | 0 | 2 |
| Multiple | 50 (27–100); n = 212 | 44 (17–99); n = 134 | 0 | 12 |
| All | 58 (33–99); n = 5,042 | 50 (30–90); n = 3,319 | 1 | 136 |

*All recorded counts* mixes actual enrolment (finished or stopped trials) with estimated enrolment (trials still running). Withdrawn trials are recorded as 0 actual participants and are included as such. IQR uses linear interpolation (pandas default).
