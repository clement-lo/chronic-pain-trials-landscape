"""Step 4: the two figures, as 300-dpi PNG and SVG, from outputs/numbers.json.

Usage:
    .venv/bin/python src/figures.py

Colours: the first two slots of a categorical palette checked with a colour-
vision-deficiency validator (blue #2a78d6, orange #eb6834: adjacent-pair CVD
Delta E 24.7, all checks pass on a light surface). Figure 1 uses one hue only,
because each panel is labelled by its title rather than by colour.
"""

import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
from rules import GROUP_LABELS  # noqa: E402
from stop_reasons import ORDER as STOP_ORDER  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"

BLUE, ORANGE = "#2a78d6", "#eb6834"
SURFACE, INK, INK2, GRID = "#ffffff", "#0b0b0b", "#52514e", "#e6e5e0"
plt.rcParams.update({
    "font.family": ["Helvetica", "Arial", "DejaVu Sans"],
    "font.size": 9, "axes.edgecolor": INK2, "axes.labelcolor": INK2,
    "xtick.color": INK2, "ytick.color": INK2, "text.color": INK,
    "axes.spines.top": False, "axes.spines.right": False,
    "figure.facecolor": SURFACE, "axes.facecolor": SURFACE,
    "svg.fonttype": "none",  # keep text as text in the SVG
})


def save(fig, stem, dpi):
    for ext in ("png", "svg"):
        fig.savefig(OUT / f"{stem}.{ext}", dpi=dpi, bbox_inches="tight", facecolor=SURFACE)
    plt.close(fig)


def fig_trials_per_year(N):
    groups = ["CPSP", "Fibromyalgia", "MSK", "Neuropathic", "CRPS", "Multiple"]
    years = sorted(N["by_start_year"]["All"], key=int)
    fig, axes = plt.subplots(2, 3, figsize=(9, 5.2), sharex=True)
    for ax, g in zip(axes.flat, groups):
        vals = [N["by_start_year"][g][y] for y in years]
        ax.bar([int(y) for y in years], vals, width=0.72, color=BLUE, edgecolor=SURFACE, linewidth=0.8)
        ax.set_title(f"{GROUP_LABELS[g]}\n(n = {N['by_group'][g]:,})", fontsize=9, loc="left", color=INK)
        ax.grid(axis="y", color=GRID, linewidth=0.6)
        ax.set_axisbelow(True)
        ax.set_ylim(0, max(vals) * 1.15)
        ax.tick_params(length=0)
        ax.set_xticks([int(years[0]), int(years[len(years) // 2]), int(years[-1])])
    for ax in axes[:, 0]:
        ax.set_ylabel("Trials")
    p = N["parameters"]
    fig.text(0.0, -0.06,
             f"Interventional chronic pain trials by start year and condition group, "
             f"n = {N['included']:,} trials starting {p['start_year_min']}–{p['start_year_max']}.\n"
             f"Each panel has its own y-axis. The latest years include anticipated start dates "
             f"({N['start_date_type'].get('ESTIMATED', 0):,} trials overall).\n"
             f"Data from ClinicalTrials.gov, accessed {N['pull_date']} (registry data dated {N['data_date']}).",
             ha="left", va="top", fontsize=8, color=INK2)
    fig.tight_layout(h_pad=1.6)
    fig.align_ylabels(axes[:, 0])
    save(fig, "fig1_trials_per_year", p["figure_dpi"])


def fig_stop_reasons(N):
    tw = N["stop_reasons"]["terminated_withdrawn"]
    cats = [c for c in STOP_ORDER if c != "Not stated"]
    cats = sorted(cats, key=lambda c: tw["TERMINATED"][c] + tw["WITHDRAWN"][c])
    cats = ["Not stated"] + cats  # keep 'Not stated' at the bottom
    term = [tw["TERMINATED"][c] for c in cats]
    wdr = [tw["WITHDRAWN"][c] for c in cats]
    n_t, n_w = sum(tw["TERMINATED"].values()), sum(tw["WITHDRAWN"].values())
    fig, ax = plt.subplots(figsize=(7.2, 4.2))
    y = range(len(cats))
    ax.barh(y, term, height=0.62, color=BLUE, edgecolor=SURFACE, linewidth=1.5,
            label=f"Terminated (n = {n_t:,})")
    ax.barh(y, wdr, left=term, height=0.62, color=ORANGE, edgecolor=SURFACE, linewidth=1.5,
            label=f"Withdrawn (n = {n_w:,})")
    for i, (a, b) in enumerate(zip(term, wdr)):
        ax.text(a + b + 1.5, i, f"{a + b}", va="center", fontsize=8.5, color=INK)
    ax.set_yticks(list(y), cats)
    ax.set_xlabel("Trials")
    ax.grid(axis="x", color=GRID, linewidth=0.6)
    ax.set_axisbelow(True)
    ax.tick_params(length=0)
    ax.set_xlim(0, max(a + b for a, b in zip(term, wdr)) * 1.12)
    ax.legend(loc="lower right", frameon=False, fontsize=8.5)
    fig.text(0.0, -0.02,
             f"Main stated reason for stopping, n = {n_t + n_w:,} trials: terminated (n = {n_t:,}) "
             f"and withdrawn (n = {n_w:,}).\nOne main reason per trial, by fixed precedence: COVID-19, "
             f"safety or futility, low accrual, funding,\nsponsor, site or investigator, other "
             f"(keyword rules in src/stop_reasons.py).\n"
             f"Data from ClinicalTrials.gov, accessed {N['pull_date']} (registry data dated {N['data_date']}).",
             ha="left", va="top", fontsize=8, color=INK2)
    fig.tight_layout()
    save(fig, "fig2_stop_reasons", N["parameters"]["figure_dpi"])


def main():
    N = json.loads((OUT / "numbers.json").read_text())
    fig_trials_per_year(N)
    fig_stop_reasons(N)
    print("wrote outputs/fig1_trials_per_year.{png,svg} and outputs/fig2_stop_reasons.{png,svg}")


if __name__ == "__main__":
    main()
