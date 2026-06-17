import pytest
from src.generator import gerar_jogo, gerar_multiplos_jogos, _resolver_repetir
from src.validator import numeros_validos

ULTIMO = [1, 2, 5, 7, 8, 9, 11, 13, 14, 17, 19, 20, 22, 24, 25]


def test_gerar_jogo_valido():
    resultado = gerar_jogo(ULTIMO)
    assert "erro" not in resultado
    assert numeros_validos(resultado["jogo"])
    assert resultado["analise"]["valido"] is True
    assert len(resultado["repete_do_ultimo"]) == 9
    assert len(resultado["novos"]) == 6


def test_gerar_jogo_forcado():
    resultado = gerar_jogo(ULTIMO, forcado=True)
    assert "erro" not in resultado
    assert numeros_validos(resultado["jogo"])
    assert resultado["analise"]["valido"] is True


def test_gerar_jogo_entrada_invalida():
    resultado = gerar_jogo([1, 2, 3])
    assert "erro" in resultado


def test_gerar_multiplos_jogos():
    resultados = gerar_multiplos_jogos(ULTIMO, quantidade=3, forcado=False)
    assert len(resultados) == 3
    for r in resultados:
        assert "erro" not in r
        assert r["analise"]["valido"] is True


def test_gerar_jogo_repetir_fixo_7():
    resultado = gerar_jogo(ULTIMO, repetir=7)
    assert "erro" not in resultado
    assert resultado["qtd_repetir"] == 7
    assert len(resultado["repete_do_ultimo"]) == 7
    assert len(resultado["novos"]) == 8


def test_gerar_jogo_repetir_fixo_11():
    resultado = gerar_jogo(ULTIMO, repetir=11)
    assert "erro" not in resultado
    assert resultado["qtd_repetir"] == 11
    assert len(resultado["repete_do_ultimo"]) == 11
    assert len(resultado["novos"]) == 4


def test_gerar_jogo_repetir_range():
    for _ in range(20):
        resultado = gerar_jogo(ULTIMO, repetir=(7, 11))
        assert "erro" not in resultado
        assert 7 <= resultado["qtd_repetir"] <= 11
        assert len(resultado["repete_do_ultimo"]) == resultado["qtd_repetir"]


def test_gerar_jogo_repetir_forcado_range():
    resultado = gerar_jogo(ULTIMO, forcado=True, repetir=(7, 11))
    assert "erro" not in resultado
    assert 7 <= resultado["qtd_repetir"] <= 11


def test_resolver_repetir_default():
    assert _resolver_repetir(None) == 9


def test_resolver_repetir_fixo():
    assert _resolver_repetir(8) == 8


def test_resolver_repetir_range():
    for _ in range(100):
        v = _resolver_repetir((7, 11))
        assert 7 <= v <= 11


def test_resolver_repetir_range_extremo():
    for _ in range(100):
        v = _resolver_repetir((5, 13))
        assert 5 <= v <= 13


def test_gerar_multiplos_jogos_repetir_range():
    resultados = gerar_multiplos_jogos(ULTIMO, quantidade=10, repetir=(7, 11))
    assert len(resultados) == 10
    for r in resultados:
        assert "erro" not in r
        assert r["analise"]["valido"] is True


def test_gerar_jogo_forcado_repetir_8():
    resultado = gerar_jogo(ULTIMO, forcado=True, repetir=8)
    assert "erro" not in resultado
    assert resultado["qtd_repetir"] == 8
    assert len(resultado["repete_do_ultimo"]) == 8
