#!/usr/bin/env python3
"""
Gerador de voz do descritivo do apresentador — voz/descritivo_<codigo>.wav.

Voz: pt-PT-DuarteNeural via edge-tts, num venv dedicado fora do projecto
(~/.venvs/musicbox-tts — ver EDGE_TTS abaixo). Mesmo processamento
(silêncio cortado nas pontas + loudness normalizado, 44.1kHz mono) dos
outros geradores de voz do projecto (gerar_vozes_nome_artista.py).

edge-tts precisa de LIGAÇÃO À INTERNET em cada geração — não há modo
offline. Se falhar, a mensagem de erro é clara e os ficheiros já
existentes NUNCA são apagados (só o/os que estava(m) a gerar nessa
chamada falham). Ver DECISIONS.md, "edge-tts é só para protótipo" —
decisão final para emissão real (voz licenciada ou locutor real) fica
para mais tarde.

voz/descritivo_index.json guarda {playlistCodigo: sha1(texto)} — por
omissão só regenera uma playlist se o texto mudou desde a última vez ou
o ficheiro de voz ainda não existe. --todos força tudo (com backup
prévio); --codigo gera só uma playlist.

Uso:
  python3 gerar_vozes_descritivo.py                       # só os que faltam/mudaram
  python3 gerar_vozes_descritivo.py --todos                # regenera tudo, com backup
  python3 gerar_vozes_descritivo.py --codigo STD.INT.50.MIX.001
"""
import argparse
import datetime
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
PLAYLISTS = RAIZ / 'playlists.json'
VOZ_DIR = RAIZ / 'voz'
INDEX_PATH = VOZ_DIR / 'descritivo_index.json'
EDGE_TTS = Path.home() / '.venvs' / 'musicbox-tts' / 'bin' / 'edge-tts'
VOZ = 'pt-PT-DuarteNeural'
SAMPLE_RATE = 44100

# Mesmo filtro usado em gerar_vozes_nome_artista.py — corta silêncio
# residual nas duas pontas e normaliza loudness.
FILTRO_TRIM_NORM = (
    "silenceremove=start_periods=1:start_threshold=-50dB:start_silence=0.05:detection=peak,"
    "areverse,"
    "silenceremove=start_periods=1:start_threshold=-50dB:start_silence=0.05:detection=peak,"
    "areverse,"
    "loudnorm=I=-16:TP=-1.5:LRA=11"
)


def carregar_playlists():
    with open(PLAYLISTS, encoding='utf-8') as f:
        return json.load(f)


def carregar_index():
    if INDEX_PATH.exists():
        with open(INDEX_PATH, encoding='utf-8') as f:
            return json.load(f)
    return {}


def gravar_index(index):
    with open(INDEX_PATH, 'w', encoding='utf-8') as f:
        json.dump(index, f, ensure_ascii=False, indent=2, sort_keys=True)
        f.write('\n')


def sha1_texto(texto):
    return hashlib.sha1(texto.encode('utf-8')).hexdigest()


def gerar_um(texto, destino):
    with tempfile.TemporaryDirectory() as tmp:
        mp3 = Path(tmp) / 'descritivo.mp3'
        r = subprocess.run(
            [str(EDGE_TTS), '--voice', VOZ, '--text', texto, '--write-media', str(mp3)],
            capture_output=True, text=True, timeout=60,
        )
        if r.returncode != 0 or not mp3.exists():
            raise RuntimeError(
                "edge-tts falhou — provavelmente sem ligação à internet "
                f"(edge-tts precisa de rede em cada geração). Detalhe: {r.stderr.strip()[-300:]}"
            )
        subprocess.run(
            ['ffmpeg', '-y', '-i', str(mp3), '-af', FILTRO_TRIM_NORM,
             '-ar', str(SAMPLE_RATE), '-ac', '1', str(destino)],
            check=True, capture_output=True,
        )


def main():
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--todos', action='store_true',
                     help='Regenera todas as playlists (com backup prévio)')
    ap.add_argument('--codigo', help='Gera só uma playlist (playlistCodigo)')
    args = ap.parse_args()

    if not EDGE_TTS.exists():
        sys.exit(f"Erro: edge-tts não encontrado em {EDGE_TTS}\n"
                  f"Instalar: python3 -m venv ~/.venvs/musicbox-tts && "
                  f"~/.venvs/musicbox-tts/bin/pip install edge-tts")
    if shutil.which('ffmpeg') is None:
        sys.exit("Erro: 'ffmpeg' não encontrado no PATH.")

    playlists = carregar_playlists()
    index = carregar_index()
    VOZ_DIR.mkdir(exist_ok=True)

    candidatos = {k: v for k, v in playlists.items() if v.get('descritivo_apresentador')}

    if args.codigo:
        if args.codigo not in candidatos:
            sys.exit(f"Erro: '{args.codigo}' não existe em playlists.json ou não tem descritivo_apresentador.")
        alvo = [args.codigo]
    elif args.todos:
        alvo = sorted(candidatos.keys())
        existentes = list(VOZ_DIR.glob('descritivo_*.wav'))
        if existentes:
            data = datetime.date.today().isoformat()
            backup_dir = RAIZ / f'_backup_voz_{data}_descritivo'
            backup_dir.mkdir(exist_ok=True)
            for f in existentes:
                shutil.copy2(f, backup_dir / f.name)
            print(f"Backup de {len(existentes)} ficheiro(s) em {backup_dir}/")
    else:
        alvo = []
        for k, v in candidatos.items():
            texto = v['descritivo_apresentador']
            destino = VOZ_DIR / f'descritivo_{k}.wav'
            if not destino.exists() or index.get(k) != sha1_texto(texto):
                alvo.append(k)
        alvo.sort()

    if not alvo:
        print("Nada a gerar — todos os descritivos já têm voz actualizada (usa --todos para regenerar).")
        return

    print(f"A gerar {len(alvo)} descritivo(s) (voz={VOZ})…")
    falhas = []
    for k in alvo:
        texto = candidatos[k]['descritivo_apresentador']
        destino = VOZ_DIR / f'descritivo_{k}.wav'
        try:
            gerar_um(texto, destino)
            index[k] = sha1_texto(texto)
            gravar_index(index)  # grava já a cada sucesso — não perde progresso se falhar a meio
            print(f"  ✓ {k}")
        except Exception as e:
            print(f"  ✗ {k}: {e}")
            falhas.append(k)

    print(f"\nConcluído: {len(alvo) - len(falhas)}/{len(alvo)} gerado(s).")
    if falhas:
        print(f"Falhas ({len(falhas)}): {falhas}")
        print("Ficheiros de voz já existentes NÃO foram apagados.")
        sys.exit(1)


if __name__ == '__main__':
    main()
