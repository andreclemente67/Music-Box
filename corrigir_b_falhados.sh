#!/bin/bash
APP="$HOME/MusicBox/app"

baixar() {
  local url="$1" inicio="$2" dest="$3"
  find "$APP" -name "${dest%.mp3}.*" -empty -delete 2>/dev/null
  yt-dlp --force-overwrites -x --audio-format mp3 --audio-quality 0 \
    --download-sections "*${inicio}-$((inicio+15))" \
    --force-keyframes-at-cuts \
    -o "$APP/${dest%.mp3}.%(ext)s" \
    "$url" 2>/dev/null && echo "✓ $dest" || echo "✗ FALHOU: $dest"
}

echo "=== PT ==="
baixar "https://www.youtube.com/watch?v=N9weeGiL5IM" 40 "01_PT_b.mp3"
baixar "https://www.youtube.com/watch?v=zPxAnQ8Ecvk" 55 "02_PT_b.mp3"
baixar "https://www.youtube.com/watch?v=5w5HZBtgVtA" 50 "03_PT_b.mp3"
baixar "https://www.youtube.com/watch?v=4m0_bVN7Sys" 45 "04_PT_b.mp3"
baixar "https://www.youtube.com/watch?v=3LHpEMgMkZQ" 35 "05_PT_b.mp3"
baixar "https://www.youtube.com/watch?v=3e4SrqBW_8Q" 55 "06_PT_b.mp3"
baixar "https://www.youtube.com/watch?v=8Jf3_hHEXr0" 40 "07_PT_b.mp3"

echo "=== AME ==="
baixar "https://www.youtube.com/watch?v=p2oOm3OLFFU" 40 "AME_02_b.mp3"
baixar "https://www.youtube.com/watch?v=Gu5VJiAMFAE" 45 "AME_04_b.mp3"
baixar "https://www.youtube.com/watch?v=xqiRFMSJpkA" 40 "AME_05_b.mp3"
baixar "https://www.youtube.com/watch?v=nf_-aXRWNSY" 35 "AME_06_b.mp3"

echo "=== BAT ==="
baixar "https://www.youtube.com/watch?v=swBGSLBrPwM" 45 "BAT_03_b.mp3"
baixar "https://www.youtube.com/watch?v=2RYfGCYvxdc" 60 "BAT_04_b.mp3"
baixar "https://www.youtube.com/watch?v=dWJCBN0IQPY" 50 "BAT_05_b.mp3"
baixar "https://www.youtube.com/watch?v=Ro9VJMmIFRI" 40 "BAT_06_b.mp3"
baixar "https://www.youtube.com/watch?v=KsQ1bkNNKIs" 55 "BAT_07_b.mp3"

echo "=== CINEMA ==="
baixar "https://www.youtube.com/watch?v=bfYVT0MFk3U" 60 "CINEMA_01_b.mp3"
baixar "https://www.youtube.com/watch?v=fJDCVLDqFoo" 55 "CINEMA_03_b.mp3"
baixar "https://www.youtube.com/watch?v=FDH5OXNQ8p0" 60 "CINEMA_04_b.mp3"
baixar "https://www.youtube.com/watch?v=Cs6Yx2XzFIk" 50 "CINEMA_06_b.mp3"

echo "=== PT80 ==="
baixar "https://www.youtube.com/watch?v=kpCqAKBOezo" 50 "PT80_01_b.mp3"
baixar "https://www.youtube.com/watch?v=b19JHmCgBGo" 40 "PT80_02_b.mp3"
baixar "https://www.youtube.com/watch?v=3RJGcQkPYPo" 45 "PT80_03_b.mp3"
baixar "https://www.youtube.com/watch?v=vHaYfW0OBOY" 50 "PT80_04_b.mp3"

echo "=== SOLO ==="
baixar "https://www.youtube.com/watch?v=oIfMVkSsRgM" 45 "SOLO_04_b.mp3"
baixar "https://www.youtube.com/watch?v=cVJns_bMgkg" 60 "SOLO_05_b.mp3"
baixar "https://www.youtube.com/watch?v=B4jHSeFtHwA" 55 "SOLO_06_b.mp3"
baixar "https://www.youtube.com/watch?v=GbNgGcMDWFo" 70 "SOLO_07_b.mp3"

echo "=== CONCLUÍDO ==="
