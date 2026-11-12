# Query log

- **Pull date:** 2026-11-12 (UTC time 2026-11-12T06:50:25+00:00)
- **API:** ClinicalTrials.gov API v2, version 2.0.5; registry data timestamp 2026-11-10T10:00:05
- **Endpoint:** `GET https://clinicaltrials.gov/api/v2/studies`, `pageSize=1000`, `format=json`, all pages followed via `nextPageToken`
- **Filter applied to every query** (`filter.advanced`): `AREA[StudyType]INTERVENTIONAL AND AREA[StartDate]RANGE[2015-01-01,2025-12-31]`
- **Fields requested** (`fields`): `NCTId|BriefTitle|OfficialTitle|Condition|Keyword|ConditionMeshTerm|StudyType|Phase|DesignPrimaryPurpose|OverallStatus|WhyStopped|StartDate|StartDateType|PrimaryCompletionDate|PrimaryCompletionDateType|StudyFirstPostDate|LastUpdatePostDate|EnrollmentCount|EnrollmentType|LeadSponsorName|LeadSponsorClass|LocationCountry|LocationCity|HasResults|ResultsFirstPostDate|PrimaryOutcomeMeasure|PrimaryOutcomeDescription|PrimaryOutcomeTimeFrame|SecondaryOutcomeMeasure|SecondaryOutcomeDescription|SecondaryOutcomeTimeFrame|InterventionType|InterventionName|EligibilityCriteria`

Each multi-word term is in quotes so the API searches the exact phrase (with its registry synonyms) rather than any one of its words. `query.cond` searches the condition, title, keyword and MeSH fields; `query.outc` searches outcome measures. These queries only cast the net: `src/rules.py` decides which trials are kept and which group they join.

| Query key | Group | Parameter | Studies returned | Interventional, same query, no start date (not pulled) |
|---|---|---|---:|---:|
| `cpsp_named` | CPSP | `query.cond` | 250 | 1 |
| `cpsp_postop_candidates` | CPSP | `query.cond` | 4,441 | 12 |
| `cpsp_named_in_outcome` | CPSP | `query.outc` | 135 | 0 |
| `fibromyalgia` | Fibromyalgia | `query.cond` | 740 | 2 |
| `msk_back_neck` | MSK | `query.cond` | 3,109 | 11 |
| `msk_other` | MSK | `query.cond` | 3,043 | 8 |
| `msk_oa_pain` | MSK | `query.cond` | 2,296 | 11 |
| `msk_chronic_pain_combo` | MSK | `query.cond` | 424 | 0 |
| `neuropathic_core` | Neuropathic | `query.cond` | 1,022 | 8 |
| `neuropathic_radicular` | Neuropathic | `query.cond` | 390 | 1 |
| `crps` | CRPS | `query.cond` | 111 | 0 |

## Query strings

### `cpsp_named` (query.cond)

```
"chronic postsurgical pain" OR "chronic post-surgical pain" OR "chronic postoperative pain" OR "chronic post-operative pain" OR "persistent postsurgical pain" OR "persistent post-surgical pain" OR "persistent postoperative pain" OR "persistent post-operative pain" OR "chronic pain after surgery" OR "persistent pain after surgery" OR "post-mastectomy pain syndrome" OR "postmastectomy pain syndrome" OR "post-thoracotomy pain syndrome" OR "chronic post-thoracotomy pain" OR "chronic post-sternotomy pain" OR "chronic post-herniorrhaphy pain" OR "chronic groin pain" OR "inguinodynia" OR "post-amputation pain" OR "stump pain" OR "residual limb pain" OR "failed back surgery syndrome" OR "persistent spinal pain syndrome" OR "post-laminectomy syndrome"
```

### `cpsp_postop_candidates` (query.cond)

```
"postoperative pain" OR "post-operative pain" OR "postsurgical pain" OR "post-surgical pain"
```

### `cpsp_named_in_outcome` (query.outc)

```
"chronic postsurgical pain" OR "chronic post-surgical pain" OR "chronic postoperative pain" OR "chronic post-operative pain" OR "persistent postsurgical pain" OR "persistent post-surgical pain" OR "persistent postoperative pain" OR "persistent post-operative pain" OR "chronic pain after surgery" OR "persistent pain after surgery"
```

### `fibromyalgia` (query.cond)

```
"fibromyalgia" OR "fibromyalgia syndrome" OR "fibrositis" OR "chronic widespread pain"
```

### `msk_back_neck` (query.cond)

```
"low back pain" OR "back pain" OR "lumbago" OR "lumbar pain" OR "spinal pain" OR "neck pain" OR "cervical pain" OR "whiplash"
```

### `msk_other` (query.cond)

```
"musculoskeletal pain" OR "chronic musculoskeletal pain" OR "myofascial pain" OR "myofascial pain syndrome" OR "shoulder pain" OR "knee pain" OR "hip pain" OR "joint pain" OR "osteoarthritis pain" OR "chronic primary pain" OR "elbow pain" OR "lateral elbow pain" OR "heel pain" OR "plantar heel pain" OR "foot pain" OR "ankle pain" OR "wrist pain" OR "hand pain" OR "patellofemoral pain" OR "sacroiliac joint pain" OR "facet joint pain" OR "thoracic spine pain" OR "muscle pain"
```

### `msk_oa_pain` (query.cond)

```
("osteoarthritis" OR "arthrosis" OR "gonarthrosis" OR "coxarthrosis") AND ("pain" OR "painful" OR "analgesic" OR "analgesia")
```

### `msk_chronic_pain_combo` (query.cond)

```
"chronic pain" AND ("osteoarthritis" OR "arthritis" OR "arthrosis" OR "tendinopathy" OR "musculoskeletal" OR "spondylosis" OR "spinal stenosis")
```

### `neuropathic_core` (query.cond)

```
"neuropathic pain" OR "neuralgia" OR "postherpetic neuralgia" OR "trigeminal neuralgia" OR "painful diabetic neuropathy" OR "diabetic peripheral neuropathic pain" OR "painful neuropathy" OR "painful polyneuropathy" OR "central post-stroke pain" OR "central neuropathic pain" OR "spinal cord injury pain" OR "phantom limb pain" OR "nerve injury pain"
```

### `neuropathic_radicular` (query.cond)

```
"radicular pain" OR "radiculopathy" OR "sciatica"
```

### `crps` (query.cond)

```
"complex regional pain syndrome" OR "reflex sympathetic dystrophy" OR "causalgia" OR "algodystrophy" OR "CRPS"
```
