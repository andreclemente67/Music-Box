#!/usr/bin/env python3
"""
Gerador de voz do nome do artista (apresentador) — voz/nome_<id>.wav.

Pipeline: `say` (voz Alex, rate 205) -> .aiff -> `ffmpeg` (corta silêncio
nas pontas + normaliza loudness) -> .wav 44.1kHz mono.

Dependências externas (têm de estar no PATH): `say` (TTS nativo do
macOS) e `ffmpeg`.

Decisão da voz/rate ("Alex", 205): ver DECISIONS.md, secção "2026-10-04
— Nova arquitectura da voz pós-acerto". Texto falado: só o artista (ex.
"Bill Haley & His Comets"), sem efeito festivo — esse é o ficheiro
partilhado efeitos/in_the_box.wav, encadeado depois pelo jogo (ver
testeTocarSequenciaSom() em musicbox.html).

Uso:
  python3 gerar_vozes_nome_artista.py            # só os que faltam em voz/
  python3 gerar_vozes_nome_artista.py --todos    # regenera os 302, com
                                                  # backup prévio para
                                                  # _backup_voz_<data>/
  python3 gerar_vozes_nome_artista.py --id dec50_01   # só uma faixa
"""
import argparse
import datetime
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
CATALOGO = RAIZ / 'catalogo.json'
VOZ_DIR = RAIZ / 'voz'
VOZ = 'Alex'
RATE = 205
SAMPLE_RATE = 44100

# Mesmo filtro usado nos 302 ficheiros originais (2026-10-04): corta
# silêncio residual nas duas pontas (silenceremove + areverse duas vezes,
# truque padrão do ffmpeg para aparar início E fim) e normaliza loudness
# para um nível consistente entre vozes/faixas.
FILTRO_TRIM_NORM = (
    "silenceremove=start_periods=1:start_threshold=-50dB:start_silence=0.05:detection=peak,"
    "areverse,"
    "silenceremove=start_periods=1:start_threshold=-50dB:start_silence=0.05:detection=peak,"
    "areverse,"
    "loudnorm=I=-16:TP=-1.5:LRA=11"
)


def carregar_catalogo():
    with open(CATALOGO, encoding='utf-8') as f:
        return json.load(f)


def nome_para_texto(entrada_artista):
    # catalogo.json guarda 'artista' como string ou lista (colaborações,
    # ex. ["Daft Punk", "Pharrell Williams"]).
    if isinstance(entrada_artista, list):
        return ' & '.join(entrada_artista)
    return entrada_artista or ''


def gerar_um(texto, destino):
    with tempfile.TemporaryDirectory() as tmp:
        aiff = Path(tmp) / 'voz.aiff'
        subprocess.run(
            ['say', '-v', VOZ, '-r', str(RATE), texto, '-o', str(aiff)],
            check=True, capture_output=True,
        )
        subprocess.run(
            ['ffmpeg', '-y', '-i', str(aiff), '-af', FILTRO_TRIM_NORM,
             '-ar', str(SAMPLE_RATE), '-ac', '1', str(destino)],
            check=True, capture_output=True,
        )


def main():
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--todos', action='store_true',
                     help='Regenera todas as vozes (com backup prévio)')
    ap.add_argument('--id', help='Gera só uma faixa (id do catalogo.json)')
    args = ap.parse_args()

    for exe in ('say', 'ffmpeg'):
        if shutil.which(exe) is None:
            sys.exit(f"Erro: '{exe}' não encontrado no PATH.")

    catalogo = carregar_catalogo()
    por_id = {t['id']: t for t in catalogo}
    VOZ_DIR.mkdir(exist_ok=True)

    if args.id:
        if args.id not in por_id:
            sys.exit(f"Erro: id '{args.id}' não existe em catalogo.json")
        alvo_ids = [args.id]
    elif args.todos:
        alvo_ids = sorted(por_id.keys())
        existentes = list(VOZ_DIR.glob('nome_*.wav'))
        if existentes:
            data = datetime.date.today().isoformat()
            backup_dir = RAIZ / f'_backup_voz_{data}'
            backup_dir.mkdir(exist_ok=True)
            for f in existentes:
                shutil.copy2(f, backup_dir / f.name)
            print(f"Backup de {len(existentes)} ficheiro(s) em {backup_dir}/")
    else:
        alvo_ids = sorted(tid for tid in por_id if not (VOZ_DIR / f'nome_{tid}.wav').exists())

    if not alvo_ids:
        print("Nada a gerar — todas as vozes já existem (usa --todos para regenerar).")
        return

    print(f"A gerar {len(alvo_ids)} ficheiro(s) de voz (voz={VOZ}, rate={RATE})…")
    falhas = []
    for tid in alvo_ids:
        texto = nome_para_texto(por_id[tid].get('artista'))
        if not texto:
            print(f"  ✗ {tid}: sem campo 'artista' no catalogo.json")
            falhas.append(tid)
            continue
        destino = VOZ_DIR / f'nome_{tid}.wav'
        try:
            gerar_um(texto, destino)
            print(f"  ✓ {tid} — \"{texto}\"")
        except subprocess.CalledProcessError as e:
            print(f"  ✗ {tid}: {e.stderr.decode('utf-8', 'ignore')[-300:] if e.stderr else e}")
            falhas.append(tid)

    print(f"\nConcluído: {len(alvo_ids) - len(falhas)}/{len(alvo_ids)} gerado(s).")
    if falhas:
        print(f"Falhas ({len(falhas)}): {falhas}")
        sys.exit(1)


if __name__ == '__main__':
    main()
