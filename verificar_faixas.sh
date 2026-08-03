#!/bin/bash
PASTA=~/MusicBox/app
DURACAO=10
VERDE='\033[0;32m'; VERMELHO='\033[0;31m'; AMARELO='\033[1;33m'; RESET='\033[0m'; BOLD='\033[1m'
problemas=()

tocar_e_confirmar() {
  local ficheiro="$1"; local label="$2"
  if [ ! -f "$PASTA/$ficheiro" ]; then
    echo -e "  ${VERMELHO}✗ FALTA: $ficheiro${RESET}"
    problemas+=("FALTA: $label ($ficheiro)"); return
  fi
  echo -e "  ▶ $label"
  afplay -t $DURACAO "$PASTA/$ficheiro" 2>/dev/null &
  PID=$!; sleep $DURACAO; kill $PID 2>/dev/null; wait $PID 2>/dev/null
  echo -n "  [S/n/r]: "; read -r resposta; resposta=${resposta:-S}
  case "$(echo "$resposta" | tr '[:lower:]' '[:upper:]')" in
    R) tocar_e_confirmar "$ficheiro" "$label" ;;
    N) echo -e "  ${VERMELHO}✗ Problema${RESET}"; problemas+=("PROBLEMA: $label ($ficheiro)") ;;
    *) echo -e "  ${VERDE}✓${RESET}" ;;
  esac
}

verificar_playlist() {
  local nome="$1"; shift
  echo -e "\n${BOLD}${AMARELO}━━━ $nome ━━━${RESET}"
  while [ $# -gt 0 ]; do
    local label="$1"; local ficheiro="$2"; shift 2
    tocar_e_confirmar "$ficheiro" "$label"
  done
}

playlist_PT() {
  verificar_playlist "MÚSICA PORTUGUESA" \
    "1A · Grândola — José Afonso" "01_PT_a.mp3" \
    "1B · Grândola — José Afonso" "01_PT_b.mp3" \
    "2A · Não Sou O Único — Xutos" "02_PT_a.mp3" \
    "2B · Não Sou O Único — Xutos" "02_PT_b.mp3" \
    "3A · Cantiga d'Amor — Rádio Macau" "03_PT_a.mp3" \
    "3B · Cantiga d'Amor — Rádio Macau" "03_PT_b.mp3" \
    "4A · Pronúncia do Norte — GNR" "04_PT_a.mp3" \
    "4B · Pronúncia do Norte — GNR" "04_PT_b.mp3" \
    "5A · Amor de Água Fresca — Dina" "05_PT_a.mp3" \
    "5B · Amor de Água Fresca — Dina" "05_PT_b.mp3" \
    "6A · Canção do Mar — Dulce Pontes" "06_PT_a.mp3" \
    "6B · Canção do Mar — Dulce Pontes" "06_PT_b.mp3" \
    "7A · Re-Tratamento — Da Weasel" "07_PT_a.mp3" \
    "7B · Re-Tratamento — Da Weasel" "07_PT_b.mp3" \
    "🧩 Mosaico PT" "MOSAICO_PT.mp3"
}

playlist_ANOS80() {
  verificar_playlist "ANOS 80" \
    "1A · Take On Me — A-ha" "01_a.mp3" \
    "1B · Take On Me — A-ha" "01_b.mp3" \
    "2A · Sweet Child O' Mine — GNR" "02_a.mp3" \
    "2B · Sweet Child O' Mine — GNR" "02_b.mp3" \
    "3A · Power of Love — Frankie GTH" "03_a.mp3" \
    "3B · Power of Love — Frankie GTH" "03_b.mp3" \
    "4A · Don't You Want Me — Human League" "04_a.mp3" \
    "4B · Don't You Want Me — Human League" "04_b.mp3" \
    "5A · Final Countdown — Europe" "05_a.mp3" \
    "5B · Final Countdown — Europe" "05_b.mp3" \
    "6A · Every Breath — The Police" "06_a.mp3" \
    "6B · Every Breath — The Police" "06_b.mp3" \
    "7A · Billie Jean — Michael Jackson" "07_a.mp3" \
    "7B · Billie Jean — Michael Jackson" "07_b.mp3" \
    "🧩 Mosaico Anos 80" "MOSAICO_ANOS80.mp3"
}

playlist_RETRATO() {
  verificar_playlist "RETRATO SONORO — VOZES LENDÁRIAS" \
    "1 · My Way — Frank Sinatra" "RET_01.mp3" \
    "2 · Can't Help Falling — Elvis" "RET_02.mp3" \
    "3 · Love of My Life — Freddie" "RET_03.mp3" \
    "4 · Billie Jean — Michael Jackson" "RET_04.mp3" \
    "5 · I Will Always Love You — Whitney" "RET_05.mp3" \
    "6 · Rocket Man — Elton John" "RET_06.mp3" \
    "7 · Estou Além — António Variações" "RET_07.mp3" \
    "8 · Let's Dance — David Bowie" "RET_08.mp3" \
    "🧩 Mosaico Retrato" "MOSAICO_RETRATO.mp3"
}

playlist_SOLO() {
  verificar_playlist "SOLO DE GUITARRA" \
    "1 · Stairway to Heaven — Led Zeppelin" "SOLO_01.mp3" \
    "2 · Hotel California — Eagles" "SOLO_02.mp3" \
    "3 · Shine On — Pink Floyd" "SOLO_03.mp3" \
    "4 · Eruption — Van Halen" "SOLO_04.mp3" \
    "5 · Voodoo Child — Jimi Hendrix" "SOLO_05.mp3" \
    "6 · Layla — Derek and the Dominos" "SOLO_06.mp3" \
    "7 · Surfing with the Alien — Satriani" "SOLO_07.mp3" \
    "🧩 Mosaico Solo" "MOSAICO_SOLO.mp3"
}

playlist_CINEMA() {
  verificar_playlist "CINEMA" \
    "1A · Blade Runner — Vangelis" "CINEMA_01_a.mp3" \
    "1B · Blade Runner — Vangelis" "CINEMA_01_b.mp3" \
    "2A · Star Wars — John Williams" "CINEMA_02_a.mp3" \
    "2B · Star Wars — John Williams" "CINEMA_02_b.mp3" \
    "3A · ET — John Williams" "CINEMA_03_a.mp3" \
    "3B · ET — John Williams" "CINEMA_03_b.mp3" \
    "4A · Apocalypse Now — The Doors" "CINEMA_04_a.mp3" \
    "4B · Apocalypse Now — The Doors" "CINEMA_04_b.mp3" \
    "5A · Time — Hans Zimmer" "CINEMA_05_a.mp3" \
    "5B · Time — Hans Zimmer" "CINEMA_05_b.mp3" \
    "6A · The Mission — Morricone" "CINEMA_06_a.mp3" \
    "6B · The Mission — Morricone" "CINEMA_06_b.mp3" \
    "7A · 2001 — Strauss" "CINEMA_07_a.mp3" \
    "7B · 2001 — Strauss" "CINEMA_07_b.mp3" \
    "🧩 Mosaico Cinema" "MOSAICO_CINEMA.mp3"
}

playlist_AMERICANA() {
  verificar_playlist "AMERICANA" \
    "1A · Country Roads — John Denver" "AME_01_a.mp3" \
    "1B · Country Roads — John Denver" "AME_01_b.mp3" \
    "2A · Heart of Gold — Neil Young" "AME_02_a.mp3" \
    "2B · Heart of Gold — Neil Young" "AME_02_b.mp3" \
    "3A · Tambourine Man — Bob Dylan" "AME_03_a.mp3" \
    "3B · Tambourine Man — Bob Dylan" "AME_03_b.mp3" \
    "4A · Have You Ever Seen the Rain — CCR" "AME_04_a.mp3" \
    "4B · Have You Ever Seen the Rain — CCR" "AME_04_b.mp3" \
    "5A · Take It Easy — Eagles" "AME_05_a.mp3" \
    "5B · Take It Easy — Eagles" "AME_05_b.mp3" \
    "6A · A Horse With No Name — America" "AME_06_a.mp3" \
    "6B · A Horse With No Name — America" "AME_06_b.mp3" \
    "7A · Free Fallin' — Tom Petty" "AME_07_a.mp3" \
    "7B · Free Fallin' — Tom Petty" "AME_07_b.mp3" \
    "🧩 Mosaico Americana" "MOSAICO_AMERICANA.mp3"
}

playlist_BATERIA() {
  verificar_playlist "SOLO DE BATERIA" \
    "1 · In the Air Tonight — Phil Collins" "BAT_01_a.mp3" \
    "2 · We Will Rock You — Queen" "BAT_02_a.mp3" \
    "3 · Hot For Teacher — Van Halen" "BAT_03_a.mp3" \
    "4 · Moby Dick — Led Zeppelin" "BAT_04_a.mp3" \
    "5 · YYZ — Rush" "BAT_05_a.mp3" \
    "6 · Rock of Ages — Def Leppard" "BAT_06_a.mp3" \
    "7 · Los Endos — Genesis" "BAT_07_a.mp3" \
    "🧩 Mosaico Bateria" "MOSAICO_BATERIA.mp3"
}

playlist_ANOS2010() {
  verificar_playlist "ANOS 2010+" \
    "1A · Work — Rihanna" "A10_01_a.mp3" \
    "1B · Work — Rihanna" "A10_01_b.mp3" \
    "2A · Shape of You — Ed Sheeran" "A10_02_a.mp3" \
    "2B · Shape of You — Ed Sheeran" "A10_02_b.mp3" \
    "3A · Uptown Funk — Mark Ronson" "A10_03_a.mp3" \
    "3B · Uptown Funk — Mark Ronson" "A10_03_b.mp3" \
    "4A · Blinding Lights — The Weeknd" "A10_04_a.mp3" \
    "4B · Blinding Lights — The Weeknd" "A10_04_b.mp3" \
    "5A · Rolling in the Deep — Adele" "A10_05_a.mp3" \
    "5B · Rolling in the Deep — Adele" "A10_05_b.mp3" \
    "6A · Old Town Road — Lil Nas X" "A10_06_a.mp3" \
    "6B · Old Town Road — Lil Nas X" "A10_06_b.mp3" \
    "7A · Bad Guy — Billie Eilish" "A10_07_a.mp3" \
    "7B · Bad Guy — Billie Eilish" "A10_07_b.mp3" \
    "🧩 Mosaico Anos 2010" "MOSAICO_ANOS2010.mp3"
}

playlist_PT80() {
  verificar_playlist "PORTUGAL — ANOS 80" \
    "1A · Porto Sentido — Rui Veloso" "PT80_01_a.mp3" \
    "1B · Porto Sentido — Rui Veloso" "PT80_01_b.mp3" \
    "2A · Playback — Carlos Paião" "PT80_02_a.mp3" \
    "2B · Playback — Carlos Paião" "PT80_02_b.mp3" \
    "3A · Paixão — Heróis do Mar" "PT80_03_a.mp3" \
    "3B · Paixão — Heróis do Mar" "PT80_03_b.mp3" \
    "4A · Estrada da Luz — Trovante" "PT80_04_a.mp3" \
    "4B · Estrada da Luz — Trovante" "PT80_04_b.mp3" \
    "5A · A Minha Casinha — Xutos" "PT80_05_a.mp3" \
    "5B · A Minha Casinha — Xutos" "PT80_05_b.mp3" \
    "6A · Um Grande Amor — Fernando Tordo" "PT80_06_a.mp3" \
    "6B · Um Grande Amor — Fernando Tordo" "PT80_06_b.mp3" \
    "7A · Conto de Réis — José Cid" "PT80_07_a.mp3" \
    "7B · Conto de Réis — José Cid" "PT80_07_b.mp3" \
    "🧩 Mosaico PT80" "MOSAICO_PT80.mp3"
}

echo -e "\n${BOLD}MUSIC BOX — VERIFICAÇÃO [S/n/r]${RESET}"
PLAYLIST="$(echo "${1:-}" | tr '[:lower:]' '[:upper:]')"
case "$PLAYLIST" in
  PT)       playlist_PT ;;
  ANOS80)   playlist_ANOS80 ;;
  RETRATO)  playlist_RETRATO ;;
  SOLO)     playlist_SOLO ;;
  CINEMA)   playlist_CINEMA ;;
  AMERICANA) playlist_AMERICANA ;;
  BATERIA)  playlist_BATERIA ;;
  ANOS2010) playlist_ANOS2010 ;;
  PT80)     playlist_PT80 ;;
  "")
    playlist_PT; playlist_ANOS80; playlist_RETRATO
    playlist_SOLO; playlist_CINEMA; playlist_AMERICANA
    playlist_BATERIA; playlist_ANOS2010; playlist_PT80
    ;;
  *) echo "Uso: $0 [PT|ANOS80|RETRATO|SOLO|CINEMA|AMERICANA|BATERIA|ANOS2010|PT80]"; exit 1 ;;
esac

echo -e "\n${BOLD}${AMARELO}━━━ RESUMO ━━━${RESET}"
if [ ${#problemas[@]} -eq 0 ]; then
  echo -e "${VERDE}✓ Tudo OK${RESET}"
else
  for p in "${problemas[@]}"; do echo -e "  ${VERMELHO}✗ $p${RESET}"; done
fi
