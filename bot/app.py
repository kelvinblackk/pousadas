"""Robô de atendimento da Pousada Remanso do Rio (demonstração) na WhatsApp Cloud API oficial.

Rodar:  .venv\\Scripts\\uvicorn app:app --port 8000
Sem WA_TOKEN no .env ele roda em modo teste: as respostas só aparecem no terminal e no painel.
O robô fala só de assuntos da pousada (política da Meta para chatbots desde 15/01/2026).
"""
import hashlib
import hmac
import json
import os
import re
import secrets
import sqlite3
from datetime import date, datetime
from html import escape
from pathlib import Path

import httpx
from fastapi import Depends, FastAPI, Form, HTTPException, Request, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials

AQUI = Path(__file__).parent
if (AQUI / ".env").exists():
    for linha in (AQUI / ".env").read_text(encoding="utf-8").splitlines():
        if "=" in linha and not linha.lstrip().startswith("#"):
            k, v = linha.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"'))

TOKEN = os.getenv("WA_TOKEN", "")
PHONE_ID = os.getenv("WA_PHONE_ID", "")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "")
APP_SECRET = os.getenv("APP_SECRET", "")
PANEL_PASS = os.getenv("PANEL_PASS", "")
PIX_KEY = os.getenv("PIX_KEY", "pix-de-teste@remansodorio.exemplo")
GRAPH = os.getenv("GRAPH_VERSION", "v25.0")
DB_PATH = os.getenv("DB_PATH", str(AQUI / "pousada.db"))
DRY = not TOKEN  # modo teste

POUSADA = "Pousada Remanso do Rio"
QUARTOS = {  # mesmos dados da demo do site
    "casal": dict(nome="Standard Casal", preco=180, base=2, max=3),
    "familia": dict(nome="Família", preco=260, base=4, max=5),
    "varanda": dict(nome="Suíte com Varanda", preco=320, base=2, max=3),
}
EXTRA_HOSPEDE, TAXA_PET, SINAL = 50, 30, 0.30


def brl(v):
    return f"R$ {v:,.0f}".replace(",", ".")


# ---------- banco ----------
def db():
    c = sqlite3.connect(DB_PATH)
    c.row_factory = sqlite3.Row
    return c


with db() as c:
    c.executescript("""
    create table if not exists convs(phone text primary key, name text, state text, data text default '{}', human int default 0);
    create table if not exists msgs(id integer primary key, phone text, dir text, body text, ts text);
    create table if not exists pedidos(id integer primary key, phone text, name text, room text, a text, b text,
        guests int, pet int, total int, sinal int, status text, ts text);
    """)


def conv(phone, name=""):
    with db() as c:
        c.execute("insert or ignore into convs(phone, name) values(?, ?)", (phone, name))
        if name:
            c.execute("update convs set name=? where phone=?", (name, phone))
        r = c.execute("select * from convs where phone=?", (phone,)).fetchone()
    return dict(r) | {"data": json.loads(r["data"])}


def salvar(phone, state=None, data=None, human=None):
    with db() as c:
        if state is not None or data is not None:
            c.execute("update convs set state=?, data=? where phone=?", (state or "", json.dumps(data or {}), phone))
        if human is not None:
            c.execute("update convs set human=? where phone=?", (human, phone))


def log(phone, direcao, body):
    with db() as c:
        c.execute("insert into msgs(phone, dir, body, ts) values(?,?,?,?)", (phone, direcao, body, datetime.now().isoformat(timespec="seconds")))


# ---------- envio ----------
def enviar(phone, payload, texto_log):
    log(phone, "out", texto_log)
    if DRY:
        print(f"[modo teste] para {phone}: {texto_log}")
        return
    r = httpx.post(f"https://graph.facebook.com/{GRAPH}/{PHONE_ID}/messages",
                   headers={"Authorization": f"Bearer {TOKEN}"},
                   json={"messaging_product": "whatsapp", "to": phone, **payload}, timeout=15)
    if r.status_code >= 400:
        print("Erro ao enviar:", r.status_code, r.text[:300])


def texto(phone, body):
    enviar(phone, {"type": "text", "text": {"body": body}}, body)


def botoes(phone, body, opcoes):  # até 3 botões, título até 20 caracteres
    enviar(phone, {"type": "interactive", "interactive": {"type": "button", "body": {"text": body}, "action": {
        "buttons": [{"type": "reply", "reply": {"id": i, "title": t}} for i, t in opcoes]}}},
        body + "  [" + " | ".join(t for _, t in opcoes) + "]")


def lista(phone, body, botao, linhas):  # até 10 linhas, título até 24 caracteres
    enviar(phone, {"type": "interactive", "interactive": {"type": "list", "body": {"text": body}, "action": {
        "button": botao, "sections": [{"title": "Opções", "rows": [
            {"id": i, "title": t, **({"description": d} if d else {})} for i, t, d in linhas]}]}}},
        body + "  [" + " | ".join(t + (f" ({d})" if d else "") for _, t, d in linhas) + "]")


# ---------- respostas ----------
FAQ = {
    "precos": "Diárias com café da manhã incluso:\n" + "\n".join(f"• {q['nome']}: {brl(q['preco'])}" for q in QUARTOS.values())
              + f"\nHóspede adicional acima da capacidade base: {brl(EXTRA_HOSPEDE)} por noite.",
    "horarios": "Check-in a partir das 14h e check-out até 12h. Café da manhã das 6h30 às 9h30, incluso na diária.",
    "pets": f"Aceitamos pets de pequeno porte, com taxa de {brl(TAXA_PET)} por estadia. É só avisar na reserva.",
    "pagamento": "Para confirmar a reserva pedimos sinal de 30% via Pix. O restante é pago no check-in, em Pix, débito ou crédito em até 3x.",
    "cancelamento": "Cancelando com 7 dias ou mais de antecedência, devolvemos o sinal. Com menos de 7 dias, o sinal vira crédito para outra data em até 6 meses.",
    "local": "Rua das Palmeiras, 120 · Beira-Rio (endereço ilustrativo). 5 min do centro e 12 min da rodoviária. Estacionamento grátis.",
}
PALAVRAS = [
    ("atendente", ["atendente", "humano", "pessoa", "recepção", "recepcao", "falar com"]),
    ("reservar", ["reserv", "disponib", "vaga"]),
    ("precos", ["preço", "preco", "valor", "diária", "diaria", "quanto"]),
    ("horarios", ["check", "horário", "horario", "café", "cafe"]),
    ("pets", ["pet", "cachorro", "gato", "animal"]),
    ("pagamento", ["pagamento", "pagar", "pix", "cartão", "cartao", "parcel"]),
    ("cancelamento", ["cancel"]),
    ("local", ["endereço", "endereco", "onde", "chegar", "localiza", "estacionamento"]),
]
MENU = [("precos", "Preços e quartos", "Diárias com café incluso"),
        ("reservar", "Fazer uma reserva", "Calculo o total na hora"),
        ("horarios", "Check-in e café", None),
        ("pets", "Aceita pets?", None),
        ("pagamento", "Formas de pagamento", None),
        ("cancelamento", "Cancelamento", None),
        ("local", "Como chegar", None),
        ("atendente", "Falar com a recepção", None)]


def menu(phone, intro="Como posso ajudar?"):
    lista(phone, intro, "Ver opções", MENU)


def intencao(t):
    t = t.lower()
    for chave, palavras in PALAVRAS:
        if any(p in t for p in palavras):
            return chave
    return None


def ler_datas(t, hoje):
    achadas = re.findall(r"(\d{1,2})/(\d{1,2})", t)
    if len(achadas) < 2:
        return None
    ds = []
    for d, m in achadas[:2]:
        try:
            x = date(hoje.year, int(m), int(d))
        except ValueError:
            return None
        if x < hoje:  # data já passou neste ano: é do ano que vem
            x = x.replace(year=hoje.year + 1)
        ds.append(x)
    a, b = ds
    if b <= a and b.replace(year=b.year + 1) > a:  # virada de ano, ex.: 30/12 a 02/01
        b = b.replace(year=b.year + 1)
    return (a, b) if (b - a).days >= 1 else None


def calcular(quarto, noites, hospedes, pet):
    q = QUARTOS[quarto]
    total = q["preco"] * noites + max(0, hospedes - q["base"]) * EXTRA_HOSPEDE * noites + (TAXA_PET if pet else 0)
    return total, round(total * SINAL)


def responder(phone, nome, entrada, hoje=None):
    hoje = hoje or date.today()
    c = conv(phone, nome)
    log(phone, "in", entrada)
    if c["human"]:
        return  # recepção atendendo pelo painel
    t = entrada.strip()
    estado, dados = c["state"] or "", c["data"]

    if t.lower() in ("menu", "sair", "cancelar", "voltar", "início", "inicio"):
        salvar(phone, "", {})
        return menu(phone, "Tudo bem, voltei ao início. Como posso ajudar?")

    if estado == "datas":
        datas = ler_datas(t, hoje)
        if not datas:
            return texto(phone, "Não entendi as datas 😅 Me mande assim: 14/11 a 16/11 (entrada e saída).")
        a, b = datas
        salvar(phone, "hospedes", {"a": a.isoformat(), "b": b.isoformat()})
        return lista(phone, f"Entrada {a:%d/%m} e saída {b:%d/%m}: {(b - a).days} noite(s). Quantos hóspedes?",
                     "Escolher", [(f"h{n}", f"{n} pessoa{'s' if n > 1 else ''}", None) for n in range(1, 6)])

    if estado == "hospedes":
        m = re.search(r"\d", t)
        if not m or not 1 <= int(m.group()) <= 5:
            return texto(phone, "Me diga o número de hóspedes, de 1 a 5.")
        g = int(m.group())
        dados["g"] = g
        noites = (date.fromisoformat(dados["b"]) - date.fromisoformat(dados["a"])).days
        salvar(phone, "quarto", dados)
        linhas = [(k, q["nome"], f"Total {brl(calcular(k, noites, g, False)[0])} · até {q['max']} pessoas")
                  for k, q in QUARTOS.items() if g <= q["max"]]
        return lista(phone, f"Para {g} pessoa(s) e {noites} noite(s), estes quartos cabem:", "Ver quartos", linhas)

    if estado == "quarto":
        k = t if t in QUARTOS else next((k for k, q in QUARTOS.items() if q["nome"].lower() in t.lower()), None)
        if not k or dados["g"] > QUARTOS[k]["max"]:
            return texto(phone, "Escolha um dos quartos da lista, por favor.")
        dados["q"] = k
        salvar(phone, "pet", dados)
        return botoes(phone, "Vai levar pet de pequeno porte?", [("pet_sim", "Sim, vou levar"), ("pet_nao", "Não")])

    if estado == "pet":
        if t not in ("pet_sim", "pet_nao") and not re.match(r"^(sim|s|não|nao|n)\b", t.lower()):
            return botoes(phone, "É só tocar numa opção: vai levar pet?", [("pet_sim", "Sim, vou levar"), ("pet_nao", "Não")])
        dados["pet"] = t == "pet_sim" or t.lower().startswith("s")
        a, b = date.fromisoformat(dados["a"]), date.fromisoformat(dados["b"])
        total, sinal = calcular(dados["q"], (b - a).days, dados["g"], dados["pet"])
        dados |= {"total": total, "sinal": sinal}
        salvar(phone, "confirmar", dados)
        return botoes(phone, f"Resumo do pedido:\n🛏️ {QUARTOS[dados['q']]['nome']}\n📅 {a:%d/%m} a {b:%d/%m} ({(b - a).days} noites)\n"
                             f"👥 {dados['g']} hóspede(s){' + pet' if dados['pet'] else ''}\n💰 Total: {brl(total)}\n"
                             f"Sinal para confirmar (30%): {brl(sinal)}",
                      [("ok", "Confirmar pedido"), ("refazer", "Mudar dados")])

    if estado == "confirmar":
        if t == "refazer":
            salvar(phone, "datas", {})
            return texto(phone, "Sem problema! Me mande de novo as datas: ex. 14/11 a 16/11.")
        if t != "ok" and not t.lower().startswith(("sim", "confirm")):
            return botoes(phone, "Posso registrar o pedido?", [("ok", "Confirmar pedido"), ("refazer", "Mudar dados")])
        with db() as cx:
            pid = cx.execute("insert into pedidos(phone,name,room,a,b,guests,pet,total,sinal,status,ts) values(?,?,?,?,?,?,?,?,?,?,?)",
                             (phone, nome, QUARTOS[dados["q"]]["nome"], dados["a"], dados["b"], dados["g"], int(dados["pet"]),
                              dados["total"], dados["sinal"], "Aguardando sinal", datetime.now().isoformat(timespec="seconds"))).lastrowid
        salvar(phone, "", {})
        return texto(phone, f"Pedido nº {pid} registrado ✅\nPara garantir a data, faça o Pix do sinal de {brl(dados['sinal'])}:\n"
                            f"Chave Pix: {PIX_KEY}\nAssim que a recepção confirmar o pagamento, envio a confirmação por aqui.")

    acao = t if any(t == i for i, _, _ in MENU) else intencao(t)
    if acao in FAQ:
        texto(phone, FAQ[acao])
        return botoes(phone, "Quer fazer uma reserva?", [("reservar", "Sim, reservar"), ("menu", "Outras dúvidas")])
    if acao == "reservar":
        salvar(phone, "datas", {})
        return texto(phone, "Ótimo! Quais as datas de entrada e saída? Ex.: 14/11 a 16/11")
    if acao == "atendente":
        salvar(phone, "", {}, human=1)
        return texto(phone, "Certo! Passei sua conversa para a recepção. Alguém responde por aqui em instantes 🙂")
    with db() as cx:
        primeira = not cx.execute("select 1 from msgs where phone=? and dir='out' limit 1", (phone,)).fetchone()
    intro = (f"Olá{', ' + nome.split()[0] if nome else ''}! 👋 Sou o atendente virtual da {POUSADA}." if primeira
             else "Posso ajudar só com assuntos da pousada 🙂 Escolha uma opção:")
    return menu(phone, intro)


# ---------- web ----------
app = FastAPI(title="Robô da pousada")
basic = HTTPBasic()


def dono(cred: HTTPBasicCredentials = Depends(basic)):
    if not PANEL_PASS or not secrets.compare_digest(cred.password.encode(), PANEL_PASS.encode()):
        raise HTTPException(401, headers={"WWW-Authenticate": "Basic"})


@app.get("/webhook")
def verificar(request: Request):
    q = request.query_params
    if q.get("hub.mode") == "subscribe" and VERIFY_TOKEN and q.get("hub.verify_token") == VERIFY_TOKEN:
        return Response(q.get("hub.challenge", ""), media_type="text/plain")
    raise HTTPException(403)


@app.post("/webhook")
async def receber(request: Request):
    corpo = await request.body()
    if APP_SECRET:  # confere que a mensagem veio mesmo da Meta
        esperado = "sha256=" + hmac.new(APP_SECRET.encode(), corpo, hashlib.sha256).hexdigest()
        if not hmac.compare_digest(esperado, request.headers.get("X-Hub-Signature-256", "")):
            raise HTTPException(403)
    elif not DRY:
        raise HTTPException(500, "APP_SECRET faltando no .env")
    dados = json.loads(corpo)
    for entry in dados.get("entry", []):
        for ch in entry.get("changes", []):
            v = ch.get("value", {})
            for s in v.get("statuses", []):  # entregue, lida ou falhou (com o código do erro)
                erro = "; ".join(f"{e.get('code')} {e.get('title')}" for e in s.get("errors", []))
                print(f"[status] {s.get('recipient_id')}: {s.get('status')} {erro}")
                if erro:
                    log(s.get("recipient_id", "?"), "out", f"⚠️ falha na entrega: {erro}")
            nomes = {c["wa_id"]: c.get("profile", {}).get("name", "") for c in v.get("contacts", [])}
            for m in v.get("messages", []):
                if m["type"] == "text":
                    t = m["text"]["body"]
                elif m["type"] == "interactive":
                    i = m["interactive"]
                    t = (i.get("button_reply") or i.get("list_reply") or {}).get("id", "")
                    if t.startswith("h") and t[1:].isdigit():
                        t = t[1:]
                else:
                    t = "?"  # áudio, foto etc.: cai no menu
                responder(m["from"], nomes.get(m["from"], ""), t)
    return {"ok": True}


PAINEL = """<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Painel · {pousada}</title><meta http-equiv="refresh" content="20">
<style>body{{font:15px system-ui,sans-serif;margin:0;background:#F3F6F1;color:#14231B}}main{{max-width:960px;margin:auto;padding:16px}}
h1{{font-size:1.3rem}}h2{{font-size:1.05rem;margin-top:28px}}table{{width:100%;border-collapse:collapse;background:#fff;border-radius:10px;overflow:hidden}}
td,th{{padding:8px;border-bottom:1px solid #DCE4DD;text-align:left;vertical-align:top}}th{{font-size:.75rem;text-transform:uppercase;color:#5A6B61}}
.pill{{padding:2px 8px;border-radius:99px;font-size:.8rem;font-weight:700;background:#FDF0D5;color:#8a5a00}}.ok{{background:#DFF3E6;color:#1d6b3e}}
button{{border:0;border-radius:8px;padding:6px 10px;font-weight:700;background:#1D3B2C;color:#fff;cursor:pointer}}
.box{{background:#fff;border:1px solid #DCE4DD;border-radius:10px;padding:12px;margin-top:10px}}.msg{{margin:4px 0}}.in{{color:#14231B}}.out{{color:#2C5641}}
input[type=text]{{width:70%;padding:7px;border:1px solid #ccc;border-radius:8px}}.tag{{font-size:.8rem;color:#5A6B61}}</style></head>
<body><main><h1>{pousada} · Painel do dono</h1><p class="tag">{modo} · atualiza sozinho a cada 20 s</p>
<h2>Pedidos de reserva</h2><table><tr><th>Nº</th><th>Hóspede</th><th>Quarto</th><th>Período</th><th>Total</th><th>Sinal</th><th>Status</th><th></th></tr>{pedidos}</table>
<h2>Conversas com a recepção</h2>{humanos}
<h2>Últimas mensagens</h2><div class="box">{ultimas}</div></main></body></html>"""


@app.get("/painel", response_class=HTMLResponse, dependencies=[Depends(dono)])
def painel():
    with db() as c:
        ps = c.execute("select * from pedidos order by id desc limit 50").fetchall()
        hs = c.execute("select * from convs where human=1").fetchall()
        ms = c.execute("select * from msgs order by id desc limit 30").fetchall()
    fmt = lambda s: f"{s[8:10]}/{s[5:7]}"
    pedidos = "".join(
        f"<tr><td>{p['id']}</td><td>{escape(p['name'] or p['phone'])}</td><td>{escape(p['room'])}</td><td>{fmt(p['a'])} a {fmt(p['b'])}</td>"
        f"<td>{brl(p['total'])}</td><td>{brl(p['sinal'])}</td><td><span class='pill {'ok' if p['status'] == 'Confirmada' else ''}'>{p['status']}</span></td>"
        f"<td>{'' if p['status'] == 'Confirmada' else f'<form method=post action=/painel/sinal/{p['id']}><button>Sinal recebido</button></form>'}</td></tr>"
        for p in ps) or "<tr><td colspan=8>Nenhum pedido ainda.</td></tr>"
    humanos = "".join(
        f"<div class='box'><b>{escape(h['name'] or h['phone'])}</b> pediu atendimento."
        f"<form method=post action=/painel/responder/{h['phone']}><input type=text name=msg placeholder='Sua resposta' required> <button>Enviar</button></form>"
        f"<form method=post action=/painel/robo/{h['phone']}><button style='background:#5A6B61;margin-top:6px'>Devolver ao robô</button></form></div>"
        for h in hs) or "<p class='tag'>Ninguém aguardando a recepção.</p>"
    ultimas = "".join(f"<div class='msg {m['dir']}'>{'⬅️' if m['dir'] == 'in' else '➡️'} <b>{m['phone'][-4:]}</b>: {escape(m['body'])}</div>" for m in ms)
    modo = "MODO TESTE (sem WhatsApp conectado)" if DRY else "Conectado à WhatsApp Cloud API"
    return PAINEL.format(pousada=POUSADA, modo=modo, pedidos=pedidos, humanos=humanos, ultimas=ultimas or "Sem mensagens.")


@app.post("/painel/sinal/{pid}", dependencies=[Depends(dono)])
def sinal(pid: int):
    with db() as c:
        p = c.execute("select * from pedidos where id=?", (pid,)).fetchone()
        if not p:
            raise HTTPException(404)
        c.execute("update pedidos set status='Confirmada' where id=?", (pid,))
    texto(p["phone"], f"Sinal recebido! 🎉 Sua reserva nº {pid} está confirmada: {p['room']}, de {p['a'][8:10]}/{p['a'][5:7]} a {p['b'][8:10]}/{p['b'][5:7]}.\n"
                      "Check-in a partir das 14h. Um dia antes eu te mando a localização. Até breve!")
    return RedirectResponse("/painel", 303)


@app.post("/painel/responder/{phone}", dependencies=[Depends(dono)])
def responder_humano(phone: str, msg: str = Form(...)):
    texto(phone, msg)
    return RedirectResponse("/painel", 303)


@app.post("/painel/robo/{phone}", dependencies=[Depends(dono)])
def devolver(phone: str):
    salvar(phone, human=0)
    texto(phone, "Voltei! Sou o atendente virtual. Se precisar de algo, é só escrever 🙂")
    return RedirectResponse("/painel", 303)
