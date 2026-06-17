import json
import os
from datetime import date
from typing import Optional

from .models import Jogo, Desempenho
from .concursos import ConcursoDB

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
JOGOS_PATH = os.path.join(DATA_DIR, "jogos.json")


def _contar_acertos(sorteio: list[int], jogo: list[int]) -> int:
    return len(set(sorteio) & set(jogo))


NOME_FAIXAS = {11: "Quadra", 12: "Quina", 13: "Sena", 14: "Sena", 15: "15 Pontos"}


class Tracker:
    def __init__(self, concursos: Optional[ConcursoDB] = None, path: str = JOGOS_PATH):
        self.concursos = concursos or ConcursoDB()
        self.path = path
        self._jogos: dict[int, Jogo] = {}
        self._proximo_id: int = 1
        self._carregar()

    def _carregar(self) -> None:
        if os.path.exists(self.path):
            with open(self.path, "r", encoding="utf-8") as f:
                dados = json.load(f)
            self._jogos = {d["id"]: Jogo.from_dict(d) for d in dados}
            self._proximo_id = max(self._jogos.keys(), default=0) + 1

    def _salvar(self) -> None:
        os.makedirs(DATA_DIR, exist_ok=True)
        dados = [j.to_dict() for j in sorted(self._jogos.values(), key=lambda x: x.id)]
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(dados, f, indent=2, ensure_ascii=False)

    def registrar_jogo(self, numeros: list[int], concurso_base: int) -> Jogo:
        jogo = Jogo(
            id=self._proximo_id,
            numeros=sorted(numeros),
            concurso_base=concurso_base,
            data_criacao=date.today(),
        )
        self._jogos[jogo.id] = jogo
        self._proximo_id += 1
        self._salvar()
        return jogo

    def avaliar_contra_sorteio(self, concurso_numero: int) -> list[dict]:
        concurso = self.concursos.buscar(concurso_numero)
        if not concurso:
            return []

        resultados = []
        for jogo in self._jogos.values():
            acertos = _contar_acertos(concurso.sorteio, jogo.numeros)
            jogo.resultados[concurso_numero] = acertos
            resultados.append({"jogo_id": jogo.id, "acertos": acertos, "numeros": jogo.numeros})

        self._salvar()
        return resultados

    def avaliar_ultimo_sorteio(self) -> list[dict]:
        ultimo = self.concursos.ultimo()
        if not ultimo:
            return []
        return self.avaliar_contra_sorteio(ultimo.numero)

    def desempenho_total(self) -> Desempenho:
        stats = Desempenho()
        stats.total_jogos = len(self._jogos)

        concursos_avaliados = set()
        for jogo in self._jogos.values():
            for concurso_num, acertos in jogo.resultados.items():
                concursos_avaliados.add(concurso_num)
                stats.acertos_por_jogo.append(acertos)
                stats.max_acertos = max(stats.max_acertos, acertos)
                if acertos >= 11:
                    stats.total_onze += 1
                if acertos >= 12:
                    stats.total_doze += 1
                if acertos >= 13:
                    stats.total_treze += 1
                if acertos >= 14:
                    stats.total_catorze += 1
                if acertos >= 15:
                    stats.total_quinze += 1

        stats.total_concursos_avaliados = len(concursos_avaliados)
        return stats

    def listar_jogos(self) -> list[Jogo]:
        return sorted(self._jogos.values(), key=lambda j: j.id)

    def total_jogos(self) -> int:
        return len(self._jogos)

    def limpar(self) -> None:
        self._jogos = {}
        self._proximo_id = 1
        if os.path.exists(self.path):
            os.remove(self.path)
