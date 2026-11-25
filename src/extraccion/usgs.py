"""Sismos desde la API FDSN de USGS: https://earthquake.usgs.gov/fdsnws/event/1/"""

from __future__ import annotations

import logging
from collections.abc import Iterator
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any

import httpx
import psycopg
from psycopg.types.json import Jsonb

from extraccion.carga import ResultadoCarga
from extraccion.http import get_json

log = logging.getLogger(__name__)

URL = "https://earthquake.usgs.gov/fdsnws/event/1/query"
#: USGS limita cada consulta a 20.000 eventos; un mes sobre Chile queda muy por debajo.
VENTANA_MAX = timedelta(days=31)


@dataclass(frozen=True, slots=True)
class Zona:
    """Rectángulo que cubre Chile continental y su costa."""

    lat_min: float = -56.0
    lat_max: float = -17.5
    lon_min: float = -76.0
    lon_max: float = -66.0


CHILE = Zona()


def ventanas(
    inicio: datetime, fin: datetime, tamano: timedelta = VENTANA_MAX
) -> Iterator[tuple[datetime, datetime]]:
    """Divide [inicio, fin) en ventanas consecutivas que no se solapan."""
    if inicio.tzinfo is None or fin.tzinfo is None:
        raise ValueError("las fechas deben tener zona horaria")
    cursor = inicio
    while cursor < fin:
        tope = min(cursor + tamano, fin)
        yield cursor, tope
        cursor = tope


def extraer(
    client: httpx.Client,
    inicio: datetime,
    fin: datetime,
    *,
    zona: Zona = CHILE,
    magnitud_minima: float = 2.5,
) -> list[dict[str, Any]]:
    """Devuelve los eventos (features GeoJSON) con hora de origen en [inicio, fin)."""
    eventos: list[dict[str, Any]] = []
    for desde, hasta in ventanas(inicio, fin):
        payload = get_json(
            client,
            URL,
            {
                "format": "geojson",
                "starttime": desde.isoformat(timespec="seconds"),
                "endtime": hasta.isoformat(timespec="seconds"),
                "minlatitude": zona.lat_min,
                "maxlatitude": zona.lat_max,
                "minlongitude": zona.lon_min,
                "maxlongitude": zona.lon_max,
                "minmagnitude": magnitud_minima,
                "orderby": "time-asc",
            },
        )
        features = payload.get("features", [])
        log.info("usgs: %s eventos entre %s y %s", len(features), desde, hasta)
        eventos.extend(features)
    return eventos


def cargar(
    conn: psycopg.Connection, eventos: list[dict[str, Any]], ejecucion: str
) -> ResultadoCarga:
    """Upsert por id: solo reemplaza un evento si USGS lo actualizó después.

    Correr dos veces la misma ventana no cambia nada (idempotente), y una
    revisión de USGS (por ejemplo, magnitud corregida) sí reemplaza la fila.
    """
    insertados = actualizados = 0
    vistos: dict[str, dict[str, Any]] = {}
    for evento in eventos:
        if "id" not in evento or "updated" not in evento.get("properties", {}):
            raise ValueError(f"evento sin id o sin properties.updated: {evento!r:.200}")
        previo = vistos.get(evento["id"])
        if previo is None or evento["properties"]["updated"] > previo["properties"]["updated"]:
            vistos[evento["id"]] = evento

    with conn.transaction():
        for evento in vistos.values():
            fila = conn.execute(
                """
                INSERT INTO raw.usgs_eventos (id, actualizado_ms, payload, ejecucion)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET
                    actualizado_ms = excluded.actualizado_ms,
                    payload = excluded.payload,
                    cargado_en = now(),
                    ejecucion = excluded.ejecucion
                WHERE raw.usgs_eventos.actualizado_ms < excluded.actualizado_ms
                RETURNING (xmax = 0) AS insertado
                """,
                (evento["id"], evento["properties"]["updated"], Jsonb(evento), ejecucion),
            ).fetchone()
            if fila is None:
                continue
            if fila[0]:
                insertados += 1
            else:
                actualizados += 1
    sin_cambios = len(vistos) - insertados - actualizados
    return ResultadoCarga(insertados, actualizados, sin_cambios)
