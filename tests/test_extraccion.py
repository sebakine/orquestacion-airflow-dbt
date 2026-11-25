import itertools
from datetime import UTC, datetime, timedelta

import httpx
import pytest

from extraccion import mindicador, usgs
from extraccion.carga import ResultadoCarga
from extraccion.http import USER_AGENT, crear_cliente, get_json

from .conftest import leer


def _cliente(manejador):  # type: ignore[no-untyped-def]
    return crear_cliente(transport=httpx.MockTransport(manejador))


def test_ventanas_cubren_el_rango_sin_solaparse() -> None:
    inicio = datetime(2025, 1, 1, tzinfo=UTC)
    fin = datetime(2025, 3, 15, tzinfo=UTC)
    partes = list(usgs.ventanas(inicio, fin))
    assert partes[0][0] == inicio
    assert partes[-1][1] == fin
    assert all(a[1] == b[0] for a, b in itertools.pairwise(partes))
    assert all(h - d <= usgs.VENTANA_MAX for d, h in partes)
    assert list(usgs.ventanas(fin, fin)) == []


def test_ventanas_exigen_zona_horaria() -> None:
    with pytest.raises(ValueError, match="zona horaria"):
        list(usgs.ventanas(datetime(2025, 1, 1), datetime(2025, 2, 1)))  # noqa: DTZ001


def test_extraer_usgs_arma_la_consulta_por_ventana() -> None:
    pedidos: list[httpx.Request] = []
    datos = leer("usgs_1_2025T1.json")

    def manejador(request: httpx.Request) -> httpx.Response:
        pedidos.append(request)
        return httpx.Response(200, json=datos if len(pedidos) == 1 else {"features": []})

    inicio = datetime(2025, 1, 1, tzinfo=UTC)
    with _cliente(manejador) as client:
        eventos = usgs.extraer(client, inicio, inicio + timedelta(days=40), magnitud_minima=3)
    assert len(eventos) == len(datos["features"])
    assert len(pedidos) == 2
    params = pedidos[0].url.params
    assert params["starttime"] == "2025-01-01T00:00:00+00:00"
    assert params["endtime"] == "2025-02-01T00:00:00+00:00"
    assert params["minmagnitude"] == "3"
    assert params["minlatitude"] == "-56.0"
    assert pedidos[0].headers["user-agent"] == USER_AGENT


def test_get_json_reintenta_errores_temporales() -> None:
    respuestas = [httpx.Response(503), httpx.Response(429), httpx.Response(200, json={"ok": 1})]

    def manejador(request: httpx.Request) -> httpx.Response:
        return respuestas.pop(0)

    with _cliente(manejador) as client:
        assert get_json(client, "https://x.cl/api", espera_max=0) == {"ok": 1}


def test_get_json_no_reintenta_404() -> None:
    llamadas = 0

    def manejador(request: httpx.Request) -> httpx.Response:
        nonlocal llamadas
        llamadas += 1
        return httpx.Response(404)

    with _cliente(manejador) as client, pytest.raises(httpx.HTTPStatusError):
        get_json(client, "https://x.cl/api", espera_max=0)
    assert llamadas == 1


def test_get_json_agota_reintentos() -> None:
    def manejador(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("sin red")

    with _cliente(manejador) as client, pytest.raises(httpx.ConnectError):
        get_json(client, "https://x.cl/api", intentos=2, espera_max=0)


def test_extraer_mindicador() -> None:
    datos = leer("mindicador_dolar_2025.json")

    def manejador(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/api/dolar/2025"
        return httpx.Response(200, json=datos)

    with _cliente(manejador) as client:
        assert mindicador.extraer_anio(client, "dolar", 2025)["codigo"] == "dolar"


def test_mindicador_valida_que_devuelva_el_indicador_pedido() -> None:
    def manejador(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"codigo": "euro", "serie": []})

    with _cliente(manejador) as client, pytest.raises(ValueError, match="devolvió 'euro'"):
        mindicador.extraer_anio(client, "dolar", 2025)


def test_resultado_carga_se_suma() -> None:
    total = ResultadoCarga(1, 2, 3) + ResultadoCarga(10, 0, 1)
    assert total == ResultadoCarga(11, 2, 4)
    assert total.total == 17
    assert total.como_dict() == {"insertados": 11, "actualizados": 2, "sin_cambios": 4}
