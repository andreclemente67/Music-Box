# B2 tornado audível — 4 faixas aprovadas pelo André (18 Out 2026)

`trecho_b.inicio/fim` destas 4 faixas já estava em B2 no catálogo desde a aplicação
anterior (`antes-b2-00`, `antes-b2-60`), mas o ficheiro `.mp3` de produção nunca tinha
sido recortado de novo — continuava com o áudio do B antigo (ver STATUS.md). Esta
tarefa corta o B2 real de `tmp_dl/<id>_full.mp3` e substitui o ficheiro de produção.

Script: `scripts/aplicar_b2_audivel.py`. Método: corte directo (decode+reencode,
48kHz, libmp3lame `-q:a 0`) na posição `trecho_b.inicio/fim` do catálogo. Sem fades
(nenhum Trecho B existente no catálogo tem fade programático — confirmado por
inspecção de amplitude antes de decidir o método). Loudness ajustada só por
atenuação (nunca ganho, para não arriscar clipping — os cortes brutos já tinham
pico a 0dBFS) quando o corte bruto excedia 1 LU do Trecho B antigo da mesma faixa
(referência "antes/depois" por faixa — a média do pack tem ~2 LU de desvio-padrão
natural, não serve de referência útil).

Backup do catálogo: `backups_catalogo/catalogo_20261018_230802_antes-b2-audivel.json`.
Tag git: `antes-b2-audivel` (estado completo do repo antes desta tarefa).

## Resultado — 4/4 aplicadas

| Faixa | Título | B2 (s) | Ganho aplicado | Loudness final vs. B antigo | Correlação full@B2 | Correlação ext vs. B novo |
|---|---|---|---|---|---|---|
| dec60_02 | (I Can't Get No) Satisfaction | 53–68 | — | 0,0 LU | 0,997 | 1,000 |
| dec60_05 | My Girl | 86–101 | −1,6 dB | 0,0 LU | 1,000 | 1,000 |
| dec00_02 | Crazy in Love | 100–115 | −2,8 dB | 0,0 LU | 0,999 | 1,000 |
| dec00_05 | Toxic | 77–92 | −1,8 dB | 0,0 LU | 0,999 | 1,000 |

Todas as 4 passaram as 4 verificações (duração ~15s, correlação com o full ≥0,99,
ext idêntico ao B novo ≥0,95, loudness ≤1 LU do B antigo). Nenhuma faixa foi
saltada. Detalhe completo (todos os campos medidos) em
`_preview_revisao/b2_audivel_tmp/_linhas.json`.

## Ficheiros alterados

- `catalogo.json` — só `trecho_b.ficheiro_ext` gravado nas 4 faixas (diff cirúrgico
  de 8 linhas). `trecho_b.inicio/fim`, Trecho A e `trecho_a.ficheiro_ext` inalterados.
- `dec60_02_b.mp3`, `dec60_05_b.mp3`, `dec00_02_b.mp3`, `dec00_05_b.mp3` — ficheiro
  de produção substituído (mesmo nome).
- `assets/audio_ext/dec60_02_b_ext.mp3`, `dec60_05_b_ext.mp3`, `dec00_02_b_ext.mp3`,
  `dec00_05_b_ext.mp3` — novos (B2 + 10s, mesmo corte/ganho do B novo).
- `_arquivo/b2_substituidos/` — os 4 ficheiros de produção antigos (conteúdo do B
  anterior), movidos (não apagados).
- `playlists.json`, `mp3_index.json` — intocados.

## Como reverter

Repo completo ao estado anterior:

```
git checkout antes-b2-audivel -- catalogo.json dec60_02_b.mp3 dec60_05_b.mp3 dec00_02_b.mp3 dec00_05_b.mp3
git rm assets/audio_ext/dec60_02_b_ext.mp3 assets/audio_ext/dec60_05_b_ext.mp3 assets/audio_ext/dec00_02_b_ext.mp3 assets/audio_ext/dec00_05_b_ext.mp3
```

Ou, por faixa, repor só o ficheiro de produção a partir do arquivo (sem tocar no
catálogo nem no ext):

```
cp _arquivo/b2_substituidos/<id>_b.mp3 <id>_b.mp3
```

Catálogo isolado: `cp backups_catalogo/catalogo_20261018_230802_antes-b2-audivel.json catalogo.json`.
