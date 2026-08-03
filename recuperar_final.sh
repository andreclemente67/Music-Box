#!/bin/bash
D=~/MusicBox/app
dl() { yt-dlp -x --audio-format mp3 --audio-quality 0 -o "$D/dl_tmp.mp3" "$1" && ffmpeg -y -ss $2 -i "$D/dl_tmp.mp3" -t 30 -q:a 2 "$D/$3" && cp "$D/$3" "$D/$4" 2>/dev/null; rm -f "$D/dl_tmp.mp3"; echo "OK: $3"; }
# Anos 80 faixa 4
dl https://www.youtube.com/watch?v=SJcKqJCEBhQ 0 04_a.mp3 04_b.mp3
# Solo Guitarra
dl https://www.youtube.com/watch?v=M4Czx8EWXb0 0 SOLO_04.mp3 SOLO_04.mp3
dl https://www.youtube.com/watch?v=N70lxcC7uvE 0 SOLO_06.mp3 SOLO_06.mp3
# Americana
dl https://www.youtube.com/watch?v=1vrEljMfXYo 0 AME_01_a.mp3 AME_01_b.mp3
dl https://www.youtube.com/watch?v=EQ_vJN3GrFI 0 AME_02_a.mp3 AME_02_b.mp3
dl https://www.youtube.com/watch?v=6l9y4TmRjxA 0 AME_03_a.mp3 AME_03_b.mp3
dl https://www.youtube.com/watch?v=mytHDiGGShA 0 AME_04_a.mp3 AME_04_b.mp3
dl https://www.youtube.com/watch?v=tpUFhL6oFE0 0 AME_06_a.mp3 AME_06_b.mp3
# Cinema em falta
dl https://www.youtube.com/watch?v=YkADj0TPrJA 0 CINEMA_01_a.mp3 CINEMA_01_b.mp3
dl https://www.youtube.com/watch?v=kwiawhDk2TM 0 CINEMA_03_a.mp3 CINEMA_03_b.mp3
dl https://www.youtube.com/watch?v=IZBlqcbpmxY 0 CINEMA_04_a.mp3 CINEMA_04_b.mp3
dl https://www.youtube.com/watch?v=iXQUu5Dti4g 0 CINEMA_06_a.mp3 CINEMA_06_b.mp3
# Solo Bateria
dl https://www.youtube.com/watch?v=YkADj0TPrJA 0 BAT_01_a.mp3 BAT_01_a.mp3
dl https://www.youtube.com/watch?v=4uleJD8UQSA 0 BAT_02_a.mp3 BAT_02_a.mp3
dl https://www.youtube.com/watch?v=cWGE9Gi0bB0 0 BAT_03_a.mp3 BAT_03_a.mp3
dl https://www.youtube.com/watch?v=r4OiLTjDqB0 0 BAT_04_a.mp3 BAT_04_a.mp3
dl https://www.youtube.com/watch?v=3rYTBtMYMJE 0 BAT_05_a.mp3 BAT_05_a.mp3
dl https://www.youtube.com/watch?v=mWJxn8bUCUY 0 BAT_06_a.mp3 BAT_06_a.mp3
dl https://www.youtube.com/watch?v=lERBJOGcAB4 0 BAT_07_a.mp3 BAT_07_a.mp3
# Anos 2010
dl https://www.youtube.com/watch?v=bongjKtJehc 0 A10_05_a.mp3 A10_05_b.mp3
dl https://www.youtube.com/watch?v=pzpSHGhHFR0 0 A10_06_a.mp3 A10_06_b.mp3
echo "FINAL COMPLETO"
