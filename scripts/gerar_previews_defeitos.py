#!/usr/bin/env python3
"""Gera pré-audições (NUNCA substitui ficheiros de produção) para as faixas
"defeito real" da reavaliação de 9 Out 2026, pelo motor novo de escolha de
fonte (Topic > Official Audio, nunca Video/MV/Live/Movie/Trailer/Scene/
Teaser — ver DECISIONS.md 2026-10-08/09) e carrega-as no ecrã "▶ Revisão
YouTube" do Studio (_revisao_regeneracao.json), agrupadas por pack.

Para cada faixa, por esta ordem (packs "prontas" com mais defeitos
primeiro, depois rascunho/protótipo, depois sem playlist):
  1. Escolhe UMA fonte (escolher_fonte — mesma função usada por
     /gerar-faixa, não testa vários candidatos como a reavaliação).
  2. Gera a pré-audição (_gerar_preview_revisao.gerar_preview): descarrega,
     sugere Trecho A/B, corta 15s cada, guarda em _preview_revisao/.
  3. Verifica (fingerprint + ruído) a pré-audição contra a mesma fonte.
  4. Se tudo OK: escreve/actualiza a entrada em _revisao_regeneracao.json
     (estado "pendente", para o André ouvir e aprovar/rejeitar no Studio).
     Se qualquer passo falhar (sem fonte, download bloqueado, verificador
     não dá OK): marca "por rever" no progresso, apaga a pré-audição
     gerada (se existir) e segue para a faixa seguinte — nunca bloqueia.

Grava o progresso a CADA faixa (relatorios/previews_defeitos_progresso.csv)
— retoma sozinho sem repetir trabalho se for interrompido.

Uso: scripts/.venv/bin/python3 scripts/gerar_previews_defeitos.py
"""
import csv
import json
import os
import sys

APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, APP_DIR)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import gerar_faixa  # noqa: E402
import _gerar_preview_revisao as gpr  # noqa: E402
import verificar_trechos as vt  # noqa: E402

MANIFESTO = os.path.join(APP_DIR, '_revisao_regeneracao.json')
PROGRESSO_PATH = os.path.join(APP_DIR, 'relatorios', 'previews_defeitos_progresso.csv')
REAVALIACAO_CSV = os.path.join(APP_DIR, 'relatorios', 'reavaliacao_falhas.csv')


def ordem_packs():
    """Packs 'prontas' (sem `estado` em playlists.json) com mais defeitos
    primeiro, depois rascunho/protótipo, depois '(sem playlist)' por fim —
    ordem pedida pelo André, 9 Out 2026."""
    with open(os.path.join(APP_DIR, 'playlists.json'), encoding='utf-8') as f:
        pl = json.load(f)
    estado_pack = {cod: (p.get('estado') or 'pronta') for cod, p in pl.items()}

    with open(REAVALIACAO_CSV, encoding='utf-8') as f:
        rows = [r for r in csv.DictReader(f) if r['categoria_final'] == 'defeito real']

    from collections import defaultdict
    por_pack = defaultdict(list)
    for r in rows:
        por_pack[r['pack'] or '(sem playlist)'].append(r['faixa'])

    prontas, outros, sem_pl = [], [], []
    for pack, ids in por_pack.items():
        if pack == '(sem playlist)':
            sem_pl.append((pack, ids))
        elif estado_pack.get(pack, 'pronta') == 'pronta':
            prontas.append((pack, ids))
        else:
            outros.append((pack, ids))
    prontas.sort(key=lambda x: -len(x[1]))
    outros.sort(key=lambda x: -len(x[1]))
    return prontas + outros + sem_pl


def carregar_progresso():
    if not os.path.exists(PROGRESSO_PATH):
        return {}
    with open(PROGRESSO_PATH, encoding='utf-8') as f:
        return {r['faixa']: r for r in csv.DictReader(f)}


def gravar_progresso(progresso):
    os.makedirs(os.path.dirname(PROGRESSO_PATH), exist_ok=True)
    with open(PROGRESSO_PATH, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['faixa', 'pack', 'resultado', 'motivo'])
        for r in progresso.values():
            w.writerow([r['faixa'], r['pack'], r['resultado'], r['motivo']])


def carregar_manifesto():
    if not os.path.exists(MANIFESTO):
        return {}
    with open(MANIFESTO, encoding='utf-8') as f:
        return json.load(f)


def gravar_manifesto(dados):
    with open(MANIFESTO, 'w', encoding='utf-8') as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)


def apagar_preview(resultado):
    for chave in ('ficheiro_proposta_a', 'ficheiro_proposta_b'):
        caminho = resultado.get(chave)
        if caminho:
            caminho_abs = os.path.join(APP_DIR, caminho)
            if os.path.exists(caminho_abs):
                os.remove(caminho_abs)


def processar_faixa(tid, pack, catalogo_por_id):
    faixa = catalogo_por_id.get(tid)
    if not faixa:
        return 'por rever', 'id não encontrado no catalogo.json actual'

    titulo = faixa.get('titulo', '')
    artista = ' '.join(faixa.get('artista') or [])
    trecho_a = faixa.get('trecho_a') or {}
    trecho_b = faixa.get('trecho_b') or {}

    url, titulo_yt, canal, duracao, aviso = vt.escolher_fonte(titulo, artista)
    if not url:
        return 'por rever', f'sem fonte: {aviso}'

    resultado = gpr.gerar_preview(url, tid)
    if not resultado.get('ok'):
        return 'por rever', f'download/corte falhou: {resultado.get("erro")}'

    try:
        caminho_fonte = vt.descarregar_para_cache(url)
        dur_fonte, fp_fonte = vt.fingerprint_fpcalc(caminho_fonte, fonte_completa=True)
    except Exception as e:
        apagar_preview(resultado)
        return 'por rever', f'verificador não conseguiu obter a fonte: {e}'

    res_a = vt.verificar_trecho(resultado['ficheiro_proposta_a'], caminho_fonte, dur_fonte, fp_fonte)
    res_b = vt.verificar_trecho(resultado['ficheiro_proposta_b'], caminho_fonte, dur_fonte, fp_fonte)
    limpo = res_a['estado'] == 'OK' and res_b['estado'] in ('OK', '(sem trecho_b)')
    if not limpo:
        apagar_preview(resultado)
        return 'por rever', f"verificador NOK: A={res_a['estado']} B={res_b['estado']}"

    manifesto = carregar_manifesto()
    manifesto[tid] = {
        'id': tid,
        'playlistCodigo': pack,  # nunca None — "(sem playlist)" é uma string estável (bug real 2026-10-10: null rebentava o .sort() da sidebar do Studio)
        'titulo': titulo,
        'artista': artista,
        'ficheiro_a': trecho_a.get('ficheiro'),
        'ficheiro_b': trecho_b.get('ficheiro'),
        'estado': 'pendente',
        'url': url,
        'url_manual': None,
        'video_titulo': resultado.get('video_titulo') or titulo_yt,
        'video_canal': resultado.get('video_canal') or canal,
        'video_duracao_s': resultado.get('video_duracao_s'),
        'tempo_a': resultado['tempo_a'],
        'tempo_b': resultado['tempo_b'],
        'suspeito_tempo_a': resultado['suspeito_tempo_a'],
        'ficheiro_proposta_a': resultado['ficheiro_proposta_a'],
        'ficheiro_proposta_b': resultado['ficheiro_proposta_b'],
        'video_url': url,
    }
    gravar_manifesto(manifesto)
    return 'ok', f'{titulo_yt or url}'


def main():
    progresso = carregar_progresso()
    grupos = ordem_packs()
    total = sum(len(ids) for _, ids in grupos)
    print(f'{total} faixas a processar, em {len(grupos)} packs (ordem: prontas > rascunho/protótipo > sem playlist)')

    catalogo_por_id = {t['id']: t for t in vt.carregar_catalogo()}

    for pack, ids in grupos:
        print(f'\n=== {pack} ({len(ids)} faixas) ===')
        for tid in ids:
            if tid in progresso:
                print(f'{tid:16} — já processado ({progresso[tid]["resultado"]}), a saltar')
                continue
            try:
                resultado, motivo = processar_faixa(tid, pack, catalogo_por_id)
            except Exception as e:
                resultado, motivo = 'por rever', f'erro inesperado: {e}'
            progresso[tid] = {'faixa': tid, 'pack': pack, 'resultado': resultado, 'motivo': motivo}
            print(f'{tid:16} — {resultado} ({motivo[:100]})')
            gravar_progresso(progresso)

    ok = sum(1 for r in progresso.values() if r['resultado'] == 'ok')
    rever = sum(1 for r in progresso.values() if r['resultado'] == 'por rever')
    print(f'\n— resumo — OK (pré-audição pronta): {ok} | por rever: {rever}')
    print(f'progresso: {PROGRESSO_PATH}')
    print(f'manifesto: {MANIFESTO}')


if __name__ == '__main__':
    main()
