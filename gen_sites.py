SITES = [
  dict(slug="serra", hero_alt="Chalés de madeira entre araucárias com montanhas e névoa ao fundo", gal=['Café colonial servido na varanda com vista das araucárias', 'Trilha de terra entre araucárias numa manhã de névoa', 'Lareira acesa com poltronas e manta no chalé', 'Vale verde da serra com névoa ao amanhecer'],
       file="serra/index.html", title="Pousada Cantinho da Serra",
       short="Cantinho da Serra", tagline="Clima de montanha, lareira e café colonial",
       kicker="Pousada na serra · 6 chalés",
       about="Seis chalés de madeira entre araucárias, com lareira, café colonial servido na varanda e trilhas que começam no nosso portão. Ideal para casais que querem desacelerar no fim de semana.",
       display="Fraunces", body="Nunito Sans", layout="split",
       c=dict(bg="#F6F1EA", surface="#FFFFFF", ink="#2B1E16", muted="#6E5D50", line="#E6DACB", accent="#B5562B", accentink="#FFFFFF",
              sky="#DCE6E4", sun="#F2B655", far="#9DB3AE", mid="#5F7F74", near="#304A40", roof="#5A3A27", wall="#E9D6BC",
              roomwall="#EFE3D2", floor="#8A6146", sand="#D9C3A3", water="#7BA6B5", wall2="#E9D6BC", wall3="#E9D6BC"),
       rooms=[("Chalé Casal", 290, "Lareira, hidromassagem, varanda com vista"), ("Chalé Família", 380, "Mezanino, 2 camas extras, cozinha compacta"), ("Chalé Vista Vale", 340, "Janela panorâmica, banheira, rede")],
       amen=["Café colonial", "Lareira nos chalés", "Trilhas guiadas", "Wi-Fi", "Estacionamento", "Pet friendly"],
       where="Estrada da Serra, km 8 · 15 min do centro (endereço ilustrativo)"),
  dict(slug="mar", hero_alt="Pousada de casas brancas com coqueiros diante de mar turquesa", gal=['Piscina cercada de coqueiros e espreguiçadeiras', 'Café da manhã tropical com frutas e tapioca de frente para o mar', 'Guarda-sóis de palha e cadeiras na areia', 'Jangada de vela branca na areia da praia'],
       file="mar/index.html", title="Pousada Maré Mansa",
       short="Maré Mansa", tagline="Pé na areia, rede na varanda e mar calmo",
       kicker="Pousada pé na areia · 10 quartos",
       about="A 30 passos do mar, com piscina, café da manhã com frutas tropicais e quartos arejados. Praia de águas calmas, perfeita para famílias com crianças.",
       display="Baloo 2", body="Mulish", layout="center",
       c=dict(bg="#F2F8FA", surface="#FFFFFF", ink="#0E2A3A", muted="#4E6C7C", line="#D6E7EE", accent="#0E8FB0", accentink="#FFFFFF",
              sky="#9FD9EA", sun="#FFC94A", far="#62B7CF", mid="#1E9BBF", near="#2D5B3E", roof="#E0703A", wall="#FFFFFF",
              roomwall="#EAF5F8", floor="#E8D4AE", sand="#F1DFB8", water="#1E9BBF", wall2="#fff", wall3="#fff"),
       rooms=[("Quarto Brisa", 240, "Casal, varanda com rede, ar-condicionado"), ("Quarto Família", 330, "Até 4 pessoas, frigobar, vista lateral do mar"), ("Suíte Frente Mar", 420, "Varanda privativa de frente para o mar")],
       amen=["Piscina", "Café tropical", "Guarda-sol e cadeiras", "Wi-Fi", "Estacionamento", "Passeios de barco"],
       where="Av. Beira-Mar, 900 · Praia Mansa (endereço ilustrativo)"),
  dict(slug="colonial", hero_alt="Fachada do casarão colonial amarelo em rua de pedra com igreja barroca ao fundo", gal=['Mesa de café no pátio interno sob a jabuticabeira', 'Rua de pedra com casarões coloridos e igreja barroca', 'Corredor interno com piso de madeira original e janelas em arco', 'Bicicletas encostadas em casarão colorido'],
       file="colonial/index.html", title="Pousada Casarão Colonial",
       short="Casarão Colonial", tagline="Um casarão de 1890 no coração do centro histórico",
       kicker="Centro histórico · 7 suítes",
       about="Casarão restaurado com pé-direito alto, piso de madeira original e pátio interno com jabuticabeiras. Caminhe até igrejas, museus e restaurantes sem precisar de carro.",
       display="Playfair Display", body="Source Sans 3", layout="split",
       c=dict(bg="#F7F3EE", surface="#FFFFFF", ink="#2A1A1F", muted="#6B5A5F", line="#E8DDD6", accent="#7D2335", accentink="#FFFFFF",
              sky="#E9E4DA", sun="#E7B24A", far="#C9BBA9", mid="#8A7B6A", near="#3B5A73", roof="#8C3B2A", wall="#F3E3B5",
              wall2="#CDE0D9", wall3="#F2C9B8", roomwall="#F1E8DD", floor="#7A5235", sand="#BBA990", water="#8FB1C4"),
       rooms=[("Suíte Clássica", 260, "Cama king, móveis de época, banheiro reformado"), ("Suíte Sacada", 320, "Sacada para a rua de pedra, pé-direito de 5 m"), ("Suíte Pátio", 300, "Acesso direto ao pátio interno")],
       amen=["Café no pátio", "Roteiro histórico", "Wi-Fi", "Ar-condicionado", "Bicicletas", "Recepção 24h"],
       where="Rua do Rosário, 45 · Centro Histórico (endereço ilustrativo)"),
  dict(slug="mata", hero_alt="Bangalôs de madeira sobre palafitas à beira do igarapé na floresta", gal=['Banho de igarapé com prainha de areia branca', 'Canoa de madeira no igarapé entre a mata', 'Peixe assado na folha, açaí e farinha: culinária regional', 'Passarela de madeira suspensa entre árvores gigantes'],
       file="mata/index.html", title="Pousada Recanto da Mata",
       short="Recanto da Mata", tagline="Bangalôs na floresta, à beira do igarapé",
       kicker="Ecopousada · 5 bangalôs",
       about="Bangalôs suspensos no meio da mata, com banho de igarapé, trilhas com guia local e culinária regional. Energia solar e coleta de água da chuva.",
       display="Outfit", body="Lato", layout="center",
       c=dict(bg="#F1F5EE", surface="#FFFFFF", ink="#16261A", muted="#56685A", line="#DAE4D6", accent="#3E7D32", accentink="#FFFFFF",
              sky="#CFE3C9", sun="#F4C35A", far="#4E8A4A", mid="#2F6B35", near="#1F4A26", roof="#6B4423", wall="#E5D3B3",
              roomwall="#EAF0E3", floor="#7B5530", sand="#C7B48E", water="#6E5A3A", wall2="#E5D3B3", wall3="#E5D3B3"),
       rooms=[("Bangalô Casal", 350, "Varanda com rede, mosquiteiro, ventilador de teto"), ("Bangalô Família", 460, "Até 4 pessoas, 2 ambientes"), ("Bangalô Igarapé", 420, "Deck privativo sobre a água")],
       amen=["Pensão completa", "Trilhas com guia", "Banho de igarapé", "Energia solar", "Passeio de canoa", "Observação de aves"],
       where="Ramal do Igarapé, km 3 · acesso por estrada de terra (endereço ilustrativo)"),
]

LIGHTBOX = """<dialog class="lb" aria-label="Foto em tela cheia">
<img alt=""><p></p>
<button class="x" aria-label="Fechar">×</button><button class="pv" aria-label="Foto anterior">‹</button><button class="nx" aria-label="Próxima foto">›</button>
</dialog>
<script>
(() => {
  const d = document.querySelector(".lb"), img = d.querySelector("img"), cap = d.querySelector("p");
  const links = [...document.querySelectorAll(".gal a")];
  let i = 0, x0 = null;
  const show = n => { i = (n + links.length) % links.length; const a = links[i].querySelector("img");
    img.src = links[i].href; img.alt = a.alt; cap.textContent = a.alt + " · " + (i + 1) + "/" + links.length; };
  links.forEach((a, n) => a.addEventListener("click", e => { e.preventDefault(); show(n); d.showModal(); }));
  d.querySelector(".x").onclick = () => d.close();
  d.querySelector(".pv").onclick = () => show(i - 1);
  d.querySelector(".nx").onclick = () => show(i + 1);
  d.addEventListener("click", e => { if (e.target === d) d.close(); });
  d.addEventListener("keydown", e => { if (e.key === "ArrowLeft") show(i - 1); if (e.key === "ArrowRight") show(i + 1); });
  d.addEventListener("touchstart", e => { x0 = e.touches[0].clientX; }, { passive: true });
  d.addEventListener("touchend", e => { if (x0 === null) return; const dx = e.changedTouches[0].clientX - x0;
    if (Math.abs(dx) > 50) show(i + (dx < 0 ? 1 : -1)); x0 = null; });
})();
</script>"""

def brl(v): return f"R$ {v}"

def build(s):
    c = s["c"]
    font_q = "&".join(f"family={f.replace(' ', '+')}:wght@400;600;700" for f in (s["display"], s["body"]))
    rooms = "".join(f'''<article class="room"><div class="pic"><img src="../img/{s["slug"]}/quarto-{i+1}.webp" alt="{n}: {d}" width="800" height="600" loading="lazy"></div><div class="rb"><h3>{n}</h3><p>{d}</p><div class="pr"><b>{brl(p)}</b><span>/ noite com café</span></div>
<a class="btn" href="https://wa.me/5595981020209?text={('Olá! Quero saber a disponibilidade do ' + n).replace(' ', '%20')}">Consultar pelo WhatsApp</a></div></article>''' for i, (n, p, d) in enumerate(s["rooms"]))
    amen = "".join(f"<li>{a}</li>" for a in s["amen"])
    gal = "".join(f'<figure><a href="../img/{s["slug"]}/galeria-{i+1}-full.webp"><img src="../img/{s["slug"]}/galeria-{i+1}.webp" alt="{a}" width="800" height="600" loading="lazy"></a></figure>' for i, a in enumerate(s["gal"]))
    hero_cls = "hero split" if s["layout"] == "split" else "hero center"
    return f'''<!DOCTYPE html>
<html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{s["title"]}</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?{font_q}&display=swap" rel="stylesheet">
<style>
/* Layout: site de uma página — hero com foto, sobre, quartos, comodidades, galeria, localização e WhatsApp fixo. */
:root{{--bg:{c["bg"]};--surface:{c["surface"]};--ink:{c["ink"]};--muted:{c["muted"]};--line:{c["line"]};--accent:{c["accent"]};--accent-ink:{c["accentink"]};
--font-display:"{s["display"]}",Georgia,serif;--font-body:"{s["body"]}","Segoe UI",system-ui,sans-serif;color-scheme:light}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--ink);font-family:var(--font-body);line-height:1.6}}
h1,h2,h3{{font-family:var(--font-display);line-height:1.1;margin:0;text-wrap:balance}}p{{margin:0}}a{{color:inherit}}
:focus-visible{{outline:3px solid var(--accent);outline-offset:2px}}
.wrap{{max-width:1080px;margin:0 auto;padding:0 20px}}
.demo{{background:var(--ink);color:var(--bg);text-align:center;font-size:.82rem;padding:7px 12px}}
header{{display:flex;align-items:center;gap:16px;padding:16px 0}}header b{{font-family:var(--font-display);font-size:1.3rem}}
header nav{{margin-left:auto;display:flex;gap:18px;font-size:.95rem;color:var(--muted)}}header nav a{{text-decoration:none}}
@media (max-width:720px){{header nav{{display:none}}}}
.btn{{display:inline-flex;align-items:center;justify-content:center;background:var(--accent);color:var(--accent-ink);text-decoration:none;font-weight:700;border-radius:999px;padding:11px 20px;font-size:.95rem}}
.btn:hover{{filter:brightness(1.08)}}
.hero{{position:relative;border-radius:22px;overflow:hidden;min-height:440px;display:grid}}
.hero>img{{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}}
.hero .txt{{position:relative;align-self:end;padding:36px;display:grid;gap:12px;max-width:560px}}
.hero.split .txt{{background:var(--surface);margin:24px;border-radius:16px;box-shadow:0 14px 40px rgba(0,0,0,.18)}}
.hero.center{{place-items:center;text-align:center}}.hero.center .txt{{align-self:center;background:color-mix(in srgb,var(--surface) 90%,transparent);border-radius:18px;margin:24px;justify-items:center}}
.hero .btn{{justify-self:start}}.hero.center .btn{{justify-self:center}}.hero .k{{color:var(--accent);font-weight:700;font-size:.9rem}}.hero h1{{font-size:clamp(2rem,5vw,3.2rem)}}.hero p{{color:var(--muted)}}
@media (max-width:720px){{.hero{{min-height:600px}}.hero .txt,.hero.center .txt{{align-self:end;margin:12px;padding:20px;gap:8px}}.hero h1{{font-size:1.75rem}}}}
section{{padding:56px 0}}section h2{{font-size:clamp(1.6rem,3vw,2.2rem);margin-bottom:18px}}
.about{{display:grid;grid-template-columns:1fr 1fr;gap:30px;align-items:center}}@media (max-width:760px){{.about{{grid-template-columns:1fr}}}}
.about p{{font-size:1.08rem;color:var(--muted);max-width:60ch}}
.facts{{display:grid;grid-template-columns:1fr 1fr;gap:12px}}.facts div{{background:var(--surface);border:1px solid var(--line);border-radius:14px;padding:16px}}.facts b{{display:block;font-family:var(--font-display);font-size:1.4rem}}.facts span{{color:var(--muted);font-size:.9rem}}
.rooms{{display:grid;grid-template-columns:repeat(auto-fit,minmax(270px,1fr));gap:18px}}
.room{{background:var(--surface);border:1px solid var(--line);border-radius:16px;overflow:hidden;display:flex;flex-direction:column}}
.room .pic img{{display:block;width:100%;height:auto;aspect-ratio:4/3;object-fit:cover}}.rb{{padding:18px;display:grid;gap:10px;flex:1;align-content:start}}.rb p{{color:var(--muted);font-size:.95rem}}
.pr{{display:flex;gap:6px;align-items:baseline}}.pr b{{font-family:var(--font-display);font-size:1.5rem;font-variant-numeric:tabular-nums}}.pr span{{color:var(--muted);font-size:.85rem}}
.amen{{list-style:none;padding:0;margin:0;display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:10px}}
.amen li{{background:var(--surface);border:1px solid var(--line);border-left:4px solid var(--accent);border-radius:10px;padding:12px 14px;font-weight:600}}
.gal{{display:grid;grid-template-columns:repeat(4,1fr);gap:10px}}@media (max-width:720px){{.gal{{grid-template-columns:1fr 1fr}}}}
.gal figure{{margin:0;border-radius:12px;overflow:hidden}}.gal img{{display:block;width:100%;height:auto;aspect-ratio:4/3;object-fit:cover}}
.gal a{{display:block;cursor:zoom-in}}.gal img{{transition:transform .4s ease}}.gal a:hover img{{transform:scale(1.04)}}
.lb{{width:100vw;height:100dvh;max-width:none;max-height:none;margin:0;padding:0;border:0;background:rgba(8,10,9,.94);color:#fff}}
.lb[open]{{display:grid;place-items:center}}.lb::backdrop{{background:rgba(0,0,0,.6)}}
.lb img{{max-width:100vw;max-height:calc(100dvh - 90px);object-fit:contain}}
.lb p{{position:absolute;left:0;right:0;bottom:16px;text-align:center;font-size:.9rem;opacity:.85;padding:0 64px}}
.lb button{{position:absolute;background:rgba(255,255,255,.12);color:#fff;border:0;border-radius:999px;width:48px;height:48px;font-size:1.8rem;line-height:1;cursor:pointer}}
.lb button:hover{{background:rgba(255,255,255,.25)}}.lb .x{{top:14px;right:14px}}.lb .pv{{left:14px;top:50%;translate:0 -50%}}.lb .nx{{right:14px;top:50%;translate:0 -50%}}
@media (max-width:720px){{.lb .pv,.lb .nx{{top:auto;bottom:6px;translate:none}}}}
@media (prefers-reduced-motion:reduce){{.gal img{{transition:none}}}}
.loc{{background:var(--surface);border:1px solid var(--line);border-radius:18px;padding:28px;display:flex;flex-wrap:wrap;gap:20px;align-items:center;justify-content:space-between}}
.loc p{{color:var(--muted)}}
footer{{padding:30px 0 90px;color:var(--muted);font-size:.88rem;text-align:center}}
.wa{{position:fixed;right:18px;bottom:18px;background:#25D366;color:#0B3B1E;font-weight:800;text-decoration:none;border-radius:999px;padding:14px 20px;box-shadow:0 10px 24px rgba(0,0,0,.25);display:flex;gap:8px;align-items:center}}
</style></head><body>
<div class="demo">Modelo demonstrativo · pousada fictícia · fotos ilustrativas</div>
<div class="wrap">
<header><b>{s["short"]}</b><nav><a href="#sobre">Sobre</a><a href="#quartos">Acomodações</a><a href="#galeria">Galeria</a><a href="#local">Como chegar</a></nav><a class="btn" href="#quartos">Reservar</a></header>
<div class="{hero_cls}"><img src="../img/{s["slug"]}/hero.webp" alt="{s["hero_alt"]}" width="1600" height="900" fetchpriority="high"><div class="txt"><span class="k">{s["kicker"]}</span><h1>{s["tagline"]}</h1><p>Atendimento rápido pelo WhatsApp e café da manhã incluso.</p><a class="btn" href="#quartos">Ver acomodações</a></div></div>
<section id="sobre" class="about"><div><h2>Sobre a pousada</h2><p>{s["about"]}</p></div>
<div class="facts"><div><b>14h</b><span>Check-in</span></div><div><b>12h</b><span>Check-out</span></div><div><b>Pix</b><span>Sinal de 30% para confirmar</span></div><div><b>3x</b><span>sem juros no cartão</span></div></div></section>
<section id="quartos"><h2>Acomodações</h2><div class="rooms">{rooms}</div></section>
<section><h2>Comodidades</h2><ul class="amen">{amen}</ul></section>
<section id="galeria"><h2>Galeria</h2><div class="gal">{gal}</div></section>
<section id="local"><div class="loc"><div><h2 style="margin-bottom:6px">Como chegar</h2><p>{s["where"]}</p></div><a class="btn" href="https://wa.me/5595981020209">Pedir localização no WhatsApp</a></div></section>
</div>
<footer>{s["title"]} · modelo de site demonstrativo desenvolvido por Kelvin Jordan</footer>
<a class="wa" href="https://wa.me/5595981020209">WhatsApp</a>
{LIGHTBOX}
</body></html>'''

import os
for s in SITES:
    os.makedirs(s["slug"], exist_ok=True)
    open(s["file"], "w", encoding="utf-8").write(build(s))
print("ok")
