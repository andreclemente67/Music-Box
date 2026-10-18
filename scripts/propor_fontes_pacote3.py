#!/usr/bin/env python3
"""Propõe fonte_audio para os 3 packs seguintes depois de Cinema/
Bateria/Cancioneiro PT (ver propor_fontes_proximos3.py) — pedido do
André, 16 Out 2026.

Escolha dos 3 packs (critério: mais faixas sem fonte_audio, excluindo
os packs já feitos e os formatos "não-canção" — Retrato, Logótipos e
Tributo, todos com posições especiais/mistas em vez de trecho_a/trecho_b
uniforme): empate a 7/7 no topo — STD.INT.ALL.SYN.001 (Synthwave),
STD.PT.ALL.WLD.001 (Vozes da Terra). Para o 3º, empate a 6/7 entre 7
packs (RET.PT.90.VOZ.001 também excluído, é Retrato) — desempatado por
ordem alfabética do código, sem outro critério disponível:
STD.INT.10.MIX.001 (Anos 2010).

Acrescenta, por faixa, a comparação canal-vs-artista (heurística de
texto normalizado — nome do artista é substring do canal ou vice-versa,
ignorando "Topic"/"Official"/"Oficial"/"VEVO"). É só um sinal, não prova
nada: um canal de editora/banda sonora oficial pode legitimamente não
conter o nome do artista.

NÃO grava nada no catálogo. Sem cookies da conta pessoal. Sem
descarregar áudio (--skip-download). Ritmo lento (8s entre faixas).

Correr com:  python3 scripts/propor_fontes_pacote3.py
"""
import json
import os
import re
import subprocess
import sys
import time
import unicodedata

APP = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, APP)
import _servidor_escrita as motor  # noqa: E402

PACKS = ['STD.INT.ALL.SYN.001', 'STD.PT.ALL.WLD.001', 'STD.INT.10.MIX.001']
LIMIAR_DURACAO_S = 320.0
PAUSA_ENTRE_FAIXAS_S = 8.0
SAIDA_DIR = os.path.dirname(os.path.abspath(__file__))
SUFIXOS_CANAL = re.compile(r'\b(topic|official|oficial|vevo|music|records)\b')


def normalizar(s):
    s = unicodedata.normalize('NFKD', s or '').encode('ascii', 'ignore').decode('ascii').lower()
    return re.sub(r'[^a-z0-9 ]', '', s)


def canal_bate_artista(canal, artista):
    """True/False/None (canal desconhecido) — heurística de texto, não prova de autoria real."""
    if not canal:
        return None
    canal_n = SUFIXOS_CANAL.sub('', normalizar(canal)).strip()
    for parte in artista.split(','):
        parte_n = normalizar(parte.strip())
        if parte_n and (parte_n in canal_n or (canal_n and canal_n in parte_n)):
            return True
    return False


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


def slug(codigo):
    return codigo.lower().replace('.', '_')


def main():
    catalogo = {e['id']: e for e in json.load(open(os.path.join(APP, 'catalogo.json'), encoding='utf-8'))}
    playlists = json.load(open(os.path.join(APP, 'playlists.json'), encoding='utf-8'))

    tarefas = []
    for codigo in PACKS:
        for fid in playlists[codigo]['musicas']:
            entrada = catalogo[fid]
            if not entrada.get('fonte_audio'):
                tarefas.append((codigo, fid, entrada))

    print(f'{len(tarefas)} faixas sem fonte_audio nos 3 packs ({", ".join(PACKS)})\n')
    resultados_por_pack = {codigo: [] for codigo in PACKS}
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
            canal_ok = canal_bate_artista(canal, artista)
            linha.update({
                'ok': True,
                'url': f'https://www.youtube.com/watch?v={vid}',
                'titulo_yt': titulo_yt,
                'canal': canal,
                'canal_bate_artista': canal_ok,  # True | False | None (desconhecido)
                'classificacao': classificacao,
                'duracao_s': duracao,
                'duracao_acima_limiar': (duracao is not None and duracao > LIMIAR_DURACAO_S),
            })
            print(f'    {classificacao} | canal={canal} (bate artista: {canal_ok}) | {duracao}s | {titulo_yt}')
        resultados_por_pack[codigo].append(linha)

        if i < len(tarefas):
            time.sleep(PAUSA_ENTRE_FAIXAS_S)

    for codigo, linhas in resultados_por_pack.items():
        saida = os.path.join(SAIDA_DIR, f'propostas_fonte_{slug(codigo)}.json')
        json.dump(linhas, open(saida, 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
        print(f'{len(linhas)} propostas de {codigo} gravadas em {os.path.relpath(saida, APP)}')

    print('\nNADA foi escrito em catalogo.json/playlists.json.')


if __name__ == '__main__':
    main()
