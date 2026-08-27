# Music Box — Status

## Última actualização
2026-08-27

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
