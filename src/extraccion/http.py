"""Cliente HTTP con reintentos exponenciales para APIs públicas poco confiables."""

from __future__ import annotations

import logging
from typing import Any

import httpx
from tenacity import (
    before_sleep_log,
    retry,
    retry_if_exception,
    stop_after_attempt,
    wait_exponential,
)

from extraccion import __version__

log = logging.getLogger(__name__)

USER_AGENT = f"orquestacion-airflow-dbt/{__version__} (+https://github.com/sebakine/orquestacion-airflow-dbt)"


def _reintentable(exc: BaseException) -> bool:
    if isinstance(exc, httpx.TransportError):
        return True
    if isinstance(exc, httpx.HTTPStatusError):
        return exc.response.status_code == 429 or exc.response.status_code >= 500
    return False


def crear_cliente(
    timeout: float = 60.0, transport: httpx.BaseTransport | None = None
) -> httpx.Client:
    return httpx.Client(
        timeout=timeout,
        headers={"User-Agent": USER_AGENT, "Accept": "application/json"},
        follow_redirects=True,
        transport=transport,
    )


def get_json(
    client: httpx.Client,
    url: str,
    params: dict[str, Any] | None = None,
    *,
    intentos: int = 3,
    espera_max: float = 30.0,
) -> Any:
    """GET que reintenta errores de red, 429 y 5xx con espera exponencial.

    Los reintentos aquí cubren cortes breves; Airflow agrega reintentos a nivel
    de tarea para caídas más largas.
    """

    @retry(
        retry=retry_if_exception(_reintentable),
        stop=stop_after_attempt(intentos),
        wait=wait_exponential(multiplier=min(1.0, espera_max), max=espera_max),
        before_sleep=before_sleep_log(log, logging.WARNING),
        reraise=True,
    )
    def _get() -> Any:
        respuesta = client.get(url, params=params)
        respuesta.raise_for_status()
        return respuesta.json()

    return _get()
