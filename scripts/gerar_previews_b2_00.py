#!/usr/bin/env python3
"""Previews B_antes/B2_aplicado para os 5 B2 já aplicados em Anos 2000
(dec00_02/04/05/06/07, tag antes-b2-00) — pedido do André, 18 Out 2026.
Não altera dados (catalogo.json intocado, só leitura).

B_antes: cópia directa do <id>_b.mp3 de produção (ainda tem o conteúdo
antigo — a aplicação do B2 só mudou trecho_b.inicio/fim no catálogo,
nunca recortou um novo ficheiro, ver STATUS.md) — fonte garantidamente
correcta, sem depender de tmp_dl.

B2_aplicado: corte de 15s de tmp_dl/<id>_full.mp3 no novo `inicio` —
único sítio onde esse áudio existe hoje (ainda não foi recortado para
produção). Confirmado por correlação (ver scripts/gerar_audio_ext_dec00.py,
reaproveitado aqui): tmp_dl/<id>_full.mp3 destas 5 faixas NÃO bate com
confiança nem na posição antiga (0,09-0,32, muito abaixo do limiar
0,60) — o preview B2_aplicado fica sinalizado como “fonte não
confirmada” no index.md, não é para tomar como garantido.
"""
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gerar_audio_ext_dec00 as g  # noqa: E402 — reutiliza confirmar_fonte/pcm

APP_DIR = g.APP_DIR
OUT_DIR = os.path.join(APP_DIR, '_preview_revisao', 'b2_00')
IDS = ['dec00_02', 'dec00_04', 'dec00_05', 'dec00_06', 'dec00_07']


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    catalogo_antes = {e['id']: e for e in json.loads(subprocess.run(
        ['git', 'show', 'antes-b2-00:catalogo.json'], cwd=APP_DIR, capture_output=True, text=True
    ).stdout)}
    catalogo_atual = {e['id']: e for e in json.load(open(os.path.join(APP_DIR, 'catalogo.json'), encoding='utf-8'))}

    linhas = []
    for id_ in IDS:
        b_antes = catalogo_antes[id_]['trecho_b']
        b_atual = catalogo_atual[id_]['trecho_b']
        titulo = catalogo_atual[id_]['titulo']
        full_mp3 = os.path.join(APP_DIR, 'tmp_dl', f'{id_}_full.mp3')

        # B_antes — cópia directa do ficheiro de produção (já com o
        # conteúdo certo, nunca recortado de novo).
        origem_antes = os.path.join(APP_DIR, b_antes['ficheiro'])
        destino_antes = os.path.join(OUT_DIR, f'{id_}_B_antes.mp3')
        subprocess.run(['cp', origem_antes, destino_antes], check=True)
        dur_antes = float(subprocess.run(
            ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=nw=1:nk=1', destino_antes],
            capture_output=True, text=True
        ).stdout.strip())

        # B2_aplicado — corte de tmp_dl no novo inicio (sem fonte já
        # cortada disponível) + verificação de confiança da fonte.
        ok, motivo_corr = g.confirmar_fonte(id_, b_antes['ficheiro'], b_antes['inicio'], full_mp3)
        destino_depois = os.path.join(OUT_DIR, f'{id_}_B2_aplicado.mp3')
        duracao_nova = b_atual['fim'] - b_atual['inicio']
        g.cortar_ext(full_mp3, b_atual['inicio'], duracao_nova, destino_depois)
        dur_depois = float(subprocess.run(
            ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=nw=1:nk=1', destino_depois],
            capture_output=True, text=True
        ).stdout.strip())

        linhas.append({
            'id': id_, 'titulo': titulo,
            'b_antes': f"{b_antes['inicio']}-{b_antes['fim']}s", 'dur_antes': round(dur_antes, 2),
            'b2_aplicado': f"{b_atual['inicio']}-{b_atual['fim']}s", 'dur_depois': round(dur_depois, 2),
            'fonte_confirmada': ok, 'motivo_corr': motivo_corr,
        })
        print(id_, '-> B_antes', round(dur_antes, 2), 's | B2_aplicado', round(dur_depois, 2), 's | fonte confirmada:', ok)

    with open(os.path.join(OUT_DIR, '_linhas.json'), 'w', encoding='utf-8') as f:
        json.dump(linhas, f, indent=2, ensure_ascii=False)
    print('\nNada escrito em catalogo.json — só leitura.')


if __name__ == '__main__':
    main()
