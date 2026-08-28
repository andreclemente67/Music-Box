# Music Box — Tarefas

## Em curso

- [ ] **`01_a.mp3`/`01_b.mp3` — NÃO são realmente órfãos, reportado em vez de apagar (2026-08-29).** Nenhuma entrada de `catalogo.json` os referencia (a faixa "Take On Me" — a-ha migrou para o id `80_01`, ficheiros `80_01_a.mp3`/`80_01_b.mp3`, já em uso). MAS `musicbox.html` ainda os referencia directamente no literal hardcoded `COLLECTIONS.ANOS80` (linha ~441, `a:'01_a.mp3', b:'01_b.mp3'`) — o fallback offline usado só se `catalogo.json`/`playlists.json` falharem a carregar. Apagar quebraria esse fallback especificamente para a 1ª posição de Anos 80. Duração real (`afinfo`): 27s/15s — não seguem o formato actual (12s/10s), são cortes antigos, anteriores à convenção actual. Ficam por decidir: (a) manter como estão, servem o fallback; (b) actualizar o literal `ANOS80` em musicbox.html para `80_01_a.mp3`/`80_01_b.mp3` e só depois apagar os antigos. Não decidido aqui — a aguardar confirmação do utilizador.
- [ ] Confirmar no browser (não testável neste ambiente) que "Guardar playlists.json" no Studio já não pede autorização de pasta — deve escrever via `_servidor_escrita.py` (porta 8002) sem diálogo nenhum. Ver `DECISIONS.md` 2026-08-13.
- [ ] Testar no browser os 5 modos de "✦ Gerar com IA" (URL/Tema/Categoria/Semente múltipla/Playlist YouTube) — trocar sub-tabs, ler uma playlist real do YouTube e rever/editar a lista, gerar em cada modo, confirmar retentativas por artista repetido e o fallback claro após 3 tentativas. Só validado com testes isolados fora do browser + 1 chamada real à API. Ver `DECISIONS.md` 2026-08-21.
- [ ] Testar no browser o feedback ao vivo na Mesa de Montagem durante a geração de trechos A/B (contador + estado por faixa, incluindo depois de clicar "Ver na Mesa de Montagem" antes do lote terminar). Ver `DECISIONS.md` 2026-08-21.

## Bugs conhecidos (sessão 2026-08-25)

- [x] ~~**Catálogo:** "We Will Rock You" está atribuída a "Roger Taylor" em vez de "Queen"~~ — **RESOLVIDO 2026-08-27, na direção oposta à descrita aqui**: `bat_02` pertence à playlist "Solo de Bateria" (universo "Solistas"), onde `artista` deve mesmo ser a pessoa (o baterista), não a banda — "Roger Taylor" está correto, confirmado por biografia (TheAudioDB, artist/118481). O problema real era a *imagem*, que tinha sido encontrada a pesquisar "Queen" (banda) em vez de "Roger Taylor" — corrigida para a foto certa do baterista. A ideia de rever o catálogo à procura de casos parecidos (membro isolado vs. banda) foi implementada como `af_verificarConsistenciaArtistaBanda()` no Studio (badge 🔀, botão "Ver inconsistências artista/banda" na aba ASSETS) — ver também a extensão a `STD.PT.ALL.BAT.001` ("Bateria Portuguesa") abaixo.
- [ ] **"Gerar com IA" (modo Categoria):** consistentemente devolve só 6 faixas em vez das 7 esperadas para playlists Standard (testado 2x seguidas, mesmo resultado — 6 sugestões numeradas + mosaico, quando `expectedCount('standard')` é 7). Suspeita: o prompt/lógica de contagem deste modo especificamente (`montarPromptIA`/`af_musicasIAComSemente` em modo Categoria) pede o número errado de faixas à IA. Os outros modos (URL, Tema, Semente múltipla, Playlist YouTube) não foram testados quanto a este problema. Workaround usado: "Preencher automaticamente" para completar a posição em falta depois de criar a playlist.
- [ ] **Aba ADICIONAR FAIXA (pesquisa MusicBrainz):** a década/género gravados no catálogo vêm da gravação específica escolhida nos resultados da MusicBrainz, não da canção original — pode ficar errado quando o primeiro resultado é uma versão ao vivo, reedição ou remasterização mais tardia. Caso encontrado: "Sweet Home Alabama" (Lynyrd Skynyrd, original 1974) foi adicionada via este fluxo à playlist "Decade of Riffs" (Anos 70 — Rock) mas ficou gravada no catálogo com `decadas: ["1990s"]` e géneros "acoustic rock, blues rock, boogie rock" (vindos de uma gravação de 1997, provavelmente ao vivo/reedição), desalinhada com o resto da playlist. A causa é `afSelecionarResultado()`/`afDecadaDeAno(r.ano)` em `musicbox_studio.html`, que usa sempre o `first-release-date` da gravação específica devolvida pela API, sem distinguir gravação original de versões posteriores. Corrigir a entrada do Lynyrd Skynyrd manualmente no `catalogo.json` (década → 1970s, género → algo como "Southern Rock/Rock"), e considerar mostrar a década do resultado na lista de pesquisa (já a mostra) para o utilizador poder escolher conscientemente a gravação mais próxima do original, ou preferir resultados mais antigos por defeito.

## Pendente (sessão 2026-08-27)

- [x] ~~`ptbat_01` (UHF, "Cavalos de Corrida", 1980)~~ — **RESOLVIDO 2026-08-27**: `artista` → "Zé Carvalho" (baterista dos UHF de 1979 a 1984, creditado especificamente em "Cavalos de Corrida" e nos 4 álbuns seguintes), `banda` → "UHF". Confirmado com fonte pelo utilizador via `https://pt.wikipedia.org/wiki/Lista_de_membros_de_UHF` e `https://pt.wikipedia.org/wiki/Cavalos_de_Corrida` (secção "Membros da banda" desta última lista-o explicitamente) — verificado por mim antes de aplicar. `nota_curadoria` removido. Sem foto fiável do "Zé Carvalho" em nenhuma fonte (mesmo padrão dos outros 5) — `imagem_risco_ambiguidade: true` mantido, imagem continua a da banda.
- [x] ~~`ptbat_05` (RAMP, "Last Child")~~ — **RESOLVIDO 2026-08-29**: `artista` → "Paulo" (baterista da formação original dos RAMP e da gravação de "Thoughts", o mini-LP de estreia de 1992 que inclui "Last Child"), `banda` → "RAMP". Fontes primárias/quase-primárias (não Wikipedia): `rampmetal.com/biography/` (bio oficial, lista "Paulinho" nos ex-membros) e `portugal80smetal.blogspot.com/2011/09/ramp.html` (historial detalhado com datas — gravação nos Exit Studios, Setembro 1991, edição Fevereiro 1992 — nomeia "Paulo" explicitamente como baterista dessa sessão). Apelido continua por confirmar. **Correcção adicional**: `decadas` estava errado (`2000s`) — corrigido para `1990s`, já que "Thoughts" é de 1992. `imagem_risco_ambiguidade` mantido `true` (estava incorretamente `false` no catálogo, inconsistente com esta própria entrada de TASKS.md) — **a imagem actual (`artista_ptbat_05.png`) pode mostrar o RAMP errado (há um DJ homónimo não relacionado)**; precisa de revisão explícita na tarefa da Fototeca, não confirmada aqui.

## Por decidir / continuar amanhã (sessão 2026-08-25)

- [ ] **Playlist "Ambient & Introspectivo" (`STD.INT.ALL.MIX.001`)** — as 7 faixas
      (The Durutti Column "Sketch For Summer", Marconi Union "Weightless", Brian Eno
      "By This River" e "On Land", Thelonious Monk "Crépuscule avec Pauline", Sarah
      McLachlan "Surfacing", Buena Vista Social Club "Tres Palabras") mais o mosaico
      (Vini Reilly / The Durutti Column "For Belgian Friends") já têm trechos A/B
      gerados e `estado: "rascunho"`, mas nenhuma tem campo `imagem` — bloqueia o
      reveal em jogo. Decisão: adiado para "Versão 2" (retomar amanhã) — não incluir
      esta playlist em rotação de episódio até estar completa (confirmar também se o
      motor de selecção de playlists já filtra por `estado`, ou se isto hoje só é
      travado "à mão").
- [ ] **Faixa `the_moody_blues_tuesday_afternoon`** (Moody Blues, "Tuesday
      Afternoon") — trechos A/B já existem em disco (gerados hoje) mas a faixa não
      tem entrada em `catalogo.json`. Ficou de fora dos commits `18fef08`/`44cf7e0`
      por ser órfã (não é lixo de teste como `teste`/`aqsil_01`/`jrd_01` — precisa de
      ser catalogada).
- [ ] **77 entradas por decidir no `git status`**, deixadas de propósito por
      comitar após os commits `18fef08` (sidebar/`musicbox.html`) e `44cf7e0`
      (dados/trechos/docs): `.claude/`, `backups_catalogo/`, `mp3_index.json`, os 6
      pares de trechos órfãos (`aqsil_01`, `jrd_01`, `teste`,
      `the_durutti_column_sketch_for_summer_2`, `the_moody_blues_tuesday_afternoon` —
      este último já coberto acima), e um lote de imagens/scripts/docs não
      relacionado com o pedido de hoje. Sem pressa; rever e decidir o que entra em
      git, o que se apaga e o que fica deliberadamente fora (`.gitignore`).

## Confirmado — resposta esperada é sempre Artista/Banda (Format Book V11)

Confirmado na Bíblia (V11, secção 2 "Recognition Triangle" — tabela "Category
Objects — Matrizes Fechadas" — e secção 12 "Sistema de Validação"): para
Rock/Pop, Jazz/Blues/Soul, Hip Hop, Dance/Electrónica e Televisão, a QUESTION
permitida é sempre "Artista/Banda" — nunca nome da faixa. A secção 12 reforça
isto de forma explícita: "Resposta aceite: Nome do artista ou banda. Uma
única tipologia de resposta." Excepções: Música Clássica usa
"Compositor/Obra"; Cinema/Bandas Sonoras permite também "Filme"/"Compositor"
como alternativas.

Implicação prática: o campo `artista` de cada faixa no `catalogo.json` não é
só metadado — é o valor exacto que vai ser validado contra a resposta do
concorrente (Audio Timestamp + Speech-to-Text IA + Árbitro humano). Isto
torna o bug "We Will Rock You"/"Roger Taylor" (acima) mais crítico do que
parecia à primeira vista — não é só um erro de catalogação bonito-ou-feio, é
uma resposta que o sistema validaria mal num jogo real.

- [ ] Auditar o catálogo à procura de mais casos "membro individual em vez
      da banda" no campo `artista` (mesmo padrão do bug "We Will Rock You").
- [ ] Tratar o título da faixa (`titulo`) sempre como metadado de apoio
      (organização no Studio, reveal de imagem quando o concorrente acerta)
      — nunca como o que se pede ao concorrente para identificar.
- [ ] Quando existir UI de resposta/validação em jogo, não pode assumir
      sempre "artista/banda" de forma rígida — tem de saber qual QUESTION
      está activa por categoria (Música Clássica e Cinema diferem).

## Próximas tarefas

- [ ] Sistema de validação do catálogo
- [ ] Pesquisa MusicBrainz
- [ ] Gestão de faixas
- [ ] Sistema de trechos de áudio

## Sistema de Rotação de Playlists por Episódio

- [ ] Campo `usado_em` (array de episódios) em cada playlist no `playlists.json`
- [ ] Campo `ultimo_uso` (data) e `bloqueada_ate` (data) por playlist
- [ ] Regra: dentro do mesmo episódio não repetir género nem artista entre playlists
- [ ] Regra: playlist só volta após mínimo 10 episódios
- [ ] Vista "Preparar Episódio" no editor — seleccionar 4 playlists Fase 1 + 4 Fase 2 com validação automática de conflitos
- [ ] Filtro no editor: mostrar playlists disponíveis vs bloqueadas para uma data/episódio específico

## Decisões editoriais em aberto

*(Secção recuperada de `app/TASKS.md` em 2026-08-21, ao fundir esse
ficheiro — desactualizado e nunca commitado — para dentro deste, que é o
canónico.)*

### PENDENTE — SOLO como tipo estrutural

Actualmente Solo de Guitarra e Solo de Bateria são STD com género GTR/BAT.
Avaliar se faz sentido criar SOLO como 4º tipo estrutural (a par de
STD/RET/TRB), com implicações em `expectedCount()`, `grupos{}`, `labels{}`
e dropdown TIPO no modal Nova Playlist. Só avançar quando houver mais
playlists Solo que justifiquem a mudança.

### PENDENTE — Campos de reconhecimento no catálogo

Quando a mecânica do Recognition Triangle estiver definida, adicionar ao
catalogo.json e ao prompt do gerador IA os campos:

- `universal` (boolean) — reconhecida transgeracionalmente
- `nivel_reconhecimento` (1–5) — estimado pelo Claude na geração

Estes campos alimentarão o motor de selecção automática de Music Boxes por
episódio.

**Nota:** `catalogo.json` já tem hoje um campo `universal` (boolean, nas
109 entradas) e um campo `nivel` (inteiro, valores 1–4 em uso) — mas o
significado actual destes dois não está necessariamente ligado à mecânica
do Recognition Triangle. Confirmar, ao definir a mecânica, se `nivel`
passa a ser reaproveitado como `nivel_reconhecimento` (evitando um campo
duplicado) ou se são conceitos distintos que precisam de campos próprios.

### PENDENTE — Mecânica de selecção de playlists em jogo

Como e quando cada playlist entra num episódio é um dos segredos do
formato — decisão editorial central ainda por definir. Opções em aberto:

- Blind Draw (sorteio)
- Escolha pelo concorrente no painel
- Escolha editorial prévia
- Combinação das anteriores

Esta decisão define a tensão dramática do programa e deve ser documentada
na Bíblia V1.2 quando a mecânica estiver validada em testes de produção.

### PENDENTE — QUESTION específico para playlists Tributo

Reparado ao rever as entradas estáticas do `musicbox.html` (playlist
"Tribute Led Zeppelin", entretanto removida por não ter dados reais por
trás — ver `DECISIONS.md`): playlists Tributo (ex: "Tribute Beatles")
têm uma diferença estrutural das restantes que ainda não está pensada a
sério. Em todas as outras categorias, a regra confirmada (Format Book V11
§2/§12 — ver secção acima "Confirmado — resposta esperada é sempre
Artista/Banda") é que o concorrente identifica o artista/banda, que varia
faixa a faixa e não é conhecido à partida. Numa playlist Tributo isso não
faz sentido — o concorrente já sabe à partida qual é a banda (está no
nome da própria Music Box, ex: "Tribute Beatles"), por isso "quem é o
artista" deixa de ser uma pergunta com informação nenhuma.

A estrutura de `posicoes` já usada em `playlists.json` para Tributo (cada
posição com um `tipo` próprio — audio/trivia/solo/foto/cover/riff/capa/
bateria) sugere que a resposta já foi parcialmente pensada na direcção
certa (testar conhecimento profundo de fã sobre essa banda em específico,
não reconhecimento de artista), mas isto nunca foi documentado
explicitamente como decisão, nem ligado à mecânica QUESTION do
Recognition Triangle. Antes de criar mais playlists Tributo (ex: Led
Zeppelin, se vier a ser recriada com dados reais), definir: qual é o
QUESTION real de cada `tipo` de posição em Tributo (ex: `trivia` pede
título da faixa? `foto` pede o quê exactamente?), e como isto se encaixa
(ou não) na tabela "Category Objects — Matrizes Fechadas" do Format Book,
que hoje não cobre Tributo.

### PENDENTE — Playlist "Logótipos" (referência guardada, por fazer mais tarde)

Entrada estática `LOG-001` em `musicbox.html`, sem dados reais por trás.
Mantida deliberadamente como referência para se construir mais tarde —
ver `DECISIONS.md` 2026-08-25. Não apagar sem decisão explícita.

### PENDENTE — Categoria: Séries de TV / Banda Sonora

Avaliar a adição de uma playlist dedicada a bandas sonoras de séries de
televisão — temática com forte potencial de reconhecimento transgeracional
(ex: Twin Peaks, The Sopranos, Game of Thrones, Stranger Things, Breaking
Bad). Verificar se se enquadra na categoria "Televisão" já definida na
Bíblia ou se justifica categoria própria.

## Concluído

- [x] Estrutura inicial do Studio
- [x] Catálogo musical
- [x] Sistema de Chaves [TIPO].[GEO].[DEC].[GENERO].[VOL] (2026-08-10)
- [x] Botão "Definir início" para trecho_a.inicio na mesa de montagem (2026-08-10)
- [x] Botão "Preencher com este artista" (Retrato) na mesa de montagem (2026-08-10)
- [x] Botão "Preencher automaticamente" (qualquer tipo de playlist) na mesa de montagem (2026-08-10)
- [x] `auto_fusao.sh` + `iniciar_studio.command` — fusão automática de catalogo_adicionar.json (2026-08-10)