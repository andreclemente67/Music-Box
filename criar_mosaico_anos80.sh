#!/bin/bash
APP="$HOME/MusicBox/app"
TMP="$APP/tmp_dl"
mkdir -p "$TMP"

yt-dlp --force-overwrites -x --audio-format mp3 --audio-quality 0 \
  -o "$TMP/MOSAICO_ANOS80.%(ext)s" \
  "https://www.youtube.com/watch?v=0fAQhSRLQnM" 2>/dev/null

src=$(ls "$TMP/MOSAICO_ANOS80".* 2>/dev/null | head -1)
if [ -f "$src" ]; then
  ffmpeg -y -i "$src" -ss 30 -t 30 -c copy "$APP/MOSAICO_ANOS80.mp3" 2>/dev/null
  rm -f "$src"
  echo "OK MOSAICO_ANOS80.mp3"
else
  echo "FALHOU"
fi
rm -rf "$TMP"
