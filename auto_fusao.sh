#!/bin/bash
# Monitoriza dois ficheiros e funde-os automaticamente em catalogo.json
# assim que aparecem/mudam — depois apaga-os:
#   1. app/catalogo_adicionar.json — faixas novas da "Adicionar Faixa",
#      escritas directamente pelo Studio via _servidor_escrita.py
#      (POST /escrever). Fusão em modo "skip": nunca sobrescreve um id já
#      existente. Corrigido em 2026-08-25 (ver DECISIONS.md) — antes
#      vigiava ~/Downloads/catalogo_adicionar.json, o sítio antigo de
#      quando só existia o download manual pelo browser; o Studio deixou
#      de escrever ali, por isso os ficheiros ficavam parados em app/ sem
#      nunca serem apanhados por este loop.
#   2. app/catalogo_patch.json — edições a faixas já existentes (trecho_a
#      via "Definir início", `imagem` via Wikimedia/URL manual) escritas
#      directamente pela File System Access API (escreverFicheiro(), sem
#      passar por Downloads). Fusão em modo "upsert": SUBSTITUI a entrada
#      existente pela versão nova, porque é precisamente para isso que este
#      ficheiro existe — em "skip" as edições seriam descartadas em
#      silêncio (ver comentário em _fundir_catalogo.py).
#   3. mp3_index.json — lista (JSON) de todos os .mp3 em app/ + app/
#      originais/, para o autoMatchMp3() no Studio. Regenerado a cada
#      iteração do loop mas só REESCRITO em disco quando o conteúdo muda
#      (a pasta está em iCloud Drive — evita sincronizar a cada 2s à toa).
#
# ATENÇÃO — excepção documentada ao padrão do projecto: em todo o resto do
# Studio, "download + fusão" é sempre manual ("fusão manual obrigatória",
# ver DECISIONS.md/REGRAS_OPERADORES.md). Este script é a ÚNICA fusão
# automática, sem revisão humana, pedida explicitamente pelo utilizador em
# 2026-08-10 (Downloads) e alargada a catalogo_patch.json em 2026-08-11 —
# ver DECISIONS.md para o registo completo e as protecções abaixo, que não
# foram pedidas mas foram adicionadas por segurança (o ficheiro de origem é
# apagado, e catalogo.json é a única fonte de verdade das faixas):
#   - modo "skip" (catalogo_adicionar.json): nunca sobrescreve um id já
#     existente (salta-o, avisa); modo "upsert" (catalogo_patch.json): substitui
#   - só apaga o ficheiro de origem se a fusão foi bem sucedida
#   - faz backup de catalogo.json antes de cada fusão (backups_catalogo/)
#   - espera o ficheiro estabilizar (parar de crescer) antes de o ler
#   - regista cada fusão/erro em auto_fusao.log
#
# Iniciado por iniciar_editor.command. Corre em loop até o processo ser
# terminado (ex.: fechar o Terminal, ou `pkill -f auto_fusao.sh`).

set -uo pipefail

APP_DIR="$(cd "$(dirname "$0")" && pwd)"
CATALOGO="$APP_DIR/catalogo.json"
BACKUP_DIR="$APP_DIR/backups_catalogo"
LOG="$APP_DIR/auto_fusao.log"
ALVO_ADICIONAR="catalogo_adicionar.json"
FICHEIRO_ADICIONAR="$APP_DIR/$ALVO_ADICIONAR"
FICHEIRO_PATCH="$APP_DIR/catalogo_patch.json"
LOCKFILE="/tmp/musicbox_auto_fusao.lock"

if [ -f "$LOCKFILE" ] && kill -0 "$(cat "$LOCKFILE" 2>/dev/null)" 2>/dev/null; then
  echo "auto_fusao.sh já está em execução (PID $(cat "$LOCKFILE")) — a sair."
  exit 1
fi
echo $$ > "$LOCKFILE"
trap 'rm -f "$LOCKFILE"' EXIT

mkdir -p "$BACKUP_DIR"

log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG"
}

# Espera o ficheiro estabilizar (pode ainda estar a ser escrito/descarregado),
# funde-o em catalogo.json com o modo dado, e apaga-o se correu bem.
# Argumentos: <caminho ficheiro> <nome para o log> <modo skip|upsert>
fundir_se_pronto() {
  local ficheiro="$1" nome="$2" modo="$3"

  [ -f "$ficheiro" ] || return 0

  local tam1 tam2
  tam1=$(stat -f%z "$ficheiro" 2>/dev/null || echo 0)
  sleep 1
  tam2=$(stat -f%z "$ficheiro" 2>/dev/null || echo 0)
  if [ "$tam1" != "$tam2" ] || [ "$tam1" = "0" ]; then
    return 0
  fi

  local erro_tmp n status aviso
  erro_tmp=$(mktemp)
  n=$(python3 "$APP_DIR/_fundir_catalogo.py" "$ficheiro" "$CATALOGO" "$BACKUP_DIR" "$modo" 2>"$erro_tmp")
  status=$?
  aviso="$(cat "$erro_tmp")"
  rm -f "$erro_tmp"

  if [ $status -eq 0 ]; then
    rm -f "$ficheiro"
    echo "Fundido: $n faixas"
    log "Fundido: $n faixas (de $nome, modo $modo) — ficheiro removido"
    [ -n "$aviso" ] && log "Aviso: $aviso"
  else
    log "ERRO ao fundir $nome (modo $modo) — ficheiro MANTIDO para inspecção manual. Detalhe: $aviso"
  fi
}

# Índice de ficheiros .mp3 (app/ + app/originais/, 2 níveis) para o
# autoMatchMp3() no Studio. Só reescreve mp3_index.json quando o conteúdo
# realmente muda — esta pasta está em iCloud Drive, e reescrever a cada 2s
# sem necessidade (o ciclo do loop principal) geraria sincronização
# constante sem qualquer alteração real. Comparação por conteúdo (cmp -s),
# não por mtime dos .mp3, para não depender de relógios de ficheiro do iCloud.
INDICE_MP3="$APP_DIR/mp3_index.json"

atualizar_indice_mp3() {
  local tmp
  tmp=$(mktemp)
  find "$APP_DIR" -maxdepth 2 -iname "*.mp3" -type f | sed "s|^$APP_DIR/||" | sort | python3 -c "
import json, sys
files = [l.strip() for l in sys.stdin if l.strip()]
print(json.dumps(files, ensure_ascii=False, indent=2))
" > "$tmp"

  if [ ! -f "$INDICE_MP3" ] || ! cmp -s "$tmp" "$INDICE_MP3"; then
    mv "$tmp" "$INDICE_MP3"
    log "mp3_index.json actualizado ($(python3 -c "import json; print(len(json.load(open('$INDICE_MP3'))))") ficheiros)"
  else
    rm -f "$tmp"
  fi
}

log "auto_fusao.sh iniciado (PID $$) — a monitorizar $FICHEIRO_ADICIONAR (skip), $FICHEIRO_PATCH (upsert) e a indexar .mp3 em $INDICE_MP3"

while true; do
  fundir_se_pronto "$FICHEIRO_ADICIONAR" "$ALVO_ADICIONAR" "skip"
  fundir_se_pronto "$FICHEIRO_PATCH" "catalogo_patch.json" "upsert"
  atualizar_indice_mp3
  sleep 2
done
