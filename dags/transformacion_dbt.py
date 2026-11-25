"""Transformación con dbt, disparada cuando cambian los datos crudos.

No tiene horario: corre cuando cualquiera de las tablas raw recibe datos nuevos
(scheduling por assets). Cosmos convierte cada modelo de dbt en una tarea de
Airflow, con su test justo después, para ver en la interfaz qué modelo falló.
"""

from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path

from airflow.providers.standard.operators.bash import BashOperator
from airflow.sdk import dag
from comun import ARGUMENTOS_POR_DEFECTO, CONEXION_WAREHOUSE, RAW_INDICADORES, RAW_SISMOS, SANTIAGO
from cosmos import DbtTaskGroup, ExecutionConfig, ProfileConfig, ProjectConfig, RenderConfig
from cosmos.constants import TestBehavior
from cosmos.profiles import PostgresUserPasswordProfileMapping

DBT_PROJECT_DIR = Path(os.environ.get("DBT_PROJECT_DIR", "/opt/airflow/dbt"))
DBT_EJECUTABLE = os.environ.get("DBT_EJECUTABLE", "/opt/dbt-venv/bin/dbt")

perfil = ProfileConfig(
    profile_name="chile",
    target_name="airflow",
    profile_mapping=PostgresUserPasswordProfileMapping(
        conn_id=CONEXION_WAREHOUSE,
        profile_args={"schema": "analitica"},
    ),
)


@dag(
    dag_id="transformacion_dbt",
    description="dbt build: staging, intermedia, marts y snapshots, con tests de calidad",
    schedule=(RAW_SISMOS | RAW_INDICADORES),
    start_date=datetime(2025, 1, 1, tzinfo=SANTIAGO),
    catchup=False,
    max_active_runs=1,
    default_args={**ARGUMENTOS_POR_DEFECTO, "retries": 1},
    tags=["transformacion", "dbt"],
    doc_md=__doc__,
)
def transformacion_dbt() -> None:
    # Frescura de las fuentes: falla (y avisa) si una carga lleva días sin datos nuevos.
    # Corre en paralelo para no frenar la transformación de los datos que sí llegaron.
    BashOperator(
        task_id="frescura_fuentes",
        bash_command=(
            f"cd {DBT_PROJECT_DIR} && "
            f"{DBT_EJECUTABLE} source freshness --profiles-dir . "
            "--target-path /tmp/dbt-target --log-path /tmp/dbt-logs"
        ),
        env={
            "DBT_HOST": "{{ conn.warehouse.host }}",
            "DBT_PORT": "{{ conn.warehouse.port }}",
            "DBT_USER": "{{ conn.warehouse.login }}",
            "DBT_PASSWORD": "{{ conn.warehouse.password }}",
            "DBT_DBNAME": "{{ conn.warehouse.schema }}",
        },
        append_env=True,
    )

    DbtTaskGroup(
        group_id="dbt",
        project_config=ProjectConfig(DBT_PROJECT_DIR, install_dbt_deps=False),
        profile_config=perfil,
        execution_config=ExecutionConfig(dbt_executable_path=DBT_EJECUTABLE),
        render_config=RenderConfig(
            test_behavior=TestBehavior.AFTER_EACH,
            # Los tests que cruzan dos modelos (relationships) van en una tarea aparte
            # que espera a ambos, en vez de colgarse del primero.
            should_detach_multiple_parents_tests=True,
        ),
    )


transformacion_dbt()
