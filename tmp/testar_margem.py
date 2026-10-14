#!/usr/bin/env python3
"""Testa o teste de margem da localização por correlação.

Para cada faixa com source em cache, localiza o Trecho B pelo ficheiro de
produção e mostra a margem para o segundo pico distinto — o Hey Ya! tem
de sair marcado como ambíguo (142s vs 167s).

Correr com:  ~/.venvs/musicbox-audio/bin/python tmp/testar_margem.py
"""
import json
import os
import sys

import librosa

APP = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, APP)
import analise_refrao as ar  # noqa: E402

CACHE = os.path.join(APP, 'tmp_dl')

cat = {e['id']: e for e in json.load(open(os.path.join(APP, 'catalogo.json')))}

print(f'margem mínima exigida: {ar.MARGEM_RIVAL_MINIMA:.0%}   '
      f'(rivais separados por >= {ar.SEPARACAO_RIVAIS_S:.0f}s)\n')
print(f'{"faixa":<10}{"pico":<10}{"rival":<10}{"margem":<10}{"nitidez":<10}'
      f'{"veredicto":<22}catálogo')
print('-' * 92)

for fid in sorted(f[:-9] for f in os.listdir(CACHE) if f.endswith('_full.mp3')):
    if fid not in cat:
        continue
    e = cat[fid]
    b = e['trecho_b']
    trecho = os.path.join(APP, b['ficheiro'])
    if not os.path.exists(trecho):
        continue
    y, sr = librosa.load(os.path.join(CACHE, f'{fid}_full.mp3'), sr=ar.SR, mono=True)
    loc = ar.localizar_trecho(trecho, y, sr)
    if not loc:
        print(f'{fid:<10}(sem localização)')
        continue
    cb = (f"{b['inicio']:.0f}–{b['fim']:.0f}s"
          if b.get('inicio') is not None else 'null')
    veredicto = 'AMBÍGUO, não usar' if loc['ambiguo'] else 'ok'
    rival = f"{loc['rival_s']:.1f}s" if loc['rival_s'] is not None else '—'
    print(f"{fid:<10}{loc['inicio_s']:.1f}s{'':<4}{rival:<10}"
          f"{loc['margem_rival']:.1%}{'':<5}{loc['nitidez_pico']:.1f}x{'':<5}"
          f"{veredicto:<22}{cb}")
    if loc['ambiguo']:
        print(f"{'':<10}alternativas: "
              f"{', '.join(f'{s:.1f}s' for s in loc['alternativas_s'])}")
