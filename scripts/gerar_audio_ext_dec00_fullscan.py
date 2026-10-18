#!/usr/bin/env python3
"""Áudio estendido Anos 2000 (dec00_02/04/06/07) por correlação no ficheiro
`tmp_dl/<id>_full.mp3` INTEIRO (pedido do André, 18 Out 2026 — segue o
`relatorios/regen_00_scan_fonte.json` da sessão anterior, que já tinha
localizado os picos >=0,90 por esta via; este script refaz a localização e
avança para o corte + gravação).

Para cada Trecho A/B de dec00_02, dec00_04, dec00_06, dec00_07:
  1. Localiza a posição do trecho actual dentro do `full` por correlação de
     forma de onda ao longo do ficheiro INTEIRO (nunca usa `inicio`/`fim` do
     catálogo — confirmado noutra sessão que estão desactualizados para
     estas 4 faixas). Só avança se o pico >= LIMIAR_POSICAO (0,90).
  2. Corta `assets/audio_ext/<id>_{a,b}_ext.mp3` = full[posição : posição +
     duração real do trecho + 10s], com `ffmpeg -c copy` (sem reencoder —
     mesmo método da dec00_01, herda bitrate/loudness automaticamente).
  3. Verifica: os primeiros JANELA_S segundos do ext têm de bater com o
     trecho actual já em produção (correlação >= LIMIAR_VERIFICACAO, 0,95).
     Se não bater, apaga o ext e regista o motivo — nunca deixa um ext não
     verificado em `assets/`.

`dec00_03`/`dec00_05` ficam de fora (fonte por confirmar, fora de causa
nesta tarefa) e `dec00_01` não é tocada.

NÃO escreve em catalogo.json até todas as verificações terminarem — só no
fim, e só os `ficheiro_ext` dos lados (A/B) que passaram a verificação,
com backup prévio em `backups_catalogo/` + tag git `antes-ext-00b`.

Correr com: scripts/.venv/bin/python3 scripts/gerar_audio_ext_dec00_fullscan.py
"""
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime

import numpy as np
from scipy.signal import correlate

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gerar_audio_ext_dec00 as g  # noqa: E402 — reutiliza pcm()

APP_DIR = g.APP_DIR
IDS = ['dec00_02', 'dec00_04', 'dec00_06', 'dec00_07']
JANELA_S = 5.0
MARGEM_LAG_S = 1.5
LIMIAR_POSICAO = 0.90
LIMIAR_VERIFICACAO = 0.95
DMIN_ENCORE_S = 10
SR = 22050


def duracao(caminho):
    r = subprocess.run(
        ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=nw=1:nk=1', caminho],
        capture_output=True, text=True)
    s = r.stdout.strip()
    return float(s) if s else None


def pico_em_janela(referencia, janela_longa):
    if len(referencia) == 0 or len(janela_longa) < len(referencia):
        return 0.0, None
    c = correlate(janela_longa, referencia, mode='valid')
    nr = np.linalg.norm(referencia)
    janela2 = janela_longa.astype(np.float64) ** 2
    cum = np.insert(np.cumsum(janela2), 0, 0.0)
    n = len(referencia)
    energia_local = cum[n:] - cum[:-n]
    normas = np.sqrt(np.maximum(energia_local, 1e-12))
    corr_norm = np.abs(c) / (nr * normas + 1e-12)
    idx = int(np.argmax(corr_norm))
    return float(corr_norm[idx]), idx


def localizar_no_full(ficheiro_curto, full_mp3):
    """Pico de correlação dos primeiros JANELA_S segundos de `ficheiro_curto`
    contra TODO o `full_mp3`. Devolve (pico, posicao_s)."""
    ref = g.pcm(ficheiro_curto, offset=0, duracao=JANELA_S)
    full = g.pcm(full_mp3)
    pico, idx = pico_em_janela(ref, full)
    pos = idx / SR if idx is not None else None
    return pico, pos


def verificar_corte(ext_path, ficheiro_curto):
    """Correlação dos primeiros JANELA_S segundos do `ext_path` contra os
    primeiros JANELA_S segundos de `ficheiro_curto`, com tolerância de
    MARGEM_LAG_S ao seek do ffmpeg (mesmo método de `confirmar_fonte`)."""
    ref = g.pcm(ficheiro_curto, offset=0, duracao=JANELA_S)
    janela_longa = g.pcm(ext_path, offset=0, duracao=JANELA_S + 2 * MARGEM_LAG_S)
    pico, _ = pico_em_janela(ref, janela_longa)
    return pico


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
    motivos = {}     # id -> {'trecho_a': motivo, 'trecho_b': motivo} (só quando NÃO aprovado)

    for id_ in IDS:
        entrada = catalogo[id_]
        full_mp3 = os.path.join(APP_DIR, 'tmp_dl', f'{id_}_full.mp3')
        if not os.path.exists(full_mp3):
            motivos[id_] = {'geral': f'tmp_dl/{id_}_full.mp3 não existe'}
            print(f'{id_}: SALTADA — {motivos[id_]["geral"]}')
            continue

        resultado_lados = {}
        for lado, suf in (('trecho_a', 'a'), ('trecho_b', 'b')):
            t = entrada[lado]
            ficheiro_curto = os.path.join(APP_DIR, t['ficheiro'])
            pico_pos, pos = localizar_no_full(ficheiro_curto, full_mp3)
            print(f'{id_} {lado}: pico posição = {pico_pos:.3f} @ {pos:.2f}s' if pos is not None else f'{id_} {lado}: sem pico')

            if pico_pos < LIMIAR_POSICAO:
                motivos.setdefault(id_, {})[lado] = f'pico de posição {pico_pos:.3f} < limiar {LIMIAR_POSICAO} — não avança'
                continue

            dur_trecho = duracao(ficheiro_curto)
            duracao_ext = dur_trecho + DMIN_ENCORE_S
            destino = os.path.join(APP_DIR, 'assets', 'audio_ext', f'{id_}_{suf}_ext.mp3')
            try:
                cortar_ext(full_mp3, pos, duracao_ext, destino)
            except RuntimeError as ex:
                motivos.setdefault(id_, {})[lado] = f'ffmpeg falhou: {ex}'
                continue

            pico_verif = verificar_corte(destino, ficheiro_curto)
            if pico_verif < LIMIAR_VERIFICACAO:
                os.remove(destino)
                motivos.setdefault(id_, {})[lado] = (
                    f'verificação falhou: correlação ext-vs-actual {pico_verif:.3f} < limiar {LIMIAR_VERIFICACAO} '
                    f'— ext apagado, catálogo não tocado'
                )
                print(f'{id_} {lado}: VERIFICAÇÃO FALHOU ({pico_verif:.3f}) — ext apagado')
                continue

            resultado_lados[lado] = {
                'ext': os.path.relpath(destino, APP_DIR),
                'posicao_s': round(pos, 2),
                'pico_posicao': round(pico_pos, 3),
                'duracao_ext_s': round(duracao_ext, 2),
                'pico_verificacao': round(pico_verif, 3),
            }
            print(f'{id_} {lado}: OK — {resultado_lados[lado]["ext"]} ({round(duracao_ext,2)}s), verificação {pico_verif:.3f}')

        if resultado_lados:
            aprovadas[id_] = resultado_lados

    print(f'\n{len(aprovadas)} faixas com pelo menos um lado aprovado: {sorted(aprovadas)}')
    print(f'Motivos de exclusão: {json.dumps(motivos, ensure_ascii=False)}')

    # Regista sempre o resultado completo, mesmo sem aprovadas.
    json.dump(
        {'aprovadas': aprovadas, 'motivos_exclusao': motivos},
        open(os.path.join(APP_DIR, 'relatorios', 'ext_00_fullscan_resultado.json'), 'w', encoding='utf-8'),
        indent=2, ensure_ascii=False,
    )

    if not aprovadas:
        print('Nada a gravar no catálogo — nenhum lado aprovado.')
        return

    # ── Backup + tag antes de tocar no catálogo ──
    backup_dir = os.path.join(APP_DIR, 'backups_catalogo')
    os.makedirs(backup_dir, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = os.path.join(backup_dir, f'catalogo_{timestamp}_antes-ext-00b.json')
    shutil.copy2(catalogo_path, backup_path)
    print(f'Backup: {os.path.relpath(backup_path, APP_DIR)}')

    subprocess.run(['git', 'tag', 'antes-ext-00b'], cwd=APP_DIR, check=False)
    print('Tag git "antes-ext-00b" criada (ou já existia).')

    # ── Grava SÓ trecho_a/b.ficheiro_ext dos lados aprovados ──
    catalogo_lista = json.load(open(catalogo_path, encoding='utf-8'))
    for e in catalogo_lista:
        if e['id'] in aprovadas:
            for lado in ('trecho_a', 'trecho_b'):
                if lado in aprovadas[e['id']]:
                    e[lado]['ficheiro_ext'] = aprovadas[e['id']][lado]['ext']
    json.dump(catalogo_lista, open(catalogo_path, 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
    print(f'catalogo.json actualizado — ficheiro_ext gravado para {sum(len(v) for v in aprovadas.values())} lado(s) em {len(aprovadas)} faixa(s).')


if __name__ == '__main__':
    main()
