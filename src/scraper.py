import json
import urllib.request
from datetime import datetime
from typing import Optional

from .models import Concurso
from .concursos import ConcursoDB

API_BASE = "https://servicebus2.caixa.gov.br/portaldeloterias/api/lotofacil"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"


def _requisitar(url: str) -> Optional[dict]:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception:
        return None


def _parse_concurso(dados: dict) -> Optional[Concurso]:
    try:
        numero = int(dados["numero"])
        data = datetime.strptime(dados["dataApuracao"], "%d/%m/%Y").date()
        dezenas = sorted([int(d) for d in dados["listaDezenas"]])
        return Concurso(numero=numero, data=data, sorteio=dezenas)
    except (KeyError, ValueError, TypeError):
        return None


def fetch_latest() -> Optional[Concurso]:
    dados = _requisitar(API_BASE)
    if not dados:
        return None
    return _parse_concurso(dados)


def fetch_by_number(numero: int) -> Optional[Concurso]:
    dados = _requisitar(f"{API_BASE}/{numero}")
    if not dados:
        return None
    return _parse_concurso(dados)


def _buscar_anterior(numero: int) -> Optional[Concurso]:
    return fetch_by_number(numero - 1)


def sincronizar(db: ConcursoDB, backfill: int = 0) -> dict:
    """
    Busca o último concurso da API e adiciona ao DB se não existir.
    Se backfill > 0, busca também os N concursos anteriores.
    Retorna relatório: {adicionados: int, ja_existiam: int, erros: int}
    """
    relatorio = {"adicionados": 0, "ja_existiam": 0, "erros": 0}

    ultimo_api = fetch_latest()
    if not ultimo_api:
        relatorio["erros"] = 1
        return relatorio

    if db.buscar(ultimo_api.numero):
        relatorio["ja_existiam"] += 1
    else:
        db.adicionar(ultimo_api)
        relatorio["adicionados"] += 1

    if backfill > 0:
        pendentes = []
        prox = ultimo_api.numero - 1
        while len(pendentes) < backfill and prox >= 1:
            if db.buscar(prox):
                break
            pendentes.append(prox)
            prox -= 1

        for num in pendentes:
            concurso = fetch_by_number(num)
            if concurso:
                db.adicionar(concurso)
                relatorio["adicionados"] += 1
            else:
                relatorio["erros"] += 1

    return relatorio
