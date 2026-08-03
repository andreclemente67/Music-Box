#!/bin/bash
D=~/MusicBox/app
dl() { yt-dlp -x --audio-format mp3 --audio-quality 0 -o "$D/dl_tmp.mp3" "$1" && ffmpeg -y -ss $2 -i "$D/dl_tmp.mp3" -t 30 -q:a 2 "$D/$3" && cp "$D/$3" "$D/$4" && rm -f "$D/dl_tmp.mp3" && echo "OK: $3"; }
dl https://www.youtube.com/watch?v=N9weeGiL5IM 0 01_PT_a.mp3 01_PT_b.mp3
dl https://www.youtube.com/watch?v=bSyv4yiZBHY 0 02_PT_a.mp3 02_PT_b.mp3
dl https://www.youtube.com/watch?v=MuhzV1Up4ys 0 03_PT_a.mp3 03_PT_b.mp3
dl https://www.youtube.com/watch?v=fyRwEqV7xcY 0 04_PT_a.mp3 04_PT_b.mp3
dl https://www.youtube.com/watch?v=tP0zj220CbQ 0 05_PT_a.mp3 05_PT_b.mp3
dl https://www.youtube.com/watch?v=kVqbGQLF9To 0 06_PT_a.mp3 06_PT_b.mp3
dl https://www.youtube.com/watch?v=langBiTd0LA 0 07_PT_a.mp3 07_PT_b.mp3
echo "MUSICA PORTUGUESA COMPLETA"
