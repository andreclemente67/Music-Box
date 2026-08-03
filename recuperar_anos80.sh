#!/bin/bash
D=~/MusicBox/app
dl() { yt-dlp -x --audio-format mp3 --audio-quality 0 -o "$D/dl_tmp.mp3" "$1" && ffmpeg -y -ss $2 -i "$D/dl_tmp.mp3" -t 30 -q:a 2 "$D/$3" && cp "$D/$3" "$D/$4" && rm -f "$D/dl_tmp.mp3" && echo "OK: $3"; }
dl https://www.youtube.com/watch?v=djV11Xbc914 0 01_a.mp3 01_b.mp3
dl https://www.youtube.com/watch?v=1w7OgIMMRc4 0 02_a.mp3 02_b.mp3
dl https://www.youtube.com/watch?v=https://www.youtube.com/watch?v=AWhTLbCoMEI 10 03_a.mp3 03_b.mp3
dl https://www.youtube.com/watch?v=SJcKqJCEBhQ 0 04_a.mp3 04_b.mp3
dl https://www.youtube.com/watch?v=9jK-NcRmVcw 0 05_a.mp3 05_b.mp3
dl https://www.youtube.com/watch?v=OMOGaugKpzs 0 06_a.mp3 06_b.mp3
dl https://www.youtube.com/watch?v=Zi_XLOBDo_Y 0 07_a.mp3 07_b.mp3
echo "ANOS 80 COMPLETO"
