#!/bin/bash
ORIGEM=~/MusicBox/app/originais
DESTINO=~/MusicBox/app
THRESHOLD=-35dB
MIN_SILENCIO=0.5

if ! command -v ffmpeg &>/dev/null; then
  echo "ffmpeg nao encontrado. Instala com: brew install ffmpeg"
  exit 1
fi

if [ ! -d "$ORIGEM" ]; then
  echo "Pasta de originais nao encontrada: $ORIGEM"
  exit 1
fi

mkdir -p "$DESTINO"

processar() {
  local ficheiro="$1"
  local nome=$(basename "$ficheiro")
  local saida="$DESTINO/$nome"
  local deteccao
  deteccao=$(ffmpeg -i "$ficheiro" -af "silencedetect=noise=${THRESHOLD}:duration=${MIN_SILENCIO}" -f null - 2>&1 | grep "silence_end" | head -1)
  if [ -z "$deteccao" ]; then
    echo "OK $nome - sem silencio inicial, copia directa"
    cp "$ficheiro" "$saida"
    return
  fi
  local inicio
inicio=$(echo "$deteccao" | grep -o 'silence_end: [0-9.]*' | sed 's/silence_end: //')
  if [ -z "$inicio" ] || (( $(echo "$inicio <= 0" | bc -l) )); then
    echo "OK $nome - inicio em 0s, copia directa"
    cp "$ficheiro" "$saida"
    return
  fi
  echo "CORTA $nome - ${inicio}s de silencio inicial"
  ffmpeg -y -i "$ficheiro" -ss "$inicio" -acodec libmp3lame -q:a 2 "$saida" 2>/dev/null
  if [ $? -eq 0 ]; then
    echo "guardado em $saida"
  else
    echo "ERRO ao processar $nome"
  fi
}

if [ -n "$1" ]; then
  if [ -f "$ORIGEM/$1" ]; then
    processar "$ORIGEM/$1"
  else
    echo "Ficheiro nao encontrado: $ORIGEM/$1"
    exit 1
  fi
else
  count=0
  for f in "$ORIGEM"/*.mp3; do
    [ -f "$f" ] || continue
    processar "$f"
    ((count++))
  done
  echo "$count ficheiros processados"
fi