# Music Box — Status

## Última actualização
2026-08-29

## 2026-08-29 — Tags secundárias aplicadas a 21 playlists (`universos_secundarios`)
Plano proposto (36 playlists analisadas via `_dados_36_playlists.txt`) e
aprovado pelo utilizador sem alterações — aplicado tal e qual via
`_aplicar_tags_secundarias.py` (scratchpad). Preenche apenas o campo
`universos_secundarios` (eixo interno de metadados, nunca visível no
jogo); nenhum ID/código publicado foi alterado. As 3 Famílias jogáveis
(Décadas/Géneros/Especiais) e os 28 Universos canónicos mantêm-se
inalterados.

21 playlists actualizadas: `LOGO-001` (Guitarra), `STD.INT.00.MIX.001`
(Estados Unidos), `STD.INT.10.SYN.001` (Reino Unido, Alternative/Indie),
`STD.INT.10.SYN.002` (Alternative/Indie), `STD.INT.20.MIX.001` (Estados
Unidos), `STD.INT.50.MIX.001` (Estados Unidos), `STD.INT.60.MIX.001`
(Estados Unidos), `STD.INT.80.MIX.001` (Reino Unido, Synth),
`STD.INT.ALL.BAT.001` (Reino Unido), `STD.INT.ALL.BLU.001` (Estados
Unidos), `STD.INT.ALL.CIN.001` (Instrumental), `STD.INT.ALL.GAM.001`
(Instrumental), `STD.INT.ALL.HIP.001` (Estados Unidos),
`STD.INT.ALL.JAZ.001` (Estados Unidos), `STD.INT.ALL.MET.001` (Estados
Unidos), `STD.INT.ALL.MIX.001` (Ambient, Reino Unido),
`STD.INT.ALL.POP.001` (Estados Unidos), `STD.INT.ALL.SOU.001` (Estados
Unidos, Funk/Disco), `STD.INT.ALL.SYN.001` (França), `STD.INT.ALL.TV.001`
(Estados Unidos), `STD.US.ALL.AME.001` (Country/Folk, Acústico).

Estas tags usam também os códigos reservados nesta ronda (não aplicados
a nenhum dropdown/UI ainda, só reservados para uso futuro): Géneros —
ALT, FUK, REG, COU; Geografia — BR, US, UK, ES, FR, IT, AF, JP, LATAM;
Som/Performance — KEY, RIF, INR, OUT, ACO, LIV, COV, INS; Especiais —
AMB.

**Validado**: `playlists.json` continua JSON válido; `git diff` confirma
que só o campo `universos_secundarios` foi adicionado/alterado em 21
entradas (nenhuma outra chave tocada); `deno check` limpo em
`musicbox_studio.html` e `musicbox.html` (nenhum `.html` foi alterado
neste passo, mas confirmado por precaução).

## 2026-08-29 — Campo `sources` implementado (schema definido pelo utilizador) + confirmação de década
Schema definido pelo utilizador: `sources: {audio, imagem, data_recolha}`
— proveniência básica por faixa. Adicionado a todas as 284 faixas de
`catalogo.json` (`_adicionar_sources.py`, scratchpad):
- `imagem`: inferido de `imagem_fonte` (já existia, 100% das faixas
  preenchido).
- `data_recolha`: inferido de `imagem_data_captura` (fallback `data`).
- `audio`: **deixado `null` em todas as faixas retroactivamente** — não
  existe nenhum campo no catálogo actual que registe iTunes vs YouTube
  por faixa (confirmado: `_construir_playlist.py` calculava isto em
  memória — `e["_fonte_audio"]` — mas `_aplicar_playlist.py` nunca o
  persistia em `catalogo.json`, perdia-se sempre). Sem sinal fiável
  para inferir retroactivamente sem adivinhar, como pedido.

**Corrigido o root cause para faixas futuras**: `_aplicar_playlist.py`
(scratchpad, script usado para todas as playlists criadas nesta sessão)
actualizado para gravar `sources.audio` a partir de `_fonte_audio` a
partir de agora — deixa de se perder essa informação em playlists
novas.

**Confirmação sobre o Mosaico "Anos 2010 — Synth II"**: `decadas` de
`arcade_fire_my_body_is_a_cage` **já estava `["2000s"]`** — não
precisou de correcção, só confirmação (o campo já reflectia a data real
de lançamento, 2007; a divergência é só temática/editorial da playlist,
não um erro de dados).

Validado: JSON válido; `deno check` (exit 0, nenhum `.html` alterado).

## 2026-08-29 — Resolvida a discrepância "4 vs 10" da Fototeca (investigação de histórico git)
Pedido do utilizador: perceber o que aconteceu às outras 6 faixas da
"lista antiga de 10" que a revisão de 28 Ago só encontrou 4.
**Resposta: já tinham sido corrigidas na mesma sessão, antes mesmo de
eu começar a auditar — não é um gap real.**

Reconstruído via `git show <commit>:catalogo.json` em cada commit que
tocou o catálogo: no commit `3e797e8` (26 Ago, 17:38 — "Adiciona
cascata de imagens de artista... aplica 139 imagens melhoradas"), o
catálogo tinha mesmo **exactamente 10** faixas com `imagem_fonte`
iTunes: `a10_01, a10_03, pt80_04, pt80_06, bra001_mosaico, syn001_02,
ptbat_mosaico, beatles_03, beatles_04, disclosure_latch` — esta é, com
alta confiança, a origem real da "lista de 10". Logo no commit
**seguinte**, `1c47fdd` ("Checkpoint: recuperação de imagens apagadas
acidentalmente"), 6 dessas 10 (`a10_01, a10_03, syn001_02, beatles_03,
beatles_04, disclosure_latch`) já aparecem com `imagem_fonte:
"theaudiodb"` — confirmado que continuam assim, com retratos reais,
no catálogo actual. As 4 restantes (`pt80_04, pt80_06, bra001_mosaico,
ptbat_mosaico`) mantiveram-se iTunes até à revisão de 28 Ago (ver
entrada anterior), que as reviu/melhorou.

Conclusão: a contagem "10" estava correcta na altura em que foi feita;
6 delas foram corrigidas numa sessão anterior (mesmo dia, poucos
commits depois); as 4 finais foram as que a auditoria de 28 Ago
encontrou e reviu. Nada por resolver aqui.

## 2026-08-29 — Botão "👁 Revelar" no Mosaico da Mesa de Montagem
Novo botão no cartão do Mosaico (`slotCardHtml`, `kind==='mosaico'` +
tem imagem) — pré-visualiza a imagem já totalmente nítida, reaproveitando
o mini-player flutuante já existente (`previewImagem()`, o mesmo usado
pelo ícone 🖼 na Biblioteca), sem simular a mecânica de revelação
progressiva do jogo, como pedido.

Aplica-se a Standard e Retrato (ambos usam `slotCardHtml('mosaico', ...)`
em `renderSlotsSimples`) — **e também ao "Mosaico / Recap" das playlists
Tributo**, que reaproveita a mesma função de card do Mosaico
(`renderPosicoesTributo` chama `slotCardHtml('mosaico', ...)` no fim,
para o Recap final tipo "Abbey Road (Recap)"). Não removi essa extensão
— é o mesmo mecanismo de pré-visualização a fazer sentido no mesmo
sítio, mas fica documentado aqui porque o pedido original mencionava só
Standard/Retrato. Confirmado que playlists Retrato Sonoro sem Mosaico
(regra 30-Jul) continuam sem o botão, correctamente.

Validado: `deno check` (exit 0); teste real em Chrome
(`_teste_revelar_mosaico.js`, scratchpad) — clique no Mosaico de "Jazz"
abre o mini-player com a imagem certa ("Strange Fruit"); "Vozes
Lendárias" (Retrato Sonoro) confirmado sem Mosaico, sem botão; Tributo
Beatles mostra o botão no Recap, comportamento descrito acima.

## 2026-08-29 — Botão "Ver na app" na Mesa de Montagem
`musicbox.html` ganha suporte a abrir directamente numa playlist
específica via `?playlist=<chave>` (ex.
`musicbox.html?playlist=STD.INT.ALL.JAZ.001`) — não existia antes.
Nova IIFE `af_abrirPlaylistPorURL()` no fim do script: lê o parâmetro,
espera `catalogoPronto`, e reaproveita `testarPlaylist()` (mesmo
mecanismo do botão "◎ Testar uma Playlist" já existente) — chave
inexistente cai de volta ao ecrã inicial normal, sem rebentar.

No Studio, reaproveitado o botão "▶ App" já existente
(`af_abrirApp()`, cabeçalho geral) em vez de criar uma função
duplicada — agora inclui o parâmetro `?playlist=` quando há uma
playlist aberta, e abre sempre numa aba nova (`_blank`, nunca perde o
estado da Mesa de Montagem). Novo botão "▶ Ver na app" adicionado
directamente no cabeçalho de cada playlist na Mesa de Montagem
(`renderMontagem()`) — aplica-se a todos os tipos (Standard, Retrato,
Tributo, Vídeo), chama a mesma `af_abrirApp()`.

Validado: `deno check` (exit 0) em ambos os ficheiros; teste real em
Chrome via puppeteer-core (`_teste_ver_na_app.js`, scratchpad) — URL
directo abre e já está a tocar a playlist certa (`modoTeste:true`,
`faseGeral:"faixa"`); chave inexistente cai no ecrã inicial sem erro;
clique no botão "▶ Ver na app" (playlist Hip Hop aberta no Studio) abre
mesmo uma aba nova com a playlist certa a tocar.

## 2026-08-29 — Tooltips em controlos não óbvios (UX, item de baixa prioridade)
Passagem leve, não exaustiva ("sem pressa" — pedido de baixa
prioridade): a maioria dos botões de preenchimento automático já tinha
`title` detalhado (Auto em toda a playlist, Auto-match MP3, Gerar
trechos em falta) — adicionados os 3 que faltavam mesmo nesse grupo
("Preencher com este artista", "Preencher automaticamente" ×2, uma
ocorrência por cada formato de playlist) + os 3 rótulos de Família na
sidebar (explicam que abrem o Mapa da Biblioteca, não óbvio só pelo
ícone 🗺). Resto da UI deixado como está — cobertura exaustiva não fazia
parte do pedido.

## 2026-08-29 — Exportar créditos de imagem
Nova função `af_exportarCreditosImagem()` (botão "↓ Descarregar
créditos_imagem.md" na tab Exportar) — gera uma tabela Markdown com
id/título/artista/fonte/crédito/licença/URL de origem de cada imagem em
uso no catálogo. Cobre TODAS as fontes (TheAudioDB, Wikimedia/Wikipedia
via `usarImagemWikimedia()`, pesquisa web geral, ficheiros manuais),
não só Wikimedia como o nome da função original sugeria. Só leitura,
nunca altera `catalogo.json`; download directo via `downloadBlob()`
(não é ficheiro de dados da app, não precisa do servidor de escrita).

Validado: `deno check` (exit 0); teste real em Chrome (interceptando
`downloadBlob` para inspecionar o conteúdo sem accionar o download) —
284/284 faixas com imagem exportadas correctamente, tabela com o
número certo de linhas.

## 2026-08-29 — "Anos 2010 — Synth II": discrepância encontrada + 2 bugs reais corrigidos
Pedido do utilizador dizia "faltam 6 faixas + mosaico" em
`STD.INT.10.SYN.002` — **não confirmado**: as 7 músicas e o Mosaico já
estavam todos completos em `playlists.json`/`catalogo.json`, com áudio
e imagem reais (confirmado local + carregamento real no jogo via
`COLLECTIONS['STD.INT.10.SYN.002']`, 7/7 faixas com Trecho A/B). Não
sei a origem da contagem "6 faltam" — nada no repositório a
documentava.

Ao verificar, encontrados e corrigidos **dois bugs reais** que nada
tinham a ver com a contagem de faixas:
1. **Mosaico (`arcade_fire_my_body_is_a_cage`) em formato errado** —
   tinha `trecho_a`/`trecho_b` separados (12s+10s) em vez de um único
   ficheiro contínuo de ~30s (regra 27.7, mesmo bug já visto e corrigido
   nas 6 playlists de 27 Ago) — `elegivel_mosaico` também estava
   `false`, inconsistente com ser mesmo usado como Mosaico. Regenerado
   como `arcade_fire_my_body_is_a_cage_full.mp3` (confirmado ~30s via
   `afinfo`), campos actualizados, ficheiros antigos removidos.
2. **Mosaico com "pessoa" errada** — `pessoa: "Samuel T. Herring"`
   (vocalista dos Future Islands) associado à faixa "My Body Is a
   Cage", que é dos **Arcade Fire**, sem ligação nenhuma a Herring —
   parece cópia do Mosaico de `STD.INT.10.SYN.001` (esse sim, uma
   faixa real dos Future Islands) sem actualizar o nome ao mudar de
   faixa. Corrigido para `"Win Butler"` (vocalista/compositor dos
   Arcade Fire, confirmado por pesquisa antes de aplicar).

Também adicionado `duracao_estimada` (estava ausente, tal como no seu
par `STD.INT.10.SYN.001`, não tocado — fora do âmbito deste pedido).

Nota independente já registada em `TASKS.md`: "My Body Is a Cage" é de
2007, usada numa playlist "Anos 2010" — décadas divergente, não
corrigida (decisão editorial, não um bug técnico).

Validado: JSON válido; `deno check` (exit 0, nenhum ficheiro `.html`
alterado); teste real em Chrome confirma a playlist completa (7/7 +
Mosaico) e o par pessoa/faixa do Mosaico agora coerente.

## 2026-08-29 — Revisão da Fototeca: faixas com imagem via fallback iTunes
Pedido do utilizador referia "10 faixas" — **discrepância encontrada e
reportada**: uma varrimento completo de `catalogo.json` (por
`imagem_fonte` a conter "itunes" E por URL em `mzstatic.com`/
`itunes.apple.com`) só encontra **4** faixas realmente marcadas via
iTunes: `pt80_04`, `pt80_06`, `bra001_mosaico`, `ptbat_mosaico`. Não há
registo de uma lista de 10 em nenhum ficheiro do projecto
(`TASKS.md`/`DECISIONS.md`/`STATUS.md`) — pode ser uma contagem antiga
de outra fonte não documentada aqui. Revistas as 4 encontradas:

- **`pt80_04`** (Trovante) e **`pt80_06`** (Fernando Tordo): imagem
  antiga era capa de álbum iTunes (`imagem_credito` já dizia
  explicitamente "não retrato do artista"), substituída por foto real
  via pesquisa web (`GET /buscar-imagens-cascata`, revista manualmente
  antes de aplicar) — Trovante: foto da banda (Diário de Coimbra, "50
  anos"); Fernando Tordo: retrato (Revista Rua).
- **`bra001_mosaico`** (Elis Regina & Adoniran Barbosa, dueto): mesma
  situação — substituída pelo retrato real de Elis Regina via
  TheAudioDB. Não foi encontrada nenhuma foto conjunta dos dois — fica
  documentado explicitamente no `imagem_credito` que só um dos dois
  artistas está representado.
- **`ptbat_mosaico`** (Alexandre Frazão): **imagem NÃO substituída** —
  já é uma foto real (baterista com t-shirt Zildjian, consistente com o
  seu patrocínio confirmado por pesquisa), só o `imagem_fonte` estava
  errado (dizia `itunes_artist`, mas `imagem_credito` já indicava
  upload manual) — corrigido para `manual`, `imagem_url_origem` posto a
  `null` (fonte original do ficheiro não está registada em lado
  nenhum).

Nenhuma das 4 estava marcada `imagem_licenca_estado: "livre"` — regra
de protecção respeitada, nada bloqueado. Todos os novos URLs
confirmados a carregar (HTTP 200) antes de aplicar.

## 2026-08-28 — Correcção de 2 gaps concretos da auditoria total (decadas vazio + imagem em falta)
Fora da lista de 10 pendências já enviada — pedido isolado sobre 2
achados específicos da Parte 1 (auditoria total):

- **`decadas: []` vazio corrigido (2 faixas)**, ano confirmado por
  pesquisa antes de aplicar:
  - `the_durutti_column_sketch_for_summer` → `["1980s"]` ("Sketch for
    Summer", 1980, álbum de estreia *The Return of the Durutti Column*,
    Factory Records).
  - `future_islands_seasons_waiting_on_you` → `["2010s"]` ("Seasons
    (Waiting on You)", single de 2014, álbum *Singles*) — consistente
    com o uso desta faixa nas playlists "Anos 2010 — Synth".
- **`beatles_05` ("Something (cover)", Tribute Beatles) — imagem
  associada**: sem imagem nenhuma antes; aplicada a mesma foto de banda
  já usada nas outras 5 posições "The Beatles" desta playlist
  (`beatles_01/02/03/04/06`, via `GET /buscar-imagem-artista?artista=The
  Beatles` — TheAudioDB, mesmo URL que as outras já tinham), por
  consistência editorial (o "cover" testa reconhecer a música dos
  Beatles, não o artista da versão cover, que fica genérico "Outro
  artista"). `imagem_licenca_estado: "confirmar"` — não havia imagem
  prévia marcada `"livre"` nesta faixa, nada a proteger.

**Reverificação das 3 imagens afectadas pelo rate-limit da Wikimedia**
(`solo_mosaico`, `bra001_03`, `hip_mosaico`): todas as 3 confirmadas a
carregar normalmente agora (HTTP 200, JPEG real, tamanhos plausíveis
245KB-1.9MB) — confirma que eram mesmo falsos positivos do rate-limit
temporário, sem nenhum problema real. Nada a corrigir.

Validado: `python3 -m json.tool`/JSON válido; `deno check` (exit 0) em
ambos os ficheiros (nenhum JS alterado nesta correcção, só
catalogo.json).

## 2026-08-28 — Parte 3: 4º tipo de Playlist "Vídeo" (Bíblia §29.2)
`STD.INT.ALL.CIN.001` ("Cinema & Música") reclassificada de
`tipo: "standard"` para `tipo: "video"` em `playlists.json` — só o
campo `tipo`, código/chave/id inalterados (não pedido). Correcção
associada em `catalogo.json`: `cinema_mosaico` ("The Godfather Theme",
Nino Rota) não tinha `video`/`clip`/`filme`/`compositor` nenhum (achado
na auditoria da Parte 1) — preenchido com
`https://www.youtube.com/watch?v=e2A27akHfAM` (vídeo oficial do tema,
confirmado por pesquisa), `filme: "The Godfather"`,
`compositor: "Nino Rota"`, igualando o padrão das outras 7 faixas da
playlist. Todas as 8 posições (7 + Mosaico) têm agora `video`.

`musicbox_studio.html`:
- Filtro de Tipo ganha a 4ª opção "Vídeo" (`<option value="video">`).
- `renderSidebar()`: nova secção "Vídeo" (grupo/render loop/
  `LABEL_TIPO`, ao lado de Solo/Retrato/Tributo).
- `expectedCount('video')` → 7 (mesma forma do Standard: 7 músicas +
  Mosaico), para a validação "N/7 posições" continuar a funcionar.
- Badge de tipo na Mesa de Montagem ganha estilo próprio
  (`.tipo-video`, vermelho) em vez de cair no estilo genérico "audio".
- Mapa da Biblioteca: `af_calcularMapaBiblioteca()`/`af_chipTipo()`/
  `af_renderCartaoUniverso()` passam a contar e mostrar chips "Vídeo"
  (dot vermelho, `.mapa-dot.vid`), incluídos também na legenda.
- Player/link de vídeo na Mesa de Montagem: **já existia** — cada
  posição com `t.video` preenchido mostra um botão "▶ YouTube"
  (`trackMetaHtml()`), não gated por tipo — funciona automaticamente
  para todas as 8 posições de Cinema & Música agora que têm o campo.

`musicbox.html`: nenhuma alteração necessária — `UNIVERSOS_EXTERNOS`
(onde Cinema está registada) é agnóstico a `tipo`, e a derivação de
Família/Universo já não dependia deste campo para playlists não-
Retrato. Confirmado que `COLLECTIONS.CINEMA` continua a carregar
normalmente (7 músicas + Mosaico, Família ESPECIAIS/Universo Cinema).

Validado: `deno check` (exit 0) em ambos os ficheiros; teste real em
Chrome via puppeteer-core (`_teste_tipo_video.js`, scratchpad) —
filtro Tipo=Vídeo devolve só `STD.INT.ALL.CIN.001`; secção "Vídeo" na
sidebar; cartão "Cinema" no Mapa mostra `1 playlist` + chip Vídeo;
Mesa de Montagem mostra badge "Video" (vermelho) e 8 botões
"▶ YouTube" (uma por posição); jogo real confirma `COLLECTIONS.CINEMA`
inalterado (7 músicas, Mosaico, Família ESPECIAIS). Screenshot em
scratchpad/tipo_video_montagem.png.

## 2026-08-28 — Parte 2: Escolha única por Ronda + Pontuação plana (Bíblia §10.10/§11.2)
`musicbox.html` — duas alterações às regras do motor:

- **Escolha única por Ronda**: `iniciarEscolhaCollection()` reescrita —
  P1=Blind Draw, P2=Motor (automático), P3=Escolha, P4=Motor, P5=Motor,
  por cada Ronda (`playlistNaRonda` 1-5), substituindo a lógica antiga
  em que o líder do ranking geral escolhia em 4 das 5 Playlists. P3 é
  decidida pelo vencedor de P2 (nova `vencedorMotorEscolha()`): mais
  pontos ganhos nessa Playlist especificamente, não o total acumulado;
  empate desempatado por menor tempo de resposta acumulado
  (`TEMPO_RESPOSTA_MOTOR_ESCOLHA`, alimentado em `acertouFaixa()` a
  partir do `tempoRestante` já existente). Estado armado no início de
  P2 (`PONTOS_ANTES_MOTOR_ESCOLHA` = snapshot de `pontos[]`), lido no
  início de P3.
- **Pontuação plana**: removida a excepção `PONTOS_FAIXA5` (5ª Faixa
  valia 200) — as 7 Faixas Regulares valem sempre `PONTOS_FAIXA` (100).
  `PONTOS_MOSAICO` (200) inalterado. (Ronda 4, sistema de € separado,
  não tocada — fora do âmbito deste pedido.)

Validado: `deno check` (exit 0); teste real em Chrome via
puppeteer-core (`_teste_motor_escolha.js`, scratchpad, usando as
funções reais do jogo — `iniciarEscolhaCollection`/`acertouFaixa`, não
mocks) — ciclo completo de uma Ronda (P1-P5): P1 "BLIND DRAW" auto-
seleccionou `STD.INT.50.MIX.001`; P2 "MOTOR" armou o rasto
correctamente; simulado concorrente 3 a ganhar +200 pts em P2 (2
faixas) contra concorrente 1 a ganhar +100 (1 faixa), apesar de
concorrente 1 ser o líder do ranking GERAL (600 vs 200 pts totais); P3
mostrou correctamente "Concorrente 3 ESCOLHE A FAMÍLIA" — confirma que
é o vencedor de P2, não o líder geral, que escolhe; P4 e P5 ambos
"MOTOR". Faixa 5 e Faixa 3 confirmadas a valer ambas exactamente +100.

## 2026-08-28 — Códigos de género reservados realinhados (JAZ/SOU/HIP/CLA)
Decisão do utilizador (ver DECISIONS.md): em vez de renomear as 4
playlists já publicadas, realinhados os códigos "reservados" no
Studio para corresponderem aos códigos reais já em uso —
`JZZ→JAZ`, `SOL→SOU`, `HHP→HIP`, `CLX→CLA` — nas 5 estruturas que os
usavam: `OPCOES_GENERO` (filtro de Género + modal "Propor Nova Chave"),
`CHAVE_GENERO_PARA_PALAVRAS` (usado por `criteriosDaChave`/
`faixaCorrespondeCriterios` para "Preencher automaticamente"),
`CHAVE_GENERO_PARA_QUERY` (constrói a frase de pesquisa a partir da
chave), `MIGRACAO_CHAVES` (mapping informativo no modal de migração) e
`montarPromptIA()` (lista de códigos válidos passada à IA ao gerar uma
playlist nova — evita que a IA volte a inventar um código diferente
para o mesmo género). `playlists.json` e os ids das 4 playlists reais
mantêm-se intocados, como pedido.

Validado: `deno check` (exit 0); teste real em Chrome via
puppeteer-core (`_teste_codigos_realinhados.js`, scratchpad) — filtrar
Género por JAZ/SOU/HIP/CLA encontra agora directamente
`STD.INT.ALL.JAZ.001`/`SOU`/`HIP`/`CLA` pela etiqueta dominante (antes
só apareciam via `universos_secundarios` explícito).

## 2026-08-28 — Etiquetas secundárias de Universo (Bíblia §27.14b)
Novo campo opcional `universos_secundarios` (array de nomes canónicos de
Universo, ex. `["Rock", "Anos 80"]`) em playlists.json — vazio/ausente
por omissão, sem preenchimento retroactivo das playlists existentes.
Só para uso interno no Studio; a etiqueta dominante (derivada do código
estruturado da playlist, como sempre) continua a ser a única mostrada
no ecrã de escolha do jogo.

- **Filtros do Studio**: `af_playlistPassaFiltros()` (Década/Género)
  passa a considerar também `universos_secundarios` — uma playlist
  aparece se QUALQUER etiqueta (dominante ou secundária) bater com o
  filtro. Novo `DEC_CODIGO_DO_NOME`/`GENERO_CODIGO_DO_NOME` (inverso de
  `DECADA_NOME`/`GENERO_UNIVERSO_*`) converte o nome canónico guardado
  em `universos_secundarios` para o código curto que os filtros usam.
- **Mapa da Biblioteca**: `af_calcularMapaBiblioteca()` agora também
  agrega referências secundárias por Universo; cartões "por criar" com
  pelo menos 1 referência secundária mostram uma nota subtil
  ("↳ N playlist(s) com esta etiqueta secundária"), sem contar para o
  X/N de cobertura, que continua baseado só na etiqueta dominante.
- **Jogo (musicbox.html)**: confirmado — o loader de `COLLECTIONS` só
  copia `nome, descritivo, playlistCodigo, universo, temBonus,
  dificuldade, musicas, mosaico` de cada playlist; `universos_secundarios`
  nunca é copiado, logo estruturalmente não pode chegar ao ecrã de
  escolha mesmo que esteja presente. Nenhuma alteração necessária ali.

**Aviso separado, não relacionado com esta funcionalidade**: ao
implementar a conversão nome→código, descobri que os 4 géneros criados
em 2026-08-28 (Jazz, Soul & R&B, Hip Hop, Clássica) usam nos seus
códigos reais `GENERO=JAZ/SOU/HIP/CLA`, que **não coincidem** com os
códigos reservados nas opções do filtro/modal "Propor Nova Chave"
(`JZZ`/`SOL`/`HHP`/`CLX`, ver `OPCOES_GENERO`). Isto significa que
filtrar a sidebar por Género "JZZ — Jazz" (por exemplo) não encontra
`STD.INT.ALL.JAZ.001` pela etiqueta dominante — só passa a aparecer via
`universos_secundarios` se alguém lhe atribuir explicitamente essa
etiqueta. Pré-existente a esta sessão de trabalho, não corrigido aqui
(decisão estrutural — renomear os códigos das 4 playlists reais
afectaria ids/ficheiros já publicados — fica para confirmação do
utilizador, ver DECISIONS.md).

Validado: `deno check` (exit 0) em ambos os ficheiros; teste real em
Chrome via puppeteer-core (`_teste_universos_secundarios2.js`,
scratchpad, tudo em memória — nada gravado em disco) — filtro Género=ROC
passou a incluir `STD.INT.90.DNC.001` com `universos_secundarios:
["Rock"]`; filtro Década=80 passou a incluir `STD.INT.ALL.HIP.001` com
`universos_secundarios: ["Anos 80"]`; cartão "Slot Local" simulado como
"por criar" com 1 referência secundária mostra correctamente a nota
"↳ 1 playlist com esta etiqueta secundária" sem contar como coberto.

## 2026-08-28 — 10 playlists novas: cobertura total dos 28 Universos (4 Décadas + 6 Géneros)
Confirmado primeiro, via Mapa da Biblioteca + `playlists.json` directo,
que só faltavam 4 Décadas (Anos 50/60/2000/2020 — "Anos 70" já estava
coberta por `STD.INT.70.ROC.001`) e 6 Géneros (Jazz, Blues, Soul & R&B,
Hip Hop, Clássica, Latin) = 10 playlists, não 12.

Criadas as 10 via pipeline real (`/gerar-faixa` + iTunes,
`/buscar-imagem-artista`), mesmo padrão de 27 Ago: 7 faixas + Mosaico
contínuo de 30s por playlist, `duracao_estimada` preenchida, verificação
prévia da regra 27.8b (máx. 3 playlists/artista) contra a Biblioteca
real antes de escolher as faixas. **100% de sucesso em 80/80 faixas**
(áudio + imagem), zero falhas, zero violações da regra 27.8b (Eagles,
Michael Jackson e agora também Taylor Swift ficam exactamente no limite
de 3 — dentro da regra). Commit + push individual por playlist, `0 0`
confirmado 10 vezes:
- `13dfd98` Anos 50 — As Origens do Rock
- `250bb0f` Anos 60 — Revolução Sonora
- `065eb31` Anos 2000 — Viragem do Milénio
- `5c76396` Anos 2020 — A Geração Streaming
- `38ba68d` Jazz — Standards Essenciais
- `fcb96a1` Blues — Raízes do Delta
- `99ae16f` Soul & R&B — A Voz da Alma
- `8bc383e` Hip Hop — Do Bronx ao Mundo
- `4c7bdd5` Clássica — Grandes Compositores
- `e10c10b` Latin — Ritmos do Mundo Latino

**Bug encontrado e corrigido no fim (`0d720c4`)**: `af_universoDePlaylist()`
em `musicbox_studio.html` não conhecia os 6 novos códigos de género
(JAZ/BLU/SOU/HIP/CLA/LAT) — devolvia `universo: null` para essas
playlists, fazendo o Mapa da Biblioteca mostrar Géneros 7/13 em vez de
13/13 (a Família continuava correta, só faltava o mapeamento ao
Universo específico). `GENERO_FAMILIA` em `musicbox.html` já tinha
fallback seguro (sempre GÉNEROS por omissão), mas os códigos foram
adicionados lá também por consistência. Confirmado após a correcção,
via puppeteer-core em Chrome real: **Mapa da Biblioteca mostra 28/28
Universos cobertos** (Décadas 8/8, Géneros 13/13, Especiais 7/7); jogo
real confirma as 10 playlists carregadas via auto-discovery com família
correta. `deno check` (exit 0) em ambos os ficheiros no fim de tudo.

## 2026-08-28 — Correcção estrutural ao bug do auto-save (verificação de versão antes de escrever)
Pedido do utilizador, bloqueante para a criação das 12 playlists em
falta para cobertura total de Décadas/Géneros. Antes: a cada 60s,
`exportPlaylists()` sobrescrevia `playlists.json` incondicionalmente com
o estado em memória da aba, mesmo que o ficheiro em disco tivesse
mudado entretanto (outra aba, edição directa, fusão automática) — causa
de perdas de dados já documentadas nesta sessão (LOGO-001, imagens da
"Never Sleep Again").

Agora: `_servidor_escrita.py` ganha `GET /versao?ficheiro=X` (devolve o
`mtime` actual em disco) e `POST /escrever?...&esperado_mtime=...`
(recusa com 409 se o mtime actual não bater com o esperado — comparação
atómica do lado do servidor, sem janela de corrida entre um GET e um
POST separados). `musicbox_studio.html` guarda o mtime em
`AF_VERSAO_PLAYLISTS` ao carregar (`loadData()`) e a cada escrita bem
sucedida. Numa escrita AUTOMÁTICA em conflito: cancela, mostra um aviso
persistente no topo da página (não desaparece sozinho — só ao recarregar
ou ao guardar manualmente com sucesso) e não sobrescreve nada, nem
sequer os fallbacks (File System API/Blob). Numa escrita MANUAL
("↓ Guardar playlists.json") em conflito: mostra um modal a pedir
confirmação explícita ("Substituir mesmo assim") antes de prosseguir.

Validado: `python3 -m py_compile _servidor_escrita.py` e `deno check`
sobre o `<script>` de `musicbox_studio.html` (exit 0); teste real em
Chrome via puppeteer-core (`_teste_conflito_autosave.js`, scratchpad) —
simulou uma alteração externa real ao ficheiro em disco (mtime + conteúdo
diferentes) e confirmou: (1) escrita automática recusada, aviso
persistente visível, ficheiro no disco continua com a versão externa
(não sobrescrito às cegas); (2) escrita manual abre o modal de
confirmação; (3) "Cancelar" mantém o ficheiro intacto; (4) "Substituir
mesmo assim" escreve com sucesso e sincroniza `AF_VERSAO_PLAYLISTS` com o
novo mtime. `playlists.json` reposto ao estado original no fim do teste
(`git diff` confirma zero alterações residuais).

## 2026-08-28 — Sidebar do Studio colapsável + Mapa da Biblioteca (substitui a reorganização Família→Tipo anterior)
Instrução anterior (agrupar a sidebar por Família→Tipo como estrutura
primária) foi **anulada** pelo utilizador. Reposta a estrutura anterior
(Tipo→Década, ex. "Standard > Anos 70 > Anos 70 — Rock", commit
`7fb6f40~1`) para a lista completa de playlists, agora atrás de um
toggle colapsável (`AF_SIDEBAR_PLAYLISTS_EXPANDIDO`, persistido em
`localStorage['af_sidebar_playlists_expandido']`). Por omissão a
sidebar só mostra os filtros existentes (inalterados) + os 3 rótulos de
Família (DÉCADAS/GÉNEROS/ESPECIAIS) + o toggle "▾ Ver todas as
playlists (N)" — sem a lista completa visível, como pedido. Se houver
filtros/pesquisa activos, a lista aparece automaticamente mesmo
colapsada (para os filtros nunca ficarem "invisíveis").

Novo "Mapa da Biblioteca" (modal `#modal-mapa-biblioteca`, aberto ao
clicar num rótulo de Família): fluxograma raiz "MUSIC BOX — BIBLIOTECA"
→ 3 colunas (Décadas/Géneros/Especiais), cada uma com barra de
progresso e um cartão por Universo canónico (lista fixa dos 28 do Cap.
7.10 — `UNIVERSOS_CANONICOS`), calculado dinamicamente a partir de
`playlists.json` real via `af_universoDePlaylist()` (mesma lógica de
derivação de código estruturado das Partes 1/2 anteriores, agora também
devolvendo o Universo específico, não só a Família). Cartão com
playlist(s): selo dourado/verde com a contagem + chips por Tipo
(Standard/Retrato/Tributo); sem nenhuma: selo tracejado "por criar".
Clicar num cartão coberto chama `af_focarUniverso()` — fecha o modal,
expande a sidebar e restringe a lista às playlists desse Universo
(`AF_UNIVERSO_FOCO`), com os filtros existentes do Studio continuando a
aplicar-se por cima (chip "Universo: X ✕" para limpar o foco; "Limpar
filtros" também o remove). Estética reaproveitada das variáveis CSS já
existentes do Studio (`--bg`/`--bg2`/`--bg3`, `--accent` dourado,
`--mono`), não copiadas do protótipo de referência fornecido pelo
utilizador (usado só para orientação de layout).

Números reais calculados nesta sessão (2026-08-28): Décadas 4/8, Géneros
7/13, Especiais 7/7 — total 18/28 Universos cobertos, 26 playlists.
Validado: `deno check` (exit 0); teste real em Chrome via puppeteer-core
(`_teste_sidebar_colapsavel.js` + `_teste_persistencia.js`, scratchpad)
— confirma o estado colapsado por omissão, a expansão manual mostrando
exactamente "Standard > Anos 70 > Anos 70 — Rock", persistência via
localStorage sobrevivendo a um reload real da página, abertura do Mapa
com os números acima, e o fluxo completo de foco num Universo (cartão
"Rock" → sidebar restringe a `STD.INT.ALL.ROC.001` +
`TRB.UK.ALL.ROC.001`, as 2 playlists reais desse Universo). Screenshot em
scratchpad/mapa_biblioteca.png.

## 2026-08-28 — Parte 3: playlistCodigo em falta corrigido (5 playlists)
Varrimento completo de `playlists.json` encontrou 5 playlists sem o
campo `playlistCodigo` (causa do "(undefined)" no ecrã "Testar uma
Playlist"): `STD.INT.ALL.MIX.001` (Ambient & Introspectivo),
`STD.INT.10.SYN.001`/`STD.INT.10.SYN.002` (Anos 2010 — Synth/Synth II,
os dois casos "Anos 2010 — Synth" reportados), `STD.INT.70.ROC.001`
(Anos 70 — Rock, reportado), e `STD.INT.90.DNC.001` (Never Sleep Again:
A Club Anthem Odyssey, o caso original que motivou a Parte 3). Corrigido
em todas com `playlistCodigo` = a própria chave do objecto — mesma
convenção usada nas outras 21 playlists já correctas. Validado: JSON
continua válido (`python3 -m json.tool`); teste real em Chrome via
puppeteer-core (`_teste_playlistcodigo.js`, scratchpad) — 0 botões com
"undefined" no ecrã "Testar uma Playlist" (antes eram pelo menos os 4
reportados pelo utilizador), e as 4 playlists reportadas mostram agora o
código correcto.

## 2026-08-28 — Parte 2: removida restrição de Ronda para a família ESPECIAIS
`musicbox.html`: removida a regra "Especiais só a partir da Ronda 2"
(bíblia 3.2.1, já revogada pela Bíblia actualizada — 7.10/27.12). O ecrã
de escolha de família (Passo 1 de 2) mostra agora sempre 3 opções —
DÉCADAS/GÉNEROS/ESPECIAIS — desde a Playlist 1 da Ronda 1.
`FAMILIA_COLECAO` (mapa estático, só cobria 14 chaves legadas — as 12
playlists descobertas automaticamente de playlists.json ficavam
invisíveis no selector de família) substituído por `familiaDeChave()` +
`familiaDeUniversoCodigo()`, que derivam a família a partir do código
estruturado da playlist (mesma lógica de `af_familiaDePlaylist()` do
Studio, Parte 1). Validado: `deno check` (exit 0); teste real em Chrome
via puppeteer-core (`_teste_familia_jogo.js`, scratchpad) — Ronda 1,
Playlist 2: os 3 botões de família aparecem todos activos (nenhum
`disabled`); clicar em ESPECIAIS mostra os universos reais (Retrato
Sonoro, Geografia, Logótipos, Televisão, Ativadores Psicológicos, etc.),
sem cair no fallback "pool toda" nem em erro de página. Screenshot em
scratchpad/familia_especiais_ronda1.png.

## 2026-08-28 — Parte 1: sidebar do Studio reorganizada por Família (DÉCADAS/GÉNEROS/ESPECIAIS)
`renderSidebar()` em `musicbox_studio.html` reescrita para agrupar
primeiro por Família (nova função `af_familiaDePlaylist`), depois por
Tipo (Standard/Retrato/Tributo), depois lista as playlists. Ver
DECISIONS.md 2026-08-28 para a lógica completa de classificação.
Validado: `deno check` (exit 0) sobre o `<script>` extraído; teste real
em Chrome via puppeteer-core (`_teste_sidebar_familia.js`, scratchpad) —
confirma as 26 playlists agrupadas correctamente (DÉCADAS: 6, GÉNEROS: 10,
ESPECIAIS: 10) e que o filtro "Tipo = Retrato" continua a funcionar por
cima da nova estrutura (devolve exactamente as 3 playlists Retrato,
espalhadas por 2 famílias diferentes — Vozes Lendárias/Portuguesas e
Logótipos, todas em ESPECIAIS). Screenshot em
scratchpad/sidebar_familia.png.

## 2026-08-27 — "Bateria Portuguesa" reclassificada para o universo "Solistas"
`STD.PT.ALL.BAT.001` tinha `universo: "Geografia"` apesar de ser
conceptualmente uma playlist de Solo de Bateria, tal como a internacional
(`STD.INT.ALL.BAT.001`) — causa raiz de as suas 7 faixas terem `artista` =
banda em vez do baterista. Corrigido `universo` para `"Solistas"` em
`playlists.json` e no literal `COLLECTIONS.PT_BAT` de `musicbox.html`
(sobreposto em runtime pelo `playlists.json`, mas actualizado por
consistência de código-fonte). Não muda a "família" mostrada no ecrã de
escolha de playlist do jogo (continua `FAMILIA_GENEROS`, mapeamento
separado do `universo`).

Das 7 faixas (`ptbat_01`–`07`), 5 tiveram `artista` corrigido para o
baterista real (confirmado por texto sourced da Wikipedia PT, não por
memória): `ptbat_02` Kalú/Xutos & Pontapés, `ptbat_03` Tóli César
Machado/GNR, `ptbat_04` Kinörm/Ornatos Violeta, `ptbat_06` Hélio
Morais/Linda Martini, `ptbat_07` Salvador Seabra/Capitão Fausto — todas
com `banda` preenchido, mesmo padrão de `solo_*`/`bat_*`. Nenhuma tem foto
da pessoa disponível (TheAudioDB/Wikipedia/Wikimedia Commons sem
resultado para nenhum dos 5 nomes) — ficou a foto da banda, com
`imagem_risco_ambiguidade: true`.

`ptbat_01` (UHF) e `ptbat_05` (RAMP) ficaram deliberadamente por
confirmar — identidade do baterista específico não determinável com
confiança a partir da Wikipedia (múltiplos bateristas sem datas claras).
`artista` mantido como a banda, `imagem_risco_ambiguidade: true` +
`nota_curadoria` novo campo a explicar o motivo. Detalhe em `TASKS.md`
("Pendente (sessão 2026-08-27)").

`af_verificarConsistenciaArtistaBanda()` (Studio, aba ASSETS) corrida
antes e depois — 0 faixas sinalizadas depois da reclassificação.

## 2026-08-21 — 5 modos de geração em "Gerar com IA" (URL/Tema/Categoria/Semente múltipla/Playlist YouTube)
Além do modo URL já existente: **Tema/Mood** (texto livre), **Categoria**
(Década+Geo+Género fixos), **Semente múltipla** (até 3 título+artista,
todos entram como faixas fixas), **Playlist YouTube** (novo endpoint
`POST /listar-playlist-youtube` — `yt-dlp --flat-playlist`, nunca
descarrega áudio — lista editável, usada só como contexto/artistas
proibidos, nunca como faixas fixas). Tudo centralizado em
`af_infoModoGeracaoIA()`; `montarPromptIA`/`af_musicasIAComSemente`/
`af_detectarArtistasRepetidos`/retentativas generalizados para todos os
modos sem duplicar lógica. Prompt ganhou também regra explícita: a pessoa
do mosaico não pode ser membro conhecido de nenhuma banda já nas 7 faixas
(ex. Ian Curtis/Joy Division) — só regra de prompt, não validada
algoritmicamente (limitação conhecida, documentada).

26 testes isolados (todos os modos) + endpoint novo testado ao vivo + um
teste real contra a API Anthropic que apanhou uma repetição genuína de
artista gerada pela IA ("Joy Division" 2x), confirmando que a validação é
mesmo necessária. `deno check`/`py_compile` sem erros. **Falta testar no
browser** o fluxo de UI completo — ver `TASKS.md`. Detalhe em
`DECISIONS.md`.

## 2026-08-21 — Feedback ao vivo na Mesa de Montagem durante geração de trechos
Corrigido: depois de "Ver na Mesa de Montagem", não havia nenhum feedback
visual do progresso. Agora mostra contador no topo ("3/7 trechos gerados")
+ estado por faixa (a gerar…/pronto/falhou), ao vivo. Corrigido também um
bug introduzido na funcionalidade anterior: `af_verMontagemAgora()` limpava
a variável que ligava a Mesa de Montagem ao lote em curso — separada em
duas variáveis (`AF_NAVEGACAO_JA_FEITA` vs `AF_CHAVE_PLAYLIST_EM_PROGRESSO`).
`deno check` sem erros. Detalhe em `DECISIONS.md`.

## 2026-08-21 — ~/.zshrc limpo (tinha 6 linhas ANTHROPIC_API_KEY conflituosas)
Fora do repositório, mas registado por relevância: `~/.zshrc` tinha 6
linhas `export ANTHROPIC_API_KEY=...` acumuladas (4 placeholders nunca
preenchidos + 2 chaves reais diferentes). Perguntado ao utilizador antes
de limpar — confirmado usar a chave da sessão actual. Reduzido a uma única
linha; backup em `~/.zshrc.bak-20260821-171759`. Detalhe em `DECISIONS.md`.

## 2026-08-21 — Painel de progresso estruturado + prompt mais restritivo + fallback claro (Gerar com IA)
Texto cinzento simples da tab "✦ Gerar com IA" substituído por um painel
estruturado (`#np-ia-progresso`, `af_renderProgressoIA`): mostra a fase
actual, tentativas de substituição por artista repetido, e estado por
faixa (○ pendente/◐ a gerar/✓ pronto/✗ falhou) com contagem "X/Y trechos
gerados". Para isto aparecer mesmo "no modal" durante a geração dos
trechos A/B (que só corre depois de "Criar playlist"), `createPlaylist()`
deixou de fechar o modal logo nesse caso — fica aberto a mostrar o
progresso, com um botão "→ Ver na Mesa de Montagem" para quem não quiser
esperar. Prompt (`montarPromptIA`) e o corretivo de retentativas ganharam
uma frase explícita a proibir o artista da semente nas 6 faixas. Fallback
após 3 tentativas falhadas por artista repetido deixou de mostrar o prompt
para copiar/colar — mostra directamente "Não foi possível gerar
automaticamente — tenta outra semente." (o outro fallback, por falha de
rede/servidor, continua a mostrar o prompt, sem alteração).

Testado isoladamente (fora do browser) o `af_renderProgressoIA` com 5
estados diferentes, incluindo confirmação de escape correcto de
`<script>`/aspas em título/artista. Validado com `deno check`. **Falta
testar no browser** o fluxo completo — ver `TASKS.md`. Detalhe em
`DECISIONS.md`.

## 2026-08-21 — `ATUALIZAR.command` actualizado (porta 8000 + caminho antigo + ficheiro antigo)
`iniciar_studio.command`/`iniciar_musicbox.command` já estavam ambos em
8002 (não precisaram de correcção). Encontrado um terceiro script,
`ATUALIZAR.command`, ainda com `$HOME/MusicBox/app` (caminho antigo),
`$HOME/Descargas` (pasta que não existe neste Mac) e porta 8000 +
`episodio_piloto2.html` (versão antiga do ficheiro). Corrigido, com
confirmação do utilizador: caminho dinâmico, `$HOME/Downloads`, alvo
actualizado para `musicbox.html`, e passou a reaproveitar
`_servidor_escrita.py` (porta 8002) só arrancando se não estiver a correr
— já não mata/reinicia o servidor a cada execução. Validado com `bash -n`.
Detalhe em `DECISIONS.md`.

## 2026-08-21 — Nenhum artista repetido na playlist gerada por IA (mosaico incluído)
Validação nova: playlist gerada por IA é rejeitada se algum artista se
repetir entre as 7 faixas principais ou com o mosaico (`artista` E
`pessoa` do mosaico contam). Fluxo automático (`af_gerarFaixasIAServidor`)
tenta corrigir sozinho pedindo à IA para substituir, até 3 tentativas
(`af_montarPromptCorretivoArtistaRepetido`); se não resolver, não importa
— pré-preenche "Colar resposta JSON" com a última resposta para corrigir à
mão. Fluxo manual rejeita da mesma forma em `af_aplicarResultadoIA`.
`af_normalizarArtista` reaproveita `afSlug()` já existente. Testado
isoladamente (fora do browser) com casos sintéticos — todos a passar; não
ignora artigos ("The Beatles" ≠ "Beatles", limitação conhecida). Validado
com `deno check`. **Falta testar no browser** o fluxo real com chamada à
API — ver `TASKS.md`. Detalhe em `DECISIONS.md`.

## 2026-08-21 — `iniciar_musicbox.command` recriado para porta 8002
Estava apagado da árvore de trabalho desde antes desta sessão (`git
status` já mostrava `D iniciar_musicbox.command`). Recriado do zero (não
restaurado do `HEAD` antigo, que apontava para `~/MusicBox/app`/porta
8000/Chrome incógnito — desactualizado) para abrir
`http://localhost:8002/musicbox.html` via `_servidor_escrita.py`, mesmo
padrão do `iniciar_editor.command` mas sem `auto_fusao.sh`/
`_servidor_librosa.py` (específicos do Studio). `chmod +x` aplicado.
`iniciar_studio.command` não existe — `iniciar_editor.command` já cumpre
esse papel, já actualizado para 8002 mais abaixo nesta página. Validado
com `bash -n`. Detalhe em `DECISIONS.md`.

## 2026-08-21 — "Identificar + Gerar" chama /gerar-faixas directamente (sem copiar/colar)
O botão "🔍 Identificar + Gerar" (modal Nova Playlist, tab IA) deixou de só
mostrar o prompt para copiar/colar em claude.ai — agora chama `POST
/gerar-faixas` directamente e importa o resultado automaticamente
(`af_gerarFaixasIAServidor` → `af_aplicarResultadoIA`, extraído de
`importarResultadoIA`). Se o servidor falhar, cai para o fluxo manual
antigo (prompt + colar resposta), que continua disponível. Substitui a
decisão de 2026-08-13 de manter esse endpoint por usar. Validado com
`deno check`. **Falta testar no browser** com `ANTHROPIC_API_KEY`
definida — ver `TASKS.md`. Detalhe em `DECISIONS.md`.

## 2026-08-21 — Filtros rápidos + pesquisa na sidebar de Playlists
Adicionados à sidebar "Playlists": pesquisa por nome + filtros Década/
Género/Geo/Dificuldade/Tipo/Estado, todos combinando por E lógico.
Década/Género/Geo vêm da chave estruturada da playlist; Estado é derivado
(`af_playlistEstado` — não existe campo próprio, "pronta" = todas as
posições preenchidas e nenhuma faixa referenciada em 'rascunho' no
catálogo). Botão "Limpar filtros" só aparece com algum filtro activo.
Validado com `deno check`. **Falta testar no browser** — ver `TASKS.md`.
Detalhe em `DECISIONS.md`.

## 2026-08-21 — Geração automática de trechos A/B após "Gerar com IA" com semente do YouTube
Quando "Criar playlist" converte o resultado da tab "✦ Gerar com IA" em
faixas-rascunho e a semente veio de um URL do YouTube (não só texto livre
no campo semente), `createPlaylist()` dispara automaticamente, em segundo
plano, `POST /gerar-faixa` para cada faixa gerada (6 sugestões + semente +
mosaico), sempre por artista+título — sem confirmação por faixa, o
utilizador só valida no final na Mesa de Montagem. Sem semente do YouTube,
continua a exigir o botão manual "⬇ Gerar trechos" por faixa, como antes.

Novas funções em `musicbox_studio.html`: `af_gerarTrechoCore` (núcleo
extraído de `gerarTrechosViaServidor`, que passou a chamá-lo — botão manual
sem alterações de comportamento) e `af_gerarTrechosAutomaticoIA` (corre em
sequência, nunca em paralelo; aborta o lote se o próprio servidor não
responder, mas continua se só uma faixa falhar a gerar). `NP_IA_RESULTADO`
ganhou o campo `sementeYoutubeUrl`. Detalhe completo em `DECISIONS.md`.

Validado com `deno check` sobre o bloco `<script>` — sem erros de sintaxe.
**Falta validação no browser** (sem acesso a browser real neste ambiente):
gerar uma playlist via IA com um URL real do YouTube como semente e
confirmar que os trechos A/B aparecem de facto, sem intervenção manual, na
Mesa de Montagem (ver `TASKS.md`).

## 2026-08-21 — `ORIGEM_PERMITIDA` e `iniciar_editor.command` para 8002
`_servidor_escrita.py`: `ORIGEM_PERMITIDA` mudou de `http://localhost:8000`
para `http://localhost:8002`. `iniciar_editor.command`: já não arranca
`python3 -m http.server 8000` (redundante desde o `do_GET`, ver abaixo); o
`open` final passa a abrir `http://localhost:8002/musicbox_studio.html`.
Não existe `iniciar_studio.command` — o script actual chama-se
`iniciar_editor.command`, confirmado por pesquisa em todo o repositório.

**Atenção — servidor real interrompido durante o teste:** ao validar esta
alteração, `pkill -f "_servidor_escrita.py"` matou sem querer um processo
`_servidor_escrita.py` que já estava a correr (não o de teste, que falhou
a arrancar por a porta já estar ocupada). Se tinhas o Studio aberto a
depender dele, reinicia com `./iniciar_editor.command` ou `python3
_servidor_escrita.py`. Porta 8002 confirmada livre, sem processos
pendurados. Detalhe em `DECISIONS.md`.

## 2026-08-21 — `do_GET` em `_servidor_escrita.py`: ficheiros estáticos na porta 8002
Adicionado `do_GET` a `app/_servidor_escrita.py`, a pedido do utilizador,
para servir os ficheiros estáticos de `app/` (HTML, JSON, imagens, áudio)
directamente na porta 8002 — a app deixa de precisar de `python3 -m
http.server` na porta 8000 em paralelo para ser vista no browser. Protecção
contra path traversal (`os.path.realpath` + verificação de que o caminho
fica dentro de `APP_DIR`, 403 caso contrário), `Content-Type` via
`mimetypes.guess_type`, 404 para ficheiros inexistentes. Endpoints `POST`
existentes (`/escrever`, `/upload`, `/gerar-faixas`, `/gerar-faixa`) não
foram tocados. Detalhe completo em `DECISIONS.md` — incluindo o que ficou
por fazer (referências a `http://localhost:8000` ainda presentes em
`musicbox_studio.html`, não alteradas por não terem sido pedidas).

Validado com `python3 -m py_compile` e testado com `curl` a correr o
servidor real: GET a ficheiros existentes → 200 com Content-Type correcto;
GET a ficheiro inexistente → 404; path traversal (`../`) → 403; `POST
/escrever` confirmado sem regressão.

## 2026-08-13 — `_servidor_escrita.py` (porta 8002)
Novo servidor local (`app/_servidor_escrita.py`, stdlib puro) que passa a
ser a via principal de "Guardar playlists.json" no Studio — escreve
directamente em `app/` sem pedir autorização de pasta no browser (a File
System Access API pedia-a a cada refresh; detalhe completo em
`DECISIONS.md`). `iniciar_studio.command` arranca-o em background na porta
8002. Validado com `curl` (whitelist de ficheiros, JSON inválido, escrita
real com verificação de `md5`, CORS) e `deno check`/`py_compile` — sem
acesso a browser real neste ambiente, por isso falta confirmação visual no
Studio (ver `TASKS.md`).

## Estado geral do projecto
Aplicação web para gestão de catálogo musical, episódios, blocos de áudio, chaves e integração com a API do MusicBrainz (ver `CLAUDE.md`).

## Tarefa em curso
Nenhuma de momento — ver `TASKS.md` para "Próximas tarefas".

## Alterações realizadas nesta sessão
Em `app/musicbox_studio.html`, na mesa de montagem (Montagem):
- Novo botão "⏱ Definir início" nas posições com faixa atribuída (slots simples e posições de tributo), junto ao nome/artista da faixa.
- Ao clicar, abre um mini-painel inline. **Só tem o campo Início (s)** — `trecho_a.fim` é calculado automaticamente como `início + 15s` (`TIMING_DURACAO_FIXA`), sem campo próprio nem validação de duração mínima (a versão anterior tinha campo Fim + validação de 15s mínimos; ambos foram removidos a pedido do utilizador por já não fazerem sentido com a duração fixa).
- Ao guardar, actualiza `trecho_a.inicio`/`trecho_a.fim` do CATALOGO em memória e a posição faz refresh, mostrando a etiqueta **"A: 20s"** (só o início, sem o fim).
- Novas funções: `timingLabelHtml`, `toggleTimingEditor`, `timingEditorHtml`, `saveTimingEditor`, `exportCatalogoPatch`. Novo estado: `timingEditorSlot`, `CATALOGO_PATCH`.
- `exportPlaylists()` passa a descarregar também `catalogo_patch.json` (array com as entradas de faixa modificadas nesta sessão) sempre que houver alterações pendentes ao catálogo, além do `playlists.json` habitual.
- CSS: `.timing-row`, `.timing-btn`, `.timing-editor` (+ `input[type=number]`), `.meta-tag.timing`. CSS de validação (`.timing-error`, `input.invalid`) foi removido junto com a validação.

Também actualizados `TASKS.md` (tarefa concluída) e `DECISIONS.md` (registo da exceção arquitetural: esta funcionalidade altera CATALOGO em memória, o que contraria o ponto 1 do cabeçalho do ficheiro — decisão documentada, não escreve `catalogo.json` em disco).

Criado `app/REGRAS_OPERADORES.md` — compilação de regras editoriais e técnicas para operadores do Studio, uso interno (destino confirmado com o utilizador: equipa, não licenciados). Reúne regras já existentes em `CODIGOS.md`, `DECISIONS.md`, `validar_catalogo.py`, `SESSAO_2026_08_10.md` e no cabeçalho de `musicbox_studio.html` — não inventa regras novas.

**Divergência resolvida** (registada em `DECISIONS.md`, 2026-08-10): confirmado pelo utilizador que todas as playlists têm exactamente 8 posições, independentemente do tipo — no "tributo" a flexibilidade é o tipo de conteúdo de cada posição, não a quantidade. O validador estava correcto; corrigido o cabeçalho de arquitetura em `musicbox_studio.html` (ponto 2) e `app/REGRAS_OPERADORES.md` §1.4 para reflectir isto.

Dois novos botões na mesa de montagem, abaixo da posição 01 quando esta tem faixa atribuída:
- **"Preencher com este artista"** (só `retrato`): pesquisa no CATALOGO faixas com o mesmo artista (interseção do array `artista`), ordena por menor década, preenche `musicas[1..7]`. Nunca toca na posição 01. Notifica "X faixas encontradas para [artista]". Novas funções: `menorDecada`, `preencherComArtista`. CSS: `.fill-artista-btn`.
- **"Preencher automaticamente"** (`standard`/`retrato`/`tributo`): deriva critérios de geografia/década/género a partir da **chave** da playlist (não existem esses campos directamente em `playlists.json` — decisão confirmada com o utilizador) e ordena por `nivel` (mais fácil primeiro). Em `tributo` só mexe em posições `tipo:"audio"`; em `standard` só preenche `musicas` (não o mosaico). O mapeamento GENERO→subgéneros do catálogo é uma aproximação por substring, não uma tabela oficial — sinalizado como heurística em `DECISIONS.md` e `REGRAS_OPERADORES.md`. Novas funções: `criteriosDaChave`, `faixaCorrespondeCriterios`, `preencherAutomaticamente`; novas tabelas `CHAVE_GEO_PARA_GEOGRAFIA`, `CHAVE_DEC_PARA_DECADA`, `CHAVE_GENERO_PARA_PALAVRAS`. CSS: `.fill-auto-btn`.

`DECISIONS.md` e `app/REGRAS_OPERADORES.md` (§1.4, §2.4) actualizados com ambas as funcionalidades.

**Novos ficheiros:** `app/auto_fusao.sh`, `app/_fundir_catalogo.py`, `app/iniciar_studio.command` (este último não existia — criado porque era o pedido: `auto_fusao.sh` "iniciado pelo iniciar_studio.command"). `iniciar_studio.command` arranca o servidor local, inicia `auto_fusao.sh` em background (destacado do Terminal via `nohup`+`disown`) e abre o browser.

`auto_fusao.sh` monitoriza `~/Downloads/catalogo_adicionar.json` (loop de 2s) e funde-o automaticamente em `catalogo.json`, apaga o ficheiro de Downloads e imprime `"Fundido: X faixas"` — **única fusão automática (sem revisão manual) de todo o projecto**, pedida explicitamente pelo utilizador; todo o resto continua "download + fusão manual obrigatória". Por ser a única excepção e por apagar o ficheiro de origem, foram acrescentadas protecções não pedidas mas necessárias: nunca sobrescreve `id` já existente, só apaga o ficheiro após fusão bem sucedida (JSON inválido fica em Downloads para inspecção), faz backup timestamped de `catalogo.json` em `app/backups_catalogo/` antes de cada escrita, espera o ficheiro estabilizar antes de o ler, regista tudo em `app/auto_fusao.log`, e usa lockfile para não correr duas instâncias em simultâneo. Detalhe completo em `DECISIONS.md`.

## Validado
- `deno check` sobre o bloco `<script>` extraído de `musicbox_studio.html` — sem erros de sintaxe (exit 0), repetido após cada alteração desta sessão.
- `auto_fusao.sh`/`iniciar_studio.command` validados com `bash -n`; `_fundir_catalogo.py` com `python3 -m py_compile` — sem erros.
- `_fundir_catalogo.py` e o loop completo de `auto_fusao.sh` testados de ponta a ponta em ambiente isolado (pasta `Downloads`/`catalogo.json` falsas, não os ficheiros reais): faixa nova é fundida e o ficheiro de origem é removido; `id` duplicado é ignorado com aviso; entrada sem `id` é ignorada; JSON inválido não é apagado nem funde nada. Confirmado que não ficou nenhum processo de teste pendurado.
- Não foi possível testar no browser nesta sessão (sem acesso a servidor HTTP local) — recomenda-se testar manualmente: `python3 -m http.server` na pasta `app/`, e validar em concreto: (1) o painel "Definir início" só com campo Início; (2) "Preencher com este artista" numa playlist Retrato; (3) "Preencher automaticamente" numa playlist standard, numa retrato e numa tributo (incluindo o caso de posições tributo não-audio ficarem intocadas); (4) qualidade real das correspondências de género (heurística por substring pode ter falsos positivos); (5) `iniciar_studio.command` a correr de facto por duplo-clique no Finder (só foi corrido via `bash -n`, nunca invocado como duplo-clique real).

## Problemas encontrados
- Falta validação manual no browser de todas as funcionalidades desta sessão (ver acima).
- `iniciar_studio.command` nunca foi corrido como duplo-clique real no Finder — só validado sintaticamente. Recomenda-se um primeiro arranque supervisionado antes de confiar nele sem vigilância.

## Concluído (histórico, ver TASKS.md)
- [x] Estrutura inicial do Studio
- [x] Catálogo musical
- [x] Sistema de Chaves [TIPO].[GEO].[DEC].[GENERO].[VOL] (2026-08-10)
- [x] Botão "Definir início" para trecho_a.inicio na mesa de montagem (2026-08-10)
- [x] Compilação de regras editoriais e técnicas para operadores — `app/REGRAS_OPERADORES.md`, uso interno (2026-08-10)
- [x] Resolvida divergência standard/retrato/tributo: todas as playlists têm exactamente 8 posições (2026-08-10)
- [x] Botão "Preencher com este artista" (Retrato) na mesa de montagem (2026-08-10)
- [x] Botão "Preencher automaticamente" (qualquer tipo) na mesa de montagem (2026-08-10)
- [x] `auto_fusao.sh` + `iniciar_studio.command` — fusão automática de catalogo_adicionar.json (2026-08-10)

## 2026-08-28 — Mapa da Biblioteca: navegação termina sempre na Mesa de Montagem
Pedido explícito do utilizador: qualquer caminho de cliques a partir do
Mapa da Biblioteca deve terminar na Mesa de Montagem de uma playlist
específica, nunca preso num ecrã intermédio.

`af_focarUniverso()` agora bifurca por contagem: Universo com
exactamente 1 playlist → `af_abrirNaMontagem()` (nova função:
`switchTabProgrammatic('montagem')` + `selectPlaylistFilter()`) salta
directo para lá, sem passar pela lista filtrada. Universo com 2+
mantém a lista filtrada na sidebar como antes, mas os itens dessa lista
(`af_renderItemPlaylist`, só quando `AF_UNIVERSO_FOCO` está activo)
passam a usar `af_abrirNaMontagem()` em vez de `selectPlaylistFilter()`
simples — antes só abria a Mesa de Montagem se essa view já estivesse
activa, o que falhava a partir da Biblioteca (o ponto de entrada normal
do Mapa). Fora do foco de Universo, o clique normal na sidebar mantém
o comportamento antigo (só filtra a tabela da Biblioteca), inalterado.

Validado: `deno check` (exit 0); teste real em Chrome via
puppeteer-core (`_teste_mapa_navegacao.js`, scratchpad) — Caso 1
("Ativadores Psicológicos", 1 playlist): clique no cartão leva direito
à Mesa de Montagem com `STD.INT.ALL.NAT.001` aberta, modal fechado, sem
ecrã intermédio. Caso 2 ("Retrato Sonoro", 3 playlists): clique no
cartão mostra a lista filtrada (3 playlists, chip "Universo: Retrato
Sonoro"), continua na Biblioteca; clicar numa dessas 3 (2ª da lista)
abre a Mesa de Montagem com essa playlist específica
(`RET.PT.90.VOZ.001`). Screenshot em
scratchpad/mapa_navegacao_caso2.png.
