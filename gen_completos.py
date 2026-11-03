"""Gera sites completos (simulador, chat, painel) a partir da demo.

A demo/index.html é o molde: qualquer melhoria nela vale para todos ao rodar `python gen_completos.py`.
Cada troca confere se o trecho existe, para o script falhar alto se a demo mudar.
"""
import os
import re

MOLDE = open("demo/index.html", encoding="utf-8").read()

SITES = [
    dict(
        slug="chapada", nome="Pousada Vale das Águas", curto="Vale das Águas",
        fonte=("Plus+Jakarta+Sans:wght@500;700;800", '"Plus Jakarta Sans"'),
        claro=dict(bg="#F1F6F7", ink="#10222A", muted="#55707A", line="#D7E4E8", forest="#163A4A", forest2="#22566B", sun="#F2A541", sunink="#3A2405"),
        escuro=dict(bg="#0D171B", surface="#142229", ink="#E6EFF2", muted="#9BB2BA", line="#24363E", forest="#0F2731", forest2="#1C4556", sun="#F5B35C", sunink="#2A1A03"),
        rgb="14,38,48",
        hero_alt="Chalés de pedra e madeira no cerrado com cachoeira e paredões de arenito ao fundo, fim de tarde",
        kicker="Pousada na chapada · 8 chalés",
        h1="Cachoeiras a 10 minutos da sua varanda",
        lead="Chalés de pedra no meio do cerrado, café da roça incluso e trilhas com guia. Reserve em menos de 2 minutos.",
        facts='<span><b>Check-in</b> a partir das 14h</span><span><b>Café</b> 7h às 10h</span><span><b>Trilhas</b> com guia local</span><span><b>Estacionamento</b> grátis</span>',
        quartos=[
            ("casal", "Chalé Casal", 280, 2, 3, "22 m²", ["Cama queen", "Parede de pedra", "Vista do cerrado"], "Chalé casal com cama queen, parede de pedra e janela para o cerrado"),
            ("familia", "Chalé Família", 390, 4, 5, "32 m²", ["Casal + 2 solteiros", "Varanda", "Ventilador de teto"], "Chalé família com cama de casal, duas camas de solteiro e varanda para o cerrado"),
            ("varanda", "Chalé Mirante", 450, 2, 3, "28 m²", ["Vista do cânion", "Hidromassagem externa", "Varanda"], "Chalé mirante com hidromassagem na varanda e vista do cânion ao pôr do sol"),
        ],
        cafe=("Café da roça", "Pão de queijo, frutas do cerrado, bolo de milho"),
        atracao=("Cachoeiras", "Três quedas a até 10 min de trilha"),
        endereco="Estrada do Mirante, km 4 · Vale das Águas",
        perto=[("Centro da vila", "8 min de carro"), ("Rodoviária", "15 min de carro"), ("Cachoeira do Poço Azul", "10 min de trilha"), ("Mirante do Cânion", "20 min de carro")],
        mapa="Cânion",
    ),
    dict(
        slug="fazenda", nome="Pousada Sítio dos Ipês", curto="Sítio dos Ipês",
        fonte=("Fraunces:opsz,wght@9..144,600;9..144,700;9..144,800", '"Fraunces"'),
        claro=dict(bg="#F8F3EA", ink="#2A1C14", muted="#6E5B4E", line="#E8DCCB", forest="#3B2418", forest2="#6B3F28", sun="#E8B04A", sunink="#3A2604"),
        escuro=dict(bg="#17110D", surface="#211912", ink="#F1E9E1", muted="#B3A396", line="#382A20", forest="#2A1A11", forest2="#55321F", sun="#EDBB5C", sunink="#2A1B02"),
        rgb="44,26,17",
        hero_alt="Casarão de fazenda branco com janelas azuis, ipês amarelos floridos, cavalos e lago",
        kicker="Pousada rural · 8 quartos",
        h1="Café da roça, cavalos e silêncio de fazenda",
        lead="Casarão restaurado entre ipês, com lago, cavalgada e comida feita no fogão a lenha. Reserve em menos de 2 minutos.",
        facts='<span><b>Check-in</b> a partir das 14h</span><span><b>Café</b> 7h às 10h</span><span><b>Cavalgada</b> inclusa</span><span><b>Estacionamento</b> grátis</span>',
        quartos=[
            ("casal", "Quarto Casal", 220, 2, 3, "20 m²", ["Cama de ferro", "Ladrilho hidráulico", "Vista do jardim"], "Quarto casal com cama de ferro antiga, colcha de crochê e janela azul para o jardim"),
            ("familia", "Quarto Família", 320, 4, 5, "30 m²", ["Casal + 2 solteiros", "Pé-direito alto", "Vista do pasto"], "Quarto família com cama de casal, duas camas de solteiro e janelas para o pasto"),
            ("varanda", "Suíte do Lago", 380, 2, 3, "26 m²", ["Varanda para o lago", "Banheira", "Cadeiras de balanço"], "Suíte com banheira e varanda com cadeiras de balanço de frente para o lago"),
        ],
        cafe=("Café da roça", "Queijo da casa, pão caseiro, fogão a lenha"),
        atracao=("Lago e cavalos", "Cavalgada, pesca e passeio de caiaque"),
        endereco="Estrada Vicinal dos Ipês, km 6 · Zona Rural",
        perto=[("Centro da cidade", "15 min de carro"), ("Rodoviária", "20 min de carro"), ("Aeroporto", "35 min de carro"), ("Cachoeira mais próxima", "25 min de carro")],
        mapa="Lago",
    ),
]


def troca(t, velho, novo, todas=False):
    assert velho in t, f"trecho não encontrado no molde: {velho[:60]!r}"
    return t.replace(velho, novo) if todas else t.replace(velho, novo, 1)


def build(s):
    t = MOLDE
    c, e = s["claro"], s["escuro"]
    q = {k: (n, p, b, m, sz, tags, alt) for k, n, p, b, m, sz, tags, alt in s["quartos"]}
    nc, nf, nv = q["casal"][0], q["familia"][0], q["varanda"][0]

    # identidade
    t = troca(t, "Remanso do Rio", s["curto"], todas=True)
    t = troca(t, "Atendimento Remanso", f"Atendimento {s['curto']}")
    t = troca(t, "<title>Pousada " + s["curto"], "<title>" + s["nome"])
    t = troca(t, "Pousada " + s["curto"] + ".", s["nome"] + ".")  # mensagem do WhatsApp
    t = troca(t, "family=Bricolage+Grotesque:opsz,wght@12..96,500;12..96,700;12..96,800", "family=" + s["fonte"][0])
    t = troca(t, '--font-display:"Bricolage Grotesque"', "--font-display:" + s["fonte"][1])
    t = troca(t, "--bg:#F3F6F1;", f"--bg:{c['bg']};")
    t = troca(t, "--ink:#14231B;", f"--ink:{c['ink']};")
    t = troca(t, "--muted:#5A6B61;", f"--muted:{c['muted']};")
    t = troca(t, "--line:#DCE4DD;", f"--line:{c['line']};")
    t = troca(t, "--forest:#1D3B2C;", f"--forest:{c['forest']};")
    t = troca(t, "--forest-2:#2C5641;", f"--forest-2:{c['forest2']};")
    t = troca(t, "--sun:#E3A51C;", f"--sun:{c['sun']};")
    t = troca(t, "--sun-ink:#3A2A05;", f"--sun-ink:{c['sunink']};")
    escuro = (f"--bg:{e['bg']}; --surface:{e['surface']}; --ink:{e['ink']}; --muted:{e['muted']}; --line:{e['line']};\n"
              f"    --forest:{e['forest']}; --forest-2:{e['forest2']}; --sun:{e['sun']}; --sun-ink:{e['sunink']};")
    t = troca(t, "--bg:#0F1913; --surface:#17241C; --ink:#E7EEE9; --muted:#9DB0A4; --line:#2A3A30;\n    --forest:#12261B; --forest-2:#1F3D2D; --sun:#F0B53A; --sun-ink:#2A1E02;", escuro)
    t = troca(t, "--bg:#0F1913; --surface:#17241C; --ink:#E7EEE9; --muted:#9DB0A4; --line:#2A3A30;\n  --forest:#12261B; --forest-2:#1F3D2D; --sun:#F0B53A; --sun-ink:#2A1E02;", escuro.replace("\n    ", "\n  "))
    t = troca(t, "rgba(16,36,26,", f"rgba({s['rgb']},", todas=True)

    # topo
    t = troca(t, "../img/demo/", f"../img/{s['slug']}/", todas=True)
    t = troca(t, 'alt="Pousada de madeira e telhado de telha à beira do rio ao pôr do sol, com deck e redes"', f'alt="{s["hero_alt"]}"')
    t = troca(t, "Pousada à beira-rio · 8 quartos", s["kicker"])
    t = troca(t, "Descanso de verdade, a poucos minutos do centro", s["h1"])
    t = troca(t, "Quartos climatizados, café regional incluso e atendimento rápido pelo WhatsApp. Reserve em menos de 2 minutos.", s["lead"])
    t = re.sub(r'(<div class="hero-facts">).*?(</div>)', lambda m: m.group(1) + s["facts"] + m.group(2), t, count=1)

    # quartos (dados do JS)
    rooms = ",\n".join(
        f'  {{id:"{k}",name:"{n}",price:{p},base:{b},max:{m},size:"{sz}",tags:{tags!r},alt:"{alt}"}}'.replace("'", '"')
        for k, (n, p, b, m, sz, tags, alt) in q.items())
    t, n = re.subn(r"const ROOMS=\[\n.*?\n\];", lambda _: "const ROOMS=[\n" + rooms + "\n];", t, count=1, flags=re.S)
    assert n == 1
    t = troca(t, "Escolha o quarto Família", f"Escolha o {nf}")
    t = troca(t, '{guest:"Mariana L.",room:"Suíte com Varanda"', f'{{guest:"Mariana L.",room:"{nv}"')
    t = troca(t, 'room:"Família",a:"2026-11-07"', f'room:"{nf}",a:"2026-11-07"')
    t = troca(t, 'room:"Standard Casal",a:"2026-11-12"', f'room:"{nc}",a:"2026-11-12"')
    t = troca(t, 'room:"Standard Casal",a:"2026-11-14"', f'room:"{nc}",a:"2026-11-14"')
    t = troca(t, 'room:"Suíte com Varanda",a:"2026-11-20"', f'room:"{nv}",a:"2026-11-20"')
    t = troca(t, 'room:"Família",a:"2026-11-27"', f'room:"{nf}",a:"2026-11-27"')
    precos = "\\n".join(f"• {n}: R$ {p}" for n, p, *_ in q.values())
    t = troca(t, "• Standard Casal: R$ 180\\n• Família (até 5): R$ 260\\n• Suíte com Varanda: R$ 320", precos)
    fam = q["familia"]
    t = troca(t, "O quarto Família tem 28 m², cama de casal e 2 de solteiro, para até 5 pessoas. Diária de R$ 260 para 4 pessoas, +R$ 50 para a 5ª.",
              f"O {fam[0]} tem {fam[4]}, cama de casal e 2 de solteiro, para até 5 pessoas. Diária de R$ {fam[1]} para 4 pessoas, +R$ 50 para a 5ª.")
    t = troca(t, '"Quarto Família","Ver preços"', f'"{fam[0]}","Ver preços"')

    # comodidades, café e local
    t = troca(t, "<b>Café regional</b><span>Tapioca, frutas da estação, bolo caseiro</span>", f"<b>{s['cafe'][0]}</b><span>{s['cafe'][1]}</span>")
    t = troca(t, "<b>Deck no rio</b><span>Redes, pôr do sol e banho de rio</span>", f"<b>{s['atracao'][0]}</b><span>{s['atracao'][1]}</span>")
    t = troca(t, "O café regional é servido das 6h30 às 9h30 e está incluso na diária: tapioca, frutas, bolo caseiro, ovos e sucos.",
              f"O café da roça é servido das 7h às 10h e está incluso na diária: {s['cafe'][1].lower()}, ovos e sucos.")
    t = troca(t, "Rua das Palmeiras, 120 · Bairro Beira-Rio", s["endereco"])
    t = troca(t, "Ficamos na Rua das Palmeiras, 120, Beira-Rio. São 5 min do centro e 12 min da rodoviária.",
              f"Ficamos na {s['endereco'].replace(' · ', ', ')}. São {s['perto'][0][1].replace(' de carro', '')} do centro e {s['perto'][1][1].replace(' de carro', '')} da rodoviária.")
    li = "\n".join(f'        <li><span>{a}</span><span class="num">{b}</span></li>' for a, b in s["perto"])
    t, n = re.subn(r"(<ul>\n)(\s*<li><span>Centro da cidade.*?)(\n\s*</ul>)", lambda m: m.group(1) + li + m.group(3), t, count=1, flags=re.S)
    assert n == 1
    t = troca(t, '<text x="40" y="270">Rio</text>', f'<text x="40" y="270">{s["mapa"]}</text>')
    return t


for s in SITES:
    os.makedirs(s["slug"], exist_ok=True)
    open(f"{s['slug']}/index.html", "w", encoding="utf-8").write(build(s))
print("ok")
