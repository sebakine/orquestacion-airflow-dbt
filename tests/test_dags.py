"""Integridad de los DAGs. Corren dentro de la imagen de Airflow (ver CI y Makefile)."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

pytest.importorskip("airflow")
pytest.importorskip("cosmos")

from airflow.dag_processing.dagbag import DagBag

pytestmark = pytest.mark.airflow

DAGS = Path(__file__).parent.parent / "dags"
# Airflow agrega la carpeta de DAGs al path; aquí se hace a mano para importar comun.py.
sys.path.insert(0, str(DAGS))


@pytest.fixture(scope="module")
def dagbag() -> DagBag:
    return DagBag(dag_folder=str(DAGS))


def test_no_hay_errores_de_importacion(dagbag: DagBag) -> None:
    assert dagbag.import_errors == {}
    assert set(dagbag.dag_ids) == {
        "extraccion_sismos",
        "extraccion_indicadores",
        "transformacion_dbt",
    }


def test_todos_tienen_reintentos_dueno_y_etiquetas(dagbag: DagBag) -> None:
    for dag in dagbag.dags.values():
        assert dag.owner == "sebastian", dag.dag_id
        assert dag.tags, dag.dag_id
        assert not dag.catchup, dag.dag_id
        for tarea in dag.tasks:
            assert tarea.retries >= 1, f"{dag.dag_id}.{tarea.task_id} sin reintentos"


def test_extraccion_sismos(dagbag: DagBag) -> None:
    dag = dagbag.dags["extraccion_sismos"]
    assert dag.task_ids == ["asegurar_esquema", "cargar_sismos"]
    carga = dag.get_task("cargar_sismos")
    assert carga.upstream_task_ids == {"asegurar_esquema"}
    assert [a.uri for a in carga.outlets] == ["postgres://postgres:5432/warehouse/raw/usgs_eventos"]


def test_extraccion_indicadores_mapea_una_tarea_por_indicador(dagbag: DagBag) -> None:
    dag = dagbag.dags["extraccion_indicadores"]
    carga = dag.get_task("cargar_indicador")
    assert carga.max_active_tis_per_dag == 2
    assert carga.outlets == []  # el asset se marca una vez, en resumir
    resumir = dag.get_task("resumir")
    assert resumir.upstream_task_ids == {"cargar_indicador"}
    assert [a.uri for a in resumir.outlets] == [
        "postgres://postgres:5432/warehouse/raw/mindicador_valores"
    ]


def test_transformacion_se_dispara_con_cualquiera_de_los_assets(dagbag: DagBag) -> None:
    dag = dagbag.dags["transformacion_dbt"]
    condicion = dag.timetable.asset_condition
    assert type(condicion).__name__ == "AssetAny"  # basta con que cambie una (OR)
    assert {a.uri for a in condicion.objects} == {
        "postgres://postgres:5432/warehouse/raw/usgs_eventos",
        "postgres://postgres:5432/warehouse/raw/mindicador_valores",
    }


def test_transformacion_tiene_un_run_y_un_test_por_modelo(dagbag: DagBag) -> None:
    dag = dagbag.dags["transformacion_dbt"]
    ids = set(dag.task_ids)
    modelos = [p.stem for p in (DAGS.parent / "dbt" / "models").rglob("*.sql")]
    assert len(modelos) >= 10
    for modelo in modelos:
        assert f"dbt.{modelo}.run" in ids
        assert f"dbt.{modelo}.test" in ids
    assert "dbt.snap_usgs_sismos_snapshot" in ids
    assert "frescura_fuentes" in ids
    # fct_sismos depende de la capa intermedia, no directo de staging.
    assert dag.get_task("dbt.fct_sismos.run").upstream_task_ids == {"dbt.int_sismos__ubicados.test"}
