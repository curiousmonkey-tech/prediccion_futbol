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


def estimate_lambdas(features: pd.DataFrame, h2h: dict[str, float]) -> dict[str, float]:
    portugal = features[features["team"] == "Portugal"].iloc[0]
    spain = features[features["team"] == "Spain"].iloc[0]

    portugal_quality = quality_factor(portugal.total_market_value_eur, spain.total_market_value_eur)
    spain_quality = quality_factor(spain.total_market_value_eur, portugal.total_market_value_eur)

    portugal_recent = (portugal.home_goals_for_avg + spain.away_goals_against_avg) / 2
    spain_recent = (spain.away_goals_for_avg + portugal.home_goals_against_avg) / 2

    if h2h["matches"]:
        portugal_h2h = h2h["portugal_goals_avg"]
        spain_h2h = h2h["spain_goals_avg"]
        portugal_lambda = 0.78 * portugal_recent + 0.22 * portugal_h2h
        spain_lambda = 0.78 * spain_recent + 0.22 * spain_h2h
    else:
        portugal_lambda = portugal_recent
        spain_lambda = spain_recent

    portugal_lambda *= portugal_quality
    spain_lambda *= spain_quality

    return {
        "Portugal": max(0.15, float(portugal_lambda)),
        "Spain": max(0.15, float(spain_lambda)),
        "portugal_quality_factor": float(portugal_quality),
        "spain_quality_factor": float(spain_quality),
    }


def scoreline_probabilities(lambda_home: float, lambda_away: float, max_goals: int = 8) -> pd.DataFrame:
    rows = []
    for home_goals in range(max_goals + 1):
        for away_goals in range(max_goals + 1):
            probability = poisson_pmf(home_goals, lambda_home) * poisson_pmf(away_goals, lambda_away)
            rows.append(
                {
                    "score": f"{home_goals}-{away_goals}",
                    "portugal_goals": home_goals,
                    "spain_goals": away_goals,
                    "poisson_probability": probability,
                }
            )
    df = pd.DataFrame(rows)
    df["poisson_probability_pct"] = df["poisson_probability"] * 100
    return df.sort_values("poisson_probability", ascending=False).reset_index(drop=True)
