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
     ou: {"artista": "...", "titulo": "...", "id": "syn_01"}  (sem url —
         procura-se automaticamente no YouTube via yt-dlp ytsearch1)
  -> 200 {"ok": true, "ficheiro_a": "syn_01_a.mp3", "ficheiro_b": "syn_01_b.mp3"}
  -> 400/500/504 {"erro": "..."}
  Usado pelo botão "⬇ Gerar trechos" na Mesa de Montagem (só aparece em
  faixas com estado 'rascunho', sem áudio). Se o pedido não trouxer 'url',
  usa 'artista'+'titulo' (ou 'title') para construir uma pesquisa
  "ytsearch1:ARTISTA TITULO" e obtém o primeiro resultado com
  `yt-dlp --get-url --no-playlist` antes de continuar. Corre gerar_faixa.py
  <url> <id> --force como subprocesso (download via yt-dlp +
  sugerir_trechos.py + corte via ffmpeg — ver esse ficheiro). Só devolve os
  nomes dos ficheiros gerados; NÃO escreve em catalogo.json — quem
  actualiza a faixa é o cliente (mesmo padrão de
  updateClipField()/detectarMomentoClip() no Studio: fica em
  CATALOGO_PATCH, só entra em catalogo_patch.json quando se clica
  "Guardar", nunca escreve catalogo.json directamente).

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
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs, unquote

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
ID_FAIXA_REGEX = re.compile(r'^[A-Za-z0-9_]+$')

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
        caminho_pedido = unquote(urlparse(self.path).path)
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

        self._enviar_json(200, {"ok": True, "ficheiro_a": ficheiro_a, "ficheiro_b": ficheiro_b})

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
