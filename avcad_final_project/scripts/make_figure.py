"""
make_figure.py

Builds the project's main figure: a Fig.3-style ("Estimated losses from
individual extreme heat events by carbon majors", Mankin et al. 2025, Nature)
dot-and-whisker chart, adapted to Portugal, comparing the two candidate 2022
and 2023 Iberian heatwave events side by side.

Reads:  data/processed/portugal_event_losses_by_carbon_major.csv
Writes: figures/fig3_portugal_heat_losses.png
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"
FIGURES = ROOT / "figures"
FIGURES.mkdir(parents=True, exist_ok=True)

TOP_N = 15

ENTITY_COLORS = {
    "investor_owned": "#3F7CAC",
    "state_owned": "#D1603D",
    "nation_state": "#6B4E71",
}
ENTITY_LABELS = {
    "investor_owned": "Investor-owned company",
    "state_owned": "State-owned company",
    "nation_state": "Nation-state producer",
}


def fmt_eur(x, _):
    """Format axis ticks as €1M, €500K, etc. for readability."""
    if x >= 1_000_000:
        return f"€{x/1_000_000:.0f}M"
    elif x >= 1_000:
        return f"€{x/1_000:.0f}K"
    else:
        return f"€{x:.0f}"


def plot_panel(ax, df, title):
    df = df.sort_values("loss_eur_central", ascending=False).head(TOP_N)
    df = df.sort_values("loss_eur_central")  # ascending for horizontal barh order

    y = range(len(df))
    colors = [ENTITY_COLORS[t] for t in df["entity_type"]]

    xerr_low = (df["loss_eur_central"] - df["loss_eur_low"]).clip(lower=0)
    xerr_high = (df["loss_eur_high"] - df["loss_eur_central"]).clip(lower=0)

    ax.errorbar(
        df["loss_eur_central"], y,
        xerr=[xerr_low, xerr_high],
        fmt="none", ecolor="grey", elinewidth=1, capsize=2, zorder=1,
    )
    ax.scatter(df["loss_eur_central"], y, c=colors, s=55, zorder=2, edgecolor="white", linewidth=0.5)

    ax.set_yticks(list(y))
    ax.set_yticklabels(df["entity"], fontsize=8)
    ax.set_xscale("log")
    ax.set_xlabel("Estimated attributable loss to Portugal")
    ax.set_title(title, fontsize=10, loc="left")
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(fmt_eur))
    ax.grid(axis="x", which="major", linestyle="--", linewidth=0.5, alpha=0.5)
    ax.spines[["top", "right"]].set_visible(False)


def main():
    df = pd.read_csv(PROCESSED / "portugal_event_losses_by_carbon_major.csv")

    events = df[["event_id", "event_name"]].drop_duplicates().sort_values("event_id")

    fig, axes = plt.subplots(1, 2, figsize=(12, 7.2), sharey=False)

    for ax, (_, ev) in zip(axes, events.iterrows()):
        sub = df[df.event_id == ev.event_id]
        plot_panel(ax, sub, f"{ev.event_id}: {ev.event_name}")

    handles = [
        plt.Line2D([0], [0], marker="o", color="w", markerfacecolor=c, markersize=8, label=ENTITY_LABELS[k])
        for k, c in ENTITY_COLORS.items()
    ]
    fig.legend(handles=handles, loc="lower center", ncol=3, frameon=False, bbox_to_anchor=(0.5, -0.02))

    fig.suptitle(
        "Estimated losses from individual extreme heat events by carbon majors—Portugal",
        fontsize=13, fontweight="bold", x=0.02, ha="left", y=0.985,
    )
    fig.text(
        0.02, 0.915,
        "Top 15 carbon majors by apportioned share of national event loss. Whiskers show illustrative low–high\n"
        "attributable-intensity scenarios (see docs/methodology.md). Adapted, simplified reproduction of Fig. 3 in\n"
        "Mankin et al. (2025, Nature) — not the original published estimates.",
        fontsize=8, color="dimgrey", va="top",
    )

    plt.tight_layout(rect=[0, 0.04, 1, 0.84])
    out_path = FIGURES / "fig3_portugal_heat_losses.png"
    plt.savefig(out_path, dpi=200)
    print(f"Saved figure to {out_path}")


if __name__ == "__main__":
    main()
