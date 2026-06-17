import random
from itertools import combinations
from typing import Optional, Union

from .validator import (
    TOTAL_NUMEROS,
    QTD_NUMEROS,
    validar_criterios,
    numeros_validos,
)

_REPETIR_PADRAO = 9
RangeRepetir = Union[int, tuple[int, int]]


def _resolver_repetir(repetir: Optional[RangeRepetir] = None) -> int:
    if repetir is None:
        return _REPETIR_PADRAO
    if isinstance(repetir, tuple):
        return random.randint(repetir[0], repetir[1])
    return repetir


def _separar_repetidos_novos(ultimo_concurso: list[int]) -> tuple[set[int], set[int]]:
    todos = set(range(1, TOTAL_NUMEROS + 1))
    sorteados = set(ultimo_concurso)
    return sorteados, todos - sorteados


def _gerar_combinacao(
    repetir_candidatos: set[int],
    novos_candidatos: set[int],
    qtd_repetir: int,
) -> list[int]:
    qtd_novos = QTD_NUMEROS - qtd_repetir
    while True:
        repetir = set(random.sample(list(repetir_candidatos), qtd_repetir))
        novos = set(random.sample(list(novos_candidatos), qtd_novos))
        combinacao = sorted(repetir | novos)
        if numeros_validos(combinacao) and validar_criterios(combinacao)["valido"]:
            return combinacao


def _forcar_criterios(
    ultimo_concurso: list[int],
    qtd_repetir: int,
) -> Optional[list[int]]:
    sorteados, nao_sorteados = _separar_repetidos_novos(ultimo_concurso)
    qtd_novos = QTD_NUMEROS - qtd_repetir

    if len(sorteados) < qtd_repetir or len(nao_sorteados) < qtd_novos:
        return None

    for rep in combinations(sorted(sorteados), qtd_repetir):
        for novos in combinations(sorted(nao_sorteados), qtd_novos):
            combinacao = sorted(list(rep) + list(novos))
            if validar_criterios(combinacao)["valido"]:
                return combinacao
    return None


def gerar_jogo(
    ultimo_concurso: list[int],
    forcado: bool = False,
    repetir: Optional[RangeRepetir] = None,
) -> dict:
    if not numeros_validos(ultimo_concurso):
        return {"erro": "Último concurso deve conter 15 números únicos entre 1 e 25"}

    qtd_repetir = _resolver_repetir(repetir)

    if forcado:
        resultado = _forcar_criterios(ultimo_concurso, qtd_repetir)
        if resultado is None:
            return {"erro": "Nenhuma combinação válida encontrada com os critérios atuais"}
        combinacao = resultado
    else:
        combinacao = _gerar_combinacao(
            *_separar_repetidos_novos(ultimo_concurso), qtd_repetir
        )

    analise = validar_criterios(combinacao)
    return {
        "jogo": combinacao,
        "repete_do_ultimo": sorted(set(combinacao) & set(ultimo_concurso)),
        "novos": sorted(set(combinacao) - set(ultimo_concurso)),
        "analise": analise,
        "qtd_repetir": qtd_repetir,
    }


def gerar_multiplos_jogos(
    ultimo_concurso: list[int],
    quantidade: int = 5,
    forcado: bool = False,
    repetir: Optional[RangeRepetir] = None,
) -> list[dict]:
    return [
        gerar_jogo(ultimo_concurso, forcado=forcado, repetir=repetir)
        for _ in range(quantidade)
    ]
