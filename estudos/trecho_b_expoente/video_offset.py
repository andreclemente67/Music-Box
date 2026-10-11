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

APP_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ESTUDO_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(APP_DIR, 'scripts'))
import verificar_trechos as vt  # noqa: E402


def calcular(id_faixa, url_video):
    video_mp4 = os.path.join(ESTUDO_DIR, 'video', f'{id_faixa}_video.mp4')
    os.makedirs(os.path.dirname(video_mp4), exist_ok=True)
    if not os.path.exists(video_mp4):
        subprocess.run(
            ['yt-dlp', '-f', 'bestvideo[height<=480]+bestaudio/best[height<=480]',
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
    offset = round(video_t - fonte_t, 1)
    return {'video_offset_s': offset, 'confianca': round(conf, 3),
            'janela_usada_video_s': video_t, 'correspondente_fonte_s': round(fonte_t, 1),
            'nota': 'tempo_no_video = tempo_na_fonte_audio + video_offset_s'}


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('uso: video_offset.py <id_faixa> <url_youtube_do_videoclipe>', file=sys.stderr)
        sys.exit(1)
    resultado = calcular(sys.argv[1], sys.argv[2])
    print(json.dumps(resultado, ensure_ascii=False, indent=2))
