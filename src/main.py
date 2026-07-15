from __future__ import annotations

import argparse
import re
from pathlib import Path

import pandas as pd

from current_data import fetch_current_context
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


def slugify(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Predice el marcador probable de un partido internacional.")
    parser.add_argument("home_team", help="Seleccion local, por ejemplo: Portugal")
    parser.add_argument("away_team", help="Seleccion visitante, por ejemplo: Spain")
    parser.add_argument("--current-matches", type=int, default=5, help="Partidos recientes por seleccion a consultar en ESPN.")
    parser.add_argument("--player-limit", type=int, default=11, help="Jugadores importantes por seleccion a analizar.")
    parser.add_argument("--current-max-requests", type=int, default=40, help="Limite interno de peticiones reales a ESPN por ejecucion.")
    parser.add_argument("--force-refresh-current-data", action="store_true", help="Ignora cache local y vuelve a consultar ESPN.")
    parser.add_argument("--no-current-data", action="store_true", help="Desactiva ESPN y usa solo datos historicos/Transfermarkt.")
    return parser.parse_args()


def normalize_team_name(team: str, available_teams: set[str]) -> str:
    matches = [available for available in available_teams if available.lower() == team.lower()]
    if matches:
        return matches[0]
    examples = ", ".join(sorted(available_teams)[:12])
    raise ValueError(f"La seleccion '{team}' no existe en el historico. Ejemplos disponibles: {examples}...")


def player_form_index(players: pd.DataFrame) -> float:
    if players.empty:
        return 1.0
    avg_score = float(players["player_form_score"].mean())
    return max(0.92, min(1.08, 1 + (avg_score - 5.5) * 0.025))


def write_summary(
    home_team: str,
    away_team: str,
    features: pd.DataFrame,
    h2h: pd.DataFrame,
    lambdas: dict[str, float],
    ranking: pd.DataFrame,
    outcomes: dict[str, float],
    current_status: dict[str, object],
    player_summary: pd.DataFrame,
    output_filename: str,
) -> None:
    lines = [
        f"# Prediccion {home_team} vs {away_team}",
        "",
        f"Partido modelado: {home_team} local vs {away_team} visitante.",
        "",
        "## Fuentes reales usadas",
        "",
        "- Resultados internacionales historicos: `martj42/international_results/results.csv`.",
        "- Calidad de jugadores actuales: scraping de Transfermarkt si la seleccion tiene URL configurada; si no, factor de calidad neutro.",
        "- ESPN publico para calendario, estadisticas recientes de equipo y forma de jugadores actuales.",
        f"- Estado datos actuales: {current_status.get('reason', 'desconocido')}.",
        f"- Peticiones reales ESPN en esta ejecucion: {current_status.get('requests_made', 0)}. Cache hits: {current_status.get('cache_hits', 0)}.",
        "",
        "## Variables calculadas",
        "",
        "- Promedios recientes de goles a favor y en contra.",
        f"- Promedios como local para {home_team} y como visitante para {away_team}.",
        f"- Historial directo {home_team}-{away_team}.",
        "- Valor total y medio de mercado de las plantillas scrapeadas.",
        "",
        "## Lambdas Poisson",
        "",
        f"- {home_team}: {lambdas[home_team]:.3f}",
        f"- {away_team}: {lambdas[away_team]:.3f}",
        f"- Factor calidad {home_team}: {lambdas['home_quality_factor']:.3f}",
        f"- Factor calidad {away_team}: {lambdas['away_quality_factor']:.3f}",
        f"- Factor estadisticas actuales {home_team}: {lambdas['home_current_factor']:.3f}",
        f"- Factor estadisticas actuales {away_team}: {lambdas['away_current_factor']:.3f}",
        f"- Factor forma jugadores {home_team}: {lambdas['home_player_form_factor']:.3f}",
        f"- Factor forma jugadores {away_team}: {lambdas['away_player_form_factor']:.3f}",
        "",
        "## Probabilidades de signo",
        "",
        f"- Victoria {home_team}: {pct(outcomes['home_win_pct'])}",
        f"- Empate: {pct(outcomes['draw_pct'])}",
        f"- Victoria {away_team}: {pct(outcomes['away_win_pct'])}",
        "",
        "## Top 15 marcadores",
        "",
        ranking.head(15).to_markdown(index=False),
        "",
        "## Resumen de equipos",
        "",
        features.to_markdown(index=False),
        "",
        "## 11 jugadores mas importantes por forma reciente",
        "",
        player_summary.to_markdown(index=False) if not player_summary.empty else "No hay datos suficientes de jugadores desde ESPN.",
        "",
        "## Enfrentamientos directos disponibles",
        "",
        h2h.tail(20).to_markdown(index=False),
        "",
        "## Limitaciones",
        "",
        "- El modelo no conoce alineaciones confirmadas, lesiones de ultima hora ni contexto tactico.",
        "- Transfermarkt puede cambiar su HTML o bloquear scraping; el script falla explicitamente si no puede obtener datos reales.",
        "- Para selecciones sin URL de Transfermarkt configurada, el factor de calidad de plantilla queda neutro.",
        "- ESPN no es una API oficial contratada; el proyecto usa cache local y puede fallar si cambian sus endpoints.",
        "- El valor de mercado se usa como proxy de calidad de plantilla, no como medicion tecnica directa.",
    ]
    (OUTPUTS / output_filename).write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    args = parse_args()

    DATA_RAW.mkdir(parents=True, exist_ok=True)
    DATA_PROCESSED.mkdir(parents=True, exist_ok=True)
    OUTPUTS.mkdir(parents=True, exist_ok=True)

    results = load_results(DATA_RAW)
    available_teams = set(results["home_team"]).union(set(results["away_team"]))
    home_team = normalize_team_name(args.home_team, available_teams)
    away_team = normalize_team_name(args.away_team, available_teams)
    if home_team == away_team:
        raise ValueError("La seleccion local y la visitante deben ser distintas.")

    squads, quality = scrape_squads((home_team, away_team))
    current_team_summary, player_summary, current_status = fetch_current_context(
        DATA_RAW / "current_data",
        home_team,
        away_team,
        max(1, args.current_matches),
        max(1, args.player_limit),
        args.force_refresh_current_data,
        args.no_current_data,
        max(1, args.current_max_requests),
    )

    squads.to_csv(DATA_PROCESSED / "transfermarkt_squads.csv", index=False)
    quality.to_csv(DATA_PROCESSED / "squad_quality.csv", index=False)

    player_indexes = pd.DataFrame(
        [
            {"team": team, "player_form_index": player_form_index(player_summary[player_summary["team"] == team]) if not player_summary.empty else 1.0}
            for team in (home_team, away_team)
        ]
    )
    features = build_feature_summary(results, quality, home_team, away_team)
    if not current_team_summary.empty:
        features = features.merge(current_team_summary, on="team", how="left")
    features = features.merge(player_indexes, on="team", how="left")
    h2h_info = h2h_summary(results, home_team, away_team)
    h2h = head_to_head(results, home_team, away_team)
    lambdas = estimate_lambdas(features, h2h_info, home_team, away_team)

    poisson = scoreline_probabilities(lambdas[home_team], lambdas[away_team])
    monte_carlo = monte_carlo_scorelines(lambdas[home_team], lambdas[away_team])

    ranking = poisson.merge(monte_carlo, on="score", how="left")
    ranking["monte_carlo_count"] = ranking["monte_carlo_count"].fillna(0).astype(int)
    ranking["monte_carlo_probability"] = ranking["monte_carlo_probability"].fillna(0)
    ranking["monte_carlo_probability_pct"] = ranking["monte_carlo_probability_pct"].fillna(0)
    ranking = ranking.sort_values("monte_carlo_probability", ascending=False).reset_index(drop=True)

    outcomes = outcome_probabilities(poisson)
    prediction_filename = f"prediccion_{slugify(home_team)}_{slugify(away_team)}.csv"
    summary_filename = f"resumen_prediccion_{slugify(home_team)}_{slugify(away_team)}.md"
    ranking.to_csv(OUTPUTS / prediction_filename, index=False)
    if not player_summary.empty:
        player_summary.to_csv(DATA_PROCESSED / "current_player_form.csv", index=False)
    write_summary(home_team, away_team, features, h2h, lambdas, ranking, outcomes, current_status, player_summary, summary_filename)

    print(f"Prediccion generada en outputs/{prediction_filename}")
    print(f"Resumen generado en outputs/{summary_filename}")


if __name__ == "__main__":
    main()
