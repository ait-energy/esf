# Energy System Forecasts

Proof of concept research API to access energy system related forecasts.

> This is work in progress, improvements and more extensive documentation will follow!

## Setup

Setup a new Python environment using `uv`, e.g., by running:

```bash
uv init
```

Then install this by running

```bash
uv add git+https://github.com/ait-energy/esf
```

## Basic usage

```python
import datetime
from src.esf.esf import EnergySystemForecastClient

# Create a client
esfc = EnergySystemForecastClient(parameter="some_param", model="some_model", api_key="XXXXX")

# Check which dates have available forecasts
avail = esfc.fetch()
print(avail)

# ... which also supports checking only explicit dates
dates = [datetime.date(2026, 6, 15), datetime.date(2026, 6, 16)]
avail = esfc.fetch(dates)
print(avail)
```

You can then pull forecasts for a selection of dates:

```python
forecast = esfc.pull(avail)

# Check which quantiles this forecast contains
print(forecast.quantiles)

# Then get the median
print(forecast.get(mode="quantile", value=0.5))
```
