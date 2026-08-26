#!/usr/bin/env python3
"""Funde um ficheiro de faixas (catalogo_adicionar.json ou catalogo_patch.json)
em catalogo.json — usado por auto_fusao.sh.

Uso: _fundir_catalogo.py <origem.json> <catalogo.json> <pasta_backups> [modo]

modo (opcional, default "skip"):
  skip   — nunca sobrescreve um id já existente em catalogo.json (salta-o e
           avisa em stderr). Usado para catalogo_adicionar.json — faixas
           novas da "Adicionar Faixa"; um id já existente aí é sinal de
           conflito, não deve apagar dados curados.
  upsert — se o id já existir em catalogo.json, SUBSTITUI essa entrada pela
           versão nova; senão adiciona. Usado para catalogo_patch.json —
           esse ficheiro existe precisamente para gravar EDIÇÕES a faixas já
           existentes (ex.: trecho_a.inicio/fim via "Definir início",
           `imagem` via pesquisa Wikimedia/URL manual), por isso "skip"
           descartaria essas edições silenciosamente.

Faz backup timestamped de catalogo.json antes de o reescrever, e só o
reescreve se houver pelo menos uma alteração. Imprime SÓ o número de faixas
fundidas (novas + substituídas) em stdout (para o .sh capturar); avisos vão
para stderr. Sai com código != 0 se a origem ou o catálogo não forem JSON
válido — nesse caso nada é escrito nem apagado.
"""
import datetime
import json
import shutil
import sys


def main():
    if len(sys.argv) not in (4, 5):
        print("uso: _fundir_catalogo.py <origem.json> <catalogo.json> <pasta_backups> [skip|upsert]", file=sys.stderr)
        return 1

    origem_path, catalogo_path, backup_dir = sys.argv[1], sys.argv[2], sys.argv[3]
    modo = sys.argv[4] if len(sys.argv) == 5 else "skip"
    if modo not in ("skip", "upsert"):
        print(f"modo desconhecido: {modo!r} (esperado 'skip' ou 'upsert')", file=sys.stderr)
        return 1

    with open(origem_path, encoding="utf-8") as f:
        novas = json.load(f)
    if isinstance(novas, dict):
        novas = [novas]
    if not isinstance(novas, list):
        print(f"{origem_path}: esperava uma lista (ou objeto único) de faixas", file=sys.stderr)
        return 1

    with open(catalogo_path, encoding="utf-8") as f:
        catalogo = json.load(f)
    if not isinstance(catalogo, list):
        print(f"{catalogo_path}: não é uma lista — não vou tocar-lhe", file=sys.stderr)
        return 1

    indice_por_id = {t.get("id"): i for i, t in enumerate(catalogo)}
    adicionadas = []
    substituidas = []
    saltadas = []

    for entrada in novas:
        cid = entrada.get("id") if isinstance(entrada, dict) else None
        if not cid:
            saltadas.append("(entrada sem id)")
            continue
        if cid in indice_por_id:
            if modo == "upsert":
                catalogo[indice_por_id[cid]] = entrada
                substituidas.append(cid)
            else:
                saltadas.append(cid)
            continue
        catalogo.append(entrada)
        indice_por_id[cid] = len(catalogo) - 1
        adicionadas.append(cid)

    fundidas = adicionadas + substituidas
    if fundidas:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        shutil.copy2(catalogo_path, f"{backup_dir}/catalogo_{timestamp}.json.bak")
        with open(catalogo_path, "w", encoding="utf-8") as f:
            json.dump(catalogo, f, ensure_ascii=False, indent=2)
            f.write("\n")

    if substituidas:
        print(f"ids substituídos (upsert): {', '.join(substituidas)}", file=sys.stderr)
    if saltadas:
        print(f"ids saltados (já existiam ou sem id): {', '.join(saltadas)}", file=sys.stderr)

    print(len(fundidas))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (json.JSONDecodeError, OSError) as e:
        print(f"erro: {e}", file=sys.stderr)
        sys.exit(1)
