import os
import sys
from datetime import date, datetime

from .validator import numeros_validos, validar_criterios
from .generator import gerar_jogo, gerar_multiplos_jogos
from .concursos import ConcursoDB
from .tracker import Tracker, NOME_FAIXAS
from .models import Concurso
from .scraper import sincronizar
from .export import jogos_para_csv, jogos_para_texto

_db = ConcursoDB()
_tracker = Tracker(concursos=_db)
_HORIZONTAL = "=" * 55


def _formatar_analise(analise: dict) -> str:
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
    print(f"\n{_HORIZONTAL}")
    print(f"  Jogo #{idx}")
    print(f"{_HORIZONTAL}")
    print(f"  Números: {resultado['jogo']}")
    qtd_rep = resultado.get("qtd_repetir", len(resultado["repete_do_ultimo"]))
    print(f"  Repete do último: {resultado['repete_do_ultimo']} ({qtd_rep})")
    print(f"  Novos: {resultado['novos']} ({len(resultado['novos'])})")
    print(f"\n  Análise:")
    print(_formatar_analise(resultado["analise"]))


def _entrada_15_numeros(msg: str = "Digite os 15 números (separados por espaço): ") -> list[int]:
    while True:
        raw = input(f"\n  {msg}").strip()
        try:
            nums = [int(x) for x in raw.split()]
            if numeros_validos(nums):
                return sorted(nums)
            print("  Devem ser 15 números únicos entre 1 e 25.")
        except ValueError:
            print("  Entrada inválida. Use números separados por espaço.")


def _menu_gerar():
    concursos = _db.listar_todos()
    if not concursos:
        print("\n  Nenhum concurso cadastrado. Cadastre um primeiro.")
        return

    ultimo = _db.ultimo()
    print(f"\n  Último concurso base: #{ultimo.numero} - {ultimo.sorteio}")

    print("\n  Configuração de repetição:")
    print("  1 - Clássico (9/6)")
    print("  2 - Automático (7-11)")
    print("  3 - Personalizado (valor ou range)")
    modo_rep = input("  Escolha (Enter = 1): ").strip()

    if modo_rep == "2":
        repetir = (7, 11)
    elif modo_rep == "3":
        raw = input("  Repetir (ex: 8 ou 7-11): ").strip()
        if "-" in raw:
            partes = raw.split("-")
            repetir = (int(partes[0]), int(partes[1]))
        else:
            repetir = int(raw) if raw.isdigit() else None
    else:
        repetir = None

    qtd = input("  Quantos jogos gerar? (Enter = 5): ").strip()
    qtd = int(qtd) if qtd.isdigit() else 5
    forcado = input("  Usar busca exaustiva? (s/N): ").strip().lower() == "s"

    print(f"\n  Gerando {qtd} jogo(s) com base no concurso #{ultimo.numero}...\n")

    resultados = gerar_multiplos_jogos(ultimo.sorteio, quantidade=qtd, forcado=forcado, repetir=repetir)
    for i, r in enumerate(resultados, 1):
        _exibir_jogo(r, i)

    track = input("\n  Registrar jogo(s) no tracker? (s/N): ").strip().lower() == "s"
    if track:
        for r in resultados:
            if "erro" not in r:
                j = _tracker.registrar_jogo(r["jogo"], ultimo.numero)
                print(f"  Jogo #{j.id} registrado com sucesso.")
        _tracker.desempenho_total()

    exportar = input("  Exportar jogos para CSV? (s/N): ").strip().lower() == "s"
    if exportar:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"jogos_lotofacil_{timestamp}.csv"
        try:
            path = jogos_para_csv(resultados, filename)
            print(f"  CSV exportado: {os.path.abspath(path)}")
        except ValueError as e:
            print(f"  Erro ao exportar: {e}")


def _menu_registrar_concurso():
    print(f"\n{_HORIZONTAL}")
    print("  REGISTRAR NOVO CONCURSO")
    print(f"{_HORIZONTAL}")

    try:
        raw = input("  Número do concurso: ").strip()
        numero = int(raw)
    except ValueError:
        print("  Número inválido.")
        return

    if _db.buscar(numero):
        print(f"  Concurso #{numero} já existe.")
        return

    try:
        raw = input("  Data (AAAA-MM-DD): ").strip()
        data = date.fromisoformat(raw)
    except ValueError:
        print("  Data inválida. Use AAAA-MM-DD.")
        return

    sorteio = _entrada_15_numeros("Números sorteados: ")

    concurso = Concurso(numero=numero, data=data, sorteio=sorteio)
    _db.adicionar(concurso)
    print(f"  Concurso #{numero} registrado com sucesso!")

    avaliar = input("  Avaliar jogos registrados contra este sorteio? (s/N): ").strip().lower() == "s"
    if avaliar:
        resultados = _tracker.avaliar_contra_sorteio(numero)
        if not resultados:
            print("  Nenhum jogo registrado para avaliar.")
        else:
            for r in resultados:
                nome = NOME_FAIXAS.get(r["acertos"], "")
                extra = f" - {nome}!" if nome else ""
                print(f"  Jogo #{r['jogo_id']}: {r['acertos']} acertos{extra}")


def _menu_listar_concursos():
    concursos = _db.listar_todos()
    if not concursos:
        print("\n  Nenhum concurso cadastrado.")
        return

    print(f"\n{_HORIZONTAL}")
    print(f"  CONCURSOS CADASTRADOS ({len(concursos)})")
    print(f"{_HORIZONTAL}")
    for c in concursos[-10:]:
        print(f"  #{c.numero:5d} | {c.data} | {c.sorteio}")
    if len(concursos) > 10:
        print(f"  ... (mostrando últimos 10 de {len(concursos)})")


def _menu_desempenho():
    stats = _tracker.desempenho_total()
    jogos = _tracker.listar_jogos()
    concursos = _db.listar_todos()

    print(f"\n{_HORIZONTAL}")
    print("  DESEMPENHO AGREGADO")
    print(f"{_HORIZONTAL}")
    print(f"  Jogos registrados:          {stats.total_jogos}")
    print(f"  Concursos na base:          {len(concursos)}")
    print(f"  Concursos avaliados:        {stats.total_concursos_avaliados}")
    print(f"  Máximo de acertos:          {stats.max_acertos}")
    print(f"  Quadras (11+):              {stats.total_onze}")
    print(f"  Quinas (12+):               {stats.total_doze}")
    print(f"  Senas (13+):                {stats.total_treze}")
    print(f"  14 pontos (14+):            {stats.total_catorze}")
    print(f"  15 pontos:                  {stats.total_quinze}")

    if jogos:
        print(f"\n  ÚLTIMOS JOGOS:")
        for j in jogos[-5:]:
            acertos_str = "; ".join(f"#{c}: {a}" for c, a in j.resultados.items())
            print(f"  #{j.id} | Base: #{j.concurso_base} | {j.numeros} | {acertos_str if acertos_str else 'sem avaliação'}")


def _menu_sincronizar():
    print(f"\n{_HORIZONTAL}")
    print("  SINCRONIZAR COM API DA CAIXA")
    print(f"{_HORIZONTAL}")
    print("  Buscando último concurso...")

    backfill = input("  Quantos concursos anteriores buscar? (Enter = 0): ").strip()
    backfill = int(backfill) if backfill.isdigit() else 0

    relatorio = sincronizar(_db, backfill=backfill)

    print(f"\n  Resultado:")
    print(f"    Adicionados:  {relatorio['adicionados']}")
    print(f"    Já existiam:  {relatorio['ja_existiam']}")
    print(f"    Erros:        {relatorio['erros']}")

    if relatorio["adicionados"] > 0:
        avaliar = input("\n  Avaliar jogos contra novo(s) sorteio(s)? (s/N): ").strip().lower() == "s"
        if avaliar:
            resultados = _tracker.avaliar_ultimo_sorteio()
            if resultados:
                for r in resultados:
                    nome = NOME_FAIXAS.get(r["acertos"], "")
                    extra = f" - {nome}!" if nome else ""
                    print(f"  Jogo #{r['jogo_id']}: {r['acertos']} acertos{extra}")


def main():
    while True:
        print(f"\n{_HORIZONTAL}")
        print("  GERADOR LOTOFACIL - Plataforma de Gestão")
        print(f"{_HORIZONTAL}")
        print("  1 - Gerar jogos")
        print("  2 - Registrar concurso real")
        print("  3 - Sincronizar com API Caixa")
        print("  4 - Listar concursos")
        print("  5 - Ver desempenho")
        print("  6 - Sair")
        print(f"{_HORIZONTAL}")

        opcao = input("  Escolha: ").strip()

        if opcao == "1":
            _menu_gerar()
        elif opcao == "2":
            _menu_registrar_concurso()
        elif opcao == "3":
            _menu_sincronizar()
        elif opcao == "4":
            _menu_listar_concursos()
        elif opcao == "5":
            _menu_desempenho()
        elif opcao == "6":
            print("\n  Concluído!\n")
            break
        else:
            print("  Opção inválida.")


if __name__ == "__main__":
    main()
