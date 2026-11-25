"""Piezas compartidas por los DAGs: assets del warehouse y conexión."""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from datetime import datetime, timedelta
from typing import Any
from zoneinfo import ZoneInfo

import psycopg
from airflow.sdk import Asset, Connection, Context

CONEXION_WAREHOUSE = "warehouse"
SANTIAGO = ZoneInfo("America/Santiago")

# Cada tabla raw es un asset: cuando una tarea la actualiza, Airflow dispara
# los DAGs que dependen de ella (aquí, la transformación con dbt).
RAW_SISMOS = Asset("postgres://postgres:5432/warehouse/raw/usgs_eventos", group="raw")
RAW_INDICADORES = Asset("postgres://postgres:5432/warehouse/raw/mindicador_valores", group="raw")

ARGUMENTOS_POR_DEFECTO: dict[str, Any] = {
    "owner": "sebastian",
    "retries": 3,
    "retry_delay": timedelta(minutes=2),
    "retry_exponential_backoff": True,
    "max_retry_delay": timedelta(minutes=20),
}


def intervalo(
    contexto: Context, por_defecto: timedelta = timedelta(days=1)
) -> tuple[datetime, datetime]:
    """Intervalo de datos de la corrida.

    Con un timetable de intervalos (CronDataIntervalTimetable) las corridas programadas y
    los backfills traen [inicio, fin). Una corrida manual, o un DAG con timetable de
    disparo, no lo trae (o trae inicio == fin): entonces se toma el período que termina
    en la fecha lógica o, si tampoco hay, en el momento en que se lanzó la corrida.
    """
    inicio = contexto.get("data_interval_start")
    fin = contexto.get("data_interval_end")
    if inicio is not None and fin is not None and inicio < fin:
        return inicio, fin
    fin = fin or contexto.get("logical_date") or contexto["dag_run"].run_after
    return fin - por_defecto, fin


@contextmanager
def warehouse() -> Iterator[psycopg.Connection]:
    """Conexión psycopg al data warehouse usando la conexión `warehouse` de Airflow."""
    c = Connection.get(CONEXION_WAREHOUSE)
    with psycopg.connect(
        host=c.host,
        port=c.port or 5432,
        user=c.login,
        password=c.password,
        dbname=c.schema,
        application_name="airflow",
    ) as conn:
        yield conn
