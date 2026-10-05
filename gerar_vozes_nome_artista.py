#!/usr/bin/env python3
"""
Gerador de voz do nome do artista (apresentador) — voz/nome_<id>.wav.

Duas vozes possíveis por faixa:
- Alex, rate 205, via `say` nativo do macOS — voz por omissão (ver
  DECISIONS.md, "2026-10-04 — Nova arquitectura da voz pós-acerto").
- Uma voz edge-tts dedicada por língua (Duarte/Antonio/francês/espanhol/
  italiano/alemão/japonês/russo/grego, ver voz/pronuncia.json) — para
  artistas de playlists PT/BR, ou para excepções manuais fora delas que
  o Alex (inglês) leria mal.

voz/pronuncia.json define as excepções manuais e as vozes por língua
(`artistas`, por nome de artista → {voz, texto opcional}). Prioridade
de atribuição (ver af_resolverVoz()):
  1. Excepção manual em pronuncia.json (por nome de artista).
  2. Prefixo do código da playlist onde a faixa aparece: STD.PT./
     RET.PT. -> Duarte (pt-PT-DuarteNeural); STD.BR. -> Antonio
     (pt-BR-AntonioNeural).
  3. Alex r205 (default).
"texto" (opcional, por artista) é a grafia realmente enviada à voz
(ex: grafia nativa para japonês/russo/grego) — nunca altera o nome
mostrado no jogo (lido sempre de catalogo.json).

Dependências externas (têm de estar no PATH): `say` (TTS nativo do
macOS) e `ffmpeg`. edge-tts corre num venv dedicado (EDGE_TTS abaixo) —
precisa de LIGAÇÃO À INTERNET em cada geração.

voz/nome_index.json guarda {id: sha1(texto+voz)} — por omissão só
regenera uma faixa se o texto OU a voz atribuída mudou desde a última
vez, ou o ficheiro ainda não existe. --todos força tudo (com backup
prévio); --id gera só uma faixa.

Uso:
  python3 gerar_vozes_nome_artista.py            # só os que faltam/mudaram
  python3 gerar_vozes_nome_artista.py --todos    # regenera tudo, com backup
  python3 gerar_vozes_nome_artista.py --id dec50_01   # só uma faixa
  python3 gerar_vozes_nome_artista.py --mosaicos # voz/mosaico_<codigo>.wav,
                                                  # a partir do campo `pessoa`
                                                  # de cada playlist (mesmas
                                                  # regras de voz, índice
                                                  # próprio em mosaico_index.json)
"""
import argparse
import datetime
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
CATALOGO = RAIZ / 'catalogo.json'
PLAYLISTS = RAIZ / 'playlists.json'
VOZ_DIR = RAIZ / 'voz'
PRONUNCIA_PATH = VOZ_DIR / 'pronuncia.json'
INDEX_PATH = VOZ_DIR / 'nome_index.json'
EDGE_TTS = Path.home() / '.venvs' / 'musicbox-tts' / 'bin' / 'edge-tts'
VOZ_ALEX = 'Alex'
RATE_ALEX = 205
SAMPLE_RATE = 44100

# Prefixos de código de playlist -> voz edge-tts (ver pronuncia.json para
# as excepções manuais, que têm prioridade sobre isto).
PREFIXOS_VOZ = [
    ('STD.PT.', 'pt-PT-DuarteNeural'),
    ('RET.PT.', 'pt-PT-DuarteNeural'),
    ('STD.BR.', 'pt-BR-AntonioNeural'),
]

# Mesmo filtro usado nos 302 ficheiros originais (2026-10-04): corta
# silêncio residual nas duas pontas (silenceremove + areverse duas vezes,
# truque padrão do ffmpeg para aparar início E fim) e normaliza loudness
# para um nível consistente entre vozes/faixas.
FILTRO_TRIM_NORM = (
    "silenceremove=start_periods=1:start_threshold=-50dB:start_silence=0.05:detection=peak,"
    "areverse,"
    "silenceremove=start_periods=1:start_threshold=-50dB:start_silence=0.05:detection=peak,"
    "areverse,"
    "loudnorm=I=-16:TP=-1.5:LRA=11"
)


def carregar_catalogo():
    with open(CATALOGO, encoding='utf-8') as f:
        return json.load(f)


def carregar_playlists():
    with open(PLAYLISTS, encoding='utf-8') as f:
        return json.load(f)


def carregar_pronuncia():
    with open(PRONUNCIA_PATH, encoding='utf-8') as f:
        return json.load(f).get('artistas', {})


def carregar_index():
    if INDEX_PATH.exists():
        with open(INDEX_PATH, encoding='utf-8') as f:
            return json.load(f)
    return {}


def gravar_index(index):
    with open(INDEX_PATH, 'w', encoding='utf-8') as f:
        json.dump(index, f, ensure_ascii=False, indent=2, sort_keys=True)
        f.write('\n')


def sha1_texto(texto):
    return hashlib.sha1(texto.encode('utf-8')).hexdigest()


def nomes_artista(entrada_artista):
    # catalogo.json guarda 'artista' como string ou lista (colaborações,
    # ex. ["Daft Punk", "Pharrell Williams"]).
    if isinstance(entrada_artista, list):
        return entrada_artista
    return [entrada_artista] if entrada_artista else []


def nome_para_texto(entrada_artista):
    return ' & '.join(nomes_artista(entrada_artista))


def construir_id_para_prefixos(playlists):
    """id de catalogo.json -> set de prefixos de código de playlist (dos
    3 primeiros segmentos, ex. 'STD.PT.') onde aparece (faixa ou mosaico)."""
    mapa = {}
    for chave, pl in playlists.items():
        partes = chave.split('.')
        prefixo = '.'.join(partes[:2]) + '.' if len(partes) >= 2 else chave
        for tid in (pl.get('musicas') or []):
            mapa.setdefault(tid, set()).add(prefixo)
        mosaico = pl.get('mosaico')
        if isinstance(mosaico, dict) and mosaico.get('id'):
            mapa.setdefault(mosaico['id'], set()).add(prefixo)
    return mapa


def af_resolverVoz(id_para_prefixos, tid, entrada_artista, pronuncia):
    """Devolve (voz, texto_falado) para a faixa `tid`. Prioridade:
    excepção manual (por qualquer nome na lista de artistas) > prefixo
    da playlist > Alex (default)."""
    nomes = nomes_artista(entrada_artista)
    for nome in nomes:
        excepcao = pronuncia.get(nome)
        if excepcao:
            return excepcao['voz'], excepcao.get('texto', nome_para_texto(entrada_artista))
    prefixos = id_para_prefixos.get(tid, set())
    for prefixo, voz in PREFIXOS_VOZ:
        if prefixo in prefixos:
            return voz, nome_para_texto(entrada_artista)
    return VOZ_ALEX, nome_para_texto(entrada_artista)


def gerar_um_say(texto, destino):
    with tempfile.TemporaryDirectory() as tmp:
        aiff = Path(tmp) / 'voz.aiff'
        subprocess.run(
            ['say', '-v', VOZ_ALEX, '-r', str(RATE_ALEX), texto, '-o', str(aiff)],
            check=True, capture_output=True,
        )
        subprocess.run(
            ['ffmpeg', '-y', '-i', str(aiff), '-af', FILTRO_TRIM_NORM,
             '-ar', str(SAMPLE_RATE), '-ac', '1', str(destino)],
            check=True, capture_output=True,
        )


def gerar_um_edge(texto, voz, destino):
    with tempfile.TemporaryDirectory() as tmp:
        mp3 = Path(tmp) / 'voz.mp3'
        r = subprocess.run(
            [str(EDGE_TTS), '--voice', voz, '--text', texto, '--write-media', str(mp3)],
            capture_output=True, text=True, timeout=60,
        )
        if r.returncode != 0 or not mp3.exists():
            raise RuntimeError(
                "edge-tts falhou — provavelmente sem ligação à internet. "
                f"Detalhe: {r.stderr.strip()[-300:]}"
            )
        subprocess.run(
            ['ffmpeg', '-y', '-i', str(mp3), '-af', FILTRO_TRIM_NORM,
             '-ar', str(SAMPLE_RATE), '-ac', '1', str(destino)],
            check=True, capture_output=True,
        )


def gerar_um(texto, voz, destino):
    if voz == VOZ_ALEX:
        gerar_um_say(texto, destino)
    else:
        gerar_um_edge(texto, voz, destino)


MOSAICO_INDEX_PATH = VOZ_DIR / 'mosaico_index.json'


def af_resolverVozMosaico(chave, pessoa, pronuncia):
    """Mesma prioridade de af_resolverVoz(), mas para o `pessoa` do
    Mosaico — o prefixo relevante é o da própria playlist (chave), não
    de um id de catalogo.json cruzado."""
    excepcao = pronuncia.get(pessoa)
    if excepcao:
        return excepcao['voz'], excepcao.get('texto', pessoa)
    for prefixo, voz in PREFIXOS_VOZ:
        if chave.startswith(prefixo):
            return voz, pessoa
    return VOZ_ALEX, pessoa


def gerar_mosaicos():
    playlists = carregar_playlists()
    pronuncia = carregar_pronuncia()
    index = json.load(open(MOSAICO_INDEX_PATH, encoding='utf-8')) if MOSAICO_INDEX_PATH.exists() else {}
    VOZ_DIR.mkdir(exist_ok=True)

    resolucao = {}
    vazios = []
    for chave, pl in playlists.items():
        mosaico = pl.get('mosaico')
        if not isinstance(mosaico, dict):
            continue
        pessoa = (mosaico.get('pessoa') or '').strip()
        if not pessoa:
            vazios.append((chave, pl.get('nome')))
            continue
        voz, texto_falado = af_resolverVozMosaico(chave, pessoa, pronuncia)
        resolucao[chave] = (texto_falado, voz)

    if vazios:
        print(f"{len(vazios)} mosaico(s) sem 'pessoa' preenchida — não gerados:")
        for chave, nome in vazios:
            print(f"  {chave} ({nome})")

    alvo = []
    for chave, (texto_falado, voz) in resolucao.items():
        destino = VOZ_DIR / f'mosaico_{chave}.wav'
        if not destino.exists():
            alvo.append(chave)
            continue
        if chave not in index:
            if voz != VOZ_ALEX:
                alvo.append(chave)
            continue
        if index.get(chave) != sha1_texto(texto_falado + '|' + voz):
            alvo.append(chave)
    alvo.sort()

    if not alvo:
        print("Nada a gerar — todas as vozes de mosaico já estão actualizadas.")
        return

    existentes = [VOZ_DIR / f'mosaico_{chave}.wav' for chave in alvo if (VOZ_DIR / f'mosaico_{chave}.wav').exists()]
    if existentes:
        data = datetime.date.today().isoformat()
        backup_dir = RAIZ / f'_backup_voz_{data}_mosaico'
        backup_dir.mkdir(exist_ok=True)
        for f in existentes:
            shutil.copy2(f, backup_dir / f.name)
        print(f"Backup de {len(existentes)} ficheiro(s) em {backup_dir}/")

    print(f"A gerar {len(alvo)} voz(es) de mosaico…")
    falhas = []
    for chave in alvo:
        texto_falado, voz = resolucao[chave]
        destino = VOZ_DIR / f'mosaico_{chave}.wav'
        try:
            gerar_um(texto_falado, voz, destino)
            index[chave] = sha1_texto(texto_falado + '|' + voz)
            with open(MOSAICO_INDEX_PATH, 'w', encoding='utf-8') as f:
                json.dump(index, f, ensure_ascii=False, indent=2, sort_keys=True)
                f.write('\n')
            print(f"  ✓ {chave} — \"{texto_falado}\" (voz={voz})")
        except (subprocess.CalledProcessError, RuntimeError) as e:
            detalhe = e.stderr.decode('utf-8', 'ignore')[-300:] if isinstance(e, subprocess.CalledProcessError) and e.stderr else str(e)
            print(f"  ✗ {chave}: {detalhe}")
            falhas.append(chave)

    print(f"\nConcluído: {len(alvo) - len(falhas)}/{len(alvo)} gerado(s).")
    if falhas:
        sys.exit(1)


def main():
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--todos', action='store_true',
                     help='Regenera todas as vozes (com backup prévio)')
    ap.add_argument('--id', help='Gera só uma faixa (id do catalogo.json)')
    ap.add_argument('--mosaicos', action='store_true',
                     help='Gera voz/mosaico_<codigo>.wav a partir do campo pessoa de cada playlist')
    args = ap.parse_args()

    for exe in ('say', 'ffmpeg'):
        if shutil.which(exe) is None:
            sys.exit(f"Erro: '{exe}' não encontrado no PATH.")

    if args.mosaicos:
        gerar_mosaicos()
        return

    catalogo = carregar_catalogo()
    por_id = {t['id']: t for t in catalogo}
    playlists = carregar_playlists()
    pronuncia = carregar_pronuncia()
    id_para_prefixos = construir_id_para_prefixos(playlists)
    index = carregar_index()
    VOZ_DIR.mkdir(exist_ok=True)

    # (texto, voz) final por id — já com a resolução de prioridade feita;
    # é isto que vai para o sintetizador e para o hash do índice.
    resolucao = {}
    for tid, t in por_id.items():
        texto_cat = t.get('artista')
        if not texto_cat:
            continue
        voz, texto_falado = af_resolverVoz(id_para_prefixos, tid, texto_cat, pronuncia)
        resolucao[tid] = (texto_falado, voz)

    if args.id:
        if args.id not in por_id:
            sys.exit(f"Erro: id '{args.id}' não existe em catalogo.json")
        alvo_ids = [args.id]
    elif args.todos:
        alvo_ids = sorted(resolucao.keys())
    else:
        alvo_ids = []
        for tid, (texto_falado, voz) in resolucao.items():
            destino = VOZ_DIR / f'nome_{tid}.wav'
            if not destino.exists():
                alvo_ids.append(tid)
                continue
            if tid not in index:
                # Nunca foi rastreado pelo índice (1ª vez que este id passa
                # por aqui desde que o índice existe) — só regenera se a
                # voz atribuída não for a Alex (default histórico, sem
                # índice, sem necessidade de regenerar o que já existe).
                if voz != VOZ_ALEX:
                    alvo_ids.append(tid)
                continue
            chave_hash = sha1_texto(texto_falado + '|' + voz)
            if index.get(tid) != chave_hash:
                alvo_ids.append(tid)
        alvo_ids.sort()

    if not alvo_ids:
        print("Nada a gerar — todas as vozes já estão actualizadas (usa --todos para regenerar).")
        return

    # Backup prévio dos ficheiros que vão ser sobrescritos (sempre, não só
    # em --todos) — nunca apaga sem copiar primeiro.
    existentes = [VOZ_DIR / f'nome_{tid}.wav' for tid in alvo_ids if (VOZ_DIR / f'nome_{tid}.wav').exists()]
    if existentes:
        data = datetime.date.today().isoformat()
        backup_dir = RAIZ / f'_backup_voz_{data}'
        backup_dir.mkdir(exist_ok=True)
        for f in existentes:
            shutil.copy2(f, backup_dir / f.name)
        print(f"Backup de {len(existentes)} ficheiro(s) em {backup_dir}/")

    print(f"A gerar {len(alvo_ids)} ficheiro(s) de voz…")
    falhas = []
    for tid in alvo_ids:
        if tid not in resolucao:
            print(f"  ✗ {tid}: sem campo 'artista' no catalogo.json")
            falhas.append(tid)
            continue
        texto_falado, voz = resolucao[tid]
        destino = VOZ_DIR / f'nome_{tid}.wav'
        try:
            gerar_um(texto_falado, voz, destino)
            index[tid] = sha1_texto(texto_falado + '|' + voz)
            gravar_index(index)  # grava já a cada sucesso — não perde progresso se falhar a meio
            print(f"  ✓ {tid} — \"{texto_falado}\" (voz={voz})")
        except (subprocess.CalledProcessError, RuntimeError) as e:
            detalhe = e.stderr.decode('utf-8', 'ignore')[-300:] if isinstance(e, subprocess.CalledProcessError) and e.stderr else str(e)
            print(f"  ✗ {tid}: {detalhe}")
            falhas.append(tid)

    print(f"\nConcluído: {len(alvo_ids) - len(falhas)}/{len(alvo_ids)} gerado(s).")
    if falhas:
        print(f"Falhas ({len(falhas)}): {falhas}")
        sys.exit(1)


if __name__ == '__main__':
    main()
