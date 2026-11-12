"""Step 5: fill the text templates with values from outputs/numbers.json.

Usage:
    .venv/bin/python src/report.py

templates/summary.md.tmpl -> outputs/summary.md
templates/README.md.tmpl  -> README.md

Placeholders look like {N[included]:,} or {T[enrol_median]}; the short names
are sections of numbers.json (see NAMESPACES). The templates themselves contain
no numbers, so every number in the output comes from numbers.json.
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"
TEMPLATES = ROOT / "templates"
TARGETS = {
    "summary.md.tmpl": OUT / "summary.md",
    "README.md.tmpl": ROOT / "README.md",
}


def namespaces(N):
    return {
        "N": N,                                   # everything
        "P": N["parameters"],                     # fixed settings (window, thresholds)
        "D": N["derived"],                        # shares of all included trials
        "T": N["text"],                           # values picked for the summary text
        "R": N["results_posted"],
        "I": N["immpact"],
        "A": N["asia"],
        "H": N["asia"]["hong_kong"],
    }


def render(template_name, N=None):
    if N is None:
        N = json.loads((OUT / "numbers.json").read_text())
    return (TEMPLATES / template_name).read_text().format(**namespaces(N))


def main():
    N = json.loads((OUT / "numbers.json").read_text())
    for name, target in TARGETS.items():
        target.write_text(render(name, N))
        print(f"wrote {target.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
