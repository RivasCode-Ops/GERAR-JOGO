import subprocess
import sys
import threading
import time

from .scraper import fetch_latest
from .concursos import ConcursoDB
from .tracker import Tracker, NOME_FAIXAS

INTERVALO_PADRAO = 300


def _notificar_os(titulo: str, mensagem: str):
    sistema = sys.platform
    try:
        if sistema == "win32":
            import ctypes
            ctypes.windll.user32.MessageBoxW(0, mensagem, titulo, 0x40 | 0x1000)
        elif sistema == "linux":
            subprocess.run(["notify-send", titulo, mensagem], timeout=5, capture_output=True)
        elif sistema == "darwin":
            subprocess.run(
                ["osascript", "-e", f'display notification "{mensagem}" with title "{titulo}"'],
                timeout=5, capture_output=True,
            )
    except Exception:
        pass


def _beep():
    try:
        print("\a", end="", flush=True)
    except Exception:
        pass


def notificar(titulo: str, mensagem: str):
    linha = f"\n  [{time.strftime('%H:%M:%S')}] {titulo}: {mensagem}"
    print(linha)
    _beep()
    threading.Thread(target=_notificar_os, args=(titulo, mensagem), daemon=True).start()


class Vigia:
    def __init__(self, db: ConcursoDB, tracker: Tracker, intervalo: int = INTERVALO_PADRAO):
        self.db = db
        self.tracker = tracker
        self.intervalo = intervalo
        self._timer: threading.Timer | None = None
        self._ativo = False

    def iniciar(self):
        self._ativo = True
        self._loop()
        print(f"  Vigia ativo: checando novos concursos a cada {self.intervalo}s")

    def parar(self):
        self._ativo = False
        if self._timer:
            self._timer.cancel()
            self._timer = None

    def _loop(self):
        if not self._ativo:
            return
        try:
            ultimo_api = fetch_latest()
            if ultimo_api:
                existente = self.db.buscar(ultimo_api.numero)
                if not existente:
                    self.db.adicionar(ultimo_api)
                    resultados = self.tracker.avaliar_contra_sorteio(ultimo_api.numero)
                    if resultados:
                        msg = "\n".join(
                            f"Jogo #{r['jogo_id']}: {r['acertos']} acertos"
                            + (f" - {NOME_FAIXAS.get(r['acertos'], '')}!" if r["acertos"] >= 11 else "")
                            for r in resultados
                        )
                        notificar(
                            f"Concurso #{ultimo_api.numero}",
                            f"{len(resultados)} jogo(s) avaliado(s)\n{msg}",
                        )
                    else:
                        notificar(
                            "Novo Concurso",
                            f"Concurso #{ultimo_api.numero} registrado. Nenhum jogo para avaliar.",
                        )
        except Exception:
            pass

        self._timer = threading.Timer(self.intervalo, self._loop)
        self._timer.daemon = True
        self._timer.start()
