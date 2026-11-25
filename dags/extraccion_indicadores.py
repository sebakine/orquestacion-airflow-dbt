"""Carga diaria de indicadores económicos de mindicador.cl a raw.

Hay una tarea por indicador (mapeo dinámico): si la API falla para uno, solo esa
tarea se reintenta y las demás siguen. Cada corrida recarga el año completo del
intervalo, lo que también recoge las correcciones que publica la API.
"""

from __future__ import annotations

from datetime import datetime

from airflow.sdk import dag, get_current_context, task
from comun import ARGUMENTOS_POR_DEFECTO, RAW_INDICADORES, SANTIAGO, intervalo, warehouse

from extraccion.mindicador import INDICADORES


@dag(
    dag_id="extraccion_indicadores",
    description="Dólar, euro, UF, UTM y cobre desde mindicador.cl a la capa raw",
    # 10:00 en Chile: el Banco Central publica el dólar observado temprano en la mañana.
    schedule="0 10 * * *",
    start_date=datetime(2025, 1, 1, tzinfo=SANTIAGO),
    catchup=False,
    max_active_runs=1,
    default_args=ARGUMENTOS_POR_DEFECTO,
    tags=["extraccion", "mindicador"],
    doc_md=__doc__,
)
def extraccion_indicadores() -> None:
    @task
    def asegurar_esquema() -> None:
        from extraccion import esquema

        with warehouse() as conn:
            esquema.asegurar(conn)

    @task(max_active_tis_per_dag=2)
    def cargar_indicador(codigo: str) -> dict[str, int]:
        from extraccion import mindicador
        from extraccion.http import crear_cliente

        contexto = get_current_context()
        _, fin = intervalo(contexto)
        anio = fin.astimezone(SANTIAGO).year
        # mindicador.cl a veces tarda más de un minuto en responder.
        with crear_cliente(timeout=120) as client:
            payload = mindicador.extraer_anio(client, codigo, anio)
        with warehouse() as conn:
            return mindicador.cargar(conn, payload, contexto["run_id"]).como_dict()

    # El asset se marca una sola vez, al final, para que dbt corra una vez por carga y
    # no una vez por indicador. Si un indicador falla tras sus reintentos, la corrida
    # queda en rojo y dbt espera a la próxima carga completa (las cargas son idempotentes).
    @task(outlets=[RAW_INDICADORES])
    def resumir(resultados: list[dict[str, int]]) -> dict[str, int]:
        total: dict[str, int] = {}
        for resultado in resultados:
            for clave, valor in resultado.items():
                total[clave] = total.get(clave, 0) + valor
        get_current_context()["outlet_events"][RAW_INDICADORES].extra = total
        return total

    cargas = cargar_indicador.expand(codigo=list(INDICADORES))
    asegurar_esquema() >> cargas
    resumir(cargas)


extraccion_indicadores()
