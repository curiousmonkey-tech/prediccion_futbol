from __future__ import annotations

import re
from dataclasses import dataclass

import pandas as pd
import requests
from bs4 import BeautifulSoup


TRANSFERMARKT_URLS = {
    "Portugal": "https://www.transfermarkt.com/portugal/startseite/verein/3300",
    "Spain": "https://www.transfermarkt.com/spanien/startseite/verein/3375",
}

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}


@dataclass(frozen=True)
class SquadQuality:
    team: str
    players: int
    total_market_value_eur: float
    average_market_value_eur: float
    scraped_from: str


def parse_market_value(value: str) -> float:
    clean = value.replace("€", "").replace(" ", "").strip()
    clean = clean.replace("m", "M").replace("th.", "K").replace("Th.", "K")
    match = re.search(r"([0-9]+(?:[.,][0-9]+)?)([MK])?", clean)
    if not match:
        return 0.0
    number = float(match.group(1).replace(",", "."))
    suffix = match.group(2)
    if suffix == "M":
        return number * 1_000_000
    if suffix == "K":
        return number * 1_000
    return number


def scrape_transfermarkt_squad(team: str) -> tuple[pd.DataFrame, SquadQuality]:
    url = TRANSFERMARKT_URLS[team]
    response = requests.get(url, headers=HEADERS, timeout=45)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "lxml")
    rows = soup.select("table.items tbody tr.odd, table.items tbody tr.even")
    players: list[dict[str, object]] = []

    for row in rows:
        cells = row.select("td")
        value_cell = row.select_one("td.rechts.hauptlink")

        if len(cells) < 8 or not value_cell:
            continue

        name = cells[3].get_text(" ", strip=True)
        position = cells[4].get_text(" ", strip=True)
        date_age = cells[5].get_text(" ", strip=True)
        age_match = re.search(r"\((\d+)\)", date_age)
        market_value_text = value_cell.get_text(strip=True)
        players.append(
            {
                "team": team,
                "player": name,
                "position": position,
                "age": int(age_match.group(1)) if age_match else None,
                "market_value_text": market_value_text,
                "market_value_eur": parse_market_value(market_value_text),
                "source": url,
            }
        )

    df = pd.DataFrame(players)
    if df.empty:
        raise RuntimeError(f"No se pudieron extraer jugadores de Transfermarkt para {team}: {url}")

    total = float(df["market_value_eur"].sum())
    quality = SquadQuality(
        team=team,
        players=int(len(df)),
        total_market_value_eur=total,
        average_market_value_eur=float(df["market_value_eur"].mean()),
        scraped_from=url,
    )
    return df, quality


def scrape_squads() -> tuple[pd.DataFrame, pd.DataFrame]:
    squad_frames = []
    quality_rows = []
    for team in ("Portugal", "Spain"):
        squad, quality = scrape_transfermarkt_squad(team)
        squad_frames.append(squad)
        quality_rows.append(quality.__dict__)
    return pd.concat(squad_frames, ignore_index=True), pd.DataFrame(quality_rows)
