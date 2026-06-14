import pytest
from src.generator import gerar_jogo, gerar_multiplos_jogos
from src.validator import numeros_validos


def test_gerar_jogo_valido():
    ultimo = [1, 2, 5, 7, 8, 9, 11, 13, 14, 17, 19, 20, 22, 24, 25]
    resultado = gerar_jogo(ultimo)

    assert "erro" not in resultado
    assert numeros_validos(resultado["jogo"])
    assert resultado["analise"]["valido"] is True
    assert len(resultado["repete_do_ultimo"]) == 9
    assert len(resultado["novos"]) == 6


def test_gerar_jogo_forcado():
    ultimo = [1, 2, 5, 7, 8, 9, 11, 13, 14, 17, 19, 20, 22, 24, 25]
    resultado = gerar_jogo(ultimo, forcado=True)

    assert "erro" not in resultado
    assert numeros_validos(resultado["jogo"])
    assert resultado["analise"]["valido"] is True


def test_gerar_jogo_entrada_invalida():
    resultado = gerar_jogo([1, 2, 3])
    assert "erro" in resultado


def test_gerar_multiplos_jogos():
    ultimo = [1, 2, 5, 7, 8, 9, 11, 13, 14, 17, 19, 20, 22, 24, 25]
    resultados = gerar_multiplos_jogos(ultimo, quantidade=3)

    assert len(resultados) == 3
    for r in resultados:
        assert "erro" not in r
        assert r["analise"]["valido"] is True
