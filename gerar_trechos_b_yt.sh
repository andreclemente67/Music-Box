#!/bin/bash
APP="$HOME/MusicBox/app"

baixar() {
  local url="$1" inicio="$2" dest="$3"
  yt-dlp --force-overwrites -x --audio-format mp3 --audio-quality 0 \
    --download-sections "*${inicio}-$((inicio+15))" \
    --force-keyframes-at-cuts \
    -o "$APP/${dest%.mp3}.%(ext)s" \
    "$url" 2>/dev/null && echo "✓ $dest" || echo "✗ FALHOU: $dest"
}

echo "=== ANOS 80 ==="
baixar "https://www.youtube.com/watch?v=djV11Xbc914" 55  "01_b.mp3"   # Take On Me — refrão
baixar "https://www.youtube.com/watch?v=o9UmSMQmkME" 80  "02_b.mp3"   # Sweet Child — verso 2
baixar "https://www.youtube.com/watch?v=gBOg0Hj9KzM" 60  "03_b.mp3"   # Power of Love — refrão
baixar "https://www.youtube.com/watch?v=uPudE8nDog0" 45  "04_b.mp3"   # Don't You Want Me — refrão
baixar "https://www.youtube.com/watch?v=9jK-NcRmVcw" 35  "05_b.mp3"   # Final Countdown — refrão
baixar "https://www.youtube.com/watch?v=OMOGaugKpzs" 50  "06_b.mp3"   # Every Breath — refrão
baixar "https://www.youtube.com/watch?v=Zi_XLOBDo_Y" 50  "07_b.mp3"   # Billie Jean — refrão

echo "=== MÚSICA PORTUGUESA ==="
baixar "https://www.youtube.com/watch?v=_P-3QTHMSCs" 40  "01_PT_b.mp3"  # Grândola — refrão
baixar "https://www.youtube.com/watch?v=zPxAnQ8Ecvk" 55  "02_PT_b.mp3"  # Não Sou O Único
baixar "https://www.youtube.com/watch?v=5w5HZBtgVtA" 50  "03_PT_b.mp3"  # Cantiga d'Amor
baixar "https://www.youtube.com/watch?v=4m0_bVN7Sys" 45  "04_PT_b.mp3"  # Pronúncia do Norte
baixar "https://www.youtube.com/watch?v=3LHpEMgMkZQ" 35  "05_PT_b.mp3"  # Amor de Água Fresca
baixar "https://www.youtube.com/watch?v=3e4SrqBW_8Q" 55  "06_PT_b.mp3"  # Canção do Mar
baixar "https://www.youtube.com/watch?v=8Jf3_hHEXr0" 40  "07_PT_b.mp3"  # Re-Tratamento

echo "=== SOLO DE GUITARRA ==="
baixar "https://www.youtube.com/watch?v=QkF3oxziUI4" 382 "SOLO_01_b.mp3" # Stairway — solo
baixar "https://www.youtube.com/watch?v=09839DpTctU" 195 "SOLO_02_b.mp3" # Hotel California — solo
baixar "https://www.youtube.com/watch?v=_FrOQC-zEog" 120 "SOLO_03_b.mp3" # Shine On — parte 2
baixar "https://www.youtube.com/watch?v=oIfMVkSsRgM" 45  "SOLO_04_b.mp3" # Eruption — clímax
baixar "https://www.youtube.com/watch?v=cVJns_bMgkg" 60  "SOLO_05_b.mp3" # Voodoo Child — solo
baixar "https://www.youtube.com/watch?v=B4jHSeFtHwA" 55  "SOLO_06_b.mp3" # Layla — solo
baixar "https://www.youtube.com/watch?v=GbNgGcMDWFo" 70  "SOLO_07_b.mp3" # Surfing — clímax

echo "=== BATERIA ==="
baixar "https://www.youtube.com/watch?v=YkADj0TPrJA" 165 "BAT_01_b.mp3"  # In the Air Tonight — solo
baixar "https://www.youtube.com/watch?v=-tJYN-eG1zk" 20  "BAT_02_b.mp3"  # We Will Rock You — vocal
baixar "https://www.youtube.com/watch?v=swBGSLBrPwM" 45  "BAT_03_b.mp3"  # Hot For Teacher
baixar "https://www.youtube.com/watch?v=2RYfGCYvxdc" 60  "BAT_04_b.mp3"  # Moby Dick
baixar "https://www.youtube.com/watch?v=dWJCBN0IQPY" 50  "BAT_05_b.mp3"  # YYZ
baixar "https://www.youtube.com/watch?v=Ro9VJMmIFRI" 40  "BAT_06_b.mp3"  # Rock of Ages
baixar "https://www.youtube.com/watch?v=KsQ1bkNNKIs" 55  "BAT_07_b.mp3"  # Los Endos

echo "=== CINEMA ==="
baixar "https://www.youtube.com/watch?v=bfYVT0MFk3U" 60  "CINEMA_01_b.mp3" # Blade Runner
baixar "https://www.youtube.com/watch?v=_D0ZQPqeJkk" 35  "CINEMA_02_b.mp3" # Star Wars
baixar "https://www.youtube.com/watch?v=fJDCVLDqFoo" 55  "CINEMA_03_b.mp3" # ET
baixar "https://www.youtube.com/watch?v=FDH5OXNQ8p0" 60  "CINEMA_04_b.mp3" # Apocalypse Now
baixar "https://www.youtube.com/watch?v=RxabLA7UQ9k" 70  "CINEMA_05_b.mp3" # Time — Inception
baixar "https://www.youtube.com/watch?v=Cs6Yx2XzFIk" 50  "CINEMA_06_b.mp3" # The Mission
baixar "https://www.youtube.com/watch?v=e-QFj59PON4" 40  "CINEMA_07_b.mp3" # 2001

echo "=== AMERICANA ==="
baixar "https://www.youtube.com/watch?v=1vrEljMfXYo" 35  "AME_01_b.mp3"  # Country Roads — refrão
baixar "https://www.youtube.com/watch?v=p2oOm3OLFFU" 40  "AME_02_b.mp3"  # Heart of Gold
baixar "https://www.youtube.com/watch?v=PLj1-CMNERM" 55  "AME_03_b.mp3"  # Mr. Tambourine Man
baixar "https://www.youtube.com/watch?v=Gu5VJiAMFAE" 45  "AME_04_b.mp3"  # Have You Ever Seen
baixar "https://www.youtube.com/watch?v=xqiRFMSJpkA" 40  "AME_05_b.mp3"  # Take It Easy
baixar "https://www.youtube.com/watch?v=nf_-aXRWNSY" 35  "AME_06_b.mp3"  # Horse With No Name
baixar "https://www.youtube.com/watch?v=nvlTJrNJ5lA" 50  "AME_07_b.mp3"  # Free Fallin'

echo "=== ANOS 2010+ ==="
baixar "https://www.youtube.com/watch?v=HL1UzIK-flA" 45  "A10_01_b.mp3"  # Work — refrão
baixar "https://www.youtube.com/watch?v=JGwWNGJdvx8" 50  "A10_02_b.mp3"  # Shape of You
baixar "https://www.youtube.com/watch?v=OPf0YbXqDm0" 55  "A10_03_b.mp3"  # Uptown Funk
baixar "https://www.youtube.com/watch?v=4NRXx6U8ABQ" 50  "A10_04_b.mp3"  # Blinding Lights
baixar "https://www.youtube.com/watch?v=rYEDA3JcQqw" 45  "A10_05_b.mp3"  # Rolling in the Deep
baixar "https://www.youtube.com/watch?v=w2Ov5jzm3j8" 30  "A10_06_b.mp3"  # Old Town Road
baixar "https://www.youtube.com/watch?v=DyDfgMOUjCI" 45  "A10_07_b.mp3"  # Bad Guy

echo "=== PORTUGAL ANOS 80 ==="
baixar "https://www.youtube.com/watch?v=kpCqAKBOezo" 50  "PT80_01_b.mp3" # Porto Sentido
baixar "https://www.youtube.com/watch?v=b19JHmCgBGo" 40  "PT80_02_b.mp3" # Playback
baixar "https://www.youtube.com/watch?v=3RJGcQkPYPo" 45  "PT80_03_b.mp3" # Paixão
baixar "https://www.youtube.com/watch?v=vHaYfW0OBOY"    50  "PT80_04_b.mp3" # Estrada da Luz
baixar "https://www.youtube.com/watch?v=pQhYQLI-2Tg"    40  "PT80_05_b.mp3" # A Minha Casinha
baixar "https://www.youtube.com/watch?v=i2PzdZ61HD4"    45  "PT80_06_b.mp3" # Um Grande Grande Amor
baixar "https://www.youtube.com/watch?v=i2PzdZ61HD4"    50  "PT80_07_b.mp3" # Conto de Réis

echo "=== CONCLUÍDO ==="
