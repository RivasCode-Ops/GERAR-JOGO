# 🎲 LOTOFÁCIL — Plataforma de Gestão de Jogos

## 📋 Análise do Sistema

### 1. O que é?

Sistema **zero-dependências** (apenas Python stdlib) para gerar, trackear e analisar jogos da Lotofácil. Opera em dois modos: **terminal interativo** ou **servidor web local**.

---

### 2. Arquitetura (6 Módulos)

```
main.py                          ← Entry point (CLI ou Server)
├── src/
│   ├── generator.py             ← Geração de jogos (algoritmo 9/6 parametrizável)
│   ├── validator.py             ← Filtros estatísticos (soma, paridade, primos)
│   ├── concursos.py             ← ConcursoDB (persistência JSON dos sorteios reais)
│   ├── tracker.py               ← Registro, avaliação e desempenho dos jogos
│   ├── scraper.py               ← Consumidor da API oficial da Caixa Econômica
│   ├── notifier.py              ← Vigia automático com notificação nativa
│   ├── export.py                ← Exportação CSV para lotérica
│   ├── models.py                ← Dataclasses (Concurso, Jogo, Desempenho)
│   ├── cli.py                   ← Interface de terminal (menu interativo)
│   └── server.py                ← Servidor HTTP com API REST + frontend embutido
├── tests/
│   ├── test_generator.py        ← 12 testes
│   ├── test_validator.py        ←  8 testes
│   ├── test_concursos.py        ←  6 testes
│   ├── test_tracker.py          ← 10 testes
│   ├── test_scraper.py          ← 10 testes
│   ├── test_export.py           ←  8 testes
│   └── test_notifier.py         ←  6 testes
├── data/
│   ├── concursos.json           ← Base de concursos (runtime)
│   └── jogos.json               ← Jogos registrados (runtime)
├── iniciar.bat                  ← Atalho Windows para servidor web
└── requirements.txt             ← Zero dependências externas
```

---

### 3. Fluxo de Dados

```
[API Caixa] ──scraper──> [ConcursoDB] ──base para──> [Generator] ──> [Jogos]
                                                              │
                                                              └──> [Tracker] ──> [Desempenho]
                                                                       │
                                                                 [Notifier] ──> [Notificação OS]
```

---

### 4. Componentes em Detalhe

#### 4.1 Generator (`generator.py`)
- **Algoritmo**: repete N números do último sorteio + (15-N) novos números
- **Parametrização**: `repetir` aceita `int` (fixo), `tuple[int,int]` (range aleatório) ou `None` (default 9)
- **Forçado**: busca exaustiva por combinação que satisfaz todos os filtros estatísticos
- **Exaustão computacional**: C(25,15) = 3.268.760 possibilidades; filtros reduzem para ~869K (26,6%)

#### 4.2 Validator (`validator.py`)
- 3 filtros estatísticos baseados na distribuição histórica da Lotofácil:
  - **Soma** entre 180 e 220
  - **Pares/Ímpares** na proporção 7/8 ou 8/7
  - **Primos** entre 5 e 6 (conjunto: {2,3,5,7,11,13,17,19,23})

#### 4.3 ConcursoDB (`concursos.py`)
- Persistência em JSON (`data/concursos.json`)
- Seed com 10 concursos históricos reais (2003-2026)
- Operações: adicionar, buscar, listar, último, total

#### 4.4 Tracker (`tracker.py`)
- Registra jogos com vínculo ao concurso base
- Avalia acertos contra qualquer concurso real
- Desempenho agregado: total por faixa (11=Quadra, 12=Quina, 13=Sena, 14pts, 15pts)

#### 4.5 Scraper (`scraper.py`)
- Consome API oficial da Caixa: `https://servicebus2.caixa.gov.br/portaldeloterias/api/lotofacil/`
- `fetch_latest()` — último concurso
- `fetch_by_number(n)` — concurso específico
- `sincronizar(db, backfill=N)` — sincroniza com crawleamento retroativo

#### 4.6 Notifier (`notifier.py`)
- `Vigia`: polling thread a cada 5 min na API da Caixa
- Ao detectar novo concurso: adiciona ao DB, avalia jogos, notifica
- Notificação nativa: Windows (`MessageBoxW`), Linux (`notify-send`), macOS (`osascript`)
- Sempre imprime no terminal com beep sonoro

#### 4.7 Export (`export.py`)
- Gera CSV (`;` como separador, `utf-8-sig`, números com zero-fill de 2 dígitos)
- Formato aceito por lotéricas brasileiras

#### 4.8 Servidor Web (`server.py`)
- API REST:
  - `GET /` — interface HTML/JS completa
  - `GET /api/ping` — health check
  - `GET /api/ultimo` — último concurso
  - `GET /api/concursos` — lista todos
  - `GET /api/desempenho` — estatísticas agregadas
  - `POST /api/gerar` — gera jogos com parâmetros
  - `POST /api/sincronizar` — sincroniza com Caixa
  - `POST /api/registrar` — cadastra concurso manual
- Diagnóstico automático: detecta se `localhost` resolve, fallback para `127.0.0.1`
- Frontend single-page embutido (dark theme, sem frameworks)

---

### 5. Como Usar

```bash
# Modo terminal (menu interativo)
python main.py

# Modo servidor web
python main.py server
# Acesse: http://127.0.0.1:5000

# Windows: duplo clique em iniciar.bat
```

### 6. Cobertura de Testes

```
62 testes, 0 dependências, 100% passando

test_concursos.py  ◆ 6 testes  ◆ ConcursoDB (CRUD, seed, persistência)
test_export.py     ◆ 8 testes  ◆ CSV (válido, erros, vazio, zfill, texto)
test_generator.py  ◆ 12 testes ◆ Geração (fixo, range, forçado, edge cases)
test_notifier.py   ◆ 6 testes  ◆ Vigia (descoberta, existente, avaliação, falha)
test_scraper.py    ◆ 10 testes ◆ API (parse, fetch, sincronizar, erro)
test_tracker.py    ◆ 10 testes ◆ Registro, avaliação, desempenho, persistência
test_validator.py  ◆ 8 testes  ◆ Validação, contagem, critérios
```

### 7. Limitações Conhecidas

- **Algoritmo 9/6 é cosmético**: filtros estatísticos reduzem o espaço amostral em apenas 73% — estatisticamente equivalente a aleatório puro para acertar 15 pontos
- **Valor real do app**: não está no algoritmo preditivo, mas no ecossistema de tracking (histórico, notificações, bolões) e na gestão de jogos
- **Scraper depende de API externa**: a API da Caixa pode mudar sem aviso prévio

### 8. Próximas Evoluções Possíveis

- Modo bolão (agregação multi-usuário + rateio simulado)
- Exportação PDF
- Deploy online (com timeout para atualizações)
- Amostragem da distribuição real de repetições a partir do histórico do ConcursoDB
