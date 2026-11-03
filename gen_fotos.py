"""Gera fotos das pousadas com a Gemini API e converte para WebP.

Uso: python gen_fotos.py demo serra mar colonial mata
A chave é lida do .env do AI-VIDEO-FACTORY em tempo de execução; nunca fica neste projeto.
"""
import base64, io, json, sys, urllib.request
from pathlib import Path
from PIL import Image

ENV = Path(r"C:\Projetos\AI-VIDEO-FACTORY\.env")
MODEL = "gemini-3.1-flash-image"
ROOT = Path(__file__).parent / "img"
STYLE = ("Fotografia profissional de hotelaria, realista, luz natural, lente 24-35mm, "
         "cores naturais, sem texto, sem logotipos, sem marca d'água, sem pessoas em destaque.")

SITES = {
    "demo": {
        "hero": ("16:9", "Pequena pousada brasileira à beira de um rio largo ao pôr do sol, casas térreas de madeira e "
                 "alvenaria clara com telhado de telha, deck de madeira com redes, palmeiras e mata verde, "
                 "céu dourado refletindo na água calma, atmosfera acolhedora do interior do Brasil."),
        "quarto-casal": ("4:3", "Quarto Standard Casal de pousada simples e caprichada, cama queen com roupa de cama branca "
                         "e manta verde-musgo, ar-condicionado split na parede, frigobar pequeno, piso de madeira, "
                         "janela com luz da tarde, 18 m², decoração rústica limpa."),
        "quarto-familia": ("4:3", "Quarto Família de pousada brasileira, uma cama de casal e duas camas de solteiro, "
                           "roupa de cama branca com detalhes amarelo-mostarda, smart TV na parede, ar-condicionado, "
                           "paredes claras, piso de madeira, 28 m², iluminação natural."),
        "quarto-varanda": ("4:3", "Suíte com varanda de pousada à beira-rio, cama de casal ao fundo e porta de vidro aberta "
                           "para varanda com rede colorida e vista para o rio e a mata, banheira visível, "
                           "luz dourada do fim de tarde, madeira e tons verdes."),
    },
    "chapada": {
        "hero": ("16:9", "Pousada de chalés de pedra e madeira na Chapada brasileira, cerrado com paredões de arenito avermelhado "
                 "ao fundo, cachoeira alta caindo num poço verde-azulado perto dos chalés, céu azul de fim de tarde, luz dourada."),
        "quarto-casal": ("4:3", "Chalé casal de pedra e madeira na chapada, cama de casal com roupa de cama branca e manta azul-petróleo, "
                         "parede de pedra aparente, janela grande com vista do cerrado e paredões, luz da manhã."),
        "quarto-familia": ("4:3", "Chalé família na chapada, cama de casal e duas camas de solteiro, paredes de pedra e madeira clara, "
                           "tapete de fibra, ventilador de teto, porta aberta para varanda com vista do cerrado."),
        "quarto-varanda": ("4:3", "Chalé mirante na chapada, cama de casal virada para porta de vidro aberta para varanda com "
                           "hidromassagem externa e vista panorâmica de cânion e cachoeira ao longe, pôr do sol."),
    },
    "fazenda": {
        "hero": ("16:9", "Pousada rural numa fazenda brasileira, casarão de fazenda branco com janelas azuis e varanda comprida, "
                 "ipês amarelos floridos, gramado, cavalos pastando, lago calmo ao lado, manhã ensolarada com céu azul."),
        "quarto-casal": ("4:3", "Quarto casal de pousada de fazenda, cama de ferro antiga com colcha de crochê branca, piso de ladrilho "
                         "hidráulico, janela de madeira azul aberta para o jardim com ipê amarelo, móveis rústicos."),
        "quarto-familia": ("4:3", "Quarto família em casarão de fazenda, cama de casal e duas camas de solteiro de madeira, colchas coloridas "
                           "de retalho, piso de madeira, pé-direito alto com forro de madeira, janelas abertas para o pasto."),
        "quarto-varanda": ("4:3", "Suíte com varanda de frente para o lago numa fazenda, cama de casal com dossel leve, banheira de imersão "
                           "perto da janela, varanda com cadeiras de balanço e vista do lago e dos ipês, fim de tarde."),
    },
    "serra": {
        "hero": ("16:9", "Chalés de madeira de uma pousada na serra do sul do Brasil entre araucárias, montanhas azuladas "
                 "ao fundo, fumaça saindo da chaminé, fim de tarde com névoa leve, gramado verde, clima frio e aconchegante."),
        "quarto-1": ("4:3", "Interior de chalé de madeira para casal na serra, cama de casal com mantas de lã terracota, "
                     "lareira acesa, banheira de hidromassagem ao lado, porta para varanda com vista das montanhas."),
        "quarto-2": ("4:3", "Chalé família de madeira com mezanino, cama de casal embaixo e duas camas de solteiro no mezanino, "
                     "cozinha compacta com bancada de madeira, tapete, luz quente, decoração rústica de montanha."),
        "quarto-3": ("4:3", "Chalé com janela panorâmica do chão ao teto para um vale verde com névoa, cama de casal, "
                     "banheira de imersão perto da janela, rede de tecido cru, madeira clara, manhã fria."),
        "galeria-1": ("4:3", "Mesa de café colonial servida na varanda de madeira de uma pousada na serra: bolos, pães caseiros, "
                      "queijos, geleias, café passado, vista das araucárias ao fundo."),
        "galeria-2": ("4:3", "Trilha de terra entre araucárias e samambaias numa manhã de névoa na serra, luz suave."),
        "galeria-3": ("4:3", "Lareira acesa em sala de chalé de madeira, poltronas com mantas, caneca de chocolate quente."),
        "galeria-4": ("4:3", "Vista de um vale verde da serra ao amanhecer com névoa entre as montanhas, cerca de madeira em primeiro plano."),
    },
    "mar": {
        "hero": ("16:9", "Pousada pé na areia no Nordeste do Brasil, casas brancas com telhado de telha laranja, coqueiros, "
                 "faixa de areia clara e mar azul-turquesa calmo, céu azul com poucas nuvens, manhã ensolarada."),
        "quarto-1": ("4:3", "Quarto de casal arejado de pousada de praia, paredes brancas, cama com roupa de cama branca e almofadas "
                     "azul-turquesa, ar-condicionado, porta aberta para varanda com rede e o mar ao fundo."),
        "quarto-2": ("4:3", "Quarto família de pousada de praia para 4 pessoas, cama de casal e beliche ou duas camas de solteiro, "
                     "frigobar, cores branco e azul, janela com vista lateral do mar, piso claro."),
        "quarto-3": ("4:3", "Suíte frente mar de pousada, cama de casal virada para porta de vidro aberta para varanda privativa "
                     "com duas espreguiçadeiras e mar turquesa logo à frente, luz da manhã."),
        "galeria-1": ("4:3", "Piscina de pousada de praia cercada de coqueiros e espreguiçadeiras, água azul, dia ensolarado."),
        "galeria-2": ("4:3", "Café da manhã tropical servido em mesa de madeira: frutas como manga, mamão e abacaxi, tapioca, "
                      "suco, cuscuz, perto do mar."),
        "galeria-3": ("4:3", "Guarda-sóis de palha e cadeiras de praia na areia clara diante de mar calmo e transparente."),
        "galeria-4": ("4:3", "Jangada nordestina de madeira com vela branca triangular na areia de uma praia do Ceará, mar verde-claro calmo, coqueiros, sem montanhas."),
    },
    "colonial": {
        "hero": ("16:9", "Fachada de casarão colonial brasileiro de 1890 restaurado em centro histórico, paredes amarelo-claro, "
                 "janelas e portas em arco com molduras brancas e esquadrias azuis, rua de pedra (pé de moleque), "
                 "igreja barroca ao fundo, luz de fim de tarde."),
        "quarto-1": ("4:3", "Suíte clássica em casarão colonial, cama king com cabeceira de madeira entalhada, móveis de época, "
                     "piso de tábuas largas de madeira original, pé-direito alto, roupa de cama branca com detalhes vinho."),
        "quarto-2": ("4:3", "Suíte com sacada em casarão colonial, pé-direito de 5 metros, porta-janela alta aberta para "
                     "pequena sacada de ferro com vista para rua de pedra e casarões coloridos, cama de casal."),
        "quarto-3": ("4:3", "Suíte de casarão colonial com porta aberta para pátio interno com jabuticabeiras e vasos de plantas, "
                     "cama de casal, paredes brancas grossas, piso de madeira, luz da manhã."),
        "galeria-1": ("4:3", "Pátio interno de casarão colonial com jabuticabeira, mesa de café da manhã com toalha branca, "
                      "piso de pedra, paredes coloridas."),
        "galeria-2": ("4:3", "Rua de pedra de centro histórico brasileiro com casarões coloniais coloridos e igreja barroca ao fundo."),
        "galeria-3": ("4:3", "Corredor interno de casarão colonial com piso de madeira original, portas altas e luz entrando pelas janelas."),
        "galeria-4": ("4:3", "Bicicletas encostadas na parede colorida de um casarão colonial numa rua de pedra."),
    },
    "mata": {
        "hero": ("16:9", "Bangalôs de madeira suspensos sobre palafitas no meio da floresta amazônica, à beira de um igarapé "
                 "de água escura e calma, passarelas de madeira, árvores altas, luz da manhã atravessando as copas."),
        "quarto-1": ("4:3", "Interior de bangalô de madeira na floresta para casal, cama com mosquiteiro branco, ventilador de teto, "
                     "varanda com rede, vista para a mata verde, decoração simples com fibras naturais."),
        "quarto-2": ("4:3", "Bangalô família na floresta com dois ambientes, cama de casal e duas camas de solteiro com mosquiteiros, "
                     "paredes de madeira, janelas teladas abertas para a mata."),
        "quarto-3": ("4:3", "Deck privativo de madeira de bangalô sobre igarapé de água escura na floresta amazônica, "
                     "rede, duas cadeiras de madeira, porta aberta mostrando a cama ao fundo."),
        "galeria-1": ("4:3", "Banho em igarapé de água escura e transparente na floresta amazônica, pequena prainha de areia branca."),
        "galeria-2": ("4:3", "Canoa de madeira num igarapé estreito cercado de floresta densa, luz suave da manhã."),
        "galeria-3": ("4:3", "Mesa de culinária regional amazônica: peixe assado na folha de bananeira, açaí, farinha, tucupi."),
        "galeria-4": ("4:3", "Trilha de madeira suspensa no meio da floresta amazônica com árvores gigantes e raízes tabulares."),
    },
}


def key():
    for line in ENV.read_text(encoding="utf-8").splitlines():
        if line.startswith("GEMINI_API_KEY="):
            return line.split("=", 1)[1].strip().strip('"')
    sys.exit("GEMINI_API_KEY não encontrada")


def gerar(prompt, aspect, k):
    body = {"contents": [{"parts": [{"text": f"{prompt} {STYLE}"}]}],
            "generationConfig": {"responseModalities": ["IMAGE"], "imageConfig": {"aspectRatio": aspect}}}
    req = urllib.request.Request(
        f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent",
        data=json.dumps(body).encode(), headers={"Content-Type": "application/json", "x-goog-api-key": k})
    resp = json.load(urllib.request.urlopen(req, timeout=180))
    for part in resp["candidates"][0]["content"]["parts"]:
        if "inlineData" in part:
            return base64.b64decode(part["inlineData"]["data"])
    raise RuntimeError(f"sem imagem na resposta: {json.dumps(resp)[:300]}")


def webp(raw, dest, largura, limite=150_000):
    img = Image.open(io.BytesIO(raw)).convert("RGB")
    if img.width > largura:
        img = img.resize((largura, round(img.height * largura / img.width)), Image.LANCZOS)
    for q in range(82, 40, -6):  # baixa a qualidade até caber no limite
        buf = io.BytesIO()
        img.save(buf, "WEBP", quality=q, method=6)
        if buf.tell() <= limite:
            break
    dest.write_bytes(buf.getvalue())
    return buf.tell(), q


def main(site):
    k, pasta = key(), ROOT / site
    (pasta / "original").mkdir(parents=True, exist_ok=True)
    for nome, (aspect, prompt) in SITES[site].items():
        orig = pasta / "original" / f"{nome}.png"
        if not orig.exists():  # não paga de novo o que já foi gerado
            orig.write_bytes(gerar(prompt, aspect, k))
        tam, q = webp(orig.read_bytes(), pasta / f"{nome}.webp", 1600 if nome == "hero" else 800)
        print(f"{site}/{nome}.webp  {tam // 1024} KB  q={q}")
        if nome.startswith("galeria"):  # versão maior para a tela cheia
            tam, q = webp(orig.read_bytes(), pasta / f"{nome}-full.webp", 1200, 250_000)
            print(f"{site}/{nome}-full.webp  {tam // 1024} KB  q={q}")


if __name__ == "__main__":
    for s in sys.argv[1:] or ["demo"]:
        main(s)
