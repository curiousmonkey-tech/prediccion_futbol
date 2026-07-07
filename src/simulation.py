from __future__ import annotations

import numpy as np
import pandas as pd


def monte_carlo_scorelines(lambda_home: float, lambda_away: float, simulations: int = 100_000, seed: int = 20260706) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    home_goals = rng.poisson(lambda_home, simulations)
    away_goals = rng.poisson(lambda_away, simulations)
    scores = pd.Series([f"{h}-{a}" for h, a in zip(home_goals, away_goals)], name="score")
    counts = scores.value_counts().rename_axis("score").reset_index(name="monte_carlo_count")
    counts["monte_carlo_probability"] = counts["monte_carlo_count"] / simulations
    counts["monte_carlo_probability_pct"] = counts["monte_carlo_probability"] * 100
    return counts.sort_values("monte_carlo_probability", ascending=False).reset_index(drop=True)


def outcome_probabilities(scorelines: pd.DataFrame, home_col: str = "portugal_goals", away_col: str = "spain_goals") -> dict[str, float]:
    home = float(scorelines.loc[scorelines[home_col] > scorelines[away_col], "poisson_probability"].sum())
    draw = float(scorelines.loc[scorelines[home_col] == scorelines[away_col], "poisson_probability"].sum())
    away = float(scorelines.loc[scorelines[home_col] < scorelines[away_col], "poisson_probability"].sum())
    total = home + draw + away
    return {
        "portugal_win_pct": home / total * 100,
        "draw_pct": draw / total * 100,
        "spain_win_pct": away / total * 100,
    }
