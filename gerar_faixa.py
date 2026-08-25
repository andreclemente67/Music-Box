#!/usr/bin/env python3
"""
MUSIC BOX — Gerar Faixa a partir do YouTube
Versão genérica e parametrizada de final_b*.sh / gerar_trechos_b_yt.sh
(que tinham a lista de URL+offset+destino fixa dentro do próprio script).

Dado um URL do YouTube e um ID de faixa, faz tudo o que hoje é feito à mão
faixa a faixa:
  1. Descarrega o MP3 completo via yt-dlp (mesma receita de final_b*.sh:
     -x --audio-format mp3 --audio-quality 0).
  2. Corre sugerir_trechos.py (importado como módulo, não por subprocess —
     mesma lógica validada de volumedetect/ffmpeg, sem reimplementar nada)
     sobre o MP3 completo para obter os timestamps de Trecho A e B.
  3. Corta os dois trechos de 15s com ffmpeg -c copy (mesma receita de
     final_b*.sh/gerar_trechos_b_yt.sh).
  4. Guarda como <id>_a.mp3 e <id>_b.mp3 em app/.

Uso:
  python3 gerar_faixa.py <url_youtube> <id_faixa>
  python3 gerar_faixa.py "https://www.youtube.com/watch?v=djV11Xbc914" syn_01
  python3 gerar_faixa.py --force ... syn_01   # sobrescreve <id>_a/_b.mp3 se já existirem
  python3 gerar_faixa.py --cookies-from-browser ... syn_01   # passa --cookies-from-browser chrome ao yt-dlp

Se o yt-dlp falhar com "Sign in to confirm..." (o YouTube a pedir prova de
que não é um bot), o download é repetido automaticamente com
--cookies-from-browser chrome, mesmo sem a flag acima — não é preciso
saber de antemão que um vídeo vai precisar disto.

Ao contrário de final_b*.sh (que descarrega o áudio completo e apaga a
seguir), este script mantém o download completo em tmp_dl/ só durante a
execução — precisa dele inteiro para o sugerir_trechos.py poder analisar a
faixa toda antes de decidir onde cortar A e B.

Modo iTunes (--itunes):
  python3 gerar_faixa.py --itunes --artista "Queen" --titulo "Bohemian Rhapsody" boh_01
  python3 gerar_faixa.py --itunes --artista "..." --titulo "..." --force id_faixa

Alternativa ao modo YouTube acima: procura ARTISTA+TITULO na iTunes Search
API (https://itunes.apple.com/search), descarrega directamente o excerto
de 30s que a Apple já disponibiliza (`previewUrl`) e corta sempre
0-12s (Trecho A) e 18-30s (Trecho B) desse excerto — sem yt-dlp, sem
sugerir_trechos.py/análise de volume (o preview da Apple já é o trecho
mais reconhecível da música, escolhido por eles). Muito mais rápido e sem
o risco de "Sign in to confirm" do YouTube; só falha se a iTunes Search
API não tiver nenhum resultado com preview para essa pesquisa.
"""
import argparse
import glob
import json
import os
import re
import shutil
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request

APP_DIR = os.path.dirname(os.path.abspath(__file__))
TMP_DIR = os.path.join(APP_DIR, 'tmp_dl')
DURACAO_TRECHO = 15
ID_REGEX = re.compile(r'^[A-Za-z0-9_]+$')

# ── Modo iTunes ───────────────────────────────────────────────────────────
ITUNES_SEARCH_URL = 'https://itunes.apple.com/search'
ITUNES_TIMEOUT = 15  # segundos — pesquisa + download do preview (ficheiro pequeno, ~500KB-1MB)
ITUNES_TRECHO_A = (0, 12)   # (início, fim) em segundos dentro do preview de 30s
ITUNES_TRECHO_B = (18, 30)

# sugerir_trechos.py vive na mesma pasta — importar directamente em vez de
# invocar por subprocess evita reimplementar/parsear o "TEMPO_A=.../TEMPO_B=..."
# que o __main__ desse script imprime, e reutiliza a função tal como está.
sys.path.insert(0, APP_DIR)
import sugerir_trechos  # noqa: E402


def descarregar_mp3_completo(url: str, id_faixa: str, cookies_from_browser: bool = False) -> str:
    """Descarrega o áudio completo do YouTube para tmp_dl/ como MP3.
    Devolve o caminho do ficheiro descarregado, ou lança RuntimeError.

    Se `cookies_from_browser` for False e o yt-dlp falhar com "Sign in to
    confirm" (o YouTube a pedir prova de que não é um bot — comum em
    vídeos com restrição de idade ou picos de tráfego automatizado),
    tenta uma segunda vez com --cookies-from-browser chrome antes de
    desistir."""
    os.makedirs(TMP_DIR, exist_ok=True)
    base = os.path.join(TMP_DIR, f'{id_faixa}_full')

    def _correr_yt_dlp(com_cookies: bool):
        comando = ['yt-dlp', '--force-overwrites', '-x', '--audio-format', 'mp3', '--audio-quality', '0', '--remote-components', 'ejs:github']
        if com_cookies:
            comando += ['--cookies-from-browser', 'chrome']
        comando += ['-o', f'{base}.%(ext)s', url]
        return subprocess.run(comando, capture_output=True, text=True)

    resultado = _correr_yt_dlp(cookies_from_browser)
    if resultado.returncode != 0 and not cookies_from_browser:
        print('      ⚠ YouTube pediu confirmação de sessão — a tentar novamente com --cookies-from-browser chrome ...')
        resultado = _correr_yt_dlp(True)

    if resultado.returncode != 0:
        raise RuntimeError(f'yt-dlp falhou:\n{resultado.stderr.strip()}')

    encontrados = glob.glob(f'{base}.*')
    if not encontrados:
        raise RuntimeError('yt-dlp terminou sem erro mas não produziu nenhum ficheiro')
    return encontrados[0]


def cortar_trecho(origem: str, inicio: int, destino: str) -> None:
    """Corta DURACAO_TRECHO segundos de `origem` a partir de `inicio`
    (segundos) para `destino`, com -c copy (mesma receita dos scripts
    existentes — sem reencodar)."""
    resultado = subprocess.run(
        [
            'ffmpeg', '-y', '-i', origem,
            '-ss', str(inicio), '-t', str(DURACAO_TRECHO), '-c', 'copy',
            destino,
        ],
        capture_output=True, text=True,
    )
    if resultado.returncode != 0:
        raise RuntimeError(f'ffmpeg falhou a cortar {destino}:\n{resultado.stderr.strip()}')


def procurar_preview_itunes(artista: str, titulo: str) -> str:
    """Procura ARTISTA+TITULO na iTunes Search API e devolve o `previewUrl`
    (excerto de 30s, AAC/M4A) do primeiro resultado que tenha preview.
    Lança RuntimeError se a pesquisa falhar ou não houver nenhum preview."""
    termo = ' '.join(p for p in (artista, titulo) if p).strip()
    if not termo:
        raise ValueError('artista/título vazios — nada para procurar na iTunes')

    query = urllib.parse.urlencode({'term': termo, 'media': 'music', 'entity': 'song', 'limit': 5})
    pedido = urllib.request.Request(f'{ITUNES_SEARCH_URL}?{query}', headers={'User-Agent': 'MusicBox/1.0'})
    try:
        with urllib.request.urlopen(pedido, timeout=ITUNES_TIMEOUT) as resp:
            dados = json.loads(resp.read().decode('utf-8'))
    except (urllib.error.URLError, json.JSONDecodeError) as e:
        raise RuntimeError(f'falha a consultar a iTunes Search API para {termo!r}: {e}')

    for resultado in dados.get('results', []):
        preview = resultado.get('previewUrl')
        if preview:
            return preview
    raise RuntimeError(f'iTunes não devolveu nenhum preview para {termo!r} ({dados.get("resultCount", 0)} resultado(s) sem previewUrl)')


def descarregar_preview_itunes(preview_url: str, id_faixa: str) -> str:
    """Descarrega o excerto de 30s devolvido pela iTunes Search API para
    tmp_dl/. Devolve o caminho local, ou lança RuntimeError."""
    os.makedirs(TMP_DIR, exist_ok=True)
    extensao = os.path.splitext(urllib.parse.urlparse(preview_url).path)[1] or '.m4a'
    destino = os.path.join(TMP_DIR, f'{id_faixa}_preview{extensao}')
    pedido = urllib.request.Request(preview_url, headers={'User-Agent': 'MusicBox/1.0'})
    try:
        with urllib.request.urlopen(pedido, timeout=ITUNES_TIMEOUT) as resp, open(destino, 'wb') as f:
            shutil.copyfileobj(resp, f)
    except urllib.error.URLError as e:
        raise RuntimeError(f'falha a descarregar o preview da iTunes: {e}')
    return destino


def cortar_trecho_itunes(origem: str, inicio: int, fim: int, destino: str) -> None:
    """Corta de `origem` (preview m4a/aac da iTunes) o intervalo
    [inicio, fim) segundos, reencodando para mp3 em `destino`. Ao contrário
    de cortar_trecho() (fonte já em mp3, -c copy sem reencodar), aqui a
    fonte é m4a/aac — não dá para copiar o stream directamente para mp3."""
    resultado = subprocess.run(
        [
            'ffmpeg', '-y', '-i', origem,
            '-ss', str(inicio), '-t', str(fim - inicio),
            '-acodec', 'libmp3lame', '-q:a', '2',
            destino,
        ],
        capture_output=True, text=True,
    )
    if resultado.returncode != 0:
        raise RuntimeError(f'ffmpeg falhou a cortar {destino}:\n{resultado.stderr.strip()}')


def gerar_faixa_itunes(artista: str, titulo: str, id_faixa: str, force: bool = False) -> None:
    """Gera <id>_a.mp3/<id>_b.mp3 a partir do excerto de 30s da iTunes
    Search API para ARTISTA+TITULO — ver docstring do módulo ("Modo
    iTunes") para os detalhes e porquê dos cortes fixos 0-12s/18-30s."""
    if not ID_REGEX.match(id_faixa):
        raise ValueError(f'ID de faixa inválido: {id_faixa!r} — só letras, números e underscore')

    destino_a = os.path.join(APP_DIR, f'{id_faixa}_a.mp3')
    destino_b = os.path.join(APP_DIR, f'{id_faixa}_b.mp3')
    if not force:
        existentes = [d for d in (destino_a, destino_b) if os.path.exists(d)]
        if existentes:
            nomes = ', '.join(os.path.basename(d) for d in existentes)
            raise FileExistsError(f'já existe(m): {nomes} — usa --force para sobrescrever')

    print(f'[1/3] A procurar "{artista} - {titulo}" na iTunes Search API ...')
    preview_url = procurar_preview_itunes(artista, titulo)
    print(f'      ✓ preview encontrado')

    try:
        print('[2/3] A descarregar o excerto de 30s ...')
        preview_local = descarregar_preview_itunes(preview_url, id_faixa)
        print(f'      ✓ {os.path.basename(preview_local)}')

        print('[3/3] A cortar Trecho A (0-12s) e Trecho B (18-30s) com ffmpeg ...')
        cortar_trecho_itunes(preview_local, *ITUNES_TRECHO_A, destino_a)
        print(f'      ✓ {os.path.basename(destino_a)}')
        cortar_trecho_itunes(preview_local, *ITUNES_TRECHO_B, destino_b)
        print(f'      ✓ {os.path.basename(destino_b)}')
    finally:
        shutil.rmtree(TMP_DIR, ignore_errors=True)

    print(f'CONCLUÍDO — {id_faixa}_a.mp3 e {id_faixa}_b.mp3 em {APP_DIR} (fonte: iTunes preview)')


def gerar_faixa(url: str, id_faixa: str, force: bool = False, cookies_from_browser: bool = False) -> None:
    if not ID_REGEX.match(id_faixa):
        raise ValueError(f'ID de faixa inválido: {id_faixa!r} — só letras, números e underscore')

    destino_a = os.path.join(APP_DIR, f'{id_faixa}_a.mp3')
    destino_b = os.path.join(APP_DIR, f'{id_faixa}_b.mp3')
    if not force:
        existentes = [d for d in (destino_a, destino_b) if os.path.exists(d)]
        if existentes:
            nomes = ', '.join(os.path.basename(d) for d in existentes)
            raise FileExistsError(f'já existe(m): {nomes} — usa --force para sobrescrever')

    print(f'[1/3] A descarregar áudio completo de {url} ...')
    mp3_completo = descarregar_mp3_completo(url, id_faixa, cookies_from_browser)
    print(f'      ✓ {os.path.basename(mp3_completo)}')

    try:
        print('[2/3] A analisar volume para sugerir Trecho A e B (sugerir_trechos.py) ...')
        tempo_a, tempo_b = sugerir_trechos.sugerir_trechos(mp3_completo, DURACAO_TRECHO)
        print(f'      ✓ Trecho A → {tempo_a}s · Trecho B → {tempo_b}s')

        print('[3/3] A cortar os trechos com ffmpeg ...')
        cortar_trecho(mp3_completo, tempo_a, destino_a)
        print(f'      ✓ {os.path.basename(destino_a)}')
        cortar_trecho(mp3_completo, tempo_b, destino_b)
        print(f'      ✓ {os.path.basename(destino_b)}')
    finally:
        # O download completo só serve para a análise + corte — não fica
        # em app/ (ao contrário de destino_a/destino_b, que são o resultado).
        shutil.rmtree(TMP_DIR, ignore_errors=True)

    print(f'CONCLUÍDO — {id_faixa}_a.mp3 e {id_faixa}_b.mp3 em {APP_DIR}')


def main():
    parser = argparse.ArgumentParser(
        description='Descarrega uma música do YouTube e gera automaticamente os trechos A e B da faixa.',
    )
    parser.add_argument('url', nargs='?', default='', help='URL do vídeo do YouTube (omite se usares --itunes)')
    parser.add_argument('id_faixa', help='ID da faixa (ex.: syn_01) — nomeia os ficheiros <id>_a.mp3 / <id>_b.mp3')
    parser.add_argument('--force', action='store_true', help='sobrescreve <id>_a.mp3/<id>_b.mp3 se já existirem')
    parser.add_argument('--cookies-from-browser', action='store_true',
                         help='passa --cookies-from-browser chrome ao yt-dlp (também é tentado automaticamente se o yt-dlp falhar com "Sign in to confirm")')
    parser.add_argument('--itunes', action='store_true',
                         help='gera a partir do preview de 30s da iTunes Search API (--artista + --titulo, sem URL do YouTube) — corta sempre 0-12s/18-30s')
    parser.add_argument('--artista', default='', help='artista — obrigatório com --itunes')
    parser.add_argument('--titulo', default='', help='título da música — obrigatório com --itunes')
    args = parser.parse_args()

    try:
        if args.itunes:
            if not args.artista or not args.titulo:
                raise ValueError('--itunes exige --artista e --titulo')
            gerar_faixa_itunes(args.artista, args.titulo, args.id_faixa, force=args.force)
        else:
            if not args.url:
                raise ValueError('falta o url do YouTube (ou usa --itunes --artista ... --titulo ...)')
            gerar_faixa(args.url, args.id_faixa, force=args.force, cookies_from_browser=args.cookies_from_browser)
    except Exception as e:
        print(f'FALHOU: {e}', file=sys.stderr)
        shutil.rmtree(TMP_DIR, ignore_errors=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
