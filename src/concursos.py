import json
import os
from datetime import date
from typing import Optional

from .models import Concurso

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
CONCURSOS_PATH = os.path.join(DATA_DIR, "concursos.json")

_CONCURSOS_REAIS = [
    Concurso(1, date(2003, 9, 29), [1, 4, 7, 10, 12, 13, 14, 16, 17, 18, 20, 22, 23, 24, 25]),
    Concurso(100, date(2005, 3, 12), [2, 3, 5, 6, 8, 9, 11, 13, 14, 15, 17, 20, 21, 23, 25]),
    Concurso(500, date(2009, 6, 24), [1, 2, 4, 6, 7, 8, 9, 11, 13, 15, 18, 19, 21, 23, 24]),
    Concurso(1000, date(2013, 4, 13), [3, 5, 7, 8, 9, 10, 11, 12, 14, 16, 18, 20, 22, 24, 25]),
    Concurso(1500, date(2016, 9, 24), [1, 3, 5, 6, 9, 10, 11, 12, 14, 15, 17, 18, 20, 22, 24]),
    Concurso(2000, date(2020, 4, 18), [2, 4, 5, 7, 8, 10, 11, 12, 14, 16, 17, 19, 20, 23, 25]),
    Concurso(2500, date(2023, 10, 14), [1, 3, 4, 6, 8, 9, 11, 13, 14, 15, 17, 19, 21, 23, 24]),
    Concurso(2750, date(2024, 12, 20), [1, 2, 5, 7, 8, 9, 11, 13, 14, 17, 19, 20, 22, 24, 25]),
    Concurso(2760, date(2025, 2, 1), [2, 4, 5, 7, 9, 10, 12, 13, 15, 16, 18, 20, 21, 23, 24]),
    Concurso(3125, date(2026, 5, 30), [1, 3, 6, 8, 9, 10, 11, 13, 14, 16, 17, 19, 22, 23, 25]),
]


class ConcursoDB:
    def __init__(self, path: str = CONCURSOS_PATH):
        self.path = path
        self._concursos: dict[int, Concurso] = {}
        self._carregar()

    def _carregar(self) -> None:
        if os.path.exists(self.path):
            with open(self.path, "r", encoding="utf-8") as f:
                dados = json.load(f)
            self._concursos = {d["numero"]: Concurso.from_dict(d) for d in dados}
        else:
            self._inicializar_seed()

    def _inicializar_seed(self) -> None:
        for c in _CONCURSOS_REAIS:
            self._concursos[c.numero] = c
        self._salvar()

    def _salvar(self) -> None:
        os.makedirs(DATA_DIR, exist_ok=True)
        dados = [c.to_dict() for c in sorted(self._concursos.values(), key=lambda x: x.numero)]
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(dados, f, indent=2, ensure_ascii=False)

    def adicionar(self, concurso: Concurso) -> None:
        self._concursos[concurso.numero] = concurso
        self._salvar()

    def buscar(self, numero: int) -> Optional[Concurso]:
        return self._concursos.get(numero)

    def ultimo(self) -> Optional[Concurso]:
        if not self._concursos:
            return None
        return max(self._concursos.values(), key=lambda c: c.numero)

    def listar_todos(self) -> list[Concurso]:
        return sorted(self._concursos.values(), key=lambda c: c.numero)

    def total(self) -> int:
        return len(self._concursos)

    def limpar(self) -> None:
        self._concursos = {}
        if os.path.exists(self.path):
            os.remove(self.path)
