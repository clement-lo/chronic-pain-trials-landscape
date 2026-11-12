"""Transparent keyword rules: which trials are kept, and which group they join.

Where the project brief is silent, groups follow the IASP chronic pain
classification used in ICD-11 (Treede et al., Pain 2019, and companion papers).

Text used
---------
* Groups and exclusions: the condition list and the brief and official titles,
  i.e. what the investigators entered. Each condition and each title is tested
  as a separate string, so words from two conditions are never glued together
  ("Chronic Kidney Disease" + "Back Pain" is not chronic back pain).
* CPSP outcome rules: primary and secondary outcome measures, descriptions and
  time frames. For the 3-month rule the measure title itself must be about
  pain, and the time frame must read as follow-up (see timeframe_is_followup).
* Chronicity for musculoskeletal and radicular pain, when the condition/title
  does not say "chronic": the INCLUSION part of the eligibility criteria
  (switch: USE_ELIGIBILITY_FOR_CHRONICITY). The inclusion criteria are also
  read to spot perioperative trials whose condition/title names a block or
  anaesthesia but not the surgery (periop_from_eligibility).
Keywords and auto-assigned MeSH terms are not used here; they only widen the
API search.

Order of decisions for each trial
---------------------------------
  1. Start date outside 1 Jan 2015-31 Dec 2025 -> excluded (re-check of API filter).
  2. Match each group (CPSP, Fibromyalgia, MSK, Neuropathic, CRPS).
  3. Dental, jaw and other orofacial trials cannot match CPSP or MSK.
  4. Exclusions override group matches, in this order: headache/migraine;
     cancer pain; (no group left and orofacial) dental/jaw/orofacial;
     acute postoperative pain; no in-scope condition.
  5. Kept trials matching 2+ groups -> "Multiple" (all matches listed).
"""

import re

FLAGS = re.I
USE_ELIGIBILITY_FOR_CHRONICITY = True

# ---------------------------------------------------------------------------
# Shared building blocks
# ---------------------------------------------------------------------------
CHRONIC = r"(?:chronic|persistent|long[- ]?standing|intractable|refractory)"
CHRONIC_WORD = re.compile(rf"\b{CHRONIC}\b", FLAGS)
PAINWORD = r"(?:pains?|painful|aches?|backache|lumbago|cervicalgia|sciatica|neuralgias?)"
PAIN_ANY = re.compile(rf"\b{PAINWORD}\b", FLAGS)
SURGERY = (r"\b(?:surgery|surgeries|surgical|operation|operative|mastectom\w*|lumpectom\w*|"
           r"thoracotom\w*|thoracoscop\w*|sternotom\w*|herniorrhaph\w*|hernia repair|hernioplast\w*|"
           r"arthroplast\w*|joint replacement|knee replacement|hip replacement|amputation|"
           r"c(?:a)?esarean|cesarian|hysterectom\w*|craniotom\w*|laminectom\w*|discectom\w*|"
           r"fusion|cholecystectom\w*|resection|repair|reconstruction|arthroscop\w*|"
           r"\bTKA|\bTHA|\bTKR|\bTHR|\bUKA)")

# "chronic ... pain" inside one string, either order: "Chronic Low Back Pain",
# "Low Back Pain, Chronic", "Knee Pain Chronic", "Back Pain Lower Back Chronic".
CHRONIC_PAIN = re.compile(
    rf"\b{CHRONIC}\b[^;|]{{0,40}}?\b{PAINWORD}\b"
    rf"|\b{PAINWORD}\b[^;|]{{0,25}}?\b{CHRONIC}\b"
    r"|\bCN?S?LBP\b|\bCNLBP\b|\bCNSLBP\b",  # chronic (non-specific) low back pain abbreviations
    FLAGS)

# Time points in free text ("3 months", "week 12", "POD 90", "six months")
WORDNUM = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7,
           "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12, "eighteen": 18,
           "twenty-four": 24, "twenty four": 24, "thirty": 30, "thirty-six": 36}
NUM = r"(\d+(?:\.\d+)?|" + "|".join(sorted(WORDNUM, key=len, reverse=True)) + r")"
UNIT = r"(days?|d|weeks?|wks?|w|months?|mos?|years?|yrs?|y)"  # no bare "m" (metres/minutes)
TF_NUM_UNIT = re.compile(rf"\b{NUM}[\s-]*{UNIT}\b", FLAGS)
TF_UNIT_NUM = re.compile(rf"\b(day|week|month|year|POD|postoperative day)\s*{NUM}\b", FLAGS)
DAYS_PER = {"d": 1, "w": 7, "m": 30.4375, "y": 365.25}
MIN_CHRONIC_DAYS = 84  # 3 months, counting 12 weeks as 3 months
# Registry template text that is not a measurement time point
TF_BOILERPLATE = re.compile(r"documented progression|whichever came first|study completion|"
                            r"an average of|through (?:the )?(?:end of )?(?:the )?study|"
                            r"duration of (?:the )?study|whole study|end of (?:the )?study", FLAGS)
# A time frame reads as follow-up when it is anchored to surgery or follow-up,
# or lists a schedule of 2+ time points. A bare "12 months" or "1 year" is often
# the length of the study, not a measurement point, so it does not count.
TF_ANCHOR = re.compile(r"\b(?:after|post|following|follow[- ]?ups?|postoperative\w*|post-?op\w*|"
                       r"since|from (?:the )?(?:surgery|operation)|discharge)\b", FLAGS)
TF_BASELINE = re.compile(r"\b(?:baseline|pre-?op\w*|preoperative\w*|day of surgery|screening)\b", FLAGS)
TF_HOURS = re.compile(r"\b\d+\s*(?:h|hrs?|hours?)\b", FLAGS)


def _unit_key(u):
    u = u.lower()
    return "d" if u.startswith(("pod", "postoperative")) else u[0]


def _num(x):
    x = x.lower()
    if x in WORDNUM:
        return float(WORDNUM[x])
    try:
        return float(x)
    except ValueError:  # e.g. look-alike Unicode letters matched case-insensitively
        return None


def timeframe_is_followup(tf):
    if not tf or TF_BOILERPLATE.search(tf):
        return False
    if TF_ANCHOR.search(tf):
        return True
    n_points = (len(TF_NUM_UNIT.findall(tf)) + len(TF_UNIT_NUM.findall(tf))
                + len(TF_BASELINE.findall(tf)) + len(TF_HOURS.findall(tf)))
    return n_points >= 2


def max_timeframe_days(tf):
    """Longest time point mentioned in a time-frame string, in days (None if none)."""
    if not tf or TF_BOILERPLATE.search(tf):
        return None
    best = None
    pairs = TF_NUM_UNIT.findall(tf) + [(n, u) for u, n in TF_UNIT_NUM.findall(tf)]
    for n, u in pairs:
        v = _num(n)
        if v is None:
            continue
        days = v * DAYS_PER[_unit_key(u)]
        best = days if best is None else max(best, days)
    return best


# ---------------------------------------------------------------------------
# 1. Chronic postsurgical pain (CPSP)
# ---------------------------------------------------------------------------
# Named CPSP in a condition, title or outcome. Per ICD-11 (Schug et al., Pain
# 2019), chronic pain after spinal surgery (failed back surgery syndrome) and
# after amputation are CPSP. "Post-mastectomy pain" on its own is often acute,
# so the named form needs "syndrome" or a chronic qualifier.
CPSP_NAMED = re.compile(
    rf"\b{CHRONIC}\b(?:\W+\w+){{0,3}}?\W+post[- ]?(?:surgical|operative|op|mastectomy|thoracotomy|"
    rf"sternotomy|herniorrhaphy|hernia|amputation|craniotomy|c(?:a)?esarean|arthroplasty|"
    rf"laminectomy)\b(?:\W+\w+){{0,2}}?\W+{PAINWORD}"
    rf"|\b{CHRONIC}\b(?:\W+\w+){{0,3}}?\W+pains?\W+(?:after|following|post)\W+(?:\w+\W+){{0,4}}?{SURGERY}"
    r"|\bpost[- ]?(?:mastectomy|thoracotomy|sternotomy|herniorrhaphy|amputation|laminectomy)\W+pain\W+syndrome"
    r"|\binguinodynia\b"
    r"|\bfailed\W+(?:back|spine|spinal)\W+(?:surgery|syndrome)|\bFBSS\b"
    r"|\bpersistent\W+spinal\W+pain\W+syndrome|\bPSPS\b|\bpost[- ]?laminectomy\W+syndrome"
    r"|\bpost[- ]?amputation\W+pain|\bstump\W+pain|\bresidual\W+limb\W+pain"
    rf"|\bpost[- ]?(?:surgical|operative)\W+(?:\w+\W+){{0,1}}?{CHRONIC}\W+{PAINWORD}"  # "post-operative chronic pain"
    r"|\bpost[- ]?(?:surgical|operative)\W+neuropathic\W+pain"
    r"|\bPPSP\b",
    FLAGS)

# Context: the trial is about pain after surgery (acute or chronic).
POSTOP_CONTEXT = re.compile(
    r"\bpost[- ]?(?:operative|surgical|op)\b\W+(?:\w+\W+){0,1}?(?:pain|analgesi\w*)"
    r"|\bpains?\W+post[- ]?(?:operative|surgical)"
    r"|\bperi[- ]?operative\W+(?:pain|analgesi\w*)"
    rf"|\bpains?\W+(?:after|following)\W+(?:\w+\W+){{0,4}}?{SURGERY}"
    # an anaesthesia/analgesia technique and a surgical procedure in the same
    # string, e.g. "Erector Spinae vs. PENG Block for Total Hip Arthroplasty"
    r"|\b(?:blocks?|an(?:a)?esthe\w*|analgesi\w*|infiltration|IPACK|PENG|adductor canal|"
    r"erector spinae|cryoneurolysis|opioid[- ]free)\b[^;|]{0,80}?" + SURGERY
    + r"|" + SURGERY + r"[^;|]{0,80}?\b(?:blocks?|an(?:a)?esthe\w*|analgesi\w*|infiltration|"
    r"IPACK|PENG|adductor canal|erector spinae|cryoneurolysis)\b",
    FLAGS)

# A pain outcome: the word pain or a named pain instrument (a bare "VAS" or
# "NRS" is not enough: it is also used for satisfaction, nausea, etc.)
PAIN_OUTCOME = re.compile(
    r"\bpain|brief pain inventory|\bBPI\b|mc ?gill|\bDN4\b|\bS?-?LANSS\b|pain ?detect|\bNPSI\b",
    FLAGS)


PAIN_SCALE = re.compile(r"\bVAS\b|\bNRS\b|numeric(?:al)? rating|visual analog", FLAGS)


def is_pain_measure(o):
    """The measure title is about pain: it says pain or names a pain instrument,
    or names a VAS/NRS whose description says it rates pain."""
    m = o.get("measure") or ""
    return bool(PAIN_OUTCOME.search(m) or (PAIN_SCALE.search(m) and PAIN_OUTCOME.search(o.get("description") or "")))


def cpsp_from_outcomes(outcomes):
    """Return (basis, level) for the outcome-based CPSP rules, or (None, None).

    outcomes: list of dicts with keys level ('primary'/'secondary'), measure,
    description, time_frame. Primary outcomes and stronger bases win.
    """
    found = []
    for o in outcomes:
        text = " ".join(filter(None, [o.get("measure"), o.get("description")]))
        if CPSP_NAMED.search(text):
            found.append(("outcome names chronic postsurgical pain", o["level"], 0))
        elif CHRONIC_PAIN.search(text):
            found.append(("outcome refers to chronic/persistent pain", o["level"], 1))
        elif is_pain_measure(o) and timeframe_is_followup(o.get("time_frame")):
            d = max_timeframe_days(o.get("time_frame"))
            if d is not None and d >= MIN_CHRONIC_DAYS:
                found.append(("pain measured >=12 weeks after surgery", o["level"], 2))
    if not found:
        return None, None
    found.sort(key=lambda x: (x[1] != "primary", x[2]))
    return found[0][0], found[0][1]


# ---------------------------------------------------------------------------
# 2. Fibromyalgia. Chronic widespread pain is grouped here: in ICD-11 it is the
#    parent category of fibromyalgia (MG30.01).
# ---------------------------------------------------------------------------
FIBRO = re.compile(r"fibromyalg|fibrositis|\bchronic\W+widespread\W+pain|\bCWP\b", FLAGS)

# ---------------------------------------------------------------------------
# 3. Chronic low back and other chronic musculoskeletal pain
#    Needs a musculoskeletal site, a pain word, and evidence of chronicity:
#    "chronic"/"persistent" with the pain in a condition or title, or
#    osteoarthritis (OA pain is chronic by definition), or (switch) inclusion
#    criteria requiring chronic pain or pain for >=12 weeks.
# ---------------------------------------------------------------------------
MSK_SITE = re.compile(
    r"\b(?:low(?:er)?[- ]?back|back|lumbar|lumbosacral|lumbago|backache|spin(?:e|al)|neck|cervical|"
    r"cervicalgia|whiplash|shoulder|knee|hip|osteoarthrit\w*|arthros\w*|gonarthros\w*|coxarthros\w*|"
    r"arthrit\w*|arthropath\w*|tendinopath\w*|tendin\w*|rotator cuff|epicondyl\w*|plantar fasci\w*|"
    r"patellofemoral|facet|sacroiliac|discogenic|spondylo\w*|spinal stenosis|elbow|wrist|ankle|heel|"
    r"musculoskeletal|myofascial|trigger[- ]point|joint|muscle pain|muscular pain|hand pain|foot pain)\b",
    FLAGS)
OA = re.compile(r"osteoarthrit|\bOA\b|gonarthros|coxarthros|arthrosis", FLAGS)
# For osteoarthritis, "analgesic"/"analgesia" also counts as naming the pain
# (e.g. "Analgesic Efficacy ... of Tanezumab in Osteoarthritis of the Hip or Knee").
OA_PAIN = re.compile(rf"\b{PAINWORD}\b|\banalgesi\w*", FLAGS)
# Phrases blanked out before the MSK test (the rest of the string is kept)
NOT_MSK = re.compile(
    r"cervical (?:cancer|ripening|dilat\w*|insufficien\w*|cerclage)|(?:head and )?neck cancer|labou?r\w*|"
    r"dysmenorr\w*|pelvic pain|endometrios\w*|abdominal pain|chest pain|"
    r"spinal (?:anesthesi\w*|anaesthesi\w*|block|cord)\w*(?: (?:stimulat\w*|injur\w*))?|"
    r"joint (?:replacement|arthroplast\w*)|knee replacement|hip replacement|"
    r"(?:knee|hip|shoulder|joint) (?:surgery|arthroscop\w*)",
    FLAGS)

# Dental, jaw and other orofacial pain: outside the five groups (ICD-11 puts
# chronic orofacial pain with headache). Blocks CPSP and MSK matches only.
OROFACIAL = re.compile(
    r"\btooth|\bteeth|dental|dentin\w*|endodont\w*|pulpot\w*|pulpectom\w*|pulpitis|\bpulp\b|root canal|"
    r"\bmolars?\b|periodont\w*|periapical|apical periodontitis|gingiv\w*|caries|carious|orthodont\w*|"
    r"temporomandibular|\bTMD\b|\bTMJ\b|orofacial|\bjaw\b|mastica\w*|bruxism|"
    r"burning mouth|oral surgery|occlusal",
    FLAGS)

# ---------------------------------------------------------------------------
# 4. Neuropathic pain
#    Tier A names neuropathic pain itself (no chronic qualifier needed).
#    Tier B (radiculopathy, sciatica) needs chronicity, as for MSK.
# ---------------------------------------------------------------------------
NEURO_A = re.compile(
    r"neuropathic\W+(?:\w+\W+){0,2}?pain|\bneuralgi\w*"
    r"|\bpain\w*\W+(?:\w+\W+){0,3}?(?:poly)?neuropath\w*"   # painful (diabetic) neuropathy
    r"|neuropath\w*\W+(?:\w+\W+){0,2}?pain"                 # neuropathy pain
    r"|\bcentral\W+(?:post[- ]?stroke\W+|neuropathic\W+)?pain|post[- ]?stroke\W+pain|thalamic\W+pain"
    r"|spinal\W+cord\W+injur\w*\W+(?:\w+\W+){0,2}?pain|pain\W+(?:after|following|in)\W+spinal\W+cord\W+injur"
    r"|phantom\W+(?:limb\W+)?pain|radicular\W+pain|nerve\W+injur\w*\W+pain|\bPHN\b|\bDPNP\b|\bPDPN\b",
    FLAGS)
NEURO_B = re.compile(r"radiculopath\w*|sciatica|radiculitis", FLAGS)
ACUTE_WORD = re.compile(r"\bacute\b", FLAGS)

# ---------------------------------------------------------------------------
# 5. Complex regional pain syndrome. "Shoulder-hand syndrome" after stroke is
#    CRPS type I; "regional pain syndrome" also catches the common misspelling
#    "chronic regional pain syndrome".
# ---------------------------------------------------------------------------
CRPS = re.compile(r"regional\W+pain\W+syndrome|\bCRPS\b|reflex\W+sympathetic\W+dystroph|"
                  r"causalgi|algodystroph|algoneurodystroph|sudeck|shoulder[- ]hand\W+syndrome", FLAGS)

# ---------------------------------------------------------------------------
# Exclusions (override group matches)
# ---------------------------------------------------------------------------
HEADACHE = re.compile(r"headache|migraine|cephal(?:al)?gi", FLAGS)
# Cancer pain, including pain caused by chemotherapy or radiotherapy, which
# ICD-11 classes as chronic cancer-related pain (MG30.1). Pain after cancer
# SURGERY stays in CPSP: ICD-11 classes it as chronic postsurgical pain.
CANCER_PAIN = re.compile(
    r"cancer[- ]?(?:related\W+|induced\W+|associated\W+)?pain|oncolog\w*\W+pain|malignan\w*\W+pain|"
    r"tumou?r[- ]?(?:related\W+)?pain|pain\W+(?:due\W+to|from|in|of|caused\W+by)\W+(?:\w+\W+){0,2}?"
    r"(?:cancer|malignan\w*|tumou?r|metasta\w*)|bone\W+metasta|"
    r"chemotherapy[- ]?(?:induced|related|associated)|\bCIPN\b|oxaliplatin|paclitaxel|taxane|"
    r"bortezomib|vincristine|platinum[- ]induced|aromatase\W+inhibitor|\bAIMSS\b|"
    r"radiation[- ]induced|radiotherapy[- ]induced|post[- ]?radiation",
    FLAGS)
CANCER_TERM = re.compile(r"cancer|carcinom|neoplas|tumou?rs?\b|malignan|lymphoma|leuka?emia|"
                         r"myeloma|sarcoma|metasta|oncolog", FLAGS)

GROUPS = ["CPSP", "Fibromyalgia", "MSK", "Neuropathic", "CRPS"]
GROUP_LABELS = {
    "CPSP": "Chronic postsurgical pain",
    "Fibromyalgia": "Fibromyalgia",
    "MSK": "Chronic low back & other musculoskeletal pain",
    "Neuropathic": "Neuropathic pain",
    "CRPS": "Complex regional pain syndrome",
    "Multiple": "Multiple groups",
}


# ---------------------------------------------------------------------------
# Chronicity from the inclusion criteria. Chronic pain = pain lasting 3 months
# or more (IASP); 12 weeks counts as 3 months. Only the inclusion part of the
# eligibility text is read, line by line; a line must mention pain or symptoms,
# and lines with a negation are skipped, so "no injection for pain in the past
# 3 months" does not count.
# ---------------------------------------------------------------------------
EXCL_HEADING = re.compile(r"exclusion\s+criteria|\bexclusions?\s*:|\bnon[- ]?inclusion", FLAGS)
ELIG_PAIN = re.compile(r"\bpain|\bLBP\b|\bNSLBP\b|\bache|\bsymptom|\bcomplaint|sciatica|radicul|lumbago|"
                       r"cervicalgia|discomfort", FLAGS)
NEGATION = re.compile(r"\b(?:no|not|without|never|none|excluded?|unable)\b|n't\b", FLAGS)
DURATION_CUE = re.compile(r"(?:≥|>=|>|more than|longer than|greater than|over|at least|minimum|"
                          r"for|lasting|last(?:ed|s)?|duration|persist\w*|since|exceed\w*|of)\s*"
                          rf"(?:the\s+)?(?:last\s+|past\s+|previous\s+)?{NUM}\s*(?:consecutive\s+)?"
                          r"(weeks?|wks?|months?|mos?|years?|yrs?)\b", FLAGS)


def inclusion_text(elig):
    if not elig:
        return ""
    m = EXCL_HEADING.search(elig)
    return elig[:m.start()] if m else elig


def chronic_from_eligibility(elig):
    """True if an inclusion-criteria line says the pain is chronic or lasts >=12 weeks."""
    for line in re.split(r"[\n\r]+|(?<=\.)\s+", inclusion_text(elig)):
        if not ELIG_PAIN.search(line) or NEGATION.search(line):
            continue
        if CHRONIC_WORD.search(line):
            return True
        for n, u in DURATION_CUE.findall(line):
            v = _num(n)
            if v is not None and v * DAYS_PER[u.lower()[0]] >= MIN_CHRONIC_DAYS:
                return True
    return False


# Perioperative trials whose condition/title hides the surgery: an anaesthesia,
# analgesia or "acute pain" term in a condition or title, plus inclusion
# criteria that enrol people undergoing surgery.
ANAESTH_TERM = re.compile(r"\b(?:blocks?|an(?:a)?esthe\w*|infiltration|IPACK|PENG|"
                          r"adductor canal|erector spinae|interscalene|cryoneurolysis|opioid[- ]free|"
                          r"acute pain|pain, acute)\b", FLAGS)
UNDERGOING_SURGERY = re.compile(r"\b(?:undergo\w*|scheduled|planned|candidates?|elective|booked|listed)\b"
                                r"[^.\n]{0,60}?" + SURGERY, FLAGS)


def periop_from_eligibility(elig):
    for line in re.split(r"[\n\r]+|(?<=\.)\s+", inclusion_text(elig)):
        if UNDERGOING_SURGERY.search(line) and not NEGATION.search(line):
            return True
    return False


def _any(rx, strings):
    return [s for s in strings if rx.search(s)]


def classify(conditions, titles, outcomes, eligibility=None):
    """Classify one trial.

    Returns a dict:
      groups        matched groups before exclusions
      group         final group, "Multiple", or None if excluded
      excluded      exclusion reason, or None
      cpsp_basis    why CPSP matched, or None
      cpsp_level    'primary'/'secondary' when CPSP came from an outcome
      chronic_from  'condition/title' or 'inclusion criteria' for MSK/radicular matches
      notes         near-miss notes, used to pick borderline exclusions for review
    """
    strings = [s for s in list(conditions) + list(titles) if s]
    groups, notes = [], []
    cpsp_basis = cpsp_level = chronic_from = None
    orofacial = bool(_any(OROFACIAL, strings))
    elig_chronic = USE_ELIGIBILITY_FOR_CHRONICITY and chronic_from_eligibility(eligibility)

    # --- 1. CPSP
    # (neuropathic phrases are blanked first: "Phantom Pain Following Amputation"
    #  and "Post-surgical Neuropathic Pain" are not acute postoperative pain)
    postop = (any(POSTOP_CONTEXT.search(NEURO_A.sub(" ", s)) for s in strings)
              or (bool(_any(ANAESTH_TERM, strings)) and periop_from_eligibility(eligibility)))
    if _any(CPSP_NAMED, strings):
        cpsp_basis = "named in condition/title"
    else:
        basis, level = cpsp_from_outcomes(outcomes)
        if basis == "outcome names chronic postsurgical pain" or (basis and postop):
            cpsp_basis, cpsp_level = basis, level
    if cpsp_basis and orofacial:
        notes.append("dental/orofacial trial matched CPSP")
        cpsp_basis = cpsp_level = None
    if cpsp_basis:
        groups.append("CPSP")

    # --- 2. Fibromyalgia
    if _any(FIBRO, strings):
        groups.append("Fibromyalgia")

    # --- 3. MSK. Surgical and non-musculoskeletal phrases are blanked out first,
    #     so "chronic pain after knee arthroplasty" or "spinal cord stimulation
    #     for chronic pain" do not count as musculoskeletal pain.
    #     Strings describing radicular or neuropathic pain ("chronic lumbar
    #     radicular pain") are left to the neuropathic group.
    msk = [POSTOP_CONTEXT.sub(" ", CPSP_NAMED.sub(" ", NOT_MSK.sub(" ", s))) for s in strings
           if not (NEURO_A.search(s) or NEURO_B.search(s))]
    site, pain = bool(_any(MSK_SITE, msk)), bool(_any(PAIN_ANY, msk))
    oa = bool(_any(OA, msk))
    oa_pain = oa and bool(_any(OA_PAIN, msk))
    if (site and pain or oa_pain) and not orofacial:
        if _any(CHRONIC_PAIN, msk):
            groups.append("MSK"); chronic_from = "condition/title"
        elif oa_pain:
            groups.append("MSK"); chronic_from = "osteoarthritis"
        elif elig_chronic:
            groups.append("MSK"); chronic_from = "inclusion criteria"
        else:
            notes.append("musculoskeletal pain without evidence of chronicity")
    elif (site and pain or oa_pain) and orofacial:
        notes.append("orofacial/jaw musculoskeletal pain")
    elif oa:
        notes.append("osteoarthritis without a pain word")

    # --- 4. Neuropathic (a string that says "acute" without "chronic" does not count)
    neuro_a = [s for s in _any(NEURO_A, strings)
               if not (ACUTE_WORD.search(s) and not CHRONIC_WORD.search(s))]
    neuro_b = _any(NEURO_B, strings)
    if neuro_a:
        groups.append("Neuropathic")
    elif neuro_b and _any(CHRONIC_WORD, neuro_b):
        groups.append("Neuropathic"); chronic_from = chronic_from or "condition/title"
    elif neuro_b and elig_chronic:
        groups.append("Neuropathic"); chronic_from = chronic_from or "inclusion criteria"
    elif neuro_b:
        notes.append("radiculopathy/sciatica without evidence of chronicity")
    elif _any(NEURO_A, strings):
        notes.append("neuropathic term only in an 'acute' string")

    # --- 5. CRPS
    if _any(CRPS, strings):
        groups.append("CRPS")

    # --- Exclusions
    excluded = None
    if _any(HEADACHE, strings):
        excluded = "headache or migraine"
    elif _any(CANCER_PAIN, strings):
        excluded = "cancer pain (incl. chemotherapy/radiotherapy-induced)"
    elif _any(CANCER_TERM, conditions) and groups and "CPSP" not in groups:
        excluded = "cancer pain (cancer condition, non-surgical pain)"
    elif not groups and orofacial:
        excluded = "dental, jaw or other orofacial pain (outside the five groups)"
    elif postop and "CPSP" not in groups:
        excluded = "acute postoperative pain"
    elif not groups:
        excluded = "no in-scope condition in conditions/titles"

    group = None if excluded else ("Multiple" if len(groups) > 1 else groups[0])
    return {"groups": groups, "group": group, "excluded": excluded,
            "cpsp_basis": cpsp_basis, "cpsp_level": cpsp_level,
            "chronic_from": chronic_from if "MSK" in groups or "Neuropathic" in groups else None,
            "notes": "; ".join(notes) or None}
