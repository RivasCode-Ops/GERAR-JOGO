PRIMOS = {2, 3, 5, 7, 11, 13, 17, 19, 23}

TOTAL_NUMEROS = 25
QTD_NUMEROS = 15
SOMA_MIN = 180
SOMA_MAX = 220

def numeros_validos(nums: list[int]) -> bool:
    return (
        len(nums) == QTD_NUMEROS
        and all(1 <= n <= TOTAL_NUMEROS for n in nums)
        and len(set(nums)) == QTD_NUMEROS
    )

def contar_pares(nums: list[int]) -> int:
    return sum(1 for n in nums if n % 2 == 0)

def contar_impares(nums: list[int]) -> int:
    return QTD_NUMEROS - contar_pares(nums)

def contar_primos(nums: list[int]) -> int:
    return sum(1 for n in nums if n in PRIMOS)

def soma(nums: list[int]) -> int:
    return sum(nums)

def validar_criterios(nums: list[int]) -> dict[str, bool]:
    if not numeros_validos(nums):
        return {"valido": False, "erro": "Números inválidos"}

    soma_val = soma(nums)
    pares = contar_pares(nums)
    impares = contar_impares(nums)
    primos = contar_primos(nums)

    criterios = {
        "soma_entre_180_220": SOMA_MIN <= soma_val <= SOMA_MAX,
        "impares_pares_8_7": (impares == 8 and pares == 7) or (impares == 7 and pares == 8),
        "primos_5_6": 5 <= primos <= 6,
    }

    return {
        "valido": all(criterios.values()),
        "soma": soma_val,
        "pares": pares,
        "impares": impares,
        "primos": primos,
        **criterios,
    }
