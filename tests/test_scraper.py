import json
import os
import tempfile
from unittest.mock import patch, MagicMock
from datetime import date

from src.scraper import fetch_latest, fetch_by_number, sincronizar, _parse_concurso
from src.concursos import ConcursoDB
from src.models import Concurso

_RESPONSE_EXEMPLO = {
    "numero": 3712,
    "dataApuracao": "16/06/2026",
    "listaDezenas": ["01", "03", "04", "06", "13", "14", "15", "16", "18", "19", "20", "21", "22", "23", "25"],
    "dezenasSorteadasOrdemSorteio": ["22", "25", "01", "06", "16", "13", "23", "15", "18", "03", "04", "14", "19", "20", "21"],
    "numeroConcursoAnterior": 3711,
    "numeroConcursoProximo": 3713,
    "tipoJogo": "LOTOFACIL",
}

_RESPONSE_3711 = {
    **_RESPONSE_EXEMPLO,
    "numero": 3711,
    "listaDezenas": ["02", "04", "05", "06", "08", "09", "11", "12", "13", "15", "17", "19", "20", "22", "24"],
    "numeroConcursoAnterior": 3710,
    "numeroConcursoProximo": 3712,
}


def _mock_urlopen(response_data: dict):
    mock_resp = MagicMock()
    mock_resp.read.return_value = json.dumps(response_data).encode("utf-8")
    mock_resp.__enter__.return_value = mock_resp
    return mock_resp


def test_parse_concurso():
    concurso = _parse_concurso(_RESPONSE_EXEMPLO)
    assert concurso is not None
    assert concurso.numero == 3712
    assert concurso.data == date(2026, 6, 16)
    assert concurso.sorteio == [1, 3, 4, 6, 13, 14, 15, 16, 18, 19, 20, 21, 22, 23, 25]


def test_parse_concurso_malformed():
    assert _parse_concurso({}) is None
    assert _parse_concurso(None) is None
    assert _parse_concurso({"numero": "invalido"}) is None


@patch("urllib.request.urlopen")
def test_fetch_latest(mock_urlopen):
    mock_urlopen.return_value = _mock_urlopen(_RESPONSE_EXEMPLO)
    concurso = fetch_latest()
    assert concurso is not None
    assert concurso.numero == 3712


@patch("urllib.request.urlopen")
def test_fetch_by_number(mock_urlopen):
    mock_urlopen.return_value = _mock_urlopen(_RESPONSE_3711)
    concurso = fetch_by_number(3711)
    assert concurso is not None
    assert concurso.numero == 3711
    assert concurso.sorteio == [2, 4, 5, 6, 8, 9, 11, 12, 13, 15, 17, 19, 20, 22, 24]


@patch("urllib.request.urlopen")
def test_fetch_latest_falha(mock_urlopen):
    mock_urlopen.side_effect = Exception("Timeout")
    assert fetch_latest() is None


@patch("urllib.request.urlopen")
def test_fetch_by_number_falha(mock_urlopen):
    mock_urlopen.side_effect = Exception("Erro")
    assert fetch_by_number(9999) is None


@patch("urllib.request.urlopen")
def test_sincronizar_adiciona_novo(mock_urlopen):
    mock_urlopen.return_value = _mock_urlopen(_RESPONSE_EXEMPLO)
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "concursos.json")
        db = ConcursoDB(path)
        db.limpar()
        relatorio = sincronizar(db)
        assert relatorio["adicionados"] == 1
        assert relatorio["ja_existiam"] == 0
        assert db.buscar(3712) is not None


@patch("urllib.request.urlopen")
def test_sincronizar_ja_existente(mock_urlopen):
    mock_urlopen.return_value = _mock_urlopen(_RESPONSE_EXEMPLO)
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "concursos.json")
        db = ConcursoDB(path)
        db.limpar()
        db.adicionar(Concurso(numero=3712, data=date(2026, 6, 16), sorteio=[1, 3, 4, 6, 13, 14, 15, 16, 18, 19, 20, 21, 22, 23, 25]))
        relatorio = sincronizar(db)
        assert relatorio["adicionados"] == 0
        assert relatorio["ja_existiam"] == 1


@patch("urllib.request.urlopen")
def test_sincronizar_com_backfill(mock_urlopen):
    def side_effect(req, **kwargs):
        url = req.full_url if hasattr(req, "full_url") else str(req)
        if "3712" in url or url == "https://servicebus2.caixa.gov.br/portaldeloterias/api/lotofacil/":
            return _mock_urlopen(_RESPONSE_EXEMPLO)
        elif "3711" in url:
            return _mock_urlopen(_RESPONSE_3711)
        return _mock_urlopen(_RESPONSE_EXEMPLO)

    mock_urlopen.side_effect = side_effect
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "concursos.json")
        db = ConcursoDB(path)
        db.limpar()
        relatorio = sincronizar(db, backfill=1)
        assert relatorio["adicionados"] == 2
        assert db.buscar(3712) is not None
        assert db.buscar(3711) is not None


@patch("urllib.request.urlopen")
def test_sincronizar_com_erro_api(mock_urlopen):
    mock_urlopen.side_effect = Exception("API offline")
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "concursos.json")
        db = ConcursoDB(path)
        db.limpar()
        relatorio = sincronizar(db)
        assert relatorio["erros"] == 1
        assert relatorio["adicionados"] == 0
