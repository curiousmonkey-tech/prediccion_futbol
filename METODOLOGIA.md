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

El proyecto hace web scraping de Transfermarkt para obtener datos actuales de las selecciones que tienen URL configurada:

- Jugador.
- Posicion.
- Edad.
- Valor de mercado.

El valor de mercado se usa como proxy de calidad de plantilla. No es una medida perfecta de rendimiento deportivo, pero permite incorporar una senal objetiva y actualizable. Si una seleccion no tiene URL configurada, el modelo usa un factor de calidad neutro para no bloquear la prediccion.

## 3. Variables del modelo

Para cada seleccion se calculan promedios recientes:

- Goles a favor.
- Goles en contra.
- Rendimiento de la seleccion local como local.
- Rendimiento de la seleccion visitante como visitante.
- Goles recientes ponderados temporalmente para que los partidos antiguos influyan menos.
- Rendimiento en los ultimos 90 dias cuando hay partidos suficientes.

Tambien se calcula el historial directo entre la seleccion local y la visitante.

## 4. Datos actuales con ESPN

El proyecto consulta endpoints publicos de ESPN para obtener datos actuales del Mundial sin API key. La consulta usa cache local y limite interno de peticiones.

Se extraen datos de los ultimos partidos configurados por seleccion:

- Tiros totales.
- Tiros a puerta.
- Posesion.
- Corners.
- Tarjetas.
- Faltas.
- Goles marcados y encajados.
- Porterias a cero.

Tambien se intenta obtener estadisticas de jugadores en esos partidos para elegir los 11 mas importantes por seleccion y calcular un indice simple de forma reciente.

La cache vive en `data/raw/current_data/` para no repetir peticiones y reducir el riesgo de bloqueo.

## 5. Goles esperados

El modelo estima una lambda para cada equipo:

```text
lambda_local = forma_reciente_local + defensa_visitante + historico_directo + factor_calidad
lambda_visitante = forma_reciente_visitante + defensa_local + historico_directo + factor_calidad
```

En la version ampliada, esos componentes se ajustan con:

- Historico ponderado por fecha.
- Estadisticas recientes de equipo de ESPN.
- Factor de forma de jugadores importantes.
- Calidad actual de plantilla.

Los factores estan acotados para que una fuente nueva no distorsione todo el modelo.

## 6. Poisson

Con las lambdas calculadas, se usa la distribucion de Poisson para estimar la probabilidad de que cada equipo marque 0, 1, 2, 3 o mas goles.

Despues se combinan las probabilidades de la seleccion local y la visitante para generar marcadores posibles.

## 7. Monte Carlo

El proyecto simula 100000 partidos usando las lambdas de Poisson.

El resultado es una tabla de marcadores ordenada por frecuencia simulada.

## 8. Limitaciones

- No usa alineaciones confirmadas.
- No conoce lesiones de ultima hora.
- No modela tactica, clima, fatiga o sanciones.
- Transfermarkt puede cambiar su HTML o bloquear scraping.
- ESPN no es una API oficial contratada y puede cambiar endpoints.
- Algunos partidos pueden no devolver estadisticas completas para selecciones o jugadores concretos.
- El valor de mercado no equivale directamente al rendimiento de un jugador.

## 9. Como mejorar el modelo

- Dar mas peso a partidos recientes.
- Separar amistosos y partidos oficiales.
- Incluir ranking Elo.
- Usar expected goals si se consigue una fuente fiable.
- Ajustar pesos con backtesting historico.
- Modelar dependencia entre goles de ambos equipos.
- Conectar convocatorias oficiales para saber exactamente que jugadores estan disponibles.
