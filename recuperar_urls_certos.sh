#!/bin/bash
D=~/MusicBox/app
dl() { yt-dlp -x --audio-format mp3 --audio-quality 0 -o "$D/dl_tmp.mp3" "$1" && ffmpeg -y -ss $2 -i "$D/dl_tmp.mp3" -t 30 -q:a 2 "$D/$3" && cp "$D/$3" "$D/$4" 2>/dev/null; rm -f "$D/dl_tmp.mp3"; echo "OK: $3"; }
dl https://www.youtube.com/watch?v=QkF3oxziUI4 240 SOLO_01.mp3 SOLO_01.mp3
dl https://www.youtube.com/watch?v=dLl4PZtxia8 0 SOLO_02.mp3 SOLO_02.mp3
dl https://www.youtube.com/watch?v=cWGE9Gi0bB0 0 SOLO_03.mp3 SOLO_03.mp3
dl https://www.youtube.com/watch?v=C0XwPUFfFwE 0 SOLO_05.mp3 SOLO_05.mp3
dl https://www.youtube.com/watch?v=a-L2YoesJYc 0 SOLO_07.mp3 SOLO_07.mp3
dl https://www.youtube.com/watch?v=dLl4PZtxia8 0 AME_05_a.mp3 AME_05_b.mp3
echo "COMPLETO"
