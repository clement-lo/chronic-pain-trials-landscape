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
    r"function\w*|disabilit\w*|\bODI\b|oswestry|roland|\bRMDQ\b|\bRMQ\b|\bNDI\b|"
    r"neck\W+disability|\bWOMAC\b|western\W+ontario|\bKOOS\b|\bHOOS\b|lequesne|\bFIQR?\b|"
    r"fibromyalgia\W+impact|\bDASH\b|quick\W?dash|\bSPADI\b|constant[- ]murley|\bASES\b|"
    r"harris\W+hip|lysholm|kujala|\bPSFS\b|interference|activities\W+of\W+daily\W+living|\bADLs?\b|"
    r"daily\W+activit\w*|"
    r"physical\W+activit\w*|\bIPAQ\b|step\W+count|steps\W+per\W+day|accelerometr\w*|actigraph\w*|"
    r"walk\w*\W+test|\b6MWT\b|six[- ]minute\W+walk|timed\W+up\W+and\W+go|\bTUG\b|"
    r"sit[- ]to[- ]stand|chair\W+stand|\bgait\b|mobility|physical\W+(?:health|component|performance)|"
    r"\bWPAI\b|work\W+(?:ability|productivity)|return\W+to\W+work|\bVISA[- ]?[APG]\b",
    FLAGS)
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
    """Return (domains, matched_on) for one outcome measure."""
    d = _domains(measure)
    if d:
        return d, "title"
    d = _domains(description)
    if d:
        return d, "description"
    return [], "none"
