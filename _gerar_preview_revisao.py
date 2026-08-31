#!/usr/bin/env python3
"""Gera uma pré-audição TEMPORÁRIA (Trecho A/B propostos) a partir de um
vídeo do YouTube, para o ecrã de revisão do Studio — nunca escreve em
<id>_a.mp3/<id>_b.mp3 (produção). Reutiliza descarregar_mp3_completo() e
cortar_trecho() de gerar_faixa.py e a análise de volume de
sugerir_trechos.py — mesma lógica do modo YouTube de gerar_faixa.py, só
muda o destino do corte e não escreve em produção.

Uso:
  python3 _gerar_preview_revisao.py <url_youtube> <id_faixa>

Saída (JSON numa linha, em stdout): {"ok": true, "tempo_a":.., "tempo_b":..,
"suspeito_tempo_a": bool, "ficheiro_proposta_a": "...", "ficheiro_proposta_b": "..."}
ou {"ok": false, "erro": "..."}.

O download completo do YouTube é sempre apagado no final (sucesso ou
falha) — só os dois cortes curtos (Trecho A/B propostos, ~15s cada)
ficam em disco, em _preview_revisao/. Pedido do utilizador, 2026-08-30:
"forma mais leve" de gerar a pré-audição sem manter faixas completas."""
import json
import os
import subprocess
import sys

APP_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, APP_DIR)
import gerar_faixa  # noqa: E402 — reutiliza descarregar_mp3_completo/cortar_trecho/TMP_DIR

PREVIEW_DIR = os.path.join(APP_DIR, '_preview_revisao')


def gerar_preview(url: str, id_faixa: str) -> dict:
    if not gerar_faixa.ID_REGEX.match(id_faixa):
        return {'ok': False, 'erro': f'id inválido: {id_faixa!r}'}

    os.makedirs(PREVIEW_DIR, exist_ok=True)
    destino_a = os.path.join(PREVIEW_DIR, f'{id_faixa}_a_proposta.mp3')
    destino_b = os.path.join(PREVIEW_DIR, f'{id_faixa}_b_proposta.mp3')

    # Metadados sempre confirmados contra o URL efectivamente usado (não a
    # busca original) — cobre tanto a proposta automática como uma "Corrigir
    # URL manualmente" no ecrã de revisão, sem duplicar caminhos no Studio.
    metadados = {}
    try:
        r = subprocess.run(
            ['yt-dlp', url, '--skip-download', '--no-playlist',
             '--print', '%(title)s|||%(channel)s|||%(duration)s'],
            capture_output=True, text=True, timeout=30,
        )
        partes = (r.stdout or '').strip().splitlines()
        if partes:
            t, c, d = partes[0].split('|||')
            metadados = {'video_titulo': t, 'video_canal': c, 'video_duracao_s': d}
    except Exception:
        pass  # não crítico — a pré-audição continua sem estes campos

    try:
        mp3_completo = gerar_faixa.descarregar_mp3_completo(url, id_faixa)
    except Exception as e:
        return {'ok': False, 'erro': f'falha no download: {e}', **metadados}

    try:
        tempo_a, tempo_b = gerar_faixa.sugerir_trechos.sugerir_trechos(
            mp3_completo, gerar_faixa.DURACAO_TRECHO)
        suspeito = tempo_a > gerar_faixa.LIMITE_TEMPO_A_SUSPEITO
        gerar_faixa.cortar_trecho(mp3_completo, tempo_a, destino_a)
        gerar_faixa.cortar_trecho(mp3_completo, tempo_b, destino_b)
    except Exception as e:
        return {'ok': False, 'erro': f'falha a analisar/cortar: {e}'}
    finally:
        # Nunca guarda a faixa completa — só os 2 cortes curtos (pedido do
        # utilizador, "forma mais leve" em vez de manter downloads inteiros).
        # Apaga só o ficheiro desta faixa, nunca gerar_faixa.TMP_DIR
        # inteira — é uma pasta PARTILHADA entre chamadas concorrentes
        # (REVISAO_CONCORRENCIA=2 em musicbox_studio.html gera várias
        # pré-audições em paralelo); um rmtree(TMP_DIR) feito por uma
        # chamada apagava o download de outra ainda a meio, corrompendo o
        # resultado dela sem erro visível. Bug real encontrado e corrigido
        # em 2026-08-31.
        if os.path.exists(mp3_completo):
            os.remove(mp3_completo)

    return {
        'ok': True,
        'tempo_a': tempo_a, 'tempo_b': tempo_b,
        'suspeito_tempo_a': suspeito,
        'ficheiro_proposta_a': os.path.relpath(destino_a, APP_DIR),
        'ficheiro_proposta_b': os.path.relpath(destino_b, APP_DIR),
        'video_url': url,
        **metadados,
    }


def main():
    if len(sys.argv) != 3:
        print(json.dumps({'ok': False, 'erro': 'uso: _gerar_preview_revisao.py <url> <id_faixa>'}))
        sys.exit(1)
    resultado = gerar_preview(sys.argv[1], sys.argv[2])
    print(json.dumps(resultado, ensure_ascii=False))
    sys.exit(0 if resultado.get('ok') else 1)


if __name__ == '__main__':
    main()
