"""Conversa de ponta a ponta em modo teste (sem Meta). Rodar: .venv\\Scripts\\python test_bot.py"""
import os
import tempfile

os.environ.update(DB_PATH=os.path.join(tempfile.mkdtemp(), "t.db"), WA_TOKEN="", APP_SECRET="", PANEL_PASS="teste")
from datetime import date, timedelta

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

# frase livre: entende tudo de uma vez e só pergunta o que falta
H = date.today()
r = app.entender("queria um quarto pra mim e minha esposa de 14/11 a 16/11 com nosso cachorro", date(2026, 11, 5))
assert (r["a"], r["b"], r["g"], r["pet"]) == ("2026-11-14", "2026-11-16", 2, True)
assert app.entender("somos um casal com 2 filhos, dia 20/12 por 3 noites", date(2026, 11, 5)) == {"a": "2026-12-20", "b": "2026-12-23", "g": 4}
assert app.entender("3 pessoas de 1 a 4/12", date(2026, 11, 5))["g"] == 3
manda("menu")
out = manda("quanto custa 3 pessoas de 1 a 4/12?")
assert "Entendi" in out and "3 pessoas" in out and "recepção" not in out
assert "pet" in manda("#casal")                       # id "casal" da lista não vira "um casal"
assert "3 hóspede(s)" in manda("não") and "R$ 690" in app.db().execute("select body from msgs where dir='out' order by id desc").fetchone()[0]  # 180*3 + 50*3
manda("#ok")

# cancelamento: escolhe a reserva, aplica a regra e atualiza o painel
assert "Qual reserva" in manda("quero cancelar minha reserva")
id_690 = app.db().execute("select id from pedidos where total=690").fetchone()[0]
assert "não tem custo" in manda(f"#c{id_690}")     # sinal ainda não pago
assert "cancelada" in manda("sim")
assert app.db().execute("select status, obs from pedidos where id=?", (id_690,)).fetchone()[:] == ("Cancelada", "sem sinal")
p = {"status": "Confirmada", "sinal": 100}
assert app.regra_cancelamento(p | {"a": (H + timedelta(days=10)).isoformat()}, H)[0] == "devolver sinal"
assert app.regra_cancelamento(p | {"a": (H + timedelta(days=3)).isoformat()}, H)[0] == "crédito 6 meses"
assert "continua de pé" in (manda("desisti da reserva") and manda("não"))

# datas: virada de ano e data inválida
assert app.ler_datas("30/12 a 02/01", date(2026, 11, 5)) == (date(2026, 12, 30), date(2027, 1, 2))
assert app.ler_datas("32/11 a 33/11", date(2026, 11, 5)) is None

# verificação do webhook pela Meta
app.VERIFY_TOKEN = "abc"
assert cli.get("/webhook", params={"hub.mode": "subscribe", "hub.verify_token": "abc", "hub.challenge": "42"}).text == "42"
assert cli.get("/webhook", params={"hub.mode": "subscribe", "hub.verify_token": "x", "hub.challenge": "42"}).status_code == 403
print("tudo certo ✅")
