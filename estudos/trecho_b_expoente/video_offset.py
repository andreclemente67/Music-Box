#!/usr/bin/env python3
"""Calcula o offset entre o áudio de um videoclipe e a fonte_audio de uma
faixa, por fingerprint (mesma técnica do alinhamento iTunes em
analisar.py) — janela deslizante de 20s ao longo do vídeo, evita ficar
preso a uma introdução sem música. NUNCA escreve no catálogo; só para
estudo/demonstração (video/). Ver README.md — nenhuma das 7 faixas de
STD.INT.00.MIX.001 tem campo `video` no catálogo; os 2 vídeos aqui
(dec00_01, dec00_03) foram escolhidos manualmente só para este estudo.

Uso: scripts/.venv/bin/python3 estudos/trecho_b_expoente/video_offset.py \
       <id_faixa> <url_youtube_do_videoclipe>
"""
import json
import os
import subprocess
import sys

import numpy as np
from scipy.signal import correlate

APP_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ESTUDO_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(APP_DIR, 'scripts'))
import verificar_trechos as vt  # noqa: E402

TOLERANCIA_SINCRONIZACAO_S = 0.1


def calcular(id_faixa, url_video):
    video_mp4 = os.path.join(ESTUDO_DIR, 'video', f'{id_faixa}_video.mp4')
    os.makedirs(os.path.dirname(video_mp4), exist_ok=True)
    if not os.path.exists(video_mp4):
        subprocess.run(
            # vcodec^=avc1/acodec^=mp4a força H.264/AAC — AV1/Opus (o que o
            # YouTube serve por omissão em qualidades altas) não é
            # decodificado pela maioria dos browsers (ficava preto no
            # <video>, bug real 2026-10-12).
            ['yt-dlp', '-f',
             'bestvideo[height<=480][vcodec^=avc1]+bestaudio[acodec^=mp4a]/best[height<=480][vcodec^=avc1]',
             '--merge-output-format', 'mp4', '-o', video_mp4, url_video],
            check=True, capture_output=True, text=True, timeout=180,
        )

    audio_video = os.path.join(ESTUDO_DIR, 'cache', f'{id_faixa}_video_audio.mp3')
    os.makedirs(os.path.dirname(audio_video), exist_ok=True)
    subprocess.run(['ffmpeg', '-y', '-i', video_mp4, '-vn', '-acodec', 'libmp3lame', '-q:a', '2', audio_video],
                    check=True, capture_output=True, text=True, timeout=60)

    caminho_fonte = os.path.join(ESTUDO_DIR, 'cache', f'{id_faixa}.mp3')
    dur_fonte, fp_fonte = vt.fingerprint_fpcalc(caminho_fonte, fonte_completa=True)
    dur_video, fp_video = vt.fingerprint_fpcalc(audio_video, fonte_completa=True)
    seg_item_v = dur_video / len(fp_video)
    seg_item_f = dur_fonte / len(fp_fonte)

    melhor = (0, None, None)
    for inicio_s in range(0, int(dur_video) - 20, 15):
        i0, i1 = int(inicio_s / seg_item_v), int((inicio_s + 20) / seg_item_v)
        trecho = fp_video[i0:i1]
        if len(trecho) < 10:
            continue
        idx, conf = vt.localizar_trecho(trecho, fp_fonte)
        if conf is not None and conf > melhor[0]:
            melhor = (conf, inicio_s, idx * seg_item_f if idx is not None else None)

    conf, video_t, fonte_t = melhor
    if video_t is None:
        raise RuntimeError('nenhuma janela do vídeo alinhou com confiança na fonte')

    # fingerprint só dá ~0.128s de resolução (item do chromaprint) —
    # insuficiente para a tolerância de 0.1s pedida (bug real 2026-10-12:
    # dava sempre ~0.27-0.30s de erro sistemático). Refina com correlação
    # cruzada de forma de onda (precisão de amostra, 1/22050s) usando uma
    # janela de 15s do vídeo à volta do ponto já encontrado.
    caminho_fonte_para_pcm = caminho_fonte
    pcm_video_janela = _pcm(audio_video, offset=video_t, duracao=15)
    pcm_fonte_inteira = _pcm(caminho_fonte_para_pcm)
    correlacao = correlate(pcm_fonte_inteira, pcm_video_janela, mode='valid', method='fft')
    melhor_lag = int(np.argmax(correlacao))
    fonte_t_precisa = melhor_lag / 22050
    offset = round(video_t - fonte_t_precisa, 3)

    return {'video_offset_s': offset, 'confianca': round(conf, 3),
            'janela_usada_video_s': video_t, 'correspondente_fonte_s': round(fonte_t_precisa, 3),
            'nota': 'tempo_no_video = tempo_na_fonte_audio + video_offset_s (offset refinado por correlação de amostra)'}


def _pcm(caminho, offset=0.0, duracao=None, sr=22050):
    cmd = ['ffmpeg', '-v', 'error', '-ss', str(max(offset, 0))]
    if duracao is not None:
        cmd += ['-t', str(duracao)]
    cmd += ['-i', caminho, '-ac', '1', '-ar', str(sr), '-f', 'f32le', '-']
    r = subprocess.run(cmd, capture_output=True, timeout=60)
    return np.frombuffer(r.stdout, dtype=np.float32)


def verificar_sincronizacao(id_faixa, offset_b_na_fonte, caminho_b, video_offset_s,
                             janela_busca_s=3.0, sr=22050):
    """Confirma, por correlação cruzada de forma de onda (sample-accurate,
    não fingerprint — chromaprint tem resolução ~0.128s, insuficiente para
    a tolerância de 0.1s pedida), que o vídeo em
    `tempo_previsto = offset_b_na_fonte + video_offset_s` bate mesmo com o
    áudio de `caminho_b` (o candidato B escolhido). Devolve (desvio_s,
    dentro_da_tolerancia: bool, tempo_video_preciso_s)."""
    video_mp4 = os.path.join(ESTUDO_DIR, 'video', f'{id_faixa}_video.mp4')
    audio_video = os.path.join(ESTUDO_DIR, 'cache', f'{id_faixa}_video_audio.mp3')
    if not os.path.exists(audio_video):
        subprocess.run(['ffmpeg', '-y', '-i', video_mp4, '-vn', '-acodec', 'libmp3lame', '-q:a', '2', audio_video],
                        check=True, capture_output=True, text=True, timeout=60)

    pcm_b = _pcm(caminho_b, sr=sr)
    tempo_previsto = offset_b_na_fonte + video_offset_s
    inicio_largo = max(tempo_previsto - janela_busca_s, 0.0)
    duracao_largo = janela_busca_s * 2 + len(pcm_b) / sr
    pcm_video_largo = _pcm(audio_video, offset=inicio_largo, duracao=duracao_largo, sr=sr)

    if len(pcm_video_largo) < len(pcm_b):
        return None, False, None

    correlacao = correlate(pcm_video_largo, pcm_b, mode='valid', method='fft')
    melhor_lag = int(np.argmax(correlacao))
    tempo_video_preciso = inicio_largo + melhor_lag / sr
    desvio = round(abs(tempo_video_preciso - tempo_previsto), 3)
    return desvio, desvio <= TOLERANCIA_SINCRONIZACAO_S, round(tempo_video_preciso, 3)


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('uso: video_offset.py <id_faixa> <url_youtube_do_videoclipe>', file=sys.stderr)
        sys.exit(1)
    resultado = calcular(sys.argv[1], sys.argv[2])
    print(json.dumps(resultado, ensure_ascii=False, indent=2))
