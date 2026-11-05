"""Conversa de ponta a ponta em modo teste (sem Meta). Rodar: .venv\\Scripts\\python test_bot.py"""
import os
import tempfile

os.environ.update(DB_PATH=os.path.join(tempfile.mkdtemp(), "t.db"), WA_TOKEN="", APP_SECRET="", PANEL_PASS="teste")
from datetime import date

from fastapi.testclient import TestClient

import app

cli = TestClient(app.app)
FONE = "5595900000000"


def manda(corpo):
    msg = {"from": FONE, "type": "text", "text": {"body": corpo}} if not corpo.startswith("#") else \
        {"from": FONE, "type": "interactive", "interactive": {"list_reply": {"id": corpo[1:]}}}
    with app.db() as c:
        antes = c.execute("select coalesce(max(id), 0) from msgs").fetchone()[0]
    r = cli.post("/webhook", json={"entry": [{"changes": [{"value": {"contacts": [{"wa_id": FONE, "profile": {"name": "Ana Souza"}}], "messages": [msg]}}]}]})
    assert r.status_code == 200
    with app.db() as c:  # todas as respostas do robô a esta mensagem
        return "\n".join(x[0] for x in c.execute("select body from msgs where id>? and dir='out' order by id", (antes,)))


assert "Olá, Ana" in manda("oi")
assert "Standard Casal: R$ 180" in manda("quanto custa a diária?")
assert "datas" in manda("#reservar")
assert "Não entendi" in manda("semana que vem")
assert "Quantos hóspedes" in manda("14/11 a 16/11")
assert "Total R$ 360" in manda("#h2")                 # casal, 2 noites
assert "pet" in manda("#casal")
resumo = manda("sim")
assert "Total: R$ 390" in resumo and "R$ 117" in resumo  # 360 + pet 30; sinal 30%
assert "Chave Pix" in manda("#ok")
with app.db() as c:
    p = c.execute("select * from pedidos").fetchone()
assert (p["total"], p["sinal"], p["status"]) == (390, 117, "Aguardando sinal")

# painel exige senha e confirma o sinal
assert cli.get("/painel").status_code == 401
assert cli.get("/painel", auth=("dono", "teste")).status_code == 200
cli.post(f"/painel/sinal/{p['id']}", auth=("dono", "teste"))
assert "Sinal recebido" in app.db().execute("select body from msgs where dir='out' order by id desc").fetchone()[0]

# família com 5 pessoas: só o quarto Família aparece; hóspede extra cobra R$ 50/noite
manda("#reservar"); manda("01/12 a 04/12")
op = manda("#h5")
assert "Família" in op and "Standard" not in op and "Total R$ 930" in op  # 260*3 + 1*50*3

# pedir atendente silencia o robô até devolver pelo painel
manda("menu")
assert "recepção" in manda("quero falar com atendente")
antes = app.db().execute("select count(*) from msgs where dir='out'").fetchone()[0]
manda("oi?")
assert app.db().execute("select count(*) from msgs where dir='out'").fetchone()[0] == antes
cli.post(f"/painel/robo/{FONE}", auth=("dono", "teste"))
assert "Voltei" in app.db().execute("select body from msgs where dir='out' order by id desc").fetchone()[0]

# datas: virada de ano e data inválida
assert app.ler_datas("30/12 a 02/01", date(2026, 11, 5)) == (date(2026, 12, 30), date(2027, 1, 2))
assert app.ler_datas("32/11 a 33/11", date(2026, 11, 5)) is None

# verificação do webhook pela Meta
app.VERIFY_TOKEN = "abc"
assert cli.get("/webhook", params={"hub.mode": "subscribe", "hub.verify_token": "abc", "hub.challenge": "42"}).text == "42"
assert cli.get("/webhook", params={"hub.mode": "subscribe", "hub.verify_token": "x", "hub.challenge": "42"}).status_code == 403
print("tudo certo ✅")
