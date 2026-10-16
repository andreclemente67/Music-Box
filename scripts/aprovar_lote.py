#!/usr/bin/env python3
"""Aprova em lote as previews "pendente" do ecrã Revisão que cumprem TODAS
as salvaguardas pedidas pelo André (11 Out 2026) — reavalia tudo de novo
(nunca confia em estado antigo), aplica as que passam (substitui os
ficheiros de produção, regista fonte_audio) e deixa as outras pendentes,
com o motivo exacto.

Salvaguardas para aprovação automática (TODAS têm de passar):
  1. Verificador OK — fingerprint + ruído limpos, refeito agora (A e B).
  2. Fonte do canal Topic ("Provided to YouTube by...") OU título com
     "Official Audio" — reconfirmado agora via yt-dlp (não confia em
     dados antigos do manifesto).
  3. Título da fonte sem Remix/Live/Acoustic/Version/Edit/Cover (nem
     Video/MV/Movie/Trailer/Scene/Teaser, regra já existente).
  4. A e B sem sobreposição e ambos ~15s (duração real dos ficheiros).
  5. Duração da fonte não muito diferente do que é normal para um single
     (>320s fica de fora — sem base de dados de referência, é só uma
     salvaguarda conservadora, ver aviso no relatório).
  6. Nunca uma posição de playlist "tributo" (curadoria especial).

Qualquer falha numa destas = fica "pendente", com o motivo. Grava
progresso a cada faixa (retomável). NUNCA mexe nas 14 "aprovado"
(aprovadas à mão, ainda não aplicadas) nem nas 62 "regenerado" — só nas
76 "pendente" com pré-audição já gerada.

Uso: scripts/.venv/bin/python3 scripts/aprovar_lote.py
"""
import csv
import json
import os
import re
import subprocess
import sys

APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, APP_DIR)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import verificar_trechos as vt  # noqa: E402

MANIFESTO = os.path.join(APP_DIR, '_revisao_regeneracao.json')
PROGRESSO_PATH = os.path.join(APP_DIR, 'relatorios', 'aprovacao_lote_progresso.csv')
BACKUP_DIR = os.path.join(APP_DIR, '_backup_pre_regeneracao')
CATALOGO_PATCH = os.path.join(APP_DIR, 'catalogo_patch.json')

TITULO_PROIBIDO_LOTE = re.compile(
    r'\bvideo\b|\bmv\b|\blive\b|música\s*video|\bmovie\b|\btrailer\b|\bscene\b|\bteaser\b'
    r'|\bremix\b|\bacoustic\b|\bversion\b|\bedit\b|\bcover\b', re.I)
TITULO_OFFICIAL_AUDIO = re.compile(r'official\s*audio', re.I)
DURACAO_FONTE_MAXIMA = 320  # segundos — ver ressalva no docstring, sem BD de referência


def carregar_progresso():
    if not os.path.exists(PROGRESSO_PATH):
        return {}
    with open(PROGRESSO_PATH, encoding='utf-8') as f:
        return {r['faixa']: r for r in csv.DictReader(f)}


def gravar_progresso(progresso):
    os.makedirs(os.path.dirname(PROGRESSO_PATH), exist_ok=True)
    with open(PROGRESSO_PATH, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['faixa', 'pack', 'resultado', 'motivo'])
        for r in progresso.values():
            w.writerow([r['faixa'], r['pack'], r['resultado'], r['motivo']])


def duracao_ficheiro(caminho):
    r = subprocess.run(['ffprobe', '-v', 'quiet', '-show_entries', 'format=duration',
                         '-of', 'csv=p=0', caminho], capture_output=True, text=True, timeout=30)
    return float(r.stdout.strip())


def obter_metadados_url(url, timeout=45):
    """(titulo, canal, descricao) para uma URL concreta — reconfirma Topic/
    Official Audio agora, não confia no que o manifesto já tinha."""
    def _correr(com_cookies):
        cmd = ['yt-dlp', url, '--skip-download', '--no-playlist']
        if com_cookies:
            cmd += ['--cookies-from-browser', 'chrome']
        cmd += ['--print', '%(title)s|||%(channel)s|||%(description)s']
        return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    r = _correr(False)
    if 'sign in to confirm' in (r.stderr or '').lower():
        r = _correr(True)
    linha = (r.stdout or '').strip().splitlines()
    if not linha:
        raise RuntimeError((r.stderr or 'sem resultado')[-300:])
    partes = linha[0].split('|||', 2)
    while len(partes) < 3:
        partes.append('')
    return partes[0], partes[1], partes[2]


def avaliar(tid, e, mapa_playlists):
    """Devolve (aprovar: bool, motivo: str)."""
    pack, tipo_posicao = mapa_playlists.get(tid, (e.get('playlistCodigo'), None))
    if tipo_posicao is not None:
        return False, f'posição especial de playlist tributo (tipo "{tipo_posicao}")'

    url = e.get('url_manual') or e.get('url')
    if not url:
        return False, 'sem URL'

    caminho_a = os.path.join(APP_DIR, e['ficheiro_proposta_a'])
    caminho_b = os.path.join(APP_DIR, e['ficheiro_proposta_b']) if e.get('ficheiro_proposta_b') else None
    if not os.path.exists(caminho_a) or (caminho_b and not os.path.exists(caminho_b)):
        return False, 'ficheiro de pré-audição em falta em disco'

    try:
        dur_a = duracao_ficheiro(caminho_a)
        dur_b = duracao_ficheiro(caminho_b) if caminho_b else None
    except Exception as ex:
        return False, f'erro a medir duração: {ex}'
    if not (14.5 <= dur_a <= 15.5):
        return False, f'Trecho A com {dur_a:.1f}s, fora de ~15s'
    if dur_b is not None and not (14.5 <= dur_b <= 15.5):
        return False, f'Trecho B com {dur_b:.1f}s, fora de ~15s'

    tempo_a, tempo_b = e.get('tempo_a'), e.get('tempo_b')
    if tempo_a is not None and tempo_b is not None:
        if abs(tempo_b - tempo_a) < max(dur_a, dur_b or 0):
            return False, f'Trecho A ({tempo_a}s) e B ({tempo_b}s) sobrepõem-se na fonte'

    try:
        titulo_yt, canal, descricao = obter_metadados_url(url)
    except Exception as ex:
        return False, f'não foi possível reconfirmar a fonte: {ex}'

    if TITULO_PROIBIDO_LOTE.search(titulo_yt or ''):
        return False, f'título da fonte rejeitado: "{titulo_yt}"'

    eh_topic = 'provided to youtube' in (descricao or '').lower()
    eh_official = bool(TITULO_OFFICIAL_AUDIO.search(titulo_yt or ''))
    if not (eh_topic or eh_official):
        return False, f'fonte "fallback" — nem canal Topic nem "Official Audio" (canal: {canal!r}, título: {titulo_yt!r})'

    try:
        caminho_fonte = vt.descarregar_para_cache(url)
        dur_fonte, fp_fonte = vt.fingerprint_fpcalc(caminho_fonte, fonte_completa=True)
    except Exception as ex:
        return False, f'não foi possível descarregar a fonte para verificar: {ex}'

    if dur_fonte > DURACAO_FONTE_MAXIMA:
        return False, f'duração da fonte muito alta ({dur_fonte:.0f}s > {DURACAO_FONTE_MAXIMA}s) — por confirmar'

    trecho_a = {'ficheiro': e['ficheiro_proposta_a']}
    res_a = vt.verificar_trecho(os.path.relpath(caminho_a, APP_DIR), caminho_fonte, dur_fonte, fp_fonte)
    if caminho_b:
        res_b = vt.verificar_trecho(os.path.relpath(caminho_b, APP_DIR), caminho_fonte, dur_fonte, fp_fonte)
    else:
        res_b = {'estado': '(sem trecho_b)'}
    if res_a['estado'] != 'OK':
        return False, f"verificador falhou no Trecho A: {res_a['estado']}"
    if res_b['estado'] not in ('OK', '(sem trecho_b)'):
        return False, f"verificador falhou no Trecho B: {res_b['estado']}"

    return True, f'canal Topic ({canal})' if eh_topic else f'"Official Audio" ({titulo_yt})'


def aplicar_aprovacao(tid, e):
    """Substitui ficheiro_a/b pela proposta (mesma receita de
    _aplicar_regeneracao_playlist.py), devolve o novo fonte_audio."""
    os.makedirs(BACKUP_DIR, exist_ok=True)
    url = e.get('url_manual') or e.get('url')
    pares = [(original, proposta) for original, proposta in
             ((e.get('ficheiro_a'), e['ficheiro_proposta_a']),
              (e.get('ficheiro_b'), e.get('ficheiro_proposta_b')))
             if original and proposta]
    # Confirma AMBAS as propostas em disco antes de mover a 1ª — evita
    # troca parcial (Trecho A trocado, Trecho B falha a meio) que deixava
    # o ficheiro de produção já alterado mas o manifesto preso em
    # "pendente" (mesma classe do bug Metal metal_02/metal_03, ver
    # relatorios/bugs_studio_pendentes.md).
    for _, proposta in pares:
        if not os.path.exists(os.path.join(APP_DIR, proposta)):
            raise FileNotFoundError(f'proposta em falta, nada trocado: {proposta}')
    for original, proposta in pares:
        origem = os.path.join(APP_DIR, original)
        destino_backup = os.path.join(BACKUP_DIR, original)
        if os.path.exists(origem) and not os.path.exists(destino_backup):
            os.rename(origem, destino_backup)
        os.rename(os.path.join(APP_DIR, proposta), origem)
    return url


def main():
    progresso = carregar_progresso()
    with open(MANIFESTO, encoding='utf-8') as f:
        manifesto = json.load(f)
    mapa_playlists = vt.carregar_mapa_playlists()

    candidatos = [tid for tid, e in manifesto.items()
                  if (e.get('estado') or 'pendente') == 'pendente' and e.get('tempo_a') is not None]
    pendentes_a_avaliar = [tid for tid in candidatos if tid not in progresso]
    print(f'{len(candidatos)} pendentes com pré-audição '
          f'({len(candidatos) - len(pendentes_a_avaliar)} já avaliadas numa corrida anterior, '
          f'a avaliar {len(pendentes_a_avaliar)})')

    patch_fonte_audio = {}

    for tid in pendentes_a_avaliar:
        e = manifesto[tid]
        pack = e.get('playlistCodigo') or '(sem playlist)'
        try:
            aprovar, motivo = avaliar(tid, e, mapa_playlists)
        except Exception as ex:
            aprovar, motivo = False, f'erro inesperado: {ex}'

        if aprovar:
            try:
                url = aplicar_aprovacao(tid, e)
                e['estado'] = 'regenerado'
                e['ficheiro_proposta_a'] = None
                e['ficheiro_proposta_b'] = None
                patch_fonte_audio[tid] = url
                resultado = 'aprovado'
            except Exception as ex:
                aprovar, motivo = False, f'falhou a aplicar: {ex}'
                resultado = 'pendente'
        if not aprovar:
            resultado = 'pendente'

        progresso[tid] = {'faixa': tid, 'pack': pack, 'resultado': resultado, 'motivo': motivo}
        print(f'{tid:30} [{pack:24}] — {resultado}: {motivo}')
        gravar_progresso(progresso)
        with open(MANIFESTO, 'w', encoding='utf-8') as f:
            json.dump(manifesto, f, ensure_ascii=False, indent=2)

    aprovadas = [r for r in progresso.values() if r['resultado'] == 'aprovado']
    pendentes = [r for r in progresso.values() if r['resultado'] == 'pendente']
    print(f'\n— resumo — aprovadas e aplicadas: {len(aprovadas)} | ficaram pendentes: {len(pendentes)}')

    if patch_fonte_audio:
        patch = [{'id': tid, 'fonte_audio': url} for tid, url in patch_fonte_audio.items()]
        with open(CATALOGO_PATCH, 'w', encoding='utf-8') as f:
            json.dump(patch, f, ensure_ascii=False, indent=2)
        print(f'catalogo_patch.json escrito com {len(patch)} fonte_audio — por fundir com _fundir_catalogo.py')

    print(f'progresso: {PROGRESSO_PATH}')


if __name__ == '__main__':
    main()
