#!/usr/bin/env python3
"""Gera assets/audio_ext/<id>_{a,b}_ext.mp3 (Trecho normal + Dmin, 25s)
para dec00_02..dec00_07 — pedido do André, 16 Out 2026, mesmo método da
dec00_01 (commit 23b10da): corte directo do tmp_dl/<id>_full.mp3 com
`ffmpeg -c copy` (sem reencoder) a partir de trecho_a/trecho_b.inicio —
herda bitrate/loudness do full automaticamente, sem normalizar nada
(confirmado: dec00_01_a.mp3 normal e _a_ext.mp3 têm o mesmo bit_rate e
mean_volume via volumedetect, porque é o MESMO ffmpeg -c copy, só com
-t diferente).

Antes de cortar cada faixa, confirma por correlação de forma de onda
(scipy, mesma técnica de estudos/trecho_b_expoente/video_offset.py) que
os primeiros ~5s do ficheiro normal já existente (dec00_0X_a.mp3) batem
com os primeiros ~5s do tmp_dl/<id>_full.mp3 no tempo `inicio` registado
no catálogo — se não bater, salta a faixa (A e B) e regista o motivo,
NUNCA corta às cegas.

NÃO escreve no catálogo — isso é escreverExtNoCatalogo() no fim do
módulo, chamado só depois de todos os cortes terminarem e só para as
faixas aprovadas, com backup prévio (ver main()).

Correr com:  python3 scripts/gerar_audio_ext_dec00.py
"""
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime

import numpy as np
from scipy.signal import correlate

APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DMIN_ENCORE_S = 10
JANELA_CORR_S = 5.0
LIMIAR_CORR = 0.6  # correlação normalizada mínima para aceitar como "mesma fonte"
IDS = ['dec00_02', 'dec00_03', 'dec00_04', 'dec00_05', 'dec00_06', 'dec00_07']


def pcm(caminho, offset=0.0, duracao=None, sr=22050):
    cmd = ['ffmpeg', '-v', 'error', '-ss', str(max(offset, 0))]
    if duracao is not None:
        cmd += ['-t', str(duracao)]
    cmd += ['-i', caminho, '-ac', '1', '-ar', str(sr), '-f', 'f32le', '-']
    r = subprocess.run(cmd, capture_output=True, timeout=30)
    return np.frombuffer(r.stdout, dtype=np.float32)


MARGEM_LAG_S = 1.5  # tolerância a desalinhamento (seek do ffmpeg não é exacto ao frame)


def melhor_correlacao_normalizada(referencia, janela_longa):
    """Desliza `referencia` (mais curta) dentro de `janela_longa` e devolve
    o pico de correlação normalizada (~1.0 = formas de onda idênticas no
    melhor lag, ~0 = sem relação em lado nenhum) — tolera até
    MARGEM_LAG_S de desalinhamento entre as duas fontes."""
    if len(referencia) == 0 or len(janela_longa) < len(referencia):
        return 0.0
    c = correlate(janela_longa, referencia, mode='valid')
    nr = np.linalg.norm(referencia)
    if nr == 0:
        return 0.0
    # Energia local da janela em cada posição candidata (normaliza por
    # amplitude própria, não só pela da referência — evita que um trecho
    # mais alto bata "melhor" só por ter mais energia).
    janela2 = janela_longa.astype(np.float64) ** 2
    soma_cumulativa = np.cumsum(janela2)
    soma_cumulativa = np.insert(soma_cumulativa, 0, 0.0)
    n = len(referencia)
    energia_local = soma_cumulativa[n:] - soma_cumulativa[:-n] if len(soma_cumulativa) > n else np.array([])
    normas_locais = np.sqrt(np.maximum(energia_local, 1e-12))
    if len(normas_locais) != len(c):
        return float(np.max(np.abs(c)) / (nr * np.linalg.norm(janela_longa) + 1e-12))
    return float(np.max(np.abs(c) / (nr * normas_locais + 1e-12)))


def confirmar_fonte(id_faixa, ficheiro_curto, inicio_s, full_mp3):
    """True/False — os primeiros JANELA_CORR_S segundos do ficheiro curto
    já existente batem com o full no tempo `inicio_s` (± MARGEM_LAG_S)?"""
    caminho_curto = os.path.join(APP_DIR, ficheiro_curto)
    if not os.path.exists(caminho_curto):
        return False, f'{ficheiro_curto} não existe em disco'
    sinal_curto = pcm(caminho_curto, offset=0, duracao=JANELA_CORR_S)
    sinal_full = pcm(full_mp3, offset=max(inicio_s - MARGEM_LAG_S, 0),
                      duracao=JANELA_CORR_S + 2 * MARGEM_LAG_S)
    corr = melhor_correlacao_normalizada(sinal_curto, sinal_full)
    if corr < LIMIAR_CORR:
        return False, f'correlação {corr:.2f} < limiar {LIMIAR_CORR} em {inicio_s}s (±{MARGEM_LAG_S}s) — fonte provavelmente diferente'
    return True, f'correlação {corr:.2f} — fonte confirmada'


def cortar_ext(full_mp3, inicio_s, duracao_s, destino):
    os.makedirs(os.path.dirname(destino), exist_ok=True)
    cmd = ['ffmpeg', '-y', '-v', 'error', '-ss', str(inicio_s), '-t', str(duracao_s),
           '-i', full_mp3, '-c', 'copy', destino]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    if r.returncode != 0:
        raise RuntimeError(r.stderr[-300:])


def main():
    catalogo_path = os.path.join(APP_DIR, 'catalogo.json')
    catalogo = {e['id']: e for e in json.load(open(catalogo_path, encoding='utf-8'))}

    aprovadas = {}   # id -> {'a_ext': caminho, 'b_ext': caminho}
    saltadas = {}    # id -> motivo

    for id_faixa in IDS:
        entrada = catalogo[id_faixa]
        full_mp3 = os.path.join(APP_DIR, 'tmp_dl', f'{id_faixa}_full.mp3')
        if not os.path.exists(full_mp3):
            saltadas[id_faixa] = f'tmp_dl/{id_faixa}_full.mp3 não existe'
            print(f'{id_faixa}: SALTADA — {saltadas[id_faixa]}')
            continue

        ta, tb = entrada['trecho_a'], entrada['trecho_b']
        ok_a, motivo_a = confirmar_fonte(id_faixa, ta['ficheiro'], ta['inicio'], full_mp3)
        ok_b, motivo_b = confirmar_fonte(id_faixa, tb['ficheiro'], tb['inicio'], full_mp3)
        print(f'{id_faixa}: Trecho A — {motivo_a}')
        print(f'{id_faixa}: Trecho B — {motivo_b}')

        if not (ok_a and ok_b):
            motivo = []
            if not ok_a: motivo.append(f'Trecho A: {motivo_a}')
            if not ok_b: motivo.append(f'Trecho B: {motivo_b}')
            saltadas[id_faixa] = '; '.join(motivo)
            print(f'{id_faixa}: SALTADA — fonte não confirmada')
            continue

        destino_a = os.path.join(APP_DIR, 'assets', 'audio_ext', f'{id_faixa}_a_ext.mp3')
        destino_b = os.path.join(APP_DIR, 'assets', 'audio_ext', f'{id_faixa}_b_ext.mp3')
        duracao_a = (ta['fim'] - ta['inicio']) + DMIN_ENCORE_S
        duracao_b = (tb['fim'] - tb['inicio']) + DMIN_ENCORE_S
        try:
            cortar_ext(full_mp3, ta['inicio'], duracao_a, destino_a)
            cortar_ext(full_mp3, tb['inicio'], duracao_b, destino_b)
        except RuntimeError as ex:
            saltadas[id_faixa] = f'ffmpeg falhou: {ex}'
            print(f'{id_faixa}: SALTADA — {saltadas[id_faixa]}')
            continue

        aprovadas[id_faixa] = {
            'a_ext': os.path.relpath(destino_a, APP_DIR),
            'b_ext': os.path.relpath(destino_b, APP_DIR),
        }
        print(f'{id_faixa}: OK — {aprovadas[id_faixa]["a_ext"]} ({duracao_a}s), {aprovadas[id_faixa]["b_ext"]} ({duracao_b}s)')

    print(f'\n{len(aprovadas)} aprovadas: {sorted(aprovadas)}')
    print(f'{len(saltadas)} saltadas: {saltadas}')

    # Regista sempre o motivo das saltadas, mesmo quando 0 aprovadas —
    # bug corrigido 16 Out 2026: antes este write só corria depois do
    # "return" abaixo, perdendo o registo exactamente no caso em que mais
    # se precisa dele (nenhuma faixa aprovada).
    json.dump({'aprovadas': aprovadas, 'saltadas': saltadas}, open(
        os.path.join(APP_DIR, 'relatorios', 'audio_ext_dec00_saltadas.json'), 'w', encoding='utf-8'
    ), indent=2, ensure_ascii=False)

    if not aprovadas:
        print('Nada a gravar no catálogo — nenhuma faixa aprovada.')
        return

    # ── Backup + tag antes de tocar no catálogo ──
    backup_dir = os.path.join(APP_DIR, 'backups_catalogo')
    os.makedirs(backup_dir, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = os.path.join(backup_dir, f'catalogo_{timestamp}_antes-ext-00.json')
    shutil.copy2(catalogo_path, backup_path)
    print(f'Backup: {os.path.relpath(backup_path, APP_DIR)}')

    subprocess.run(['git', 'tag', 'antes-ext-00'], cwd=APP_DIR, check=False)
    print('Tag git "antes-ext-00" criada (ou já existia).')

    # ── Grava SÓ trecho_a/b.ficheiro_ext das faixas aprovadas ──
    catalogo_lista = json.load(open(catalogo_path, encoding='utf-8'))
    for e in catalogo_lista:
        if e['id'] in aprovadas:
            e['trecho_a']['ficheiro_ext'] = aprovadas[e['id']]['a_ext']
            e['trecho_b']['ficheiro_ext'] = aprovadas[e['id']]['b_ext']
    json.dump(catalogo_lista, open(catalogo_path, 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
    print(f'catalogo.json actualizado — ficheiro_ext gravado em {len(aprovadas)} faixas.')


if __name__ == '__main__':
    main()
