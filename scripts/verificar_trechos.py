#!/usr/bin/env python3
"""Verificador automático de trechos A/B — confirma por fingerprint de áudio
(chromaprint/fpcalc) que cada trecho_a/trecho_b de uma faixa existe mesmo
dentro da fonte de áudio esperada, e em que segundos.

Para cada faixa do catalogo.json:
  a) fonte: usa `fonte_audio` se existir; senão pesquisa no YouTube
     (yt-dlp ytsearchN "Artista - Título"), preferindo canal Topic
     ("Provided to YouTube by ...") > título com "Official Audio".
     Rejeita candidatos com "Video"/"Music Video"/"MV"/"Live" no título.
  b) descarrega o áudio completo da fonte escolhida para uma pasta de
     cache (scripts/_cache_verificacao/<video_id>.mp3) — nunca repete
     download se já estiver em cache.
  c) com `fpcalc -raw` (chromaprint), compara o fingerprint de cada
     trecho local (<id>_a.mp3/<id>_b.mp3) com o da fonte completa,
     por janela deslizante (distância de Hamming mínima) — encontra o
     deslocamento em segundos e um nível de confiança.
  c.1) ruído/diálogo: o offset do passo c é só aproximado (chromaprint
     erra tipicamente ~1-2s — não é falha, é a resolução normal do
     fingerprint); refina-se primeiro por correlação cruzada da forma
     de onda (scipy, método FFT, janela ±2,5s) e só depois compara
     espectro log-magnitude segundo a segundo (FFT + cosseno, numpy —
     substitui librosa/chroma: a dependência `numba` do librosa não
     tem wheel para Python 3.14 nesta máquina, a ideia é a mesma) entre
     o trecho local e a janela correspondente da fonte, já realinhada.
     Segundos com similaridade abaixo do limiar ficam marcados "ruído/
     diálogo em Xs–Ys" nas observações — mesmo que o fingerprint global
     ainda dê OK (cena de videoclipe sobreposta à música real, não uma
     fonte totalmente errada).
  d) escreve uma linha em relatorios/verificacao_trechos.csv.
  e) packs RET (Retrato), BAT (Bateria) e CIN (Cinema) têm formato
     próprio (faixa completa ou outra convenção) — marcados "formato
     especial — rever na BÍBLIA", nunca julgados como erro.

Instalação (uma vez):
  python3 -m venv scripts/.venv
  scripts/.venv/bin/pip install -r scripts/requirements.txt
  # fpcalc (chromaprint): já em scripts/bin/fpcalc (binário pré-compilado
  # das releases do GitHub acoustid/chromaprint, macOS x86_64 — usado em
  # vez de `brew install chromaprint` porque compila cmake+chromaprint
  # do código-fonte nesta máquina, 20+ minutos; noutra plataforma, ou se
  # preferir brew, basta que `fpcalc` esteja no PATH, o script usa-o na
  # falta do binário local).

Uso:
  scripts/.venv/bin/python3 scripts/verificar_trechos.py --packs STD.INT.00.MIX.001,STD.INT.10.MIX.001
  scripts/.venv/bin/python3 scripts/verificar_trechos.py                # catálogo todo (demorado — considerar correr em background)
"""
import argparse
import csv
import json
import os
import re
import shutil
import subprocess
import sys

import numpy as np
from scipy import signal

APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '_cache_verificacao')
RELATORIO_PATH = os.path.join(APP_DIR, 'relatorios', 'verificacao_trechos.csv')

# Binário fpcalc: primeiro scripts/bin/ (chromaprint pré-compilado das
# releases do GitHub — usado quando `brew install chromaprint` não está
# disponível/demora demasiado a compilar, ver DECISIONS.md 2026-10-08),
# senão o do PATH (brew ou outro).
_FPCALC_LOCAL = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'bin', 'fpcalc')
FPCALC_BIN = _FPCALC_LOCAL if os.path.exists(_FPCALC_LOCAL) else shutil.which('fpcalc')

# Packs com formato próprio (não standard A/B de 15s) — nunca julgados
# como erro, só sinalizados para revisão manual contra a BÍBLIA.
PACKS_FORMATO_ESPECIAL = {
    'RET.INT.ALL.VOZ.001': 'Retrato',
    'STD.INT.ALL.BAT.001': 'Bateria',
    'STD.INT.ALL.CIN.001': 'Cinema',
}

TITULO_PROIBIDO = re.compile(
    r'\bvideo\b|\bmv\b|\blive\b|música\s*video|\bmovie\b|\btrailer\b|\bscene\b|\bteaser\b', re.I)
TITULO_OFFICIAL_AUDIO = re.compile(r'official\s*audio', re.I)

LIMIAR_CONFIANCA_OK = 0.80  # fracção de bits concordantes considerada "encontrado"


def carregar_catalogo():
    with open(os.path.join(APP_DIR, 'catalogo.json'), encoding='utf-8') as f:
        return json.load(f)


def carregar_mapa_playlists():
    with open(os.path.join(APP_DIR, 'playlists.json'), encoding='utf-8') as f:
        pl = json.load(f)
    mapa = {}
    for codigo, p in pl.items():
        for tid in (p.get('musicas') or []):
            if tid:
                mapa[tid] = codigo
    return mapa


def _pesquisar_candidatos(titulo, artista, n=5):
    """Pesquisa no YouTube e devolve (candidatos_validos_ordenados,
    candidatos_rejeitados, erro|None). Cada candidato é
    (vid, titulo_yt, canal, duracao, descricao). Ordem: canal Topic
    ("Provided to YouTube by...") primeiro, depois título "Official
    Audio", depois o resto — todos sem "Video"/"MV"/"Live"/"Movie"/
    "Trailer"/"Scene"/"Teaser" no título (DECISIONS.md 2026-10-08/09)."""
    consulta = f'{artista} {titulo}'

    def _pesquisar(com_cookies):
        comando = ['yt-dlp', f'ytsearch{n}:{consulta}', '--skip-download', '--no-playlist']
        if com_cookies:
            comando += ['--cookies-from-browser', 'chrome']
        comando += ['--print', '%(id)s|||%(title)s|||%(channel)s|||%(duration)s|||%(description)s']
        return subprocess.run(comando, capture_output=True, text=True, timeout=90)

    try:
        r = _pesquisar(False)
        # "Sign in to confirm" (bloqueio anti-bot do YouTube, comum depois
        # de muitos pedidos seguidos — ver DECISIONS.md 2026-10-09) pode
        # falhar resultado a resultado sem tornar o returncode != 0; por
        # isso o sinal é o texto no stderr, não só o código de saída.
        if 'sign in to confirm' in (r.stderr or '').lower():
            r = _pesquisar(True)
    except subprocess.TimeoutExpired:
        return [], [], 'pesquisa no YouTube excedeu 90s'
    except Exception as e:
        return [], [], f'erro na pesquisa: {e}'
    linhas = [l for l in (r.stdout or '').strip().splitlines() if l]
    candidatos = []
    for linha in linhas:
        partes = linha.split('|||', 4)
        if len(partes) < 5:
            continue
        vid, tit, canal, dur, desc = partes
        try:
            dur = float(dur)
        except ValueError:
            dur = None
        candidatos.append((vid, tit, canal, dur, desc))

    if not candidatos:
        return [], [], 'sem resultados na pesquisa'

    def rejeitado(c):
        return bool(TITULO_PROIBIDO.search(c[1] or ''))

    def eh_topic(c):
        return 'provided to youtube' in (c[4] or '').lower()

    def eh_official_audio(c):
        return bool(TITULO_OFFICIAL_AUDIO.search(c[1] or ''))

    validos = [c for c in candidatos if not rejeitado(c)]
    rejeitados = [c for c in candidatos if rejeitado(c)]
    topic = [c for c in validos if eh_topic(c)]
    oficial = [c for c in validos if eh_official_audio(c) and c not in topic]
    resto = [c for c in validos if c not in topic and c not in oficial]
    return topic + oficial + resto, rejeitados, None


def escolher_fonte(titulo, artista):
    """Escolhe UMA fonte (a melhor, 1º candidato válido) — usado na
    corrida normal. Devolve (url, titulo_yt, canal, duracao, aviso)."""
    validos, rejeitados, erro = _pesquisar_candidatos(titulo, artista, n=5)
    if erro:
        return None, None, None, None, erro
    if not validos:
        vid, tit, canal, dur, _ = rejeitados[0]
        url = f'https://www.youtube.com/watch?v={vid}'
        return url, tit, canal, dur, 'ATENÇÃO: todos os candidatos pareciam Video/MV/Live/Movie/Trailer/Scene/Teaser — usado o 1º sem filtro'

    vid, tit, canal, dur, desc = validos[0]
    url = f'https://www.youtube.com/watch?v={vid}'
    aviso = None
    if 'provided to youtube' not in (desc or '').lower() and not TITULO_OFFICIAL_AUDIO.search(tit or ''):
        aviso = 'sem canal Topic nem título "Official Audio" — usado o 1º candidato não-Video/MV/Live/Movie/Trailer/Scene/Teaser'
    return url, tit, canal, dur, aviso


def escolher_candidatos_fonte(titulo, artista, n=5):
    """Devolve a lista ORDENADA de candidatos válidos (url, titulo_yt,
    canal, duracao) — para testar mais do que o 1º quando esse falha
    (ver `reavaliar_falhas`)."""
    validos, _, erro = _pesquisar_candidatos(titulo, artista, n=n)
    if erro:
        return [], erro
    return [(f'https://www.youtube.com/watch?v={vid}', tit, canal, dur)
            for vid, tit, canal, dur, _ in validos], None


def descarregar_para_cache(url):
    """Descarrega `url` para a cache. Se falhar com "Sign in to confirm"
    (YouTube a pedir prova de que não é bot — comum depois de muitos
    pedidos seguidos, ver DECISIONS.md 2026-10-09), tenta uma 2ª vez com
    --cookies-from-browser chrome antes de desistir (mesmo padrão de
    `gerar_faixa.descarregar_mp3_completo`)."""
    os.makedirs(CACHE_DIR, exist_ok=True)
    m = re.search(r'(?:v=|youtu\.be/)([\w-]{11})', url)
    video_id = m.group(1) if m else re.sub(r'\W+', '_', url)[:32]
    destino = os.path.join(CACHE_DIR, f'{video_id}.mp3')
    if os.path.exists(destino):
        return destino

    def _correr(com_cookies):
        comando = ['yt-dlp', '-x', '--audio-format', 'mp3', '--audio-quality', '0', '--remote-components', 'ejs:github']
        if com_cookies:
            comando += ['--cookies-from-browser', 'chrome']
        comando += ['-o', destino.replace('.mp3', '.%(ext)s'), url]
        return subprocess.run(comando, capture_output=True, text=True, timeout=120)

    r = _correr(False)
    if r.returncode != 0 and 'sign in to confirm' in (r.stderr or '').lower():
        r = _correr(True)
    if r.returncode != 0 or not os.path.exists(destino):
        raise RuntimeError((r.stderr or r.stdout or 'yt-dlp falhou')[-400:])
    return destino


def fingerprint_fpcalc(ficheiro, fonte_completa=False):
    """Devolve (duracao_s, lista_de_ints) via `fpcalc -raw`.

    `fonte_completa=True` passa `-length 0` (sem limite — o default do
    fpcalc só analisa os primeiros 120s, o que faria falhar qualquer
    Trecho B depois desse ponto, ex. dec00_01 aos 142s). Nos trechos
    locais (15s) o default já cobre o ficheiro todo, não precisa disto."""
    comando = [FPCALC_BIN, '-raw']
    if fonte_completa:
        comando += ['-length', '0']
    comando.append(ficheiro)
    r = subprocess.run(comando, capture_output=True, text=True, timeout=120)
    if r.returncode != 0:
        raise RuntimeError(f'fpcalc falhou em {ficheiro}: {r.stderr.strip()}')
    duracao = None
    fingerprint = []
    for linha in r.stdout.splitlines():
        if linha.startswith('DURATION='):
            duracao = float(linha.split('=', 1)[1])
        elif linha.startswith('FINGERPRINT='):
            fingerprint = [int(x) for x in linha.split('=', 1)[1].split(',') if x]
    return duracao, fingerprint


def _popcount(x):
    return bin(x & 0xFFFFFFFF).count('1')


def localizar_trecho(fp_trecho, fp_fonte):
    """Janela deslizante por distância de Hamming — devolve (indice_melhor,
    confianca 0..1) ou (None, 0.0) se fp_trecho for maior que fp_fonte."""
    n = len(fp_trecho)
    if n == 0 or len(fp_fonte) < n:
        return None, 0.0
    melhor_idx, melhor_dist = None, None
    for i in range(0, len(fp_fonte) - n + 1):
        dist = sum(_popcount(a ^ b) for a, b in zip(fp_trecho, fp_fonte[i:i + n]))
        if melhor_dist is None or dist < melhor_dist:
            melhor_dist, melhor_idx = dist, i
    bits_totais = n * 32
    confianca = 1 - (melhor_dist / bits_totais)
    return melhor_idx, confianca


LIMIAR_SIMILARIDADE_RUIDO = 0.95  # calibrado contra os controlos — ver DECISIONS.md 2026-10-08
# (limpos reais: dec00_01/a10_04 actuais ≈0.998-1.0; controlo negativo
# dec00_01 OLD com diálogo ≈0.72-0.88 — 0.95 separa os dois com margem)


def _decodificar_pcm(ficheiro, offset=0.0, duracao=None, sr=22050):
    """Decodifica um excerto de `ficheiro` para PCM mono float32 via ffmpeg
    (evita qualquer dependência de descodificador mp3 em numpy)."""
    cmd = ['ffmpeg', '-v', 'error', '-ss', str(offset)]
    if duracao is not None:
        cmd += ['-t', str(duracao)]
    cmd += ['-i', ficheiro, '-ac', '1', '-ar', str(sr), '-f', 'f32le', '-']
    r = subprocess.run(cmd, capture_output=True, timeout=60)
    if r.returncode != 0:
        raise RuntimeError(r.stderr.decode(errors='replace')[-300:])
    return np.frombuffer(r.stdout, dtype=np.float32)


def _espectro_log_normalizado(frame, sr=22050):
    """Espectro log-magnitude normalizado (norma 1) de 1s de áudio —
    substitui o mel/chroma do librosa (indisponível nesta máquina, ver
    docstring do módulo); serve igualmente para medir semelhança
    tímbrica/harmónica entre dois excertos de 1s."""
    if len(frame) < sr // 2 or np.allclose(frame, 0):
        return None
    janela = frame * np.hanning(len(frame))
    mag = np.abs(np.fft.rfft(janela))
    log_mag = np.log1p(mag)
    norma = np.linalg.norm(log_mag)
    if norma < 1e-9:
        return None
    return log_mag / norma


def detectar_ruido(caminho_local, caminho_fonte, offset_fonte_seg, sr=22050,
                    limiar=LIMIAR_SIMILARIDADE_RUIDO, janela_refinamento=2.5):
    """Compara, segundo a segundo, o espectro do trecho local com o da
    janela correspondente na fonte. O offset do fingerprint (chromaprint)
    é só aproximado — erro típico de ~1-2s, suficiente para identificar a
    fonte mas não para comparar segundo a segundo — por isso refina-se
    primeiro por correlação cruzada da forma de onda (scipy, método FFT)
    numa janela de ±`janela_refinamento`s em torno desse offset. Devolve
    (similaridades_por_segundo, intervalos suspeitos [(inicio,fim)],
    offset_refinado, erro|None)."""
    try:
        pcm_local = _decodificar_pcm(caminho_local, sr=sr)
        inicio_largo = max(offset_fonte_seg - janela_refinamento, 0.0)
        duracao_largo = janela_refinamento * 2 + len(pcm_local) / sr
        pcm_fonte_largo = _decodificar_pcm(caminho_fonte, offset=inicio_largo, duracao=duracao_largo, sr=sr)
    except Exception as e:
        return [], [], None, f'erro a decodificar para análise de ruído: {e}'

    if len(pcm_fonte_largo) < len(pcm_local):
        return [], [], None, 'janela da fonte menor que o trecho — sem margem para refinar'

    correlacao = signal.correlate(pcm_fonte_largo, pcm_local, mode='valid', method='fft')
    melhor_lag = int(np.argmax(correlacao))
    offset_refinado = round(inicio_largo + melhor_lag / sr, 2)
    pcm_fonte = pcm_fonte_largo[melhor_lag:melhor_lag + len(pcm_local)]

    n = min(len(pcm_local), len(pcm_fonte))
    pcm_local, pcm_fonte = pcm_local[:n], pcm_fonte[:n]
    n_segundos = int(n // sr)
    similaridades = []
    for s in range(n_segundos):
        a = _espectro_log_normalizado(pcm_local[s * sr:(s + 1) * sr])
        b = _espectro_log_normalizado(pcm_fonte[s * sr:(s + 1) * sr])
        similaridades.append(float(np.dot(a, b)) if a is not None and b is not None else None)

    intervalos, inicio = [], None
    for s, sim in enumerate(similaridades):
        suspeito = sim is not None and sim < limiar
        if suspeito and inicio is None:
            inicio = s
        elif not suspeito and inicio is not None:
            intervalos.append((inicio, s))
            inicio = None
    if inicio is not None:
        intervalos.append((inicio, len(similaridades)))
    return similaridades, intervalos, offset_refinado, None


def verificar_trecho(ficheiro_local, caminho_fonte, duracao_fonte, fp_fonte):
    caminho_local = os.path.join(APP_DIR, ficheiro_local)
    if not os.path.exists(caminho_local):
        return {'estado': 'ficheiro em falta', 'seg': None, 'confianca': None}
    try:
        dur_local, fp_local = fingerprint_fpcalc(caminho_local)
    except Exception as e:
        return {'estado': f'erro fpcalc: {e}', 'seg': None, 'confianca': None}
    idx, confianca = localizar_trecho(fp_local, fp_fonte)
    if idx is None:
        return {'estado': 'NÃO encontrado (trecho maior que a fonte?)', 'seg': None, 'confianca': confianca, 'duracao': dur_local}
    seg_por_item = duracao_fonte / len(fp_fonte)
    segundos = round(idx * seg_por_item, 1)
    estado = 'OK' if confianca >= LIMIAR_CONFIANCA_OK else 'NÃO encontrado'

    _, intervalos_ruido, _, erro_ruido = detectar_ruido(caminho_local, caminho_fonte, segundos)
    if erro_ruido:
        estado += f' (ruído não avaliado: {erro_ruido})'
    elif intervalos_ruido:
        trechos_txt = ', '.join(f'{a}s–{b}s' for a, b in intervalos_ruido)
        estado = f'ruído/diálogo em {trechos_txt}' if estado == 'OK' else f'{estado}; ruído/diálogo em {trechos_txt}'

    return {'estado': estado, 'seg': segundos, 'confianca': round(confianca, 3), 'duracao': dur_local}


PROPOSTAS_PATH = os.path.join(APP_DIR, 'relatorios', 'propostas_fonte_audio.json')


def testar_candidatos(trecho_a, trecho_b, candidatos):
    """Testa cada candidato (url, titulo_yt, canal, duracao) por ordem até
    um dar limpo (fingerprint OK nos dois trechos, sem ruído/diálogo).
    Devolve (encontrado|None, tentativas) — cada tentativa é
    (url, titulo_yt, detalhe, comparado:bool); comparado=False significa
    que nem chegou a descarregar/analisar (não é evidência de conteúdo
    errado, só de download bloqueado nesse candidato)."""
    encontrado = None
    tentativas = []
    for url, tit, canal, dur in candidatos:
        try:
            caminho_fonte = descarregar_para_cache(url)
            dur_fonte, fp_fonte = fingerprint_fpcalc(caminho_fonte, fonte_completa=True)
        except Exception as e:
            tentativas.append((url, tit, f'erro a descarregar/analisar: {e}', False))
            continue
        res_a = verificar_trecho(trecho_a['ficheiro'], caminho_fonte, dur_fonte, fp_fonte)
        res_b = (verificar_trecho(trecho_b['ficheiro'], caminho_fonte, dur_fonte, fp_fonte)
                 if trecho_b.get('ficheiro') else {'estado': '(sem trecho_b)'})
        limpo = res_a['estado'] == 'OK' and res_b['estado'] in ('OK', '(sem trecho_b)')
        tentativas.append((url, tit, f"A={res_a['estado']} B={res_b['estado']}", True))
        if limpo:
            encontrado = (url, tit, canal, dur)
            break
    return encontrado, tentativas


def decidir_categoria(tid, encontrado, tentativas, candidatos, propostas):
    """Decide a categoria final a partir do resultado de `testar_candidatos`
    e, se "OK confirmado", regista a proposta em `propostas` (dict
    passado por referência). Devolve (categoria, detalhe). Três
    desfechos possíveis: OK confirmado (algum candidato limpo); defeito
    real (pelo menos um candidato foi mesmo comparado ao conteúdo e
    nenhum deu limpo — há evidência real de conteúdo errado);
    inconclusivo — download bloqueado (NENHUM candidato chegou a ser
    comparado, só erros de download — não prova nada sobre o trecho)."""
    if encontrado:
        url, tit, canal, dur = encontrado
        propostas[tid] = {'url': url, 'titulo_yt': tit, 'canal': canal, 'duracao': dur,
                           'tentativas_antes': len(tentativas) - 1}
        return 'OK confirmado', f'candidato {len(tentativas)}/{len(candidatos)}: {tit}'

    algum_comparado = any(t[3] for t in tentativas)
    detalhe = ' | '.join(f'{t[1]}: {t[2]}' for t in tentativas)
    if algum_comparado:
        return 'defeito real', f'{len(tentativas)} candidato(s) testado(s), nenhum limpo: {detalhe}'
    return 'inconclusivo', f'download bloqueado em todos os {len(tentativas)} candidato(s): {detalhe}'


def _carregar_estado_reavaliacao():
    """Lê o progresso já gravado (propostas.json + reavaliacao_falhas.csv),
    para retomar depois de uma corrida interrompida sem repetir trabalho
    já feito (nunca repete download/análise de um id já resolvido)."""
    propostas = {}
    if os.path.exists(PROPOSTAS_PATH):
        with open(PROPOSTAS_PATH, encoding='utf-8') as f:
            propostas = json.load(f)
    reavaliacao_csv = os.path.join(APP_DIR, 'relatorios', 'reavaliacao_falhas.csv')
    linhas = {}
    if os.path.exists(reavaliacao_csv):
        with open(reavaliacao_csv, encoding='utf-8') as f:
            for linha in csv.DictReader(f):
                linhas[linha['faixa']] = linha
    return propostas, linhas, reavaliacao_csv


def _gravar_estado_reavaliacao(propostas, linhas, reavaliacao_csv):
    """Grava já — chamado a cada faixa processada, não só no fim, para
    nunca perder progresso se o processo for interrompido ou crashar a
    meio (bug real encontrado em 2026-10-09: um TimeoutExpired não
    tratado na pesquisa de candidatos matou a corrida inteira depois de
    58 faixas já avaliadas, perdidas por só se gravar no fim)."""
    os.makedirs(os.path.dirname(PROPOSTAS_PATH), exist_ok=True)
    with open(PROPOSTAS_PATH, 'w', encoding='utf-8') as f:
        json.dump(propostas, f, ensure_ascii=False, indent=2)
    with open(reavaliacao_csv, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['faixa', 'pack', 'categoria_final', 'detalhe'])
        for linha in linhas.values():
            w.writerow([linha['faixa'], linha['pack'], linha['categoria_final'], linha['detalhe']])


def _obter_candidatos_falha(faixa, row):
    """Candidatos para uma faixa "NÃO encontrado"/"ruído/diálogo": só os
    do ytsearch5, sem a fonte original (essa já falhou ao conteúdo, não
    ao download — não vale repeti-la)."""
    return escolher_candidatos_fonte(faixa.get('titulo', ''), ' '.join(faixa.get('artista') or []))


def _obter_candidatos_erro(faixa, row):
    """Candidatos para uma faixa "erro" (download falhou): primeiro a
    fonte original (pode ter sido um bloqueio pontual), depois os
    alternativos do ytsearch5 que não sejam essa mesma URL."""
    partes_fonte = (row['fonte proposta'] or '').split(' | ')
    url_original = partes_fonte[0].strip() if partes_fonte else ''
    titulo_original = partes_fonte[1].strip() if len(partes_fonte) > 1 else '(fonte original, retentativa)'
    alternativos, erro_busca = escolher_candidatos_fonte(faixa.get('titulo', ''), ' '.join(faixa.get('artista') or []))
    candidatos = ([(url_original, titulo_original, None, None)] if url_original else []) \
        + [c for c in alternativos if c[0] != url_original]
    return candidatos, (None if candidatos else erro_busca)


def _reavaliar(csv_in, filtro_linha, obter_candidatos, label):
    """Motor comum a `reavaliar_falhas`/`reavaliar_erros`: para cada
    linha do CSV `csv_in` que passe `filtro_linha`, obtém candidatos via
    `obter_candidatos(faixa, row)` e testa-os um a um (`testar_candidatos`)
    até um dar limpo. Grava progresso a CADA faixa (nunca só no fim —
    bug real de 2026-10-09: um crash a meio perdeu 58 resultados já
    calculados porque só se gravava no fim) e retoma sozinho se um id já
    tiver resultado gravado de uma corrida anterior (nunca repete
    trabalho). Qualquer erro inesperado por faixa fica "inconclusivo",
    nunca mata a corrida inteira."""
    with open(csv_in, encoding='utf-8') as f:
        linhas_antigas = list(csv.DictReader(f))
    catalogo = carregar_catalogo()
    por_id = {t.get('id'): t for t in catalogo}

    candidatas = [r for r in linhas_antigas if filtro_linha(r)]
    propostas, linhas_estado, reavaliacao_csv = _carregar_estado_reavaliacao()
    pendentes = [r for r in candidatas if r['faixa'] not in linhas_estado]
    ja_feitas = len(candidatas) - len(pendentes)
    print(f'{label}: {len(candidatas)} faixas candidatas'
          + (f' ({ja_feitas} já retomadas de uma corrida anterior, a processar {len(pendentes)})' if ja_feitas else ''))

    for row in pendentes:
        tid = row['faixa']
        try:
            faixa = por_id.get(tid)
            if not faixa:
                cat, detalhe = 'inconclusivo', 'id não encontrado no catalogo.json actual'
            else:
                trecho_a = faixa.get('trecho_a') or {}
                trecho_b = faixa.get('trecho_b') or {}
                candidatos, erro = obter_candidatos(faixa, row)
                if erro or not candidatos:
                    cat, detalhe = 'inconclusivo', erro or 'nenhum candidato passou o filtro de título'
                else:
                    encontrado, tentativas = testar_candidatos(trecho_a, trecho_b, candidatos)
                    cat, detalhe = decidir_categoria(tid, encontrado, tentativas, candidatos, propostas)
        except Exception as e:
            cat, detalhe = 'inconclusivo', f'erro inesperado a reavaliar: {e}'

        linhas_estado[tid] = {'faixa': tid, 'pack': row['pack'], 'categoria_final': cat, 'detalhe': detalhe}
        print(f'{tid:16} — {cat} ({detalhe[:100]})')
        _gravar_estado_reavaliacao(propostas, linhas_estado, reavaliacao_csv)

    print(f'\npropostas de fonte_audio (NÃO aplicadas ao catálogo): {PROPOSTAS_PATH} ({len(propostas)} faixas no total)')
    print(f'detalhe da reavaliação: {reavaliacao_csv}')
    return {tid: (l['categoria_final'], l['detalhe']) for tid, l in linhas_estado.items() if tid in {r['faixa'] for r in candidatas}}


def reavaliar_falhas(csv_in):
    """Para cada faixa "NÃO encontrado"/"ruído/diálogo" de uma corrida
    anterior (excepto *_mosaico — formato especial), testa até 5
    candidatos do YouTube em vez de só o 1º. Ver `_reavaliar` para o
    comportamento de gravação/retomada e `decidir_categoria` para as 3
    categorias finais possíveis."""
    def filtro(r):
        return not r['faixa'].endswith('_mosaico') and (
            'NÃO encontrado' in r['A ok?'] or 'NÃO encontrado' in r['B ok?']
            or 'ruído/diálogo' in r['A ok?'] or 'ruído/diálogo' in r['B ok?'])
    return _reavaliar(csv_in, filtro, _obter_candidatos_falha, 'reavaliar_falhas')


def reavaliar_erros(csv_in):
    """Para as faixas "erro" (download falhou, tipicamente HTTP 403) de
    uma corrida anterior: retenta a fonte original 1x antes de cair nos
    candidatos alternativos do ytsearch5. Partilha o mesmo estado
    gravado (propostas.json/reavaliacao_falhas.csv) de `reavaliar_falhas`
    — nunca o substitui, só acrescenta/retoma."""
    def filtro(r):
        return r['observacoes'].startswith('erro a descarregar')
    return _reavaliar(csv_in, filtro, _obter_candidatos_erro, 'reavaliar_erros')


def verificar_um(id_faixa, fonte_url):
    """Verifica UMA faixa já cortada (<id>_a.mp3/<id>_b.mp3 na raiz,
    convenção de gerar_faixa.py/_servidor_escrita.py) contra `fonte_url`
    — sem tocar em catalogo.json nem fazer pesquisa nenhuma; usado logo
    depois de uma geração (ver `_verificar_trecho_gerado` em
    _servidor_escrita.py:/gerar-faixa, DECISIONS.md 2026-10-09). Imprime
    uma linha de resumo (a última linha de stdout) e devolve o estado."""
    ficheiro_a = os.path.join(APP_DIR, f'{id_faixa}_a.mp3')
    ficheiro_b = os.path.join(APP_DIR, f'{id_faixa}_b.mp3')
    if not os.path.exists(ficheiro_a):
        print(f'{id_faixa}: ficheiro em falta ({ficheiro_a})')
        return 'ficheiro em falta'
    try:
        caminho_fonte = descarregar_para_cache(fonte_url)
        dur_fonte, fp_fonte = fingerprint_fpcalc(caminho_fonte, fonte_completa=True)
    except Exception as e:
        print(f'{id_faixa}: não avaliado (erro a obter a fonte: {e})')
        return 'não avaliado'

    res_a = verificar_trecho(f'{id_faixa}_a.mp3', caminho_fonte, dur_fonte, fp_fonte)
    res_b = (verificar_trecho(f'{id_faixa}_b.mp3', caminho_fonte, dur_fonte, fp_fonte)
             if os.path.exists(ficheiro_b) else {'estado': '(sem trecho_b)'})
    limpo = res_a['estado'] == 'OK' and res_b['estado'] in ('OK', '(sem trecho_b)')
    resumo = 'OK' if limpo else f"A={res_a['estado']} B={res_b['estado']}"
    print(f'{id_faixa}: {resumo}')
    return resumo


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--packs', help='lista de playlistCodigo separados por vírgula (default: catálogo todo)')
    ap.add_argument('--id', help='verifica só esta faixa (<id>_a.mp3/<id>_b.mp3), precisa de --fonte-url')
    ap.add_argument('--fonte-url', help='URL a usar com --id, sem pesquisar nada')
    ap.add_argument('--reavaliar-falhas', metavar='CSV',
                     help='em vez da corrida normal, reavalia as faixas "NÃO encontrado"/"ruído/diálogo" '
                          'de uma corrida anterior (CSV), testando até 5 candidatos por faixa')
    ap.add_argument('--reavaliar-erros', metavar='CSV',
                     help='idem, mas para as faixas "erro" (download falhou) — retenta a fonte original '
                          '1x antes de cair nos candidatos alternativos; funde o resultado com uma '
                          'reavaliação --reavaliar-falhas já feita (não a substitui)')
    args = ap.parse_args()
    packs_filtro = set(args.packs.split(',')) if args.packs else None

    if not FPCALC_BIN or not os.path.exists(FPCALC_BIN):
        print('ERRO: fpcalc não encontrado (scripts/bin/fpcalc nem no PATH — '
              'brew install chromaprint, ou binário pré-compilado em '
              'scripts/bin/)', file=sys.stderr)
        sys.exit(1)
    print(f'fpcalc: {FPCALC_BIN}')

    if args.id:
        if not args.fonte_url:
            print('ERRO: --id precisa de --fonte-url', file=sys.stderr)
            sys.exit(1)
        verificar_um(args.id, args.fonte_url)
        return

    if args.reavaliar_erros:
        resultados = reavaliar_erros(args.reavaliar_erros)
        resumo = {'OK confirmado': 0, 'defeito real': 0, 'inconclusivo': 0}
        for _, (cat, _) in resultados.items():
            resumo[cat] += 1
        print('\n— resumo (reavaliação de erros) —')
        for k, v in resumo.items():
            print(f'{k}: {v}')
        return

    if args.reavaliar_falhas:
        resultados = reavaliar_falhas(args.reavaliar_falhas)
        resumo = {'OK confirmado': 0, 'defeito real': 0, 'inconclusivo': 0}
        for _, (cat, _) in resultados.items():
            resumo[cat] += 1
        print('\n— resumo (reavaliação) —')
        for k, v in resumo.items():
            print(f'{k}: {v}')
        return

    catalogo = carregar_catalogo()
    mapa_playlists = carregar_mapa_playlists()

    os.makedirs(os.path.dirname(RELATORIO_PATH), exist_ok=True)
    linhas_csv = []
    resumo = {'OK': 0, 'ruído/diálogo': 0, 'NÃO encontrado': 0, 'sem fonte': 0, 'formato especial': 0, 'erro': 0}

    for faixa in catalogo:
        tid = faixa.get('id')
        pack = mapa_playlists.get(tid, '')
        if packs_filtro is not None and pack not in packs_filtro:
            continue
        trecho_a = faixa.get('trecho_a') or {}
        trecho_b = faixa.get('trecho_b') or {}
        if not trecho_a.get('ficheiro'):
            continue  # sem trecho_a — fora do âmbito deste verificador (ex.: Retrato sem A/B)

        if pack in PACKS_FORMATO_ESPECIAL or tid.endswith('_mosaico'):
            motivo = 'mosaico (full, sem trecho_b)' if tid.endswith('_mosaico') else PACKS_FORMATO_ESPECIAL[pack]
            linhas_csv.append([tid, pack, '', '', '', '', '', f'formato especial ({motivo}) — rever na BÍBLIA'])
            resumo['formato especial'] += 1
            print(f'{tid:16} [{pack}] — formato especial ({motivo}), não avaliado')
            continue

        fonte_audio = faixa.get('fonte_audio')
        if fonte_audio:
            url, titulo_yt, canal, duracao, aviso = fonte_audio, None, None, None, None
        else:
            url, titulo_yt, canal, duracao, aviso = escolher_fonte(
                faixa.get('titulo', ''), ' '.join(faixa.get('artista') or []))

        if not url:
            linhas_csv.append([tid, pack, '', '', '', '', '', f'sem fonte: {aviso}'])
            resumo['sem fonte'] += 1
            print(f'{tid:16} [{pack}] — SEM FONTE ({aviso})')
            continue

        try:
            caminho_fonte = descarregar_para_cache(url)
            dur_fonte, fp_fonte = fingerprint_fpcalc(caminho_fonte, fonte_completa=True)
        except Exception as e:
            linhas_csv.append([tid, pack, url, '', '', '', '', f'erro a descarregar/analisar fonte: {e}'])
            resumo['erro'] += 1
            print(f'{tid:16} [{pack}] — ERRO fonte: {e}')
            continue

        res_a = verificar_trecho(trecho_a['ficheiro'], caminho_fonte, dur_fonte, fp_fonte)
        res_b = verificar_trecho(trecho_b['ficheiro'], caminho_fonte, dur_fonte, fp_fonte) if trecho_b.get('ficheiro') else {'estado': '(sem trecho_b)', 'seg': None, 'confianca': None}

        observacoes = []
        if aviso:
            observacoes.append(aviso)
        if res_a['estado'] != 'OK' and 'sem trecho_b' not in res_a['estado']:
            observacoes.append(f"A: {res_a['estado']}")
        if res_b['estado'] not in ('OK', '(sem trecho_b)'):
            observacoes.append(f"B: {res_b['estado']}")

        fonte_desc = titulo_yt or '(fonte_audio registada)'
        linhas_csv.append([
            tid, pack, f'{url} | {fonte_desc} | {duracao or ""}s',
            f"{res_a['estado']} ({res_a['seg']}s, conf={res_a['confianca']})",
            f"{res_b['estado']} ({res_b['seg']}s, conf={res_b['confianca']})" if res_b['seg'] is not None else res_b['estado'],
            res_a.get('duracao', ''), res_b.get('duracao', ''),
            '; '.join(observacoes),
        ])
        def categoria(estado):
            if estado.startswith('NÃO encontrado'):
                return 'NÃO encontrado'
            if estado.startswith('ruído/diálogo'):
                return 'ruído/diálogo'
            return 'OK'

        cat_a = categoria(res_a['estado'])
        cat_b = 'OK' if res_b['estado'] in ('OK', '(sem trecho_b)') else categoria(res_b['estado'])
        ordem_severidade = {'NÃO encontrado': 2, 'ruído/diálogo': 1, 'OK': 0}
        chave_resumo = max((cat_a, cat_b), key=lambda c: ordem_severidade[c])
        resumo[chave_resumo] += 1
        print(f"{tid:16} [{pack}] A={res_a['estado']}({res_a['seg']}s) B={res_b['estado']}({res_b['seg']}s)")

    with open(RELATORIO_PATH, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['faixa', 'pack', 'fonte proposta', 'A ok?', 'B ok?', 'duracao_a', 'duracao_b', 'observacoes'])
        w.writerows(linhas_csv)

    print('\n— resumo —')
    for k, v in resumo.items():
        print(f'{k}: {v}')
    print(f'\nrelatório: {RELATORIO_PATH}')


if __name__ == '__main__':
    main()
