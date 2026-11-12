"""Keyword rules for why trials stopped (terminated, withdrawn, suspended).

Each stated reason is tested against every category; all matches are kept
(column `stop_categories`). One main category per trial (`stop_reason`) is then
chosen by the fixed precedence below, so a reason such as "low enrolment due to
COVID-19" counts once, under its root cause:

  1. COVID-19            an external event that explains whatever followed
  2. Safety or futility  a scientific stop
  3. Low accrual
  4. Funding
  5. Sponsor or business decision
  6. Site or investigator
  7. Other               a reason is given but fits none of the above
  8. Not stated          the registry field is empty

Reasons that match no keyword at all are also put under "Other" and flagged
`unclassified = True`, so they can be listed for review.
"""

import re

FLAGS = re.I

CATEGORIES = [
    ("COVID-19", re.compile(
        r"covid|\bcovd\b|corona\s*virus|\bcorona\b|sars[- ]?cov|pandemic|lockdown", FLAGS)),
    ("Safety or futility", re.compile(
        r"safety|adverse|side[- ]?effect|toxicit|futil|lack of (?:efficacy|effect|benefit)|"
        r"no (?:clinical |significant )?(?:benefit|efficacy|effect)|ineffect|"
        r"did not meet[^.;]{0,40}endpoint|efficacy endpoint|interim analys|\bDSMB\b|\bDSMC\b|\bDMC\b|"
        r"data (?:and )?safety monitoring|data monitoring committee|\bharm|death|died|"
        r"(?:study|trial) was negative|negative (?:results?|pilot)", FLAGS)),
    ("Low accrual", re.compile(
        r"enrol|recruit|accru|inclusion rate|slow inclusion|low inclusion|insufficient inclusion|"
        r"no (?:local )?inclusions|no (?:eligible )?(?:participants|patients|subjects)|"
        r"lack of (?:eligible )?(?:participants|patients|subjects)|"
        r"not enough (?:eligible )?(?:participants|patients|subjects)|few (?:participants|patients)|"
        r"non-?response|participant interest|could not (?:find|identify) (?:participants|patients)|"
        r"participation|lack of patients?\b|including patients|take part|accept\w* (?:to )?participat|"
        r"(?:number|numbers) of (?:eligible )?patients", FLAGS)),
    ("Funding", re.compile(
        r"fund|financ|budget|\bgrant|money|no support|lack of support|\bcost", FLAGS)),
    ("Sponsor or business decision", re.compile(
        r"sponsor|business|company|commercial|strateg|portfolio|prioriti|acquisi|merger|licens|"
        r"marketing|\bCE mark|product development|development program|corporate|manufacturer", FLAGS)),
    ("Site or investigator", re.compile(
        r"investigator|\bPI\b|left the (?:institution|university|hospital)|leaving|relocat|retire|"
        r"\bmoved\b|transferred|staff|personnel|research assistant|coordinator|collaborator|"
        r"\bsites?\b|institution|pharmacy|maternity leave|availability|study lead|employer|"
        r"study team|provider|\bDr\.? [A-Z]", FLAGS)),
    ("Other", re.compile(
        r"\bIRB\b|ethic|regulat|\bFDA\b|approval|protocol|design|method|duplicate|replaced|"
        r"combined with|merged|logistic|feasib|technical|supply|availab|material|equipment|"
        r"hardware|vendor|contract|administrat|insurance|legal|unforeseen|circumstance|"
        r"competing stud|never (?:initiated|started|began)|not (?:initiated|started|begun)|"
        r"error|completed|new version|confound|missing (?:participant )?data|internal decision|"
        r"decision", FLAGS)),
]
ORDER = [c for c, _ in CATEGORIES] + ["Not stated"]


def classify_stop(reason):
    """Return (main category, all matched categories, unclassified flag)."""
    if reason is None or reason != reason or not str(reason).strip():  # None, NaN or blank
        return "Not stated", [], False
    text = str(reason)
    matched = [name for name, rx in CATEGORIES if rx.search(text)]
    if not matched:
        return "Other", [], True
    return matched[0], matched, False
