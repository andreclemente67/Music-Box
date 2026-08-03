#!/bin/bash
NOME="$1"
if [ -z "$NOME" ]; then echo "Uso: atualizar.sh nome_do_ficheiro"; exit 1; fi
BASE="${NOME%.*}"
EXT="${NOME##*.}"
FICHEIRO=$(find ~/Downloads -name "${BASE}*.${EXT}" -o -name "${BASE}*.txt" 2>/dev/null | sort -V | tail -1)
if [ -z "$FICHEIRO" ]; then echo "Nao encontrei $NOME em Downloads."; exit 1; fi
DESTINO="$NOME"
if [ "$EXT" = "txt" ]; then
  if head -1 "$FICHEIRO" | grep -q "python"; then
    DESTINO="${BASE}.py"
  else
    DESTINO="${BASE}.sh"
  fi
fi
cp "$FICHEIRO" ~/MusicBox/app/"$DESTINO"
find ~/Downloads -name "${BASE}*.${EXT}" -delete 2>/dev/null
find ~/Downloads -name "${BASE}*.txt" -delete 2>/dev/null
case "$DESTINO" in
  *.sh|*.py|*.command) chmod +x ~/MusicBox/app/"$DESTINO" ;;
esac
echo "✓ $DESTINO instalado."
