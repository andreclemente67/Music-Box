#!/usr/bin/env python3
"""
MUSIC BOX — Analisar Trechos A (silêncio/fade-in + posição relativa)

Percorre catalogo.json e, para cada faixa com trecho_a.ficheiro, verifica:

  1. Silêncio/fade-in nos primeiros 3s do ficheiro local (trecho_a) — usa
     ffmpeg volumedetect sobre os primeiros 3s, mesmo padrão de
     sugerir_trechos.py (limiar -45dB: abaixo disso considera-se
     silêncio/fade-in perceptível).

  2. trecho_a.inicio depois de 50% da duração total da música original —
     só é possível calcular quando o catálogo tem AMBOS trecho_a.inicio
     (offset dentro da fonte original) e video (URL do YouTube, para
     descobrir a duração total da fonte). A maioria das entradas tem
     trecho_a.inicio=null (nunca foi registado onde o corte começa na
     fonte original — ver DECISIONS.md/creditos, mesmo caso encontrado em
     "Take On Me" 80_01) — essas ficam marcadas como "não avaliável", não
     "aprovadas": não há dados para decidir, não é o mesmo que "ok".
     Para as que têm os dois campos, pede só a DURAÇÃO ao yt-dlp
     (--skip-download, sem descarregar o vídeo) — rápido, sem gravar
     nada em disco.

Uso:
  python3 analisar_trechos_a.py                 # tudo (check 1 local + check 2 com rede p/ os poucos elegíveis)
  python3 analisar_trechos_a.py --sem-rede       # só check 1 (silêncio/fade-in), sem tocar na rede
  python3 analisar_trechos_a.py --json out.json  # além do relatório em texto, grava tudo em JSON
"""
import argparse
import json
import os
import re
import subprocess
import sys

APP_DIR = os.path.dirname(os.path.abspath(__file__))
CATALOGO_PATH = os.path.join(APP_DIR, 'catalogo.json')

LIMIAR_SILENCIO_DB = -45.0   # mesmo limiar de sugerir_trechos.py (V1.2)
JANELA_INICIO_S = 3          # primeiros N segundos a analisar para silêncio/fade-in
LIMITE_POSICAO_RELATIVA = 0.5  # 50% da duração total


def nome_artista(faixa):
    art = faixa.get('artista') or []
    return ' / '.join(art) if art else '?'


def volume_medio_inicio(caminho_mp3, janela_s=JANELA_INICIO_S):
    """mean_volume (dB) dos primeiros janela_s segundos — None se o
    ffmpeg falhar (ficheiro corrompido/demasiado curto/em falta)."""
    r = subprocess.run(
        ['ffmpeg', '-i', caminho_mp3, '-t', str(janela_s),
         '-af', 'volumedetect', '-vn', '-sn', '-dn', '-f', 'null', '-'],
        capture_output=True, text=True
    )
    m = re.search(r'mean_volume: ([-\d.]+) dB', r.stderr)
    return float(m.group(1)) if m else None


def duracao_ficheiro(caminho):
    r = subprocess.run(
        ['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
         '-of', 'default=noprint_wrappers=1:nokey=1', caminho],
        capture_output=True, text=True
    )
    try:
        return float(r.stdout.strip())
    except ValueError:
        return None


def duracao_youtube(url, timeout=20):
    """Duração (segundos) da fonte no YouTube, sem descarregar nada —
    só pede metadados (--skip-download). None se falhar (vídeo privado/
    removido, rede em baixo, etc.) — falha sempre para o lado seguro
    (marca como não avaliável, nunca finge um valor)."""
    try:
        r = subprocess.run(
            ['yt-dlp', '--skip-download', '--print', 'duration', url],
            capture_output=True, text=True, timeout=timeout
        )
        return float(r.stdout.strip())
    except (subprocess.TimeoutExpired, ValueError, FileNotFoundError):
        return None


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--sem-rede', action='store_true',
                         help='só faz o check 1 (silêncio/fade-in) — não chama yt-dlp para durações')
    parser.add_argument('--json', metavar='FICHEIRO', help='grava o relatório completo também em JSON')
    args = parser.parse_args()

    catalogo = json.load(open(CATALOGO_PATH, encoding='utf-8'))

    resultados = []
    sem_ficheiro = []
    silencio_fadein = []
    inicio_tardio = []
    nao_avaliaveis_check2 = []

    total = len(catalogo)
    for i, faixa in enumerate(catalogo, 1):
        fid = faixa.get('id', '?')
        trecho_a = faixa.get('trecho_a') or {}
        ficheiro = trecho_a.get('ficheiro')
        print(f'\r[{i}/{total}] {fid:<20}', end='', file=sys.stderr, flush=True)

        entrada = {
            'id': fid, 'titulo': faixa.get('titulo'), 'artista': nome_artista(faixa),
            'ficheiro': ficheiro,
        }

        if not ficheiro:
            entrada['erro'] = 'sem trecho_a.ficheiro no catalogo.json'
            sem_ficheiro.append(entrada)
            resultados.append(entrada)
            continue

        caminho = os.path.join(APP_DIR, ficheiro)
        if not os.path.isfile(caminho):
            entrada['erro'] = f'ficheiro não encontrado em disco: {ficheiro}'
            sem_ficheiro.append(entrada)
            resultados.append(entrada)
            continue

        # ── Check 1: silêncio/fade-in nos primeiros 3s ──────────────────
        vol = volume_medio_inicio(caminho)
        entrada['volume_medio_primeiros_3s_db'] = vol
        if vol is not None and vol < LIMIAR_SILENCIO_DB:
            entrada['silencio_ou_fadein'] = True
            silencio_fadein.append(entrada)
        else:
            entrada['silencio_ou_fadein'] = False

        # ── Check 2: trecho_a.inicio depois de 50% da duração total ────
        inicio = trecho_a.get('inicio')
        video = faixa.get('video')
        if inicio is None:
            entrada['check2'] = 'nao_avaliavel'
            entrada['motivo_nao_avaliavel'] = 'trecho_a.inicio não registado (null)'
            nao_avaliaveis_check2.append(entrada)
        elif not video or args.sem_rede:
            entrada['check2'] = 'nao_avaliavel'
            entrada['motivo_nao_avaliavel'] = (
                'sem campo "video" (YouTube) para saber a duração total' if not video
                else 'rede desligada (--sem-rede)'
            )
            nao_avaliaveis_check2.append(entrada)
        else:
            duracao_total = duracao_youtube(video)
            if duracao_total is None or duracao_total <= 0:
                entrada['check2'] = 'nao_avaliavel'
                entrada['motivo_nao_avaliavel'] = 'yt-dlp não conseguiu obter a duração (vídeo indisponível?)'
                nao_avaliaveis_check2.append(entrada)
            else:
                posicao_relativa = inicio / duracao_total
                entrada['duracao_total_s'] = round(duracao_total, 1)
                entrada['trecho_a_inicio_s'] = inicio
                entrada['posicao_relativa'] = round(posicao_relativa, 3)
                if posicao_relativa > LIMITE_POSICAO_RELATIVA:
                    entrada['check2'] = 'inicio_tardio'
                    inicio_tardio.append(entrada)
                else:
                    entrada['check2'] = 'ok'

        resultados.append(entrada)

    print('\r' + ' ' * 40 + '\r', end='', file=sys.stderr)  # limpa a linha de progresso

    # ── Relatório ────────────────────────────────────────────────────────
    print(f'\n{"="*72}\nANÁLISE DE TRECHOS A — {total} faixas em catalogo.json\n{"="*72}')

    print(f'\n--- 1) Começam com silêncio/fade-in nos primeiros {JANELA_INICIO_S}s '
          f'(volume médio < {LIMIAR_SILENCIO_DB}dB) — {len(silencio_fadein)} faixa(s) ---')
    if silencio_fadein:
        for e in sorted(silencio_fadein, key=lambda e: e['volume_medio_primeiros_3s_db']):
            print(f'  {e["id"]:<18} {e["titulo"]} — {e["artista"]}  '
                  f'({e["volume_medio_primeiros_3s_db"]:.1f}dB, {e["ficheiro"]})')
    else:
        print('  (nenhuma)')

    print(f'\n--- 2) trecho_a_inicio depois de {int(LIMITE_POSICAO_RELATIVA*100)}% da duração total '
          f'— {len(inicio_tardio)} faixa(s) avaliada(s) como tarde ---')
    if inicio_tardio:
        for e in sorted(inicio_tardio, key=lambda e: -e['posicao_relativa']):
            print(f'  {e["id"]:<18} {e["titulo"]} — {e["artista"]}  '
                  f'(início aos {e["trecho_a_inicio_s"]}s de {e["duracao_total_s"]}s = '
                  f'{e["posicao_relativa"]*100:.0f}%)')
    else:
        print('  (nenhuma)')

    print(f'\n--- Não avaliáveis para o check 2 (sem dados suficientes) — {len(nao_avaliaveis_check2)} faixa(s) ---')
    motivos = {}
    for e in nao_avaliaveis_check2:
        motivos.setdefault(e['motivo_nao_avaliavel'], 0)
        motivos[e['motivo_nao_avaliavel']] += 1
    for motivo, n in sorted(motivos.items(), key=lambda x: -x[1]):
        print(f'  {n:>3}× {motivo}')

    if sem_ficheiro:
        print(f'\n--- Ficheiro em falta/sem trecho_a — {len(sem_ficheiro)} faixa(s), excluídas dos checks ---')
        for e in sem_ficheiro:
            print(f'  {e["id"]:<18} {e["titulo"]} — {e.get("erro")}')

    print(f'\n{"="*72}\nResumo: {len(silencio_fadein)} com silêncio/fade-in · '
          f'{len(inicio_tardio)} com início tardio (de {total - len(nao_avaliaveis_check2) - len(sem_ficheiro)} avaliáveis) · '
          f'{len(nao_avaliaveis_check2)} não avaliáveis (check 2) · {len(sem_ficheiro)} sem ficheiro')

    if args.json:
        with open(args.json, 'w', encoding='utf-8') as f:
            json.dump({
                'silencio_ou_fadein': silencio_fadein,
                'inicio_tardio': inicio_tardio,
                'nao_avaliaveis_check2': nao_avaliaveis_check2,
                'sem_ficheiro': sem_ficheiro,
                'todos': resultados,
            }, f, indent=2, ensure_ascii=False)
        print(f'\nRelatório completo gravado em {args.json}')


if __name__ == '__main__':
    main()
