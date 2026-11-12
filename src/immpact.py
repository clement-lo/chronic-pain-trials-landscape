"""Keyword rules mapping primary outcome measures to the six IMMPACT core domains.

IMMPACT core outcome domains for chronic pain trials (Turk et al., Pain 2003;
Dworkin et al., Pain 2005):
  1. Pain intensity
  2. Physical functioning
  3. Emotional functioning
  4. Participant ratings of improvement and satisfaction
  5. Symptoms and adverse events
  6. Participant disposition

How a measure is mapped
-----------------------
* The measure TITLE is tested first. Only if the title matches no domain is the
  measure DESCRIPTION tested (column `matched_on`), because long descriptions
  often mention other domains in passing.
* A measure can match several domains (e.g. WOMAC pain and function, or a
  quality-of-life scale); `n_domains` > 1 marks these.
* A measure that matches none is kept with an empty domain list.

Choices worth knowing
---------------------
* Pain intensity: any remaining mention of pain after laboratory and cognitive
  pain measures are removed (pressure pain threshold, conditioned pain
  modulation, temporal summation, catastrophising, pain interference, pain
  knowledge/education, pain self-efficacy), plus VAS/NRS/verbal rating scales.
  Incidence of chronic pain counts as pain.
* Physical functioning: self-reported function and disability (ODI, RMDQ, NDI,
  WOMAC, KOOS, FIQ, DASH, SPADI, pain interference ...) and physical activity or
  walking/sit-to-stand tests. Range of motion and muscle strength are
  impairments, not function, and are not mapped.
* Generic health-related quality of life (SF-36, SF-12, EQ-5D, PROMIS-29/global,
  "quality of life") spans physical AND emotional functioning.
* Emotional functioning: depression, anxiety, mood, distress and well-being
  scales (BDI, HADS, PHQ, GAD-7, POMS, STAI, DASS ...). Pain catastrophising,
  kinesiophobia and fear-avoidance are pain-related cognitions, not IMMPACT
  emotional functioning, and are not mapped.
* Opioid or analgesic consumption, pressure pain thresholds, imaging,
  biomarkers, range of motion and strength match none.

Named instruments (Reviewer 2 flag 3)
-------------------------------------
Composite instruments get all the domains they report, wherever the measure
names them (title or description), unless the title restricts the measure to
one subscale ("WOMAC pain subscale", "BPI interference"):
  * pain + physical: WOMAC, KOOS, HOOS, Brief Pain Inventory (BPI), SPADI,
    ASES, Constant-Murley, Lequesne index, PEG scale
  * pain + physical + emotional: FIQ/FIQR, PROMIS-29/43/57
  * physical only (one disability score): ODI, RMDQ, NDI, Kujala, DASH and
    QuickDASH, Lysholm, Harris hip score
  * pain only: McGill/SF-MPQ, NPSI, DN4, LANSS, painDETECT
"""

import re

FLAGS = re.I

DOMAINS = [
    "Pain intensity",
    "Physical functioning",
    "Emotional functioning",
    "Improvement and satisfaction",
    "Symptoms and adverse events",
    "Participant disposition",
]

# Removed before the pain-intensity test (they are not ratings of pain intensity)
PAIN_NOT_INTENSITY = re.compile(
    r"(?:pressure\W+)?pain\W+(?:pressure\W+)?thresholds?|pain\W+tolerance|"
    r"conditioned\W+pain\W+modulation|temporal\W+summation(?:\W+of\W+pain)?|"
    r"pain\W+catastroph\w*|catastroph\w*|"
    r"(?:brief\W+pain\W+inventory|\bBPI\b)[^,;]{0,25}?interference|pain\W+interference|"
    r"interference[^,;]{0,40}?(?:brief\W+pain\W+inventory|\bBPI\b)|impact\W+of\W+pain|"
    r"kujala|anterior\W+knee\W+pain\W+scale|"
    r"pain\W+self[- ]?efficacy|pain\W+acceptance|pain\W+beliefs?|pain\W+knowledge|"
    r"pain\W+neuroscience|pain\W+education|pain[- ]related\W+fear|fear\W+of\W+pain|"
    r"(?:low\W+)?(?:back\W+)?pain[- ]?(?:related\W+)?disability|pain\W+medication|"
    r"pain\W+processing|pain\W+sensitivity|pain\W+mapping|pain\W+behaviou?r",
    FLAGS)
PAIN_INTENSITY = re.compile(
    r"\bpain|\bVAS\b|visual\W+analog|\bNRS\b|\bNPRS\b|numeric(?:al)?\W+(?:pain\W+)?rating|"
    r"verbal\W+rating|\bVRS\b|mc\s?gill|\bMPQ\b|\bNPSI\b|\bDN4\b|\bLANSS\b",
    FLAGS)

# Organ or laboratory "function" that is not physical functioning
NOT_PHYSICAL = re.compile(
    r"(?:renal|kidney|pulmonary|lung|liver|hepatic|cognitive|sexual|bladder|bowel|immune|"
    r"endothelial|autonomic|mitochondrial|cardiac|platelet|nerve|sensory|respiratory|"
    r"diaphragm\w*|thyroid|executive|ovarian|erectile)\W+(?:\w+\W+)?function\w*",
    FLAGS)
PHYSICAL = re.compile(
    r"function\w*|disabilit\w*|harris\W+hip|lysholm|kujala|\bPSFS\b|interference|"
    r"activities\W+of\W+daily\W+living|\bADLs?\b|daily\W+activit\w*|"
    r"physical\W+activit\w*|\bIPAQ\b|step\W+count|steps\W+per\W+day|accelerometr\w*|actigraph\w*|"
    r"walk\w*\W+test|\b6MWT\b|six[- ]minute\W+walk|timed\W+up\W+and\W+go|\bTUG\b|"
    r"sit[- ]to[- ]stand|chair\W+stand|\bgait\b|mobility|physical\W+(?:health|component|performance)|"
    r"\bWPAI\b|work\W+(?:ability|productivity)|return\W+to\W+work|\bVISA[- ]?[APG]\b",
    FLAGS)  # composite instruments (WOMAC, KOOS, FIQ, ODI ...) are mapped in INSTRUMENTS
HRQOL = re.compile(
    r"quality\W+of\W+life|\bQoL\b|\bHRQoL\b|\bSF[- ]?36\b|\bSF[- ]?12\b|\bEQ[- ]?5D|"
    r"\bPROMIS[- ]?(?:29|43|57)\b|PROMIS\W+global|\bWHOQOL", FLAGS)
EMOTIONAL = re.compile(
    r"depress\w*|anxi\w*|\bmood\b|emotion\w*|psychological\W+(?:distress|well|status|health)|"
    r"distress|\bBDI\b|beck\W+(?:depression|anxiety)|\bHADS\b|hospital\W+anxiety|\bPHQ|"
    r"\bGAD[- ]?7\b|\bPOMS\b|profile\W+of\W+mood|\bSTAI\b|state[- ]trait|\bDASS\b|\bPANAS\b|"
    r"\bCES[- ]?D\b|hamilton|\bHAM[- ]?[AD]\b|well[- ]?being|mental\W+(?:health|component)|"
    r"\bPTSD\b|\bstress\b",
    FLAGS)
GLOBAL = re.compile(
    r"global\W+impression|\bPGI[- ]?C\b|\bCGI\b|global\W+(?:assessment|rating|perceived|"
    r"improvement|change)|\bGPE\b|\bGRC\b|satisf\w*|impression\W+of\W+change|"
    r"patient\W+acceptable\W+symptom\W+state",
    FLAGS)
ADVERSE = re.compile(
    r"adverse|side[- ]?effects?|\bsafety\b|tolerab\w*|toxicit\w*|complication\w*|\bTEAEs?\b|"
    r"\bSAEs?\b|nausea|vomit\w*|\bPONV\b|sedation|somnolence|dizziness|constipation|pruritus|"
    r"respiratory\W+depression|laboratory[^,;]{0,20}abnormal\w*|withdrawal\W+symptoms?",
    FLAGS)
DISPOSITION = re.compile(
    r"drop[- ]?outs?|attrition|retention|adherence|complian\w*|completion\W+rate|"
    r"withdraw\w*\W+(?:from|rate)|premature\W+(?:withdrawal|discontinuation)|discontinu\w*|"
    r"completed\W+(?:the\W+)?(?:study|sessions?|intervention|treatment)|practice\W+completion|"
    r"attendance",
    FLAGS)


PI, PF, EF = "Pain intensity", "Physical functioning", "Emotional functioning"
INSTRUMENTS = [
    (re.compile(r"\bWOMAC\b|western\W+ontario\W+(?:and\W+)?mc\s?master", FLAGS), [PI, PF]),
    (re.compile(r"\bKOOS\b|knee\W+injury\W+and\W+osteoarthritis\W+outcome", FLAGS), [PI, PF]),
    (re.compile(r"\bHOOS\b|hip\W+disability\W+and\W+osteoarthritis\W+outcome", FLAGS), [PI, PF]),
    (re.compile(r"\bBPI\b|brief\W+pain\W+inventory", FLAGS), [PI, PF]),
    (re.compile(r"\bSPADI\b|shoulder\W+pain\W+and\W+disability\W+index", FLAGS), [PI, PF]),
    (re.compile(r"\bASES\b|american\W+shoulder\W+and\W+elbow", FLAGS), [PI, PF]),
    (re.compile(r"constant[- ]murley|\bconstant\W+(?:shoulder\W+)?score", FLAGS), [PI, PF]),
    (re.compile(r"lequesne", FLAGS), [PI, PF]),
    (re.compile(r"\bPEG\b(?:\W+scale)?|pain,?\W+enjoyment(?:\W+of\W+life)?,?\W+and\W+general\W+activity", FLAGS), [PI, PF]),
    (re.compile(r"\bFIQR?\b|fibromyalgia\W+impact\W+questionnaire", FLAGS), [PI, PF, EF]),
    (re.compile(r"\bPROMIS[- ]?(?:29|43|57)\b", FLAGS), [PI, PF, EF]),
    (re.compile(r"\bODI\b|oswestry|\bRMDQ\b|\bRMQ\b|roland|\bNDI\b|neck\W+disability\W+index|"
                r"kujala|\bAKPS\b|\bQuick\W?DASH\b|\bDASH\b|lysholm|harris\W+hip", FLAGS), [PF]),
    (re.compile(r"mc\s?gill|\bS?F?-?MPQ\b|\bNPSI\b|\bDN4\b|\bS?-?LANSS\b|pain\s?detect", FLAGS), [PI]),
]
# The measure is restricted to one part of an instrument
SUBSCALE = re.compile(
    r"\b(?:WOMAC|KOOS|HOOS|BPI|brief\W+pain\W+inventory|SPADI|ASES|FIQR?)\W+(?:\w+\W+){0,3}?"
    r"(?:pain|function\w*|stiffness|ADL|sports?|symptoms?|QoL|severity|intensity|interference|disability)\b"
    r"|\b(?:pain|function\w*|stiffness|severity|intensity|interference|disability)\W+(?:sub-?scale|sub-?score|"
    r"domain|component|items?)\b"
    r"|\b(?:severity|intensity|interference)\b[^,;]{0,40}?(?:\bBPI\b|brief\W+pain\W+inventory)",
    FLAGS)


def _instrument_domains(text):
    if not text:
        return []
    out = []
    for rx, doms in INSTRUMENTS:
        if rx.search(text):
            out += doms
    return out


def _domains(text):
    if not text:
        return []
    out = []
    if PAIN_INTENSITY.search(PAIN_NOT_INTENSITY.sub(" ", text)):
        out.append("Pain intensity")
    hrqol = bool(HRQOL.search(text))
    if hrqol or PHYSICAL.search(NOT_PHYSICAL.sub(" ", text)):
        out.append("Physical functioning")
    if hrqol or EMOTIONAL.search(text):
        out.append("Emotional functioning")
    if GLOBAL.search(text):
        out.append("Improvement and satisfaction")
    if ADVERSE.search(text):
        out.append("Symptoms and adverse events")
    if DISPOSITION.search(text):
        out.append("Participant disposition")
    return out


def map_measure(measure, description=None):
    """Return (domains, matched_on) for one outcome measure.

    Keyword domains come from the title. A composite instrument named in the
    title adds all its domains, unless the title names a single subscale. Only
    if the title gives no domain at all is the description used, in the same
    way (keywords plus any instrument it names).
    """
    def from_text(text, label):
        d = _domains(text)
        inst = [] if SUBSCALE.search(text or "") else _instrument_domains(text)
        extra = [x for x in inst if x not in d]
        on = None
        if d and extra:
            on = f"{label} + instrument"
        elif d:
            on = label
        elif extra:
            on = "instrument" if label == "title" else f"{label} instrument"
        return [x for x in DOMAINS if x in d + extra], on

    d, on = from_text(measure, "title")
    if not d:
        d, on = from_text(description, "description")
    return d, on or "none"
