#!/bin/bash
# Arranca o Music Box Studio: servidor local + auto_fusao.sh em background +
# browser. Ver DECISIONS.md (2026-08-10) para o porquê do auto_fusao.sh.
APP_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$APP_DIR" || exit 1

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  MUSIC BOX STUDIO"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# O Studio usa fetch() para catalogo.json/playlists.json — não funciona por
# file://, precisa sempre de um servidor local (ver REGRAS_OPERADORES.md §2.5).
# Desde 2026-08-21 (ver DECISIONS.md) o próprio _servidor_escrita.py (porta
# 8002, mais abaixo) já serve os ficheiros estáticos via GET — deixou de ser
# preciso arrancar `python3 -m http.server 8000` à parte.

# auto_fusao.sh: monitoriza ~/Downloads e app/catalogo_patch.json e funde
# automaticamente. Corre destacado do Terminal (nohup + disown) para
# sobreviver a esta janela ser fechada. O PRÓPRIO auto_fusao.sh já escreve
# em auto_fusao.log via tee (para se ver no ecrã se corrido à mão) — por
# isso aqui só se descarta o stdout/stderr do nohup, para não duplicar cada
# linha do log (aconteceu: >> auto_fusao.log 2>&1 aqui + tee -a lá dentro).
chmod +x "$APP_DIR/auto_fusao.sh"
nohup "$APP_DIR/auto_fusao.sh" >/dev/null 2>&1 &
disown
echo "✓ auto_fusao.sh iniciado em background — ver app/auto_fusao.log"

# _servidor_librosa.py (porta 8001): detecta o momento mais reconhecível
# dum MP3 já cortado localmente, para o botão "🎯 Detectar momento" no
# campo Clip (Cinema). Corre com o Python do venv .venv_librosa/, NUNCA
# com o Python do sistema — é lá que o librosa está instalado (ver
# DECISIONS.md: instalar librosa no Python gerido pelo Homebrew com
# --break-system-packages foi propositadamente evitado). Se o venv não
# existir ou faltar o librosa, salta este passo sem travar o resto do
# arranque — só o botão de detecção fica sem efeito.
VENV_PY="$APP_DIR/.venv_librosa/bin/python3"
if [ -x "$VENV_PY" ] && "$VENV_PY" -c "import librosa" >/dev/null 2>&1; then
  if lsof -i :8001 -sTCP:LISTEN >/dev/null 2>&1; then
    echo "✓ _servidor_librosa.py já estava em execução (porta 8001)"
  else
    nohup "$VENV_PY" "$APP_DIR/_servidor_librosa.py" >> "$APP_DIR/_servidor_librosa.log" 2>&1 &
    disown
    echo "✓ _servidor_librosa.py iniciado em background — porta 8001"
  fi
else
  echo "⚠ librosa não disponível (.venv_librosa) — botão '🎯 Detectar momento' fica sem efeito"
fi

# _servidor_escrita.py (porta 8002): escreve playlists.json/catalogo_patch.json
# etc. directamente em app/ quando o Studio clica "Guardar", sem pedir
# autorização de pasta nenhuma no browser. Stdlib puro (sem venv, ao
# contrário do _servidor_librosa.py) — ver DECISIONS.md 2026-08-13: a File
# System Access API pedia autorização a cada refresh do browser, o que se
# tornou incómodo no uso diário. Continua a existir como fallback manual
# ("📁 Autorizar pasta (fallback)" no Studio) se este servidor não estiver
# a correr.
if lsof -i :8002 -sTCP:LISTEN >/dev/null 2>&1; then
  echo "✓ _servidor_escrita.py já estava em execução (porta 8002)"
else
  nohup python3 "$APP_DIR/_servidor_escrita.py" >> "$APP_DIR/_servidor_escrita.log" 2>&1 &
  disown
  echo "✓ _servidor_escrita.py iniciado em background — porta 8002"
fi

# "✦ Gerar faixas com IA" (modal Nova Playlist, POST /gerar-faixas) precisa
# de ANTHROPIC_API_KEY no ambiente deste servidor — ver DECISIONS.md
# 2026-08-13: a chave nunca chega ao browser, só é lida aqui do lado do
# servidor. Se não estiver definida, o botão "✦ Gerar" continua visível mas
# devolve erro claro em vez de falhar silenciosamente.
if [ -z "$ANTHROPIC_API_KEY" ]; then
  echo "⚠ ANTHROPIC_API_KEY não definida — '✦ Gerar faixas com IA' vai falhar até exportares a chave (ex.: no ~/.zshrc) e reiniciares este script"
fi

open "http://localhost:8002/musicbox_studio.html"
echo "✓ Browser aberto"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Para parar o auto_fusao.sh: pkill -f auto_fusao.sh"
echo "Para parar o _servidor_librosa.py: pkill -f _servidor_librosa.py"
echo "Para parar o _servidor_escrita.py: pkill -f _servidor_escrita.py"
echo ""
read -p "Pressiona Enter para fechar esta janela (o Studio continua a correr)..."
