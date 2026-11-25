"""Pruebas de integración de la carga a raw contra PostgreSQL real."""

import copy

import psycopg
import pytest

from extraccion import esquema, mindicador, usgs
from extraccion.carga import ResultadoCarga

from .conftest import leer

pytestmark = pytest.mark.integracion


def test_esquema_es_idempotente(conn: psycopg.Connection) -> None:
    esquema.asegurar(conn)
    esquema.asegurar(conn)
    tablas = conn.execute(
        "SELECT table_name FROM information_schema.tables WHERE table_schema = 'raw' ORDER BY 1"
    ).fetchall()
    assert [t for (t,) in tablas] == [
        "mindicador_indicadores", "mindicador_valores", "usgs_eventos",
    ]  # fmt: skip


def test_carga_usgs_idempotente_y_con_revisiones(conn: psycopg.Connection) -> None:
    esquema.asegurar(conn)
    eventos = leer("usgs_1_2025T1.json")["features"]

    assert usgs.cargar(conn, eventos, "r1") == ResultadoCarga(insertados=len(eventos))
    assert usgs.cargar(conn, eventos, "r2") == ResultadoCarga(sin_cambios=len(eventos))

    [revision] = leer("usgs_2_revision.json")["features"]
    assert usgs.cargar(conn, [revision], "r3") == ResultadoCarga(actualizados=1)
    mag, ejecucion = conn.execute(
        "SELECT (payload->'properties'->>'mag')::numeric, ejecucion "
        "FROM raw.usgs_eventos WHERE id = %s",
        (revision["id"],),
    ).fetchone()  # type: ignore[misc]
    assert (float(mag), ejecucion) == (revision["properties"]["mag"], "r3")

    # Volver a cargar la versión vieja no pisa la revisión.
    assert usgs.cargar(conn, eventos, "r4").actualizados == 0


def test_carga_usgs_deja_la_version_mas_nueva_de_un_mismo_lote(conn: psycopg.Connection) -> None:
    esquema.asegurar(conn)
    original = leer("usgs_1_2025T1.json")["features"][0]
    nueva = copy.deepcopy(original)
    nueva["properties"]["updated"] += 1000
    nueva["properties"]["mag"] = 9.9
    assert usgs.cargar(conn, [nueva, original], "r1") == ResultadoCarga(insertados=1)
    [(mag,)] = conn.execute("SELECT payload->'properties'->>'mag' FROM raw.usgs_eventos").fetchall()
    assert mag == "9.9"


def test_carga_usgs_rechaza_eventos_sin_id(conn: psycopg.Connection) -> None:
    esquema.asegurar(conn)
    with pytest.raises(ValueError, match="sin id"):
        usgs.cargar(conn, [{"properties": {}}], "r1")


def test_carga_mindicador(conn: psycopg.Connection) -> None:
    esquema.asegurar(conn)
    payload = leer("mindicador_dolar_2025.json")
    n = len(payload["serie"])
    assert mindicador.cargar(conn, payload, "r1") == ResultadoCarga(insertados=n)
    assert mindicador.cargar(conn, payload, "r2") == ResultadoCarga(sin_cambios=n)

    corregido = copy.deepcopy(payload)
    corregido["serie"][0]["valor"] = 1.5
    corregido["nombre"] = "Dólar (corregido)"
    assert mindicador.cargar(conn, corregido, "r3") == ResultadoCarga(
        actualizados=1, sin_cambios=n - 1
    )
    assert conn.execute(
        "SELECT nombre FROM raw.mindicador_indicadores WHERE codigo = 'dolar'"
    ).fetchone() == ("Dólar (corregido)",)
