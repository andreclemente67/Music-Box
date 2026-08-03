#!/usr/bin/env python3
"""
MUSIC BOX — Sugerir Trechos A e B
Regra V1.2: começa no momento mais reconhecível — voz ou instrumental.
Evita: silêncio, fade-in longo, comentador falado.
Usa ffmpeg volumedetect — sem dependências externas.
"""

import sys
import subprocess
import re

def analisar_volume(ficheiro):
    result = subprocess.run(
        ['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
         '-of', 'default=noprint_wrappers=1:nokey=1', ficheiro],
        capture_output=True, text=True
    )
    duracao = float(result.stdout.strip())

    volumes = []
    passo = 2
    for t in range(0, int(duracao) - passo, passo):
        r = subprocess.run(
            ['ffmpeg', '-ss', str(t), '-t', str(passo), '-i', ficheiro,
             '-af', 'volumedetect', '-vn', '-sn', '-dn', '-f', 'null', '/dev/null'],
            capture_output=True, text=True
        )
        match = re.search(r'mean_volume: ([-\d.]+) dB', r.stderr)
        vol = float(match.group(1)) if match else -91.0
        volumes.append((t, vol))

    return duracao, volumes

def sugerir_trechos(ficheiro, duracao_trecho=15):
    duracao, volumes = analisar_volume(ficheiro)

    # Limiar V1.2: -45dB — aceita voz suave, rejeita silêncio/fade-in
    LIMIAR = -45.0

    # Trecho A: primeiro momento com som perceptível, mínimo 3s
    tempo_a = 3
    for t, v in volumes:
        if t >= 3 and v > LIMIAR:
            tempo_a = t
            break

    # Trecho B: pico de volume após A + duração + 5s
    min_b = tempo_a + duracao_trecho + 5
    candidatos_b = [(t, v) for t, v in volumes if t >= min_b and t <= duracao - duracao_trecho]
    if candidatos_b:
        tempo_b = max(candidatos_b, key=lambda x: x[1])[0]
    else:
        tempo_b = int(min_b)

    return tempo_a, tempo_b

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Uso: python3 sugerir_trechos.py ficheiro.mp3")
        sys.exit(1)
    ta, tb = sugerir_trechos(sys.argv[1])
    print(f"Trecho A → {ta}s")
    print(f"Trecho B → {tb}s")
    print(f"TEMPO_A={ta}")
    print(f"TEMPO_B={tb}")
