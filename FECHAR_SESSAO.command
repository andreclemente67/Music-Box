#!/bin/bash
APP="$HOME/MusicBox/app"
BACKUP="$HOME/MusicBox/backups"
mkdir -p "$BACKUP" "$BACKUP/mp3" "$BACKUP/jpg"

DATA=$(date +%Y-%m-%d)
NN=01
while [ -f "$BACKUP/episodio_piloto2_${DATA}-${NN}.html" ]; do
  NN=$(printf "%02d" $((10#$NN + 1)))
done
BUILD="${DATA}-${NN}"

python3 << PYEOF
import re, os
path = '$APP/episodio_piloto2.html'
content = open(path).read()
content = re.sub(r'BUILD \d{4}-\d{2}-\d{2}-\d{2}', f'BUILD $BUILD', content)
open(path, 'w').write(content)
print('BUILD atualizado: $BUILD')
PYEOF

cp "$APP/episodio_piloto2.html" "$BACKUP/episodio_piloto2_${BUILD}.html"
echo "✓ Backup HTML guardado"

rsync -a "$APP/"*.mp3 "$BACKUP/mp3/"
echo "✓ Backup MP3 sincronizado"

rsync -a "$APP/"*.jpg "$BACKUP/jpg/" 2>/dev/null
echo "✓ Backup JPG sincronizado"

echo ""
echo "Backups disponíveis:"
ls -lh "$BACKUP/" | awk '{print $NF, $5}' | tail -10

echo ""
echo "✅ Sessão encerrada — BUILD $BUILD"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  📋 LEMBRETE PARA A PRÓXIMA SESSÃO COM O CLAUDE:"
echo ""
echo "  Arrasta episodio_piloto2.html + MUSICBOX_HANDOFF.md"
echo "  para o chat no início da sessão."
echo ""
echo "  Ficheiros em: ~/MusicBox/app/"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
read -p "Pressiona Enter para fechar..."
