import pytest
from src.validator import (
    numeros_validos,
    contar_pares,
    contar_impares,
    contar_primos,
    soma,
    validar_criterios,
)


def test_numeros_validos_ok():
    nums = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
    assert numeros_validos(nums) is True


def test_numeros_validos_menos_de_15():
    assert numeros_validos([1, 2, 3]) is False


def test_numeros_validos_duplicados():
    nums = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 14]
    assert numeros_validos(nums) is False


def test_numeros_validos_fora_range():
    nums = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 26]
    assert numeros_validos(nums) is False


def test_contar_pares():
    assert contar_pares([2, 4, 6, 8, 10, 12, 14, 1, 3, 5, 7, 9, 11, 13, 15]) == 7


def test_contar_impares():
    assert contar_impares([1, 3, 5, 7, 9, 11, 13, 15, 2, 4, 6, 8, 10, 12, 14]) == 8


def test_contar_primos():
    nums = [2, 3, 5, 7, 11, 13, 1, 4, 6, 8, 9, 10, 12, 14, 15]
    assert contar_primos(nums) == 6


def test_soma():
    nums = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
    assert soma(nums) == 120


def test_validar_criterios_valido():
    nums = [1, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 25, 3]
    resultado = validar_criterios(nums)
    assert isinstance(resultado, dict)
    assert "valido" in resultado
