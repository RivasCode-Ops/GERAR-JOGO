import json
import os
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from datetime import date, datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.concursos import ConcursoDB
from src.tracker import Tracker
from src.generator import gerar_multiplos_jogos
from src.scraper import sincronizar
from src.export import jogos_para_csv, jogos_para_texto
from src.models import Concurso
from src.notifier import Vigia

_db = ConcursoDB()
_tracker = Tracker(concursos=_db)
CONCURSOS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")


def _gerar_html() -> str:
    return """<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Lotofácil - Plataforma de Gestão</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:system-ui,-apple-system,sans-serif;background:#0f172a;color:#e2e8f0;min-height:100vh}
.container{max-width:960px;margin:0 auto;padding:20px}
h1{text-align:center;color:#fbbf24;margin-bottom:8px;font-size:1.5rem}
.sub{text-align:center;color:#64748b;margin-bottom:24px;font-size:.85rem}
nav{display:flex;gap:4px;flex-wrap:wrap;margin-bottom:24px;justify-content:center}
nav button{background:#1e293b;border:1px solid #334155;color:#e2e8f0;padding:8px 16px;border-radius:6px;cursor:pointer;font-size:.85rem;transition:.2s}
nav button:hover{background:#334155;border-color:#fbbf24}
nav button.ativo{background:#fbbf24;color:#0f172a;border-color:#fbbf24;font-weight:600}
.painel{display:none;background:#1e293b;border:1px solid #334155;border-radius:8px;padding:20px}
.painel.ativo{display:block}
label{display:block;margin:12px 0 4px;color:#94a3b8;font-size:.85rem}
input,select{width:100%;padding:10px;background:#0f172a;border:1px solid #334155;border-radius:6px;color:#e2e8f0;font-size:.9rem}
input:focus{outline:none;border-color:#fbbf24}
input[type=number]{width:120px}
.linha{display:flex;gap:12px;flex-wrap:wrap;align-items:center}
.btn{background:#fbbf24;color:#0f172a;border:none;padding:10px 24px;border-radius:6px;font-weight:600;cursor:pointer;margin-top:16px;font-size:.9rem;transition:.2s}
.btn:hover{background:#f59e0b}
.btn:disabled{opacity:.5;cursor:not-allowed}
.btn-sec{background:#334155;color:#e2e8f0}
.btn-sec:hover{background:#475569}
#resultado{margin-top:16px;padding:12px;background:#0f172a;border-radius:6px;white-space:pre-wrap;font-family:monospace;font-size:.8rem;overflow-x:auto;max-height:500px;overflow-y:auto}
table{width:100%;border-collapse:collapse;margin-top:12px;font-size:.8rem}
th{background:#334155;color:#fbbf24;padding:8px;text-align:left}
td{padding:8px;border-bottom:1px solid #1e293b}
tr:hover td{background:#0f172a}
.erro{color:#f87171}
.ok{color:#4ade80}
.ace{display:inline-block;padding:2px 8px;border-radius:4px;font-weight:600}
.ace11{background:#1e3a5f;color:#93c5fd}
.ace12{background:#1e3a5f;color:#93c5fd}
.ace13{background:#5f3a1e;color:#fcd34d}
.ace14{background:#5f3a1e;color:#fcd34d}
.ace15{background:#5f1e1e;color:#fca5a5}
.spin{display:inline-block;width:16px;height:16px;border:2px solid #fbbf24;border-top-color:transparent;border-radius:50%;animation:spin .6s linear infinite;vertical-align:middle;margin-right:8px}
@keyframes spin{to{transform:rotate(360deg)}}
}
</style>
</head>
<body>
<div class="container">
<h1>&#127922; LOTOFÁCIL</h1>
<p class="sub">Plataforma de Gestão de Jogos</p>

<nav id="nav">
<button class="ativo" onclick="mostrar('gerar')">&#9889; Gerar</button>
<button onclick="mostrar('sinc')">&#128260; Sincronizar</button>
<button onclick="mostrar('concursos')">&#128218; Concursos</button>
<button onclick="mostrar('desempenho')">&#128200; Desempenho</button>
<button onclick="mostrar('registrar')">&#10003; Registrar</button>
</nav>

<div id="p-gerar" class="painel ativo">
<label>Último concurso base</label>
<div id="ultimo-info" class="linha" style="color:#94a3b8">Carregando...</div>
<label>Modo de repetição</label>
<select id="modo-rep">
<option value="classico">Clássico (9/6)</option>
<option value="auto">Automático (7-11)</option>
<option value="personalizado">Personalizado</option>
</select>
<div id="rep-personalizado" style="display:none">
<label>Valor ou range (ex: 8 ou 7-11)</label>
<input type="text" id="rep-valor" placeholder="8">
</div>
<label>Quantidade de jogos</label>
<input type="number" id="qtd" value="5" min="1" max="100">
<label><input type="checkbox" id="forcado"> Busca exaustiva (forçada)</label>
<button class="btn" onclick="gerar()">&#9889; Gerar Jogos</button>
<div id="resultado-gerar"></div>
</div>

<div id="p-sinc" class="painel">
<label>Buscar últimos concursos da Caixa</label>
<label>Concursos anteriores (backfill)</label>
<input type="number" id="backfill" value="0" min="0" max="100">
<button class="btn" onclick="sincronizar()">&#128260; Sincronizar</button>
<div id="resultado-sinc"></div>
</div>

<div id="p-concursos" class="painel">
<button class="btn btn-sec" onclick="listarConcursos()">&#128218; Atualizar</button>
<div id="resultado-concursos"></div>
</div>

<div id="p-desempenho" class="painel">
<button class="btn btn-sec" onclick="verDesempenho()">&#128200; Atualizar</button>
<div id="resultado-desempenho"></div>
</div>

<div id="p-registrar" class="painel">
<label>Número do concurso</label>
<input type="number" id="reg-numero">
<label>Data (AAAA-MM-DD)</label>
<input type="date" id="reg-data">
<label>15 números sorteados (separados por espaço)</label>
<input type="text" id="reg-numeros" placeholder="ex: 01 03 04 06 13 14 15 16 18 19 20 21 22 23 25">
<button class="btn" onclick="registrarConcurso()">&#10003; Registrar</button>
<div id="resultado-registrar"></div>
</div>
</div>

<script>
const BASE = '';
function mostrar(id) {
document.querySelectorAll('.painel').forEach(p=>p.classList.remove('ativo'));
document.getElementById('p-'+id).classList.add('ativo');
document.querySelectorAll('nav button').forEach(b=>b.classList.remove('ativo'));
[...document.querySelectorAll('nav button')].find(b=>b.textContent.includes(document.querySelector('#p-'+id+' label')?.textContent[0]||id))?.classList.add('ativo');
event?.target?.classList?.add('ativo');
}
document.getElementById('modo-rep').onchange=function(){
document.getElementById('rep-personalizado').style.display=this.value==='personalizado'?'block':'none';
};
function api(path,body,cb){
const opts={method:'POST',headers:{'Content-Type':'application/json'}};
if(body)opts.body=JSON.stringify(body);
fetch(path,opts).then(r=>r.json()).then(cb).catch(e=>cb({erro:e.message}));
}
function carregarUltimo(){
fetch('/api/ultimo').then(r=>r.json()).then(d=>{
document.getElementById('ultimo-info').innerHTML=d.erro ? `<span class="erro">${d.erro}</span>` : `#${d.numero} | ${d.data} | <code>${d.numeros.join(' ')}</code>`;
});
}
window.onload=function(){
carregarUltimo();
listarConcursos();
};
function gerar(){
const el=document.getElementById('resultado-gerar');
el.innerHTML='<span class="spin"></span> Gerando...';
const modo=document.getElementById('modo-rep').value;
let repetir=null;
if(modo==='personalizado'){
const v=document.getElementById('rep-valor').value.trim();
if(v.includes('-')){const p=v.split('-');repetir=[parseInt(p[0]),parseInt(p[1])]}
else if(v){repetir=parseInt(v)}
}
api('/api/gerar',{
ultimo:null,
quantidade:parseInt(document.getElementById('qtd').value),
forcado:document.getElementById('forcado').checked,
repetir:repetir
},d=>{
if(d.erro){el.innerHTML=`<span class="erro">${d.erro}</span>`;return}
let html='';
d.jogos.forEach((r,i)=>{
if(r.erro){html+=`<div class="erro"><b>Jogo #${i+1}:</b> ${r.erro}</div>`;return}
html+=`<div><b>Jogo #${i+1}</b> (repete: ${r.qtd_repetir})<br><code>${r.numeros.join(' ')}</code></div>`;
});
el.innerHTML=html;
});
}
function sincronizar(){
const el=document.getElementById('resultado-sinc');
el.innerHTML='<span class="spin"></span> Sincronizando...';
api('/api/sincronizar',{backfill:parseInt(document.getElementById('backfill').value)},d=>{
el.innerHTML=`Adicionados: <b>${d.adicionados}</b> | Já existiam: <b>${d.ja_existiam}</b> | Erros: <b>${d.erros}</b>`;
carregarUltimo();
listarConcursos();
});
}
function listarConcursos(){
const el=document.getElementById('resultado-concursos');
fetch('/api/concursos').then(r=>r.json()).then(d=>{
if(d.erro||!d.concursos||d.concursos.length===0){el.innerHTML='<span style="color:#94a3b8">Nenhum concurso cadastrado.</span>';return}
let html=`<table><tr><th>#</th><th>Data</th><th>Números</th></tr>`;
d.concursos.slice(-15).forEach(c=>{
html+=`<tr><td>${c.numero}</td><td>${c.data}</td><td><code>${c.numeros.join(' ')}</code></td></tr>`;
});
html+=`</table>${d.concursos.length>15?`<p style="color:#64748b;margin-top:8px">... mostrando últimos 15 de ${d.concursos.length}</p>`:''}`;
el.innerHTML=html;
});
}
function verDesempenho(){
const el=document.getElementById('resultado-desempenho');
el.innerHTML='<span class="spin"></span> Carregando...';
fetch('/api/desempenho').then(r=>r.json()).then(d=>{
let html=`
<div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:16px">
<div style="background:#0f172a;padding:12px;border-radius:6px"><b style="color:#fbbf24">${d.total_jogos}</b><br><span style="color:#94a3b8">Jogos registrados</span></div>
<div style="background:#0f172a;padding:12px;border-radius:6px"><b style="color:#fbbf24">${d.total_concursos}</b><br><span style="color:#94a3b8">Concursos na base</span></div>
<div style="background:#0f172a;padding:12px;border-radius:6px"><b style="color:#fbbf24">${d.concursos_avaliados}</b><br><span style="color:#94a3b8">Avaliados</span></div>
<div style="background:#0f172a;padding:12px;border-radius:6px"><b style="color:#fbbf24">${d.max_acertos}</b><br><span style="color:#94a3b8">Máx acertos</span></div>
</div>
<div style="display:grid;grid-template-columns:repeat(5,1fr);gap:8px;text-align:center;margin-bottom:16px">
<div class="ace ace11">${d.onze}</div><div class="ace ace12">${d.doze}</div><div class="ace ace13">${d.treze}</div><div class="ace ace14">${d.catorze}</div><div class="ace ace15">${d.quinze}</div>
</div>
<div style="display:grid;grid-template-columns:repeat(5,1fr);gap:8px;text-align:center;font-size:.7rem;color:#94a3b8;margin-top:-12px;margin-bottom:16px">
<span>Quadra(11)</span><span>Quina(12)</span><span>Sena(13)</span><span>14pts</span><span>15pts</span>
</div>`;
if(d.ultimos_jogos&&d.ultimos_jogos.length){
html+=`<table><tr><th>#</th><th>Jogo</th><th>Base</th><th>Acertos</th></tr>`;
d.ultimos_jogos.forEach(j=>{
const acertos=Object.entries(j.acertos||{}).map(([c,a])=>`#${c}: ${a}`).join('; ')||'sem avaliação';
html+=`<tr><td>${j.id}</td><td><code>${j.numeros.join(' ')}</code></td><td>#${j.concurso_base}</td><td>${acertos}</td></tr>`;
});
html+=`</table>`;
}
el.innerHTML=html;
});
}
function registrarConcurso(){
const el=document.getElementById('resultado-registrar');
const nums=document.getElementById('reg-numeros').value.trim().split(/\\s+/).map(Number);
api('/api/registrar',{
numero:parseInt(document.getElementById('reg-numero').value),
data:document.getElementById('reg-data').value,
numeros:nums
},d=>{
el.innerHTML=d.erro?`<span class="erro">${d.erro}</span>`:`<span class="ok">Concurso #${d.numero} registrado!</span>`;
if(!d.erro){carregarUltimo();listarConcursos()}
});
}
</script>
</body>
</html>"""


class Handler(BaseHTTPRequestHandler):
    def _json(self, data, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False, default=str).encode("utf-8"))

    def _html(self, content):
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(content.encode("utf-8"))

    def _ler_corpo(self):
        length = int(self.headers.get("Content-Length", 0))
        if length == 0:
            return {}
        return json.loads(self.rfile.read(length).decode("utf-8"))

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/":
            self._html(_gerar_html())
        elif path == "/api/ultimo":
            ultimo = _db.ultimo()
            if not ultimo:
                self._json({"erro": "Nenhum concurso cadastrado"})
            else:
                self._json({"numero": ultimo.numero, "data": str(ultimo.data), "numeros": ultimo.sorteio})
        elif path == "/api/concursos":
            todos = _db.listar_todos()
            self._json({"concursos": [{"numero": c.numero, "data": str(c.data), "numeros": c.sorteio} for c in todos]})
        elif path == "/api/desempenho":
            stats = _tracker.desempenho_total()
            jogos = _tracker.listar_jogos()
            self._json({
                "total_jogos": stats.total_jogos,
                "total_concursos": _db.total(),
                "concursos_avaliados": stats.total_concursos_avaliados,
                "max_acertos": stats.max_acertos,
                "onze": stats.total_onze,
                "doze": stats.total_doze,
                "treze": stats.total_treze,
                "catorze": stats.total_catorze,
                "quinze": stats.total_quinze,
                "ultimos_jogos": [{"id": j.id, "numeros": j.numeros, "concurso_base": j.concurso_base, "acertos": j.resultados} for j in jogos[-10:]],
            })
        else:
            self._json({"erro": "rota nao encontrada"}, 404)

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path
        try:
            body = self._ler_corpo()
        except Exception:
            self._json({"erro": "corpo JSON invalido"}, 400)
            return

        try:
            self._handle_post(path, body)
        except Exception as e:
            import traceback
            traceback.print_exc()
            self._json({"erro": str(e)}, 500)

    def _handle_post(self, path: str, body: dict):
        if path == "/api/gerar":
            ultimo = _db.ultimo()
            if not ultimo:
                self._json({"erro": "Nenhum concurso cadastrado. Sincronize primeiro."})
                return
            quantidade = body.get("quantidade", 5)
            forcado = body.get("forcado", False)
            repetir = body.get("repetir", None)
            resultados = gerar_multiplos_jogos(ultimo.sorteio, quantidade=quantidade, forcado=forcado, repetir=repetir)
            self._json({
                "jogos": [{"numeros": r.get("jogo", []), "qtd_repetir": r.get("qtd_repetir"), "erro": r.get("erro")} for r in resultados]
            })
        elif path == "/api/sincronizar":
            backfill = body.get("backfill", 0)
            relatorio = sincronizar(_db, backfill=backfill)
            self._json(relatorio)
        elif path == "/api/registrar":
            try:
                numero = int(body["numero"])
                data = date.fromisoformat(body["data"])
                numeros = sorted(int(n) for n in body["numeros"])
                from src.validator import numeros_validos
                if not numeros_validos(numeros):
                    self._json({"erro": "15 numeros unicos entre 1 e 25 required"}, 400)
                    return
                if _db.buscar(numero):
                    self._json({"erro": f"Concurso #{numero} ja existe"}, 400)
                    return
                c = Concurso(numero=numero, data=data, sorteio=numeros)
                _db.adicionar(c)
                _tracker.avaliar_contra_sorteio(numero)
                self._json({"numero": numero, "data": str(data), "numeros": numeros})
            except (KeyError, ValueError, TypeError) as e:
                self._json({"erro": str(e)}, 400)
        else:
            self._json({"erro": "rota nao encontrada"}, 404)

    def log_message(self, format, *args):
        sys.stderr.write(f"[SERVER] {args[0]} {args[1]} {args[2]}\n")


def main(port: int = 5000):
    vigia = Vigia(_db, _tracker, intervalo=300)
    vigia.iniciar()

    server = HTTPServer(("0.0.0.0", port), Handler)
    print(f"\n  {'='*50}")
    print(f"  LOTOFACIL - Servidor Web")
    print(f"  {'='*50}")
    print(f"  Acesse: http://localhost:{port}")
    print(f"  Pressione Ctrl+C para parar")
    print(f"  {'='*50}\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  Servidor encerrado.\n")


if __name__ == "__main__":
    import sys
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 5000
    main(port)
