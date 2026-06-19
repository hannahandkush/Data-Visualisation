# Methodology, Sources & Limitations

**Project:** Estimated losses from individual extreme heat events by carbon majors — Portugal
**Course:** AVCAD, final project
**Target figure replicated (in spirit):** Fig. 3, Mankin, J.S. et al. (2025) "Carbon majors and the scientific case for climate liability," *Nature*. https://doi.org/10.1038/s41586-025-08751-3

---

## 1. Goal and scope

The published Fig. 3 in Mankin et al. (2025) shows, for a global sample of extreme heat events, the share of economic loss attributable to each of ~100+ "carbon majors" (fossil fuel and cement producers), derived by running each entity's historical emissions through a reduced-complexity climate model, pattern-scaling the resulting warming to the affected region, and applying an empirical temperature-growth damage function with bootstrapped uncertainty.

This project narrows that approach to **Portugal**, comparing two real, well-documented Iberian heatwave events side by side:

- **E1 — April 2023 Iberian heatwave** (26–28 April 2023): a record-breaking 3-day event, independently and rigorously attributed by World Weather Attribution.
- **E2 — July 2022 Iberian heatwave** (7–18 July 2022): a longer, deadlier event that set Portugal's all-time national temperature record and caused substantial excess mortality.

The full Mankin et al. (2025) pipeline (scope 1+3 emissions → FaIR/OSCAR climate model → pattern scaling → bootstrapped empirical damages) depends on a 7TB+ dataset and model runs released only on IEEE DataPort, and is out of reach for a course project. **The simplifications below are deliberate and are the main thing this project should be evaluated on**, not just the resulting chart.

---

## 2. Data sources

| Input | Source | Notes |
|---|---|---|
| April 2023 event statistics | World Weather Attribution (2023), *"Extreme April heat in Spain, Portugal, Morocco and Algeria almost impossible without climate change"* | Peer-reviewed-equivalent rapid attribution study. Probability ratio "at least a factor of 100"; attributable intensity "at least 2°C cooler in a 1.2°C colder world." National April record: 36.9°C (Portugal). Return period ≈1-in-400 years. |
| July 2022 event statistics | DGS Portugal (Directorate-General of Health) excess-mortality reporting, via The Portugal News / Anadolu Agency; anthropogenic warming contribution from the BAMS 2024 paper, *"The Summer Heatwave 2022 over Western Europe: An Attribution to Anthropogenic Climate Change"* (Lentink et al., BAMS, 2024) | National July record: 47.4°C (Pinhão, 14 July 2022). Excess mortality: 1,063 deaths (7–18 July window) to 1,380 deaths (2–18 July window). The BAMS storyline-attribution result (anthropogenic contribution ≈1.25°C on average, up to 5.7°C regionally) is for **Western Europe as a whole**, not Portugal specifically — see limitations. |
| Portugal GDP | INE (Statistics Portugal), National Accounts, current prices | 2022: €242.3bn. 2023: €267.4bn. |
| Carbon majors emissions | InfluenceMap/Carbon Majors, *"The Carbon Majors Database: Launch Report"* (April 2024), Appendix 1 (Table 12: cumulative emissions 1854–2022 by entity) | The live per-record CSV downloads at carbonmajors.org now require a login ("Please log in for access to more detailed datasets"), so this project uses the entity-level cumulative totals published in the official PDF launch report instead — the same underlying database, at a coarser (but fully sufficient and properly cited) level of aggregation. 122 entities, covering 72% of global fossil fuel & cement CO2 emissions since 1751. |
| Damage function | Burke, Hsiang & Miguel (2015), *"Global non-linear effect of temperature on economic production,"* Nature 527, 235–239; functional form follows Callahan & Mankin (2022), *Climatic Change* 172, 40, Eq. (1) | Pooled quadratic specification, optimum at 13°C. Coefficients used: β1≈0.0127 °C⁻¹, β2≈-0.0005 °C⁻². These are the widely-cited values consistent with the paper's reported optimum (the original regression tables in the Nature PDF are image-only and not machine-extractable; the values used here reproduce the published 13°C optimum and are the same ones used in derivative replications of BHM, including Callahan & Mankin's). |

---

## 3. Loss attribution method

**Step 1 — National event loss.**
Each event's attributable temperature anomaly (ΔT, °C) is converted into an annual-mean-equivalent perturbation by weighting it by the event's duration share of the year (ΔT_event × days/365), following the same daily-to-annual aggregation logic set out in Burke et al. (2015), Eq. (1). This annualized perturbation is passed through the marginal (first-derivative) effect of the BHM quadratic damage function, evaluated at Portugal's 1991–2020 mean annual temperature (≈15.5°C, IPMA), to give a fractional GDP-growth effect, which is then multiplied by Portugal's GDP in the event year to obtain a national loss in euros.

**Step 2 — Apportionment to carbon majors.**
The national event loss is split across the 122 tracked carbon majors in direct proportion to each entity's share of *cumulative global CO2 emissions, 1854–2022* (from the Carbon Majors Launch Report). This replaces Mankin et al.'s full climate-model-based "share of GMST contribution," which cannot be reproduced here. The two measures are highly correlated in the literature (see e.g. Quilcaille et al. 2025, Nature, on carbon-major heatwave attribution), so emissions share is a reasonable, transparent, and fully reproducible proxy — but it is **not** the same calculation, and will systematically misstate any entity whose emissions-to-warming-contribution ratio differs from the cohort average (e.g. due to different gas mixes, timing of emissions, or methane content).

**Step 3 — Uncertainty.**
Each event is run under low/central/high attributable-intensity scenarios (see `scripts/attribute_losses.py`), reflecting the published ranges (or, where only a one-sided bound was published — as for the April 2023 event's "at least 2°C" — an illustrative upper scenario). This is a simple sensitivity range, not a formally propagated statistical confidence interval (the published studies' own bootstrapped/model-ensemble uncertainty was not available to re-derive).

---

## 4. Sanity check against the published global figures (Task #7)

Mankin et al. (2025) report that Chevron's emissions "very likely caused between US $791 billion and $3.6 trillion in heat-related losses" globally, cumulated over 1991–2020 (29 years, many events worldwide).

- Midpoint: ≈$2.2 trillion → ≈$73.2 billion/year, averaged across all global heat events in all countries.
- Portugal's GDP is ≈0.27% of global GDP.
- A naive GDP-share scaling of Chevron's global annual average loss would imply an "average annual Portugal share" of ≈$196 million/year.
- This project's single-event Chevron estimate for the 12-day July 2022 event is ≈€1.1 million — roughly **170x smaller**.

This gap is expected and informative, not a red flag:

1. The naive scaling above is a *full-year, all-events* average; this project estimates *one* multi-day event, which is a small fraction of a year's cumulative heat exposure.
2. This project's damage channel is limited to the contemporaneous output/growth effect captured by the BHM curve. It excludes mortality, healthcare costs, capital destruction, and sector-specific losses (agriculture, tourism) that materially inflate the real-world cost of a heatwave — and that the July 2022 event's death toll (1,063+ excess deaths) shows are far from negligible here.
3. The linearized, marginal approximation used to keep this project tractable is, by construction, a conservative lower bound relative to the full non-linear, multi-channel damage estimates in the peer-reviewed literature.

**Conclusion:** the estimates in this project are directionally sensible and several orders of magnitude below the (much larger, multi-channel, full-year) published global figures, in the direction expected given the simplifications made. They should be read as an illustrative lower-bound, output-only estimate of two specific events — not as a substitute for the peer-reviewed company-level loss estimates.

---

## 5. Key limitations

- **Emissions-share ≠ GMST-contribution-share.** The central simplification (Section 3, Step 2) substitutes a static historical-emissions proxy for the dynamic, time-resolved climate-model attribution used in the source paper.
- **July 2022 attribution statistic is not Portugal-specific.** The BAMS (2024) anthropogenic-contribution estimate (≈1.25°C average, up to 5.7°C regionally) is for Western Europe as a whole; no dedicated WWA-style rapid attribution study with a Portugal-specific probability ratio for this event was located during research for this project.
- **Single damage channel.** Only the contemporaneous GDP-growth effect is modeled; mortality, health system costs, infrastructure, agriculture, and tourism losses are excluded, despite being significant for the July 2022 event in particular.
- **Linear/marginal approximation.** Using the first derivative of the BHM curve around Portugal's normal temperature is only a local approximation; it will understate damages from very extreme short-duration temperature spikes whose instantaneous severity is far from the annual mean.
- **Carbon Majors data granularity.** Entity-level cumulative totals (1854–2022) were used in place of the year/commodity-level CSVs, because the live downloads now require an account login; this does not affect the entity ranking used for apportionment but means year-specific emissions weighting (e.g., weighting 2022 emissions more heavily for the 2022 event) was not applied — every event uses the same all-time cumulative emissions share.
- **No formal bootstrapped uncertainty.** Low/central/high scenarios are illustrative, not a reproduction of the source papers' Monte Carlo/bootstrap confidence intervals.

---

## 6. Reproducing this project

```
pip install pandas matplotlib
python scripts/attribute_losses.py   # writes data/processed/portugal_event_losses_by_carbon_major.csv
python scripts/make_figure.py        # writes figures/fig3_portugal_heat_losses.png
```
