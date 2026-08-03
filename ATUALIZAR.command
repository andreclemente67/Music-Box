#!/bin/bash
APP="$HOME/MusicBox/app"
DESCARGAS="$HOME/Descargas"
HTML="episodio_piloto2.html"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  MUSIC BOX — ATUALIZAR"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ ! -f "$DESCARGAS/$HTML" ]; then
  echo "⚠️  Nenhum $HTML encontrado em Descargas."
  read -p "Pressiona Enter para fechar..."
  exit 1
fi

cp "$DESCARGAS/$HTML" "$APP/$HTML"
echo "✓ HTML copiado para app/"
rm "$DESCARGAS/$HTML"
echo "✓ Removido de Descargas"

pkill -f "python3 -m http.server 8000" 2>/dev/null
sleep 0.5
cd "$APP"
python3 -m http.server 8000 &>/dev/null &
sleep 0.8
echo "✓ Servidor reiniciado"

open "http://localhost:8000/$HTML"
echo "✓ Browser aberto"
echo ""
grep -o 'BUILD [0-9-]*' "$APP/$HTML" | head -1
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
