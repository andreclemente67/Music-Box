#!/usr/bin/env python3
"""Aplica a regeneração DEFINITIVA das faixas "aprovado" de UMA playlist,
a partir das decisões já tomadas no ecrã de Revisão YouTube do Studio.

Para cada faixa "aprovado" da playlist:
  1. Move (nunca apaga) <id>_a.mp3/<id>_b.mp3 de produção para
     _backup_pre_regeneracao/ — só se ainda não tiver sido feito antes
     (idempotente, seguro correr duas vezes).
  2. Move a pré-audição já revista (_preview_revisao/<id>_a_proposta.mp3,
     gerada e ouvida no ecrã de revisão — não gera um corte novo aqui,
     promove exactamente o que foi aprovado) para <id>_a.mp3 de produção.
  3. Marca a faixa como "regenerado" no manifesto (_revisao_regeneracao.json).

Faixas "rejeitado" ficam sempre intocadas. Faixas ainda "pendente" também
não são tocadas (reportadas, não deviam existir se a playlist estiver
100% revista — ver renderRevisaoCards() no Studio).

NUNCA faz commit — isso é sempre uma acção manual e explícita do
utilizador, fora deste script (ver DECISIONS.md 2026-08-31).

Uso: python3 _aplicar_regeneracao_playlist.py <playlistCodigo>
Saída (JSON, stdout): {"ok": true, "playlistCodigo":..., "regeneradas": [...],
"rejeitadas": [...], "pendentes": [...], "erros": [...]}"""
import json
import os
import shutil
import sys

APP_DIR = os.path.dirname(os.path.abspath(__file__))
MANIFESTO = os.path.join(APP_DIR, '_revisao_regeneracao.json')
BACKUP_DIR = os.path.join(APP_DIR, '_backup_pre_regeneracao')


def aplicar(playlist_codigo: str) -> dict:
    if not os.path.exists(MANIFESTO):
        return {'ok': False, 'erro': 'não existe _revisao_regeneracao.json'}
    with open(MANIFESTO, encoding='utf-8') as f:
        dados = json.load(f)

    faixas = {tid: e for tid, e in dados.items() if e.get('playlistCodigo') == playlist_codigo}
    if not faixas:
        return {'ok': False, 'erro': f'nenhuma faixa encontrada para {playlist_codigo!r} no manifesto'}

    regeneradas, ja_regeneradas, rejeitadas, pendentes, erros = [], [], [], [], []
    os.makedirs(BACKUP_DIR, exist_ok=True)

    for tid, e in faixas.items():
        estado = e.get('estado', 'pendente')
        if estado == 'rejeitado':
            rejeitadas.append(tid)
            continue
        if estado == 'regenerado':
            ja_regeneradas.append(tid)  # já processada numa corrida anterior — idempotente
            continue
        if estado != 'aprovado':
            pendentes.append(tid)
            continue

        fa, fb = e.get('ficheiro_a'), e.get('ficheiro_b')
        pa, pb = e.get('ficheiro_proposta_a'), e.get('ficheiro_proposta_b')
        if not (pa and pb and os.path.exists(os.path.join(APP_DIR, pa)) and os.path.exists(os.path.join(APP_DIR, pb))):
            erros.append({'id': tid, 'erro': 'pré-audição aprovada em falta em disco — não regenerado'})
            continue

        try:
            for original, proposta in ((fa, pa), (fb, pb)):
                origem = os.path.join(APP_DIR, original)
                destino_backup = os.path.join(BACKUP_DIR, original)
                if os.path.exists(origem) and not os.path.exists(destino_backup):
                    shutil.move(origem, destino_backup)
                shutil.move(os.path.join(APP_DIR, proposta), origem)
            e['estado'] = 'regenerado'
            e['ficheiro_proposta_a'] = None
            e['ficheiro_proposta_b'] = None
            regeneradas.append(tid)
        except Exception as ex:
            erros.append({'id': tid, 'erro': str(ex)})

    with open(MANIFESTO, 'w', encoding='utf-8') as f:
        json.dump(dados, f, indent=2, ensure_ascii=False)

    return {
        'ok': True,
        'playlistCodigo': playlist_codigo,
        'regeneradas': regeneradas,
        'ja_regeneradas': ja_regeneradas,
        'rejeitadas': rejeitadas,
        'pendentes': pendentes,
        'erros': erros,
    }


def main():
    if len(sys.argv) != 2:
        print(json.dumps({'ok': False, 'erro': 'uso: _aplicar_regeneracao_playlist.py <playlistCodigo>'}))
        sys.exit(1)
    resultado = aplicar(sys.argv[1])
    print(json.dumps(resultado, ensure_ascii=False))
    sys.exit(0 if resultado.get('ok') else 1)


if __name__ == '__main__':
    main()
