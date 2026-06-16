# Energy System Forecasts

Proof of concept research API to access energy system related forecasts.

> This is work in progress, improvements and more extensive documentation will follow!

## Getting Started

### Setup

Setup a new Python environment using `uv`, e.g., by running:

```bash
uv init
```

Then install this by running

```bash
uv add git+https://github.com/ait-energy/esf
```

### Basic usage

```python
import datetime
from esf import EnergySystemForecastClient

# Create a client
esfc = EnergySystemForecastClient(parameter="some_param", model="some_model", api_key="XXXXX")

# Check which dates have available forecasts
avail = esfc.fetch()
print(avail)
# > [datetime.date(2026, 6, 1), datetime.date(2026, 6, 2),
# > ...,
# > datetime.date(2026, 7, 2), datetime.date(2026, 7, 3)]

# ... which also supports checking only explicit dates
dates = [datetime.date(2026, 6, 15), datetime.date(2026, 6, 16)]
avail = esfc.fetch(dates)
print(avail)
# > [datetime.date(2026, 6, 15), datetime.date(2026, 6, 16)]

# Pull forecasts for a selection of dates
forecast = esfc.pull(avail)

# Check which quantiles this forecast contains
print(forecast.quantiles)
# > [0.025, 0.05, 0.1, 0.5, 0.9, 0.95, 0.975]

# Then get the median
print(forecast.get(mode="quantile", value=0.5))
# > 2026-06-15 00:00:00+02:00    122.05
# > 2026-06-15 00:15:00+02:00    108.87
# >                               ...  
# > 2026-06-16 23:30:00+02:00    139.27
# > 2026-06-16 23:45:00+02:00    133.63
# > Name: 3, Length: 192, dtype: float64
```

## Development

Format using:

```bash
uvx ruff format .
```
