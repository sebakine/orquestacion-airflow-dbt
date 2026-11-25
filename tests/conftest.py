from __future__ import annotations

import json
import os
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import psycopg
import pytest

FIXTURES = Path(__file__).parent / "fixtures"


def leer(nombre: str) -> Any:
    return json.loads((FIXTURES / nombre).read_text(encoding="utf-8"))


@pytest.fixture
def conn() -> Iterator[psycopg.Connection]:
    """Conexión a una base de prueba vacía. Se salta si no hay TEST_DATABASE_URL."""
    dsn = os.environ.get("TEST_DATABASE_URL")
    if not dsn:
        pytest.skip("define TEST_DATABASE_URL para las pruebas de integración")
    with psycopg.connect(dsn, autocommit=True) as c:
        c.execute("DROP SCHEMA IF EXISTS raw CASCADE")
        yield c
