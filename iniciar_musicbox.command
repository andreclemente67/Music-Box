#!/bin/bash
cd ~/MusicBox/app
python3 -m http.server 8000 &
sleep 1
ULTIMO=$(ls episodio_piloto*.html 2>/dev/null | sort -V | tail -1)
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
  --autoplay-policy=no-user-gesture-required \
  --incognito \
  "http://localhost:8000/$ULTIMO" &
