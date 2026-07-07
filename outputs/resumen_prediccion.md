# Prediccion Portugal vs Espana

Partido modelado: Portugal local vs Espana visitante.

## Fuentes reales usadas

- Resultados internacionales historicos: `martj42/international_results/results.csv`.
- Calidad de jugadores actuales: scraping de Transfermarkt para las paginas de Portugal y Espana.

## Variables calculadas

- Promedios recientes de goles a favor y en contra.
- Promedios como local para Portugal y como visitante para Espana.
- Historial directo Portugal-Espana.
- Valor total y medio de mercado de las plantillas scrapeadas.

## Lambdas Poisson

- Portugal: 1.732
- Espana: 1.606
- Factor calidad Portugal: 0.979
- Factor calidad Espana: 1.026

## Probabilidades de signo

- Victoria Portugal: 41.22%
- Empate: 22.83%
- Victoria Espana: 35.95%

## Top 15 marcadores

| score   |   portugal_goals |   spain_goals |   poisson_probability |   poisson_probability_pct |   monte_carlo_count |   monte_carlo_probability |   monte_carlo_probability_pct |
|:--------|-----------------:|--------------:|----------------------:|--------------------------:|--------------------:|--------------------------:|------------------------------:|
| 1-1     |                1 |             1 |             0.0987553 |                   9.87553 |                9858 |                   0.09858 |                         9.858 |
| 2-1     |                2 |             1 |             0.0855301 |                   8.55301 |                8507 |                   0.08507 |                         8.507 |
| 1-2     |                1 |             2 |             0.079309  |                   7.9309  |                7965 |                   0.07965 |                         7.965 |
| 2-2     |                2 |             2 |             0.068688  |                   6.8688  |                6838 |                   0.06838 |                         6.838 |
| 1-0     |                1 |             0 |             0.0614849 |                   6.14849 |                6073 |                   0.06073 |                         6.073 |
| 0-1     |                0 |             1 |             0.0570128 |                   5.70128 |                5730 |                   0.0573  |                         5.73  |
| 2-0     |                2 |             0 |             0.0532509 |                   5.32509 |                5368 |                   0.05368 |                         5.368 |
| 3-1     |                3 |             1 |             0.049384  |                   4.9384  |                4910 |                   0.0491  |                         4.91  |
| 0-2     |                0 |             2 |             0.0457862 |                   4.57862 |                4593 |                   0.04593 |                         4.593 |
| 1-3     |                1 |             3 |             0.0424613 |                   4.24613 |                4097 |                   0.04097 |                         4.097 |
| 3-2     |                3 |             2 |             0.0396596 |                   3.96596 |                3999 |                   0.03999 |                         3.999 |
| 2-3     |                2 |             3 |             0.0367749 |                   3.67749 |                3741 |                   0.03741 |                         3.741 |
| 0-0     |                0 |             0 |             0.0354961 |                   3.54961 |                3538 |                   0.03538 |                         3.538 |
| 3-0     |                3 |             0 |             0.0307464 |                   3.07464 |                3059 |                   0.03059 |                         3.059 |
| 0-3     |                0 |             3 |             0.0245135 |                   2.45135 |                2511 |                   0.02511 |                         2.511 |

## Resumen de equipos

| team     |   matches_used |   goals_for_avg |   goals_against_avg |   home_goals_for_avg |   home_goals_against_avg |   away_goals_for_avg |   away_goals_against_avg |   players |   total_market_value_eur |   average_market_value_eur | scraped_from                                                  |
|:---------|---------------:|----------------:|--------------------:|---------------------:|-------------------------:|---------------------:|-------------------------:|----------:|-------------------------:|---------------------------:|:--------------------------------------------------------------|
| Portugal |             30 |         2.13333 |            0.833333 |              3.03333 |                 0.9      |              1.7     |                 0.766667 |        26 |               1.0055e+09 |                3.86731e+07 | https://www.transfermarkt.com/portugal/startseite/verein/3300 |
| Spain    |             30 |         2.43333 |            0.766667 |              2.76667 |                 0.766667 |              2.06667 |                 0.833333 |        26 |               1.2228e+09 |                4.70308e+07 | https://www.transfermarkt.com/spanien/startseite/verein/3375  |

## Enfrentamientos directos disponibles

| date                | home_team   | away_team   |   home_score |   away_score | tournament          | city                  | country      | neutral   |
|:--------------------|:------------|:------------|-------------:|-------------:|:--------------------|:----------------------|:-------------|:----------|
| 1958-04-13 00:00:00 | Spain       | Portugal    |            1 |            0 | Friendly            | Madrid                | Spain        | False     |
| 1964-11-15 00:00:00 | Portugal    | Spain       |            2 |            1 | Friendly            | Porto                 | Portugal     | False     |
| 1979-09-26 00:00:00 | Spain       | Portugal    |            1 |            1 | Friendly            | Vigo                  | Spain        | False     |
| 1981-06-20 00:00:00 | Portugal    | Spain       |            2 |            0 | Friendly            | Porto                 | Portugal     | False     |
| 1984-06-17 00:00:00 | Portugal    | Spain       |            1 |            1 | UEFA Euro           | Marseille             | France       | True      |
| 1991-01-16 00:00:00 | Spain       | Portugal    |            1 |            1 | Friendly            | Castellón de la Plana | Spain        | False     |
| 1992-01-15 00:00:00 | Portugal    | Spain       |            0 |            0 | Friendly            | Torres Novas          | Portugal     | False     |
| 1994-01-19 00:00:00 | Spain       | Portugal    |            2 |            2 | Friendly            | Vigo                  | Spain        | False     |
| 2002-02-13 00:00:00 | Spain       | Portugal    |            1 |            1 | Friendly            | Barcelona             | Spain        | False     |
| 2003-09-06 00:00:00 | Portugal    | Spain       |            0 |            3 | Friendly            | Guimarães             | Portugal     | False     |
| 2004-06-20 00:00:00 | Portugal    | Spain       |            1 |            0 | UEFA Euro           | Lisbon                | Portugal     | False     |
| 2010-06-29 00:00:00 | Spain       | Portugal    |            1 |            0 | FIFA World Cup      | Cape Town             | South Africa | True      |
| 2010-11-17 00:00:00 | Portugal    | Spain       |            4 |            0 | Friendly            | Lisbon                | Portugal     | False     |
| 2012-06-27 00:00:00 | Portugal    | Spain       |            0 |            0 | UEFA Euro           | Donetsk               | Ukraine      | True      |
| 2018-06-15 00:00:00 | Portugal    | Spain       |            3 |            3 | FIFA World Cup      | Sochi                 | Russia       | True      |
| 2020-10-07 00:00:00 | Portugal    | Spain       |            0 |            0 | Friendly            | Lisbon                | Portugal     | False     |
| 2021-06-04 00:00:00 | Spain       | Portugal    |            0 |            0 | Friendly            | Madrid                | Spain        | False     |
| 2022-06-02 00:00:00 | Spain       | Portugal    |            1 |            1 | UEFA Nations League | Seville               | Spain        | False     |
| 2022-09-27 00:00:00 | Portugal    | Spain       |            0 |            1 | UEFA Nations League | Braga                 | Portugal     | False     |
| 2025-06-08 00:00:00 | Portugal    | Spain       |            2 |            2 | UEFA Nations League | Munich                | Germany      | True      |

## Limitaciones

- El modelo no conoce alineaciones confirmadas, lesiones de ultima hora ni contexto tactico.
- Transfermarkt puede cambiar su HTML o bloquear scraping; el script falla explicitamente si no puede obtener datos reales.
- El valor de mercado se usa como proxy de calidad de plantilla, no como medicion tecnica directa.