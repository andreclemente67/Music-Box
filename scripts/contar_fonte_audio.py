#!/usr/bin/env python3
"""Quantas faixas do catálogo têm fonte_audio. Só leitura.

Correr com:  python3 scripts/contar_fonte_audio.py
"""
import json
import os
from collections import Counter

APP = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

catalogo = json.load(open(os.path.join(APP, 'catalogo.json'), encoding='utf-8'))
playlists = json.load(open(os.path.join(APP, 'playlists.json'), encoding='utf-8'))

com = [e for e in catalogo if e.get('fonte_audio')]
sem = [e for e in catalogo if not e.get('fonte_audio')]
print(f'catálogo: {len(catalogo)} faixas')
print(f'  com fonte_audio : {len(com)}  ({len(com) / len(catalogo):.0%})')
print(f'  sem fonte_audio : {len(sem)}  ({len(sem) / len(catalogo):.0%})')

# tempos de trecho_b no catálogo, que é o outro dado que falta
por_id = {e['id']: e for e in catalogo}
def tem_tempos(e, qual):
    t = e.get(qual) or {}
    return t.get('inicio') is not None and t.get('fim') is not None

print(f'\ntempos no catálogo (todas as {len(catalogo)}):')
print(f'  trecho_a com inicio/fim : {sum(1 for e in catalogo if tem_tempos(e, "trecho_a"))}')
print(f'  trecho_b com inicio/fim : {sum(1 for e in catalogo if tem_tempos(e, "trecho_b"))}')

# cruzamento: o que é preciso para a regra correr (fonte_audio) e o que
# dispensa correlação (tempos no catálogo)
analisavel = sum(1 for e in catalogo if e.get('fonte_audio'))
sem_correlacao = sum(1 for e in catalogo
                     if e.get('fonte_audio') and tem_tempos(e, 'trecho_a'))
print(f'\npara a regra correr:')
print(f'  analisáveis (têm fonte_audio)            : {analisavel}')
print(f'  dessas, com Trecho A no catálogo          : {sem_correlacao}')
print(f'  dessas, a precisar de correlação para o A : {analisavel - sem_correlacao}')

# por pack, só para ver onde está concentrado
print('\npor playlist (faixas com fonte_audio / total):')
linhas = []
for codigo, p in playlists.items():
    ids = p.get('musicas') or []
    if not ids:
        continue
    c = sum(1 for i in ids if por_id.get(i, {}).get('fonte_audio'))
    linhas.append((c / len(ids), c, len(ids), codigo, p.get('nome', '')))
linhas.sort(reverse=True)
for frac, c, tot, codigo, nome in linhas:
    barra = '#' * round(frac * 10)
    print(f'  {c:>2}/{tot:<3} {barra:<10} {codigo:<22}{nome}')

em_playlists = {i for p in playlists.values() for i in (p.get('musicas') or [])}
print(f'\nfaixas do catálogo em alguma playlist (via "musicas"): {len(em_playlists & set(por_id))}')
print(f'faixas fora de qualquer playlist "musicas"            : {len(catalogo) - len(em_playlists & set(por_id))}')
