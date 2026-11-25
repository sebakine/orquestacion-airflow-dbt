"""Indicadores económicos desde https://mindicador.cl (series por año)."""

from __future__ import annotations

import logging
from typing import Any

import httpx
import psycopg
from psycopg.types.json import Jsonb

from extraccion.carga import ResultadoCarga
from extraccion.http import get_json

log = logging.getLogger(__name__)

URL_BASE = "https://mindicador.cl/api"
INDICADORES = ("dolar", "euro", "uf", "utm", "libra_cobre")


def extraer_anio(client: httpx.Client, codigo: str, anio: int) -> dict[str, Any]:
    payload: dict[str, Any] = get_json(client, f"{URL_BASE}/{codigo}/{anio}")
    if payload.get("codigo") != codigo:
        raise ValueError(f"mindicador devolvió {payload.get('codigo')!r} al pedir {codigo!r}")
    log.info("mindicador: %s %s con %s valores", codigo, anio, len(payload.get("serie", [])))
    return payload


def cargar(conn: psycopg.Connection, payload: dict[str, Any], ejecucion: str) -> ResultadoCarga:
    """Upsert por (código, fecha); una fila solo cambia si mindicador corrigió el valor."""
    codigo = payload["codigo"]
    serie = {p["fecha"]: p["valor"] for p in payload.get("serie", []) if "fecha" in p}
    insertados = actualizados = 0
    with conn.transaction():
        conn.execute(
            """
            INSERT INTO raw.mindicador_indicadores (codigo, nombre, unidad_medida)
            VALUES (%s, %s, %s)
            ON CONFLICT (codigo) DO UPDATE SET
                nombre = excluded.nombre,
                unidad_medida = excluded.unidad_medida,
                cargado_en = now()
            """,
            (codigo, payload.get("nombre") or codigo, payload.get("unidad_medida") or ""),
        )
        for fecha, valor in serie.items():
            fila = conn.execute(
                """
                INSERT INTO raw.mindicador_valores (codigo, fecha, valor, ejecucion)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (codigo, fecha) DO UPDATE SET
                    valor = excluded.valor,
                    cargado_en = now(),
                    ejecucion = excluded.ejecucion
                WHERE raw.mindicador_valores.valor IS DISTINCT FROM excluded.valor
                RETURNING (xmax = 0) AS insertado
                """,
                (codigo, fecha, Jsonb(valor), ejecucion),
            ).fetchone()
            if fila is None:
                continue
            if fila[0]:
                insertados += 1
            else:
                actualizados += 1
    return ResultadoCarga(insertados, actualizados, len(serie) - insertados - actualizados)
