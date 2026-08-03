#!/bin/bash
D=~/MusicBox/app
dl() { yt-dlp -x --audio-format mp3 --audio-quality 0 -o "$D/dl_tmp.mp3" "$1" && ffmpeg -y -ss $2 -i "$D/dl_tmp.mp3" -t 30 -q:a 2 "$D/$3" && cp "$D/$3" "$D/$4" && rm -f "$D/dl_tmp.mp3" && echo "OK: $3"; }
# Vozes Lendarias
dl https://www.youtube.com/watch?v=Qp6D71kQRhA 0 RET_01.mp3 RET_01.mp3
dl https://www.youtube.com/watch?v=TlrNxJqODBc 0 RET_02.mp3 RET_02.mp3
dl https://www.youtube.com/watch?v=fJ9rUzIMcZQ 0 RET_03.mp3 RET_03.mp3
dl https://www.youtube.com/watch?v=pAyKJAtDNCw 0 RET_04.mp3 RET_04.mp3
dl https://www.youtube.com/watch?v=tP0zj220CbQ 0 RET_05.mp3 RET_05.mp3
dl https://www.youtube.com/watch?v=BdEe5SpdIuo 0 RET_06.mp3 RET_06.mp3
dl https://www.youtube.com/watch?v=W53_LKgw3Ho 0 RET_07.mp3 RET_07.mp3
dl https://www.youtube.com/watch?v=VbD_kBJc_gI 0 RET_08.mp3 RET_08.mp3
# Portugal Anos 80
dl https://www.youtube.com/watch?v=o4pv31t-gIk 0 PT80_01_a.mp3 PT80_01_b.mp3
dl https://www.youtube.com/watch?v=Q2RB28EGxA8 0 PT80_02_a.mp3 PT80_02_b.mp3
dl https://www.youtube.com/watch?v=BBRpchprHGM 0 PT80_03_a.mp3 PT80_03_b.mp3
dl https://www.youtube.com/watch?v=IlMfi6AGP5o 0 PT80_04_a.mp3 PT80_04_b.mp3
dl https://www.youtube.com/watch?v=pQhYQLI-2Tg 0 PT80_05_a.mp3 PT80_05_b.mp3
dl https://www.youtube.com/watch?v=hbYcpMVZs5E 0 PT80_06_a.mp3 PT80_06_b.mp3
dl https://www.youtube.com/watch?v=i2PzdZ61HD4 0 PT80_07_a.mp3 PT80_07_b.mp3
echo "FASE 1 COMPLETA"
