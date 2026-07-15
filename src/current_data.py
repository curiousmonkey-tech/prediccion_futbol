from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import requests


BASE_URL = "https://site.api.espn.com/apis/site/v2/sports/soccer/fifa.world"
HEADERS = {"User-Agent": "Mozilla/5.0", "Accept": "application/json"}


class EspnCurrentDataClient:
    def __init__(self, cache_dir: Path, force_refresh: bool = False, max_requests: int = 40) -> None:
        self.cache_dir = cache_dir
        self.force_refresh = force_refresh
        self.max_requests = max_requests
        self.requests_made = 0
        self.cache_hits = 0
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _cache_path(self, endpoint: str, params: dict[str, Any] | None = None) -> Path:
        payload = json.dumps({"endpoint": endpoint, "params": params or {}}, sort_keys=True)
        key = hashlib.sha256(payload.encode("utf-8")).hexdigest()[:24]
        return self.cache_dir / f"{endpoint.replace('/', '_')}_{key}.json"

    def get(self, endpoint: str, params: dict[str, Any] | None = None) -> dict[str, Any] | None:
        cache_path = self._cache_path(endpoint, params)
        if cache_path.exists() and not self.force_refresh:
            self.cache_hits += 1
            return json.loads(cache_path.read_text(encoding="utf-8"))
        if self.requests_made >= self.max_requests:
            return None

        response = requests.get(f"{BASE_URL}/{endpoint}", params=params, headers=HEADERS, timeout=30)
        self.requests_made += 1
        response.raise_for_status()
        data = response.json()
        cache_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        return data

    def teams(self) -> list[dict[str, Any]]:
        data = self.get("teams") or {}
        leagues = data.get("sports", [{}])[0].get("leagues", [])
        if not leagues:
            return []
        return [row.get("team", {}) for row in leagues[0].get("teams", [])]

    def team_id(self, team_name: str) -> str | None:
        normalized = team_name.lower()
        for team in self.teams():
            names = {team.get("displayName", "").lower(), team.get("name", "").lower(), team.get("location", "").lower()}
            if normalized in names:
                return str(team.get("id"))
        return None

    def schedule(self, team_id: str) -> list[dict[str, Any]]:
        data = self.get(f"teams/{team_id}/schedule") or {}
        return data.get("events", [])

    def summary(self, event_id: str) -> dict[str, Any] | None:
        return self.get("summary", {"event": event_id})


def stat_value(stats: list[dict[str, Any]], name: str) -> float:
    for row in stats:
        if row.get("name") == name:
            raw = row.get("value", row.get("displayValue", 0))
            try:
                return float(str(raw).replace("%", ""))
            except ValueError:
                return 0.0
    return 0.0


def score_value(raw: Any) -> float:
    if isinstance(raw, dict):
        raw = raw.get("value", raw.get("displayValue", 0))
    try:
        return float(str(raw).replace("%", ""))
    except (TypeError, ValueError):
        return 0.0


def team_score(event: dict[str, Any], team_name: str) -> tuple[float, float] | None:
    competitors = event.get("competitions", [{}])[0].get("competitors", [])
    selected = None
    opponent = None
    for competitor in competitors:
        display_name = competitor.get("team", {}).get("displayName")
        if display_name == team_name:
            selected = competitor
        else:
            opponent = competitor
    if not selected or not opponent:
        return None
    return score_value(selected.get("score", 0)), score_value(opponent.get("score", 0))


def finished_events(events: list[dict[str, Any]], team_name: str, limit: int) -> list[dict[str, Any]]:
    finished = []
    for event in events:
        competition = event.get("competitions", [{}])[0]
        status = competition.get("status", {}).get("type", {})
        if not status.get("completed"):
            continue
        if team_score(event, team_name) is None:
            continue
        finished.append(event)
    return sorted(finished, key=lambda row: row.get("date", ""), reverse=True)[:limit]


def team_stats_from_summary(summary: dict[str, Any], team_name: str) -> dict[str, float] | None:
    for team_block in summary.get("boxscore", {}).get("teams", []):
        if team_block.get("team", {}).get("displayName") != team_name:
            continue
        stats = team_block.get("statistics", [])
        return {
            "shots": stat_value(stats, "totalShots"),
            "shots_on_goal": stat_value(stats, "shotsOnTarget"),
            "possession": stat_value(stats, "possessionPct"),
            "corners": stat_value(stats, "wonCorners"),
            "yellow_cards": stat_value(stats, "yellowCards"),
            "red_cards": stat_value(stats, "redCards"),
            "fouls": stat_value(stats, "foulsCommitted"),
            "pass_pct": stat_value(stats, "passPct"),
        }
    return None


def build_current_team_summary(team_name: str, events: list[dict[str, Any]], summaries: dict[str, dict[str, Any]]) -> dict[str, float | str]:
    rows = []
    for event in events:
        score = team_score(event, team_name)
        summary = summaries.get(str(event.get("id")))
        if not score or not summary:
            continue
        stats = team_stats_from_summary(summary, team_name) or {}
        rows.append({"goals_for": score[0], "goals_against": score[1], **stats})

    if not rows:
        return {"team": team_name, "current_recent_matches": 0.0, "current_attacking_index": 1.0, "current_defensive_index": 1.0}

    def avg(key: str) -> float:
        return sum(float(row.get(key, 0.0)) for row in rows) / len(rows)

    goals_for = avg("goals_for")
    goals_against = avg("goals_against")
    shots_on_goal = avg("shots_on_goal")
    clean_sheet_rate = sum(1 for row in rows if float(row.get("goals_against", 0.0)) == 0.0) / len(rows)
    attacking = max(0.85, min(1.15, 1 + ((shots_on_goal - 4.0) * 0.025) + ((goals_for - 1.3) * 0.04)))
    defensive = max(0.85, min(1.15, 1 + ((1.2 - goals_against) * 0.04) + ((clean_sheet_rate - 0.25) * 0.04)))
    return {
        "team": team_name,
        "current_recent_matches": float(len(rows)),
        "current_goals_for_avg": goals_for,
        "current_goals_against_avg": goals_against,
        "current_shots_avg": avg("shots"),
        "current_shots_on_goal_avg": shots_on_goal,
        "current_possession_avg": avg("possession"),
        "current_corners_avg": avg("corners"),
        "current_yellow_cards_avg": avg("yellow_cards"),
        "current_fouls_avg": avg("fouls"),
        "current_clean_sheet_rate": clean_sheet_rate,
        "current_attacking_index": attacking,
        "current_defensive_index": defensive,
    }


def player_stat(stats: list[dict[str, Any]], name: str) -> float:
    for row in stats:
        if row.get("name") == name:
            return float(row.get("value", 0.0) or 0.0)
    return 0.0


def build_current_player_summary(team_name: str, summaries: dict[str, dict[str, Any]], player_limit: int) -> Any:
    import pandas as pd

    players: dict[str, dict[str, Any]] = {}
    for summary in summaries.values():
        for team_roster in summary.get("rosters", []):
            if team_roster.get("team", {}).get("displayName") != team_name:
                continue
            for player in team_roster.get("roster", []):
                athlete = player.get("athlete", {})
                player_id = str(athlete.get("id"))
                stats = player.get("stats", [])
                row = players.setdefault(
                    player_id,
                    {
                        "team": team_name,
                        "player": athlete.get("displayName", "unknown"),
                        "position": player.get("position", {}).get("abbreviation", ""),
                        "appearances": 0.0,
                        "starts": 0.0,
                        "goals": 0.0,
                        "assists": 0.0,
                        "shots": 0.0,
                        "shots_on_goal": 0.0,
                        "yellow_cards": 0.0,
                        "red_cards": 0.0,
                    },
                )
                row["appearances"] += player_stat(stats, "appearances") or (1.0 if player.get("active") else 0.0)
                row["starts"] += 1.0 if player.get("starter") else 0.0
                row["goals"] += player_stat(stats, "totalGoals")
                row["assists"] += player_stat(stats, "goalAssists")
                row["shots"] += player_stat(stats, "totalShots")
                row["shots_on_goal"] += player_stat(stats, "shotsOnTarget")
                row["yellow_cards"] += player_stat(stats, "yellowCards")
                row["red_cards"] += player_stat(stats, "redCards")

    rows = []
    for row in players.values():
        form_score = row["appearances"] * 1.2 + row["starts"] * 1.5 + row["goals"] * 1.1 + row["assists"] * 0.8 + row["shots_on_goal"] * 0.15 - row["yellow_cards"] * 0.15 - row["red_cards"] * 0.7
        rows.append({**row, "player_form_score": max(0.0, float(form_score))})

    df = pd.DataFrame(rows)
    if df.empty:
        return pd.DataFrame(columns=["team", "player", "position", "appearances", "starts", "goals", "assists", "shots", "shots_on_goal", "yellow_cards", "red_cards", "player_form_score"])
    return df.sort_values(["starts", "appearances", "player_form_score"], ascending=False).head(player_limit).reset_index(drop=True)


def fetch_current_context(cache_dir: Path, home_team: str, away_team: str, recent_matches: int, player_limit: int, force_refresh: bool, disabled: bool, max_requests: int = 40) -> tuple[Any, Any, dict[str, Any]]:
    import pandas as pd

    if disabled:
        return pd.DataFrame(), pd.DataFrame(), {"enabled": False, "reason": "Desactivado con --no-current-data", "requests_made": 0, "cache_hits": 0}

    client = EspnCurrentDataClient(cache_dir, force_refresh=force_refresh, max_requests=max_requests)
    try:
        events_by_team: dict[str, list[dict[str, Any]]] = {}
        for team in (home_team, away_team):
            team_id = client.team_id(team)
            if not team_id:
                events_by_team[team] = []
                continue
            events_by_team[team] = finished_events(client.schedule(team_id), team, recent_matches)

        event_ids = sorted({str(event.get("id")) for events in events_by_team.values() for event in events if event.get("id")})
        summaries = {event_id: summary for event_id in event_ids if (summary := client.summary(event_id))}
        team_summary = pd.DataFrame([build_current_team_summary(team, events_by_team[team], summaries) for team in (home_team, away_team)])
        players = pd.concat([build_current_player_summary(team, summaries, player_limit) for team in (home_team, away_team)], ignore_index=True)
        return team_summary, players, {"enabled": True, "reason": "ESPN actual disponible", "requests_made": client.requests_made, "cache_hits": client.cache_hits, "event_ids": event_ids}
    except Exception as exc:
        return pd.DataFrame(), pd.DataFrame(), {"enabled": False, "reason": f"ESPN actual no disponible: {exc}", "requests_made": client.requests_made, "cache_hits": client.cache_hits}
