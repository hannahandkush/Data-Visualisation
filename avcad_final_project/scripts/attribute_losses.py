"""
attribute_losses.py

Estimates the economic losses Portugal incurred from two extreme-heat events
(April 2023 Iberian heatwave; July 2022 Iberian heatwave) that are attributable
to anthropogenic climate change, and apportions that national loss across the
fossil-fuel and cement "carbon majors" tracked by the Carbon Majors database
(InfluenceMap / Climate Accountability Institute), in proportion to each
entity's share of cumulative global CO2 emissions (1854-2022).

This is a deliberately simplified, transparent adaptation of the method used in:
  - Callahan, C.W. & Mankin, J.S. (2022) "National attribution of historical
    climate damages." Climatic Change 172, 40.
  - Mankin, J.S. et al. (2025) "Carbon majors and the scientific case for
    climate liability." Nature (Fig. 3: "Estimated losses from individual
    extreme heat events by carbon majors.")

The full published methodology runs each carbon major's emissions through a
reduced-complexity climate model (FaIR/OSCAR) to get a company-specific GMST
contribution, pattern-scales that to local temperature, and feeds the result
through an empirical damage function with bootstrapped uncertainty. That
chain requires proprietary/unreleased 7TB-scale datasets and model runs that
are out of scope for this course project. The simplification made here -
apportioning a single national event-loss total by each entity's share of
*cumulative historical emissions* rather than by its modeled share of *GMST
contribution* - is documented in detail in docs/methodology.md. The two are
highly correlated in the published literature (e.g. Quilcaille et al. 2025),
which is why this proxy is defensible for an illustrative, course-scale
reproduction, but it is NOT equivalent to the peer-reviewed figure.

Outputs:
  data/processed/portugal_event_losses_by_carbon_major.csv
"""

import pandas as pd
import numpy as np
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"
PROCESSED.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# 1. Burke, Hsiang & Miguel (2015, Nature) pooled temperature-growth response
#    g(T) = b1*T + b2*T^2 , optimum at T* = -b1/(2*b2) = 13C
#    Coefficients as commonly cited in the replication literature
#    (incl. Callahan & Mankin 2022's own BHM short-run specification).
# ---------------------------------------------------------------------------
B1 = 0.0127      # per degree C
B2 = -0.0005     # per degree C^2
T_OPTIMUM = -B1 / (2 * B2)  # ~12.7-13C, sanity check against Burke et al. 2015

# Portugal mainland mean annual temperature, 1991-2020 climatological normal
# (IPMA - Instituto Portugues do Mar e da Atmosfera; derived from published
# mean daily min ~10C / mean daily max ~21C -> annual mean ~15.5C).
T_PT_NORMAL = 15.5

def marginal_damage_slope(T):
    """dG/dT of the BHM quadratic response function, evaluated at T."""
    return B1 + 2 * B2 * T


def event_to_annual_equivalent_dT(dT_event, duration_days):
    """
    Converts an event's attributable temperature anomaly into an
    annual-mean-equivalent temperature perturbation, following the
    duration-weighted aggregation logic of Burke et al. (2015) Eq. (1)
    (daily/instantaneous impacts aggregate into the annual macro signal
    in proportion to the fraction of the year's unit-days they occupy).
    """
    return dT_event * (duration_days / 365.0)


def national_event_loss(dT_event, duration_days, gdp_eur, T_normal=T_PT_NORMAL):
    """
    Estimated national GDP loss (EUR) attributable to climate change for a
    single heat event, via a first-order (marginal) approximation of the
    BHM damage function around Portugal's normal annual temperature.
    """
    dT_annual_equiv = event_to_annual_equivalent_dT(dT_event, duration_days)
    slope = marginal_damage_slope(T_normal)          # dG/dT, typically negative for PT
    delta_g = slope * dT_annual_equiv                 # fractional growth effect
    loss_eur = -delta_g * gdp_eur                     # positive loss when delta_g<0
    return loss_eur


def main():
    events = pd.read_csv(RAW / "portugal_heat_events.csv")
    gdp = pd.read_csv(RAW / "portugal_gdp.csv")
    cmajors = pd.read_csv(RAW / "carbon_majors_top122_1854_2022.csv")

    # normalise emissions shares so they sum to 1 across the *tracked* entities
    # (the database covers ~72% of global CO2; we keep shares relative to the
    # tracked universe so the apportioned losses sum exactly to the national
    # event loss - documented explicitly as a scope simplification).
    cmajors["share_of_tracked"] = (
        cmajors["emissions_MtCO2e_1854_2022"] / cmajors["emissions_MtCO2e_1854_2022"].sum()
    )

    duration_days = {"E1": 3, "E2": 12}

    records = []
    for _, ev in events.iterrows():
        eid = ev["event_id"]
        gdp_year = ev["gdp_year"]
        gdp_eur = gdp.loc[gdp["year"] == gdp_year, "gdp_eur_billion"].iloc[0] * 1e9
        dur = duration_days[eid]

        # central / low / high attributable-intensity scenarios
        # (see docs/methodology.md for literature basis & caveats on bounds)
        if eid == "E1":
            dT_scn = {"low": 2.0, "central": 2.5, "high": 3.5}
        else:
            dT_scn = {"low": 1.25, "central": 1.25, "high": 2.5}

        loss_scn = {
            k: national_event_loss(v, dur, gdp_eur) for k, v in dT_scn.items()
        }

        for _, c in cmajors.iterrows():
            share = c["share_of_tracked"]
            records.append({
                "event_id": eid,
                "event_name": ev["event_name"],
                "entity": c["entity"],
                "entity_type": c["entity_type"],
                "pct_global_CO2_1854_2022": c["pct_global_CO2"],
                "loss_eur_low": loss_scn["low"] * share,
                "loss_eur_central": loss_scn["central"] * share,
                "loss_eur_high": loss_scn["high"] * share,
            })

    out = pd.DataFrame.from_records(records)
    out_path = PROCESSED / "portugal_event_losses_by_carbon_major.csv"
    out.to_csv(out_path, index=False)

    # ---- console summary / sanity checks (feeds Task #7) ----
    print(f"Wrote {len(out)} rows to {out_path}\n")
    for eid, name in events[["event_id", "event_name"]].values:
        sub = out[out.event_id == eid]
        total = sub["loss_eur_central"].sum()
        print(f"{eid} ({name}): total national loss (central) = EUR {total:,.0f}")
        top5 = sub.sort_values("loss_eur_central", ascending=False).head(5)
        for _, r in top5.iterrows():
            print(f"   {r.entity:35s} EUR {r.loss_eur_central:>12,.0f}  "
                  f"[{r.loss_eur_low:,.0f} - {r.loss_eur_high:,.0f}]")
        print()


if __name__ == "__main__":
    main()
