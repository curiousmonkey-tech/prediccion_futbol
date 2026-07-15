from __future__ import annotations

from math import exp, factorial

import pandas as pd


def poisson_pmf(k: int, lam: float) -> float:
    return (lam**k * exp(-lam)) / factorial(k)


def quality_factor(team_value: float, opponent_value: float, weight: float = 0.12) -> float:
    if team_value <= 0 or opponent_value <= 0:
        return 1.0
    ratio = team_value / opponent_value
    return max(0.88, min(1.12, 1 + (ratio - 1) * weight))


def row_value(row: pd.Series, key: str, default: float) -> float:
    value = row.get(key, default)
    if pd.isna(value):
        return default
    return float(value)


def clamp(value: float, lower: float = 0.85, upper: float = 1.15) -> float:
    return max(lower, min(upper, value))


def estimate_lambdas(features: pd.DataFrame, h2h: dict[str, float], home_team: str, away_team: str) -> dict[str, float]:
    home = features[features["team"] == home_team].iloc[0]
    away = features[features["team"] == away_team].iloc[0]

    home_quality = quality_factor(home.total_market_value_eur, away.total_market_value_eur)
    away_quality = quality_factor(away.total_market_value_eur, home.total_market_value_eur)

    home_base = (home.home_goals_for_avg + away.away_goals_against_avg) / 2
    away_base = (away.away_goals_for_avg + home.home_goals_against_avg) / 2
    home_weighted = (row_value(home, "weighted_goals_for_avg", home.home_goals_for_avg) + row_value(away, "weighted_goals_against_avg", away.away_goals_against_avg)) / 2
    away_weighted = (row_value(away, "weighted_goals_for_avg", away.away_goals_for_avg) + row_value(home, "weighted_goals_against_avg", home.home_goals_against_avg)) / 2
    home_recent = 0.45 * home_base + 0.55 * home_weighted
    away_recent = 0.45 * away_base + 0.55 * away_weighted

    if h2h["matches"]:
        home_h2h = h2h["home_goals_avg"]
        away_h2h = h2h["away_goals_avg"]
        home_lambda = 0.78 * home_recent + 0.22 * home_h2h
        away_lambda = 0.78 * away_recent + 0.22 * away_h2h
    else:
        home_lambda = home_recent
        away_lambda = away_recent

    home_current_factor = clamp(row_value(home, "current_attacking_index", 1.0) / row_value(away, "current_defensive_index", 1.0), 0.88, 1.12)
    away_current_factor = clamp(row_value(away, "current_attacking_index", 1.0) / row_value(home, "current_defensive_index", 1.0), 0.88, 1.12)
    home_player_factor = row_value(home, "player_form_index", 1.0)
    away_player_factor = row_value(away, "player_form_index", 1.0)

    home_lambda *= home_quality * home_current_factor * home_player_factor
    away_lambda *= away_quality * away_current_factor * away_player_factor

    return {
        home_team: max(0.15, float(home_lambda)),
        away_team: max(0.15, float(away_lambda)),
        "home_quality_factor": float(home_quality),
        "away_quality_factor": float(away_quality),
        "home_current_factor": float(home_current_factor),
        "away_current_factor": float(away_current_factor),
        "home_player_form_factor": float(home_player_factor),
        "away_player_form_factor": float(away_player_factor),
    }


def scoreline_probabilities(lambda_home: float, lambda_away: float, max_goals: int = 8) -> pd.DataFrame:
    rows = []
    for home_goals in range(max_goals + 1):
        for away_goals in range(max_goals + 1):
            probability = poisson_pmf(home_goals, lambda_home) * poisson_pmf(away_goals, lambda_away)
            rows.append(
                {
                    "score": f"{home_goals}-{away_goals}",
                    "home_goals": home_goals,
                    "away_goals": away_goals,
                    "poisson_probability": probability,
                }
            )
    df = pd.DataFrame(rows)
    df["poisson_probability_pct"] = df["poisson_probability"] * 100
    return df.sort_values("poisson_probability", ascending=False).reset_index(drop=True)
