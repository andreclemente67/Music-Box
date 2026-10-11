#!/usr/bin/env python3
"""Candidato B2 (regra "refrão mais intenso") para teste cego contra o B actual.

Usa analise_refrao.py (chroma CENS beat-sync + matriz de recorrência + RMS,
com LRCLIB como cross-check). NUNCA toca em catalogo.json, playlists.json
nem nos <id>_b.mp3 de produção: os candidatos saem como <id>_b2.mp3 em
estudos/trecho_b_regra_energia/ e o índice fica em mp3_index_b2.json
(dentro da pasta do estudo).

Precisa do venv com librosa (o Python 3.14 do sistema não o suporta):
  ~/.venvs/musicbox-audio/bin/python gerar_b2_teste_regra.py --faixa dec00_01
  ~/.venvs/musicbox-audio/bin/python gerar_b2_teste_regra.py --todas
  ~/.venvs/musicbox-audio/bin/python gerar_b2_teste_regra.py --todas --gerar-mp3
"""

import argparse
import json
import os
import subprocess
import sys

APP_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, APP_DIR)

import analise_refrao  # noqa: E402

PACK_OMISSAO = 'STD.INT.80.MIX.001'
ESTUDO_DIR = os.path.join(APP_DIR, 'estudos', 'trecho_b_regra_energia')
INDICE = os.path.join(ESTUDO_DIR, 'mp3_index_b2.json')


def carregar(pack: str):
    with open(os.path.join(APP_DIR, 'catalogo.json')) as f:
        catalogo = json.load(f)
    with open(os.path.join(APP_DIR, 'playlists.json')) as f:
        playlists = json.load(f)
    if pack not in playlists:
        sys.exit(f'pack desconhecido: {pack}')
    return {e['id']: e for e in catalogo}, playlists[pack]


def analisar(entrada: dict) -> dict:
    url = entrada.get('fonte_audio')
    if not url:
        return {'ok': False, 'id_faixa': entrada['id'], 'candidatos': [],
                'escolhido': None, 'lrclib': None, 'duracao_total_s': None,
                'criterio_escolha': '', 'mensagem': 'sem fonte_audio registada'}
    a, b = entrada['trecho_a'], entrada['trecho_b']
    return analise_refrao.analisar_refrao(
        id_faixa=entrada['id'],
        titulo=entrada['titulo'],
        artista=', '.join(entrada['artista']),
        url_youtube=url,
        trecho_a_inicio=a.get('inicio'),
        trecho_a_fim=a.get('fim'),
        ficheiro_trecho_a=os.path.join(APP_DIR, a['ficheiro']),
        ficheiro_trecho_b=os.path.join(APP_DIR, b['ficheiro']),
    )


def sobreposicao(x: dict, y: dict) -> float:
    """Fracção do trecho mais curto que os dois intervalos partilham."""
    inter = max(0.0, min(x['fim_s'], y['fim_s']) - max(x['inicio_s'], y['inicio_s']))
    menor = min(x['fim_s'] - x['inicio_s'], y['fim_s'] - y['inicio_s'])
    return inter / menor if menor > 0 else 0.0


def _intervalo(t: dict) -> str:
    """"12–27s", ou "não registado" — meio pack dos Anos 80 tem
    inicio/fim a null no catálogo (os mp3 existem, os tempos nunca foram
    gravados), e sem isto o diagnóstico rebentava a formatar None."""
    if t.get('inicio') is None or t.get('fim') is None:
        return 'não registado no catálogo'
    return f"{t['inicio']:.0f}–{t['fim']:.0f}s"


def mostrar_diagnostico(entrada: dict, r: dict):
    a, b = entrada['trecho_a'], entrada['trecho_b']
    print(f"\n{'='*78}")
    print(f"{entrada['id']} — {entrada['titulo']} ({', '.join(entrada['artista'])})")
    print(f"{'='*78}")
    print(f"duração do source : {r['duracao_total_s']:.1f}s" if r['duracao_total_s'] else 'duração: ?')
    for etiqueta, chave, t in (('A', 'trecho_a_usado', a), ('B', 'trecho_b_actual', b)):
        loc = r.get(chave)
        if loc and loc['origem'] == 'correlação':
            aviso = '' if loc.get('fiavel', True) else '  ATENÇÃO: pico fraco, source provavelmente diferente'
            print(f"Trecho {etiqueta} actual   : {loc['inicio_s']:.1f}–{loc['fim_s']:.1f}s "
                  f"(localizado por correlação, pico {loc['nitidez_pico']:.1f}x){aviso}")
        elif loc:
            print(f"Trecho {etiqueta} actual   : {loc['inicio_s']:.0f}–{loc['fim_s']:.0f}s (catálogo)")
        else:
            print(f"Trecho {etiqueta} actual   : {_intervalo(t)}")
    if r.get('lrclib'):
        print(f"LRCLIB            : {r['lrclib']['mensagem']}")
    if r.get('repeticao_max'):
        print(f"filtro repetição  : >= {r['limiar_repeticao']:.1f} "
              f"({analise_refrao.LIMIAR_REPETICAO_REL:.0%} do máximo {r['repeticao_max']:.1f})")

    if not r['candidatos']:
        print(f"\nsem candidatos: {r['mensagem']}")
        return

    print(f"\nOcorrências de refrão encontradas ({len(r['candidatos'])}):")
    print('-' * 78)
    print(f"{'janela (s)':<15}{'INTENS':<9}{'onset':<8}{'alta':<8}"
          f"{'rep':<7}{'RMS':<9}{'linhas':<8}{'situação'}")
    print('-' * 78)
    for c in r['candidatos']:
        letra = '—' if c['refrao_lirico'] is None else str(c['linhas_refrao'])
        marca = '  <<<' if r['escolhido'] is c else ''
        situacao = c['razao_rejeicao'] or 'válido'
        intens = f"{c['intensidade']:.3f}" if c['intensidade'] is not None else '—'
        onset_n = f"{c['onset_norm']:.2f}" if c['onset_norm'] is not None else '—'
        alta_n = f"{c['alta_norm']:.2f}" if c['alta_norm'] is not None else '—'
        print(f"{c['inicio_s']:>6.0f}–{c['fim_s']:<8.0f}{intens:<9}{onset_n:<8}{alta_n:<8}"
              f"{c['score_repeticao']:<7.1f}{c['rms']:<9.4f}{letra:<8}{situacao}{marca}")

    print('-' * 78)
    if r['escolhido']:
        e = r['escolhido']
        print(f"\nESCOLHIDO: {e['inicio_s']:.1f}–{e['fim_s']:.1f}s   "
              f"(intensidade {e['intensidade']:.3f} = "
              f"min(onset {e['onset_norm']:.2f}, alta {e['alta_norm']:.2f}))")
        print(f"critério : {r['criterio_escolha']}")
        if r.get('trecho_b_actual'):
            ba = r['trecho_b_actual']
            sobr = sobreposicao(ba, e)
            print(f"B actual : {ba['inicio_s']:.1f}–{ba['fim_s']:.1f}s  →  "
                  f"B2 novo: {e['inicio_s']:.1f}–{e['fim_s']:.1f}s  "
                  f"(desvio {e['inicio_s'] - ba['inicio_s']:+.1f}s, "
                  f"sobreposição {sobr:.0%})")
    else:
        print(f"\nsem escolha: {r['mensagem']}")


def gerar_mp3_b2(entrada: dict, escolhido: dict) -> str:
    """Corta o candidato B2 do source já em tmp_dl/ (nunca toca em produção)."""
    os.makedirs(ESTUDO_DIR, exist_ok=True)
    source = os.path.join(analise_refrao.gerar_faixa.TMP_DIR, f"{entrada['id']}_full.mp3")
    destino = os.path.join(ESTUDO_DIR, f"{entrada['id']}_b2.mp3")
    subprocess.run(
        ['ffmpeg', '-y', '-ss', str(escolhido['inicio_s']), '-i', source,
         '-t', str(analise_refrao.DURACAO_TRECHO_S), '-c:a', 'libmp3lame',
         '-q:a', '2', destino],
        check=True, capture_output=True,
    )
    return destino


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--pack', default=PACK_OMISSAO, help=f'playlist a analisar (omissão: {PACK_OMISSAO})')
    p.add_argument('--faixa', help='diagnóstico detalhado de uma faixa (ex.: 80_02)')
    p.add_argument('--todas', action='store_true', help='analisa as faixas do pack')
    p.add_argument('--gerar-mp3', action='store_true',
                   help='com --todas: corta também os <id>_b2.mp3 para o teste cego')
    args = p.parse_args()

    cat, playlist = carregar(args.pack)
    ids = playlist['musicas']

    if args.faixa:
        if args.faixa not in ids:
            sys.exit(f'{args.faixa} não pertence a {args.pack} ({", ".join(ids)})')
        mostrar_diagnostico(cat[args.faixa], analisar(cat[args.faixa]))
        return

    if not args.todas:
        print(f"{args.pack} — {playlist['nome']} ({len(ids)} faixas)")
        for i, fid in enumerate(ids, 1):
            e = cat[fid]
            fonte = 'ok' if e.get('fonte_audio') else 'SEM fonte_audio'
            print(f"  {i}. {fid:<12}{e['titulo']:<26}{fonte}")
        print('\n--faixa <id> para o diagnóstico de uma; --todas para as sete.')
        return

    resultados, indice = {}, {}
    for fid in ids:
        entrada = cat[fid]
        r = analisar(entrada)
        resultados[fid] = r
        mostrar_diagnostico(entrada, r)
        if args.gerar_mp3 and r['escolhido']:
            caminho = gerar_mp3_b2(entrada, r['escolhido'])
            e2, ba = r['escolhido'], r.get('trecho_b_actual')
            indice[fid] = {
                'titulo': entrada['titulo'],
                'artista': ', '.join(entrada['artista']),
                'b2': {
                    'ficheiro': os.path.relpath(caminho, APP_DIR),
                    'inicio': round(e2['inicio_s'], 3),
                    'fim': round(e2['fim_s'], 3),
                    'intensidade': round(e2['intensidade'], 4),
                    'onset_norm': round(e2['onset_norm'], 4),
                    'alta_norm': round(e2['alta_norm'], 4),
                    'repeticao': round(e2['score_repeticao'], 2),
                    'linhas_refrao': e2['linhas_refrao'],
                },
                # o B actual é o ficheiro de produção, inalterado; os
                # tempos vêm do catálogo quando lá estão e da correlação
                # contra o source quando não (ver localizar_trecho)
                'b_actual': {
                    'ficheiro': entrada['trecho_b']['ficheiro'],
                    'inicio': round(ba['inicio_s'], 3) if ba else None,
                    'fim': round(ba['fim_s'], 3) if ba else None,
                    'origem_tempos': ba['origem'] if ba else 'desconhecida',
                },
                'criterio': r['criterio_escolha'],
            }

    print(f"\n\n{'='*78}\nRESUMO — B actual vs B2 (repetição >= 70% + intensidade)\n{'='*78}")
    print(f"{'faixa':<9}{'título':<24}{'B actual':<15}{'B2 regra':<15}{'concordam?'}")
    print('-' * 78)
    concordam = divergem = indisponiveis = 0
    for fid in ids:
        r, e = resultados[fid], cat[fid]
        ba, b2 = r.get('trecho_b_actual'), r.get('escolhido')
        if not b2:
            actual = f"{ba['inicio_s']:.0f}–{ba['fim_s']:.0f}s" if ba else '?'
            veredicto = r['mensagem'][:28]
            novo = '—'
            indisponiveis += 1
        else:
            novo = f"{b2['inicio_s']:.0f}–{b2['fim_s']:.0f}s"
            if not ba:
                actual, veredicto = '?', 'B actual não localizado'
                indisponiveis += 1
            else:
                actual = f"{ba['inicio_s']:.0f}–{ba['fim_s']:.0f}s"
                sobr = sobreposicao(ba, b2)
                if sobr >= 0.5:
                    veredicto = f'SIM ({sobr:.0%} sobreposição)'
                    concordam += 1
                else:
                    veredicto = f'NÃO (desvio {b2["inicio_s"] - ba["inicio_s"]:+.0f}s)'
                    divergem += 1
        print(f"{fid:<9}{e['titulo'][:23]:<24}{actual:<15}{novo:<15}{veredicto}")

    print('-' * 78)
    print(f"concordam: {concordam}   divergem: {divergem}   "
          f"sem comparação possível: {indisponiveis}")

    if indice:
        os.makedirs(ESTUDO_DIR, exist_ok=True)
        with open(INDICE, 'w') as f:
            json.dump(indice, f, indent=2, ensure_ascii=False)
        print(f"\n{len(indice)} candidatos B2 escritos em {os.path.relpath(ESTUDO_DIR, APP_DIR)}/")
        print(f"índice: {os.path.relpath(INDICE, APP_DIR)}")


if __name__ == '__main__':
    main()
