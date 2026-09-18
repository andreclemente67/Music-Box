#!/usr/bin/env python3
"""
MUSIC BOX — Popular feedback.json com as playlists existentes (Opção B)

Script de uso único (backfill): percorre todas as playlists em
playlists.json com feedback_id: null (as 39 criadas antes do sistema de
feedback existir, todas manuais — nunca passaram pela tab "✦ Gerar com
IA") e cria um registo em feedback.json para cada uma, marcando todas as
faixas como já aceites pelo curador (decisao: "aceite",
posicao_sugerida == posicao_final == posição actual na playlist).

Cobre os 4 "tipo" de playlist encontrados:
  - standard / retrato / video: pl.musicas (lista de ids) + pl.mosaico
    ({categoria, pessoa, id}).
  - tributo: pl.posicoes (lista de {pos, tipo, id, chave, ...}) — sem
    mosaico próprio (o conceito de mosaico aqui é um booleano por
    posição, "mosaico": true/false, não um objecto separado como nos
    outros tipos) — por isso o registo de tributo fica sempre com
    "mosaico": null. Posições sem id de catálogo (ex. tipo "capa", só
    imagem) entram com id_faixa=null e titulo tirado de `chave`.

Não altera nada em modo_geracao/parametro (fixos a "manual"/null, como
pedido — estas playlists não vieram de nenhuma geração por IA).
"""
import json
import os

APP_DIR = os.path.dirname(os.path.abspath(__file__))
PLAYLISTS_PATH = os.path.join(APP_DIR, 'playlists.json')
CATALOGO_PATH = os.path.join(APP_DIR, 'catalogo.json')
FEEDBACK_PATH = os.path.join(APP_DIR, 'feedback.json')


def nome_artista(faixa):
    art = faixa.get('artista') or []
    return ' / '.join(art) if art else ''


def faixas_de_playlist(pl, catalogo_por_id):
    """Devolve (faixas[], mosaico|None) no formato do registo de feedback."""
    if pl.get('tipo') == 'tributo':
        faixas = []
        for pos in pl.get('posicoes') or []:
            fid = pos.get('id')
            cat = catalogo_por_id.get(fid) if fid else None
            faixas.append({
                'id_faixa': fid,
                'titulo': cat['titulo'] if cat else (pos.get('chave') or ''),
                'artista': nome_artista(cat) if cat else '',
                'decisao': 'aceite',
                'posicao_sugerida': pos['pos'],
                'posicao_final': pos['pos'],
                'motivo': None,
            })
        return faixas, None

    faixas = []
    for i, fid in enumerate(pl.get('musicas') or [], start=1):
        cat = catalogo_por_id.get(fid)
        faixas.append({
            'id_faixa': fid,
            'titulo': cat['titulo'] if cat else '',
            'artista': nome_artista(cat) if cat else '',
            'decisao': 'aceite',
            'posicao_sugerida': i,
            'posicao_final': i,
            'motivo': None,
        })

    mosaico = None
    if pl.get('mosaico'):
        mos_id = pl['mosaico'].get('id')
        mosaico = {
            'id_faixa': mos_id,
            'decisao': 'aceite',
            'motivo': None,
        }
    return faixas, mosaico


def main():
    with open(PLAYLISTS_PATH, encoding='utf-8') as f:
        playlists = json.load(f)
    with open(CATALOGO_PATH, encoding='utf-8') as f:
        catalogo = json.load(f)
    with open(FEEDBACK_PATH, encoding='utf-8') as f:
        feedback = json.load(f)

    catalogo_por_id = {f['id']: f for f in catalogo}

    alvo = [chave for chave, pl in playlists.items() if pl.get('feedback_id') is None]
    print(f'{len(alvo)} playlist(s) com feedback_id: null')

    criados = []
    for chave in sorted(alvo):
        pl = playlists[chave]
        faixas, mosaico = faixas_de_playlist(pl, catalogo_por_id)

        fb_id = 'fb_' + str(len(feedback['historico']) + 1).zfill(3)
        registo = {
            'id': fb_id,
            'data': pl.get('data') or '2026-09-18',
            'curador': 'andre',
            'modo_geracao': 'manual',
            'parametro': None,
            'playlist_codigo': chave,
            'faixas': faixas,
            'mosaico': mosaico,
            'playlist_aprovada': True,
            'feedback_jogo': None,
        }
        feedback['historico'].append(registo)
        pl['feedback_id'] = fb_id
        criados.append((fb_id, chave, len(faixas)))

    with open(PLAYLISTS_PATH, 'w', encoding='utf-8') as f:
        json.dump(playlists, f, indent=2, ensure_ascii=False)
        f.write('\n')
    with open(FEEDBACK_PATH, 'w', encoding='utf-8') as f:
        json.dump(feedback, f, indent=2, ensure_ascii=False)
        f.write('\n')

    print(f'\n{len(criados)} registo(s) criado(s) em feedback.json e ligado(s) em playlists.json:\n')
    for fb_id, chave, n in criados:
        print(f'  {fb_id}  {chave:<28} {n} faixa(s)')


if __name__ == '__main__':
    main()
