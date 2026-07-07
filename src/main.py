from __future__ import annotations

from pathlib import Path

import pandas as pd

from data_loader import load_results
from features import build_feature_summary, h2h_summary, head_to_head
from model import estimate_lambdas, scoreline_probabilities
from scrapers import scrape_squads
from simulation import monte_carlo_scorelines, outcome_probabilities


ROOT = Path(__file__).resolve().parents[1]
DATA_RAW = ROOT / "data" / "raw"
DATA_PROCESSED = ROOT / "data" / "processed"
OUTPUTS = ROOT / "outputs"


def pct(value: float) -> str:
    return f"{value:.2f}%"


def write_summary(
    features: pd.DataFrame,
    h2h: pd.DataFrame,
    lambdas: dict[str, float],
    ranking: pd.DataFrame,
    outcomes: dict[str, float],
) -> None:
    lines = [
        "# Prediccion Portugal vs Espana",
        "",
        "Partido modelado: Portugal local vs Espana visitante.",
        "",
        "## Fuentes reales usadas",
        "",
        "- Resultados internacionales historicos: `martj42/international_results/results.csv`.",
        "- Calidad de jugadores actuales: scraping de Transfermarkt para las paginas de Portugal y Espana.",
        "",
        "## Variables calculadas",
        "",
        "- Promedios recientes de goles a favor y en contra.",
        "- Promedios como local para Portugal y como visitante para Espana.",
        "- Historial directo Portugal-Espana.",
        "- Valor total y medio de mercado de las plantillas scrapeadas.",
        "",
        "## Lambdas Poisson",
        "",
        f"- Portugal: {lambdas['Portugal']:.3f}",
        f"- Espana: {lambdas['Spain']:.3f}",
        f"- Factor calidad Portugal: {lambdas['portugal_quality_factor']:.3f}",
        f"- Factor calidad Espana: {lambdas['spain_quality_factor']:.3f}",
        "",
        "## Probabilidades de signo",
        "",
        f"- Victoria Portugal: {pct(outcomes['portugal_win_pct'])}",
        f"- Empate: {pct(outcomes['draw_pct'])}",
        f"- Victoria Espana: {pct(outcomes['spain_win_pct'])}",
        "",
        "## Top 15 marcadores",
        "",
        ranking.head(15).to_markdown(index=False),
        "",
        "## Resumen de equipos",
        "",
        features.to_markdown(index=False),
        "",
        "## Enfrentamientos directos disponibles",
        "",
        h2h.tail(20).to_markdown(index=False),
        "",
        "## Limitaciones",
        "",
        "- El modelo no conoce alineaciones confirmadas, lesiones de ultima hora ni contexto tactico.",
        "- Transfermarkt puede cambiar su HTML o bloquear scraping; el script falla explicitamente si no puede obtener datos reales.",
        "- El valor de mercado se usa como proxy de calidad de plantilla, no como medicion tecnica directa.",
    ]
    (OUTPUTS / "resumen_prediccion.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    DATA_RAW.mkdir(parents=True, exist_ok=True)
    DATA_PROCESSED.mkdir(parents=True, exist_ok=True)
    OUTPUTS.mkdir(parents=True, exist_ok=True)

    results = load_results(DATA_RAW)
    squads, quality = scrape_squads()

    squads.to_csv(DATA_PROCESSED / "transfermarkt_squads.csv", index=False)
    quality.to_csv(DATA_PROCESSED / "squad_quality.csv", index=False)

    features = build_feature_summary(results, quality)
    h2h_info = h2h_summary(results)
    h2h = head_to_head(results)
    lambdas = estimate_lambdas(features, h2h_info)

    poisson = scoreline_probabilities(lambdas["Portugal"], lambdas["Spain"])
    monte_carlo = monte_carlo_scorelines(lambdas["Portugal"], lambdas["Spain"])

    ranking = poisson.merge(monte_carlo, on="score", how="left")
    ranking["monte_carlo_count"] = ranking["monte_carlo_count"].fillna(0).astype(int)
    ranking["monte_carlo_probability"] = ranking["monte_carlo_probability"].fillna(0)
    ranking["monte_carlo_probability_pct"] = ranking["monte_carlo_probability_pct"].fillna(0)
    ranking = ranking.sort_values("monte_carlo_probability", ascending=False).reset_index(drop=True)

    outcomes = outcome_probabilities(poisson)
    ranking.to_csv(OUTPUTS / "prediccion_portugal_espana.csv", index=False)
    write_summary(features, h2h, lambdas, ranking, outcomes)

    print("Prediccion generada en outputs/prediccion_portugal_espana.csv")
    print("Resumen generado en outputs/resumen_prediccion.md")


if __name__ == "__main__":
    main()
