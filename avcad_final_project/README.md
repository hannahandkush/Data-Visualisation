# Estimated losses from individual extreme heat events by carbon majors — Portugal

Final project (AVCAD). A simplified, fully-documented Portugal-focused reproduction of the reasoning behind Fig. 3 in Mankin et al. (2025, *Nature*), *"Carbon majors and the scientific case for climate liability,"* comparing two real Iberian heatwave events:

- **April 2023** (3-day record heatwave; World Weather Attribution study)
- **July 2022** (12-day heatwave; Portugal's all-time temperature record + 1,000+ excess deaths)

See **[docs/methodology.md](docs/methodology.md)** for full sources, the loss-attribution method, a check against the published global figures, and limitations.

## Structure

```
data/raw/         Source data (heat event stats, GDP, carbon majors emissions)
data/processed/   Output of attribute_losses.py
scripts/          attribute_losses.py (analysis) + make_figure.py (plot)
figures/          fig3_portugal_heat_losses.png
docs/             methodology.md
```

## Run it

```
pip install pandas matplotlib
python scripts/attribute_losses.py
python scripts/make_figure.py
```

## Key sources

- Mankin, J.S. et al. (2025). Carbon majors and the scientific case for climate liability. *Nature*. https://doi.org/10.1038/s41586-025-08751-3
- Callahan, C.W. & Mankin, J.S. (2022). National attribution of historical climate damages. *Climatic Change* 172, 40. https://doi.org/10.1007/s10584-022-03387-y
- Burke, M., Hsiang, S.M. & Miguel, E. (2015). Global non-linear effect of temperature on economic production. *Nature* 527, 235–239.
- World Weather Attribution (2023). Extreme April heat in Spain, Portugal, Morocco and Algeria almost impossible without climate change.
- Carbon Majors Database, Launch Report (InfluenceMap, April 2024). carbonmajors.org
