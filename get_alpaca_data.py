from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pandas as pd
import requests
from dotenv import load_dotenv

from config import ALPACA_DATA_ENDPOINT, TIMEFRAME


SYMBOL = "AAPL"
NEW_YORK_TIMEZONE = "America/New_York"
OUTPUT_DIRECTORY = Path(__file__).resolve().parent / "data"


def get_alpaca_data(symbol: str = SYMBOL) -> pd.DataFrame:
    """Descarga las velas del último día de mercado disponible."""
    load_dotenv(Path(__file__).resolve().parent / ".env", override=True)

    api_key = os.getenv("ALPACA_API_KEY")
    secret_key = os.getenv("ALPACA_SECRET_KEY")
    if not api_key or not secret_key:
        raise RuntimeError(
            "Faltan ALPACA_API_KEY o ALPACA_SECRET_KEY en el fichero .env."
        )

    end = datetime.now(timezone.utc)
    start = end - timedelta(days=10)
    url = f"{ALPACA_DATA_ENDPOINT.rstrip('/')}/stocks/bars"
    headers = {
        "APCA-API-KEY-ID": api_key,
        "APCA-API-SECRET-KEY": secret_key,
    }
    params = {
        "symbols": symbol.upper(),
        "timeframe": TIMEFRAME,
        "start": start.isoformat(),
        "end": end.isoformat(),
        "limit": 10000,
        "adjustment": "raw",
        "feed": "iex",
        "sort": "asc",
    }

    response = requests.get(url, headers=headers, params=params, timeout=30)
    if response.status_code == 401:
        raise RuntimeError(
            "Alpaca rechazó las credenciales. Revisa ALPACA_API_KEY y "
            "ALPACA_SECRET_KEY en el fichero .env."
        )
    response.raise_for_status()
    bars = response.json().get("bars", {}).get(symbol.upper(), [])
    if not bars:
        raise RuntimeError(f"Alpaca no devolvió datos para {symbol.upper()}.")

    data = pd.DataFrame(bars).rename(
        columns={
            "t": "timestamp",
            "o": "open",
            "h": "high",
            "l": "low",
            "c": "close",
            "v": "volume",
            "n": "trade_count",
            "vw": "vwap",
        }
    )
    data["timestamp"] = pd.to_datetime(data["timestamp"], utc=True)
    market_dates = data["timestamp"].dt.tz_convert(NEW_YORK_TIMEZONE).dt.date
    latest_market_date = market_dates.max()
    return data.loc[market_dates == latest_market_date].reset_index(drop=True)


def save_alpaca_data(data: pd.DataFrame, symbol: str = SYMBOL) -> Path:
    """Guarda los datos descargados en un CSV."""
    market_date = (
        data["timestamp"]
        .dt.tz_convert(NEW_YORK_TIMEZONE)
        .dt.strftime("%Y-%m-%d")
        .iloc[0]
    )
    OUTPUT_DIRECTORY.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUT_DIRECTORY / f"{symbol.upper()}_{market_date}_{TIMEFRAME}.csv"
    data.to_csv(output_path, index=False)
    return output_path


if __name__ == "__main__":
    apple_data = get_alpaca_data()
    saved_path = save_alpaca_data(apple_data)
    print(apple_data.to_string(index=False))
    print(f"\nDatos guardados en: {saved_path}")
