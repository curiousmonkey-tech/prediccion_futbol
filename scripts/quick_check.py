from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from model import scoreline_probabilities  # noqa: E402
from simulation import monte_carlo_scorelines, outcome_probabilities  # noqa: E402


def main() -> None:
    poisson = scoreline_probabilities(1.4, 1.1, max_goals=8)
    if poisson.empty:
        raise RuntimeError("No se generaron probabilidades Poisson.")

    total_probability = float(poisson["poisson_probability"].sum())
    if not 0.99 <= total_probability <= 1.0:
        raise RuntimeError(f"Probabilidad Poisson fuera de rango: {total_probability}")

    outcomes = outcome_probabilities(poisson)
    outcome_total = sum(outcomes.values())
    if not 99.9 <= outcome_total <= 100.1:
        raise RuntimeError(f"Probabilidades de signo fuera de rango: {outcome_total}")

    monte_carlo = monte_carlo_scorelines(1.4, 1.1, simulations=1000, seed=7)
    if int(monte_carlo["monte_carlo_count"].sum()) != 1000:
        raise RuntimeError("La simulacion Monte Carlo no suma el numero esperado de partidos.")

    print("Quick check correcto.")


if __name__ == "__main__":
    main()
