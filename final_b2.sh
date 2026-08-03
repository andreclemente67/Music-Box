#!/bin/bash
APP="$HOME/MusicBox/app"
TMP="$APP/tmp_dl"
mkdir -p "$TMP"
bc() {
  local url="$1" ss="$2" dest="$3"
  local base="$TMP/${dest%.mp3}"
  yt-dlp --force-overwrites -x --audio-format mp3 --audio-quality 0 -o "${base}.%(ext)s" "https://www.youtube.com/watch?v=$url" 2>/dev/null
  local src=$(ls "${base}".* 2>/dev/null | head -1)
  if [ -f "$src" ]; then
    ffmpeg -y -i "$src" -ss "$ss" -t 15 -c copy "$APP/$dest" 2>/dev/null
    rm -f "$src"; echo "OK $dest"
  else
    echo "FALHOU $dest"
  fi
}
bc "o9UmSMQmkME" 80 "02_b.mp3"
bc "gBOg0Hj9KzM" 60 "03_b.mp3"
bc "ftVTWDrtrlc" 50 "BAT_05_b.mp3"
rm -rf "$TMP"
echo "CONCLUIDO"
