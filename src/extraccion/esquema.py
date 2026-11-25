"""Tablas de la capa raw: los datos tal como llegan de cada API, más metadatos de carga."""

from __future__ import annotations

import psycopg

DDL = """
CREATE SCHEMA IF NOT EXISTS raw;

-- Un registro por sismo, con la última versión publicada por USGS.
-- Las revisiones anteriores las conserva el snapshot de dbt.
CREATE TABLE IF NOT EXISTS raw.usgs_eventos (
    id              text PRIMARY KEY,
    actualizado_ms  bigint NOT NULL,
    payload         jsonb NOT NULL,
    cargado_en      timestamptz NOT NULL DEFAULT now(),
    ejecucion       text NOT NULL
);

CREATE TABLE IF NOT EXISTS raw.mindicador_indicadores (
    codigo         text PRIMARY KEY,
    nombre         text NOT NULL,
    unidad_medida  text NOT NULL,
    cargado_en     timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS raw.mindicador_valores (
    codigo      text NOT NULL,
    fecha       text NOT NULL,          -- tal como viene: 2025-01-02T03:00:00.000Z
    valor       jsonb NOT NULL,         -- jsonb para no rechazar valores raros antes de dbt
    cargado_en  timestamptz NOT NULL DEFAULT now(),
    ejecucion   text NOT NULL,
    PRIMARY KEY (codigo, fecha)
);
"""


def asegurar(conn: psycopg.Connection) -> None:
    """Crea el esquema raw si no existe. Es idempotente."""
    with conn.transaction():
        conn.execute(DDL)
