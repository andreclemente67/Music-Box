#!/bin/bash
# Copia um novo build do Music Box (HTML) de Downloads para app/ e abre-o
# no browser via _servidor_escrita.py (porta 8002). Actualizado em
# 2026-08-21 — ver DECISIONS.md: caminho antigo ($HOME/MusicBox/app),
# pasta "Descargas" (não existe neste Mac — a real é Downloads) e porta
# 8000/http.server estavam todos desactualizados; ficheiro alvo
# actualizado de "episodio_piloto2.html" (versão antiga) para
# "musicbox.html" (nome actual do mesmo ficheiro — ver git: rename
# episodio_piloto4.html -> musicbox.html).
APP_DIR="$(cd "$(dirname "$0")" && pwd)"
DOWNLOADS="$HOME/Downloads"
HTML="musicbox.html"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  MUSIC BOX — ATUALIZAR"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ ! -f "$DOWNLOADS/$HTML" ]; then
  echo "⚠️  Nenhum $HTML encontrado em Downloads."
  read -p "Pressiona Enter para fechar..."
  exit 1
fi

cp "$DOWNLOADS/$HTML" "$APP_DIR/$HTML"
echo "✓ HTML copiado para app/"
rm "$DOWNLOADS/$HTML"
echo "✓ Removido de Downloads"

# _servidor_escrita.py (porta 8002) já serve os ficheiros estáticos via GET
# (do_GET) — não reinicia se já estiver a correr, para não interromper uma
# sessão do Studio em curso a usá-lo para escrever (ver DECISIONS.md
# 2026-08-21, incidente com pkill genérico numa sessão anterior).
if lsof -i :8002 -sTCP:LISTEN >/dev/null 2>&1; then
  echo "✓ _servidor_escrita.py já estava em execução (porta 8002)"
else
  nohup python3 "$APP_DIR/_servidor_escrita.py" >> "$APP_DIR/_servidor_escrita.log" 2>&1 &
  disown
  sleep 0.8
  echo "✓ _servidor_escrita.py iniciado em background — porta 8002"
fi

open "http://localhost:8002/$HTML"
echo "✓ Browser aberto"
echo ""
grep -o 'BUILD [0-9-]*' "$APP_DIR/$HTML" | head -1
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
