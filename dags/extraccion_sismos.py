"""Carga diaria de sismos de USGS a raw.usgs_eventos.

Cada corrida procesa su intervalo de datos (un día), así que un backfill de
cualquier período solo repite corridas ya probadas:

    airflow backfill create --dag-id extraccion_sismos --from-date 2025-01-01 --to-date 2025-03-31
"""

from __future__ import annotations

from datetime import datetime, timedelta

from airflow.sdk import CronDataIntervalTimetable, dag, get_current_context, task
from comun import ARGUMENTOS_POR_DEFECTO, RAW_SISMOS, SANTIAGO, intervalo, warehouse

# USGS revisa los sismos durante días después de publicarlos (magnitud, ubicación, estado).
# Cada corrida vuelve a pedir la última semana para recoger esas revisiones.
VENTANA_REVISIONES = timedelta(days=7)


@dag(
    dag_id="extraccion_sismos",
    description="Sismos de Chile desde la API de USGS a la capa raw",
    # Intervalos de un día [00:00, 00:00) en hora de Chile: cada corrida sabe exactamente
    # qué día le toca, y un backfill de un mes son 30 corridas independientes.
    schedule=CronDataIntervalTimetable("0 0 * * *", timezone="America/Santiago"),
    start_date=datetime(2025, 1, 1, tzinfo=SANTIAGO),
    catchup=False,
    max_active_runs=3,
    default_args=ARGUMENTOS_POR_DEFECTO,
    tags=["extraccion", "usgs"],
    doc_md=__doc__,
)
def extraccion_sismos() -> None:
    @task
    def asegurar_esquema() -> None:
        from extraccion import esquema

        with warehouse() as conn:
            esquema.asegurar(conn)

    @task(outlets=[RAW_SISMOS])
    def cargar_sismos() -> dict[str, int]:
        from extraccion import usgs
        from extraccion.http import crear_cliente

        contexto = get_current_context()
        inicio, fin = intervalo(contexto)
        inicio -= VENTANA_REVISIONES
        with crear_cliente() as client:
            eventos = usgs.extraer(client, inicio, fin)
        with warehouse() as conn:
            resultado = usgs.cargar(conn, eventos, contexto["run_id"])
        # Los conteos quedan en el evento del asset y se ven en la vista de assets de Airflow.
        contexto["outlet_events"][RAW_SISMOS].extra = resultado.como_dict()
        return resultado.como_dict()

    asegurar_esquema() >> cargar_sismos()


extraccion_sismos()
