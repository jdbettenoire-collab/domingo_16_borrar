from datetime import timezone
import os
from pathlib import Path

BASE_DIRECTORY = Path(__file__).resolve().parent
CHARTS_DIRECTORY = BASE_DIRECTORY / "charts"
os.environ.setdefault("MPLCONFIGDIR", str(CHARTS_DIRECTORY / ".matplotlib"))

import matplotlib

matplotlib.use("Agg")

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd


DATA_FILE = BASE_DIRECTORY / "data" / "AAPL_2026-06-26_1H.csv"


def create_close_chart(data_file: Path = DATA_FILE) -> Path:
    data_file = Path(data_file)
    data = pd.read_csv(data_file, skipinitialspace=True)
    data.columns = data.columns.str.strip()

    required_columns = {"timestamp", "close"}
    missing_columns = required_columns.difference(data.columns)
    if missing_columns:
        raise ValueError(
            f"Faltan columnas en el CSV: {', '.join(sorted(missing_columns))}"
        )

    data["timestamp"] = pd.to_datetime(data["timestamp"], utc=True)
    data["close"] = pd.to_numeric(data["close"])
    data = data.sort_values("timestamp")

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(
        data["timestamp"],
        data["close"],
        color="#2563eb",
        linewidth=2,
        marker="o",
        markersize=5,
    )
    ax.set_title("AAPL - Precio de cierre (1H)", fontsize=16, pad=15)
    ax.set_xlabel("Hora (UTC)")
    ax.set_ylabel("Precio de cierre (USD)")
    ax.grid(True, linestyle="--", alpha=0.35)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M", tz=timezone.utc))

    fig.autofmt_xdate()
    fig.tight_layout()

    CHARTS_DIRECTORY.mkdir(parents=True, exist_ok=True)
    output_file = CHARTS_DIRECTORY / f"{data_file.stem}_close.png"
    fig.savefig(output_file, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return output_file


if __name__ == "__main__":
    chart_path = create_close_chart()
    print(f"Chart guardado en: {chart_path}")
