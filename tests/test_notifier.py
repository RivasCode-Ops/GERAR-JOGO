import json
import os
import tempfile
import threading
from datetime import date
from unittest.mock import patch, MagicMock

from src.concursos import ConcursoDB
from src.tracker import Tracker
from src.notifier import Vigia, notificar
from src.models import Concurso

RESPOSTA_API = {
    "numero": 9999,
    "dataApuracao": "17/06/2026",
    "listaDezenas": ["01", "03", "04", "06", "13", "14", "15", "16", "18", "19", "20", "21", "22", "23", "25"],
    "dezenasSorteadasOrdemSorteio": [],
    "numeroConcursoAnterior": 9998,
    "numeroConcursoProximo": 10000,
    "tipoJogo": "LOTOFACIL",
}


def _setup(tmp: str):
    cpath = os.path.join(tmp, "concursos.json")
    jpath = os.path.join(tmp, "jogos.json")
    db = ConcursoDB(cpath)
    db.limpar()
    db.adicionar(Concurso(numero=9998, data=date(2026, 6, 16), sorteio=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]))
    tracker = Tracker(concursos=db, path=jpath)
    return db, tracker


@patch("src.notifier.fetch_latest")
def test_vigia_descobre_novo_concurso(mock_fetch):
    mock_fetch.return_value = Concurso(numero=9999, data=date(2026, 6, 17), sorteio=[1, 3, 4, 6, 13, 14, 15, 16, 18, 19, 20, 21, 22, 23, 25])

    with tempfile.TemporaryDirectory() as tmp:
        db, tracker = _setup(tmp)
        assert db.buscar(9999) is None

        evento = threading.Event()

        class VigiaTest(Vigia):
            def _loop(self):
                super()._loop()
                evento.set()

        v = VigiaTest(db, tracker, intervalo=1)
        v.iniciar()
        evento.wait(timeout=5)
        v.parar()

        assert db.buscar(9999) is not None


@patch("src.notifier.fetch_latest")
def test_vigia_ignora_existente(mock_fetch):
    mock_fetch.return_value = Concurso(numero=9998, data=date(2026, 6, 16), sorteio=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15])

    with tempfile.TemporaryDirectory() as tmp:
        db, tracker = _setup(tmp)
        assert db.buscar(9998) is not None

        evento = threading.Event()

        class VigiaTest(Vigia):
            def _loop(self):
                super()._loop()
                evento.set()

        v = VigiaTest(db, tracker, intervalo=1)
        v.iniciar()
        evento.wait(timeout=5)
        v.parar()

        assert db.total() == 1


@patch("src.notifier.fetch_latest")
def test_vigia_avalia_jogos(mock_fetch):
    mock_fetch.return_value = Concurso(numero=9999, data=date(2026, 6, 17), sorteio=[1, 3, 4, 6, 13, 14, 15, 16, 18, 19, 20, 21, 22, 23, 25])

    with tempfile.TemporaryDirectory() as tmp:
        db, tracker = _setup(tmp)
        tracker.registrar_jogo([1, 3, 4, 6, 13, 14, 15, 16, 18, 19, 20, 21, 22, 23, 25], 9998)

        evento = threading.Event()

        class VigiaTest(Vigia):
            def _loop(self):
                super()._loop()
                evento.set()

        v = VigiaTest(db, tracker, intervalo=1)
        v.iniciar()
        evento.wait(timeout=5)
        v.parar()

        stats = tracker.desempenho_total()
        assert stats.total_concursos_avaliados == 1
        assert stats.total_quinze == 1


@patch("src.notifier.fetch_latest")
def test_vigia_falha_api(mock_fetch):
    mock_fetch.return_value = None

    with tempfile.TemporaryDirectory() as tmp:
        db, tracker = _setup(tmp)
        evento = threading.Event()

        class VigiaTest(Vigia):
            def _loop(self):
                super()._loop()
                evento.set()

        v = VigiaTest(db, tracker, intervalo=1)
        v.iniciar()
        evento.wait(timeout=5)
        v.parar()

        assert db.total() == 1


def test_notificar_nao_quebra():
    notificar("Teste", "Notificacao de teste")


def test_notificar_os_falha_silenciosa():
    notificar("Teste", "Mensagem")
