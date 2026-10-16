#!/usr/bin/env python3
"""Propõe fonte_audio para as faixas sem fonte dos 4 packs pedidos pelo
André (14 Out 2026) — STD.INT.80/00/50/60.MIX.001, 11 faixas no total.

NÃO grava nada no catálogo. Só escreve o JSON de propostas ao lado deste
script, para decisão humana (ouvir as marcadas "fallback"/">320s" antes
de qualquer aprovação).

Reutiliza a classificação Topic/Official Audio de
_servidor_escrita.py:_escolher_fonte_youtube() (motor de 9 Out 2026,
commit 41df8f9) — mesmas regex TITULO_FONTE_PROIBIDO/
TITULO_FONTE_OFFICIAL_AUDIO, mesma consulta "artista titulo". NÃO chama
essa função directamente: ela tem um 2º passo que repete a pesquisa com
--cookies-from-browser chrome se o YouTube responder "sign in to
confirm" — o André pediu explicitamente sem cookies da conta pessoal
para esta tarefa, por isso a pesquisa aqui é só a 1ª tentativa, sem
retry. Uma faixa que só dê esse erro fica sem proposta, não escondida.

Ritmo lento (pausa entre faixas) para não martelar o YouTube.

Correr com:  python3 scripts/propor_fontes_4packs.py
"""
import json
import os
import subprocess
import sys
import time

APP = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, APP)
import _servidor_escrita as motor  # noqa: E402 — só para reutilizar as regex/timeout, sem chamar main()

PACKS = ['STD.INT.80.MIX.001', 'STD.INT.00.MIX.001', 'STD.INT.50.MIX.001', 'STD.INT.60.MIX.001']
LIMIAR_DURACAO_S = 320.0
PAUSA_ENTRE_FAIXAS_S = 6.0
SAIDA = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'propostas_fonte_4packs.json')


def pesquisar_sem_cookies(consulta, timeout):
    """Mesma lógica de classificação de _escolher_fonte_youtube(), mas só
    a 1ª tentativa (sem --cookies-from-browser) — ver docstring do módulo."""
    try:
        r = subprocess.run(
            ['yt-dlp', 'ytsearch5:' + consulta, '--skip-download', '--no-playlist',
             '--print', '%(id)s|||%(title)s|||%(description)s'],
            cwd=APP, capture_output=True, text=True, timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        return None, None, None, f'pesquisa excedeu {timeout}s'
    except Exception as e:
        return None, None, None, f'falha a correr yt-dlp: {e}'

    if 'sign in to confirm' in (r.stderr or '').lower():
        return None, None, None, 'YouTube pediu "sign in to confirm" — sem cookies nesta tarefa, sem proposta'

    linhas = [l for l in (r.stdout or '').strip().splitlines() if l]
    candidatos = [p for p in (l.split('|||', 2) for l in linhas) if len(p) == 3]
    if not candidatos:
        return None, None, None, f'sem resultados: {(r.stderr or r.stdout or "").strip()[-300:]}'

    validos = [c for c in candidatos if not motor.TITULO_FONTE_PROIBIDO.search(c[1] or '')]
    if not validos:
        vid, tit, _ = candidatos[0]
        return vid, tit, 'sem_filtro', 'todos pareciam Video/MV/Live/Movie/Trailer/Scene/Teaser'

    topic = [c for c in validos if 'provided to youtube' in (c[2] or '').lower()]
    oficial = [c for c in validos if motor.TITULO_FONTE_OFFICIAL_AUDIO.search(c[1] or '')]
    vid, tit, _ = (topic or oficial or validos)[0]
    classificacao = 'topic' if topic else ('official_audio' if oficial else 'fallback')
    return vid, tit, classificacao, None


def obter_duracao(video_id, timeout):
    try:
        r = subprocess.run(
            ['yt-dlp', f'https://www.youtube.com/watch?v={video_id}', '--skip-download',
             '--no-playlist', '--print', '%(channel)s|||%(duration)s'],
            cwd=APP, capture_output=True, text=True, timeout=timeout,
        )
        partes = (r.stdout or '').strip().split('|||')
        if len(partes) == 2 and partes[1]:
            return partes[0], float(partes[1])
    except Exception:
        pass
    return None, None


def main():
    catalogo = {e['id']: e for e in json.load(open(os.path.join(APP, 'catalogo.json'), encoding='utf-8'))}
    playlists = json.load(open(os.path.join(APP, 'playlists.json'), encoding='utf-8'))

    tarefas = []
    for codigo in PACKS:
        for fid in playlists[codigo]['musicas']:
            entrada = catalogo[fid]
            if not entrada.get('fonte_audio'):
                tarefas.append((codigo, fid, entrada))

    print(f'{len(tarefas)} faixas sem fonte_audio nos 4 packs\n')
    resultados = []
    for i, (codigo, fid, entrada) in enumerate(tarefas, 1):
        titulo, artista = entrada['titulo'], ', '.join(entrada['artista'])
        consulta = f'{artista} {titulo}'
        print(f'[{i}/{len(tarefas)}] {fid} — {consulta} ...', flush=True)

        vid, titulo_yt, classificacao, erro = pesquisar_sem_cookies(consulta, motor.YT_SEARCH_TIMEOUT)
        linha = {'pack': codigo, 'faixa': fid, 'titulo': titulo, 'artista': artista,
                  'consulta': consulta}
        if erro:
            linha.update({'ok': False, 'erro': erro})
            print(f'    falhou: {erro}')
        else:
            canal, duracao = obter_duracao(vid, motor.YT_SEARCH_TIMEOUT)
            linha.update({
                'ok': True,
                'url': f'https://www.youtube.com/watch?v={vid}',
                'titulo_yt': titulo_yt,
                'canal': canal,
                'classificacao': classificacao,  # topic | official_audio | fallback | sem_filtro
                'duracao_s': duracao,
                'duracao_acima_limiar': (duracao is not None and duracao > LIMIAR_DURACAO_S),
            })
            print(f'    {classificacao} | canal={canal} | {duracao}s | {titulo_yt}')
        resultados.append(linha)

        if i < len(tarefas):
            time.sleep(PAUSA_ENTRE_FAIXAS_S)

    json.dump(resultados, open(SAIDA, 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
    print(f'\n{len(resultados)} propostas gravadas em {os.path.relpath(SAIDA, APP)}')
    print('NADA foi escrito em catalogo.json/playlists.json.')


if __name__ == '__main__':
    main()
