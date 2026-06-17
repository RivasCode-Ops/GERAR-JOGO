import os
import tempfile
from datetime import date

from src.concursos import ConcursoDB
from src.models import Concurso


def _db_limpo(tmp: str) -> tuple[ConcursoDB, str]:
    path = os.path.join(tmp, "concursos.json")
    db = ConcursoDB(path)
    db.limpar()
    return db, path


def test_concurso_db_cria_com_seed():
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "concursos.json")
        db = ConcursoDB(path)
        assert db.total() > 0


def test_concurso_adicionar_e_buscar():
    with tempfile.TemporaryDirectory() as tmp:
        db, _ = _db_limpo(tmp)
        c = Concurso(numero=9999, data=date(2025, 1, 1), sorteio=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15])
        db.adicionar(c)
        assert db.buscar(9999) is not None
        assert db.buscar(9999).sorteio == [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]


def test_concurso_ultimo():
    with tempfile.TemporaryDirectory() as tmp:
        db, _ = _db_limpo(tmp)
        c = Concurso(numero=9999, data=date(2025, 1, 1), sorteio=list(range(1, 16)))
        db.adicionar(c)
        ultimo = db.ultimo()
        assert ultimo is not None
        assert ultimo.numero == 9999


def test_concurso_listar_todos():
    with tempfile.TemporaryDirectory() as tmp:
        db, _ = _db_limpo(tmp)
        c1 = Concurso(numero=1, data=date(2025, 1, 1), sorteio=list(range(1, 16)))
        c2 = Concurso(numero=2, data=date(2025, 1, 2), sorteio=list(range(2, 17)))
        db.adicionar(c1)
        db.adicionar(c2)
        todos = db.listar_todos()
        assert len(todos) == 2
        assert todos[0].numero == 1
        assert todos[1].numero == 2


def test_concurso_buscar_inexistente():
    with tempfile.TemporaryDirectory() as tmp:
        db, _ = _db_limpo(tmp)
        assert db.buscar(99999) is None


def test_concurso_persistencia():
    with tempfile.TemporaryDirectory() as tmp:
        db, path = _db_limpo(tmp)
        c = Concurso(numero=5000, data=date(2025, 6, 1), sorteio=list(range(1, 16)))
        db.adicionar(c)

        db2 = ConcursoDB(path)
        assert db2.buscar(5000) is not None
        assert db2.buscar(5000).data == date(2025, 6, 1)
