#!/usr/bin/env python3
"""_servidor_escrita.py — servidor HTTP local (porta 8002) que escreve
ficheiros da pasta app/ recebidos por POST, para o musicbox_studio.html
deixar de depender da File System Access API (que pede autorização de
pasta a cada refresh do browser — não persiste entre sessões; ver
DECISIONS.md 2026-08-13). Também serve ficheiros estáticos da pasta app/
por GET (ver DECISIONS.md 2026-08-21), para a app poder correr inteira
numa única porta (8002) em vez de depender também de
`python3 -m http.server` na porta 8000.

GET /qualquer/ficheiro.ext
  -> 200 + conteúdo do ficheiro (Content-Type adivinhado por extensão)
  -> 403 se o caminho tentar sair de app/ (ex.: ../)
  -> 404 se o ficheiro não existir

GET /mb-proxy?caminho=artist/&query=...&fmt=json&limit=5
GET /mb-proxy?caminho=artist/<mbid>&fmt=json&inc=genres
GET /mb-proxy?caminho=recording/&query=...&fmt=json&limit=100
  -> 200 + corpo devolvido pela MusicBrainz (JSON), sem alterações
  -> 400/502 {"erro": "..."}
  Proxy do lado do servidor para a API da MusicBrainz — chamar
  musicbrainz.org directamente do browser dá net::ERR_CONNECTION_CLOSED,
  porque a MusicBrainz exige um User-Agent próprio e o fetch() do browser
  não permite defini-lo (forbidden header). `caminho` restrito a
  `artist/`, `recording/` ou `artist/<mbid>` — nunca um caminho arbitrário
  da MusicBrainz. Ver DECISIONS.md 2026-08-25.

Uso: python3 _servidor_escrita.py (stdlib puro, sem dependências — ao
contrário de _servidor_librosa.py não precisa de venv).

POST /escrever?ficheiro=playlists.json
  corpo: conteúdo literal do ficheiro (texto, UTF-8)
  -> 200 {"ok": true, "ficheiro": "...", "bytes": N}
  -> 400/403/500 {"erro": "..."}

POST /upload?ficheiro=concorrente_1.jpg
  corpo: bytes binários da imagem (JPEG/PNG)
  -> 200 {"ok": true, "ficheiro": "...", "bytes": N}
  -> 400/403/500 {"erro": "..."}
  Usado pelo separador "Concorrentes" do Studio para gravar a foto de cada
  concorrente directamente em app/, em vez de exigir um URL alojado
  algures. Nome do ficheiro sempre concorrente_[1-4].(jpg|jpeg|png) — um
  novo upload para o mesmo concorrente substitui o ficheiro (os.replace),
  nunca acumula.

POST /gerar-faixas
  corpo: {"prompt": "..."}
  -> 200 {"ok": true, "resultado": {...}}  (objecto JSON já parseado)
  -> 400/500/502 {"erro": "..."}
  Usado pela secção "✦ Gerar faixas com IA" do modal "Nova Playlist" (só
  playlists STD). Chama a API da Anthropic (model claude-sonnet-4-6) DO
  LADO DO SERVIDOR — a ANTHROPIC_API_KEY nunca chega ao browser, lê-se
  só da variável de ambiente ANTHROPIC_API_KEY deste processo. Se não
  estiver definida, devolve 500 com uma mensagem clara em vez de tentar
  chamar a API sem chave. Ver DECISIONS.md 2026-08-13 — decisão de
  arquitectura: chave só do lado do servidor, nunca em prompt()/browser.

POST /gerar-faixa
  corpo: {"url": "https://www.youtube.com/watch?v=...", "id": "syn_01"}
     ou: {"artista": "...", "titulo": "...", "id": "syn_01"}  (sem url)
  -> 200 {"ok": true, "ficheiro_a": "syn_01_a.mp3", "ficheiro_b": "syn_01_b.mp3", "fonte": "itunes"|"youtube"}
  -> 400/500/504 {"erro": "..."}
  Usado pelo botão "⬇ Gerar trechos" na Mesa de Montagem (só aparece em
  faixas com estado 'rascunho', sem áudio). Se o pedido não trouxer 'url':
    1. Com 'artista' E 'titulo', tenta primeiro o modo iTunes
       (gerar_faixa.py --itunes --artista ... --titulo ... <id> --force):
       procura na iTunes Search API, descarrega o preview oficial de 30s
       (previewUrl) e corta sempre 0-12s/18-30s — sem YouTube, sem
       sugerir_trechos.py, muito mais rápido e sem o risco de "Sign in to
       confirm". Ver DECISIONS.md 2026-08-25.
    2. Se a iTunes não tiver preview (ou só vier 'artista' ou só 'titulo'),
       cai para o comportamento anterior: pesquisa
       "ytsearch1:ARTISTA TITULO" via yt-dlp --get-url --no-playlist,
       depois corre gerar_faixa.py <url> <id> --force como subprocesso
       (download via yt-dlp + sugerir_trechos.py + corte via ffmpeg — ver
       esse ficheiro).
  Só devolve os nomes dos ficheiros gerados; NÃO escreve em catalogo.json —
  quem actualiza a faixa é o cliente (mesmo padrão de
  updateClipField()/detectarMomentoClip() no Studio: fica em
  CATALOGO_PATCH, só entra em catalogo_patch.json quando se clica
  "Guardar", nunca escreve catalogo.json directamente).

GET /buscar-imagem-artista?artista=Queen
  -> 200 {"ok": true, "imagem": "https://...", "imagem_fonte": "itunes_artist"
          |"theaudiodb"|"wikipedia_infobox", "imagem_credito": "...",
          "imagem_url_origem": "https://...", "imagem_data_captura": "AAAA-MM-DD",
          "imagem_licenca_estado": "livre"|"confirmar", "largura": N, "altura": N}
  -> 404 {"ok": false, "erro": "..."}  (nenhuma fonte teve resultado ≥300x300)
  Estratégia de imagem para o piloto (ver DECISIONS.md) — vai além do
  Wikimedia Commons já usado em abrirPesquisaImagem()/executarPesquisaImagem()
  no lado do cliente. Cascata do lado do SERVIDOR (não do browser) por três
  razões: evita CORS em fontes que não o suportem, mantém a porta aberta a
  chaves de API futuras (ex. Bing/Google Image Search) sem as expor no
  browser — mesmo padrão já usado para ANTHROPIC_API_KEY — e permite testar
  esta cadeia directamente com curl, sem depender do Studio no browser.
  Ordem (pára na primeira com resultado ≥300x300px):
    1. iTunes Search API (entity=song) — sem chave. NOTA HONESTA: a API
       gratuita da iTunes não expõe fotos de artista, só artwork de
       álbum/single — usada aqui como aproximação visual, sinalizada no
       imagem_credito, não como retrato confirmado do artista.
    2. TheAudioDB (search.php, chave de teste pública "2") — strArtistThumb.
       Sem dimensões na resposta da API — descarrega a imagem e lê a
       largura/altura directamente dos bytes (JPEG/PNG), sem Pillow (não
       está instalado neste ambiente — ver decisão sobre não instalar
       pacotes Python fora de venv).
    3. Wikipedia (REST API page/summary do artigo mais relevante por
       pesquisa) — imagem do infobox, que tende a ser "a" foto canónica já
       escolhida pela comunidade, não um resultado aleatório de categoria.
       imagem_licenca_estado só fica "livre" se a imagem vier mesmo do
       Wikimedia Commons E a extmetadata da Commons confirmar uma licença
       livre reconhecida (cc0/cc-by/cc-by-sa/domínio público) — nunca por
       assumpção só por vir da Wikipedia.
    4. Pesquisa de imagem geral — POR IMPLEMENTAR. A Bing Search API (toda
       a família, incl. Image) foi retirada pela Microsoft a 2025-08-11 —
       já não existe. Alternativa real: Google Custom Search JSON API
       (paga, API key + Search Engine ID). BING_IMAGE_SEARCH_KEY existe só
       como placeholder — decisão de serviço + chave por fazer; a função
       devolve sempre None por agora, mesmo padrão dos stubs
       _buscar_spotify/_buscar_youtube em gerar_faixa_v2.py.
  imagem_url_origem é sempre a página onde a imagem foi encontrada (perfil/
  artigo/resultado), não o link directo do CDN da imagem — é o que permite
  voltar à fonte mais tarde para confirmar licença/autor.

Só escreve nos ficheiros da whitelist FICHEIROS_PERMITIDOS (/escrever) ou
que cumpram NOME_UPLOAD_REGEX (/upload), dentro de app/ — nunca um caminho
arbitrário vindo do parâmetro da URL (protecção contra escrever/substituir
qualquer ficheiro do disco). CORS restrito à origem do Studio
(http://localhost:8000), ao contrário do '*' aberto do
_servidor_librosa.py — aquele só lê ficheiros, este escreve, por isso tem
de ser mais cauteloso quanto a quem pode chamar. Escrita atómica
(ficheiro temporário + os.replace) para nunca deixar o ficheiro a meio
caso o processo seja interrompido durante a escrita.
"""
import json
import mimetypes
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs, unquote, urlencode, quote

APP_DIR = os.path.dirname(os.path.abspath(__file__))
PORTA = 8002
ORIGEM_PERMITIDA = 'http://localhost:8002'
UPLOAD_MAX_BYTES = 8 * 1024 * 1024  # 8MB — generoso para uma foto, evita upload disparatado

# ── Geração de faixas com IA (Anthropic) ────────────────────────────────
ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY', '')
ANTHROPIC_MODEL = 'claude-sonnet-4-6'
ANTHROPIC_URL = 'https://api.anthropic.com/v1/messages'
ANTHROPIC_VERSION = '2023-06-01'
GERAR_FAIXAS_MAX_PROMPT = 4000   # protecção contra corpos disparatados
GERAR_FAIXAS_TIMEOUT = 60        # segundos — geração de texto pode demorar

# ── Gerar trechos A/B a partir do YouTube (gerar_faixa.py) ──────────────
GERAR_FAIXA_SCRIPT = os.path.join(APP_DIR, 'gerar_faixa.py')
GERAR_FAIXA_TIMEOUT = 600  # segundos (10min) — download + análise + corte; músicas longas (ex. "Weightless", Marconi Union) podem demorar mais
YT_SEARCH_TIMEOUT = 60  # segundos — yt-dlp --get-url só resolve o URL, não descarrega áudio
GERAR_FAIXA_ITUNES_TIMEOUT = 60  # segundos — pesquisa + download do preview de 30s + corte ffmpeg (ficheiro pequeno, bem mais rápido que o modo YouTube)
ID_FAIXA_REGEX = re.compile(r'^[A-Za-z0-9_]+$')

# User-Agent identificando a app — MusicBrainz E Wikipedia/Wikimedia
# exigem um User-Agent próprio nos pedidos server-to-server (bloqueiam o
# genérico do urllib com 403); mesma etiqueta usada nas duas.
APP_USER_AGENT = 'MusicBoxStudio/1.0 (andreclemente67@gmail.com)'

# ── Proxy de pedidos à MusicBrainz (GET /mb-proxy — ver _mb_proxy) ───────
MUSICBRAINZ_BASE = 'https://musicbrainz.org/ws/2/'
MUSICBRAINZ_TIMEOUT = 15

# ── Imagem de artista (GET /buscar-imagem-artista — ver _buscar_imagem_artista
# e a cascata de fontes documentada no cabeçalho deste ficheiro) ────────
IMAGEM_ARTISTA_TIMEOUT = 15
RESOLUCAO_MINIMA_IMAGEM = 300  # px, largura e altura — ver DECISIONS.md
BING_IMAGE_SEARCH_KEY = os.environ.get('BING_IMAGE_SEARCH_KEY', '')  # ainda não usada — fonte 4 por implementar
LICENCAS_LIVRES_COMMONS = ('cc0', 'cc-by', 'public domain', 'pd-old', 'pdm')

# ── Ler playlist do YouTube sem descarregar (tab "Playlist YouTube" de
# "Gerar com IA" no Studio) ──────────────────────────────────────────────
LISTAR_PLAYLIST_TIMEOUT = 60  # segundos — --flat-playlist só lê metadados (não descarrega áudio nem vídeo), mas playlists grandes podem demorar
LISTAR_PLAYLIST_MAX_FAIXAS = 30  # protecção contra playlists gigantes — só os primeiros N vídeos (--playlist-end)
YOUTUBE_URL_REGEX = re.compile(r'^https?://(www\.)?(youtube\.com|youtu\.be|music\.youtube\.com)/', re.IGNORECASE)

FICHEIROS_PERMITIDOS = {
    'playlists.json',
    'catalogo_patch.json',
    'catalogo_adicionar.json',
    'propostas_chaves.md',
    'concorrentes.json',
    'apresentador.json',
}

NOME_UPLOAD_REGEX = re.compile(r'^(concorrente_[1-4]|apresentador|artista_[a-z0-9_]+)\.(jpg|jpeg|png)$')


# ── Cascata de fontes de imagem de artista (GET /buscar-imagem-artista) ──

def _dimensoes_imagem(dados):
    """Largura/altura a partir dos bytes de uma imagem JPEG ou PNG, sem
    Pillow (não instalado neste ambiente). Devolve None se o formato não
    for reconhecido ou os bytes forem insuficientes para decidir."""
    if dados[:8] == b'\x89PNG\r\n\x1a\n':
        if len(dados) >= 24:
            return int.from_bytes(dados[16:20], 'big'), int.from_bytes(dados[20:24], 'big')
        return None
    if dados[:2] == b'\xff\xd8':
        i = 2
        while i < len(dados) - 9:
            if dados[i] != 0xFF:
                i += 1
                continue
            marcador = dados[i + 1]
            if marcador in (0xC0, 0xC1, 0xC2, 0xC3):
                altura = int.from_bytes(dados[i + 5:i + 7], 'big')
                largura = int.from_bytes(dados[i + 7:i + 9], 'big')
                return largura, altura
            tamanho_segmento = int.from_bytes(dados[i + 2:i + 4], 'big')
            i += 2 + tamanho_segmento
        return None
    return None


def _get_json(url, timeout=IMAGEM_ARTISTA_TIMEOUT):
    # User-Agent sempre definido: a Wikipedia/Wikimedia (tal como a
    # MusicBrainz) devolve 403 ao User-Agent genérico do urllib — só
    # descoberto ao testar "Queen" em 2026-08-26 (falhava silenciosamente,
    # tratado como "sem resultado" pelo try/except das funções chamadoras).
    req = urllib.request.Request(url, headers={'User-Agent': APP_USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode('utf-8'))


def _itunes_imagem_artista(artista):
    # NOTA HONESTA: a API gratuita da iTunes não devolve fotos de artista,
    # só artwork de álbum/single — usado aqui como aproximação, sinalizado
    # no imagem_credito. Mesmo padrão de upgrade 100x100bb->600x600bb já
    # usado em aplicar_artwork.py.
    try:
        url = f'https://itunes.apple.com/search?{urlencode({"term": artista, "entity": "song", "limit": 1})}'
        dados = _get_json(url)
    except Exception:
        return None
    resultados = dados.get('results') or []
    if not resultados:
        return None
    r = resultados[0]
    artwork = r.get('artworkUrl100')
    if not artwork:
        return None
    return {
        'imagem': artwork.replace('100x100bb', '600x600bb'),
        'imagem_fonte': 'itunes_artist',
        'imagem_credito': 'Capa iTunes (Apple Music) — capa de álbum/single, não retrato do artista',
        'imagem_url_origem': r.get('trackViewUrl') or r.get('collectionViewUrl') or r.get('artistViewUrl') or '',
        'imagem_licenca_estado': 'confirmar',
        'largura': 600, 'altura': 600,
    }


def _theaudiodb_imagem_artista(artista):
    try:
        dados = _get_json(f'https://www.theaudiodb.com/api/v1/json/2/search.php?s={quote(artista)}')
    except Exception:
        return None
    artistas = dados.get('artists') or []
    if not artistas:
        return None
    a = artistas[0]
    thumb = a.get('strArtistThumb')
    if not thumb:
        return None
    try:
        with urllib.request.urlopen(thumb, timeout=IMAGEM_ARTISTA_TIMEOUT) as resp:
            img_bytes = resp.read()
    except Exception:
        return None
    dim = _dimensoes_imagem(img_bytes)
    if not dim or dim[0] < RESOLUCAO_MINIMA_IMAGEM or dim[1] < RESOLUCAO_MINIMA_IMAGEM:
        return None
    id_artista = a.get('idArtist')
    return {
        'imagem': thumb,
        'imagem_fonte': 'theaudiodb',
        'imagem_credito': 'TheAudioDB',
        'imagem_url_origem': f'https://www.theaudiodb.com/artist/{id_artista}' if id_artista else 'https://www.theaudiodb.com/',
        'imagem_licenca_estado': 'confirmar',
        'largura': dim[0], 'altura': dim[1],
    }


def _licenca_commons_e_livre(nome_ficheiro):
    """Confirma (não assume) que um ficheiro do Wikimedia Commons tem
    licença livre reconhecida, via extmetadata — mesmo campo já lido em
    executarPesquisaImagem() no lado do cliente."""
    try:
        url = f'https://commons.wikimedia.org/w/api.php?{urlencode({"action": "query", "titles": f"File:{nome_ficheiro}", "prop": "imageinfo", "iiprop": "extmetadata", "format": "json"})}'
        dados = _get_json(url)
        paginas = (dados.get('query') or {}).get('pages') or {}
        for pagina in paginas.values():
            infos = pagina.get('imageinfo') or []
            if not infos:
                continue
            licenca = ((infos[0].get('extmetadata') or {}).get('LicenseShortName') or {}).get('value', '').lower()
            if any(termo in licenca for termo in LICENCAS_LIVRES_COMMONS):
                return True
    except Exception:
        pass
    return False


TERMOS_CATEGORIA_MUSICAL = (
    'musical group', 'musician', 'singer', 'band', 'record label',
    'rock band', 'pop group', 'songwriter', 'rapper', 'vocalist',
    'music group', 'record producer', 'musical duo',
)


def _pagina_wikipedia_e_musical(titulo_pagina):
    """Confirma (não assume) que a página é mesmo sobre um artista/banda de
    música, via categorias da própria página. Sozinho NÃO chega — descoberto
    ao testar "Grimes": "Scott Grimes" (actor) tem mesmo categorias como
    "American male singers" (canta a sério, só não é quem procuramos), por
    isso isto combina-se sempre com _titulo_corresponde_artista(), nunca
    usado isolado. Falha para o lado seguro: qualquer erro devolve False."""
    try:
        url = f'https://en.wikipedia.org/w/api.php?{urlencode({"action": "query", "prop": "categories", "titles": titulo_pagina, "format": "json", "cllimit": 50})}'
        dados = _get_json(url)
        paginas = (dados.get('query') or {}).get('pages') or {}
        for pagina in paginas.values():
            categorias = ' '.join(c.get('title', '') for c in (pagina.get('categories') or [])).lower()
            if any(termo in categorias for termo in TERMOS_CATEGORIA_MUSICAL):
                return True
    except Exception:
        pass
    return False


def _titulo_corresponde_artista(titulo_pagina, artista):
    """O título da página, sem o desambiguador entre parênteses (ex.
    "Queen (band)" -> "Queen"), tem de bater EXACTAMENTE com o nome
    pesquisado — não basta o nome aparecer como substring do título.
    "Scott Grimes" contém "Grimes" mas não É "Grimes"; isto é o que
    realmente separa os dois, a categoria sozinha não chega (ver acima)."""
    base = titulo_pagina.split(' (', 1)[0].strip().lower()
    return base == artista.strip().lower()


def _wikipedia_imagem_artista(artista):
    # Tenta "{artista} band" e depois "{artista} musician" — nomes comuns
    # (ex. "Queen") caem no artigo genérico da palavra sem desambiguador
    # (mesmo truque já usado na pesquisa Wikimedia Commons no cliente,
    # "${artista} musician"). Examina até 5 candidatos por qualificador
    # (não só o 1º resultado — a página certa muitas vezes não é a
    # primeira, ex. "Grimes" aparecia em 2º/1º lugar, não em 1º/1º), e só
    # aceita um candidato que passe as DUAS verificações: título
    # corresponde ao artista E página é musical. Se nada passar em nenhum
    # qualificador, devolve None e cai para a fonte seguinte (protecção
    # adicionada em 2026-08-26 depois do caso "Scott Grimes").
    titulo_pagina = None
    for qualificador in ('band', 'musician'):
        try:
            url_busca = f'https://en.wikipedia.org/w/api.php?{urlencode({"action": "query", "list": "search", "srsearch": f"{artista} {qualificador}", "format": "json", "srlimit": 5})}'
            busca = _get_json(url_busca)
            resultados = (busca.get('query') or {}).get('search') or []
        except Exception:
            resultados = []
        for r in resultados:
            candidato = r['title']
            if _titulo_corresponde_artista(candidato, artista) and _pagina_wikipedia_e_musical(candidato):
                titulo_pagina = candidato
                break
        if titulo_pagina:
            break

    if not titulo_pagina:
        return None

    try:
        resumo = _get_json(f'https://en.wikipedia.org/api/rest_v1/page/summary/{quote(titulo_pagina)}')
    except Exception:
        return None

    thumb = resumo.get('originalimage') or resumo.get('thumbnail')
    if not thumb or not thumb.get('source'):
        return None
    largura, altura = thumb.get('width', 0), thumb.get('height', 0)
    if largura < RESOLUCAO_MINIMA_IMAGEM or altura < RESOLUCAO_MINIMA_IMAGEM:
        return None

    fonte_url = thumb['source']
    licenca_livre = False
    if '/wikipedia/commons/' in fonte_url:
        # originalimage vem com query string colada (?utm_source=...) —
        # tem de ser removida antes de extrair o nome do ficheiro, senão a
        # consulta à Commons falha sempre ("ficheiro não encontrado") e cai
        # sempre em "confirmar" mesmo quando a licença é livre. Descoberto
        # ao testar Queen/Led Zeppelin/Chromatics em 2026-08-26.
        sem_query = fonte_url.split('?', 1)[0]
        partes = sem_query.split('/')
        nome_ficheiro = unquote(partes[-2] if '/thumb/' in sem_query else partes[-1])
        licenca_livre = _licenca_commons_e_livre(nome_ficheiro)

    return {
        'imagem': fonte_url,
        'imagem_fonte': 'wikipedia_infobox',
        'imagem_credito': f'Wikipedia — {titulo_pagina}',
        'imagem_url_origem': ((resumo.get('content_urls') or {}).get('desktop') or {}).get('page', ''),
        'imagem_licenca_estado': 'livre' if licenca_livre else 'confirmar',
        'largura': largura, 'altura': altura,
    }


def _bing_imagem_artista(artista):
    # Rede de segurança final — POR IMPLEMENTAR. Confirmado por pesquisa
    # (2026-08-26): a Bing Search API (Web/Image/Video/Entity/Custom/News,
    # todos os tiers) foi COMPLETAMENTE RETIRADA pela Microsoft a
    # 2025-08-11 — não existe já, nem para quem a usava antes; não é
    # substituível por uma chave. Alternativa real: Google Custom Search
    # JSON API (paga, precisa de API key + Search Engine ID configurados).
    # BING_IMAGE_SEARCH_KEY mantém o nome só por já estar documentado
    # acima — se/quando isto for implementado, é quase de certeza para o
    # Google, não para o Bing. Decisão de serviço + chave por fazer; até
    # lá devolve sempre None, mesmo padrão dos stubs
    # _buscar_spotify/_buscar_youtube em gerar_faixa_v2.py.
    if not BING_IMAGE_SEARCH_KEY:
        return None
    return None


class Handler(BaseHTTPRequestHandler):
    def log_message(self, formato, *args):
        print(f"[_servidor_escrita] {self.address_string()} - {formato % args}")

    def _enviar_json(self, status, corpo):
        payload = json.dumps(corpo, ensure_ascii=False).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', ORIGEM_PERMITIDA)
        self.send_header('Content-Length', str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def do_OPTIONS(self):
        # Pré-voo CORS — o browser envia isto antes do POST real.
        self.send_response(204)
        self.send_header('Access-Control-Allow-Origin', ORIGEM_PERMITIDA)
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_GET(self):
        # Serve ficheiros estáticos de app/ (musicbox_studio.html, .mp3,
        # imagens, .json, etc.) para a app poder correr só na porta 8002.
        parsed = urlparse(self.path)
        if parsed.path == '/mb-proxy':
            self._mb_proxy(parsed)
            return
        if parsed.path == '/buscar-imagem-artista':
            self._buscar_imagem_artista(parsed)
            return

        caminho_pedido = unquote(parsed.path)
        relativo = caminho_pedido.lstrip('/')
        caminho = os.path.realpath(os.path.join(APP_DIR, relativo))

        # Protecção contra sair de app/ (ex.: GET /../_servidor_escrita.py
        # ou qualquer caminho absoluto disfarçado) — mesmo princípio da
        # whitelist usada em /escrever e /upload.
        if caminho != APP_DIR and not caminho.startswith(APP_DIR + os.sep):
            self._enviar_texto(403, 'acesso negado')
            return
        if not os.path.isfile(caminho):
            self._enviar_texto(404, 'ficheiro não encontrado')
            return

        tipo, _ = mimetypes.guess_type(caminho)
        try:
            with open(caminho, 'rb') as f:
                dados = f.read()
        except Exception as e:
            self._enviar_texto(500, f'falha a ler ficheiro: {e}')
            return

        self.send_response(200)
        self.send_header('Content-Type', tipo or 'application/octet-stream')
        self.send_header('Content-Length', str(len(dados)))
        self.end_headers()
        self.wfile.write(dados)

    def _mb_proxy(self, parsed):
        # Proxy de pedidos à API da MusicBrainz do lado do servidor — o
        # browser, ao chamar musicbrainz.org directamente, recebe
        # net::ERR_CONNECTION_CLOSED: a MusicBrainz exige um User-Agent
        # próprio identificando a aplicação e o fetch() do browser não
        # permite definir esse cabeçalho (forbidden header), pelo que os
        # pedidos chegam com o User-Agent genérico do Chrome e são
        # recusados. Aqui controlamos o User-Agent e o problema
        # desaparece. Ver DECISIONS.md 2026-08-25.
        #
        # GET /mb-proxy?caminho=artist/&query=...&fmt=json&limit=5
        # GET /mb-proxy?caminho=artist/<mbid>&fmt=json&inc=genres
        # GET /mb-proxy?caminho=recording/&query=...&fmt=json&limit=100
        params = parse_qs(parsed.query)
        caminho = (params.get('caminho') or [''])[0]
        permitido = caminho in ('artist/', 'recording/') or re.match(r'^artist/[0-9a-fA-F-]+$', caminho or '')
        if not permitido:
            self._enviar_json(400, {"erro": f"caminho MusicBrainz não permitido: {caminho!r}"})
            return

        resto = {k: v[0] for k, v in params.items() if k != 'caminho'}
        url = f'{MUSICBRAINZ_BASE}{caminho}?{urlencode(resto)}'

        pedido = urllib.request.Request(url, headers={
            'User-Agent': APP_USER_AGENT,
            'Accept': 'application/json',
        })
        try:
            with urllib.request.urlopen(pedido, timeout=MUSICBRAINZ_TIMEOUT) as resp:
                dados = resp.read()
                status = resp.status
        except urllib.error.HTTPError as e:
            self._enviar_json(e.code, {"erro": f"MusicBrainz HTTP {e.code}"})
            return
        except urllib.error.URLError as e:
            self._enviar_json(502, {"erro": f"falha a contactar a MusicBrainz: {e}"})
            return

        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', ORIGEM_PERMITIDA)
        self.send_header('Content-Length', str(len(dados)))
        self.end_headers()
        self.wfile.write(dados)

    def _buscar_imagem_artista(self, parsed):
        # Cascata documentada no cabeçalho do ficheiro. Pára na primeira
        # fonte com resultado ≥300x300px; cada função de fonte já faz a
        # sua própria verificação de resolução.
        params = parse_qs(parsed.query)
        artista = (params.get('artista') or [''])[0].strip()
        if not artista:
            self._enviar_json(400, {"erro": "falta o parâmetro 'artista'"})
            return

        # Ordem revista em 2026-08-26, depois de testar 5 artistas: TheAudioDB
        # acertou 5/5 (foto real), Wikipedia 3/5 (uma delas com licença por
        # confirmar), iTunes só 1/5 (dá quase sempre capa de álbum, não
        # retrato — ver _itunes_imagem_artista). iTunes fica como fallback,
        # não primeira opção. Ver DECISIONS.md.
        for buscar in (_theaudiodb_imagem_artista, _wikipedia_imagem_artista, _itunes_imagem_artista, _bing_imagem_artista):
            try:
                resultado = buscar(artista)
            except Exception as e:
                resultado = None
                print(f"[_servidor_escrita] {buscar.__name__} falhou para {artista!r}: {e}")
            if resultado:
                resultado['ok'] = True
                resultado['imagem_data_captura'] = datetime.now().strftime('%Y-%m-%d')
                self._enviar_json(200, resultado)
                return

        self._enviar_json(404, {"ok": False, "erro": f"nenhuma fonte devolveu imagem ≥{RESOLUCAO_MINIMA_IMAGEM}x{RESOLUCAO_MINIMA_IMAGEM}px para {artista!r}"})

    def _enviar_texto(self, status, mensagem):
        payload = mensagem.encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'text/plain; charset=utf-8')
        self.send_header('Content-Length', str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path == '/escrever':
            self._escrever_texto(parsed)
        elif parsed.path == '/upload':
            self._upload_binario(parsed)
        elif parsed.path == '/gerar-faixas':
            self._gerar_faixas_ia()
        elif parsed.path == '/gerar-faixa':
            self._gerar_faixa()
        elif parsed.path == '/listar-playlist-youtube':
            self._listar_playlist_youtube()
        else:
            self._enviar_json(404, {"erro": "endpoint desconhecido — usa POST /escrever?ficheiro=..., POST /upload?ficheiro=..., POST /gerar-faixas, POST /gerar-faixa ou POST /listar-playlist-youtube"})

    def _escrever_texto(self, parsed):
        params = parse_qs(parsed.query)
        ficheiro = (params.get('ficheiro') or [''])[0]
        if ficheiro not in FICHEIROS_PERMITIDOS:
            self._enviar_json(403, {"erro": f"ficheiro não permitido: {ficheiro!r} — só {sorted(FICHEIROS_PERMITIDOS)}"})
            return

        tamanho = int(self.headers.get('Content-Length') or 0)
        if tamanho <= 0:
            self._enviar_json(400, {"erro": "corpo vazio"})
            return
        corpo = self.rfile.read(tamanho).decode('utf-8')

        if ficheiro.endswith('.json'):
            try:
                json.loads(corpo)
            except json.JSONDecodeError as e:
                self._enviar_json(400, {"erro": f"JSON inválido, não escrevi nada: {e}"})
                return

        caminho = os.path.join(APP_DIR, ficheiro)
        caminho_tmp = caminho + '.tmp'
        try:
            with open(caminho_tmp, 'w', encoding='utf-8') as f:
                f.write(corpo)
            os.replace(caminho_tmp, caminho)
        except Exception as e:
            self._enviar_json(500, {"erro": f"falha a escrever: {e}"})
            return

        self._enviar_json(200, {"ok": True, "ficheiro": ficheiro, "bytes": len(corpo)})

    def _upload_binario(self, parsed):
        params = parse_qs(parsed.query)
        ficheiro = (params.get('ficheiro') or [''])[0]
        if not NOME_UPLOAD_REGEX.match(ficheiro):
            self._enviar_json(403, {"erro": f"nome não permitido para upload: {ficheiro!r} — só concorrente_1..4.(jpg|jpeg|png)"})
            return

        tamanho = int(self.headers.get('Content-Length') or 0)
        if tamanho <= 0:
            self._enviar_json(400, {"erro": "corpo vazio"})
            return
        if tamanho > UPLOAD_MAX_BYTES:
            self._enviar_json(400, {"erro": f"ficheiro demasiado grande (máx. {UPLOAD_MAX_BYTES // (1024*1024)}MB)"})
            return
        corpo = self.rfile.read(tamanho)

        # os.replace substitui atomicamente — um novo upload para o mesmo
        # concorrente_N.ext apaga/troca a foto anterior, nunca acumula.
        caminho = os.path.join(APP_DIR, ficheiro)
        caminho_tmp = caminho + '.tmp'
        try:
            with open(caminho_tmp, 'wb') as f:
                f.write(corpo)
            os.replace(caminho_tmp, caminho)
        except Exception as e:
            self._enviar_json(500, {"erro": f"falha a escrever: {e}"})
            return

        self._enviar_json(200, {"ok": True, "ficheiro": ficheiro, "bytes": len(corpo)})

    def _gerar_faixas_ia(self):
        if not ANTHROPIC_API_KEY:
            self._enviar_json(500, {"erro": "ANTHROPIC_API_KEY não está definida no ambiente deste servidor — exporta-a antes de correr iniciar_editor.command (ex.: export ANTHROPIC_API_KEY=sk-ant-...)"})
            return

        tamanho = int(self.headers.get('Content-Length') or 0)
        if tamanho <= 0 or tamanho > GERAR_FAIXAS_MAX_PROMPT * 4:
            self._enviar_json(400, {"erro": "corpo vazio ou demasiado grande"})
            return
        try:
            pedido = json.loads(self.rfile.read(tamanho).decode('utf-8'))
        except json.JSONDecodeError as e:
            self._enviar_json(400, {"erro": f"JSON inválido no corpo do pedido: {e}"})
            return

        prompt = (pedido.get('prompt') or '').strip()
        if not prompt:
            self._enviar_json(400, {"erro": "falta o campo 'prompt' no corpo do pedido"})
            return
        if len(prompt) > GERAR_FAIXAS_MAX_PROMPT:
            self._enviar_json(400, {"erro": f"prompt demasiado longo (máx. {GERAR_FAIXAS_MAX_PROMPT} caracteres)"})
            return

        corpo_anthropic = json.dumps({
            "model": ANTHROPIC_MODEL,
            "max_tokens": 2000,
            "system": (
                "Respondes sempre apenas com um único objecto JSON válido, sem "
                "markdown, sem crases, sem comentários e sem texto antes ou "
                "depois do JSON."
            ),
            "output_config": {"effort": "medium"},
            "messages": [{"role": "user", "content": prompt}],
        }).encode('utf-8')

        req = urllib.request.Request(
            ANTHROPIC_URL,
            data=corpo_anthropic,
            method='POST',
            headers={
                'x-api-key': ANTHROPIC_API_KEY,
                'anthropic-version': ANTHROPIC_VERSION,
                'content-type': 'application/json',
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=GERAR_FAIXAS_TIMEOUT) as resp:
                resposta = json.loads(resp.read().decode('utf-8'))
        except urllib.error.HTTPError as e:
            detalhe = e.read().decode('utf-8', errors='replace')
            self._enviar_json(502, {"erro": f"API Anthropic devolveu {e.code}: {detalhe[:500]}"})
            return
        except urllib.error.URLError as e:
            self._enviar_json(502, {"erro": f"falha de rede a chamar a API Anthropic: {e}"})
            return
        except Exception as e:
            self._enviar_json(500, {"erro": f"erro inesperado a chamar a API Anthropic: {e}"})
            return

        if resposta.get('stop_reason') == 'refusal':
            self._enviar_json(502, {"erro": "a API recusou o pedido (stop_reason=refusal) — tenta reformular a música semente ou os critérios"})
            return

        texto = ''
        for bloco in resposta.get('content') or []:
            if bloco.get('type') == 'text':
                texto += bloco.get('text', '')
        texto = texto.strip()

        resultado = None
        try:
            resultado = json.loads(texto)
        except json.JSONDecodeError:
            inicio, fim = texto.find('{'), texto.rfind('}')
            if inicio != -1 and fim > inicio:
                try:
                    resultado = json.loads(texto[inicio:fim + 1])
                except json.JSONDecodeError:
                    pass

        if resultado is None:
            self._enviar_json(502, {"erro": "a resposta da IA não continha JSON válido", "bruto": texto[:800]})
            return

        self._enviar_json(200, {"ok": True, "resultado": resultado})

    def _gerar_faixa(self):
        tamanho = int(self.headers.get('Content-Length') or 0)
        if tamanho <= 0 or tamanho > 4000:
            self._enviar_json(400, {"erro": "corpo vazio ou demasiado grande"})
            return
        try:
            pedido = json.loads(self.rfile.read(tamanho).decode('utf-8'))
        except json.JSONDecodeError as e:
            self._enviar_json(400, {"erro": f"JSON inválido no corpo do pedido: {e}"})
            return

        url = (pedido.get('url') or '').strip()
        id_faixa = (pedido.get('id') or '').strip()
        artista = (pedido.get('artista') or '').strip()
        titulo = (pedido.get('titulo') or pedido.get('title') or '').strip()

        if not id_faixa:
            self._enviar_json(400, {"erro": "falta o 'id' no corpo do pedido"})
            return
        if not ID_FAIXA_REGEX.match(id_faixa):
            self._enviar_json(400, {"erro": f"id inválido: {id_faixa!r} — só letras, números e underscore"})
            return

        if not url:
            if not artista and not titulo:
                self._enviar_json(400, {"erro": "faltam 'url' ou 'artista'+'titulo' no corpo do pedido"})
                return

            if artista and titulo:
                # Modo iTunes primeiro — procura o preview oficial de 30s
                # (mais rápido, sem risco de "Sign in to confirm" do
                # YouTube). Só cai para a pesquisa no YouTube abaixo se a
                # iTunes não tiver preview para esta música, ou se o
                # subprocesso demorar demasiado.
                try:
                    resultado_itunes = subprocess.run(
                        [sys.executable, GERAR_FAIXA_SCRIPT, '--itunes',
                         '--artista', artista, '--titulo', titulo, id_faixa, '--force'],
                        cwd=APP_DIR, capture_output=True, text=True, timeout=GERAR_FAIXA_ITUNES_TIMEOUT,
                    )
                except subprocess.TimeoutExpired:
                    resultado_itunes = None
                except Exception:
                    resultado_itunes = None

                if resultado_itunes is not None and resultado_itunes.returncode == 0:
                    ficheiro_a = f'{id_faixa}_a.mp3'
                    ficheiro_b = f'{id_faixa}_b.mp3'
                    if os.path.exists(os.path.join(APP_DIR, ficheiro_a)) and os.path.exists(os.path.join(APP_DIR, ficheiro_b)):
                        self._enviar_json(200, {"ok": True, "ficheiro_a": ficheiro_a, "ficheiro_b": ficheiro_b, "fonte": "itunes"})
                        return
                    # ficheiros não apareceram apesar do returncode 0 — cai para YouTube também

            # Fallback: pesquisa no YouTube (sem preview iTunes disponível,
            # ou só veio 'artista' ou só 'titulo').
            consulta = ' '.join(p for p in (artista, titulo) if p)
            try:
                pesquisa = subprocess.run(
                    ['yt-dlp', f'ytsearch1:{consulta}', '--get-url', '--no-playlist'],
                    cwd=APP_DIR, capture_output=True, text=True, timeout=YT_SEARCH_TIMEOUT,
                )
            except subprocess.TimeoutExpired:
                self._enviar_json(504, {"erro": f"pesquisa no YouTube excedeu {YT_SEARCH_TIMEOUT}s para {consulta!r}"})
                return
            except Exception as e:
                self._enviar_json(500, {"erro": f"falha a correr yt-dlp para pesquisar {consulta!r}: {e}"})
                return
            if pesquisa.returncode != 0 or not pesquisa.stdout.strip():
                detalhe = (pesquisa.stderr or pesquisa.stdout or '').strip()
                self._enviar_json(500, {"erro": f"yt-dlp não encontrou resultados para {consulta!r}: {detalhe[-500:]}"})
                return
            url = pesquisa.stdout.strip().splitlines()[0].strip()

        # limpar URL — remover parâmetros de playlist
        from urllib.parse import urlparse, parse_qs
        _p = urlparse(url)
        _v = parse_qs(_p.query).get('v')
        if _v:
            url = f'https://www.youtube.com/watch?v={_v[0]}'
        if not url:
            self._enviar_json(400, {"erro": "não foi possível obter um url válido"})
            return

        try:
            resultado = subprocess.run(
                [sys.executable, GERAR_FAIXA_SCRIPT, url, id_faixa, '--force'],
                cwd=APP_DIR, capture_output=True, text=True, timeout=GERAR_FAIXA_TIMEOUT,
            )
        except subprocess.TimeoutExpired:
            self._enviar_json(504, {"erro": f"gerar_faixa.py excedeu {GERAR_FAIXA_TIMEOUT}s — download/corte demorou demasiado"})
            return
        except Exception as e:
            self._enviar_json(500, {"erro": f"falha a correr gerar_faixa.py: {e}"})
            return

        if resultado.returncode != 0:
            detalhe = (resultado.stderr or resultado.stdout or '').strip()
            self._enviar_json(500, {"erro": f"gerar_faixa.py falhou: {detalhe[-800:]}"})
            return

        ficheiro_a = f'{id_faixa}_a.mp3'
        ficheiro_b = f'{id_faixa}_b.mp3'
        if not os.path.exists(os.path.join(APP_DIR, ficheiro_a)) or not os.path.exists(os.path.join(APP_DIR, ficheiro_b)):
            self._enviar_json(500, {"erro": "gerar_faixa.py terminou sem erro mas os ficheiros não apareceram em app/"})
            return

        self._enviar_json(200, {"ok": True, "ficheiro_a": ficheiro_a, "ficheiro_b": ficheiro_b, "fonte": "youtube"})

    def _listar_playlist_youtube(self):
        tamanho = int(self.headers.get('Content-Length') or 0)
        if tamanho <= 0 or tamanho > 2000:
            self._enviar_json(400, {"erro": "corpo vazio ou demasiado grande"})
            return
        try:
            pedido = json.loads(self.rfile.read(tamanho).decode('utf-8'))
        except json.JSONDecodeError as e:
            self._enviar_json(400, {"erro": f"JSON inválido no corpo do pedido: {e}"})
            return

        url = (pedido.get('url') or '').strip()
        if not url or not YOUTUBE_URL_REGEX.match(url):
            self._enviar_json(400, {"erro": "url inválido — só URLs do youtube.com/youtu.be/music.youtube.com"})
            return

        try:
            resultado = subprocess.run(
                ['yt-dlp', '--flat-playlist', '--playlist-end', str(LISTAR_PLAYLIST_MAX_FAIXAS),
                 '--print', '%(title)s|||%(uploader)s', url],
                capture_output=True, text=True, timeout=LISTAR_PLAYLIST_TIMEOUT,
            )
        except subprocess.TimeoutExpired:
            self._enviar_json(504, {"erro": f"leitura da playlist excedeu {LISTAR_PLAYLIST_TIMEOUT}s"})
            return
        except Exception as e:
            self._enviar_json(500, {"erro": f"falha a correr yt-dlp: {e}"})
            return

        if resultado.returncode != 0:
            detalhe = (resultado.stderr or resultado.stdout or '').strip()
            self._enviar_json(500, {"erro": f"yt-dlp não conseguiu ler essa playlist: {detalhe[-500:]}"})
            return

        faixas = []
        for linha in resultado.stdout.splitlines():
            linha = linha.strip()
            if not linha:
                continue
            partes = linha.split('|||', 1)
            titulo = partes[0].strip()
            uploader = partes[1].strip() if len(partes) > 1 else ''
            if titulo and titulo != 'NA':
                faixas.append({"titulo": titulo, "uploader": '' if uploader == 'NA' else uploader})

        if not faixas:
            self._enviar_json(404, {"erro": "não encontrei nenhum vídeo nessa playlist (privada, vazia, ou url inválido)"})
            return

        self._enviar_json(200, {"ok": True, "faixas": faixas})


def main():
    servidor = ThreadingHTTPServer(('localhost', PORTA), Handler)
    print(f"_servidor_escrita.py a correr em http://localhost:{PORTA} (Ctrl+C para parar)")
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()
