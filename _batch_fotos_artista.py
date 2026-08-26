#!/usr/bin/env python3
"""Corre a cascata de imagem de artista (GET /buscar-imagem-artista) para
todas as faixas de catalogo.json com imagem_licenca_estado != 'livre'.

Equivalente ao botão "Auto-preencher fotos de artista (cascata)" do
Studio, mas correndo aqui porque não há browser disponível para clicar.
NÃO escreve em catalogo_patch.json (o auto_fusao.sh fundia-o de imediato,
sem revisão) — escreve num ficheiro separado, catalogo_patch_proposto.json,
para revisão manual antes de decidir aplicar.
"""
import json
import time
import urllib.parse
import urllib.request

CATALOGO_PATH = "catalogo.json"
SAIDA_PATH = "catalogo_patch_proposto.json"
ENDPOINT = "http://localhost:8002/buscar-imagem-artista"
PAUSA_SEGUNDOS = 0.3


def artista_texto(t):
    a = t.get("artista")
    if isinstance(a, list):
        return " / ".join(a)
    return a or ""


def buscar_imagem(artista):
    url = f"{ENDPOINT}?{urllib.parse.urlencode({'artista': artista})}"
    try:
        with urllib.request.urlopen(url, timeout=20) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        return {"ok": False, "erro": str(e)}


def main():
    catalogo = json.load(open(CATALOGO_PATH, encoding="utf-8"))
    elegiveis = [t for t in catalogo if t.get("id") and t.get("imagem_licenca_estado") != "livre"]

    print(f"Total no catálogo: {len(catalogo)} | Elegíveis: {len(elegiveis)}")
    print("=" * 60)

    melhoradas = []
    sem_resultado = []
    propostas = []

    for i, t in enumerate(elegiveis, 1):
        artista = artista_texto(t)
        resultado = buscar_imagem(artista)
        if resultado.get("ok"):
            novo = dict(t)
            novo["imagem"] = resultado["imagem"]
            novo["imagem_fonte"] = resultado["imagem_fonte"]
            novo["imagem_credito"] = resultado["imagem_credito"]
            novo["imagem_url_origem"] = resultado["imagem_url_origem"]
            novo["imagem_data_captura"] = resultado["imagem_data_captura"]
            novo["imagem_licenca_estado"] = resultado["imagem_licenca_estado"]
            propostas.append(novo)
            melhoradas.append((t["id"], artista, resultado["imagem_fonte"]))
            print(f"[{i}/{len(elegiveis)}] OK  {t['id']:40s} {artista:30s} via {resultado['imagem_fonte']}")
        else:
            sem_resultado.append((t["id"], artista))
            print(f"[{i}/{len(elegiveis)}] --  {t['id']:40s} {artista:30s} sem resultado")

        time.sleep(PAUSA_SEGUNDOS)

    with open(SAIDA_PATH, "w", encoding="utf-8") as f:
        json.dump(propostas, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print("=" * 60)
    print(f"✓ Melhoradas: {len(melhoradas)}")
    print(f"✗ Sem resultado: {len(sem_resultado)}")
    print(f"\nProposta guardada em: {SAIDA_PATH} ({len(propostas)} entradas) — NÃO aplicada a catalogo.json")

    print("\n--- Melhoradas (id | artista | fonte) ---")
    for id_, artista, fonte in melhoradas:
        print(f"{id_} | {artista} | {fonte}")

    print("\n--- Sem resultado (id | artista) ---")
    for id_, artista in sem_resultado:
        print(f"{id_} | {artista}")


if __name__ == "__main__":
    main()
