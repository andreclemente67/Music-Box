#!/usr/bin/env python3
"""Estudo "Trecho B = expoente da música" — playlist STD.INT.00.MIX.001
(9-11 Out 2026, pedido do André). REGRA ABSOLUTA: nunca escreve em
<id>_a.mp3/<id>_b.mp3 de produção nem em catalogo.json — tudo isolado em
estudos/trecho_b_expoente/.

Para cada faixa, 4 candidatos a Trecho B (15s):
  A) alinhar o preview iTunes de 30s na faixa completa (fpcalc/Hamming).
  B) auto-semelhança de chroma + energia (repetição = refrão provável).
  C) letras sincronizadas LRCLIB — linha mais repetida.
  D) controlo — método actual (sugerir_trechos.py, pico de volume).

Gera previews com nomes anónimos B1-B4 (ordem aleatória por faixa) em
estudos/trecho_b_expoente/audio/, e guarda a chave método↔ficheiro em
estudos/trecho_b_expoente/dados/chave_<id>.json (NÃO publicado na página
de teste). Ritmo lento no YouTube (pausa entre pedidos), sem
--cookies-from-browser (sem login) — se um pedido for bloqueado, fica
para retomar depois, nunca força sessão.

Uso: scripts/.venv/bin/python3 estudos/trecho_b_expoente/analisar.py
"""
import json
import os
import random
import re
import subprocess
import sys
import time
import urllib.parse
import urllib.request

APP_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ESTUDO_DIR = os.path.dirname(os.path.abspath(__file__))
AUDIO_DIR = os.path.join(ESTUDO_DIR, 'audio')
CACHE_DIR = os.path.join(ESTUDO_DIR, 'cache')
DADOS_DIR = os.path.join(ESTUDO_DIR, 'dados')
PROGRESSO_PATH = os.path.join(DADOS_DIR, 'progresso.json')

sys.path.insert(0, APP_DIR)
sys.path.insert(0, os.path.join(APP_DIR, 'scripts'))
import gerar_faixa  # noqa: E402
import verificar_trechos as vt  # noqa: E402
import sugerir_trechos  # noqa: E402

import numpy as np  # noqa: E402
from scipy.signal import stft  # noqa: E402

PAUSA_ENTRE_PEDIDOS = 4  # segundos — "ritmo lento" pedido, sem bater o YouTube

FAIXAS = [
    {'id': 'dec00_01', 'titulo': 'Hey Ya!', 'artista': 'OutKast',
     'url': 'https://www.youtube.com/watch?v=-7XnDlYY9qw'},
    {'id': 'dec00_02', 'titulo': 'Crazy in Love', 'artista': 'Beyoncé',
     'url': 'https://www.youtube.com/watch?v=KmJI1JqF-dU'},
    {'id': 'dec00_03', 'titulo': 'Mr. Brightside', 'artista': 'The Killers',
     'url': 'https://www.youtube.com/watch?v=l7MaKmKJqoc'},
    {'id': 'dec00_04', 'titulo': 'Seven Nation Army', 'artista': 'The White Stripes',
     'url': 'https://www.youtube.com/watch?v=CBEJo18auXE'},
    {'id': 'dec00_05', 'titulo': 'Toxic', 'artista': 'Britney Spears',
     'url': 'https://www.youtube.com/watch?v=7l1A2gShWZo'},
    {'id': 'dec00_06', 'titulo': 'In the End', 'artista': 'Linkin Park',
     'url': 'https://www.youtube.com/watch?v=gB9P0kpc1O4'},
    {'id': 'dec00_07', 'titulo': 'Umbrella', 'artista': 'Rihanna',
     'url': 'https://www.youtube.com/watch?v=EPtrQpx9VDw'},
]

for d in (AUDIO_DIR, CACHE_DIR, DADOS_DIR):
    os.makedirs(d, exist_ok=True)


def carregar_progresso():
    if os.path.exists(PROGRESSO_PATH):
        with open(PROGRESSO_PATH, encoding='utf-8') as f:
            return json.load(f)
    return {}


def gravar_progresso(p):
    with open(PROGRESSO_PATH, 'w', encoding='utf-8') as f:
        json.dump(p, f, ensure_ascii=False, indent=2)


def baixar_sem_login(url, destino_sem_ext):
    """yt-dlp, 1 só tentativa, NUNCA --cookies-from-browser (sem login,
    pedido explícito). Se falhar (ex. bloqueio anti-bot), propaga o erro —
    fica para retomar mais tarde, nunca força sessão."""
    comando = ['yt-dlp', '-x', '--audio-format', 'mp3', '--audio-quality', '0',
               '--remote-components', 'ejs:github', '-o', f'{destino_sem_ext}.%(ext)s', url]
    r = subprocess.run(comando, capture_output=True, text=True, timeout=180)
    if r.returncode != 0:
        raise RuntimeError((r.stderr or r.stdout or 'yt-dlp falhou')[-400:])
    caminho = f'{destino_sem_ext}.mp3'
    if not os.path.exists(caminho):
        raise RuntimeError('yt-dlp terminou sem erro mas o ficheiro não apareceu')
    return caminho


def obter_fonte_completa(tid, url):
    destino = os.path.join(CACHE_DIR, tid)
    caminho = f'{destino}.mp3'
    if os.path.exists(caminho):
        return caminho
    caminho = baixar_sem_login(url, destino)
    time.sleep(PAUSA_ENTRE_PEDIDOS)
    return caminho


# ───────────────────────── Método D (controlo) ─────────────────────────

def metodo_d_controlo(caminho_fonte):
    _, tempo_b = sugerir_trechos.sugerir_trechos(caminho_fonte, 15)
    return tempo_b, 'pico de volume após Trecho A (sugerir_trechos.py, método actual)'


# ───────────────────────── Método A (iTunes) ─────────────────────────

def metodo_a_itunes(tid, artista, titulo, caminho_fonte):
    preview_url = gerar_faixa.procurar_preview_itunes(artista, titulo)
    preview_local = gerar_faixa.descarregar_preview_itunes(preview_url, f'{tid}_estudo')
    time.sleep(PAUSA_ENTRE_PEDIDOS)
    try:
        preview_mp3 = os.path.join(CACHE_DIR, f'{tid}_itunes_preview.mp3')
        subprocess.run(['ffmpeg', '-y', '-i', preview_local, '-acodec', 'libmp3lame', '-q:a', '2', preview_mp3],
                        capture_output=True, text=True, timeout=30, check=True)
    finally:
        if os.path.exists(preview_local):
            os.remove(preview_local)

    dur_fonte, fp_fonte = vt.fingerprint_fpcalc(caminho_fonte, fonte_completa=True)
    dur_prev, fp_prev = vt.fingerprint_fpcalc(preview_mp3)
    idx, confianca = vt.localizar_trecho(fp_prev, fp_fonte)
    if idx is None:
        raise RuntimeError('preview iTunes maior que a fonte — não foi possível alinhar')
    seg_por_item = dur_fonte / len(fp_fonte)
    offset = idx * seg_por_item
    return round(offset, 1), f'alinhamento do preview iTunes de 30s (confiança={confianca:.2f})'


# ─────────────── Método B (chroma, auto-semelhança + energia) ───────────────

NOTAS = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']


def _carregar_pcm(caminho, sr=11025):
    r = subprocess.run(['ffmpeg', '-v', 'error', '-i', caminho, '-ac', '1', '-ar', str(sr), '-f', 'f32le', '-'],
                        capture_output=True, timeout=60)
    return np.frombuffer(r.stdout, dtype=np.float32), sr


def _chromagrama(pcm, sr, hop_s=0.5, win_s=2.0):
    nper = int(win_s * sr)
    nhop = int(hop_s * sr)
    f, t, Z = stft(pcm, fs=sr, nperseg=nper, noverlap=nper - nhop, boundary=None)
    mag = np.abs(Z)  # (freq, tempo)
    chroma = np.zeros((12, mag.shape[1]))
    # mapeia cada bin de frequência para a classe de altura mais próxima (A4=440Hz)
    with np.errstate(divide='ignore'):
        midi = 69 + 12 * np.log2(np.maximum(f, 1e-6) / 440.0)
    classes = np.round(midi).astype(int) % 12
    for c in range(12):
        sel = classes == c
        if sel.any():
            chroma[c] = mag[sel].sum(axis=0)
    norma = np.linalg.norm(chroma, axis=0, keepdims=True)
    norma[norma == 0] = 1
    chroma = chroma / norma
    rms = np.sqrt(np.mean(np.lib.stride_tricks.sliding_window_view(pcm, nper)[::nhop] ** 2, axis=1)) \
        if len(pcm) >= nper else np.zeros(mag.shape[1])
    n = min(chroma.shape[1], len(rms))
    return chroma[:, :n], rms[:n], hop_s


def metodo_b_chroma(caminho_fonte):
    pcm, sr = _carregar_pcm(caminho_fonte)
    chroma, rms, hop_s = _chromagrama(pcm, sr)
    n = chroma.shape[1]
    min_dist_frames = int(20 / hop_s)  # só compara repetições a >=20s de distância
    melhor = (-1.0, None, None)
    passo = max(1, n // 400)  # sub-amostra se a faixa for muito longa, mantém rápido
    for i in range(0, n, passo):
        for j in range(i + min_dist_frames, n, passo):
            sim = float(np.dot(chroma[:, i], chroma[:, j]))
            if sim > melhor[0]:
                melhor = (sim, i, j)
    sim, i, j = melhor
    if i is None:
        raise RuntimeError('faixa demasiado curta para encontrar repetição a 20s+')
    # entre as duas repetições, fica com a de maior energia (RMS) — mais
    # provável de ser o refrão do que uma repetição silenciosa de verso
    candidato = j if rms[j] >= rms[i] else i
    offset = candidato * hop_s
    return round(offset, 1), f'repetição mais semelhante por chroma (similaridade={sim:.2f}), maior energia'


# ───────────────────────── Método C (LRCLIB) ─────────────────────────

LRCLIB_API = 'https://lrclib.net/api/search'


def metodo_c_lrclib(artista, titulo):
    query = urllib.parse.urlencode({'artist_name': artista, 'track_name': titulo})
    pedido = urllib.request.Request(f'{LRCLIB_API}?{query}', headers={'User-Agent': 'MusicBoxEstudo/1.0'})
    with urllib.request.urlopen(pedido, timeout=20) as resp:
        resultados = json.loads(resp.read().decode('utf-8'))
    time.sleep(1.5)
    synced = None
    for r in resultados:
        if r.get('syncedLyrics'):
            synced = r['syncedLyrics']
            break
    if not synced:
        raise RuntimeError('LRCLIB sem letra sincronizada para esta faixa')

    linhas = []
    for linha in synced.splitlines():
        m = re.match(r'\[(\d+):(\d+\.\d+)\](.*)', linha)
        if not m:
            continue
        seg = int(m.group(1)) * 60 + float(m.group(2))
        texto = re.sub(r'[^\w\s]', '', m.group(3)).strip().lower()
        if len(texto.split()) >= 3:
            linhas.append((seg, texto))

    from collections import Counter
    contagem = Counter(texto for _, texto in linhas)
    if not contagem:
        raise RuntimeError('letra sincronizada sem linhas com texto suficiente')
    texto_mais_repetido, n_rep = contagem.most_common(1)[0]
    if n_rep < 2:
        raise RuntimeError('nenhuma linha repete — sem refrão claro na letra')
    ocorrencias = [seg for seg, texto in linhas if texto == texto_mais_repetido]
    # 2ª ocorrência (ou a 1ª, se só houver evidência de repetição mais à
    # frente) — evita apanhar o verso de abertura quando esse por acaso
    # também repete a frase do refrão
    offset = ocorrencias[1] if len(ocorrencias) > 1 else ocorrencias[0]
    return round(offset, 1), f'linha mais repetida na letra ({n_rep}x): "{texto_mais_repetido[:40]}"'


def cortar_candidato(caminho_fonte, offset, destino):
    r = subprocess.run(['ffmpeg', '-y', '-ss', str(max(offset, 0)), '-t', '15', '-i', caminho_fonte,
                         '-c', 'copy', destino], capture_output=True, text=True, timeout=30)
    if r.returncode != 0 or not os.path.exists(destino):
        raise RuntimeError((r.stderr or 'ffmpeg falhou')[-300:])


def processar_faixa(faixa, progresso):
    tid = faixa['id']
    if tid in progresso and progresso[tid].get('completo'):
        print(f'{tid} — já processada, a saltar')
        return

    print(f'\n=== {tid} — {faixa["titulo"]} ({faixa["artista"]}) ===')
    caminho_fonte = obter_fonte_completa(tid, faixa['url'])
    print(f'  fonte completa: {caminho_fonte}')

    candidatos = {}
    for nome, fn, args in [
        ('controlo_volume', metodo_d_controlo, (caminho_fonte,)),
        ('itunes_alinhamento', metodo_a_itunes, (tid, faixa['artista'], faixa['titulo'], caminho_fonte)),
        ('chroma_repeticao', metodo_b_chroma, (caminho_fonte,)),
        ('lrclib_refrao', metodo_c_lrclib, (faixa['artista'], faixa['titulo'])),
    ]:
        try:
            offset, detalhe = fn(*args)
            candidatos[nome] = {'offset': offset, 'detalhe': detalhe}
            print(f'  {nome:20} -> {offset}s ({detalhe})')
        except Exception as e:
            candidatos[nome] = {'offset': None, 'erro': str(e)}
            print(f'  {nome:20} -> FALHOU: {e}')

    validos = {k: v for k, v in candidatos.items() if v.get('offset') is not None}
    if not validos:
        progresso[tid] = {'completo': False, 'erro': 'nenhum método produziu candidato'}
        gravar_progresso(progresso)
        return

    nomes_metodo = list(validos.keys())
    random.shuffle(nomes_metodo)
    chave = {}
    for i, nome_metodo in enumerate(nomes_metodo, start=1):
        label = f'B{i}'
        offset = validos[nome_metodo]['offset']
        destino = os.path.join(AUDIO_DIR, f'{tid}_{label}.mp3')
        try:
            cortar_candidato(caminho_fonte, offset, destino)
        except Exception as e:
            print(f'  falha a cortar {label} ({nome_metodo}): {e}')
            continue
        chave[label] = {'metodo': nome_metodo, 'offset': offset, **validos[nome_metodo]}

    with open(os.path.join(DADOS_DIR, f'chave_{tid}.json'), 'w', encoding='utf-8') as f:
        json.dump(chave, f, ensure_ascii=False, indent=2)

    progresso[tid] = {'completo': True, 'labels': list(chave.keys()),
                       'titulo': faixa['titulo'], 'artista': faixa['artista']}
    gravar_progresso(progresso)
    print(f'  ✓ {len(chave)} candidatos cortados, chave em dados/chave_{tid}.json')


def main():
    progresso = carregar_progresso()
    for faixa in FAIXAS:
        try:
            processar_faixa(faixa, progresso)
        except Exception as e:
            print(f'{faixa["id"]} — ERRO GERAL: {e}')
            progresso[faixa['id']] = {'completo': False, 'erro': str(e)}
            gravar_progresso(progresso)

    completas = sum(1 for p in progresso.values() if p.get('completo'))
    print(f'\n— resumo — {completas}/{len(FAIXAS)} faixas com candidatos prontos')


if __name__ == '__main__':
    main()
