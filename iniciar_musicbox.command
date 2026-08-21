#!/bin/bash
# Arranca o Music Box (musicbox.html — o jogo/player, distinto do Studio:
# ver iniciar_editor.command) via _servidor_escrita.py na porta 8002.
# Recriado em 2026-08-21 (o ficheiro tinha sido apagado da árvore de
# trabalho; conteúdo antigo, commit "Primeira versão do Music Box", ainda
# apontava para ~/MusicBox/app e porta 8000 — ver DECISIONS.md 2026-08-21).
APP_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$APP_DIR" || exit 1

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  MUSIC BOX"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# musicbox.html usa fetch() para catalogo.json/playlists.json — não
# funciona por file://, precisa sempre de um servidor local. Desde
# 2026-08-21 o próprio _servidor_escrita.py já serve os ficheiros
# estáticos de app/ via GET (do_GET) — não precisa de python3 -m
# http.server à parte.
if lsof -i :8002 -sTCP:LISTEN >/dev/null 2>&1; then
  echo "✓ _servidor_escrita.py já estava em execução (porta 8002)"
else
  nohup python3 "$APP_DIR/_servidor_escrita.py" >> "$APP_DIR/_servidor_escrita.log" 2>&1 &
  disown
  sleep 0.8
  echo "✓ _servidor_escrita.py iniciado em background — porta 8002"
fi

open "http://localhost:8002/musicbox.html"
echo "✓ Browser aberto"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Para parar o _servidor_escrita.py: pkill -f _servidor_escrita.py"
echo ""
read -p "Pressiona Enter para fechar esta janela (o Music Box continua a correr)..."
