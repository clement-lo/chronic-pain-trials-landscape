# Chronic pain trials on ClinicalTrials.gov, 2015–2025: summary tables

Data from ClinicalTrials.gov (API v2, version 2.0.5), pulled 2026-11-12. Interventional studies with a start date from 1 Jan 2015 to 31 Dec 2025. 12,413 unique trials were retrieved by the searches; **5,050** met the inclusion rules (see `src/rules.py`).

Group key: **CPSP** = Chronic postsurgical pain; **Fibromyalgia** = Fibromyalgia; **MSK** = Chronic low back & other musculoskeletal pain; **Neuropathic** = Neuropathic pain; **CRPS** = Complex regional pain syndrome; **Multiple** = Multiple groups.
A trial matching two or more groups is counted once, under *Multiple*.

## 1. Trials by group and phase

| Phase | CPSP | Fibromyalgia | MSK | Neuropathic | CRPS | Multiple | **Total** |
|---|---:|---:|---:|---:|---:|---:|---:|
| Early phase 1 | 6 | 5 | 20 | 8 | 2 | 5 | **46** |
| Phase 1 | 1 | 5 | 60 | 46 | 1 | 6 | **119** |
| Phase 1/2 | 0 | 3 | 27 | 15 | 0 | 2 | **47** |
| Phase 2 | 15 | 22 | 111 | 100 | 2 | 12 | **262** |
| Phase 2/3 | 10 | 5 | 28 | 10 | 1 | 3 | **57** |
| Phase 3 | 31 | 15 | 95 | 50 | 6 | 4 | **201** |
| Phase 4 | 75 | 11 | 79 | 30 | 4 | 15 | **214** |
| Not applicable | 300 | 453 | 2,630 | 500 | 55 | 161 | **4,099** |
| Missing | 0 | 0 | 4 | 1 | 0 | 0 | **5** |
| **Total** | **438** | **519** | **3,054** | **760** | **71** | **208** | **5,050** |

*Missing* = no phase recorded in the registry.

## 2. Trials by overall status

| Status | CPSP | Fibromyalgia | MSK | Neuropathic | CRPS | Multiple | **Total** |
|---|---:|---:|---:|---:|---:|---:|---:|
| Completed | 206 | 317 | 1,861 | 374 | 31 | 102 | **2,891** |
| Recruiting | 66 | 53 | 279 | 111 | 11 | 25 | **545** |
| Not yet recruiting | 10 | 8 | 77 | 19 | 3 | 3 | **120** |
| Active, not recruiting | 19 | 16 | 107 | 25 | 1 | 9 | **177** |
| Enrolling by invitation | 2 | 6 | 29 | 7 | 2 | 2 | **48** |
| Terminated | 25 | 14 | 77 | 52 | 5 | 7 | **180** |
| Withdrawn | 14 | 10 | 63 | 32 | 2 | 12 | **133** |
| Suspended | 0 | 3 | 4 | 4 | 0 | 0 | **11** |
| Unknown status | 96 | 92 | 557 | 136 | 16 | 48 | **945** |
| **Total** | **438** | **519** | **3,054** | **760** | **71** | **208** | **5,050** |

*Unknown status* is the registry's label for a trial whose record has not been verified for more than two years.

## 3. Trials by lead sponsor class

| Sponsor class | CPSP | Fibromyalgia | MSK | Neuropathic | CRPS | Multiple | **Total** |
|---|---:|---:|---:|---:|---:|---:|---:|
| Industry | 12 | 34 | 380 | 155 | 6 | 17 | **604** |
| Other (universities, hospitals, non-profits) | 405 | 465 | 2,570 | 571 | 60 | 180 | **4,251** |
| Other US federal | 4 | 7 | 50 | 8 | 1 | 5 | **75** |
| Other government | 16 | 12 | 48 | 21 | 3 | 5 | **105** |
| Network | 1 | 1 | 5 | 3 | 1 | 0 | **11** |
| Individual | 0 | 0 | 1 | 2 | 0 | 1 | **4** |
| **Total** | **438** | **519** | **3,054** | **760** | **71** | **208** | **5,050** |

*Sponsor class* is the registry's own classification of the lead sponsor.

## 4. Planned or actual enrolment by group

| Group | Median (IQR), all recorded counts | Median (IQR), actual counts only | Missing | Recorded as 0 |
|---|---:|---:|---:|---:|
| CPSP | 80 (50–150); n = 437 | 65 (36–118); n = 259 | 1 | 14 |
| Fibromyalgia | 60 (36–98); n = 519 | 54 (34–90); n = 356 | 0 | 10 |
| MSK | 56 (35–90); n = 3,054 | 51 (32–86); n = 2,068 | 0 | 63 |
| Neuropathic | 46 (22–90); n = 760 | 40 (14–83); n = 481 | 0 | 32 |
| CRPS | 40 (24–61); n = 71 | 35 (14–62); n = 40 | 0 | 2 |
| Multiple | 50 (28–99); n = 208 | 44 (19–90); n = 128 | 0 | 12 |
| All | 57 (33–99); n = 5,049 | 50 (30–90); n = 3,332 | 1 | 133 |

*All recorded counts* mixes actual enrolment (finished or stopped trials) with estimated enrolment (trials still running). Withdrawn trials are recorded as 0 actual participants and are included as such. IQR uses linear interpolation (pandas default).
