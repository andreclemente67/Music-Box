#!/usr/bin/env python3
"""
Auditoria total ao catálogo e às playlists — só relatório, não altera
nada em catalogo.json/playlists.json. Escreve docs/auditoria_catalogo_
<data>.md directamente (output no terminal é só um resumo curto).

Por faixa (catalogo.json): Trecho A/B existem, duração dentro do
esperado, não estão em silêncio; imagem existe e abre (HTTP, se for
URL remota); estado da licença da imagem; voz do nome existe
(voz/nome_<id>.wav).

Por playlist (playlists.json): todas as posições preenchidas, mosaico
com pessoa e imagem, descritivo e voz do descritivo, perguntas bónus
nas posições certas (Bíblia §3.6/§5.3 — Especiais Faixas 3/6, Décadas/
Estilos Faixa 4, só playlists tipo 'standard'), artista repetido
(banda conta como a própria banda — Bíblia §27.2, revisto 5 Out 2026).

Severidade: bloqueia o jogo (ficheiro de áudio em falta, posição vazia,
mosaico incompleto — numa playlist "pronta"/activa) > afecta o piloto
(imagem/voz em falta, licença a confirmar, bónus em falta, artista
repetido — numa playlist activa) > cosmético (o mesmo em playlists só
rascunho/sem uso, ou duração/silêncio fora do ideal mas reproduzível).

Uso: python3 _auditoria_catalogo.py
"""
import concurrent.futures
import datetime
import json
import subprocess
import time
import urllib.error
import urllib.request
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
DATA_HOJE = datetime.date.today().isoformat()
RELATORIO_PATH = RAIZ / 'docs' / f'auditoria_catalogo_{DATA_HOJE}.md'

FAMILIA_DECADAS = 'DÉCADAS'
FAMILIA_GENEROS = 'ESTILOS'
FAMILIA_ESPECIAIS = 'ESPECIAIS'
GENERO_FAMILIA = {
    'ROC': FAMILIA_GENEROS, 'POP': FAMILIA_GENEROS, 'MET': FAMILIA_GENEROS, 'AME': FAMILIA_GENEROS,
    'SYN': FAMILIA_GENEROS, 'DNC': FAMILIA_GENEROS, 'GTR': FAMILIA_GENEROS, 'BAT': FAMILIA_GENEROS,
    'JAZ': FAMILIA_GENEROS, 'BLU': FAMILIA_GENEROS, 'SOU': FAMILIA_GENEROS, 'HIP': FAMILIA_GENEROS,
    'CLA': FAMILIA_GENEROS, 'LAT': FAMILIA_GENEROS,
    'CIN': FAMILIA_ESPECIAIS, 'TV': FAMILIA_ESPECIAIS, 'GAM': FAMILIA_ESPECIAIS, 'NAT': FAMILIA_ESPECIAIS,
    'VOZ': FAMILIA_ESPECIAIS,
}
FAIXAS_COM_BONUS_ESPECIAIS = {3, 6}
FAIXA_BONUS_MUSICAL = 4


def familia_da_playlist(chave, pl):
    partes = chave.split('.')
    if len(partes) >= 4:
        tipo, geo, dec, genero = partes[0], partes[1], partes[2], partes[3]
        if tipo == 'RET':
            return FAMILIA_ESPECIAIS
        if geo == 'PT':
            if genero in ('BAT', 'GTR'):
                return FAMILIA_GENEROS
            return FAMILIA_ESPECIAIS
        if dec != 'ALL':
            return FAMILIA_DECADAS
        if genero == 'MIX' and geo == 'INT':
            return FAMILIA_ESPECIAIS
        return GENERO_FAMILIA.get(genero, FAMILIA_GENEROS)
    return FAMILIA_GENEROS


def faixa_tem_bonus(chave, pl, posicao):
    # Mesma regra usada para gerar os dados (musicbox_studio.html,
    # af_faixaTemBonus) — só playlists tipo 'standard' (retrato/
    # tributo/vídeo têm estrutura incompatível com "Faixa N").
    if pl.get('tipo') != 'standard':
        return False
    familia = familia_da_playlist(chave, pl)
    if familia == FAMILIA_ESPECIAIS:
        return posicao in FAIXAS_COM_BONUS_ESPECIAIS
    if familia in (FAMILIA_DECADAS, FAMILIA_GENEROS):
        return posicao == FAIXA_BONUS_MUSICAL
    return False


def playlist_ids(pl):
    if pl.get('tipo') == 'tributo':
        return [p.get('id') for p in (pl.get('posicoes') or [])]
    return list(pl.get('musicas') or [])


def af_playlist_estado(pl, by_id):
    ids = playlist_ids(pl)
    if pl.get('mosaico') and pl['mosaico'].get('id'):
        ids = ids + [pl['mosaico']['id']]
    if not ids:
        return 'rascunho'
    tudo_pronto = all(by_id.get(i) and by_id[i].get('estado') != 'rascunho' for i in ids if i)
    return 'pronta' if tudo_pronto else 'rascunho'


def artista_principal(c):
    a = c.get('artista')
    a = a[0] if isinstance(a, list) else a
    return (a or '').strip()


def identidade_artista(tid, by_id):
    c = by_id.get(tid)
    if not c:
        return None
    banda = (c.get('banda') or '').strip()
    if banda:
        return banda
    return artista_principal(c) or None


def artistas_repetidos(chave, pl, by_id):
    if pl.get('tipo') == 'tributo':
        return []
    vistos = {}
    for i, tid in enumerate(pl.get('musicas') or [], 1):
        nome = identidade_artista(tid, by_id)
        if not nome:
            continue
        chave_norm = nome.lower()
        vistos.setdefault(chave_norm, {'nome': nome, 'posicoes': []})
        vistos[chave_norm]['posicoes'].append(f'Faixa {i}')
    mosaico = pl.get('mosaico')
    if mosaico and mosaico.get('id'):
        nome = identidade_artista(mosaico['id'], by_id)
        if nome:
            chave_norm = nome.lower()
            vistos.setdefault(chave_norm, {'nome': nome, 'posicoes': []})
            vistos[chave_norm]['posicoes'].append('Mosaico')
    return [v for v in vistos.values() if len(v['posicoes']) > 1]


# ---------- checagens de áudio ----------

def ffprobe_duracao(caminho):
    try:
        r = subprocess.run(
            ['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
             '-of', 'default=noprint_wrappers=1:nokey=1', str(caminho)],
            capture_output=True, text=True, timeout=10,
        )
        return float(r.stdout.strip()) if r.returncode == 0 and r.stdout.strip() else None
    except Exception:
        return None


def ffmpeg_volume_medio(caminho):
    try:
        r = subprocess.run(
            ['ffmpeg', '-v', 'error', '-i', str(caminho), '-af', 'volumedetect', '-f', 'null', '-'],
            capture_output=True, text=True, timeout=15,
        )
        for linha in r.stderr.splitlines():
            if 'mean_volume' in linha:
                return float(linha.split(':')[1].strip().replace(' dB', ''))
    except Exception:
        pass
    return None


def verificar_trecho(caminho_rel, inicio, fim):
    """Devolve dict com existe/duracao/silencio/duracao_ok para um trecho.

    `inicio`/`fim` descrevem o intervalo dentro da faixa ORIGINAL de onde
    o excerto foi extraído (proveniência) — não são os limites internos
    do próprio ficheiro já exportado, por isso não servem para calcular
    uma duração "esperada" por subtracção (confirmado: dezenas de
    ficheiros com fim-inicio=12 têm, de forma consistente, ~15s reais —
    a margem de exportação é deliberada). Só um intervalo de sanidade
    (claramente demasiado curto ou demasiado longo para um trecho)."""
    caminho = RAIZ / caminho_rel if caminho_rel else None
    if not caminho or not caminho.is_file():
        return {'existe': False, 'duracao': None, 'silencio': None, 'duracao_ok': None}
    duracao = ffprobe_duracao(caminho)
    vol = ffmpeg_volume_medio(caminho)
    silencio = (vol is not None and vol < -45)
    duracao_ok = (3 <= duracao <= 40) if duracao is not None else None
    return {'existe': True, 'duracao': duracao, 'silencio': silencio, 'duracao_ok': duracao_ok}


def imagem_abre(url_ou_caminho):
    """True/False, ou None se não foi possível concluir (ex: 429 — rate
    limit do servidor remoto, não um ficheiro realmente partido)."""
    if not url_ou_caminho:
        return None
    if not (url_ou_caminho.startswith('http://') or url_ou_caminho.startswith('https://')):
        return (RAIZ / url_ou_caminho).is_file()
    for tentativa in range(3):
        try:
            req = urllib.request.Request(url_ou_caminho, method='HEAD', headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=8) as resp:
                return resp.status < 400
        except urllib.error.HTTPError as e:
            if e.code == 429:
                time.sleep(1.5 * (tentativa + 1))
                continue
            if e.code in (403, 405):  # HEAD bloqueado por este servidor — tenta GET
                try:
                    req = urllib.request.Request(url_ou_caminho, headers={'User-Agent': 'Mozilla/5.0'})
                    with urllib.request.urlopen(req, timeout=8) as resp:
                        return resp.status < 400
                except Exception:
                    return False
            return False
        except Exception:
            return False
    return None  # esgotou as tentativas, sempre 429 — inconclusivo, não "não abre"


def main():
    with open(RAIZ / 'catalogo.json', encoding='utf-8') as f:
        catalogo = json.load(f)
    with open(RAIZ / 'playlists.json', encoding='utf-8') as f:
        playlists = json.load(f)
    by_id = {c['id']: c for c in catalogo}

    # ids realmente usados por alguma playlist (activa ou rascunho) —
    # só esses entram na auditoria por faixa, para não gastar tempo em
    # ids órfãos (já cobertos pela Fototeca, 5 Out 2026).
    #
    # ids_sem_trecho_b_esperado: Mosaico (sempre, Bíblia §27.7 — trecho
    # único de 30s, só trecho_a), Retrato Sonoro (mecânica de 1 excerto
    # só, não A/B) e posições de Tributo cujo tipo não usa trecho_a/b
    # (foto/trivia/capa/logo usam imagem ou `full`, não os dois trechos).
    TIPOS_TRIBUTO_COM_TRECHO_B = {'audio', 'solo', 'cover', 'riff', 'bateria'}
    ids_usados = {}
    ids_sem_trecho_b_esperado = set()
    for chave, pl in playlists.items():
        estado = af_playlist_estado(pl, by_id)
        if pl.get('tipo') == 'tributo':
            for p in (pl.get('posicoes') or []):
                tid = p.get('id')
                if tid:
                    ids_usados.setdefault(tid, []).append((chave, estado))
                    if p.get('tipo') not in TIPOS_TRIBUTO_COM_TRECHO_B:
                        ids_sem_trecho_b_esperado.add(tid)
        else:
            for tid in playlist_ids(pl):
                if tid:
                    ids_usados.setdefault(tid, []).append((chave, estado))
                    if pl.get('tipo') == 'retrato':
                        ids_sem_trecho_b_esperado.add(tid)
        mos = pl.get('mosaico')
        if mos and mos.get('id'):
            ids_usados.setdefault(mos['id'], []).append((chave, estado))
            ids_sem_trecho_b_esperado.add(mos['id'])

    print(f'A auditar {len(ids_usados)} faixas usadas em {len(playlists)} playlists…')

    # ---------- auditoria por faixa ----------
    problemas_faixa = []  # (severidade, tid, descricao)

    def activa(tid):
        return any(e == 'pronta' for _, e in ids_usados.get(tid, []))

    def auditar_faixa(tid):
        c = by_id.get(tid)
        locais = []
        if not c:
            return tid, locais
        sev_base = 'bloqueia o jogo' if activa(tid) else 'cosmético'
        sev_qualidade = 'afecta o piloto' if activa(tid) else 'cosmético'

        trechos_esperados = [('A', 'trecho_a')]
        if tid not in ids_sem_trecho_b_esperado:
            trechos_esperados.append(('B', 'trecho_b'))
        for letra, campo in trechos_esperados:
            trecho = c.get(campo) or {}
            ficheiro = trecho.get('ficheiro')
            if not ficheiro:
                locais.append((sev_base, f'Trecho {letra}: sem ficheiro definido'))
                continue
            r = verificar_trecho(ficheiro, trecho.get('inicio'), trecho.get('fim'))
            if not r['existe']:
                locais.append((sev_base, f'Trecho {letra} ({ficheiro}): ficheiro não existe'))
                continue
            if r['silencio']:
                locais.append(('cosmético', f'Trecho {letra} ({ficheiro}): parece estar em silêncio'))
            if r['duracao_ok'] is False:
                locais.append(('cosmético', f'Trecho {letra} ({ficheiro}): duração {r["duracao"]:.1f}s fora do esperado'))

        if not c.get('imagem'):
            locais.append((sev_qualidade, 'sem imagem'))
        else:
            ok = imagem_abre(c['imagem'])
            if ok is False:
                locais.append((sev_qualidade, f'imagem não abre ({c["imagem"]})'))
            elif ok is None:
                locais.append(('cosmético', 'imagem não verificada (servidor remoto limitou os pedidos — confirmar manualmente)'))
            # imagem_licenca_estado:"confirmar" não entra aqui um a um —
            # é a maioria do catálogo (94%), já rastreado como item único
            # no checklist do STATUS.md; ver contagem agregada no resumo.

        voz_nome = RAIZ / 'voz' / f'nome_{tid}.wav'
        if not voz_nome.is_file():
            locais.append((sev_qualidade, 'sem voz/nome_<id>.wav'))

        return tid, locais

    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
        resultados = list(ex.map(auditar_faixa, ids_usados.keys()))

    for tid, locais in resultados:
        for sev, desc in locais:
            problemas_faixa.append((sev, tid, desc))

    print(f'Concluída a auditoria por faixa — {len(problemas_faixa)} problema(s) encontrados.')

    # ---------- auditoria por playlist ----------
    problemas_playlist = []  # (severidade, chave, descricao)

    for chave, pl in playlists.items():
        estado = af_playlist_estado(pl, by_id)
        sev_base = 'bloqueia o jogo' if estado == 'pronta' else 'cosmético'
        sev_qualidade = 'afecta o piloto' if estado == 'pronta' else 'cosmético'

        if pl.get('tipo') == 'tributo':
            posicoes = pl.get('posicoes') or []
            # "capa" é a única posição de Tributo sem id de faixa por
            # desenho (é só uma imagem de álbum) — não é uma posição vazia.
            vazios = [p.get('pos') for p in posicoes if not p.get('id') and p.get('tipo') != 'capa']
            esperado_n = 8
            n_preenchido = len(posicoes)
        else:
            ids = playlist_ids(pl)
            vazios = [i + 1 for i, tid in enumerate(ids) if not tid]
            # Retrato não tem Mosaico (confirmado nos dados) — compensa
            # com 8 posições em `musicas` em vez de 7+Mosaico.
            esperado_n = 8 if pl.get('tipo') == 'retrato' else 7
            n_preenchido = len(ids)
        if vazios:
            problemas_playlist.append((sev_base, chave, f'posições vazias: {vazios}'))
        if n_preenchido < esperado_n:
            problemas_playlist.append((sev_qualidade, chave, f'só {n_preenchido} posições preenchidas (esperado {esperado_n})'))

        mosaico = pl.get('mosaico')
        # Retrato Sonoro não tem Mosaico por desenho (confirmado nos dados:
        # as 2 playlists existentes têm mosaico:None de forma consistente).
        if pl.get('tipo') not in ('tributo', 'retrato'):
            if not mosaico or not mosaico.get('id'):
                problemas_playlist.append((sev_base, chave, 'Mosaico sem id de faixa'))
            elif not mosaico.get('pessoa'):
                problemas_playlist.append((sev_qualidade, chave, 'Mosaico sem "pessoa"'))
            if mosaico and mosaico.get('id'):
                faixa_mosaico = by_id.get(mosaico['id'])
                if not faixa_mosaico or not faixa_mosaico.get('imagem'):
                    problemas_playlist.append((sev_qualidade, chave, 'Mosaico sem imagem'))

        if not pl.get('descritivo_apresentador'):
            problemas_playlist.append((sev_qualidade, chave, 'sem descritivo_apresentador'))
        else:
            voz_descritivo = RAIZ / 'voz' / f'descritivo_{chave}.wav'
            if not voz_descritivo.is_file():
                problemas_playlist.append((sev_qualidade, chave, 'sem voz/descritivo_<código>.wav'))

        perguntas_bonus = pl.get('perguntas_bonus') or {}
        for i in range(1, len(ids) + 1):
            deve_ter = faixa_tem_bonus(chave, pl, i)
            tem = str(i) in perguntas_bonus or i in perguntas_bonus
            if deve_ter and not tem:
                problemas_playlist.append((sev_qualidade, chave, f'Faixa {i}: devia ter Pergunta Bónus e não tem'))
            elif tem and not deve_ter:
                problemas_playlist.append(('cosmético', chave, f'Faixa {i}: tem Pergunta Bónus mas a regra não prevê aqui'))
            elif tem and deve_ter:
                pb = perguntas_bonus.get(str(i)) or perguntas_bonus.get(i) or {}
                if pb.get('revisto') is False:
                    problemas_playlist.append(('cosmético', chave, f'Faixa {i}: Pergunta Bónus ainda "por rever" (IA)'))

        repetidos = artistas_repetidos(chave, pl, by_id)
        for r in repetidos:
            problemas_playlist.append((sev_qualidade, chave, f'artista repetido: {r["nome"]} ({", ".join(r["posicoes"])})'))

    print(f'Concluída a auditoria por playlist — {len(problemas_playlist)} problema(s) encontrados.')

    # ---------- escreve o relatório ----------
    ordem_sev = {'bloqueia o jogo': 0, 'afecta o piloto': 1, 'cosmético': 2}
    todos = [(s, 'faixa', tid, desc) for s, tid, desc in problemas_faixa] + \
            [(s, 'playlist', chave, desc) for s, chave, desc in problemas_playlist]
    todos.sort(key=lambda x: (ordem_sev.get(x[0], 9), x[0], x[1], x[2]))

    contagem_sev = {'bloqueia o jogo': 0, 'afecta o piloto': 0, 'cosmético': 0}
    for s, *_ in todos:
        contagem_sev[s] = contagem_sev.get(s, 0) + 1

    linhas = []
    linhas.append(f'# Auditoria ao catálogo e às playlists — {DATA_HOJE}\n')
    linhas.append('Gerado por `_auditoria_catalogo.py` — só leitura, nada alterado em `catalogo.json`/`playlists.json`.\n')
    linhas.append('## Resumo\n')
    linhas.append(f'- Faixas auditadas (usadas em alguma playlist): **{len(ids_usados)}**')
    linhas.append(f'- Playlists auditadas: **{len(playlists)}**')
    linhas.append(f'- Problemas encontrados: **{len(todos)}** — 🔴 bloqueia o jogo: {contagem_sev["bloqueia o jogo"]} · 🟠 afecta o piloto: {contagem_sev["afecta o piloto"]} · ⚪ cosmético: {contagem_sev["cosmético"]}')
    n_confirmar = sum(1 for c in catalogo if c.get('imagem_licenca_estado') == 'confirmar')
    linhas.append(f'- Imagens com `imagem_licenca_estado:"confirmar"`: **{n_confirmar}/{len(catalogo)}** (não listadas uma a uma abaixo — já no checklist "Revisão de conteúdo" do STATUS.md)\n')

    for sev, emoji in (('bloqueia o jogo', '🔴'), ('afecta o piloto', '🟠'), ('cosmético', '⚪')):
        itens = [t for t in todos if t[0] == sev]
        if not itens:
            continue
        linhas.append(f'## {emoji} {sev.capitalize()} ({len(itens)})\n')
        for s, tipo, chave_ou_id, desc in itens:
            linhas.append(f'- **[{tipo}] {chave_ou_id}** — {desc}')
        linhas.append('')

    RELATORIO_PATH.parent.mkdir(exist_ok=True)
    RELATORIO_PATH.write_text('\n'.join(linhas), encoding='utf-8')
    print(f'\nRelatório escrito em {RELATORIO_PATH}')
    print(f'Total: {len(todos)} problema(s) — bloqueia o jogo: {contagem_sev["bloqueia o jogo"]}, afecta o piloto: {contagem_sev["afecta o piloto"]}, cosmético: {contagem_sev["cosmético"]}')


if __name__ == '__main__':
    main()
