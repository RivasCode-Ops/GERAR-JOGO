import os
import tempfile
from datetime import date

from src.concursos import ConcursoDB
from src.tracker import Tracker, _contar_acertos
from src.models import Concurso


def _db_com_concurso(tmp: str, numero: int = 9999, sorteio: list[int] | None = None) -> ConcursoDB:
    path = os.path.join(tmp, "concursos.json")
    db = ConcursoDB(path)
    db.limpar()
    if sorteio is None:
        sorteio = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
    db.adicionar(Concurso(numero=numero, data=date(2025, 1, 1), sorteio=sorteio))
    return db


def test_contar_acertos():
    sorteio = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
    jogo = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16]
    assert _contar_acertos(sorteio, jogo) == 14


def test_contar_acertos_zero():
    sorteio = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
    jogo = [16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 11, 12, 13, 14, 15]
    assert _contar_acertos(sorteio, jogo) == 5


def test_registrar_jogo():
    with tempfile.TemporaryDirectory() as tmp:
        db = _db_com_concurso(tmp)
        path = os.path.join(tmp, "jogos.json")
        tracker = Tracker(concursos=db, path=path)
        jogo = tracker.registrar_jogo([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15], 9999)
        assert jogo.id == 1
        assert tracker.total_jogos() == 1


def test_avaliar_contra_sorteio():
    with tempfile.TemporaryDirectory() as tmp:
        db = _db_com_concurso(tmp, 9999, [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15])
        path = os.path.join(tmp, "jogos.json")
        tracker = Tracker(concursos=db, path=path)
        tracker.registrar_jogo([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16], 9999)

        resultados = tracker.avaliar_contra_sorteio(9999)
        assert len(resultados) == 1
        assert resultados[0]["acertos"] == 14


def test_avaliar_ultimo_sorteio():
    with tempfile.TemporaryDirectory() as tmp:
        sorteio = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
        db = _db_com_concurso(tmp, 9999, sorteio)
        path = os.path.join(tmp, "jogos.json")
        tracker = Tracker(concursos=db, path=path)
        tracker.registrar_jogo(sorteio, 9999)

        resultados = tracker.avaliar_ultimo_sorteio()
        assert len(resultados) == 1
        assert resultados[0]["acertos"] == 15


def test_desempenho_total():
    with tempfile.TemporaryDirectory() as tmp:
        db = _db_com_concurso(tmp, 9999, [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15])
        path = os.path.join(tmp, "jogos.json")
        tracker = Tracker(concursos=db, path=path)
        tracker.registrar_jogo([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15], 9999)
        tracker.avaliar_contra_sorteio(9999)

        stats = tracker.desempenho_total()
        assert stats.total_jogos == 1
        assert stats.total_concursos_avaliados == 1
        assert stats.max_acertos == 15
        assert stats.total_quinze == 1


def test_tracker_persistencia():
    with tempfile.TemporaryDirectory() as tmp:
        db = _db_com_concurso(tmp)
        path = os.path.join(tmp, "jogos.json")
        tracker = Tracker(concursos=db, path=path)
        tracker.registrar_jogo([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15], 9999)

        tracker2 = Tracker(concursos=db, path=path)
        assert tracker2.total_jogos() == 1
        assert tracker2.listar_jogos()[0].numeros == [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]


def test_avaliar_concurso_inexistente():
    with tempfile.TemporaryDirectory() as tmp:
        db = _db_com_concurso(tmp)
        path = os.path.join(tmp, "jogos.json")
        tracker = Tracker(concursos=db, path=path)
        resultado = tracker.avaliar_contra_sorteio(8888)
        assert resultado == []


def test_desempenho_vazio():
    with tempfile.TemporaryDirectory() as tmp:
        db = _db_com_concurso(tmp)
        path = os.path.join(tmp, "jogos.json")
        tracker = Tracker(concursos=db, path=path)
        stats = tracker.desempenho_total()
        assert stats.total_jogos == 0
        assert stats.max_acertos == 0
