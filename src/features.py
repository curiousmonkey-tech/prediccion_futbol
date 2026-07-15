from __future__ import annotations

from math import exp

import pandas as pd


def team_matches(results: pd.DataFrame, team: str) -> pd.DataFrame:
    mask = (results["home_team"] == team) | (results["away_team"] == team)
    df = results.loc[mask].copy()
    df["team"] = team
    df["is_home"] = df["home_team"].eq(team)
    df["goals_for"] = df.apply(lambda r: r.home_score if r.home_team == team else r.away_score, axis=1)
    df["goals_against"] = df.apply(lambda r: r.away_score if r.home_team == team else r.home_score, axis=1)
    df["opponent"] = df.apply(lambda r: r.away_team if r.home_team == team else r.home_team, axis=1)
    return df.sort_values("date")


def head_to_head(results: pd.DataFrame, home_team: str, away_team: str) -> pd.DataFrame:
    teams = (home_team, away_team)
    mask = results["home_team"].isin(teams) & results["away_team"].isin(teams)
    return results.loc[mask].copy().sort_values("date")


def summarize_team(results: pd.DataFrame, team: str, recent_matches: int = 30) -> dict[str, float]:
    matches = team_matches(results, team)
    recent = matches.tail(recent_matches)
    home = matches[matches["is_home"]].tail(recent_matches)
    away = matches[~matches["is_home"]].tail(recent_matches)
    max_date = results["date"].max()
    weighted = recent.copy()
    weighted["days_ago"] = (max_date - weighted["date"]).dt.days.clip(lower=0)
    weighted["weight"] = weighted["days_ago"].apply(lambda days: exp(-days / 90))
    recent_90 = matches[matches["date"] >= max_date - pd.Timedelta(days=90)]
    recent_90_points = recent_90.apply(lambda r: 3 if r.goals_for > r.goals_against else 1 if r.goals_for == r.goals_against else 0, axis=1)

    weighted_for = float((weighted["goals_for"] * weighted["weight"]).sum() / weighted["weight"].sum()) if len(weighted) else 0.0
    weighted_against = float((weighted["goals_against"] * weighted["weight"]).sum() / weighted["weight"].sum()) if len(weighted) else 0.0

    return {
        "team": team,
        "matches_used": float(len(recent)),
        "goals_for_avg": float(recent["goals_for"].mean()),
        "goals_against_avg": float(recent["goals_against"].mean()),
        "weighted_goals_for_avg": weighted_for,
        "weighted_goals_against_avg": weighted_against,
        "recent_90_matches": float(len(recent_90)),
        "recent_90_goals_for_avg": float(recent_90["goals_for"].mean()) if len(recent_90) else 0.0,
        "recent_90_goals_against_avg": float(recent_90["goals_against"].mean()) if len(recent_90) else 0.0,
        "recent_90_points_per_match": float(recent_90_points.mean()) if len(recent_90_points) else 0.0,
        "home_goals_for_avg": float(home["goals_for"].mean()) if len(home) else float(recent["goals_for"].mean()),
        "home_goals_against_avg": float(home["goals_against"].mean()) if len(home) else float(recent["goals_against"].mean()),
        "away_goals_for_avg": float(away["goals_for"].mean()) if len(away) else float(recent["goals_for"].mean()),
        "away_goals_against_avg": float(away["goals_against"].mean()) if len(away) else float(recent["goals_against"].mean()),
    }


def build_feature_summary(results: pd.DataFrame, quality: pd.DataFrame, home_team: str, away_team: str, recent_matches: int = 30) -> pd.DataFrame:
    summary = pd.DataFrame([summarize_team(results, team, recent_matches) for team in (home_team, away_team)])
    return summary.merge(quality, on="team", how="left")


def h2h_summary(results: pd.DataFrame, home_team: str, away_team: str) -> dict[str, float]:
    h2h = head_to_head(results, home_team, away_team)
    if h2h.empty:
        return {"matches": 0.0, "home_goals_avg": 0.0, "away_goals_avg": 0.0}

    home_goals = h2h.apply(lambda r: r.home_score if r.home_team == home_team else r.away_score, axis=1)
    away_goals = h2h.apply(lambda r: r.home_score if r.home_team == away_team else r.away_score, axis=1)
    return {
        "matches": float(len(h2h)),
        "home_goals_avg": float(home_goals.mean()),
        "away_goals_avg": float(away_goals.mean()),
    }
