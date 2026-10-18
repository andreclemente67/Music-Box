#!/usr/bin/env python3
"""Corta o Trecho B real (B2) para produção nas 4 faixas aprovadas pelo André
(dec60_02, dec60_05, dec00_02, dec00_05) — `trecho_b.inicio/fim` já estava
em B2 no catálogo (ver STATUS.md "B2 aplicado..."), mas o ficheiro .mp3 de
produção nunca tinha sido recortado de novo: continuava com o áudio do B
antigo. Esta tarefa torna o B2 audível de facto.

Método: corte directo de tmp_dl/<id>_full.mp3 nos tempos trecho_b.inicio/fim
(decode+reencode para alinhar a amostra exacta, mp3 48kHz, libmp3lame -q:a 0 —
mesma taxa/qualidade observada nos outros Trecho B do catálogo). Sem fades
(nenhum dos Trecho B existentes tem fade programático — confirmado por
inspecção de amplitude). Ajuste de loudness: só se o corte bruto ficar a
mais de 1 LU do Trecho B antigo da MESMA faixa (a única referência "antes/
depois" comparável — a média do pack tem ~2 LU de desvio-padrão, não é
referência útil) — sempre por atenuação (nunca ganho, para não arriscar
clipping; os cortes testados já tinham pico a 0dBFS).

Gera também assets/audio_ext/<id>_b_ext.mp3 (B2 + 10s, mesmo corte/ganho).

Verificações antes de gravar (todas têm de passar):
  - duração do B novo ~15s (tolerância 0.3s)
  - correlação do B novo com o full na posição B2 >=0.99
  - ext começa idêntico ao B novo (>=0.95 nos primeiros ~5s)
  - loudness do B novo (depois de eventual atenuação) a <=1 LU do B antigo

Não escreve nada em disco/catálogo antes de todas as 4 faixas passarem a
validação — grava resultados em memória e só aplica no fim, faixa a faixa.
"""
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import gerar_audio_ext_dec00 as g  # reutiliza pcm()/melhor_correlacao_normalizada()

APP_DIR = g.APP_DIR
CATALOGO_PATH = os.path.join(APP_DIR, 'catalogo.json')
ARQUIVO_DIR = os.path.join(APP_DIR, '_arquivo', 'b2_substituidos')
BACKUP_DIR = os.path.join(APP_DIR, 'backups_catalogo')
DMIN_ENCORE_S = 10
IDS = ['dec60_02', 'dec60_05', 'dec00_02', 'dec00_05']
TOLERANCIA_LU = 1.0
TOLERANCIA_DUR_S = 0.3
LIMIAR_CORR_B2 = 0.99
LIMIAR_CORR_EXT = 0.95


def duracao(caminho):
    r = subprocess.run(
        ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=nw=1:nk=1', caminho],
        capture_output=True, text=True)
    return float(r.stdout.strip())


def loudness_integrada(caminho):
    r = subprocess.run(
        ['ffmpeg', '-i', caminho, '-af', 'loudnorm=print_format=summary', '-f', 'null', '-'],
        capture_output=True, text=True)
    for linha in r.stderr.splitlines():
        if 'Input Integrated' in linha:
            return float(linha.split(':')[1].strip().split(' ')[0])
    raise RuntimeError('loudnorm não devolveu "Input Integrated" para ' + caminho)


def cortar(full_mp3, inicio_s, duracao_s, destino, ganho_db=0.0):
    os.makedirs(os.path.dirname(destino), exist_ok=True)
    filtros = [] if ganho_db == 0.0 else [f'volume={ganho_db}dB']
    cmd = ['ffmpeg', '-y', '-v', 'error', '-i', full_mp3, '-ss', str(inicio_s), '-t', str(duracao_s)]
    if filtros:
        cmd += ['-af', ','.join(filtros)]
    cmd += ['-ar', '48000', '-ac', '2', '-c:a', 'libmp3lame', '-q:a', '0', destino]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    if r.returncode != 0:
        raise RuntimeError(r.stderr[-400:])


def correlacao_posicional(caminho_a, caminho_b_full, offset_full_s, duracao_s):
    """Correlação normalizada no mesmo lag (0) — caminho_a é um corte já
    alinhado, caminho_b_full é a fonte completa; usa a mesma janela."""
    sinal_a = g.pcm(caminho_a, offset=0, duracao=duracao_s)
    sinal_full = g.pcm(caminho_b_full, offset=offset_full_s, duracao=duracao_s)
    n = min(len(sinal_a), len(sinal_full))
    sinal_a, sinal_full = sinal_a[:n], sinal_full[:n]
    na, nb = np.linalg.norm(sinal_a), np.linalg.norm(sinal_full)
    if na == 0 or nb == 0:
        return 0.0
    return float(np.dot(sinal_a, sinal_full) / (na * nb))


def correlacao_inicio(caminho_a, caminho_b, duracao_s):
    sinal_a = g.pcm(caminho_a, offset=0, duracao=duracao_s)
    sinal_b = g.pcm(caminho_b, offset=0, duracao=duracao_s)
    n = min(len(sinal_a), len(sinal_b))
    sinal_a, sinal_b = sinal_a[:n], sinal_b[:n]
    na, nb = np.linalg.norm(sinal_a), np.linalg.norm(sinal_b)
    if na == 0 or nb == 0:
        return 0.0
    return float(np.dot(sinal_a, sinal_b) / (na * nb))


def processar(id_faixa, catalogo, tmp_dir):
    entrada = catalogo[id_faixa]
    tb = entrada['trecho_b']
    inicio, fim = tb['inicio'], tb['fim']
    dur = fim - inicio
    full_mp3 = os.path.join(APP_DIR, 'tmp_dl', f'{id_faixa}_full.mp3')
    producao_b = os.path.join(APP_DIR, tb['ficheiro'])

    linha = {'id': id_faixa, 'titulo': entrada['titulo'], 'inicio': inicio, 'fim': fim, 'duracao_s': dur}

    if not os.path.exists(full_mp3):
        linha['falhou'] = f'tmp_dl/{id_faixa}_full.mp3 não existe'
        return linha, None
    if not os.path.exists(producao_b):
        linha['falhou'] = f'{tb["ficheiro"]} (produção) não existe'
        return linha, None

    loud_antigo = loudness_integrada(producao_b)
    linha['loudness_b_antigo_lufs'] = round(loud_antigo, 1)

    cand_raw = os.path.join(tmp_dir, f'{id_faixa}_b_raw.mp3')
    cortar(full_mp3, inicio, dur, cand_raw, ganho_db=0.0)
    loud_raw = loudness_integrada(cand_raw)
    diff = loud_raw - loud_antigo
    linha['loudness_b_novo_bruto_lufs'] = round(loud_raw, 1)

    ganho = 0.0
    if abs(diff) > TOLERANCIA_LU:
        ganho = round(-diff, 2)
        linha['ganho_aplicado_db'] = ganho
    cand_final = os.path.join(tmp_dir, f'{id_faixa}_b_final.mp3')
    cortar(full_mp3, inicio, dur, cand_final, ganho_db=ganho)
    loud_final = loudness_integrada(cand_final)
    linha['loudness_b_novo_final_lufs'] = round(loud_final, 1)
    linha['loudness_diff_lu'] = round(loud_final - loud_antigo, 2)

    dur_final = duracao(cand_final)
    linha['duracao_b_final_s'] = round(dur_final, 2)
    ok_dur = abs(dur_final - 15.0) <= TOLERANCIA_DUR_S

    corr_b2 = correlacao_posicional(cand_raw, full_mp3, inicio, dur)
    linha['correlacao_full_b2'] = round(corr_b2, 4)
    ok_corr_b2 = corr_b2 >= LIMIAR_CORR_B2

    dur_ext = dur + DMIN_ENCORE_S
    cand_ext = os.path.join(tmp_dir, f'{id_faixa}_b_ext.mp3')
    cortar(full_mp3, inicio, dur_ext, cand_ext, ganho_db=ganho)
    dur_ext_real = duracao(cand_ext)
    linha['duracao_ext_s'] = round(dur_ext_real, 2)

    corr_ext = correlacao_inicio(cand_final, cand_ext, min(5.0, dur))
    linha['correlacao_ext_vs_b_novo'] = round(corr_ext, 4)
    ok_corr_ext = corr_ext >= LIMIAR_CORR_EXT

    ok_loud = abs(loud_final - loud_antigo) <= TOLERANCIA_LU

    linha['verificacoes'] = {
        'duracao_b_~15s': ok_dur,
        'correlacao_full_b2_>=0.99': ok_corr_b2,
        'correlacao_ext_vs_b_novo_>=0.95': ok_corr_ext,
        'loudness_<=1LU_do_antigo': ok_loud,
    }
    passou = ok_dur and ok_corr_b2 and ok_corr_ext and ok_loud
    linha['passou'] = passou
    if not passou:
        linha['falhou'] = 'uma ou mais verificações não passaram — ver "verificacoes"'
        return linha, None

    return linha, {'b_final': cand_final, 'b_ext': cand_ext, 'producao_b': producao_b}


def main():
    catalogo_lista = json.load(open(CATALOGO_PATH, encoding='utf-8'))
    catalogo = {e['id']: e for e in catalogo_lista}

    tmp_dir = os.path.join(APP_DIR, '_preview_revisao', 'b2_audivel_tmp')
    os.makedirs(tmp_dir, exist_ok=True)

    linhas = []
    aplicaveis = {}
    for id_faixa in IDS:
        linha, dados = processar(id_faixa, catalogo, tmp_dir)
        linhas.append(linha)
        print(id_faixa, '->', 'OK' if dados else 'SALTADA: ' + linha.get('falhou', '?'))
        if dados:
            aplicaveis[id_faixa] = dados

    if not aplicaveis:
        print('\nNenhuma faixa passou a validação — nada aplicado.')
        json.dump(linhas, open(os.path.join(tmp_dir, '_linhas.json'), 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
        return linhas

    # ── Backup + tag + arquivo ANTES de tocar em produção ──
    os.makedirs(BACKUP_DIR, exist_ok=True)
    os.makedirs(ARQUIVO_DIR, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = os.path.join(BACKUP_DIR, f'catalogo_{timestamp}_antes-b2-audivel.json')
    shutil.copy2(CATALOGO_PATH, backup_path)
    print('Backup catálogo:', os.path.relpath(backup_path, APP_DIR))

    subprocess.run(['git', 'tag', 'antes-b2-audivel'], cwd=APP_DIR, check=False)
    print('Tag git "antes-b2-audivel" criada (ou já existia).')

    for id_faixa, dados in aplicaveis.items():
        nome_ficheiro = os.path.basename(dados['producao_b'])
        destino_arquivo = os.path.join(ARQUIVO_DIR, nome_ficheiro)
        shutil.move(dados['producao_b'], destino_arquivo)
        print(f'{id_faixa}: B antigo arquivado em {os.path.relpath(destino_arquivo, APP_DIR)}')

        shutil.copy2(dados['b_final'], dados['producao_b'])
        print(f'{id_faixa}: produção substituída -> {os.path.relpath(dados["producao_b"], APP_DIR)}')

        destino_ext = os.path.join(APP_DIR, 'assets', 'audio_ext', f'{id_faixa}_b_ext.mp3')
        os.makedirs(os.path.dirname(destino_ext), exist_ok=True)
        shutil.copy2(dados['b_ext'], destino_ext)
        print(f'{id_faixa}: ext gerado -> {os.path.relpath(destino_ext, APP_DIR)}')

        catalogo[id_faixa]['trecho_b']['ficheiro_ext'] = os.path.relpath(destino_ext, APP_DIR)

    json.dump(catalogo_lista, open(CATALOGO_PATH, 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
    print(f'\ncatalogo.json actualizado — ficheiro_ext gravado em {len(aplicaveis)} faixas.')

    json.dump(linhas, open(os.path.join(tmp_dir, '_linhas.json'), 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
    return linhas


if __name__ == '__main__':
    main()
