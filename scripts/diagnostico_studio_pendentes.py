#!/usr/bin/env python3
"""Números para a página "O que falta fazer" do Studio — só leitura.

(a) aprovadas por aplicar; (b) por rever/ouvir; (c) sem fonte_audio;
(d) sem imagem; (e) Trecho B p/ revisão manual (<0,15 ou >75%);
(f) inconclusivos do verificador; (g) faixas órfãs (nenhuma playlist).

Não escreve em catalogo.json/playlists.json/_revisao_regeneracao.json.
Correr com:  python3 scripts/diagnostico_studio_pendentes.py
"""
import csv
import json
import os

APP = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def caminho(*p):
    return os.path.join(APP, *p)


def main():
    catalogo = json.load(open(caminho('catalogo.json'), encoding='utf-8'))
    playlists = json.load(open(caminho('playlists.json'), encoding='utf-8'))
    revisao = json.load(open(caminho('_revisao_regeneracao.json'), encoding='utf-8'))

    # ids referenciados por QUALQUER playlist, via "musicas" (maioria) ou
    # "posicoes" (tipo tributo — ver DECISIONS.md 11 Out)
    ids_em_playlist = set()
    for p in playlists.values():
        ids_em_playlist.update(p.get('musicas') or [])
        for pos in (p.get('posicoes') or []):
            if pos.get('id'):
                ids_em_playlist.add(pos['id'])
        mosaico_id = (p.get('mosaico') or {}).get('id')
        if mosaico_id:
            ids_em_playlist.add(mosaico_id)

    todos_ids = {e['id'] for e in catalogo}

    # (a) aprovadas por aplicar
    aprovadas = [v for v in revisao.values() if v.get('estado') == 'aprovado']
    packs_aprovadas = {v['playlistCodigo'] for v in aprovadas if v.get('playlistCodigo')}

    # (b) por rever/ouvir — pendentes no manifesto da Revisão + pendentes
    # da aprovação em lote (mesmo universo, fontes diferentes: o
    # manifesto cobre as 95 pré-audições de 9 Out, o CSV cobre as 76 que
    # já tinham pré-audição quando a aprovação em lote correu — podem
    # sobrepor-se, por isso contam-se também em separado)
    pendentes_revisao = [v for v in revisao.values() if v.get('estado') == 'pendente']
    lote = list(csv.DictReader(open(caminho('relatorios', 'aprovacao_lote_progresso.csv'), encoding='utf-8')))
    pendentes_lote = [r for r in lote if r['resultado'] == 'pendente']
    ids_revisao_pend = {v['id'] for v in pendentes_revisao}
    ids_lote_pend = {r['faixa'] for r in pendentes_lote}
    uniao_pendentes = ids_revisao_pend | ids_lote_pend

    # (c) sem fonte_audio — catálogo inteiro e só as em playlist
    sem_fonte = [e['id'] for e in catalogo if not e.get('fonte_audio')]
    sem_fonte_em_playlist = [i for i in sem_fonte if i in ids_em_playlist]

    # (d) sem imagem
    sem_imagem = [e['id'] for e in catalogo if not e.get('imagem')]

    # (e) Trecho B para revisão manual — só entre as faixas já analisadas
    # pela regra "refrão mais intenso" nesta sessão (7 faixas, não o
    # catálogo todo: correr a análise chroma nas 348 não está ao
    # alcance de "um script curto", precisa de source + minutos por
    # faixa). Os valores vêm de scripts/propostas_fonte_4packs.json? NÃO
    # — essa é outra coisa (fontes, não B2). Os valores de confluência
    # só existem nos outputs já mostrados ao André (STATUS.md/DECISIONS.md),
    # não há ficheiro próprio: hardcoded aqui a partir desses outputs,
    # claramente marcados como "amostra", não como cobertura do catálogo.
    amostra_b2 = {
        # faixa: (confluencia, pct_fim)
        '80_02': (0.356, 0.41), '80_04': (0.074, 0.84), '80_05': (0.328, 0.44),
        '80_06': (0.346, 0.72), '80_07': (0.391, 0.77),
        'dec00_01': (0.927, 0.68), 'dec00_06': (0.303, 0.39),
    }
    revisao_manual_b2 = [f for f, (conf, pct) in amostra_b2.items() if conf < 0.15 or pct > 0.75]

    # (f) inconclusivos do verificador
    reavaliacao = list(csv.DictReader(open(caminho('relatorios', 'reavaliacao_falhas.csv'), encoding='utf-8')))
    inconclusivos = [r['faixa'] for r in reavaliacao if r['categoria_final'] == 'inconclusivo']

    # (g) faixas do catálogo não usadas em nenhuma playlist
    orfas = sorted(todos_ids - ids_em_playlist)

    print(f"{'':<4}{'métrica':<46}{'valor'}")
    print('-' * 70)
    print(f"(a) {'aprovadas por aplicar':<46}{len(aprovadas)} faixas, {len(packs_aprovadas)} playlists")
    print(f"(b) {'por rever/ouvir (revisão)':<46}{len(pendentes_revisao)}")
    print(f"    {'por rever/ouvir (aprovação em lote)':<46}{len(pendentes_lote)}")
    print(f"    {'união (sem duplicar)':<46}{len(uniao_pendentes)}")
    print(f"(c) {'sem fonte_audio — catálogo':<46}{len(sem_fonte)}/{len(catalogo)}")
    print(f"    {'sem fonte_audio — em alguma playlist':<46}{len(sem_fonte_em_playlist)}/{len(ids_em_playlist)}")
    print(f"(d) {'sem imagem — catálogo':<46}{len(sem_imagem)}/{len(catalogo)}")
    print(f"(e) {'Trecho B p/ revisão manual (AMOSTRA 7 faixas)':<46}{len(revisao_manual_b2)}/7  {revisao_manual_b2}")
    print(f"(f) {'inconclusivos do verificador':<46}{len(inconclusivos)}")
    print(f"(g) {'faixas não usadas em nenhuma playlist':<46}{len(orfas)}  {orfas}")

    if aprovadas:
        print('\naprovadas por aplicar, por pack:')
        from collections import Counter
        for codigo, n in Counter(v['playlistCodigo'] for v in aprovadas).most_common():
            print(f'   {codigo}: {n}')


if __name__ == '__main__':
    main()
