"""Ejecución manual sin Airflow, útil para desarrollo y para cargar datos de prueba.

python -m extraccion sismos --desde 2025-01-01 --hasta 2025-02-01
python -m extraccion indicadores --anio 2025
python -m extraccion fixtures tests/fixtures
"""

from __future__ import annotations

import argparse
import json
import logging
import os
from datetime import UTC, date, datetime, time
from pathlib import Path

import psycopg

from extraccion import esquema, mindicador, usgs
from extraccion.http import crear_cliente


def _dia(texto: str) -> datetime:
    return datetime.combine(date.fromisoformat(texto), time(), tzinfo=UTC)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="python -m extraccion")
    parser.add_argument("--dsn", default=os.environ.get("WAREHOUSE_DSN"))
    sub = parser.add_subparsers(dest="comando", required=True)
    s = sub.add_parser("sismos", help="carga sismos de un rango de fechas (UTC)")
    s.add_argument("--desde", type=_dia, required=True)
    s.add_argument("--hasta", type=_dia, required=True)
    i = sub.add_parser("indicadores", help="carga un año completo de cada indicador")
    i.add_argument("--anio", type=int, default=datetime.now(UTC).year)
    i.add_argument("--codigo", action="append", choices=mindicador.INDICADORES)
    f = sub.add_parser("fixtures", help="carga los JSON guardados en una carpeta")
    f.add_argument("carpeta", type=Path)
    args = parser.parse_args(argv)
    if not args.dsn:
        parser.error("falta --dsn o la variable WAREHOUSE_DSN")

    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    ejecucion = f"manual__{datetime.now(UTC):%Y-%m-%dT%H:%M:%S}"
    with psycopg.connect(args.dsn) as conn, crear_cliente() as client:
        esquema.asegurar(conn)
        if args.comando == "sismos":
            eventos = usgs.extraer(client, args.desde, args.hasta)
            print(usgs.cargar(conn, eventos, ejecucion))
        elif args.comando == "indicadores":
            for codigo in args.codigo or mindicador.INDICADORES:
                payload = mindicador.extraer_anio(client, codigo, args.anio)
                print(codigo, mindicador.cargar(conn, payload, ejecucion))
        else:
            for archivo in sorted(args.carpeta.glob("usgs_*.json")):
                eventos = json.loads(archivo.read_text(encoding="utf-8"))["features"]
                print(archivo.name, usgs.cargar(conn, eventos, f"fixtures__{archivo.name}"))
            for archivo in sorted(args.carpeta.glob("mindicador_*.json")):
                payload = json.loads(archivo.read_text(encoding="utf-8"))
                print(archivo.name, mindicador.cargar(conn, payload, f"fixtures__{archivo.name}"))


if __name__ == "__main__":
    main()
