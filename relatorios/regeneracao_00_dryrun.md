# Regeneração Anos 2000 (STD.INT.00.MIX.001) a partir da fonte nova — ENSAIO (dry-run), 18 Out 2026

**Nada foi alterado em `catalogo.json`, `playlists.json`, `mp3_index.json` nem `assets/`.** Scripts em `scripts/regen_00_scan_fonte.py` e `scripts/regen_00_ensaio.py`; saída em `relatorios/regen_00_scan_fonte.json`, `relatorios/regen_00_ensaio.json` e `_preview_revisao/regen_00/` (índice: `_preview_revisao/regen_00/index.md`).

## 1. Proveniência por faixa

Campos existentes no catálogo (os pedidos "fonte"/"datas" não existem como tal): cada entrada tem só `fonte_audio` (URL do YouTube), `ficheiro` (nome do `.mp3` de produção) e `full: null` sempre (não há caminho de ficheiro completo gravado — o download fica só em `tmp_dl/`, que está no `.gitignore`, efémero). `data` é uma data única de curadoria (28 Ago 2026) para as 7 faixas, não há datas por trecho.

| id | `fonte_audio` (catálogo) | URL no manifesto (`_revisao_regeneracao.json`) | Igual? |
|---|---|---|---|
| dec00_01 | `-7XnDlYY9qw` | `PWgvGjAhvIw` | **Não** — mas fora de causa (ver §3) |
| dec00_02 | `ViwtNLUqkMY` | *(sem entrada no manifesto)* | — |
| dec00_03 | `l7MaKmKJqoc` | `l7MaKmKJqoc` | Sim |
| dec00_04 | `0J2QdDbelmY` | `0J2QdDbelmY` | Sim |
| dec00_05 | `7l1A2gShWZo` | `7l1A2gShWZo` | Sim |
| dec00_06 | `gB9P0kpc1O4` | `gB9P0kpc1O4` | Sim |
| dec00_07 | `CvBfHwUxHIk` | `CvBfHwUxHIk` | Sim |

### `tmp_dl/<id>_full.mp3` corresponde ao download original (`estudos/trecho_b_expoente/cache/<id>.mp3`, 11 Out)?

Comparação por md5 (não há forma de reconfirmar contra o YouTube em modo ensaio/offline — isto confirma se é o MESMO download de sessões anteriores, não se o YouTube ainda serve o mesmo ficheiro hoje):

| id | `tmp_dl` == cache 11 Out? |
|---|---|
| dec00_01 | Sim (mesmo tamanho, 8.428.125 bytes) |
| dec00_02 | **Não** — tamanhos diferentes (7.249.581 vs 7.739.949) |
| dec00_03 | Sim (md5 `a4c067b0...` idêntico) |
| dec00_04 | **Não** — md5 diferente |
| dec00_05 | Sim (md5 `cbe1f7fd...` idêntico) |
| dec00_06 | Sim (md5 `171536f0...` idêntico) |
| dec00_07 | **Não** — md5 diferente |

### Confirmação por um segundo método: correlação com o ficheiro `tmp_dl` **inteiro** (não só na posição registada no catálogo)

Já existia uma verificação (`scripts/gerar_audio_ext_dec00.py`, 16 Out) que testava a correlação só numa janela estreita à volta do `inicio` do catálogo — resultado: 0,06 a 0,48 em quase todas (abaixo do limiar 0,60), exceto `dec00_01` (0,99–1,00, controlo) e o Trecho B de `dec00_06` (0,98). É essa a leitura "0,09–0,32" que o André tinha em mente (ver também `scripts/gerar_previews_b2_00.py`, docstring).

Fiz um **segundo método**: varrer o ficheiro `tmp_dl` completo (não só a janela antiga) à procura do melhor pico de correlação em qualquer posição — isto distingue "ficheiro errado" (pico baixo em todo o lado) de "mesma gravação, só numa posição diferente da que o catálogo registou" (pico alto, noutro sítio):

| id | Trecho A — pico @posição | Trecho B — pico @posição | Leitura |
|---|---|---|---|
| dec00_01 | 0,991 @0,0s | 0,997 @142,0s | mesma gravação, posição certa — controlo OK |
| dec00_02 | 0,931 @**47,5s** | 0,938 @**65,4s** | mesma gravação — **catálogo desactualizado** (diz 0s/100s, ficheiro real já está a 47,5s/65,4s) |
| dec00_03 | 0,548 @0,5s | 0,558 @186,4s | **nenhum pico passa o limiar 0,60** — fonte não confirmada com confiança nos dois lados |
| dec00_04 | 0,997 @4,0s | 0,968 @152,0s | mesma gravação — catálogo desactualizado (diz 0s/18s) |
| dec00_05 | 0,607 @4,1s | **0,436** @69,4s | Trecho A à justa; **Trecho B não bate em posição nenhuma** — fonte não confirmada |
| dec00_06 | 0,999 @4,0s | 0,981 @68,0s | mesma gravação, confirmada |
| dec00_07 | 0,996 @4,0s | 0,982 @128,0s | mesma gravação — catálogo desactualizado (diz 0s/18s) |

**Leitura de conjunto**: não são, na maioria, "ficheiros errados" — são **duas coisas sobrepostas**:
1. **Metadados desactualizados** (`dec00_02/04/07`, e provavelmente `06`): o ficheiro de produção já foi recortado numa posição nova (4s/68s/128s/152s — tudo próximo das propostas "regenerado"/"rejeitado" no manifesto), mas `catalogo.json` nunca foi actualizado — é por **desenho**: `_aplicar_regeneracao_playlist.py` só troca os `.mp3`, nunca escreve em `catalogo.json` (confirmado no código, linha a linha). Isto é cosmético para o jogo (que toca o ficheiro directamente, não usa `inicio`/`fim` em runtime) mas torna `catalogo.json` não fiável como registo do que está realmente em produção.
2. **Fonte genuinamente duvidosa** (`dec00_03` e `dec00_05`): o pico de correlação mais alto encontrado em todo o ficheiro `tmp_dl` fica abaixo (ou mal acima, no caso do A de `dec00_05`) do limiar de 0,60 — não há posição nenhuma no `tmp_dl` actual que explique com confiança o conteúdo hoje em produção. Mais provável **edição/remaster diferente** do que "ficheiro de outra música": os tamanhos/duração do `full` são plausíveis para a mesma canção (não há suspeita de artista/título errado), e no caso de `dec00_03` o pico mais alto do Trecho B (186,4s) cai exactamente onde a proposta pendente do manifesto também aponta (`tempo_b: 186`) — sugere que a produção actual já foi cortada de uma fonte parecida mas não idêntica (reencode/remaster/versão de vídeo diferente da oficial), não de uma fonte aleatória.

## 2/3. Ensaio da regeneração (dec00_02–dec00_07) e previews

Replica a lógica de `_aplicar_regeneracao_playlist.py` **sem mover nada** (`scripts/regen_00_ensaio.py`). Resultado por faixa — o que o script real faria **se corresse agora**:

| id | estado no manifesto | o que o script faria agora |
|---|---|---|
| dec00_02 | *sem entrada* | nada — não há proposta nenhuma para esta faixa neste fluxo |
| dec00_03 | `aprovado` | **TROCARIA** `dec00_03_a.mp3`/`dec00_03_b.mp3` pela pré-audição já em disco — **sem criar novo backup** (o backup em `_backup_pre_regeneracao/` já existe e é de uma troca ANTERIOR; o estado actual, que está entre o backup e a proposta, perder-se-ia sem cópia) |
| dec00_04 | `regenerado` | nada — já aplicado, idempotente |
| dec00_05 | `aprovado` | **TROCARIA** `dec00_05_a.mp3`/`dec00_05_b.mp3` pela pré-audição — mesmo risco de `dec00_03` (sem backup do estado actual) |
| dec00_06 | `rejeitado` | nada — decisão do André já registada |
| dec00_07 | `regenerado` | nada — já aplicado, idempotente |

Tabela Trecho A/B actual vs proposto, ficheiros, e áudio estendido (+10s): ver `_preview_revisao/regen_00/index.md` (inclui pico de correlação e alertas por faixa). Resumo: `_novo` só foi gerado para `dec00_03`/`dec00_05` (têm pré-audição guardada) — para `dec00_02/04/06/07` **não há corte novo a propor** (04/07 já aplicados; 02 sem proposta; 06 já rejeitada), por isso não se cortou nada de `tmp_dl` sem confirmação para essas quatro.

## 4. `dec00_01` e `dec00_03` — impacto no vídeo

- **`dec00_01`** (fora do ensaio, como pedido): `video_offset_s = 68,049`, fonte confirmada (0,99/0,997, controlo). Não regenerar — não há nada a ganhar e perder-se-ia a calibração.
- **`dec00_03`**: `video_offset_s = 3,597`, `video_sincronizado: true`, calibrado sobre uma janela de referência de ~101s na fonte (ver `relatorios/dec00_03_calibracao.md`) — **nem a posição actual do catálogo (18s) nem a proposta pendente (186s)** correspondem a essa janela. Aplicar a proposta pendente (ou qualquer troca de `trecho_b`) **dessincronizaria o vídeo** (`video_local`/`clip_b` continuariam a mostrar a cena calibrada para outra posição) — exigiria recalibração completa do offset, não só trocar o áudio. Combinado com a correlação de fonte fraca (0,55 no Trecho B, abaixo do limiar), **`dec00_03` é a faixa de maior risco desta playlist** — não aplicar sem (a) confirmar a fonte por audição directa e (b) recalibrar o vídeo se o trecho mudar.

## Sequência segura para aplicar (quando/se o André decidir avançar)

1. **Ouvir primeiro, sem tocar em nada**: `_preview_revisao/regen_00/dec00_03_{A,B}_novo.mp3` e `dec00_05_{A,B}_novo.mp3` contra os `_actual` — são os dois casos sem fonte confirmada.
2. Se `dec00_03`/`dec00_05` forem confirmados por audição: **backup manual explícito do estado ACTUAL** (não o antigo em `_backup_pre_regeneracao/`, que já é de uma troca anterior) + tag git, antes de correr `_aplicar_regeneracao_playlist.py` — o script, tal como está, não protegeria este backup.
3. Uma faixa de cada vez (nunca a playlist toda de uma vez), com o André a testar no jogo entre cada troca.
4. `dec00_03`: só depois de decidir se o `trecho_b` muda — se mudar, recalibrar `video_offset_s` com `estudos/trecho_b_expoente/video_offset.py` antes de considerar a faixa fechada.
5. `dec00_02`: sem proposta disponível neste fluxo — se se quiser corrigir o metadado desactualizado (`inicio`/`fim` no catálogo não reflectem o ficheiro real a 47,5s/65,4s), é uma edição separada e pequena ao catálogo, não uma regeneração de áudio; precisa de aprovação à parte (regra do catálogo).
6. `dec00_04`/`dec00_06`/`dec00_07`: nada a fazer — já aplicados/decididos; o desalinhamento `inicio`/`fim` no catálogo é cosmético (não afecta o jogo), corrigir só se/quando houver uma arrumação geral deste metadado.
