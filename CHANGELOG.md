# Changelog

Todos los cambios importantes de este proyecto se documentan en este archivo.
El formato sigue [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/) y el proyecto usa
[versionado semántico](https://semver.org/lang/es/).

## [0.1.0] - 2026-11-25

### Agregado

- Paquete `extraccion` con la extracción de la USGS y de mindicador.cl y carga idempotente al
  esquema `raw` en JSONB.
- DAGs de Airflow 3: `extraccion_sismos` (intervalos de datos y backfill),
  `extraccion_indicadores` (mapeo dinámico) y `transformacion_dbt` (scheduling por assets con
  Cosmos).
- Proyecto dbt con capas staging, intermedia y marts, snapshot de revisiones de sismos, modelo
  incremental con contrato, seeds, tests genéricos propios, tests singulares y tests unitarios.
- Docker Compose con PostgreSQL y Airflow (api-server, scheduler y dag-processor).
- CI con lint, tests contra PostgreSQL, tests de DAGs en la imagen y publicación de la
  documentación de dbt en GitHub Pages.
