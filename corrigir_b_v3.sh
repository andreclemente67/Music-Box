#!/bin/bash
APP="$HOME/MusicBox/app"
TMP="$APP/tmp_dl"
mkdir -p "$TMP"

bc() {
  local url="$1" ss="$2" dest="$3"
  local base="$TMP/${dest%.mp3}"
  yt-dlp --force-overwrites -x --audio-format mp3 --audio-quality 0 \
    -o "${base}.%(ext)s" "$url" 2>/dev/null
  local src="${base}.mp3"
  [ -f "$src" ] || src=$(ls "${base}".* 2>/dev/null | head -1)
  if [ -f "$src" ]; then
    ffmpeg -y -i "$src" -ss "$ss" -t 15 -c copy "$APP/$dest" 2>/dev/null
    rm -f "$src"
    echo "✓ $dest"
  else
    echo "✗ FALHOU: $dest"
  fi
}

echo "=== PT ==="
bc "https://www.youtube.com/watch?v=n92WXR-AuUM" 55 "02_PT_b.mp3"
bc "https://www.youtube.com/watch?v=MuhzV1Up4ys" 50 "03_PT_b.mp3"
bc "https://www.youtube.com/watch?v=fyRwEqV7xcY" 45 "04_PT_b.mp3"
bc "https://www.youtube.com/watch?v=DyoKXKO1aSk" 35 "05_PT_b.mp3"
bc "https://www.youtube.com/watch?v=3e4SrqBW_8Q" 55 "06_PT_b.mp3"
bc "https://www.youtube.com/watch?v=8Jf3_hHEXr0" 40 "07_PT_b.mp3"

echo "=== AME ==="
bc "https://www.youtube.com/watch?v=c7eB7Wns1-M" 40 "AME_02_b.mp3"
bc "https://www.youtube.com/watch?v=Gu5VJiAMFAE" 45 "AME_04_b.mp3"
bc "https://www.youtube.com/watch?v=xqiRFMSJpkA" 40 "AME_05_b.mp3"
bc "https://www.youtube.com/watch?v=nf_-aXRWNSY" 35 "AME_06_b.mp3"

echo "=== BAT ==="
bc "https://www.youtube.com/watch?v=swBGSLBrPwM" 45 "BAT_03_b.mp3"
bc "https://www.youtube.com/watch?v=2RYfGCYvxdc" 60 "BAT_04_b.mp3"
bc "https://www.youtube.com/watch?v=dWJCBN0IQPY" 50 "BAT_05_b.mp3"
bc "https://www.youtube.com/watch?v=Ro9VJMmIFRI" 40 "BAT_06_b.mp3"
bc "https://www.youtube.com/watch?v=KsQ1bkNNKIs" 55 "BAT_07_b.mp3"

echo "=== CINEMA ==="
bc "https://www.youtube.com/watch?v=bfYVT0MFk3U" 60 "CINEMA_01_b.mp3"
bc "https://www.youtube.com/watch?v=MFxq7WOn3cI" 55 "CINEMA_03_b.mp3"
bc "https://www.youtube.com/watch?v=FDH5OXNQ8p0" 60 "CINEMA_04_b.mp3"
bc "https://www.youtube.com/watch?v=Cs6Yx2XzFIk" 50 "CINEMA_06_b.mp3"

echo "=== PT80 ==="
bc "https://www.youtube.com/watch?v=kpCqAKBOezo" 50 "PT80_01_b.mp3"
bc "https://www.youtube.com/watch?v=b19JHmCgBGo" 40 "PT80_02_b.mp3"
bc "https://www.youtube.com/watch?v=3RJGcQkPYPo" 45 "PT80_03_b.mp3"
bc "https://www.youtube.com/watch?v=vHaYfW0OBOY" 50 "PT80_04_b.mp3"

echo "=== SOLO ==="
bc "https://www.youtube.com/watch?v=oIfMVkSsRgM" 45 "SOLO_04_b.mp3"
bc "https://www.youtube.com/watch?v=cVJns_bMgkg" 60 "SOLO_05_b.mp3"
bc "https://www.youtube.com/watch?v=B4jHSeFtHwA" 55 "SOLO_06_b.mp3"
bc "https://www.youtube.com/watch?v=GbNgGcMDWFo" 70 "SOLO_07_b.mp3"

rm -rf "$TMP"
echo "=== CONCLUÍDO ==="
