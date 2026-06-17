from dataclasses import dataclass, field, asdict
from datetime import date
from typing import Optional


@dataclass
class Concurso:
    numero: int
    data: date
    sorteio: list[int]

    def to_dict(self) -> dict:
        d = asdict(self)
        d["data"] = self.data.isoformat()
        return d

    @staticmethod
    def from_dict(d: dict) -> "Concurso":
        return Concurso(
            numero=d["numero"],
            data=date.fromisoformat(d["data"]),
            sorteio=d["sorteio"],
        )


@dataclass
class Jogo:
    id: int
    numeros: list[int]
    concurso_base: int
    data_criacao: date
    resultados: dict[int, int] = field(default_factory=dict)

    def to_dict(self) -> dict:
        d = asdict(self)
        d["data_criacao"] = self.data_criacao.isoformat()
        return d

    @staticmethod
    def from_dict(d: dict) -> "Jogo":
        return Jogo(
            id=d["id"],
            numeros=d["numeros"],
            concurso_base=d["concurso_base"],
            data_criacao=date.fromisoformat(d["data_criacao"]),
            resultados={int(k): v for k, v in d.get("resultados", {}).items()},
        )


@dataclass
class Desempenho:
    total_jogos: int = 0
    total_concursos_avaliados: int = 0
    acertos_por_jogo: list[int] = field(default_factory=list)
    max_acertos: int = 0
    total_onze: int = 0
    total_doze: int = 0
    total_treze: int = 0
    total_catorze: int = 0
    total_quinze: int = 0
