import random
from itertools import combinations

from .validator import (
    PRIMOS,
    TOTAL_NUMEROS,
    QTD_NUMEROS,
    validar_criterios,
    numeros_validos,
)

REPETIR = 9
NOVOS = 6


def _separar_repetidos_novos(ultimo_concurso: list[int]) -> tuple[set[int], set[int]]:
    todos = set(range(1, TOTAL_NUMEROS + 1))
    sorteados = set(ultimo_concurso)
    return sorteados, todos - sorteados


def _gerar_combinacao(repetir_candidatos: set[int], novos_candidatos: set[int]) -> list[int]:
    while True:
        repetir = set(random.sample(list(repetir_candidatos), REPETIR))
        novos = set(random.sample(list(novos_candidatos), NOVOS))
        combinacao = sorted(repetir | novos)
        if numeros_validos(combinacao) and validar_criterios(combinacao)["valido"]:
            return combinacao


def _forcar_criterios(ultimo_concurso: list[int]) -> list[int] | None:
    sorteados, nao_sorteados = _separar_repetidos_novos(ultimo_concurso)

    if len(sorteados) < REPETIR or len(nao_sorteados) < NOVOS:
        return None

    for rep in combinations(sorted(sorteados), REPETIR):
        for novos in combinations(sorted(nao_sorteados), NOVOS):
            combinacao = sorted(list(rep) + list(novos))
            if validar_criterios(combinacao)["valido"]:
                return combinacao

    return None


def gerar_jogo(
    ultimo_concurso: list[int],
    forcado: bool = False,
) -> dict:
    if not numeros_validos(ultimo_concurso):
        return {"erro": "Último concurso deve conter 15 números únicos entre 1 e 25"}

    if forcado:
        resultado = _forcar_criterios(ultimo_concurso)
        if resultado is None:
            return {"erro": "Nenhuma combinação válida encontrada com os critérios atuais"}
        combinacao = resultado
    else:
        combinacao = _gerar_combinacao(
            *_separar_repetidos_novos(ultimo_concurso)
        )

    analise = validar_criterios(combinacao)
    return {
        "jogo": combinacao,
        "repete_do_ultimo": sorted(set(combinacao) & set(ultimo_concurso)),
        "novos": sorted(set(combinacao) - set(ultimo_concurso)),
        "analise": analise,
    }


def gerar_multiplos_jogos(
    ultimo_concurso: list[int],
    quantidade: int = 5,
    forcado: bool = False,
) -> list[dict]:
    return [
        gerar_jogo(ultimo_concurso, forcado=forcado)
        for _ in range(quantidade)
    ]
