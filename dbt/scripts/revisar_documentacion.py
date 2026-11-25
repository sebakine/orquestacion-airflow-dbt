"""Falla si algún modelo, snapshot, seed o fuente tiene columnas sin descripción.

Uso: python dbt/scripts/revisar_documentacion.py dbt/target
(después de ``dbt docs generate``, que deja manifest.json y catalog.json).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

TIPOS = {"model", "snapshot", "seed", "source"}


def pendientes(target: Path) -> list[str]:
    manifest = json.loads((target / "manifest.json").read_text(encoding="utf-8"))
    catalog = json.loads((target / "catalog.json").read_text(encoding="utf-8"))
    faltan: list[str] = []
    for clave, nodo in {**manifest["nodes"], **manifest["sources"]}.items():
        if nodo["resource_type"] not in TIPOS:
            continue
        if not nodo["description"].strip():
            faltan.append(f"{nodo['name']}: sin descripción")
        en_base = (catalog["nodes"].get(clave) or catalog["sources"].get(clave) or {}).get(
            "columns", {}
        )
        documentadas = nodo["columns"]
        faltan.extend(
            f"{nodo['name']}.{columna}: sin descripción"
            for columna in en_base
            if not documentadas.get(columna, {}).get("description", "").strip()
        )
    return faltan


def main() -> int:
    target = Path(sys.argv[1] if len(sys.argv) > 1 else "target")
    faltan = pendientes(target)
    for linea in faltan:
        print(linea)
    print(f"{len(faltan)} elementos sin documentar" if faltan else "Todo documentado.")
    return 1 if faltan else 0


if __name__ == "__main__":
    sys.exit(main())
