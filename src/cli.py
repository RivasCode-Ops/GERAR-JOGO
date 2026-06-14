import sys

from .validator import numeros_validos, validar_criterios
from .generator import gerar_jogo, gerar_multiplos_jogos


def _formatar_analise(analise: dict) -> str:
    status = "[OK]" if analise["valido"] else "[FAIL]"
    return (
        f"    Soma: {analise['soma']} ({'OK' if analise['soma_entre_180_220'] else 'FORA'})\n"
        f"    Pares: {analise['pares']} / Impares: {analise['impares']} "
        f"({'OK' if analise['impares_pares_8_7'] else 'FORA'})\n"
        f"    Primos: {analise['primos']} "
        f"({'OK' if analise['primos_5_6'] else 'FORA'})"
    )


def _exibir_jogo(resultado: dict, idx: int = 1) -> None:
    if "erro" in resultado:
        print(f"  Jogo #{idx}: ERRO - {resultado['erro']}")
        return

    print(f"\n{'='*50}")
    print(f"  Jogo #{idx}")
    print(f"{'='*50}")
    print(f"  Números: {resultado['jogo']}")
    print(f"  Repete do último: {resultado['repete_do_ultimo']} ({len(resultado['repete_do_ultimo'])})")
    print(f"  Novos: {resultado['novos']} ({len(resultado['novos'])})")
    print(f"\n  Análise:")
    print(_formatar_analise(resultado["analise"]))


def _entrada_manual() -> list[int]:
    while True:
        raw = input("\nDigite os 15 números do último concurso (separados por espaço): ").strip()
        try:
            nums = [int(x) for x in raw.split()]
            if numeros_validos(nums):
                return sorted(nums)
            print("  ❌ Devem ser 15 números únicos entre 1 e 25.")
        except ValueError:
            print("  ❌ Entrada inválida. Use números separados por espaço.")


def main():
    print("\n" + "="*50)
    print("  GERADOR LOTOFACIL - Algoritmo 9/6")
    print("="*50)

    print("\n  Como deseja informar o último concurso?")
    print("  1 - Digitar manualmente")
    print("  2 - Usar exemplo interno (último concurso real)")

    opcao = input("\n  Escolha (1/2): ").strip()

    if opcao == "2":
        ultimo = [1, 2, 5, 7, 8, 9, 11, 13, 14, 17, 19, 20, 22, 24, 25]
        print(f"\n  Usando concurso exemplo: {ultimo}")
    else:
        ultimo = _entrada_manual()

    print(f"\n  Último concurso: {ultimo}")
    print(f"  {validar_criterios(ultimo)}")

    qtd = input("\n  Quantos jogos gerar? (Enter = 5): ").strip()
    qtd = int(qtd) if qtd.isdigit() else 5

    forcado = input("  Usar busca exaustiva (forçada)? (s/N): ").strip().lower() == "s"

    print(f"\n  Gerando {qtd} jogo(s) com algoritmo 9/6...\n")

    if qtd == 1:
        resultado = gerar_jogo(ultimo, forcado=forcado)
        _exibir_jogo(resultado)
    else:
        resultados = gerar_multiplos_jogos(ultimo, quantidade=qtd, forcado=forcado)
        for i, r in enumerate(resultados, 1):
            _exibir_jogo(r, i)

    print("\n" + "="*50)
    print("  Concluido!")
    print("="*50 + "\n")


if __name__ == "__main__":
    main()
