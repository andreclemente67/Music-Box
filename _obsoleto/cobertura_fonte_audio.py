#!/usr/bin/env python3
"""Diagnóstico de cobertura de fonte_audio por playlist. Só leitura.

Por pack: nº de faixas, nº com fonte_audio, nº com Trecho A no catálogo
(inicio/fim != null), nº com video_local. Marca os packs já usados como
demo/piloto (Encore, regra do Trecho B). Para os 10 packs com mais
faixas SEM fonte_audio, conta quantas dessas têm uma fonte proposta
classificada como "fallback" (não canal Topic/"Official Audio"), a
partir de relatorios/aprovacao_lote_progresso.csv — único relatório que
guarda essa classificação por faixa.

Correr com:  python3 scripts/cobertura_fonte_audio.py
"""
import csv
import json
import os

APP = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Packs já usados como demo/piloto — ver STATUS.md/DECISIONS.md 11-14 Out 2026
PILOTO = {
    'STD.INT.00.MIX.001': 'piloto Encore (clip_b)',
    'STD.INT.80.MIX.001': 'piloto regra Trecho B',
}


def tem_tempos(trecho):
    t = trecho or {}
    return t.get('inicio') is not None and t.get('fim') is not None


def main():
    catalogo = json.load(open(os.path.join(APP, 'catalogo.json'), encoding='utf-8'))
    playlists = json.load(open(os.path.join(APP, 'playlists.json'), encoding='utf-8'))
    por_id = {e['id']: e for e in catalogo}

    # classificação "fallback" por faixa, só para quem tem motivo registado
    fallback_por_faixa = {}
    caminho_csv = os.path.join(APP, 'relatorios', 'aprovacao_lote_progresso.csv')
    if os.path.exists(caminho_csv):
        for row in csv.DictReader(open(caminho_csv, encoding='utf-8')):
            motivo = row.get('motivo') or ''
            fallback_por_faixa[row['faixa']] = motivo.startswith('fonte "fallback"')

    linhas = []
    for codigo, p in playlists.items():
        ids = [i for i in (p.get('musicas') or []) if i in por_id]
        if not ids:
            continue
        total = len(ids)
        com_fonte = sum(1 for i in ids if por_id[i].get('fonte_audio'))
        com_tempos_a = sum(1 for i in ids if tem_tempos(por_id[i].get('trecho_a')))
        com_video = sum(1 for i in ids if por_id[i].get('video_local'))
        sem_fonte = total - com_fonte
        linhas.append({
            'codigo': codigo, 'nome': p.get('nome', ''), 'total': total,
            'com_fonte': com_fonte, 'sem_fonte': sem_fonte,
            'com_tempos_a': com_tempos_a, 'com_video': com_video,
            'pct': com_fonte / total,
        })

    linhas.sort(key=lambda l: (-l['pct'], -l['total']))

    print(f'{len(linhas)} packs com faixas (de {len(playlists)} entradas em playlists.json)\n')
    print(f'{"pack":<24}{"nome":<34}{"faixas":<8}{"fonte":<8}{"%":<7}'
          f'{"temposA":<9}{"vídeo":<7}marca')
    print('-' * 105)
    for l in linhas[:40]:
        marca = PILOTO.get(l['codigo'], '')
        print(f"{l['codigo']:<24}{l['nome'][:33]:<34}{l['total']:<8}{l['com_fonte']:<8}"
              f"{l['pct']:.0%}{'':<4}{l['com_tempos_a']:<9}{l['com_video']:<7}{marca}")
    if len(linhas) > 40:
        print(f'... ({len(linhas) - 40} packs não mostrados — limite de 40 linhas)')

    totais = {k: sum(l[k] for l in linhas) for k in ('total', 'com_fonte', 'com_tempos_a', 'com_video')}
    print('-' * 105)
    print(f"{'TOTAL':<24}{'':<34}{totais['total']:<8}{totais['com_fonte']:<8}"
          f"{totais['com_fonte']/totais['total']:.0%}{'':<4}"
          f"{totais['com_tempos_a']:<9}{totais['com_video']:<7}")

    # 10 packs com mais faixas SEM fonte_audio (em absoluto, não em %)
    print(f'\n{"="*105}')
    print('10 packs com MAIS faixas sem fonte_audio — quantas dessas são fonte "fallback" conhecida')
    print('(classificação só existe para faixas que passaram pela aprovação em lote de 11 Out)')
    print('='*105)
    piores = sorted(linhas, key=lambda l: -l['sem_fonte'])[:10]
    print(f'{"pack":<24}{"sem fonte":<12}{"fallback conhecida":<20}{"sem classificação"}')
    print('-' * 80)
    for l in piores:
        ids = [i for i in playlists[l['codigo']].get('musicas', []) if i in por_id
               and not por_id[i].get('fonte_audio')]
        fallback = sum(1 for i in ids if fallback_por_faixa.get(i) is True)
        sem_classificacao = sum(1 for i in ids if i not in fallback_por_faixa)
        print(f"{l['codigo']:<24}{l['sem_fonte']:<12}{fallback:<20}{sem_classificacao}")


if __name__ == '__main__':
    main()
