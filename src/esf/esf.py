from datetime import date
import pandas as pd
import requests


_FIDS = {
    "price_dayahead": {"induflex": "nz2c8co"},
}
_BASE_URL = "https://ies-tools.ait.ac.at/esf"


class Forecast:
    """Represents a forecast returned by the ESF API."""

    def __init__(self, data: dict):
        """
        Initialize a Forecast from a raw API response dict.

        Args:
            data: Dict with keys ``times`` (list of ISO timestamps),
                  ``values`` (dict of column -> list of values), and
                  ``columns`` (dict of column -> metadata).
        """
        self._data = pd.DataFrame(index=pd.to_datetime(data["times"]), data=data["values"])
        self._entries: dict[str, dict] = data["columns"]
        self._quantiles = self._parse_quantiles()

    @property
    def quantiles(self) -> list[float]:
        """Return the sorted list of available quantile levels."""
        return sorted(self._quantiles.keys())

    def get(self, mode: str, value: float | None = None) -> pd.Series:
        """
        Retrieve a forecast series by mode.

        Args:
            mode:  Retrieval mode. Currently only ``"quantile"`` is supported.
            value: The quantile level to retrieve (e.g. ``0.5`` for the median).
                   Required when *mode* is ``"quantile"``.

        Returns:
            A :class:`pandas.Series` indexed by timestamp.

        Raises:
            ValueError: If *mode* is unknown, or *value* is missing / not available.
        """
        if mode == "quantile":
            if value is None:
                raise ValueError("Value must be provided for quantile mode.")
            if value not in self._quantiles:
                raise ValueError(f"Quantile value {value} not found. Available quantiles: {self.quantiles}")
            return self._data[self._quantiles[value]]
        else:
            raise ValueError(f"Unknown mode '{mode}'. Supported modes: 'quantile'.")

    def _parse_quantiles(self) -> dict[float, str]:
        """Parse column metadata and return a mapping of quantile level -> column name."""
        quantiles = dict()
        for col, entry in self._entries.items():
            if entry.get("type") == "quantile":
                quantiles[entry["value"]] = col
        return quantiles


class EnergySystemForecastClient:
    """Client for fetching energy system forecasts from the ESF API."""

    def __init__(self, parameter: str, model: str, api_key: str):
        """
        Initialize the client.

        Args:
            parameter: Forecast parameter name.
            model:     Model identifier within the parameter.
            api_key:   API key used for authentication.

        Raises:
            ValueError: If *parameter* or *model* is not recognised.
        """
        self._headers: dict[str, str] = {"X-API-Key": api_key, "Content-Type": "application/json"}

        if parameter not in _FIDS:
            raise ValueError(f"Parameter '{parameter}' not found in forecast IDs.")
        if model not in _FIDS[parameter]:
            raise ValueError(f"Model '{model}' not found for parameter '{parameter}'.")
        self.fid: str = _FIDS[parameter][model]

    def fetch(self, dates: list[date] | None = None) -> list[date]:
        """
        Query the API for which dates have forecast data available.

        Args:
            dates: Optional list of specific dates to check. If empty or
                   ``None``, the API returns all available dates.

        Returns:
            List of :class:`datetime.date` objects for which forecasts exist.

        Raises:
            requests.HTTPError: If the API request fails.
        """
        dates: list[date] = dates or []
        response = requests.post(
            f"{_BASE_URL}/fetch", json=dict(fid=self.fid, dates=[d.isoformat() for d in dates]), headers=self._headers
        )
        response.raise_for_status()
        response = response.json()
        available_dates = response.get("available_dates", [])
        return [date.fromisoformat(d) for d in available_dates]

    def pull(self, dates: list[date]) -> Forecast:
        """
        Download forecast data for the given dates.

        Args:
            dates: Dates to retrieve.

        Returns:
            A :class:`Forecast` instance containing the downloaded data.

        Raises:
            requests.HTTPError: If the API request fails.
        """
        dates: list[date] = dates or []
        response = requests.post(
            f"{_BASE_URL}/pull", json=dict(fid=self.fid, dates=[d.isoformat() for d in dates]), headers=self._headers
        )
        response.raise_for_status()
        return Forecast(response.json())
