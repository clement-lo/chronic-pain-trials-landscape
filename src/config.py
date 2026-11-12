"""Search settings for the chronic pain trials landscape.

Field (piece) names come from the ClinicalTrials.gov API v2 data model
(GET /api/v2/studies/metadata) and the query syntax from the API's OpenAPI
spec (GET /api/oas/v2) and the "Constructing Complex Search Queries" page.

The API queries are a deliberately broad net. Which trials are kept, and which
group each one goes into, is decided afterwards by the rules in src/rules.py.
"""

API_BASE = "https://clinicaltrials.gov/api/v2"

# Every query shares this filter: interventional studies that started
# (actual or anticipated) between 1 Jan 2015 and 31 Dec 2025 inclusive.
START_MIN = "2015-01-01"
START_MAX = "2025-12-31"
BASE_FILTER = (
    f"AREA[StudyType]INTERVENTIONAL AND AREA[StartDate]RANGE[{START_MIN},{START_MAX}]"
)
# Count-only companion filter: interventional studies with no start date at all,
# which the date filter above cannot see. Reported, never added to the data.
MISSING_START_FILTER = "AREA[StudyType]INTERVENTIONAL AND AREA[StartDate]MISSING"

PAGE_SIZE = 1000  # the API caps pageSize at 1,000

# Pieces requested for every study (names from /studies/metadata).
FIELDS = [
    "NCTId", "BriefTitle", "OfficialTitle",
    "Condition", "Keyword", "ConditionMeshTerm",
    "StudyType", "Phase", "DesignPrimaryPurpose",
    "OverallStatus", "WhyStopped",
    "StartDate", "StartDateType",
    "PrimaryCompletionDate", "PrimaryCompletionDateType",
    "StudyFirstPostDate", "LastUpdatePostDate",
    "EnrollmentCount", "EnrollmentType",
    "LeadSponsorName", "LeadSponsorClass",
    "LocationCountry", "LocationCity",
    "HasResults", "ResultsFirstPostDate",
    "PrimaryOutcomeMeasure", "PrimaryOutcomeDescription", "PrimaryOutcomeTimeFrame",
    "SecondaryOutcomeMeasure", "SecondaryOutcomeDescription", "SecondaryOutcomeTimeFrame",
    "InterventionType", "InterventionName",
    "EligibilityCriteria",
]


def _or(terms):
    """Join terms with OR, quoting each one.

    Quoting matters: an unquoted multi-word term is searched with the default
    'Relaxation' expansion, which also returns records that contain only some
    of its words.
    """
    return " OR ".join(f'"{t}"' for t in terms)


# Each query: key -> (API parameter, Essie expression, condition group it serves)
QUERIES = {
    # --- Chronic postsurgical pain (CPSP) -------------------------------------
    "cpsp_named": ("query.cond", _or([
        "chronic postsurgical pain", "chronic post-surgical pain",
        "chronic postoperative pain", "chronic post-operative pain",
        "persistent postsurgical pain", "persistent post-surgical pain",
        "persistent postoperative pain", "persistent post-operative pain",
        "chronic pain after surgery", "persistent pain after surgery",
        "post-mastectomy pain syndrome", "postmastectomy pain syndrome",
        "post-thoracotomy pain syndrome", "chronic post-thoracotomy pain",
        "chronic post-sternotomy pain", "chronic post-herniorrhaphy pain",
        "chronic groin pain", "inguinodynia",
        "post-amputation pain", "stump pain", "residual limb pain",
        "failed back surgery syndrome", "persistent spinal pain syndrome",
        "post-laminectomy syndrome",
    ]), "CPSP"),
    # Candidate net for the 3-month rule: trials coded as postoperative pain.
    # Most are acute analgesia trials and are dropped by src/rules.py.
    "cpsp_postop_candidates": ("query.cond", _or([
        "postoperative pain", "post-operative pain",
        "postsurgical pain", "post-surgical pain",
    ]), "CPSP"),
    # Surgical trials whose outcome (not condition) names chronic postsurgical pain.
    "cpsp_named_in_outcome": ("query.outc", _or([
        "chronic postsurgical pain", "chronic post-surgical pain",
        "chronic postoperative pain", "chronic post-operative pain",
        "persistent postsurgical pain", "persistent post-surgical pain",
        "persistent postoperative pain", "persistent post-operative pain",
        "chronic pain after surgery", "persistent pain after surgery",
    ]), "CPSP"),
    # --- Fibromyalgia -----------------------------------------------------------
    "fibromyalgia": ("query.cond", _or([
        "fibromyalgia", "fibromyalgia syndrome", "fibrositis",
        "chronic widespread pain",
    ]), "Fibromyalgia"),
    # --- Chronic low back and other chronic musculoskeletal pain --------------
    "msk_back_neck": ("query.cond", _or([
        "low back pain", "back pain", "lumbago", "lumbar pain",
        "spinal pain", "neck pain", "cervical pain", "whiplash",
    ]), "MSK"),
    "msk_other": ("query.cond", _or([
        "musculoskeletal pain", "chronic musculoskeletal pain",
        "myofascial pain", "myofascial pain syndrome",
        "shoulder pain", "knee pain", "hip pain", "joint pain",
        "osteoarthritis pain", "chronic primary pain",
        "elbow pain", "lateral elbow pain", "heel pain", "plantar heel pain",
        "foot pain", "ankle pain", "wrist pain", "hand pain",
        "patellofemoral pain", "sacroiliac joint pain", "facet joint pain",
        "thoracic spine pain", "muscle pain",
    ]), "MSK"),
    # Osteoarthritis trials that mention pain or analgesia anywhere in the
    # condition, title, keyword or MeSH fields (phrases like "pain in knee
    # osteoarthritis" do not match "knee pain").
    "msk_oa_pain": ("query.cond",
        "(" + _or(["osteoarthritis", "arthrosis", "gonarthrosis", "coxarthrosis"]) + ") AND ("
        + _or(["pain", "painful", "analgesic", "analgesia"]) + ")", "MSK"),
    # Records coded "chronic pain" plus a musculoskeletal diagnosis.
    "msk_chronic_pain_combo": ("query.cond",
        '"chronic pain" AND (' + _or([
            "osteoarthritis", "arthritis", "arthrosis", "tendinopathy",
            "musculoskeletal", "spondylosis", "spinal stenosis",
        ]) + ")", "MSK"),
    # --- Neuropathic pain -------------------------------------------------------
    "neuropathic_core": ("query.cond", _or([
        "neuropathic pain", "neuralgia", "postherpetic neuralgia",
        "trigeminal neuralgia", "painful diabetic neuropathy",
        "diabetic peripheral neuropathic pain", "painful neuropathy",
        "painful polyneuropathy", "central post-stroke pain",
        "central neuropathic pain", "spinal cord injury pain",
        "phantom limb pain", "nerve injury pain",
    ]), "Neuropathic"),
    "neuropathic_radicular": ("query.cond", _or([
        "radicular pain", "radiculopathy", "sciatica",
    ]), "Neuropathic"),
    # --- Complex regional pain syndrome ---------------------------------------
    "crps": ("query.cond", _or([
        "complex regional pain syndrome", "reflex sympathetic dystrophy",
        "causalgia", "algodystrophy", "CRPS",
    ]), "CRPS"),
}
