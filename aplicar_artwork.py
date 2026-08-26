#!/usr/bin/env python3
"""Aplica artwork do iTunes (mp3_index.json) a todas as faixas do catalogo.json que tenham entrada correspondente."""
import json
import shutil
from datetime import datetime

CATALOGO_PATH = "catalogo.json"
INDEX_PATH = "mp3_index.json"

def upgrade_artwork(url):
    if not url:
        return url
    return url.replace("100x100bb", "600x600bb")

def main():
    backup_path = f"catalogo_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    shutil.copy(CATALOGO_PATH, backup_path)
    print(f"✓ Backup criado: {backup_path}")

    with open(INDEX_PATH, "r", encoding="utf-8") as f:
        mp3_index = json.load(f)

    with open(CATALOGO_PATH, "r", encoding="utf-8") as f:
        catalogo = json.load(f)

    aplicadas = 0
    ignoradas = 0

    for faixa in catalogo:
        fid = faixa.get("id")
        entrada = mp3_index.get(fid)
        if not entrada or not entrada.get("artwork_url"):
            ignoradas += 1
            continue

        faixa["imagem"] = upgrade_artwork(entrada["artwork_url"])
        faixa["imagem_credito"] = "Capa iTunes (Apple Music)"
        faixa["imagem_fonte"] = "itunes_artwork"
        faixa["imagem_licenca_estado"] = "confirmar"
        aplicadas += 1

    with open(CATALOGO_PATH, "w", encoding="utf-8") as f:
        json.dump(catalogo, f, indent=2, ensure_ascii=False)

    print(f"\n✓ Artwork aplicada: {aplicadas} faixas")
    print(f"— Sem entrada em mp3_index.json (ignoradas): {ignoradas} faixas")
    print(f"\nBackup guardado em: {backup_path}")

if __name__ == "__main__":
    main()
