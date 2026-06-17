import os
import tempfile

from src.export import jogos_para_csv, jogos_para_texto


JOGO_VALIDO_1 = {
    "jogo": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
    "analise": {"valido": True},
}
JOGO_VALIDO_2 = {
    "jogo": [2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 25, 1, 3],
    "analise": {"valido": True},
}
JOGO_ERRO = {"erro": "Inválido"}


def test_exportar_csv_simples():
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "test.csv")
        resultado = jogos_para_csv([JOGO_VALIDO_1, JOGO_VALIDO_2], path)
        assert resultado == path
        assert os.path.exists(path)

        with open(path, "r", encoding="utf-8-sig") as f:
            linhas = f.read().strip().split("\n")
        assert len(linhas) == 2
        assert "01;02" in linhas[0]


def test_exportar_csv_com_erro():
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "test.csv")
        resultado = jogos_para_csv([JOGO_VALIDO_1, JOGO_ERRO, JOGO_VALIDO_2], path)
        with open(path, "r", encoding="utf-8-sig") as f:
            linhas = f.read().strip().split("\n")
        assert len(linhas) == 2


def test_exportar_csv_sem_jogos_validos():
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "test.csv")
        try:
            jogos_para_csv([JOGO_ERRO], path)
            assert False, "Deveria levantar ValueError"
        except ValueError:
            pass


def test_exportar_csv_lista_vazia():
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "test.csv")
        try:
            jogos_para_csv([], path)
            assert False, "Deveria levantar ValueError"
        except ValueError:
            pass


def test_exportar_csv_padrao_zfill():
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "test.csv")
        jogo = {"jogo": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 25], "analise": {"valido": True}}
        jogos_para_csv([jogo], path)
        with open(path, "r", encoding="utf-8-sig") as f:
            linha = f.read().strip()
        assert "25" in linha


def test_jogos_para_texto():
    texto = jogos_para_texto([JOGO_VALIDO_1, JOGO_ERRO, JOGO_VALIDO_2])
    assert "Jogo   1" in texto
    assert "Jogo   2" not in texto
    assert "Jogo   3" in texto
    assert "01 02 03" in texto


def test_jogos_para_texto_vazio():
    texto = jogos_para_texto([])
    assert texto == ""


def test_jogos_para_texto_tudo_erro():
    texto = jogos_para_texto([JOGO_ERRO, JOGO_ERRO])
    assert texto == ""
