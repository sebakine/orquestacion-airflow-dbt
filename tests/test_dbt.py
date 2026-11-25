"""Prueba de punta a punta del proyecto dbt con los datos de tests/fixtures.

Carga la capa raw, corre `dbt build`, simula una revisión de USGS y vuelve a correr:
el snapshot debe guardar las dos versiones y fct_sismos (incremental) la nueva magnitud.
Necesita PostgreSQL (TEST_DATABASE_URL) y dbt (DBT_EJECUTABLE o `dbt` en el PATH).
"""

from __future__ import annotations

import os
import shutil
import subprocess
from decimal import Decimal
from pathlib import Path

import psycopg
import pytest

from extraccion import esquema, mindicador, usgs

from .conftest import FIXTURES, leer

pytestmark = pytest.mark.integracion

DBT_DIR = Path(__file__).parent.parent / "dbt"


def _dbt(*args: str, dsn: psycopg.conninfo.ConnectionInfo, tmp: Path) -> str:
    ejecutable = os.environ.get("DBT_EJECUTABLE") or shutil.which("dbt")
    if not ejecutable:
        pytest.skip("dbt no está instalado")
    entorno = {
        **os.environ,
        "DBT_HOST": dsn.host,
        "DBT_PORT": str(dsn.port),
        "DBT_USER": dsn.user,
        "DBT_PASSWORD": dsn.password or "",
        "DBT_DBNAME": dsn.dbname,
        "DBT_SEND_ANONYMOUS_USAGE_STATS": "false",
    }
    resultado = subprocess.run(
        [ejecutable, *args, "--profiles-dir", ".", "--target-path", str(tmp / "target"),
         "--log-path", str(tmp / "logs")],
        cwd=DBT_DIR, env=entorno, capture_output=True, text=True, check=False,
    )  # fmt: skip
    assert resultado.returncode == 0, resultado.stdout[-4000:]
    return resultado.stdout


def test_dbt_build_completo_y_revision_de_un_sismo(
    conn: psycopg.Connection, tmp_path: Path
) -> None:
    for esquema_dbt in ("staging", "intermedia", "marts", "snapshots", "referencia"):
        conn.execute(f"DROP SCHEMA IF EXISTS {esquema_dbt} CASCADE")
    esquema.asegurar(conn)
    usgs.cargar(conn, leer("usgs_1_2025T1.json")["features"], "prueba")
    for archivo in sorted(FIXTURES.glob("mindicador_*.json")):
        mindicador.cargar(conn, leer(archivo.name), "prueba")

    salida = _dbt("build", dsn=conn.info, tmp=tmp_path)
    assert "ERROR=0" in salida
    assert "WARN=0" in salida

    [revision] = leer("usgs_2_revision.json")["features"]
    usgs.cargar(conn, [revision], "revision")
    _dbt("build", dsn=conn.info, tmp=tmp_path)

    versiones = conn.execute(
        "SELECT magnitud, estado_revision FROM snapshots.snap_usgs_sismos "
        "WHERE sismo_id = %s ORDER BY dbt_valid_from",
        (revision["id"],),
    ).fetchall()
    assert versiones == [(Decimal("6.10"), "reviewed"), (Decimal("6.30"), "reviewed")]

    fila = conn.execute(
        "SELECT versiones, magnitud_inicial, magnitud_actual, cambio_magnitud "
        "FROM marts.mart_revisiones_sismos WHERE sismo_id = %s",
        (revision["id"],),
    ).fetchone()
    assert fila == (2, Decimal("6.10"), Decimal("6.30"), Decimal("0.20"))

    assert conn.execute(
        "SELECT magnitud, categoria FROM marts.fct_sismos WHERE sismo_id = %s", (revision["id"],)
    ).fetchone() == (Decimal("6.30"), "fuerte")

    # El dólar no se publica el sábado: ese día repite el valor del viernes.
    assert conn.execute(
        "SELECT es_publicado, valor = lag(valor) OVER () FROM ("
        "  SELECT * FROM marts.fct_indicadores_diarios WHERE indicador_codigo = 'dolar'"
        "  AND fecha IN ('2025-01-03', '2025-01-04') ORDER BY fecha) d OFFSET 1"
    ).fetchone() == (False, True)
