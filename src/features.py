from __future__ import annotations

import pandas as pd


TEAMS = ("Portugal", "Spain")


def team_matches(results: pd.DataFrame, team: str) -> pd.DataFrame:
    mask = (results["home_team"] == team) | (results["away_team"] == team)
    df = results.loc[mask].copy()
    df["team"] = team
    df["is_home"] = df["home_team"].eq(team)
    df["goals_for"] = df.apply(lambda r: r.home_score if r.home_team == team else r.away_score, axis=1)
    df["goals_against"] = df.apply(lambda r: r.away_score if r.home_team == team else r.home_score, axis=1)
    df["opponent"] = df.apply(lambda r: r.away_team if r.home_team == team else r.home_team, axis=1)
    return df.sort_values("date")


def head_to_head(results: pd.DataFrame) -> pd.DataFrame:
    mask = results["home_team"].isin(TEAMS) & results["away_team"].isin(TEAMS)
    return results.loc[mask].copy().sort_values("date")


def summarize_team(results: pd.DataFrame, team: str, recent_matches: int = 30) -> dict[str, float]:
    matches = team_matches(results, team)
    recent = matches.tail(recent_matches)
    home = matches[matches["is_home"]].tail(recent_matches)
    away = matches[~matches["is_home"]].tail(recent_matches)

    return {
        "team": team,
        "matches_used": float(len(recent)),
        "goals_for_avg": float(recent["goals_for"].mean()),
        "goals_against_avg": float(recent["goals_against"].mean()),
        "home_goals_for_avg": float(home["goals_for"].mean()) if len(home) else float(recent["goals_for"].mean()),
        "home_goals_against_avg": float(home["goals_against"].mean()) if len(home) else float(recent["goals_against"].mean()),
        "away_goals_for_avg": float(away["goals_for"].mean()) if len(away) else float(recent["goals_for"].mean()),
        "away_goals_against_avg": float(away["goals_against"].mean()) if len(away) else float(recent["goals_against"].mean()),
    }


def build_feature_summary(results: pd.DataFrame, quality: pd.DataFrame, recent_matches: int = 30) -> pd.DataFrame:
    summary = pd.DataFrame([summarize_team(results, team, recent_matches) for team in TEAMS])
    return summary.merge(quality, on="team", how="left")


def h2h_summary(results: pd.DataFrame) -> dict[str, float]:
    h2h = head_to_head(results)
    if h2h.empty:
        return {"matches": 0.0, "portugal_goals_avg": 0.0, "spain_goals_avg": 0.0}

    portugal_goals = h2h.apply(lambda r: r.home_score if r.home_team == "Portugal" else r.away_score, axis=1)
    spain_goals = h2h.apply(lambda r: r.home_score if r.home_team == "Spain" else r.away_score, axis=1)
    return {
        "matches": float(len(h2h)),
        "portugal_goals_avg": float(portugal_goals.mean()),
        "spain_goals_avg": float(spain_goals.mean()),
    }
