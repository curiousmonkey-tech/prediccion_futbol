# Metodologia

Este documento explica de forma resumida como funciona el modelo.

## 1. Datos historicos

El proyecto descarga resultados internacionales desde el dataset publico `martj42/international_results`.

Se usan columnas como:

- Fecha del partido.
- Equipo local.
- Equipo visitante.
- Goles local.
- Goles visitante.
- Torneo.
- Campo neutral.

Antes de entrenar el modelo se eliminan partidos sin marcador, porque pueden ser fixtures futuros o partidos no disputados.

## 2. Datos de plantilla

El proyecto hace web scraping de Transfermarkt para obtener datos actuales de Portugal y Espana:

- Jugador.
- Posicion.
- Edad.
- Valor de mercado.

El valor de mercado se usa como proxy de calidad de plantilla. No es una medida perfecta de rendimiento deportivo, pero permite incorporar una senal objetiva y actualizable.

## 3. Variables del modelo

Para cada seleccion se calculan promedios recientes:

- Goles a favor.
- Goles en contra.
- Rendimiento de Portugal como local.
- Rendimiento de Espana como visitante.

Tambien se calcula el historial directo Portugal vs Espana.

## 4. Goles esperados

El modelo estima una lambda para cada equipo:

```text
lambda_portugal = forma_reciente_portugal + defensa_espana + historico_directo + factor_calidad
lambda_espana = forma_reciente_espana + defensa_portugal + historico_directo + factor_calidad
```

En el codigo, esos componentes se combinan con pesos simples para mantener el proyecto entendible y modificable.

## 5. Poisson

Con las lambdas calculadas, se usa la distribucion de Poisson para estimar la probabilidad de que cada equipo marque 0, 1, 2, 3 o mas goles.

Despues se combinan las probabilidades de Portugal y Espana para generar marcadores posibles.

## 6. Monte Carlo

El proyecto simula 100000 partidos usando las lambdas de Poisson.

El resultado es una tabla de marcadores ordenada por frecuencia simulada.

## 7. Limitaciones

- No usa alineaciones confirmadas.
- No conoce lesiones de ultima hora.
- No modela tactica, clima, fatiga o sanciones.
- Transfermarkt puede cambiar su HTML o bloquear scraping.
- El valor de mercado no equivale directamente al rendimiento de un jugador.

## 8. Como mejorar el modelo

- Dar mas peso a partidos recientes.
- Separar amistosos y partidos oficiales.
- Incluir ranking Elo.
- Usar expected goals si se consigue una fuente fiable.
- Ajustar pesos con backtesting historico.
- Modelar dependencia entre goles de ambos equipos.
