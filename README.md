# Predicción de fútbol con Python

Antes de nada: gracias.

Si has llegado hasta aquí desde curious monkey, gracias de verdad por apoyar el contenido, por comentar, por compartir, por probar los proyectos y por estar ahí mientras empiezo este camino creando contenido sobre tecnologia, datos, automatizacion e inteligencia artificial.

Este proyecto esta pensado para que puedas abrirlo, ejecutarlo, entenderlo, modificarlo y mejorarlo. No es un modelo perfecto ni pretende vender humo: es una base práctica para aprender como combinar datos historicos, scraping, estadística y simulación Monte Carlo para estimar marcadores probables de un partido de fútbol.

## Sígueme en:

- Instagram: https://www.instagram.com/curiousmonkey.tech/
- YouTube: https://www.youtube.com/@curiousmonkey_tech
- TikTok: https://www.tiktok.com/@curiousmonkey.tech

Si mejoras algo, encuentras un fallo o haces una versión más potente, me encantaria que me lo contaras por cualquiera de esas redes. La idea es que este proyecto también sirva para aprender entre todos.

## Qué hace este proyecto

Este proyecto predice marcadores probables para cualquier partido internacional indicando por consola la seleccion local y la seleccion visitante:

- Seleccion local.
- Seleccion visitante.

Para ello combina varias piezas:

- Resultados internacionales historicos.
- Forma reciente de cada seleccion.
- Rendimiento de la seleccion local como local.
- Rendimiento de la seleccion visitante como visitante.
- Enfrentamientos directos entre ambas selecciones.
- Valor de mercado de las plantillas obtenido desde Transfermarkt cuando hay URL configurada.
- Distribución de Poisson para estimar probabilidades de goles.
- Simulación Monte Carlo con 100000 partidos simulados.

El resultado final es un ranking de marcadores ordenados por probabilidad y un resumen en Markdown con las principales conclusiones.

## Estructura del proyecto

```text
prediccion_futbol/
|-- .github/
|   `-- workflows/
|       `-- python-check.yml
|-- data/
|   |-- raw/
|   |   `-- .gitkeep
|   `-- processed/
|       `-- .gitkeep
|-- outputs/
|   |-- prediccion_<local>_<visitante>.csv
|   `-- resumen_prediccion_<local>_<visitante>.md
|-- src/
|   |-- current_data.py
|   |-- data_loader.py
|   |-- features.py
|   |-- main.py
|   |-- model.py
|   |-- scrapers.py
|   `-- simulation.py
|-- CONTRIBUTING.md
|-- LICENSE
|-- METODOLOGIA.md
|-- requirements.txt
`-- README.md
```

Los CSV de `data/` se generan al ejecutar el proyecto y estan ignorados por Git para evitar subir datos descargados o scrapeados como si fueran codigo fuente. Los archivos de `outputs/` incluidos sirven como ejemplo de resultado.

## Clonar el repositorio

```bash
git clone https://github.com/curiousmonkey-tech/prediccion-futbol.git
cd prediccion-futbol
```

## Instalacion

Necesitas tener Python instalado. Se recomienda usar Python 3.11 o superior.

Desde la carpeta del proyecto, instala las dependencias con:

```bash
python -m pip install -r requirements.txt
```

## Datos actuales sin API key

El proyecto funciona con datos historicos, Transfermarkt y una fuente publica de ESPN para datos actuales del Mundial. No hace falta API key.

Los datos actuales se guardan en cache local para evitar repetir peticiones y para que el proyecto sea mas respetuoso con la fuente.

Si prefieres trabajar con un entorno virtual:

```bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
```

En macOS o Linux, la activación del entorno virtual sería:

```bash
source .venv/bin/activate
```

## Ejecucion

Ejecuta el proyecto indicando la seleccion local y la visitante:

```bash
python src/main.py Portugal Spain
```

Para analizar el partido Espana vs Belgica con datos actuales:

```bash
python src/main.py Spain Belgium --current-matches 5 --player-limit 11 --current-max-requests 40
```

Si quieres evitar por completo el scraping de datos actuales:

```bash
python src/main.py Spain Belgium --no-current-data
```

La fuente actual usa cache local en `data/raw/current_data/`. Si repites el mismo analisis, el proyecto reutiliza respuestas guardadas. Usa `--force-refresh-current-data` solo si quieres renovar datos.

Los nombres deben coincidir con los del historico internacional, que normalmente estan en ingles. Por ejemplo:

```bash
python src/main.py Argentina France
python src/main.py Brazil Germany
python src/main.py Morocco Croatia
```

Al terminar, deberías ver mensajes parecidos a estos:

```text
Prediccion generada en outputs/prediccion_portugal_spain.csv
Resumen generado en outputs/resumen_prediccion_portugal_spain.md
```

## Comprobación rápida

Puedes ejecutar una verificacion local sin scraping ni descarga de datos:

```bash
python scripts/quick_check.py
```

Esta comprobación valida que las funciones principales de Poisson y Monte Carlo producen salidas coherentes.

## Salidas generadas

- `data/raw/international_results.csv`: resultados históricos internacionales descargados.
- `data/raw/current_data/`: cache local de respuestas de ESPN.
- `data/processed/transfermarkt_squads.csv`: jugadores scrapeados desde Transfermarkt.
- `data/processed/squad_quality.csv`: valor total y valor medio de plantilla.
- `data/processed/current_player_form.csv`: forma de los jugadores importantes si ESPN devuelve datos suficientes.
- `outputs/prediccion_<local>_<visitante>.csv`: ranking de marcadores con probabilidad Poisson y Monte Carlo.
- `outputs/resumen_prediccion_<local>_<visitante>.md`: resumen explicativo del proceso, lambdas, probabilidades y top de marcadores.

## Documentación extra

- `METODOLOGIA.md`: explicación más detallada del enfoque estadístico.
- `CONTRIBUTING.md`: guía para que otras personas puedan proponer mejoras.
- `LICENSE`: licencia MIT para permitir uso, modificación y distribución.
- `.github/workflows/python-check.yml`: comprobación automática basica en GitHub Actions.

## Metodologia resumida

El proyecto sigue este flujo:

1. Descarga o carga resultados históricos internacionales.
2. Obtiene información de plantillas desde Transfermarkt.
3. Consulta datos actuales de ESPN con cache y limite de peticiones.
4. Calcula variables de rendimiento ponderando mas los partidos recientes.
5. Anade estadisticas recientes de equipo: tiros, tiros a puerta, posesion, corners, tarjetas y solidez defensiva.
6. Analiza los 11 jugadores importantes por seleccion cuando hay datos suficientes.
7. Estima los goles esperados de cada equipo usando historico ponderado, localia/visita, calidad de plantilla, estadisticas recientes y forma de jugadores.
8. Usa Poisson para calcular probabilidades de marcadores.
9. Ejecuta una simulación Monte Carlo de 100000 partidos.
10. Guarda los resultados en `outputs/`.

## Importante

Este proyecto es educativo. Una prediccion deportiva real depende de muchisimos factores que aquí no se están modelando, por ejemplo:

- Alineaciones confirmadas.
- Lesiones de última hora.
- Rotaciones.
- Contexto del torneo.
- Fatiga.
- Estilo táctico.
- Clima.
- Motivación competitiva.
- Cambios recientes de entrenador.

Además, el valor de mercado de Transfermarkt se usa como proxy de calidad, pero no representa por sí solo el nivel real de un equipo.

## Sobre el scraping

El proyecto consulta Transfermarkt mediante scraping web para las selecciones que tienen URL configurada en `src/scrapers.py`. Si una seleccion no tiene URL configurada, la prediccion se puede generar igualmente usando un factor de calidad neutro basado solo en datos historicos.

El scraping puede dejar de funcionar si la página cambia su estructura HTML, modifica sus políticas de acceso o bloquea peticiones automatizadas.

Usa este código de forma responsable, con fines educativos y respetando los terminos de uso de las webs consultadas.

## Ideas para mejorar el proyecto

Si quieres llevar este proyecto más lejos, puedes probar mejoras como estas:

- Anadir mas URLs de Transfermarkt para cubrir mas selecciones con calidad de plantilla.
- Mejorar la seleccion automatica de los 11 jugadores importantes con convocatorias oficiales.
- Crear una interfaz web sencilla con Streamlit o FastAPI.
- Anadir datos de rankings FIFA o Elo.
- Incluir lesiones, convocatorias o alineaciones probables.
- Separar partidos oficiales y amistosos.
- Dar mas peso a partidos recientes.
- Ajustar los pesos del modelo y comparar resultados.
- Crear graficos con las probabilidades de marcadores.
- Anadir tests automáticos.
- Guardar históricos de predicciones para evaluar el modelo con el tiempo.

## Invitación a la comunidad

Si descargas este zip y lo pruebas, me haría mucha ilusión saber qué has hecho con él.

Puedes modificarlo, romperlo, arreglarlo, ampliarlo o usarlo como base para tus propios experimentos. Y si consigues una version mejor, escríbeme y cuéntame qué has cambiado: qué variable añadiste, qué error encontraste, qué idea se te ocurrió o qué resultado obtuviste.

Estoy empezando con curious monkey y cada mensaje, comentario, mejora o sugerencia ayuda muchisimo.

Gracias por apoyar el proyecto.

## Aviso

Este proyecto no es asesoramiento financiero ni una recomendación de apuestas. Es un experimento educativo de programación, datos y modelado estadístico aplicado al fútbol.
