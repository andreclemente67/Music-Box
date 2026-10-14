#!/usr/bin/env python3
"""Detecção de refrão ("expoente") por repetição harmónica + energia.

Regra implementada (decisão do André, 11 Out 2026 — por validar em teste
cego antes de entrar em produção): o Trecho B deve ser a ocorrência do
refrão com MAIS energia, desde que não se sobreponha ao Trecho A e tenha
pelo menos 30s de música depois.

Como encontra o refrão (sem saber a estrutura da música à partida):
1. `chroma_cens` com beat-sync — o refrão repete-se com a mesma sequência
   harmónica; beat-sync torna a comparação robusta a pequenas variações
   de tempo e a CENS é a variante de chroma pensada para repetição.
2. Matriz de recorrência (afinidade) entre beats: pares de beats
   harmonicamente parecidos. O refrão distingue-se por se parecer com
   *outras partes distantes* da música (versos parecem-se menos entre si).
3. Para cada janela candidata de 15s (a duração real do Trecho B em jogo),
   pontua a repetição: quanto os beats dessa janela se parecem com beats
   fora dela. Picos deste score = ocorrências do refrão.
4. RMS por janela = energia.
5. LRCLIB (letra sincronizada), quando existe, serve de cross-check:
   linhas de texto que se repetem ao longo da música são o refrão lírico;
   as janelas que caem nesses timestamps ficam marcadas e têm prioridade.

Nada aqui escreve em produção nem decide sozinho: devolve os candidatos
todos (com a razão de rejeição de cada um) para inspecção.
"""

import json
import os
import re
import sys
import urllib.parse
import urllib.request
from collections import Counter
from typing import Optional

import numpy as np
import librosa
from scipy.signal import correlate

APP_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, APP_DIR)
import gerar_faixa  # noqa: E402 — reutiliza descarregar_mp3_completo/TMP_DIR

DURACAO_TRECHO_S = 15.0
MUSICA_DEPOIS_MIN_S = 30.0
SEPARACAO_MIN_OCORRENCIAS_S = 15.0
# Margem para trás na contagem de linhas de refrão: uma linha que arranca
# pouco antes da janela ainda está a ser cantada dentro dela (a janela
# "contém" esse refrão). Corrigido 11 Out 2026 — antes exigia-se que a
# janela COMEÇASSE a ≤5s de uma linha, o que marcava só 3 de 12 janelas
# no Hey Ya! apesar de a letra ter 13 ocorrências do refrão, e fazia o
# cross-check decidir a escolha em vez da energia.
MARGEM_LINHA_ANTES_S = 3.0
SR = 22050
HOP = 512
N_FFT = 2048
# Acima deste corte vive o que marca o auge de um arranjo (pratos,
# hi-hats, brilho da mistura), e não o baixo/bombo que estão presentes
# em toda a música e saturam o RMS.
CORTE_BANDA_ALTA_HZ = 2000.0
# As duas componentes combinam-se pelo MÍNIMO, não pela média: o auge de
# uma música é dos dois eixos ao mesmo tempo (bateria completa E brilho),
# e a média deixava ganhar quem tivesse um extremo num eixo só. Medido
# nos Anos 80 (11 Out 2026): com média 50/50, 3 dos 4 vencedores tinham
# uma componente a 1.00 e a outra a ~0.05 — "intensidade 0.52" que na
# verdade era "máximo numa coisa, mínimo na outra". No Hey Ya!, onde a
# escolha coincide com o Trecho B escolhido por um humano, o vencedor
# tinha onset 0.93 E alta 0.95: é essa confluência que se quer exigir.
# Só concorrem janelas cuja repetição harmónica chega a esta fracção do
# máximo da faixa. Sem este filtro a intensidade escolhia a secção mais
# percussiva e não o refrão: no Hey Ya! ganhava a coda do "shake it like
# a Polaroid" (186-201s), com o onset mais alto da faixa mas a repetição
# MAIS BAIXA (6.0 contra 12-14.3 das zonas de refrão). A intensidade é
# para desempatar entre ocorrências do refrão, não para as escolher
# (decisão do André, 11 Out 2026).
LIMIAR_REPETICAO_REL = 0.70
# Nitidez mínima do pico de correlação (pico / mediana) para aceitar a
# localização de um trecho no source. Medido 11 Out 2026 em 80_02, com o
# source certo: 9.8x (Trecho A) e 8.9x (Trecho B).
NITIDEZ_MINIMA = 4.0


def obter_audio_source(url_youtube: str, id_faixa: str) -> Optional[str]:
    """Descarrega (ou reutiliza) o áudio completo em tmp_dl/.

    Mantém o ficheiro em disco de propósito: o mesmo source é usado para
    gerar o candidato depois do diagnóstico, e re-descarregar o mesmo
    vídeo duas vezes só gasta tempo e banda.
    """
    ja_existe = os.path.join(gerar_faixa.TMP_DIR, f'{id_faixa}_full.mp3')
    if os.path.exists(ja_existe) and os.path.getsize(ja_existe) > 0:
        return ja_existe
    try:
        return gerar_faixa.descarregar_mp3_completo(url_youtube, id_faixa)
    except Exception as e:
        print(f'[{id_faixa}] falha no download: {e}')
        return None


def chroma_beat_sync(y: np.ndarray, sr: int):
    """Chroma CENS agregada por beat.

    Devolve (chroma_sync (12, n_beats), beat_times (n_beats,)).
    """
    chroma = librosa.feature.chroma_cens(y=y, sr=sr)
    _, beats = librosa.beat.beat_track(y=y, sr=sr, trim=False)
    if len(beats) < 8:
        # música sem beat detectável — cai para frames fixos de ~0.5s
        passo = max(int(0.5 * sr / 512), 1)
        beats = np.arange(0, chroma.shape[1], passo)
    chroma_sync = librosa.util.sync(chroma, beats, aggregate=np.median)
    beat_times = librosa.frames_to_time(beats, sr=sr)
    # sync devolve um segmento por intervalo entre beats
    beat_times = beat_times[:chroma_sync.shape[1]]
    chroma_sync = chroma_sync[:, :len(beat_times)]
    return chroma_sync, beat_times


def matriz_recorrencia(chroma_sync: np.ndarray) -> np.ndarray:
    """Matriz de afinidade entre beats (valores ~[0,1], simétrica)."""
    return librosa.segment.recurrence_matrix(
        chroma_sync, mode='affinity', sym=True, metric='cosine',
    )


def pontuar_janelas(
    R: np.ndarray,
    beat_times: np.ndarray,
    duracao_total_s: float,
    duracao_janela_s: float = DURACAO_TRECHO_S,
    passo_s: float = 1.0,
) -> list:
    """Pontua cada janela de `duracao_janela_s` pela sua repetição.

    score = média, sobre os beats da janela, da afinidade a beats fora da
    janela e da sua vizinhança imediata (±duração da janela). Alto = esta
    parte da música repete-se noutros pontos distantes = refrão.
    """
    janelas = []
    fim_max = duracao_total_s - duracao_janela_s
    if fim_max <= 0:
        return janelas
    for inicio in np.arange(0, fim_max, passo_s):
        fim = inicio + duracao_janela_s
        dentro = np.where((beat_times >= inicio) & (beat_times < fim))[0]
        if len(dentro) < 4:
            continue
        # exclui a própria janela e a vizinhança contígua (auto-semelhança
        # trivial); o que sobra é repetição genuína noutra parte da música
        vizinhanca = np.where(
            (beat_times >= inicio - duracao_janela_s)
            & (beat_times < fim + duracao_janela_s)
        )[0]
        mascara_fora = np.ones(R.shape[1], dtype=bool)
        mascara_fora[vizinhanca] = False
        if not mascara_fora.any():
            continue
        score = float(R[np.ix_(dentro, mascara_fora)].sum() / len(dentro))
        janelas.append({'inicio_s': float(inicio), 'fim_s': float(fim), 'score_repeticao': score})
    return janelas


def agrupar_ocorrencias(janelas: list, separacao_min_s: float = SEPARACAO_MIN_OCORRENCIAS_S) -> list:
    """Reduz janelas sobrepostas a ocorrências distintas (non-max suppression).

    Mantém a janela de maior score de cada grupo; duas ocorrências ficam
    sempre a >= separacao_min_s uma da outra.
    """
    ocorrencias = []
    for j in sorted(janelas, key=lambda x: -x['score_repeticao']):
        if all(abs(j['inicio_s'] - o['inicio_s']) >= separacao_min_s for o in ocorrencias):
            ocorrencias.append(j)
    return sorted(ocorrencias, key=lambda x: x['inicio_s'])


def rms_janela(y: np.ndarray, sr: int, inicio_s: float, fim_s: float) -> float:
    secao = y[int(inicio_s * sr):int(fim_s * sr)]
    if secao.size == 0:
        return 0.0
    return float(np.sqrt(np.mean(secao.astype(np.float64) ** 2)))


def localizar_trecho(caminho_trecho: str, y_source: np.ndarray, sr: int) -> Optional[dict]:
    """Onde é que um trecho de produção começa dentro do source.

    Metade das faixas tem `trecho_a/b.inicio` e `.fim` a null no catálogo
    (os mp3 existem, os tempos nunca foram gravados — todo o pack dos
    Anos 80, por exemplo). Sem os tempos não há como aplicar o filtro de
    sobreposição com o A nem comparar o B actual com o B2 proposto.

    Correlaciona o envelope de energia (RMS) do trecho contra o do
    source: o envelope é robusto às diferenças de encoding e de volume
    entre o mp3 de produção e o source re-descarregado, que uma
    correlação de amostras não perdoaria. Devolve também a nitidez do
    pico (pico / mediana) — um pico baixo significa que o trecho não veio
    deste source, e aí o chamador deve desconfiar em vez de usar o valor.
    """
    if not os.path.exists(caminho_trecho):
        return None
    t, _ = librosa.load(caminho_trecho, sr=sr, mono=True)
    if t.size == 0 or t.size > y_source.size:
        return None

    hop = 256
    env_t = librosa.feature.rms(y=t, hop_length=hop)[0]
    env_s = librosa.feature.rms(y=y_source, hop_length=hop)[0]
    env_t = (env_t - env_t.mean()) / (env_t.std() + 1e-9)
    env_s = (env_s - env_s.mean()) / (env_s.std() + 1e-9)

    c = correlate(env_s, env_t, mode='valid')
    i = int(np.argmax(c))
    nitidez = float(c[i] / (np.median(np.abs(c)) + 1e-9))
    inicio = i * hop / sr
    duracao = len(t) / sr
    return {
        'inicio_s': inicio, 'fim_s': inicio + duracao,
        'duracao_s': duracao, 'nitidez_pico': nitidez,
        'fiavel': nitidez >= NITIDEZ_MINIMA,
    }


def perfil_intensidade(y: np.ndarray, sr: int) -> dict:
    """Pré-calcula, para a faixa toda, as duas medidas de intensidade.

    O RMS puro não serve para escolher o "expoente" em masterizações
    modernas: no Hey Ya! todas as janelas candidatas ficavam entre 0.3056
    e 0.3415 (~11%) e o vencedor ganhava por 1.3% — ruído do limiter, não
    sinal (medido 11 Out 2026). O que distingue mesmo o auge da música é a
    densidade de ataques (bateria completa, mais instrumentos a entrar) e
    o brilho (pratos/hi-hats), e nenhuma das duas é achatada pela
    compressão:

    - `onset_strength`: força/densidade de ataques por frame.
    - energia acima de CORTE_BANDA_ALTA_HZ, em dB.
    """
    onset_env = librosa.onset.onset_strength(y=y, sr=sr, hop_length=HOP)
    onset_times = librosa.times_like(onset_env, sr=sr, hop_length=HOP)

    S = np.abs(librosa.stft(y, n_fft=N_FFT, hop_length=HOP))
    freqs = librosa.fft_frequencies(sr=sr, n_fft=N_FFT)
    alta = freqs >= CORTE_BANDA_ALTA_HZ
    energia_alta = (S[alta, :] ** 2).sum(axis=0)
    energia_alta_db = 10.0 * np.log10(energia_alta + 1e-10)
    stft_times = librosa.times_like(energia_alta_db, sr=sr, hop_length=HOP)

    return {
        'onset_env': onset_env, 'onset_times': onset_times,
        'energia_alta_db': energia_alta_db, 'stft_times': stft_times,
    }


def medir_janela(perfil: dict, y: np.ndarray, sr: int, inicio_s: float, fim_s: float) -> dict:
    """Medidas cruas de intensidade de uma janela (ainda sem normalizar)."""
    def media(valores, tempos):
        dentro = (tempos >= inicio_s) & (tempos < fim_s)
        return float(valores[dentro].mean()) if dentro.any() else 0.0

    return {
        'onset': media(perfil['onset_env'], perfil['onset_times']),
        'alta_db': media(perfil['energia_alta_db'], perfil['stft_times']),
        'rms': rms_janela(y, sr, inicio_s, fim_s),
    }


def _normalizar(valores: list) -> list:
    """Min-max para [0,1]. A comparação é sempre DENTRO da mesma faixa —
    o que interessa é qual janela é mais intensa que as outras, não o
    valor absoluto (que depende da masterização de cada tema)."""
    lo, hi = min(valores), max(valores)
    if hi - lo < 1e-9:
        return [0.5] * len(valores)
    return [(v - lo) / (hi - lo) for v in valores]


def _normalizar_letra(linha: str) -> str:
    return re.sub(r'[^a-z0-9 ]', '', linha.lower()).strip()


def lrclib_timestamps_refrao(titulo: str, artista: str) -> dict:
    """Timestamps de TODAS as linhas de letra que se repetem no tema.

    Uma linha cantada duas ou mais vezes é hook/refrão, não verso — e um
    tema pode ter mais do que um hook. Usar só a linha mais frequente como
    proxy do refrão falha nesses casos: no Hey Ya! marcava as 13 linhas de
    "hey ya uh-oh" (100-121s, 201-230s) e ignorava as 10 de "hey ya"
    (34-64s) e as 2 de "alright alright..." (143/147s, que é precisamente
    onde está o Trecho B actual). Corrigido 11 Out 2026.

    Não se exige separação temporal entre ocorrências: hooks curtos
    repetidos dentro da mesma secção ("alright alright alright") contam
    como refrão de propósito. O custo é algum falso positivo em versos
    cantados em staccato ("then what makes, then what makes"), que só
    acrescenta 1 linha à contagem de uma janela e não decide nada sozinho.

    Devolve {'ok': bool, 'timestamps': [s, ...], 'linhas': [(n, texto)],
    'mensagem': str}. Nunca levanta excepção — sem letra, a análise segue
    sem cross-check.
    """
    saida = {'ok': False, 'timestamps': [], 'linhas': [], 'mensagem': ''}
    try:
        qs = urllib.parse.urlencode({'track_name': titulo, 'artist_name': artista})
        pedido = urllib.request.Request(
            f'https://lrclib.net/api/search?{qs}',
            headers={'User-Agent': 'MusicBox2026 (estudo interno)'},
        )
        with urllib.request.urlopen(pedido, timeout=12) as r:
            resultados = json.load(r)
    except Exception as e:
        saida['mensagem'] = f'LRCLIB indisponível ({e})'
        return saida

    sincronizada = next(
        (x for x in (resultados or []) if x.get('syncedLyrics')), None
    )
    if not sincronizada:
        saida['mensagem'] = 'sem letra sincronizada no LRCLIB'
        return saida

    linhas = []
    for bruta in sincronizada['syncedLyrics'].splitlines():
        m = re.match(r'\[(\d+):(\d+(?:\.\d+)?)\]\s*(.*)', bruta)
        if not m:
            continue
        t = int(m.group(1)) * 60 + float(m.group(2))
        texto = _normalizar_letra(m.group(3))
        if texto:
            linhas.append((t, texto))

    if not linhas:
        saida['mensagem'] = 'letra sincronizada vazia'
        return saida

    contagem = Counter(texto for _, texto in linhas)
    repetidas = {texto for texto, n in contagem.items() if n >= 2}
    if not repetidas:
        saida['mensagem'] = 'nenhuma linha repetida (sem refrão lírico claro)'
        return saida

    saida['ok'] = True
    saida['timestamps'] = sorted(t for t, texto in linhas if texto in repetidas)
    saida['linhas'] = sorted(
        ((contagem[texto], texto) for texto in repetidas), reverse=True,
    )
    resumo = ', '.join(f'{n}x "{texto[:22]}"' for n, texto in saida['linhas'][:3])
    saida['mensagem'] = (
        f'{len(saida["timestamps"])} linhas repetidas em '
        f'{len(repetidas)} hooks — {resumo}'
    )
    return saida


def analisar_refrao(
    id_faixa: str,
    titulo: str,
    artista: str,
    url_youtube: str,
    trecho_a_inicio: Optional[float] = None,
    trecho_a_fim: Optional[float] = None,
    trecho_b_inicio: Optional[float] = None,
    trecho_b_fim: Optional[float] = None,
    ficheiro_trecho_a: Optional[str] = None,
    ficheiro_trecho_b: Optional[str] = None,
) -> dict:
    """Análise completa de uma faixa. Não escreve nada em produção.

    Os tempos de cada trecho vêm do catálogo quando lá estão; só quando
    estão a None (metade das faixas) é que são recuperados por correlação
    contra o source, a partir do `ficheiro_trecho_*` — ver
    localizar_trecho(). O catálogo tem precedência nos dois trechos
    (decisão do André, 14 Out 2026): antes disso o B era SEMPRE
    correlacionado mesmo com tempos no catálogo, e no Hey Ya! isso
    substituiu o valor correcto (142–157s, corroborado pelo offset de
    vídeo do clip_b) por uma repetição errada do mesmo refrão (167–182s).
    O B actual serve só para comparar com o B2 proposto.
    """
    saida = {
        'ok': False,
        'id_faixa': id_faixa,
        'duracao_total_s': None,
        'lrclib': None,
        'candidatos': [],
        'escolhido': None,
        'criterio_escolha': '',
        'trecho_a_usado': None,
        'trecho_b_actual': None,
        'mensagem': '',
    }

    caminho = obter_audio_source(url_youtube, id_faixa)
    if not caminho:
        saida['mensagem'] = 'sem áudio source'
        return saida

    y, sr = librosa.load(caminho, sr=SR)
    duracao = float(librosa.get_duration(y=y, sr=sr))
    saida['duracao_total_s'] = duracao

    # Trecho A: do catálogo quando lá está, senão localizado no source
    if trecho_a_inicio is not None and trecho_a_fim is not None:
        saida['trecho_a_usado'] = {
            'inicio_s': float(trecho_a_inicio), 'fim_s': float(trecho_a_fim),
            'origem': 'catálogo',
        }
    elif ficheiro_trecho_a:
        loc = localizar_trecho(ficheiro_trecho_a, y, sr)
        if loc:
            saida['trecho_a_usado'] = {**loc, 'origem': 'correlação'}
    if saida['trecho_a_usado'] is None:
        saida['mensagem'] = 'sem Trecho A (nem no catálogo nem localizável no source)'
        return saida
    trecho_a_inicio = saida['trecho_a_usado']['inicio_s']
    trecho_a_fim = saida['trecho_a_usado']['fim_s']

    # Trecho B actual: mesma precedência do A — catálogo primeiro,
    # correlação só quando o catálogo está a null
    if trecho_b_inicio is not None and trecho_b_fim is not None:
        saida['trecho_b_actual'] = {
            'inicio_s': float(trecho_b_inicio), 'fim_s': float(trecho_b_fim),
            'origem': 'catálogo',
        }
    elif ficheiro_trecho_b:
        loc_b = localizar_trecho(ficheiro_trecho_b, y, sr)
        if loc_b:
            saida['trecho_b_actual'] = {**loc_b, 'origem': 'correlação'}

    chroma_sync, beat_times = chroma_beat_sync(y, sr)
    R = matriz_recorrencia(chroma_sync)
    janelas = pontuar_janelas(R, beat_times, duracao)
    if not janelas:
        saida['mensagem'] = 'áudio demasiado curto para janelas de 15s'
        return saida

    ocorrencias = agrupar_ocorrencias(janelas)
    lrclib = lrclib_timestamps_refrao(titulo, artista)
    saida['lrclib'] = lrclib
    perfil = perfil_intensidade(y, sr)

    repeticao_max = max(o['score_repeticao'] for o in ocorrencias)
    limiar_repeticao = LIMIAR_REPETICAO_REL * repeticao_max
    saida['repeticao_max'] = repeticao_max
    saida['limiar_repeticao'] = limiar_repeticao

    for o in ocorrencias:
        razoes = []
        if not (o['fim_s'] <= trecho_a_inicio or o['inicio_s'] >= trecho_a_fim):
            razoes.append(f'sobrepõe o Trecho A ({trecho_a_inicio:.0f}–{trecho_a_fim:.0f}s)')
        musica_depois = duracao - o['fim_s']
        if musica_depois < MUSICA_DEPOIS_MIN_S:
            razoes.append(f'só {musica_depois:.0f}s de música depois (<{MUSICA_DEPOIS_MIN_S:.0f}s)')
        if o['score_repeticao'] < limiar_repeticao:
            razoes.append(
                f'repetição {o["score_repeticao"]:.1f} < {LIMIAR_REPETICAO_REL:.0%} '
                f'do máximo da faixa ({repeticao_max:.1f})'
            )

        # cross-check: quantas linhas do refrão são cantadas dentro desta
        # janela (uma linha que arranca pouco antes ainda conta — ver
        # MARGEM_LINHA_ANTES_S)
        if lrclib['ok']:
            linhas_na_janela = sum(
                1 for t in lrclib['timestamps']
                if o['inicio_s'] - MARGEM_LINHA_ANTES_S <= t < o['fim_s']
            )
            refrao_lirico = linhas_na_janela > 0
        else:
            linhas_na_janela, refrao_lirico = 0, None

        saida['candidatos'].append({
            **o,
            **medir_janela(perfil, y, sr, o['inicio_s'], o['fim_s']),
            'refrao_lirico': refrao_lirico,
            'linhas_refrao': linhas_na_janela,
            'razao_rejeicao': '; '.join(razoes) or None,
        })

    validos = [c for c in saida['candidatos'] if not c['razao_rejeicao']]
    if not validos:
        saida['mensagem'] = f'nenhum candidato válido (de {len(saida["candidatos"])} ocorrências)'
        return saida

    # Intensidade = onset + banda alta, normalizados entre os candidatos
    # que concorrem (os válidos). Os rejeitados recebem o mesmo cálculo
    # com a mesma escala, só para aparecerem na tabela de diagnóstico.
    onset_n = _normalizar([c['onset'] for c in validos])
    alta_n = _normalizar([c['alta_db'] for c in validos])
    for c, o_n, a_n in zip(validos, onset_n, alta_n):
        c['intensidade'] = min(o_n, a_n)
        c['onset_norm'], c['alta_norm'] = o_n, a_n
    for c in saida['candidatos']:
        c.setdefault('intensidade', None)
        c.setdefault('onset_norm', None)
        c.setdefault('alta_norm', None)

    # cross-check LRCLIB: se há ocorrências confirmadas pela letra, a
    # escolha fica restrita a essas; senão usa só a repetição harmónica.
    confirmados = [c for c in validos if c['refrao_lirico']]
    pool = confirmados or validos
    saida['criterio_escolha'] = (
        'maior intensidade entre ocorrências confirmadas pela letra (LRCLIB)'
        if confirmados else
        'maior intensidade entre ocorrências por repetição harmónica (sem confirmação de letra)'
    )
    escolhido = max(pool, key=lambda c: c['intensidade'])
    saida['escolhido'] = escolhido
    saida['ok'] = True
    saida['mensagem'] = (
        f'escolhido {escolhido["inicio_s"]:.1f}–{escolhido["fim_s"]:.1f}s '
        f'(intensidade {escolhido["intensidade"]:.3f})'
    )
    return saida
