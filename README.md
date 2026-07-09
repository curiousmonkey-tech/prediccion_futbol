# Predicción de fútbol con Python: Portugal vs España

Antes de nada: gracias.

Si has llegado hasta aquí desde curious monkey, gracias de verdad por apoyar el contenido, por comentar, por compartir, por probar los proyectos y por estar ahí mientras empiezo este camino creando contenido sobre tecnologia, datos, automatizacion e inteligencia artificial.

Este proyecto esta pensado para que puedas abrirlo, ejecutarlo, entenderlo, modificarlo y mejorarlo. No es un modelo perfecto ni pretende vender humo: es una base práctica para aprender como combinar datos historicos, scraping, estadística y simulación Monte Carlo para estimar marcadores probables de un partido de fútbol.

## Sígueme en:

- Instagram: https://www.instagram.com/curiousmonkey.tech/
- YouTube: https://www.youtube.com/@curiousmonkey_tech
- TikTok: https://www.tiktok.com/@curiousmonkey.tech

Si mejoras algo, encuentras un fallo o haces una versión más potente, me encantaria que me lo contaras por cualquiera de esas redes. La idea es que este proyecto también sirva para aprender entre todos.

## Qué hace este proyecto

Este proyecto predice marcadores probables para un partido concreto:

- Portugal como equipo local.
- Espana como equipo visitante.

Para ello combina varias piezas:

- Resultados internacionales historicos.
- Forma reciente de cada seleccion.
- Rendimiento de Portugal como local.
- Rendimiento de Espana como visitante.
- Enfrentamientos directos Portugal vs Espana.
- Valor de mercado de las plantillas obtenido desde Transfermarkt.
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
|   |-- prediccion_portugal_espana.csv
|   `-- resumen_prediccion.md
|-- src/
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

Ejecuta el proyecto con:

```bash
python src/main.py
```

Al terminar, deberías ver mensajes parecidos a estos:

```text
Predicción generada en outputs/prediccion_portugal_espana.csv
Resumen generado en outputs/resumen_prediccion.md
```

## Comprobación rápida

Puedes ejecutar una verificacion local sin scraping ni descarga de datos:

```bash
python scripts/quick_check.py
```

Esta comprobación valida que las funciones principales de Poisson y Monte Carlo producen salidas coherentes.

## Salidas generadas

- `data/raw/international_results.csv`: resultados históricos internacionales descargados.
- `data/processed/transfermarkt_squads.csv`: jugadores scrapeados desde Transfermarkt.
- `data/processed/squad_quality.csv`: valor total y valor medio de plantilla.
- `outputs/prediccion_portugal_espana.csv`: ranking de marcadores con probabilidad Poisson y Monte Carlo.
- `outputs/resumen_prediccion.md`: resumen explicativo del proceso, lambdas, probabilidades y top de marcadores.

## Documentación extra

- `METODOLOGIA.md`: explicación más detallada del enfoque estadístico.
- `CONTRIBUTING.md`: guía para que otras personas puedan proponer mejoras.
- `LICENSE`: licencia MIT para permitir uso, modificación y distribución.
- `.github/workflows/python-check.yml`: comprobación automática basica en GitHub Actions.

## Metodologia resumida

El proyecto sigue este flujo:

1. Descarga o carga resultados históricos internacionales.
2. Obtiene información de plantillas desde Transfermarkt.
3. Calcula variables de rendimiento para Portugal y España.
4. Resume los enfrentamientos directos entre ambas selecciones.
5. Estima los goles esperados de cada equipo usando una combinación de forma reciente, localia/visita, histórico directo y calidad de plantilla.
6. Usa Poisson para calcular probabilidades de marcadores.
7. Ejecuta una simulación Monte Carlo de 100000 partidos.
8. Guarda los resultados en `outputs/`.

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

El proyecto consulta Transfermarkt mediante scraping web. Puede dejar de funcionar si la página cambia su estructura HTML, modifica sus políticas de acceso o bloquea peticiones automatizadas.

Usa este código de forma responsable, con fines educativos y respetando los terminos de uso de las webs consultadas.

## Ideas para mejorar el proyecto

Si quieres llevar este proyecto más lejos, puedes probar mejoras como estas:

- Permitir elegir cualquier partido desde consola.
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
