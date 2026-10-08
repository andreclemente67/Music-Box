#!/usr/bin/env python3
"""Funde um ficheiro de faixas (catalogo_adicionar.json ou catalogo_patch.json)
em catalogo.json — usado por auto_fusao.sh.

Uso: _fundir_catalogo.py <origem.json> <catalogo.json> <pasta_backups> [modo]

modo (opcional, default "skip"):
  skip   — nunca sobrescreve um id já existente em catalogo.json (salta-o e
           avisa em stderr). Usado para catalogo_adicionar.json — faixas
           novas da "Adicionar Faixa"; um id já existente aí é sinal de
           conflito, não deve apagar dados curados.
  upsert — se o id já existir em catalogo.json, FUNDE essa entrada com a
           versão nova campo a campo (deep merge: os campos presentes no
           patch substituem, os campos ausentes do patch mantêm-se tal
           como estavam) — senão adiciona a entrada nova por completo.
           Usado para catalogo_patch.json — esse ficheiro existe
           precisamente para gravar EDIÇÕES a faixas já existentes (ex.:
           trecho_a.inicio/fim via "Definir início", `imagem` via pesquisa
           Wikimedia/URL manual), por isso "skip" descartaria essas
           edições silenciosamente. Antes, o upsert substituía a entrada
           INTEIRA — um patch gerado a partir de uma cópia antiga do
           catálogo podia apagar silenciosamente campos escritos
           directamente em catalogo.json depois dessa cópia (ex.:
           `fonte_audio`, 2026-10-08) sem o patch saber que existiam;
           corrigido nesta versão (2026-10-08) para fusão campo a campo.
           Sempre que o patch altera `fonte_audio`, `trecho_a` ou
           `trecho_b` de uma entrada já existente, avisa em stderr (não
           bloqueia — só torna a alteração visível).

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

CAMPOS_SENSIVEIS = ("fonte_audio", "trecho_a", "trecho_b")


def fundir_campos(actual, novo):
    """Deep merge: campos presentes em `novo` substituem os de `actual`
    (recursivamente, se ambos forem dict); campos ausentes em `novo`
    mantêm-se de `actual`. Devolve um dict novo, não modifica os
    argumentos."""
    resultado = dict(actual)
    for chave, valor in novo.items():
        if isinstance(valor, dict) and isinstance(resultado.get(chave), dict):
            resultado[chave] = fundir_campos(resultado[chave], valor)
        else:
            resultado[chave] = valor
    return resultado


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
    avisos_campos_sensiveis = []

    for entrada in novas:
        cid = entrada.get("id") if isinstance(entrada, dict) else None
        if not cid:
            saltadas.append("(entrada sem id)")
            continue
        if cid in indice_por_id:
            if modo == "upsert":
                i = indice_por_id[cid]
                actual = catalogo[i]
                for campo in CAMPOS_SENSIVEIS:
                    if campo in entrada and entrada[campo] != actual.get(campo):
                        avisos_campos_sensiveis.append(
                            f"{cid}.{campo}: {actual.get(campo)!r} -> {entrada[campo]!r}")
                catalogo[i] = fundir_campos(actual, entrada)
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
        print(f"ids substituídos (upsert, fusão campo a campo): {', '.join(substituidas)}", file=sys.stderr)
    for aviso in avisos_campos_sensiveis:
        print(f"AVISO campo sensível alterado pelo patch — {aviso}", file=sys.stderr)
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
