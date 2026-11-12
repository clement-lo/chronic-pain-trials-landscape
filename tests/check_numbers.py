"""Check that the text outputs only quote numbers produced by the analysis.

Usage:
    .venv/bin/python tests/check_numbers.py

Checks
------
1. Every number in outputs/summary.md and README.md appears as a value in
   outputs/numbers.json. Dates (YYYY-MM-DD) and version strings (2.0.5) must
   match a text value; other numbers must match a numeric value, after
   removing thousands separators.
2. Both files are exactly what src/report.py renders from their templates and
   the current numbers.json, so no number was typed in or left stale.
3. The templates' fixed text contains no numbers of its own: every number
   enters through a named placeholder. (Check 1 alone could pass by
   coincidence for small numbers; checks 2 and 3 close that gap.)
4. outputs/summary.md is within the word limit in numbers.json.
5. Both figures exist as PNG and SVG.

Not counted as numbers: code blocks and inline code (commands and file names),
link targets (file names), and digits that are part of a name, such as
COVID-19, SF-36 or API v2.
Exit code 0 when every check passes, 1 otherwise.
"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from report import TARGETS, TEMPLATES, render  # noqa: E402

N = json.loads((ROOT / "outputs" / "numbers.json").read_text())

TOKEN = re.compile(
    r"(?<![A-Za-z0-9_.])(?<![A-Za-z]-)"            # not part of a name like v2, fig1, COVID-19
    r"(\d{4}-\d{2}-\d{2}"                          # ISO date
    r"|\d+(?:\.\d+){2,}"                           # version, e.g. 2.0.5
    r"|\d{1,3}(?:,\d{3})+(?:\.\d+)?"               # 12,413
    r"|\d+(?:\.\d+)?)"                             # 58, 16.2
    r"(?![A-Za-z0-9_])")
PLACEHOLDER = re.compile(r"\{[A-Z]\[[^{}]*\}")


def strip_non_text(md):
    md = re.sub(r"```.*?```", " ", md, flags=re.S)   # code blocks
    md = re.sub(r"`[^`]*`", " ", md)                 # inline code
    md = re.sub(r"\]\([^)]*\)", "]", md)            # link targets
    return md


def leaves(obj):
    if isinstance(obj, dict):
        for v in obj.values():
            yield from leaves(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from leaves(v)
    else:
        yield obj


VALUES = list(leaves(N))
NUMS = {float(v) for v in VALUES if isinstance(v, (int, float)) and not isinstance(v, bool)}
STRS = {v for v in VALUES if isinstance(v, str)}


def is_known(tok):
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}|\d+(?:\.\d+){2,}", tok):
        return tok in STRS
    x = float(tok.replace(",", ""))
    return any(abs(x - v) < 1e-9 for v in NUMS)


def word_count(md):
    md = re.sub(r"\]\([^)]*\)", "]", md)
    return sum(1 for w in md.split() if re.search(r"[A-Za-z0-9]", w))


def main():
    failures, report = [], []
    for tmpl, target in TARGETS.items():
        name = target.relative_to(ROOT)
        text = target.read_text()

        # 1. every number is a value in numbers.json
        toks = TOKEN.findall(strip_non_text(text))
        unknown = [t for t in toks if not is_known(t)]
        report.append(f"{name}: {len(toks)} numbers checked, {len(unknown)} not found in numbers.json")
        if unknown:
            failures.append(f"{name}: numbers not in numbers.json: {sorted(set(unknown))}")

        # 2. file matches a fresh render of its template
        if render(tmpl, N) != text:
            failures.append(f"{name}: differs from templates/{tmpl} rendered with the current "
                            f"numbers.json (run src/report.py)")
        else:
            report.append(f"{name}: matches templates/{tmpl}")

        # 3. no numbers typed into the template's fixed text
        fixed = PLACEHOLDER.sub(" ", strip_non_text((TEMPLATES / tmpl).read_text()))
        typed = TOKEN.findall(fixed)
        if typed:
            failures.append(f"templates/{tmpl}: numbers typed into fixed text: {typed}")
        else:
            report.append(f"templates/{tmpl}: no numbers outside placeholders")

    # 4. word limit
    limit = N["parameters"]["summary_max_words"]
    words = word_count((ROOT / "outputs" / "summary.md").read_text())
    report.append(f"outputs/summary.md: {words} words (limit {limit})")
    if words > limit:
        failures.append(f"outputs/summary.md has {words} words, over the {limit}-word limit")

    # 5. figures exist
    for stem in ("fig1_trials_per_year", "fig2_stop_reasons"):
        for ext in ("png", "svg"):
            f = ROOT / "outputs" / f"{stem}.{ext}"
            if not f.exists() or f.stat().st_size == 0:
                failures.append(f"missing figure: {f.relative_to(ROOT)}")
    report.append("figures: checked PNG and SVG for both")

    print("\n".join(report))
    if failures:
        print("\nFAILED:")
        print("\n".join(f"  - {x}" for x in failures))
        sys.exit(1)
    print("\nPASSED: all checks")


if __name__ == "__main__":
    main()
