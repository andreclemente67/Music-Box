#!/usr/bin/env python3
"""Repete a proposta de fonte da cinema_02 (falhou por timeout na corrida
de propor_fontes_proximos3.py, 16 Out 2026) — pedido do André, 1 único
retry, ritmo lento. Mesma lógica de propor_fontes_proximos3.py.

NÃO grava nada no catálogo. Sem cookies da conta pessoal. Sem
descarregar áudio (--skip-download).

Correr com:  python3 scripts/retry_fonte_cinema_02.py
"""
import json
import os
import subprocess
import sys
import time

APP = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, APP)
import _servidor_escrita as motor  # noqa: E402

FAIXA = 'cinema_02'
PACK = 'STD.INT.ALL.CIN.001'
LIMIAR_DURACAO_S = 320.0
PAUSA_ANTES_RETRY_S = 10.0
SAIDA = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'propostas_fonte_std_int_all_cin_001.json')


def pesquisar_sem_cookies(consulta, timeout):
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


def tentar(consulta):
    return pesquisar_sem_cookies(consulta, motor.YT_SEARCH_TIMEOUT)


def main():
    catalogo = {e['id']: e for e in json.load(open(os.path.join(APP, 'catalogo.json'), encoding='utf-8'))}
    entrada = catalogo[FAIXA]
    titulo, artista = entrada['titulo'], ', '.join(entrada['artista'])
    consulta = f'{artista} {titulo}'

    print(f'{FAIXA} — {consulta} — tentativa 1...', flush=True)
    vid, titulo_yt, classificacao, erro = tentar(consulta)

    if erro:
        print(f'  tentativa 1 falhou: {erro}')
        print(f'  a aguardar {PAUSA_ANTES_RETRY_S}s antes do retry único...')
        time.sleep(PAUSA_ANTES_RETRY_S)
        print(f'{FAIXA} — {consulta} — tentativa 2 (retry único)...', flush=True)
        vid, titulo_yt, classificacao, erro = tentar(consulta)

    if erro:
        linha = {'pack': PACK, 'faixa': FAIXA, 'titulo': titulo, 'artista': artista,
                  'consulta': consulta, 'ok': False, 'erro': f'falhou nas 2 tentativas — última: {erro}'}
        print(f'  falhou outra vez: {erro}')
    else:
        canal, duracao = obter_duracao(vid, motor.YT_SEARCH_TIMEOUT)
        linha = {'pack': PACK, 'faixa': FAIXA, 'titulo': titulo, 'artista': artista,
                  'consulta': consulta, 'ok': True,
                  'url': f'https://www.youtube.com/watch?v={vid}', 'titulo_yt': titulo_yt,
                  'canal': canal, 'classificacao': classificacao, 'duracao_s': duracao,
                  'duracao_acima_limiar': (duracao is not None and duracao > LIMIAR_DURACAO_S)}
        print(f'  sucesso: {classificacao} | canal={canal} | {duracao}s | {titulo_yt}')

    dados = json.load(open(SAIDA, encoding='utf-8'))
    dados = [linha if r['faixa'] == FAIXA else r for r in dados]
    json.dump(dados, open(SAIDA, 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
    print(f'\n{FAIXA} actualizada em {os.path.relpath(SAIDA, APP)}. NADA escrito no catálogo.')


if __name__ == '__main__':
    main()
