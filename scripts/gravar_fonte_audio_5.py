#!/usr/bin/env python3
"""Grava fonte_audio (campo "data" -> "fonte_audio") para 5 faixas
aprovadas pelo André em 14 Out 2026 — as 5 propostas limpas (Topic/
Official Audio, <=320s) de scripts/propostas_fonte_4packs.json.

Edição de texto cirúrgica (não json.dump do catálogo inteiro) para o
diff ficar restrito às 5 linhas novas, sem reformatar o resto do
ficheiro. Confirma por faixa que fonte_audio estava vazio antes de
escrever — nunca sobrepõe um valor já existente.

Correr com:  python3 scripts/gravar_fonte_audio_5.py
"""
import json
import os

APP = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CATALOGO = os.path.join(APP, 'catalogo.json')

APROVADAS = ['dec00_03', 'dec00_05', 'dec50_02', 'dec50_03', 'dec60_02']


def main():
    catalogo = json.load(open(CATALOGO, encoding='utf-8'))
    por_id = {e['id']: e for e in catalogo}
    propostas = {p['faixa']: p for p in
                 json.load(open(os.path.join(APP, 'scripts', 'propostas_fonte_4packs.json'), encoding='utf-8'))}

    for fid in APROVADAS:
        entrada = por_id[fid]
        if entrada.get('fonte_audio'):
            raise SystemExit(f'{fid} já tem fonte_audio ({entrada["fonte_audio"]!r}) — nada escrito')
        if fid not in propostas or not propostas[fid].get('ok'):
            raise SystemExit(f'{fid} sem proposta válida em propostas_fonte_4packs.json')

    linhas = open(CATALOGO, encoding='utf-8').read().split('\n')
    escritas = []
    for fid in APROVADAS:
        url = propostas[fid]['url']
        idx_id = next(i for i, l in enumerate(linhas) if l.strip() == f'"id": "{fid}",')
        # limite do bloco desta faixa: até ao próximo "id": (ou fim do ficheiro)
        idx_fim = next((i for i in range(idx_id + 1, len(linhas))
                        if linhas[i].strip().startswith('"id": "')), len(linhas))
        idx_data = next(i for i in range(idx_id, idx_fim)
                        if linhas[i].strip().startswith('"data":'))
        indent = linhas[idx_data][:len(linhas[idx_data]) - len(linhas[idx_data].lstrip())]
        linhas.insert(idx_data + 1, f'{indent}"fonte_audio": "{url}",')
        escritas.append((fid, url))

    open(CATALOGO, 'w', encoding='utf-8').write('\n'.join(linhas))

    print(f'{len(escritas)} faixas actualizadas:')
    for fid, url in escritas:
        print(f'  {fid} -> {url}')


if __name__ == '__main__':
    main()
