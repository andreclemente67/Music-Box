#!/bin/bash
D=~/MusicBox/app
dl() { yt-dlp -x --audio-format mp3 --audio-quality 0 -o "$D/dl_tmp.mp3" "$1" && ffmpeg -y -ss $2 -i "$D/dl_tmp.mp3" -t 30 -q:a 2 "$D/$3" && cp "$D/$3" "$D/$4" 2>/dev/null; rm -f "$D/dl_tmp.mp3"; echo "OK: $3"; }
# Anos 80 faixa 4 - Human League
dl https://www.youtube.com/watch?v=uPudE8nDog0 0 04_a.mp3 04_b.mp3
# Americana
dl https://www.youtube.com/watch?v=kldxFW_7hpI 0 AME_02_a.mp3 AME_02_b.mp3
dl https://www.youtube.com/watch?v=JKES3yfnD9U 0 AME_04_a.mp3 AME_04_b.mp3
dl https://www.youtube.com/watch?v=dLl4PZtxia8 0 AME_03_a.mp3 AME_03_b.mp3
dl https://www.youtube.com/watch?v=1lWJXDG2i0A 0 AME_06_a.mp3 AME_06_b.mp3
# Solo Bateria
dl https://www.youtube.com/watch?v=YkADj0TPrJA 180 BAT_02_a.mp3 BAT_02_a.mp3
dl https://www.youtube.com/watch?v=WtFd74B7HRk 0 BAT_04_a.mp3 BAT_04_a.mp3
dl https://www.youtube.com/watch?v=3rYTBtMYMJE 0 BAT_05_a.mp3 BAT_05_a.mp3
dl https://www.youtube.com/watch?v=QkF3oxziUI4 0 BAT_06_a.mp3 BAT_06_a.mp3
dl https://www.youtube.com/watch?v=cWGE9Gi0bB0 120 BAT_07_a.mp3 BAT_07_a.mp3
# Anos 2010
dl https://www.youtube.com/watch?v=r7qovpFAGrQ 0 A10_05_a.mp3 A10_05_b.mp3
dl https://www.youtube.com/watch?v=DyDfgMOUjCI 0 A10_06_a.mp3 A10_06_b.mp3
echo "ULTIMO COMPLETO"
