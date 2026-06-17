import csv
import os
from datetime import datetime

from .validator import numeros_validos


def jogos_para_csv(resultados: list[dict], path: str, delimiter: str = ";") -> str:
    valido = any("erro" not in r and numeros_validos(r["jogo"]) for r in resultados)
    if not valido:
        raise ValueError("Nenhum jogo válido para exportar")

    linhas = []
    for i, r in enumerate(resultados, 1):
        if "erro" in r or not numeros_validos(r.get("jogo", [])):
            continue
        numeros_str = [str(n).zfill(2) for n in r["jogo"]]
        linhas.append([f"Jogo {i}"] + numeros_str)

    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f, delimiter=delimiter)
        writer.writerows(linhas)

    return path


def jogos_para_texto(resultados: list[dict]) -> str:
    linhas = []
    for i, r in enumerate(resultados, 1):
        if "erro" in r:
            continue
        numeros_str = " ".join(str(n).zfill(2) for n in r["jogo"])
        linhas.append(f"Jogo {i:3d}: {numeros_str}")
    return "\n".join(linhas)
