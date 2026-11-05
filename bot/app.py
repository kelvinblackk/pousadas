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
from datetime import date, datetime, timedelta
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
        guests int, pet int, total int, sinal int, status text, ts text, obs text);
    """)
    if "obs" not in [x[1] for x in c.execute("pragma table_info(pedidos)")]:  # banco criado antes do cancelamento
        c.execute("alter table pedidos add column obs text")


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
    ("atendente", ["atendente", "humano", "uma pessoa", "recepção", "recepcao", "falar com"]),
    ("reservar", ["reserv", "disponib", "vaga"]),
    ("precos", ["preço", "preco", "valor", "diária", "diaria", "quanto", "custa"]),
    ("horarios", ["check", "horário", "horario", "café", "cafe"]),
    ("pets", ["pet", "cachorro", "gato", "animal"]),
    ("pagamento", ["pagamento", "pagar", "pix", "cartão", "cartao", "parcel"]),
    ("cancelamento", ["cancel"]),
    ("local", ["endereço", "endereco", "onde", "chegar", "localiza", "estacionamento"]),
]
MENU = [("precos", "Preços e quartos", "Diárias com café incluso"),  # até 10 linhas (limite do WhatsApp)
        ("reservar", "Fazer uma reserva", "Calculo o total na hora"),
        ("cancelar_reserva", "Cancelar uma reserva", None),
        ("horarios", "Check-in e café", None),
        ("pets", "Aceita pets?", None),
        ("pagamento", "Formas de pagamento", None),
        ("cancelamento", "Cancelamento", None),
        ("local", "Como chegar", None),
        ("atendente", "Falar com a recepção", None)]
NUM = {"um": 1, "uma": 1, "dois": 2, "duas": 2, "três": 3, "tres": 3, "quatro": 4, "cinco": 5}


def menu(phone, intro="Como posso ajudar?"):
    lista(phone, intro, "Ver opções", MENU)


def intencao(t):
    t = t.lower()
    for chave, palavras in PALAVRAS:
        if any(p in t for p in palavras):
            return chave
    return None


def _data(d, m, hoje):
    try:
        x = date(hoje.year, m, d)
    except ValueError:  # 31/02 e afins
        return None
    return x.replace(year=hoje.year + 1) if x < hoje else x


def ler_datas(t, hoje):
    a = b = None
    ach = re.findall(r"(\d{1,2})/(\d{1,2})", t)
    curto = re.search(r"(\d{1,2})\s*(?:a|até|ao|e|-)\s*(\d{1,2})/(\d{1,2})", t)  # "14 a 16/11"
    qtd = re.search(r"(\d+)\s*(?:noites?|di[aá]rias?)", t)                      # "14/11 por 2 noites"
    if len(ach) >= 2:
        a, b = _data(int(ach[0][0]), int(ach[0][1]), hoje), _data(int(ach[1][0]), int(ach[1][1]), hoje)
    elif curto:
        a, b = _data(int(curto[1]), int(curto[3]), hoje), _data(int(curto[2]), int(curto[3]), hoje)
    elif len(ach) == 1 and qtd:
        a = _data(int(ach[0][0]), int(ach[0][1]), hoje)
        b = a and a + timedelta(days=int(qtd[1]))
    if not a or not b:
        return None
    if b <= a and b.replace(year=b.year + 1) > a:  # virada de ano, ex.: 30/12 a 02/01
        b = b.replace(year=b.year + 1)
    return (a, b) if (b - a).days >= 1 else None


def entender(t, hoje):
    """Lê da frase livre tudo o que der: datas, pessoas, pet e quarto."""
    low, r = t.lower(), {}
    ds = ler_datas(low, hoje)
    if ds:
        r["a"], r["b"] = ds[0].isoformat(), ds[1].isoformat()
    g, achou = 0, False
    for n, _ in re.findall(r"(\d+|uma?|duas|dois|três|tres|quatro|cinco)\s*(pessoas?|h[oó]spedes?|adultos?|crian[cç]as?|filh[oa]s?)", low):
        g += int(n) if n.isdigit() else NUM[n]
        achou = True
    if re.search(r"\bcasal\b", low) and not re.search(r"quarto casal|standard", low):
        g, achou = g + 2, True
    elif re.search(r"\beu e (minha|meu)\b|minha esposa|meu marido|namorad[ao]", low):
        g, achou = g + 2, True
    elif re.search(r"sozinh[oa]", low) and not achou:
        g, achou = 1, True
    if achou and g > 0:
        r["g"] = g
    if re.search(r"\bsem (pet|cachorro|animal)", low):
        r["pet"] = False
    elif re.search(r"\bpet\b|cachorr|\bc[aã]o\b|cadela|\bgat[oa]\b|animal", low):
        r["pet"] = True
    if re.search(r"varanda|su[ií]te", low):
        r["q"] = "varanda"
    elif re.search(r"quarto fam[ií]lia", low):
        r["q"] = "familia"
    elif re.search(r"standard|quarto casal", low):
        r["q"] = "casal"
    return r


def calcular(quarto, noites, hospedes, pet):
    q = QUARTOS[quarto]
    total = q["preco"] * noites + max(0, hospedes - q["base"]) * EXTRA_HOSPEDE * noites + (TAXA_PET if pet else 0)
    return total, round(total * SINAL)


dm = lambda iso: f"{iso[8:10]}/{iso[5:7]}"
noites_de = lambda d: (date.fromisoformat(d["b"]) - date.fromisoformat(d["a"])).days


def entendi(r):
    p = []
    if "a" in r:
        p.append(f"📅 {dm(r['a'])} a {dm(r['b'])}")
    if "g" in r:
        p.append(f"👥 {r['g']} pessoa{'s' if r['g'] > 1 else ''}")
    if "pet" in r:
        p.append("🐶 com pet" if r["pet"] else "sem pet")
    if "q" in r:
        p.append(f"🛏️ {QUARTOS[r['q']]['nome']}")
    return "Entendi: " + " · ".join(p) if p else ""


def proximo(phone, d):
    """Pergunta só o que ainda falta para fechar a reserva. d['_ask'] guarda a última pergunta."""
    def pergunta(ask):
        d["_ask"] = ask
        salvar(phone, "reserva", d)
    if "a" not in d:
        pergunta("datas")
        return texto(phone, "Quais as datas de entrada e saída? Ex.: 14/11 a 16/11")
    n = noites_de(d)
    if d.get("g", 0) > 5:
        d.pop("g")
        texto(phone, 'Nossos quartos recebem até 5 pessoas. Para grupos maiores, escreva "atendente" que a recepção monta uma opção.')
    if "g" not in d:
        pergunta("hospedes")
        return lista(phone, f"Entrada {dm(d['a'])} e saída {dm(d['b'])}: {n} noite(s). Quantos hóspedes?", "Escolher",
                     [(str(k), f"{k} pessoa{'s' if k > 1 else ''}", None) for k in range(1, 6)])
    if "q" in d and d["g"] > QUARTOS[d["q"]]["max"]:
        texto(phone, f"O {QUARTOS[d['q']]['nome']} recebe até {QUARTOS[d['q']]['max']} pessoas. Veja os que cabem:")
        d.pop("q")
    if "q" not in d:
        pergunta("quarto")
        return lista(phone, f"Para {d['g']} pessoa(s) e {n} noite(s), estes quartos cabem:", "Ver quartos",
                     [(k, q["nome"], f"Total {brl(calcular(k, n, d['g'], False)[0])} · até {q['max']} pessoas")
                      for k, q in QUARTOS.items() if d["g"] <= q["max"]])
    if "pet" not in d:
        pergunta("pet")
        return botoes(phone, "Vai levar pet de pequeno porte?", [("pet_sim", "Sim, vou levar"), ("pet_nao", "Não")])
    d["total"], d["sinal"] = calcular(d["q"], n, d["g"], d["pet"])
    pergunta("confirmar")
    return botoes(phone, f"Resumo do pedido:\n🛏️ {QUARTOS[d['q']]['nome']}\n📅 {dm(d['a'])} a {dm(d['b'])} ({n} noites)\n"
                         f"👥 {d['g']} hóspede(s){' + pet' if d['pet'] else ''}\n💰 Total: {brl(d['total'])}\n"
                         f"Sinal para confirmar (30%): {brl(d['sinal'])}",
                  [("ok", "Confirmar pedido"), ("refazer", "Mudar dados")])


# ---------- cancelamento ----------
def ativos(phone):
    with db() as c:
        return c.execute("select * from pedidos where phone=? and status!='Cancelada' order by id", (phone,)).fetchall()


def regra_cancelamento(p, hoje):
    dias = (date.fromisoformat(p["a"]) - hoje).days
    if p["status"] != "Confirmada":
        return "sem sinal", "Como o sinal ainda não foi pago, o cancelamento não tem custo."
    if dias >= 7:
        return "devolver sinal", f"Faltam {dias} dias para o check-in, então devolvemos o sinal de {brl(p['sinal'])} integralmente."
    return "crédito 6 meses", f"Faltam {dias} dia(s) para o check-in, então o sinal de {brl(p['sinal'])} vira crédito para outra data em até 6 meses."


def confirmar_cancelamento(phone, p, hoje):
    salvar(phone, "cancelar", {"_ask": "confirmar", "cid": p["id"]})
    return botoes(phone, f"Reserva nº {p['id']}: {p['room']}, de {dm(p['a'])} a {dm(p['b'])}.\n{regra_cancelamento(p, hoje)[1]}\nConfirma o cancelamento?",
                  [("cancel_ok", "Sim, cancelar"), ("cancel_nao", "Não, manter")])


def cancelar_inicio(phone, hoje):
    lst = ativos(phone)
    if not lst:
        salvar(phone, "", {})
        return texto(phone, 'Não encontrei nenhuma reserva ativa neste número. Se você reservou por outro canal, escreva "atendente" que a recepção ajuda.')
    if len(lst) == 1:
        return confirmar_cancelamento(phone, lst[0], hoje)
    salvar(phone, "cancelar", {"_ask": "qual"})
    return lista(phone, "Qual reserva você quer cancelar?", "Minhas reservas",
                 [(f"c{p['id']}", f"Nº {p['id']} · {p['room']}"[:24], f"{dm(p['a'])} a {dm(p['b'])} · {brl(p['total'])}") for p in lst])


def cancelar(phone, t, low, d, hoje):
    if d.get("_ask") == "qual":
        p = next((x for x in ativos(phone) if t == f"c{x['id']}" or str(x["id"]) in low), None)
        return confirmar_cancelamento(phone, p, hoje) if p else texto(phone, "Escolha a reserva na lista, por favor.")
    with db() as c:
        p = c.execute("select * from pedidos where id=? and phone=?", (d.get("cid"), phone)).fetchone()
    if not p:
        salvar(phone, "", {})
        return menu(phone)
    if t == "cancel_nao" or re.match(r"^(n[aã]o|manter)", low):
        salvar(phone, "", {})
        return texto(phone, "Combinado, sua reserva continua de pé 🙂")
    if t != "cancel_ok" and not re.match(r"^(sim|pode|cancela)", low):
        return confirmar_cancelamento(phone, p, hoje)
    tipo, _ = regra_cancelamento(p, hoje)
    with db() as c:
        c.execute("update pedidos set status='Cancelada', obs=? where id=?", (tipo, p["id"]))
    salvar(phone, "", {})
    validade = hoje + timedelta(days=182)
    extra = {"devolver sinal": f"\nA recepção faz o Pix de devolução de {brl(p['sinal'])} em até 2 dias úteis.",
             "crédito 6 meses": f"\nSeu crédito de {brl(p['sinal'])} vale até {validade:%d/%m/%Y}. É só pedir uma nova reserva por aqui."}.get(tipo, "")
    return texto(phone, f"Reserva nº {p['id']} cancelada.{extra}\nSe mudar de ideia, estou por aqui!")


def responder(phone, nome, entrada, hoje=None):
    hoje = hoje or date.today()
    c = conv(phone, nome)
    log(phone, "in", entrada)
    if c["human"]:
        return  # recepção atendendo pelo painel
    t = entrada.strip()
    low, estado, d = t.lower(), c["state"] or "", c["data"]

    if low in ("menu", "sair", "voltar", "início", "inicio"):
        salvar(phone, "", {})
        return menu(phone, "Tudo bem, voltei ao início. Como posso ajudar?")
    if t == "cancelar_reserva" or (re.search(r"cancel|desist", low) and re.search(r"reserva|pedido|hospedagem", low)):
        return cancelar_inicio(phone, hoje)
    if estado == "cancelar":
        return cancelar(phone, t, low, d, hoje)

    if estado == "reserva":
        ask = d.get("_ask")
        if ask == "confirmar":
            if t == "refazer" or re.search(r"mudar|trocar|alterar", low):
                return proximo(phone, {})
            if t == "ok" or re.match(r"^(sim|confirm|pode|ok)", low):
                with db() as cx:
                    pid = cx.execute("insert into pedidos(phone,name,room,a,b,guests,pet,total,sinal,status,ts) values(?,?,?,?,?,?,?,?,?,?,?)",
                                     (phone, nome, QUARTOS[d["q"]]["nome"], d["a"], d["b"], d["g"], int(d["pet"]),
                                      d["total"], d["sinal"], "Aguardando sinal", datetime.now().isoformat(timespec="seconds"))).lastrowid
                salvar(phone, "", {})
                return texto(phone, f"Pedido nº {pid} registrado ✅\nPara garantir a data, faça o Pix do sinal de {brl(d['sinal'])}:\n"
                                    f"Chave Pix: {PIX_KEY}\nAssim que a recepção confirmar o pagamento, envio a confirmação por aqui.")
        r = {"q": t} if ask == "quarto" and t in QUARTOS else entender(t, hoje)  # id da lista ("casal") não é "um casal"
        if ask == "hospedes" and "g" not in r and re.fullmatch(r"\s*\d+\s*", t):
            r["g"] = int(t)
        if ask == "quarto" and "q" not in r:
            k = next((k for k, q in QUARTOS.items() if q["nome"].lower() in low), None)
            if k:
                r["q"] = k
        if ask == "pet" and "pet" not in r:
            if t == "pet_sim" or re.match(r"^(sim|s|vou)\b", low):
                r["pet"] = True
            elif t == "pet_nao" or re.match(r"^(n[aã]o|n)\b", low):
                r["pet"] = False
        if r:
            return proximo(phone, d | r)
        if low == "cancelar" or re.search(r"desisti|deixa pra l[aá]", low):
            salvar(phone, "", {})
            return texto(phone, "Tudo bem, deixei a reserva de lado. Se precisar, é só chamar 🙂")
        faq = intencao(t)
        if faq in FAQ:  # responde a dúvida e retoma a reserva
            texto(phone, FAQ[faq])
            return proximo(phone, d)
        if faq != "atendente":
            texto(phone, "Não entendi as datas 😅 Pode mandar assim: 14/11 a 16/11." if ask == "datas" else "Não entendi 😅")
            return proximo(phone, d)
        salvar(phone, "", {})

    r = entender(t, hoje)
    acao = t if any(t == i for i, _, _ in MENU) else intencao(t)
    if r and acao != "atendente":  # já veio com datas, pessoas, pet ou quarto: vai direto para a reserva
        if e := entendi(r):
            texto(phone, e)
        return proximo(phone, r)
    if acao == "cancelamento":
        texto(phone, FAQ["cancelamento"])
        if ativos(phone):
            return botoes(phone, "Quer cancelar uma reserva sua?", [("cancelar_reserva", "Cancelar reserva"), ("menu", "Não, só queria saber")])
        return botoes(phone, "Posso ajudar com mais alguma coisa?", [("reservar", "Fazer uma reserva"), ("menu", "Outras dúvidas")])
    if acao in FAQ:
        texto(phone, FAQ[acao])
        return botoes(phone, "Quer fazer uma reserva?", [("reservar", "Sim, reservar"), ("menu", "Outras dúvidas")])
    if acao == "reservar":
        return proximo(phone, {})
    if acao == "atendente":
        salvar(phone, "", {}, human=1)
        return texto(phone, "Certo! Passei sua conversa para a recepção. Alguém responde por aqui em instantes 🙂")
    with db() as cx:
        primeira = not cx.execute("select 1 from msgs where phone=? and dir='out' limit 1", (phone,)).fetchone()
    intro = (f"Olá{', ' + nome.split()[0] if nome else ''}! 👋 Sou o atendente virtual da {POUSADA}. "
             'Pode escrever do seu jeito, ex.: "quarto pra 2 de 14/11 a 16/11", ou escolher uma opção:' if primeira
             else "Posso ajudar só com assuntos da pousada 🙂 Escolha uma opção ou escreva o que precisa:")
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
.pill{{padding:2px 8px;border-radius:99px;font-size:.8rem;font-weight:700;background:#FDF0D5;color:#8a5a00}}.ok{{background:#DFF3E6;color:#1d6b3e}}.cx{{background:#FBE1DE;color:#A02B1E}}
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
        f"<td>{brl(p['total'])}</td><td>{brl(p['sinal'])}</td><td><span class='pill {'ok' if p['status'] == 'Confirmada' else 'cx' if p['status'] == 'Cancelada' else ''}'>{p['status']}{' · ' + p['obs'] if p['obs'] else ''}</span></td>"
        f"<td>{f'<form method=post action=/painel/sinal/{p['id']}><button>Sinal recebido</button></form>' if p['status'] == 'Aguardando sinal' else ''}</td></tr>"
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
        if not p or p["status"] != "Aguardando sinal":
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
