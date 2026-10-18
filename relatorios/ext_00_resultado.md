# Áudio estendido Anos 2000 por correlação no ficheiro inteiro + verificação do B2 em runtime (18 Out 2026)

Scripts: `scripts/gerar_audio_ext_dec00_fullscan.py` (geração) — saída em `relatorios/ext_00_fullscan_resultado.json`. `node --check` não se aplica (nenhum ficheiro `.js`/`.html` foi editado nesta tarefa, só lido para o diagnóstico do ponto 3).

## 1–2. Localização por correlação no ficheiro inteiro + geração + verificação

Para `dec00_02`, `dec00_04`, `dec00_06`, `dec00_07`: localizado cada Trecho A/B actual dentro de `tmp_dl/<id>_full.mp3` por correlação ao longo do ficheiro **inteiro** (nunca `inicio`/`fim` do catálogo, confirmado desactualizado nestas 4 faixas numa sessão anterior).

| id | lado | pico posição | posição | ≥0,90? | ext gerado | verificação (≥0,95) | resultado |
|---|---|---|---|---|---|---|---|
| dec00_02 | A | 0,931 | 47,47s | sim | sim | **0,931 — falhou** | ext apagado |
| dec00_02 | B | 0,938 | 65,43s | sim | sim | **0,238 — falhou** | ext apagado |
| dec00_04 | A | 0,997 | 4,02s | sim | sim | 1,000 | ✅ gravado |
| dec00_04 | B | 0,968 | 152,03s | sim | sim | 1,000 | ✅ gravado |
| dec00_06 | A | 0,999 | 4,02s | sim | sim | 1,000 | ✅ gravado |
| dec00_06 | B | 0,981 | 68,03s | sim | sim | 1,000 | ✅ gravado |
| dec00_07 | A | 0,996 | 4,02s | sim | sim | 1,000 | ✅ gravado |
| dec00_07 | B | 0,982 | 128,03s | sim | sim | 1,000 | ✅ gravado |

**dec00_02 — os dois lados passaram o limiar de localização (0,90) mas falharam a verificação pós-corte (0,95)** — o pico de A ficou exactamente no limite (0,931, nunca ia passar 0,95) e o de B caiu de 0,938 para 0,238 depois do corte (desalinhamento real, não um problema do método: a correlação na busca usa uma janela de 5s a deslizar por todo o ficheiro, a verificação exige que o alinhamento preciso no ponto escolhido se mantenha nos primeiros segundos — aqui não se manteve). **Ambos os `ext` foram apagados automaticamente, catálogo não tocado para `dec00_02`.** Confirma a desconfiança já registada no relatório anterior sobre a fonte desta faixa.

`dec00_04`, `dec00_06`, `dec00_07` — **os dois lados confirmados e gravados**, verificação perfeita (1,000, fonte e corte alinhados ao sample).

`dec00_01`, `dec00_03`, `dec00_05` **não foram tocadas** (fora do âmbito desta tarefa; `03`/`05` continuam com fonte por confirmar).

## Backup e gravação no catálogo

Só depois de todas as verificações: backup em `backups_catalogo/catalogo_20261018_210203_antes-ext-00b.json`, tag git `antes-ext-00b`, e `catalogo.json` actualizado com `trecho_a.ficheiro_ext`/`trecho_b.ficheiro_ext` **só** para `dec00_04`, `dec00_06`, `dec00_07` (6 campos, 3 faixas). `dec00_02` ficou sem qualquer escrita no catálogo.

Ficheiros gerados (25s cada = trecho real 15s + 10s Dmin, `ffmpeg -c copy` a partir do `tmp_dl` full — mesmo bitrate/loudness da `dec00_01`, herdados automaticamente por não haver reencoder):
`assets/audio_ext/dec00_04_a_ext.mp3`, `dec00_04_b_ext.mp3`, `dec00_06_a_ext.mp3`, `dec00_06_b_ext.mp3`, `dec00_07_a_ext.mp3`, `dec00_07_b_ext.mp3`.

## 3. Diagnóstico (só leitura) — o jogo lê `inicio`/`fim` ou só o ficheiro?

Confirmado em `musicbox.html`: a reprodução normal usa sempre `trecho_a.ficheiro`/`trecho_b.ficheiro` (e `ficheiro_ext` quando presente em **ambos** os lados — `temAudioExtendido()`, linha ~1578, exige `ficheiro_ext` em A **e** B para activar o áudio estendido). **`inicio`/`fim` nunca são lidos em runtime para tocar** — a única referência encontrada a `trecho_a.inicio` é num comentário sobre a calibração do offset de vídeo (`video_offset_s`), não em código de reprodução. Ou seja: `inicio`/`fim` só importam na altura de CORTAR o ficheiro (offline); depois de cortado, o jogo toca o `.mp3` do início ao fim, seja o que for que esse ficheiro contenha.

### B2 — a alteração é audível hoje?

Verificado directamente nos objectos git (os `.mp3` estão em Git LFS — comparar só o ficheiro em disco contra um `git show` de outra revisão compara o *pointer* LFS, não o áudio; a comparação correcta é o `oid sha256` do pointer):

| id | oid LFS antes do B2 | oid LFS agora | Mudou? |
|---|---|---|---|
| dec00_02 | `f448445...` | `f448445...` | **Não** |
| dec00_05 | `10facb5...` | `10facb5...` | **Não** |
| dec60_02 | `6f378ab...` | `6f378ab...` | **Não** |
| dec60_05 | `c92a70d...` | `c92a70d...` | **Não** |

**Nas 4 faixas, o `.mp3` de produção é byte-a-byte o mesmo de antes do B2** — confirma a leitura da sessão anterior (`gerar_previews_b2_00.py`): B2 só mudou `trecho_b.inicio`/`fim` em `catalogo.json`. Combinado com o ponto anterior (o jogo nunca lê `inicio`/`fim` para tocar): **a decisão "B2 melhor" não é audível em jogo em nenhuma das 4 faixas hoje** — é só um registo no catálogo, sem efeito no som.

**O que seria preciso para a tornar audível**: cortar de novo o ficheiro `trecho_b.ficheiro` (mesmo nome, conteúdo novo) a partir do `full` correspondente, nos tempos `inicio`/`fim` já gravados pelo B2, e substituir o `.mp3` de produção (com backup antes). **Não é um passo trivial para `dec00_02`/`dec00_05`**: a fonte actual em `tmp_dl` já não dá garantias — o Trecho B de `dec00_02` só bate com confiança a 65,4s (não aos 100s que o B2 regista) e o de `dec00_05` não bate com confiança em posição nenhuma (ver `relatorios/regeneracao_00_dryrun.md`); seria preciso confirmar/obter uma fonte fiável primeiro. `dec60_02`/`dec60_05` não foram analisados por correlação nesta tarefa (fora do pedido) — o mesmo tipo de confirmação seria necessário antes de cortar.

**Nada foi alterado para tornar o B2 audível — isto é só diagnóstico, como pedido.**
