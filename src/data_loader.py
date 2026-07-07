from __future__ import annotations

from pathlib import Path

import pandas as pd
import requests


RESULTS_URL = "https://raw.githubusercontent.com/martj42/international_results/master/results.csv"


def download_results(raw_dir: Path) -> Path:
    raw_dir.mkdir(parents=True, exist_ok=True)
    output = raw_dir / "international_results.csv"
    response = requests.get(RESULTS_URL, timeout=60)
    response.raise_for_status()
    output.write_bytes(response.content)
    return output


def load_results(raw_dir: Path) -> pd.DataFrame:
    csv_path = raw_dir / "international_results.csv"
    if not csv_path.exists():
        csv_path = download_results(raw_dir)

    df = pd.read_csv(csv_path)
    df["date"] = pd.to_datetime(df["date"])
    df = df.dropna(subset=["home_score", "away_score"]).copy()
    df["home_score"] = df["home_score"].astype(int)
    df["away_score"] = df["away_score"].astype(int)
    df["neutral"] = df["neutral"].astype(str).str.upper().eq("TRUE")
    return df.sort_values("date").reset_index(drop=True)
