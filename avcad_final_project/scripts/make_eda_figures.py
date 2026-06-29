"""
make_eda_figures.py

Builds three exploratory data analysis (EDA) figures for the AVCAD final
project, complementing the main fig3_portugal_heat_losses.png produced by
make_figure.py (Hannah).

Figures produced:
  1. fig_entity_type_breakdown.png  — total central loss by entity type (E1 & E2)
  2. fig_e1_vs_e2_comparison.png   — side-by-side E1 vs E2 for top 15 entities
  3. fig_loss_distribution.png     — loss distribution across all 122 carbon majors

Reads:  data/processed/portugal_event_losses_by_carbon_major.csv
Writes: figures/fig_entity_type_breakdown.png
        figures/fig_e1_vs_e2_comparison.png
        figures/fig_loss_distribution.png

Style follows make_figure.py (same colours, fonts, spine treatment).
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"
FIGURES = ROOT / "figures"
FIGURES.mkdir(parents=True, exist_ok=True)

# ── Colour palette — identical to make_figure.py ────────────────────────────
ENTITY_COLORS = {
    "investor_owned": "#3F7CAC",
    "state_owned":    "#D1603D",
    "nation_state":   "#6B4E71",
}
ENTITY_LABELS = {
    "investor_owned": "Investor-owned company",
    "state_owned":    "State-owned company",
    "nation_state":   "Nation-state producer",
}

# ── Shared style helpers ─────────────────────────────────────────────────────
def apply_style(ax):
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="x", which="major", linestyle="--", linewidth=0.5, alpha=0.5)

def fmt_eur(x, _):
    return f"{x:,.0f}"

def shared_legend(fig):
    handles = [
        plt.Line2D([0], [0], marker="o", color="w",
                   markerfacecolor=c, markersize=8, label=ENTITY_LABELS[k])
        for k, c in ENTITY_COLORS.items()
    ]
    fig.legend(handles=handles, loc="lower center", ncol=3,
               frameon=False, bbox_to_anchor=(0.5, -0.06))


# ════════════════════════════════════════════════════════════════════════════
# FIGURE 1 — Breakdown by entity type
# ════════════════════════════════════════════════════════════════════════════
def make_entity_type_breakdown(df):
    fig, axes = plt.subplots(1, 2, figsize=(12, 5), sharey=False)

    for ax, eid in zip(axes, ["E1", "E2"]):
        sub = df[df.event_id == eid].copy()
        grouped = (
            sub.groupby("entity_type")[["loss_eur_low", "loss_eur_central", "loss_eur_high"]]
            .sum()
            .reset_index()
            .sort_values("loss_eur_central")
        )
        colors = [ENTITY_COLORS[t] for t in grouped["entity_type"]]
        y = range(len(grouped))

        xerr_low  = (grouped["loss_eur_central"] - grouped["loss_eur_low"]).clip(lower=0)
        xerr_high = (grouped["loss_eur_high"] - grouped["loss_eur_central"]).clip(lower=0)

        ax.barh(list(y), grouped["loss_eur_central"], color=colors, alpha=0.85, zorder=2)
        ax.errorbar(
            grouped["loss_eur_central"], list(y),
            xerr=[xerr_low, xerr_high],
            fmt="none", ecolor="grey", elinewidth=1.2, capsize=4, zorder=3,
        )
        ax.set_yticks(list(y))
        ax.set_yticklabels([ENTITY_LABELS[t] for t in grouped["entity_type"]], fontsize=9)
        ax.set_xscale("log")
        ax.set_xlabel("Total attributable loss to Portugal (EUR)", fontsize=9)
        ev_name = df[df.event_id == eid]["event_name"].iloc[0]
        ax.set_title(f"{eid}: {ev_name}", fontsize=10, loc="left")
        ax.xaxis.set_major_formatter(mticker.FuncFormatter(fmt_eur))
        apply_style(ax)

    fig.suptitle(
        "Attributable loss by entity type — Portugal",
        fontsize=13, fontweight="bold", x=0.02, ha="left", y=1.01,
    )
    fig.text(
        0.02, -0.04,
        "Total central-scenario loss summed across all tracked entities of each type. "
        "Whiskers show low–high attributable-intensity scenarios.\n"
        "Adapted from Mankin et al. (2025, Nature) — not the original published estimates.",
        fontsize=8, color="dimgrey",
    )
    plt.tight_layout()
    out = FIGURES / "fig_entity_type_breakdown.png"
    fig.savefig(out, dpi=200, bbox_inches="tight")
    print(f"Saved: {out}")


# ════════════════════════════════════════════════════════════════════════════
# FIGURE 2 — E1 vs E2 comparison (top 15 entities)
# ════════════════════════════════════════════════════════════════════════════
def make_e1_vs_e2_comparison(df):
    e1 = df[df.event_id == "E1"].set_index("entity")
    e2 = df[df.event_id == "E2"].set_index("entity")
    common = e1.index.intersection(e2.index)

    top15 = (
        e1.loc[common, "loss_eur_central"]
        .sort_values(ascending=False)
        .head(15)
        .index.tolist()
    )
    e1_top = e1.loc[top15].sort_values("loss_eur_central")
    e2_top = e2.loc[top15].reindex(e1_top.index)

    fig, ax = plt.subplots(figsize=(10, 6.5))
    y = np.arange(len(top15))
    height = 0.35

    ax.barh(y - height / 2, e1_top["loss_eur_central"], height,
            color="#7BAFD4", alpha=0.9, label="E1: April 2023", zorder=2)
    ax.barh(y + height / 2, e2_top["loss_eur_central"], height,
            color="#E8956D", alpha=0.9, label="E2: July 2022", zorder=2)

    ax.errorbar(
        e1_top["loss_eur_central"], y - height / 2,
        xerr=[(e1_top["loss_eur_central"] - e1_top["loss_eur_low"]).clip(lower=0),
              (e1_top["loss_eur_high"] - e1_top["loss_eur_central"]).clip(lower=0)],
        fmt="none", ecolor="grey", elinewidth=0.8, capsize=2, zorder=3,
    )
    ax.errorbar(
        e2_top["loss_eur_central"], y + height / 2,
        xerr=[(e2_top["loss_eur_central"] - e2_top["loss_eur_low"]).clip(lower=0),
              (e2_top["loss_eur_high"] - e2_top["loss_eur_central"]).clip(lower=0)],
        fmt="none", ecolor="grey", elinewidth=0.8, capsize=2, zorder=3,
    )

    ax.set_yticks(y)
    ax.set_yticklabels(e1_top.index.tolist(), fontsize=8)
    ax.set_xscale("log")
    ax.set_xlabel("Estimated attributable loss to Portugal (EUR)", fontsize=9)
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(fmt_eur))
    ax.legend(frameon=False, fontsize=9)
    apply_style(ax)

    fig.suptitle(
        "E1 vs E2: estimated losses by carbon major — Portugal",
        fontsize=13, fontweight="bold", x=0.02, ha="left",
    )
    fig.text(
        0.02, -0.03,
        "Top 15 carbon majors ranked by E1 central-scenario loss. "
        "E2 (July 2022) consistently higher due to longer duration (12 vs 3 days).\n"
        "Whiskers show low–high attributable-intensity scenarios. "
        "Adapted from Mankin et al. (2025, Nature) — not the original published estimates.",
        fontsize=8, color="dimgrey",
    )
    plt.tight_layout()
    out = FIGURES / "fig_e1_vs_e2_comparison.png"
    fig.savefig(out, dpi=200, bbox_inches="tight")
    print(f"Saved: {out}")


# ════════════════════════════════════════════════════════════════════════════
# FIGURE 3 — Loss distribution across all 122 carbon majors
# ════════════════════════════════════════════════════════════════════════════
def make_loss_distribution(df):
    fig, axes = plt.subplots(1, 2, figsize=(12, 5), sharey=False)

    for ax, eid in zip(axes, ["E1", "E2"]):
        sub = df[df.event_id == eid].copy()
        sub = sub.sort_values("loss_eur_central", ascending=False).reset_index(drop=True)
        colors = [ENTITY_COLORS[t] for t in sub["entity_type"]]

        for i, row in sub.iterrows():
            ax.plot([i, i], [row["loss_eur_low"], row["loss_eur_high"]],
                    color="grey", linewidth=0.5, alpha=0.5, zorder=1)

        ax.scatter(range(len(sub)), sub["loss_eur_central"],
                   c=colors, s=30, alpha=0.85, zorder=2,
                   edgecolor="white", linewidth=0.3)

        ax.set_yscale("log")
        ax.set_xlabel("Carbon major rank (by central loss, descending)", fontsize=9)
        ax.set_ylabel("Attributable loss to Portugal (EUR)", fontsize=9)
        ev_name = df[df.event_id == eid]["event_name"].iloc[0]
        ax.set_title(f"{eid}: {ev_name}", fontsize=10, loc="left")
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(fmt_eur))
        apply_style(ax)

    shared_legend(fig)

    fig.suptitle(
        "Distribution of estimated losses across all 122 carbon majors — Portugal",
        fontsize=13, fontweight="bold", x=0.02, ha="left",
    )
    fig.text(
        0.02, -0.05,
        "Each dot is one carbon major. Vertical lines show low–high attributable-intensity scenarios. "
        "Log scale highlights the heavy tail.\n"
        "Adapted from Mankin et al. (2025, Nature) — not the original published estimates.",
        fontsize=8, color="dimgrey",
    )
    plt.tight_layout()
    out = FIGURES / "fig_loss_distribution.png"
    fig.savefig(out, dpi=200, bbox_inches="tight")
    print(f"Saved: {out}")


# ── Main ─────────────────────────────────────────────────────────────────────
def main():
    df = pd.read_csv(PROCESSED / "portugal_event_losses_by_carbon_major.csv")
    make_entity_type_breakdown(df)
    make_e1_vs_e2_comparison(df)
    make_loss_distribution(df)


if __name__ == "__main__":
    main()
