#!/usr/bin/env python3
"""ENSAIO (dry-run) da regeneração de STD.INT.00.MIX.001 (Anos 2000).

Replica a LÓGICA de decisão de `_aplicar_regeneracao_playlist.py` para esta
playlist sem mover/escrever nenhum ficheiro de produção, backup ou manifesto —
só lê e reporta o que aconteceria. Gera também previews (cópias, nunca cortes
novos de fonte não confirmada) em `_preview_revisao/regen_00/` e grava o
resultado em `relatorios/regen_00_ensaio.json`.

Pedido do André, 18 Out 2026 — ponto 2/3 da regeneração Anos 2000.
"""
import json
import os
import shutil
import subprocess

APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MANIFESTO = os.path.join(APP_DIR, '_revisao_regeneracao.json')
BACKUP_DIR = os.path.join(APP_DIR, '_backup_pre_regeneracao')
OUT_DIR = os.path.join(APP_DIR, '_preview_revisao', 'regen_00')
PLAYLIST = 'STD.INT.00.MIX.001'
IDS_ENSAIO = [f'dec00_0{i}' for i in range(2, 8)]  # dec00_02..dec00_07 (01 fica de fora, vídeo calibrado)


def duracao(caminho):
    if not os.path.exists(caminho):
        return None
    r = subprocess.run(
        ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=nw=1:nk=1', caminho],
        capture_output=True, text=True)
    s = r.stdout.strip()
    return round(float(s), 2) if s else None


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    manifesto = json.load(open(MANIFESTO, encoding='utf-8'))
    catalogo = {e['id']: e for e in json.load(open(os.path.join(APP_DIR, 'catalogo.json'), encoding='utf-8'))}

    resultado = {}
    for tid in IDS_ENSAIO:
        e = manifesto.get(tid)
        cat = catalogo[tid]
        linha = {'titulo': cat['titulo'], 'no_manifesto': e is not None}
        if e is None:
            linha['decisao_script'] = 'sem entrada no manifesto — _aplicar_regeneracao_playlist.py não teria nada a fazer'
            resultado[tid] = linha
            for lado, suf in (('trecho_a', 'A'), ('trecho_b', 'B')):
                origem = os.path.join(APP_DIR, cat[lado]['ficheiro'])
                destino = os.path.join(OUT_DIR, f'{tid}_{suf}_actual.mp3')
                if os.path.exists(origem):
                    shutil.copy2(origem, destino)
            continue

        estado = e.get('estado', 'pendente')
        linha['estado_manifesto'] = estado
        fa, fb = e.get('ficheiro_a'), e.get('ficheiro_b')
        pa, pb = e.get('ficheiro_proposta_a'), e.get('ficheiro_proposta_b')

        if estado == 'rejeitado':
            linha['decisao_script'] = 'rejeitado — ficaria intocada'
        elif estado == 'regenerado':
            linha['decisao_script'] = 'já regenerado (idempotente) — ficaria intocada'
        elif estado != 'aprovado':
            linha['decisao_script'] = f'estado "{estado}" não é "aprovado" — ficaria intocada (pendente)'
        else:
            proposta_existe = bool(pa and pb and os.path.exists(os.path.join(APP_DIR, pa)) and os.path.exists(os.path.join(APP_DIR, pb)))
            if not proposta_existe:
                linha['decisao_script'] = 'aprovado mas pré-audição em falta em disco — erro, não regenerado'
            else:
                backup_a_existe = os.path.exists(os.path.join(BACKUP_DIR, fa))
                backup_b_existe = os.path.exists(os.path.join(BACKUP_DIR, fb))
                linha['decisao_script'] = (
                    'aprovado + pré-audição em disco — O SCRIPT TROCARIA ' + fa + '/' + fb +
                    ' pela pré-audição agora, SEM criar novo backup (' +
                    ('backup A e B já existem — ficariam o estado ANTERIOR a esta troca, não o actual' if backup_a_existe and backup_b_existe
                     else 'backup em falta — seria criado agora, a partir do ficheiro ACTUAL em produção')
                    + ')'
                )
                linha['ficheiros_que_seriam_escritos'] = [fa, fb]
                linha['backup_a_ja_existe'] = backup_a_existe
                linha['backup_b_ja_existe'] = backup_b_existe

        # Trecho A/B actual (catálogo) vs proposto (manifesto)
        for lado, suf, tempo_key in (('trecho_a', 'A', 'tempo_a'), ('trecho_b', 'B', 'tempo_b')):
            t = cat[lado]
            origem = os.path.join(APP_DIR, t['ficheiro'])
            destino_actual = os.path.join(OUT_DIR, f'{tid}_{suf}_actual.mp3')
            if os.path.exists(origem):
                shutil.copy2(origem, destino_actual)
            linha[lado] = {
                'actual_catalogo_inicio_fim': f"{t['inicio']}-{t['fim']}s",
                'actual_ficheiro_duracao_s': duracao(origem),
                'proposto_tempo_manifesto_s': e.get(tempo_key),
            }
            proposta_path = pa if suf == 'A' else pb
            if proposta_path and os.path.exists(os.path.join(APP_DIR, proposta_path)):
                destino_novo = os.path.join(OUT_DIR, f'{tid}_{suf}_novo.mp3')
                shutil.copy2(os.path.join(APP_DIR, proposta_path), destino_novo)
                linha[lado]['proposto_ficheiro_duracao_s'] = duracao(os.path.join(APP_DIR, proposta_path))
                # áudio estendido (Trecho + 10s) a partir do tmp_dl full, só para preview — não grava em assets/
                full_mp3 = os.path.join(APP_DIR, 'tmp_dl', f'{tid}_full.mp3')
                tempo_inicio = e.get(tempo_key)
                if os.path.exists(full_mp3) and tempo_inicio is not None:
                    destino_ext = os.path.join(OUT_DIR, f'{tid}_{suf}_novo_ext10s.mp3')
                    dur_base = duracao(os.path.join(APP_DIR, proposta_path)) or 15.0
                    cmd = ['ffmpeg', '-y', '-v', 'error', '-ss', str(tempo_inicio), '-t', str(dur_base + 10),
                           '-i', full_mp3, '-c', 'copy', destino_ext]
                    r = subprocess.run(cmd, capture_output=True, text=True)
                    linha[lado]['ext10s_gerado'] = r.returncode == 0

        resultado[tid] = linha
        print(tid, '->', linha['decisao_script'])

    out = os.path.join(APP_DIR, 'relatorios', 'regen_00_ensaio.json')
    json.dump(resultado, open(out, 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
    print('\nGravado:', os.path.relpath(out, APP_DIR))
    print('Previews em:', os.path.relpath(OUT_DIR, APP_DIR))
    print('ENSAIO — nada escrito em catalogo.json/playlists.json/mp3_index.json/assets/, nenhum ficheiro de produção movido, nenhum backup criado, manifesto não tocado.')


if __name__ == '__main__':
    main()
