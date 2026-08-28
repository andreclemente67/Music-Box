#!/usr/bin/env python3
"""
Music Box 2.0 — Gerador de Faixas Multi-Fonte
Extrai previews de iTunes → Spotify → YouTube (fallback)
Corta em formato: Trecho A (0-12s) + Gap (12-20s) + Trecho B (20-30s)
"""

import os
import json
import subprocess
import requests
from datetime import datetime
from pathlib import Path

class GeradorFaixaV2:
    def __init__(self, catalogo_path="catalogo.json", output_dir="./"):
        self.catalogo_path = catalogo_path
        self.output_dir = Path(output_dir)
        self.catalogo = self._load_json(catalogo_path)
        self.mp3_index = {}
        self.faixas_geradas = 0
        self.faixas_falhadas = 0

    def _load_json(self, path):
        """Carrega ficheiro JSON (catalogo.json é uma lista; converte para dict por id)"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if isinstance(data, list):
                return {item['id']: item for item in data if 'id' in item}
            return data
        except Exception as e:
            print(f"❌ Erro ao abrir {path}: {e}")
            return {}

    def _colisao_case_insensitive(self, faixa_id):
        """Devolve outro id do catálogo que resultaria no mesmo nome de
        ficheiro num sistema de ficheiros case-insensitive (macOS/APFS
        por omissão) — sem esta verificação, dois ids que só diferem em
        maiúsculas/minúsculas (ex. "Abc_01" e "abc_01") sobrescrever-
        se-iam silenciosamente em disco: o segundo gerar_faixa() apagaria
        os trechos do primeiro sem erro nenhum, e o mp3_index.json
        ficaria com as duas entradas a apontar (incorrectamente) para o
        mesmo ficheiro físico. Devolve None se não houver colisão."""
        alvo = faixa_id.lower()
        for outro_id in self.catalogo:
            if outro_id != faixa_id and outro_id.lower() == alvo:
                return outro_id
        return None

    def gerar_faixa(self, faixa_id, verbose=True):
        """Gera trechos A e B para uma faixa"""
        faixa = self.catalogo.get(faixa_id)
        if not faixa:
            if verbose:
                print(f"❌ Faixa {faixa_id} não encontrada no catálogo")
            self.faixas_falhadas += 1
            return False

        colisao = self._colisao_case_insensitive(faixa_id)
        if colisao:
            if verbose:
                print(f"❌ Colisão case-insensitive: '{faixa_id}' e '{colisao}' gerariam o mesmo ficheiro num sistema de ficheiros case-insensitive (ex. macOS) — a abortar para não sobrescrever '{colisao}' silenciosamente.")
            self.faixas_falhadas += 1
            return False

        titulo = faixa.get('titulo', 'Unknown')
        artista = ', '.join(faixa.get('artista', ['Unknown']))

        if verbose:
            print(f"\n📀 Gerando: {titulo} — {artista}")

        preview_data = None

        if verbose:
            print("   → Tentando iTunes...", end=" ", flush=True)
        preview_data = self._buscar_itunes(titulo, artista)
        if preview_data:
            if verbose:
                print("✓")
        else:
            if verbose:
                print("✗")
            if verbose:
                print("   → Tentando Spotify...", end=" ", flush=True)
            preview_data = self._buscar_spotify(titulo, artista)
            if preview_data:
                if verbose:
                    print("✓")
            else:
                if verbose:
                    print("✗")
                if verbose:
                    print("   → Tentando YouTube...", end=" ", flush=True)
                preview_data = self._buscar_youtube(titulo, artista)
                if preview_data:
                    if verbose:
                        print("✓")
                else:
                    if verbose:
                        print("✗")

        if not preview_data:
            if verbose:
                print(f"   ❌ Nenhuma fonte disponível")
            self.faixas_falhadas += 1
            return False

        fonte = preview_data.get('fonte')
        preview_url = preview_data.get('url')
        artwork_url = preview_data.get('artwork')

        if verbose:
            print(f"   ✓ Fonte: {fonte}")

        preview_file = f"/tmp/{faixa_id}_preview.mp3"
        if not self._download_audio(preview_url, preview_file, verbose):
            self.faixas_falhadas += 1
            return False

        duracao = self._get_duration(preview_file)
        if duracao < 29:
            if verbose:
                print(f"   ❌ Preview muito curto ({duracao:.1f}s, precisamos ≥29s)")
            os.remove(preview_file)
            self.faixas_falhadas += 1
            return False

        if verbose:
            print(f"   ✓ Duração: {duracao:.1f}s")

        trecho_a = self.output_dir / f"{faixa_id}_a.mp3"
        trecho_b = self.output_dir / f"{faixa_id}_b.mp3"

        if not self._cortar_audio(preview_file, str(trecho_a), start=0, duration=12, verbose=verbose):
            self.faixas_falhadas += 1
            return False
        if not self._cortar_audio(preview_file, str(trecho_b), start=20, duration=10, verbose=verbose):
            self.faixas_falhadas += 1
            return False

        try:
            os.remove(preview_file)
        except:
            pass

        if verbose:
            print(f"   ✓ Trechos cortados (A: 0-12s, B: 20-30s)")

        self.mp3_index[faixa_id] = {
            "id": faixa_id,
            "titulo": titulo,
            "artista": artista,
            "fonte": fonte,
            "duracao_preview": round(duracao, 1),
            "data_geracao": datetime.now().isoformat(),
            "trecho_a": str(trecho_a.name),
            "trecho_b": str(trecho_b.name),
            "artwork_url": artwork_url
        }

        self.faixas_geradas += 1
        return True

    def _buscar_itunes(self, titulo, artista):
        """Buscar preview em iTunes"""
        try:
            url = "https://itunes.apple.com/search"
            params = {
                "term": f"{titulo} {artista}",
                "media": "music",
                "entity": "song",
                "limit": 5,
                "country": "PT"
            }
            resp = requests.get(url, params=params, timeout=5)
            data = resp.json()

            if data.get('results'):
                for result in data['results']:
                    preview = result.get('previewUrl')
                    artwork = result.get('artworkUrl100')
                    if preview:
                        return {
                            'fonte': 'itunes',
                            'url': preview,
                            'artwork': artwork
                        }
        except Exception as e:
            pass

        return None

    def _buscar_spotify(self, titulo, artista):
        """Buscar preview em Spotify"""
        try:
            pass
        except:
            pass

        return None

    def _buscar_youtube(self, titulo, artista):
        """Fallback: buscar em YouTube com yt-dlp"""
        try:
            query = f"{titulo} {artista} official"
            pass
        except:
            pass

        return None

    def _download_audio(self, url, output_path, verbose=False):
        """Download do ficheiro de áudio com ffmpeg"""
        try:
            cmd = [
                "ffmpeg", "-i", url,
                "-q:a", "0",
                "-y",
                output_path
            ]
            result = subprocess.run(cmd, capture_output=True, timeout=60)
            if result.returncode == 0:
                return True
            else:
                if verbose:
                    print(f"   ❌ Erro ffmpeg: {result.stderr.decode()[:100]}")
                return False
        except subprocess.TimeoutExpired:
            if verbose:
                print(f"   ❌ Timeout ao descarregar")
            return False
        except Exception as e:
            if verbose:
                print(f"   ❌ Erro: {e}")
            return False

    def _cortar_audio(self, input_file, output_file, start, duration, verbose=False):
        """Cortar áudio com ffmpeg"""
        try:
            cmd = [
                "ffmpeg", "-i", input_file,
                "-ss", str(start),
                "-t", str(duration),
                "-c", "copy",
                "-y",
                output_file
            ]
            result = subprocess.run(cmd, capture_output=True, timeout=30)
            if result.returncode == 0:
                return True
            else:
                if verbose:
                    print(f"   ❌ Erro ao cortar: {result.stderr.decode()[:100]}")
                return False
        except Exception as e:
            if verbose:
                print(f"   ❌ Erro: {e}")
            return False

    def _get_duration(self, file_path):
        """Obter duração do ficheiro em segundos"""
        try:
            cmd = [
                "ffprobe", "-v", "error",
                "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1",
                file_path
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                return float(result.stdout.strip())
        except:
            pass

        return 0

    def gerar_todas(self, limite=None):
        """Gerar trechos para todas as faixas do catálogo"""
        faixas = list(self.catalogo.keys())
        if limite:
            faixas = faixas[:limite]

        print(f"\n🎵 Gerando {len(faixas)} faixas...")
        print("=" * 60)

        for i, faixa_id in enumerate(faixas, 1):
            print(f"\n[{i}/{len(faixas)}]", end=" ")
            self.gerar_faixa(faixa_id, verbose=True)

        print("\n" + "=" * 60)
        print(f"✓ Geradas: {self.faixas_geradas}")
        print(f"✗ Falhadas: {self.faixas_falhadas}")

    def salvar_index(self, output_path="mp3_index.json"):
        """Salvar índice de faixas geradas"""
        output_path = self.output_dir / output_path
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.mp3_index, f, indent=2, ensure_ascii=False)
        print(f"\n✓ Índice salvo: {output_path}")
        print(f"  ({len(self.mp3_index)} faixas registadas)")

if __name__ == "__main__":
    import sys

    print("Music Box 2.0 — Gerador de Faixas")
    print("=" * 60)

    gerador = GeradorFaixaV2()

    if len(sys.argv) > 1:
        faixa_id = sys.argv[1]
        print(f"\nGerando faixa: {faixa_id}")
        gerador.gerar_faixa(faixa_id)
    else:
        print("\n⚠️  Modo teste: gerando 5 primeiras faixas")
        print("   (para gerar todas, chamar com argumento: python3 gerar_faixa_v2.py --all)")
        gerador.gerar_todas(limite=5)

    gerador.salvar_index()
    print("\n✓ Concluído!")
