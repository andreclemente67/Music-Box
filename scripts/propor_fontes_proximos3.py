#!/usr/bin/env python3
"""Propõe fonte_audio para os 3 packs com mais faixas em falta depois dos
4 packs de demo já feitos (STD.INT.80/00/50/60.MIX.001, ver
propor_fontes_4packs.py) — pedido do André, 16 Out 2026.

Escolha dos 3 packs (critério: mais faixas sem fonte_audio, excluindo os
4 já feitos): havia um empate a 7-8 faltas entre vários; dos candidatos
no topo, ficaram de fora RET.INT.ALL.VOZ.001 ("Retrato", mecânica de voz,
não trechos de música) e LOGO-001 (jingles/stings, não canções — fonte
de áudio é um problema diferente). Escolhidos os 3 packs "standard"
(mesma mecânica trecho_a/trecho_b de sempre) com mais faltas:
STD.INT.ALL.CIN.001 (Cinema & Música), STD.INT.ALL.BAT.001 (Solo de
Bateria), STD.PT.ALL.FAD.001 (Cancioneiro Português) — 7 faixas cada,
sem contar a posição `mosaico` de cada pack (mesmo âmbito do script dos
4 packs de demo, que também só trata `musicas`).

NÃO grava nada no catálogo. Sem cookies da conta pessoal (só a 1ª
tentativa de pesquisa, sem retry com --cookies-from-browser). Sem
descarregar áudio — só metadados (yt-dlp --skip-download). Ritmo lento
(8s entre faixas) para não martelar o YouTube.

Correr com:  python3 scripts/propor_fontes_proximos3.py
"""
import json
import os
import subprocess
import sys
import time

APP = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, APP)
import _servidor_escrita as motor  # noqa: E402 — só para reutilizar as regex/timeout, sem chamar main()

PACKS = ['STD.INT.ALL.CIN.001', 'STD.INT.ALL.BAT.001', 'STD.PT.ALL.FAD.001']
LIMIAR_DURACAO_S = 320.0
PAUSA_ENTRE_FAIXAS_S = 8.0
SAIDA_DIR = os.path.dirname(os.path.abspath(__file__))


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
