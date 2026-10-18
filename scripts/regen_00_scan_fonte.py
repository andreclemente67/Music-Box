#!/usr/bin/env python3
"""ENSAIO (dry-run) — varrimento de correlação ao ficheiro `tmp_dl/<id>_full.mp3`
INTEIRO (não só na janela `inicio`±1,5s de `confirmar_fonte`), para dec00_01..07.

Pedido do André (18 Out 2026), ponto 1 da regeneração Anos 2000: confirmar se a
baixa correlação já registada em scripts/gerar_audio_ext_dec00.py (0,06-0,48 em
quase todas) é "ficheiro errado" (pico de correlação baixo em TODO o full) ou
"mesma gravação, posição diferente" (pico alto, só não está onde o catálogo diz).

Não escreve em catalogo.json/playlists.json/mp3_index.json nem assets/ — só
relatorios/regen_00_scan_fonte.json (saída desta corrida).
"""
import json
import os
import subprocess
import sys

import numpy as np
from scipy.signal import correlate

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gerar_audio_ext_dec00 as g  # noqa: E402 — reutiliza pcm()

APP_DIR = g.APP_DIR
IDS = [f'dec00_0{i}' for i in range(1, 8)]
JANELA_S = 5.0


def duracao(caminho):
    r = subprocess.run(
        ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=nw=1:nk=1', caminho],
        capture_output=True, text=True)
    s = r.stdout.strip()
    return float(s) if s else None


def varrer(ficheiro_curto, full_mp3):
    """Correlaciona os primeiros JANELA_S segundos de `ficheiro_curto` contra
    TODO o `full_mp3`. Devolve (pico_corr, posicao_s_do_pico)."""
    ref = g.pcm(ficheiro_curto, offset=0, duracao=JANELA_S)
    sr = 22050
    full = g.pcm(full_mp3)
    if len(ref) == 0 or len(full) < len(ref):
        return 0.0, None
    c = correlate(full, ref, mode='valid')
    nr = np.linalg.norm(ref)
    full2 = full.astype(np.float64) ** 2
    cum = np.insert(np.cumsum(full2), 0, 0.0)
    n = len(ref)
    energia_local = cum[n:] - cum[:-n]
    normas = np.sqrt(np.maximum(energia_local, 1e-12))
    corr_norm = np.abs(c) / (nr * normas + 1e-12)
    idx = int(np.argmax(corr_norm))
    return float(corr_norm[idx]), idx / sr


def main():
    catalogo = {e['id']: e for e in json.load(open(os.path.join(APP_DIR, 'catalogo.json'), encoding='utf-8'))}
    resultados = {}
    for id_ in IDS:
        full_mp3 = os.path.join(APP_DIR, 'tmp_dl', f'{id_}_full.mp3')
        if not os.path.exists(full_mp3):
            resultados[id_] = {'erro': 'tmp_dl full não existe'}
            print(id_, 'SEM tmp_dl full')
            continue
        e = catalogo[id_]
        linha = {'titulo': e['titulo'], 'dur_full_s': round(duracao(full_mp3), 1)}
        for lado in ('trecho_a', 'trecho_b'):
            t = e[lado]
            caminho = os.path.join(APP_DIR, t['ficheiro'])
            if not os.path.exists(caminho):
                linha[lado] = {'erro': 'ficheiro de produção não existe'}
                continue
            pico, pos = varrer(caminho, full_mp3)
            linha[lado] = {
                'inicio_catalogo_s': t['inicio'],
                'dur_ficheiro_s': round(duracao(caminho), 2),
                'pico_corr_full_inteiro': round(pico, 3),
                'posicao_pico_s': round(pos, 2) if pos is not None else None,
                'desvio_vs_catalogo_s': round(pos - t['inicio'], 2) if pos is not None else None,
            }
            print(f"{id_} {lado}: pico={pico:.3f} em {pos:.2f}s (catálogo diz inicio={t['inicio']}s, desvio={pos - t['inicio']:.2f}s)" if pos is not None else f"{id_} {lado}: sem pico")
        resultados[id_] = linha

    out = os.path.join(APP_DIR, 'relatorios', 'regen_00_scan_fonte.json')
    json.dump(resultados, open(out, 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
    print('\nGravado:', os.path.relpath(out, APP_DIR))
    print('Nada escrito em catalogo.json/playlists.json/mp3_index.json/assets/.')


if __name__ == '__main__':
    main()
