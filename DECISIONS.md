# Music Box — Decisões

## 2026-08-10 — Sistema de Chaves: formato [TIPO].[GEO].[DEC].[GENERO].[VOL]

Implementado o Sistema de Chaves com o formato `[TIPO].[GEO].[DEC].[GENERO].[VOL]`.

Alterações realizadas:
- Modal do Studio redesenhado para suportar a atribuição/edição das chaves.
- 13 playlists migradas para o novo formato de chaves.
- Criado `CODIGOS.md` V2.0 com a definição dos códigos/valores válidos para cada segmento da chave.

Tarefa marcada como concluída em `TASKS.md`.

## 2026-08-10 — Botão "Definir início" (trecho_a) e catalogo_patch.json

Adicionado à mesa de montagem do Studio (`musicbox_studio.html`) um botão
"⏱ Definir início" nas posições com faixa atribuída, que abre um mini-painel
inline (campos numéricos para `trecho_a.inicio` e `trecho_a.fim`, em
segundos, e um botão "Guardar"). O valor guardado fica visível na posição
como etiqueta "A: 0s–30s".

Exceção deliberada à regra do ponto 1 do cabeçalho de `musicbox_studio.html`
("o Studio nunca edita CATALOGO"): esta funcionalidade altera o objeto
CATALOGO em memória. Continua sem escrever `catalogo.json` em disco — ao
guardar `playlists.json`, as entradas de faixa tocadas nesta sessão são
descarregadas à parte em `catalogo_patch.json` (mesmo padrão de
"download + fusão manual" já usado para `catalogo_adicionar.json`), para
posterior fusão manual em `catalogo.json`.

Validado com `deno check` sobre o bloco `<script>` extraído — sem erros de sintaxe.

## 2026-08-10 — Todas as playlists têm exactamente 8 posições

Resolve a divergência assinalada em `STATUS.md` entre o cabeçalho de
`musicbox_studio.html` (descrevia "tributo" como "sem contagem fixa") e
`validar_catalogo.py` (exige exactamente 8 posições nos três tipos). **O
validador estava correcto.**

Decisão: **todas as playlists têm exactamente 8 posições, independentemente
do tipo** (`standard` / `retrato` / `tributo`). A flexibilidade do tipo
"tributo" está no **tipo de conteúdo de cada posição** (`audio`, `trivia`,
`solo`, `foto`, `cover`, `riff`, `capa`, `bateria`), não na quantidade de
posições.

Como isto se traduz na estrutura já existente em `playlists.json`
(inalterada por esta decisão — só a documentação estava errada):
- `standard`: 7 `musicas` + 1 `mosaico` = 8 posições no total.
- `retrato`: 8 `musicas`, sem `mosaico` (regra herdada da fonte, mantém-se).
- `tributo`: 8 `posicoes`, cada uma com o `tipo` de conteúdo que fizer
  sentido para essa posição; o `mosaico`/recap final é um slot adicional,
  à parte das 8 posições curadas.

Alterações feitas para corrigir a divergência (só documentação — nenhuma
estrutura, ID ou comportamento de validação foi alterado):
- Corrigido o cabeçalho de arquitetura em `musicbox_studio.html` (ponto 2),
  que descrevia "tributo" como "sem contagem fixa".
- Actualizado `app/REGRAS_OPERADORES.md` §1.4 com a regra confirmada.
- Removida a nota de divergência em `STATUS.md`.

## 2026-08-10 — Botão "Preencher com este artista" (só Retrato)

Adicionado à mesa de montagem, para playlists tipo `retrato`: quando a
posição 01 tem faixa atribuída, aparece um botão "Preencher com este
artista". Pesquisa no CATALOGO faixas cujo array `artista` tenha
interseção com o de `musicas[0]`, ordena por menor década, e preenche
`musicas[1..7]` (posições 02–08) com os resultados — as que sobrarem sem
correspondência ficam vazias (`null`). Nunca altera a posição 01. Mostra
notificação "X faixas encontradas para [artista]".

## 2026-08-10 — "Definir início" simplificado: só INÍCIO, fim automático (+15s)

Simplificado o mini-painel "⏱ Definir início" na mesa de montagem: deixou de
ter os dois campos (início/fim). Fica só **Início (s)**. `trecho_a.fim` é
sempre calculado automaticamente como `inicio + 15` (constante
`TIMING_DURACAO_FIXA` em `musicbox_studio.html`) — sem campo próprio e sem
possibilidade de valor diferente.

Consequências:
- A etiqueta na posição passa de `"A: 20s–35s"` para `"A: 20s"` (só mostra o
  início — `timingLabelHtml`).
- **Removida a validação de duração mínima de 15s** introduzida na decisão
  anterior — deixou de fazer sentido, porque a duração é sempre fixa (15s)
  por construção, não há mais dois valores independentes para validar.
  Removidos também `TIMING_MIN_DURACAO`, a mensagem de erro inline
  "Mínimo 15 segundos" e o CSS associado (`.timing-error`, `input.invalid`).
- `trecho_a.fim` continua a ser gravado no CATALOGO em memória e incluído em
  `catalogo_patch.json` tal como antes — só deixou de ser editável
  directamente pelo operador.

Validado com `deno check` sobre o bloco `<script>` extraído — sem erros de sintaxe.

## 2026-08-10 — Botão "Preencher automaticamente" (qualquer tipo de playlist)

Adicionado à mesa de montagem: quando a posição 01 de **qualquer** playlist
(standard, retrato ou tributo) tem faixa atribuída, aparece um botão
"Preencher automaticamente" (além do "Preencher com este artista", que
continua exclusivo do Retrato). Ao clicar, deriva critérios de
geografia/década/género da **chave da playlist** e preenche as posições
seguintes com as melhores correspondências do CATALOGO, ordenadas por
`nivel` (mais fácil primeiro). Nunca toca na posição 01.

**Decisão sobre a fonte dos critérios** (pedida directamente ao
utilizador, porque `playlists.json` não tem hoje campos
`decadas`/`generos`/`geografia` no objeto da playlist — só na faixa):
critérios são derivados da **chave** (`playlistCodigo`, formato
`TIPO.GEO.DEC.GENERO.VOL` — ver `CODIGOS.md`), não de campos directos na
playlist nem da faixa da posição 01.

- `GEO`→`geografia` e `DEC`→`decadas` mapeiam de forma exacta para os
  valores usados em `catalogo.json` (tabelas `CHAVE_GEO_PARA_GEOGRAFIA` e
  `CHAVE_DEC_PARA_DECADA` em `musicbox_studio.html`).
- `GENERO` é uma categoria larga (ex. `ROC`) comparada por **substring**
  com os subgéneros reais em `generos` (ex. "Rock", "Rock Alternativo",
  "Hard Rock") — tabela `CHAVE_GENERO_PARA_PALAVRAS`. É uma **aproximação
  heurística construída para esta funcionalidade**, não uma tabela
  oficial do `CODIGOS.md` — pode precisar de afinação manual ao longo do
  tempo (ex. géneros novos, falsos positivos por substring).
- `GEO:INT` e `DEC:ALL` e `GENERO:MIX` não aplicam restrição (correspondem
  à semântica "internacional/atemporal/multi-género" do próprio
  `CODIGOS.md`). Chaves legadas sem pontos (formato antigo) não têm
  segmentos para extrair — o botão cai para pesquisa sem filtro, ordenada
  só por `nivel`.

**Alcance por tipo de playlist** (adaptado à forma de cada tipo — não
literalmente "sempre posições 02–08"):
- `standard`: preenche só até ao fim de `musicas` (posições 02–07); o
  mosaico (posição 08 neste tipo) tem forma própria (`categoria`/`pessoa`)
  e não é tocado por esta função.
- `retrato`: preenche `musicas[1..7]` (posições 02–08), igual ao
  "Preencher com este artista".
- `tributo`: preenche só `posicoes[i].id` onde `posicoes[i].tipo ===
  'audio'` — posições curadas como `trivia`/`foto`/`cover`/etc. nunca são
  tocadas nem contam para "vazias".

Notificação final: `"X faixas encontradas"`.

Validado com `deno check` sobre o bloco `<script>` extraído — sem erros de sintaxe.

## 2026-08-10 — auto_fusao.sh: fusão automática de catalogo_adicionar.json

Criados `app/auto_fusao.sh`, `app/_fundir_catalogo.py` e
`app/iniciar_studio.command` (este último não existia — criado porque o
pedido exigia que `auto_fusao.sh` fosse "iniciado pelo
iniciar_studio.command"). `iniciar_studio.command` arranca o servidor
local (se não estiver já a correr), inicia `auto_fusao.sh` destacado em
background (`nohup` + `disown`, sobrevive a fechar a janela do Terminal) e
abre o browser em `musicbox_studio.html`.

`auto_fusao.sh` corre num loop (`sleep 2`) a vigiar
`~/Downloads/catalogo_adicionar.json`. Quando aparece: espera o ficheiro
estabilizar (deixar de crescer, para não ler um download a meio), funde-o
em `catalogo.json` via `_fundir_catalogo.py`, apaga-o de Downloads e
imprime `"Fundido: X faixas"`.

**Excepção arquitetural deliberada, pedida explicitamente pelo utilizador**
(não decidida silenciosamente): em todo o resto do projecto, "download +
fusão" é sempre **manual** — ver a regra "fusão manual obrigatória" em
`REGRAS_OPERADORES.md` §2.1/§2.3, herdada do ponto 1 do cabeçalho de
`musicbox_studio.html` ("o Studio nunca edita catalogo.json"). Este é o
**único ponto do projecto com fusão automática, sem revisão humana**, numa
faixa de dados que é a única fonte de verdade do catálogo.

Dado esse risco (fusão sem revisão + apagar a única cópia de origem),
foram adicionadas protecções não pedidas explicitamente mas necessárias
para isto não poder corromper `catalogo.json` silenciosamente:
- nunca sobrescreve um `id` já existente em `catalogo.json` — salta essa
  entrada e regista aviso em `auto_fusao.log`, nunca substitui dados
  curados;
- só apaga o ficheiro de `~/Downloads` **depois** de confirmar que a
  fusão foi bem sucedida — se `catalogo_adicionar.json` não for JSON
  válido, ou não for uma lista/objecto de faixas, o ficheiro **fica** em
  Downloads e o erro fica registado, para inspecção manual;
- faz backup timestamped de `catalogo.json` antes de cada escrita, em
  `app/backups_catalogo/` — permite reverter uma fusão indesejada mesmo
  depois do ficheiro de origem já ter sido apagado;
- espera o tamanho do ficheiro estabilizar antes de o ler, para não
  processar um download ainda incompleto;
- regista cada fusão (sucesso ou erro) em `app/auto_fusao.log`;
- ficheiro de *lock* (`/tmp/musicbox_auto_fusao.lock`) para impedir duas
  instâncias em simultâneo caso `iniciar_studio.command` seja corrido
  mais que uma vez.

Testado em ambiente isolado (pasta `Downloads`/`catalogo.json` falsas, não
os ficheiros reais do projecto): faixa nova é fundida e removida de
Downloads; `id` duplicado é ignorado com aviso; entrada sem `id` é
ignorada; JSON inválido não é apagado nem funde nada (sai com erro,
ficheiro mantido). Validado também com `bash -n` (ambos os `.sh`/`.command`)
e `python3 -m py_compile` — sem erros de sintaxe.

## 2026-08-13 — `_servidor_escrita.py` (porta 8002) substitui a File System Access API como via principal de escrita

Problema reportado: a File System Access API (`FS_DIR_HANDLE`, botão
"📁 Autorizar pasta") pedia autorização de novo a cada refresh do browser —
o handle da pasta não persiste entre sessões — tornando-se incómodo no uso
diário do Studio.

Decisão: criado `app/_servidor_escrita.py`, um servidor HTTP local em
stdlib puro (sem dependências, ao contrário do `_servidor_librosa.py`), na
porta 8002, que recebe `POST /escrever?ficheiro=...` e escreve o corpo do
pedido directamente num ficheiro dentro de `app/`. `escreverFicheiro()` em
`musicbox_studio.html` passa a tentar este servidor primeiro
(`escreverViaServidor`); só cai para a File System Access API
(`escreverViaFileSystemAPI`, o mesmo código de antes, inalterado) se o
servidor não estiver a correr; e só cai para `downloadBlob()` se nenhuma
das duas funcionar. Contrato externo de `escreverFicheiro(nome, conteudo)`
mantido (`Promise<boolean>`), por isso `exportPlaylists()`,
`exportCatalogoPatch()` e as restantes chamadas não precisaram de
alteração.

Protecções adicionadas (mais que as de `_servidor_librosa.py`, que só lê):
- **Whitelist fixa de ficheiros** (`playlists.json`, `catalogo_patch.json`,
  `catalogo_adicionar.json`, `propostas_chaves.md`) — o nome vem de um
  parâmetro de URL controlado pelo browser, por isso nunca escreve num
  caminho arbitrário do disco.
- **CORS restrito a `http://localhost:8000`** (a origem real do Studio),
  ao contrário do `*` aberto do `_servidor_librosa.py` — este endpoint
  escreve, não só lê, por isso o CSRF de outra origem é um risco real a
  fechar.
- **JSON validado antes de escrever** nos ficheiros `.json` — um corpo
  inválido devolve 400 e não toca no ficheiro.
- **Escrita atómica** (ficheiro `.tmp` + `os.replace`) — nunca deixa o
  ficheiro a meio se o processo for interrompido a meio da escrita.

`iniciar_studio.command` arranca-o em background (mesmo padrão do
`_servidor_librosa.py`: `nohup` + `disown`, log próprio em
`_servidor_escrita.log`, salta se a porta 8002 já estiver ocupada). Botão
"📁 Autorizar pasta" mantido no Studio, mas re-rotulado "(fallback)" — só é
preciso se este servidor não estiver a correr.

Testado com `curl` directamente contra o servidor (sem browser disponível
neste ambiente): ficheiro fora da whitelist → 403; JSON inválido → 400 sem
tocar no ficheiro; escrita real do `playlists.json` actual sobre si mesmo
→ 200, `md5` do ficheiro inalterado (roundtrip correcto); preflight CORS
devolve só a origem `http://localhost:8000`. Validado com `deno check`
(`musicbox_studio.html`) e `python3 -m py_compile`
(`_servidor_escrita.py`) — sem erros de sintaxe.

## 2026-08-13 — Chave ANTHROPIC_API_KEY só do lado do servidor local

*(Entrada recuperada de `app/DECISIONS.md` em 2026-08-21, ao fundir esse
ficheiro — desactualizado e nunca commitado — para dentro deste, que é o
canónico. Faltava aqui apesar de várias entradas de 2026-08-21 já a
citarem como "ver DECISIONS.md 2026-08-13".)*

**Contexto:** o modal "Nova Playlist" (musicbox_studio.html) ganhou uma
secção "✦ Gerar faixas com IA" (só visível quando TIPO === 'STD') que
chama a API da Anthropic para sugerir 6 faixas + 1 mosaico a partir dos
critérios já escolhidos no modal (Tipo, Geo, Década, Género, Dificuldade)
e de uma música semente opcional.

**Problema:** o Studio é uma app "sem backend" (HTML/JS estático, servido
por `python3 -m http.server`). Chamar `https://api.anthropic.com/v1/messages`
directamente do JS do browser obrigaria a ter a `ANTHROPIC_API_KEY` visível
no código-fonte ou pedida ao utilizador a cada sessão — em qualquer dos
casos, visível a quem abrir o DevTools (Network tab) ou ver o ficheiro.

**Decisão:** a chamada à API Anthropic é feita do lado do servidor, num
novo endpoint `POST /gerar-faixas` em `_servidor_escrita.py` (porta 8002,
já usado para escrever ficheiros directamente em `app/`). Esse endpoint lê
`ANTHROPIC_API_KEY` da variável de ambiente do processo do servidor — a
chave nunca é enviada ao browser, nunca aparece no código-fonte do
`musicbox_studio.html`, nunca é gravada em disco pelo Studio. O browser só
envia `{"prompt": "..."}` e recebe `{"resultado": {...}}` já processado.

**Porquê esta opção e não `prompt()` + `sessionStorage` no browser:**
essa alternativa (pedir a chave uma vez e chamar a API directamente do
browser com o header `anthropic-dangerous-direct-browser-access`) deixaria
a chave visível no DevTools/Network tab durante toda a sessão — aceitável
só para uso estritamente pessoal, mas mais frágil e mais fácil de expor
por acidente (captura de ecrã, partilha do browser). Optou-se pela via
servidor por já existir a infra-estrutura de servidor local (`_servidor_escrita.py`,
`_servidor_librosa.py`) e por manter a chave completamente fora do browser.

**Consequência prática:** a secção "✦ Gerar faixas com IA" só funciona com
`_servidor_escrita.py` a correr (normal via `iniciar_editor.command`) E com
`ANTHROPIC_API_KEY` exportada no ambiente antes de o arrancar. Sem chave,
o endpoint devolve erro claro (500) em vez de falhar silenciosamente;
`iniciar_editor.command` avisa no arranque se a variável não estiver
definida.

**Modelo usado:** `claude-sonnet-4-6` (pedido explicitamente) — não é o
modelo mais recente da Anthropic (que seria `claude-sonnet-5`), mas foi a
escolha explícita para esta funcionalidade.

## 2026-08-21 — `_servidor_escrita.py` passa a servir ficheiros estáticos (`do_GET`), app numa única porta 8002

Pedido explícito do utilizador: adicionar `do_GET` a `_servidor_escrita.py`
para servir os ficheiros estáticos de `app/` (HTML, JSON, imagens, áudio),
para a app poder correr inteira na porta 8002 em vez de depender também de
`python3 -m http.server` na porta 8000 em paralelo.

Implementação: `do_GET` resolve o caminho pedido dentro de `APP_DIR` com
`os.path.realpath`, rejeita com 403 qualquer caminho que tente sair da
pasta (`../`), devolve 404 se o ficheiro não existir, e usa
`mimetypes.guess_type` para o `Content-Type` (cobre `.html`, `.json`,
`.mp3`, `.jpg`/`.jpeg`/`.png`, `.webp`, `.avif`, `.js`, `.css` sem tabela
própria — confirmado com `mimetypes.guess_type` nesta versão do Python).
Sem listagem de directório (não implementada — não é necessária, cada
ficheiro é pedido pelo nome, como já acontecia com `http.server` na porta
8000).

**Não alterado nesta decisão** (fora do pedido, sinalizado para decisão
futura do utilizador): `ORIGEM_PERMITIDA` continua fixa em
`http://localhost:8000`, e `musicbox_studio.html` ainda tem referências
directas a `http://localhost:8000` (ex.: botão "▶ App", texto de ajuda).
Se o utilizador vier a abrir o Studio directamente em
`http://localhost:8002/musicbox_studio.html`, os pedidos `POST` a
`/escrever`/`/upload`/etc. passam a ser same-origin (o cabeçalho CORS deixa
de ser relevante nesse caso), mas essas referências a 8000 no HTML ficam
desactualizadas até serem revistas à parte.

Testado com `curl` contra o servidor: GET a ficheiro existente
(`musicbox.html`, `catalogo.json`) → 200 com `Content-Type` correcto; GET a
ficheiro inexistente → 404; tentativa de path traversal (`GET
/../STATUS.md` e `/../../etc/passwd`, enviados com `--path-as-is` para não
serem normalizados pelo próprio curl) → 403; `POST /escrever` continua a
funcionar sem alterações. Validado com `python3 -m py_compile` — sem erros
de sintaxe.

## 2026-08-21 — `ORIGEM_PERMITIDA` e `iniciar_editor.command` actualizados para 8002

Pedido explícito do utilizador, continuação da decisão anterior (única
porta 8002): `ORIGEM_PERMITIDA` em `_servidor_escrita.py` passou de
`http://localhost:8000` para `http://localhost:8002`. Em
`iniciar_editor.command`, removido o arranque de `python3 -m http.server
8000` (redundante — `_servidor_escrita.py` já serve os estáticos via
`do_GET`, ver decisão anterior nesta mesma data) e o `open` final passou a
abrir `http://localhost:8002/musicbox_studio.html`.

Não existe (já não existe) `iniciar_studio.command` — o nome actual do
script é `iniciar_editor.command`; confirmado por pesquisa em todo o
repositório que `iniciar_studio.command` só é mencionado em documentação
histórica (`STATUS.md`, `TASKS.md`, entradas antigas deste ficheiro), não
como ficheiro real. Actualizado `iniciar_editor.command` por ser o
ficheiro com esta função hoje.

**Incidente durante o teste, registado por transparência:** ao validar a
alteração com `curl` + `pkill -f "_servidor_escrita.py"`, o `pkill` matou
um processo `_servidor_escrita.py` **já em execução** antes da sessão
(provavelmente arrancado numa sessão anterior via `iniciar_editor.command`)
— não o processo de teste, que tinha falhado a arrancar com "Address
already in use" precisamente por essa porta já estar ocupada. Confirmado
depois que a porta 8002 ficou livre e sem processos pendurados. Se o
Studio estava aberto no browser a depender desse servidor, os "Guardar"
ficaram sem efeito até o utilizador reiniciar `_servidor_escrita.py` (por
exemplo, correndo `iniciar_editor.command` de novo).

## 2026-08-21 — Geração automática de trechos A/B após "Gerar com IA" com semente do YouTube

Pedido explícito do utilizador: quando uma playlist é criada via "✦ Gerar
com IA" (tab do modal "Nova Playlist") e a semente da geração veio de um
URL do YouTube identificado por `identificarEGerarIA()`, `createPlaylist()`
passa a disparar automaticamente, em segundo plano, `POST /gerar-faixa`
(`_servidor_escrita.py`, porta 8002) para **cada** faixa gerada (as 6
sugestões da IA + a própria semente, que entra como faixa #1 + o mosaico,
se houver) — sempre por **artista+título** (nunca a URL da semente, que é
doutra música), tal como o utilizador pediu. Sem confirmação por faixa; o
utilizador só valida no final, na Mesa de Montagem.

**Distinção importante, decidida sem pedido explícito mas necessária para
não disparar isto por engano:** só corre quando a semente concretamente
veio de um **URL do YouTube** (`np-ia-youtube-url` ainda preenchido no
momento de `importarResultadoIA()`, guardado em
`NP_IA_RESULTADO.sementeYoutubeUrl`) — não basta o campo "Música semente"
ter texto (podia ter sido escrito à mão, sem qualquer vídeo identificado).
Playlists geradas por IA sem semente do YouTube continuam a exigir o botão
manual "⬇ Gerar trechos" por faixa, tal como antes — nenhum comportamento
existente foi alterado para esse caso.

**Implementação:**
- `af_gerarTrechoCore(id, url)` — núcleo extraído de
  `gerarTrechosViaServidor()` (o botão manual, que passou a chamar este
  núcleo em vez de duplicar a lógica — comportamento do botão manual
  inalterado). Sem dependência de elementos da UI; devolve
  `{ok, erro, servidorEmFalha}`.
- `af_gerarTrechosAutomaticoIA(ids)` — corre `af_gerarTrechoCore` **em
  sequência** (nunca em paralelo: cada chamada pode demorar minutos —
  download + corte — e paralelizar arriscava sobrecarregar o
  yt-dlp/ffmpeg locais ou disparar rate-limit do YouTube). Se
  `servidorEmFalha` (o `_servidor_escrita.py` nem respondeu — `TypeError`
  do próprio `fetch`), aborta o resto do lote em vez de repetir a mesma
  falha para cada faixa; erros de geração de uma faixa em concreto (ex.:
  yt-dlp não encontrou resultado) não abortam as restantes. Notificação
  única de resumo no final (`X/Y faixas`, falhas listadas se houver).
- `createPlaylist()`: captura `sementeYoutubeUrl` e os ids das faixas
  recém-criadas (`pl.musicas` + `pl.mosaico.id`) antes de `NP_IA_RESULTADO`
  ser limpo; dispara `af_gerarTrechosAutomaticoIA()` sem `await` (não
  bloqueia a UI — o modal já fechou e a Mesa de Montagem já está visível
  quando a geração está a decorrer em segundo plano).

Validado com `deno check` sobre o bloco `<script>` extraído — sem erros de
sintaxe. Não foi possível testar no browser nesta sessão (sem acesso a
browser real neste ambiente) — falta confirmação visual end-to-end (ver
`TASKS.md`): gerar uma playlist via IA com um URL real do YouTube como
semente e confirmar que os trechos aparecem de facto na Mesa de Montagem
sem intervenção manual.

## 2026-08-21 — Filtros rápidos + pesquisa na sidebar de Playlists

Pedido explícito do utilizador: adicionados à secção "Playlists" da
sidebar do Studio uma barra de pesquisa por nome (`#pl-search`) e 6
filtros rápidos — Década, Género, Geo, Dificuldade (1–5), Tipo
(Standard/Retrato/Tributo) e Estado (Pronta/Rascunho) — todos a combinar
por **E lógico** (ex.: Década=80 + Género=ROC só mostra playlists que
sejam as duas coisas ao mesmo tempo), tal como pedido.

**Origem dos valores filtrados:**
- Década/Género/Geo vêm directamente da chave estruturada da playlist
  `[TIPO].[GEO].[DEC].[GENERO].[VOL]` (`chave.split('.')`) — as mesmas
  tabelas `OPCOES_DEC`/`OPCOES_GENERO`/`OPCOES_GEO` do modal "Nova
  Playlist" populam os `<select>` (`af_popularFiltrosPlaylist()`, chamado
  uma única vez em `loadData()` — nunca em `renderSidebar()`, para não
  apagar a selecção do utilizador a cada re-render).
- Tipo e Dificuldade são campos directos do objecto playlist (`pl.tipo`,
  `pl.dificuldade`).
- **Estado é derivado, decisão tomada sem pedido explícito mas necessária
  — não existe campo `estado` em playlists.json** (só a faixa individual
  tem, com valores `rascunho`/`ativo`/`arquivado`). `af_playlistEstado(pl)`
  define "pronta" como: todas as posições preenchidas (`musicas`+`mosaico`
  para standard/retrato, `posicoes`+`mosaico` para tributo) e nenhuma faixa
  referenciada em estado `'rascunho'` no catálogo (nem em falta);
  "rascunho" caso contrário. Confirmado em `catalogo.json`/`playlists.json`
  que TODAS as posições de tributo — incluindo tipos não-áudio como
  `trivia`/`foto`/`capa` — referenciam sempre um id real do catálogo, por
  isso não precisou de tratamento à parte por tipo de posição.

Implementação em `musicbox_studio.html`: `af_playlistPassaFiltros(chave,
pl)` filtra `Object.entries(PLAYLISTS)` antes do agrupamento
standard/solo/retrato/tributo já existente em `renderSidebar()` (o
agrupamento "Solo" continua a funcionar sem alterações — um filtro
Género=ROC simplesmente nunca corresponde a GTR/BAT, por isso o grupo
desaparece sozinho). Botão "✕ Limpar filtros" (`af_limparFiltrosPlaylist`)
só visível quando algum filtro está activo. Mensagem "Nenhuma playlist
corresponde aos filtros" quando a combinação não encontra nada. Não afecta
o pseudo-item "Todas" (mantém a contagem total, como antes) nem a Mesa de
Montagem.

Validado com `deno check` — sem erros de sintaxe. Não testado no browser
(sem esse acesso neste ambiente) — falta confirmação visual (ver
`TASKS.md`).

## 2026-08-21 — "Identificar + Gerar" chama POST /gerar-faixas directamente, sem copiar/colar

Pedido explícito do utilizador — **substitui** a decisão de 2026-08-13
descrita mais acima nesta secção ("fica por usar por agora, mantido a
pedido"): o botão "🔍 Identificar + Gerar" (tab "✦ Gerar com IA" do modal
"Nova Playlist") deixa de só montar o prompt para copiar/colar em
claude.ai — depois de identificar o vídeo via oEmbed, chama directamente
`POST /gerar-faixas` (`_servidor_escrita.py`, porta 8002, já existia mas
estava por usar) com o prompt gerado, e importa o resultado JSON
automaticamente, sem o utilizador colar nada.

**Fallback preservado, decisão não pedida mas necessária:** se a chamada
ao servidor falhar (`_servidor_escrita.py` não a correr, `ANTHROPIC_API_KEY`
não definida, resposta sem JSON válido, etc.), cai para o fluxo manual
antigo — mostra o prompt na caixa de texto para copiar e colar à mão
(`gerarPromptIA()`), em vez de deixar o utilizador sem alternativa. A
caixa "Colar resposta JSON" e o botão "Importar" continuam a existir e a
funcionar exactamente como antes, para esse caso.

**Implementação:**
- `af_aplicarResultadoIA(res)` — núcleo extraído de `importarResultadoIA()`
  (que passou a fazer só o parsing do texto colado e entregar o objecto já
  parseado a esta função — comportamento do fluxo manual inalterado).
  Opera sobre um objecto já parseado (nunca texto), para poder ser chamada
  tanto pelo fluxo manual como pelo automático.
- `af_gerarFaixasIAServidor()` — chama `POST /gerar-faixas` com
  `{prompt: montarPromptIA()}`, e em caso de sucesso chama
  `af_aplicarResultadoIA(dados.resultado)`; em caso de falha, `notify()`
  do erro e cai para `gerarPromptIA()`.
- `identificarEGerarIA()`: depois de identificar o vídeo via oEmbed, passa
  a chamar `await af_gerarFaixasIAServidor()` em vez de `gerarPromptIA()`
  directamente.

Validado com `deno check` — sem erros de sintaxe. Não testado no browser
(sem esse acesso neste ambiente) — falta confirmação visual end-to-end:
colar um URL real do YouTube, clicar "Identificar + Gerar" e confirmar que
as faixas aparecem importadas sem qualquer copiar/colar, com
`ANTHROPIC_API_KEY` definida no ambiente do `_servidor_escrita.py` (ver
`TASKS.md`).

## 2026-08-21 — `iniciar_musicbox.command` recriado para porta 8002

Pedido explícito do utilizador: actualizar `iniciar_studio.command` e
`iniciar_musicbox.command` para abrir, respectivamente,
`http://localhost:8002/musicbox_studio.html` e
`http://localhost:8002/musicbox.html`, usando `_servidor_escrita.py` na
porta 8002.

`iniciar_studio.command` **não existe** — confirmado (outra vez) que o
script real com essa função é `iniciar_editor.command`, já actualizado
para 8002 mais acima nesta mesma data; nenhuma acção nova foi precisa aqui
para não criar um ficheiro duplicado/concorrente com o mesmo propósito.

`iniciar_musicbox.command` **estava apagado da árvore de trabalho**
(`git status` mostrava `D iniciar_musicbox.command` desde o início desta
sessão — não foi esta sessão que o apagou). O conteúdo em `HEAD` (commit
"Primeira versão do Music Box") apontava para um caminho antigo
(`~/MusicBox/app`, fora da localização actual em iCloud Drive), porta
8000, e abria `episodio_piloto*.html` num Chrome incógnito à parte — nada
disso faz sentido hoje. Em vez de restaurar esse conteúdo, foi recriado de
raiz, seguindo o mesmo padrão do `iniciar_editor.command` (verifica se
`_servidor_escrita.py` já está a correr na porta 8002 antes de o
arrancar) mas mais simples: sem `auto_fusao.sh` nem `_servidor_librosa.py`
— ambos específicos do Studio de edição, não fazem sentido para
`musicbox.html` (o jogo/player). Abre
`http://localhost:8002/musicbox.html`. Tornado executável (`chmod +x`),
como `iniciar_editor.command`.

Validado com `bash -n` — sem erros de sintaxe. Não corrido interactivamente
(abriria de facto um browser e arrancaria um servidor em background neste
ambiente — sem necessidade para validação de sintaxe).

## 2026-08-21 — Nenhum artista repetido na playlist gerada por IA (incluindo mosaico/pessoa)

Pedido explícito do utilizador, em duas partes: (1) nenhum artista pode
aparecer mais do que uma vez em toda a playlist gerada por IA (7 faixas
principais + mosaico); se houver repetição, rejeita e pede à IA para
substituir; (2) a validação tem de incluir o mosaico especificamente — o
`artista` da faixa do mosaico E a `pessoa` a adivinhar não podem coincidir
com nenhum artista das 7 faixas principais.

**Implementação em `musicbox_studio.html`:**
- `af_musicasIAComSemente(res)` — extraído de `af_aplicarResultadoIA()`
  (junta `res.musicas` com a semente como faixa #1, se houver); passou a
  ser partilhado com a validação, que precisa da mesma lista de "7 faixas
  principais" antes de `NP_IA_RESULTADO` sequer existir.
- `af_normalizarArtista(nome)` — reaproveita `afSlug()` (já existia, usada
  para gerar ids do catálogo) em vez de duplicar a lógica de remover
  acentos. **Testado isoladamente** (fora do browser, com casos
  sintéticos): apanha o mesmo artista escrito com maiúsculas/espaços
  diferentes (o caso real — a IA repete com grafia quase idêntica), mas
  **não** ignora artigos (`"The Beatles"` e `"Beatles"` não coincidem,
  porque `afSlug` mantém o "the") nem faz correspondência semântica —
  limitação conhecida e documentada no código, não um requisito pedido.
- `af_detectarArtistasRepetidos(musicas, mosaico)` — compara os artistas
  das 7 faixas entre si, e separadamente compara `mosaico.artista` e
  `mosaico.pessoa` contra esse mesmo conjunto (nunca contra si próprios —
  o exemplo do próprio prompt, "Sultans of Swing" dos Dire Straits com
  pessoa "Mark Knopfler", é legítimo e não deve disparar, porque Knopfler
  não é o nome de nenhuma das 7 faixas principais; testado explicitamente
  para não dar falso positivo). Devolve descrições dos conflitos.
- `af_aplicarResultadoIA(res)` — chama a validação **antes** de aceitar
  qualquer coisa; se houver conflito, rejeita por completo (não define
  `NP_IA_RESULTADO`, `notify()` de erro com o(s) conflito(s)) — nunca uma
  importação parcial. Aplica-se aos dois fluxos (manual e automático), por
  ser o ponto de entrada partilhado de ambos.
- `af_gerarFaixasIAServidor()` — ganhou um ciclo de até
  `AF_MAX_TENTATIVAS_ARTISTA_REPETIDO` (3) tentativas: valida a resposta
  do servidor antes de a entregar a `af_aplicarResultadoIA()`; se houver
  conflito, chama `/gerar-faixas` outra vez com
  `af_montarPromptCorretivoArtistaRepetido()` em vez do prompt original —
  **é literalmente o "pede à IA para substituir"** pedido pelo utilizador.
  Esgotadas as tentativas sem resolver, **não importa** (mesma regra de
  rejeição, sem excepção) — mostra um aviso claro e pré-preenche "Colar
  resposta JSON" com a última resposta da IA, para o utilizador só ter de
  corrigir o nome do artista à mão e clicar "Importar", em vez de
  recomeçar tudo do zero.
- `montarPromptIA()` — ganhou uma frase explícita ("Regra obrigatória:
  nenhum artista pode repetir-se...") no prompt base, para reduzir a
  frequência de repetições à partida, tanto no fluxo automático como no
  manual (copiar/colar em claude.ai).

**Limitação arquitectural conhecida, não resolvida:** `POST /gerar-faixas`
em `_servidor_escrita.py` é sem memória de conversa (um pedido = uma
resposta da API Anthropic, ver `_gerar_faixas_ia()`) — por isso o prompt
correctivo tem de incluir a resposta anterior completa como contexto num
único pedido novo, em vez de continuar uma conversa já existente. Funciona,
mas gasta mais tokens por tentativa do que uma conversa multi-turno faria.

Validado com `deno check` sobre o bloco `<script>` — sem erros de sintaxe.
`af_detectarArtistasRepetidos`/`af_normalizarArtista` testados
isoladamente fora do browser (Deno, casos sintéticos: sem repetição;
repetição entre músicas com grafia diferente; artista do mosaico repete
artista de faixa; pessoa do mosaico repete artista de faixa; exemplo
válido do prompt sem falso positivo) — todos a passar. **Não testado no
browser real** o fluxo completo (chamada real a `/gerar-faixas` com
`ANTHROPIC_API_KEY`, incluindo o ciclo de retentativas) — falta essa
confirmação end-to-end (ver `TASKS.md`).

## 2026-08-21 — `ATUALIZAR.command` actualizado (estava desactualizado em vários pontos, não só a porta)

O utilizador pediu para corrigir `iniciar_studio.command`/`iniciar_musicbox.command`
para 8002 — ambos já estavam correctos (`iniciar_studio.command` continua
sem existir como ficheiro; `iniciar_editor.command` e `iniciar_musicbox.command`
já apontavam para 8002, confirmado por `grep`). Encontrado, em vez disso,
um terceiro `.command` ainda em 8000: `ATUALIZAR.command`. Como não fazia
parte do pedido original, perguntei antes de mexer — utilizador confirmou
"sim, actualizar para 8002 e caminho actual".

**Estava desactualizado em mais do que a porta**, confirmado antes de
editar:
- `APP="$HOME/MusicBox/app"` — caminho antigo, de antes da mudança para
  iCloud Drive; passou a `APP_DIR="$(cd "$(dirname "$0")" && pwd)"`, mesmo
  padrão dinâmico de `iniciar_editor.command`/`iniciar_musicbox.command`.
- `DESCARGAS="$HOME/Descargas"` — confirmado com `ls` que esta pasta **não
  existe** neste Mac (`$HOME/Downloads` é a real); corrigido para
  `DOWNLOADS="$HOME/Downloads"`.
- `HTML="episodio_piloto2.html"` — ficheiro de uma versão antiga do
  projecto. **Decisão tomada sem pedido explícito, sinalizada aqui**:
  actualizado para `"musicbox.html"`, o nome actual do mesmo ficheiro
  (confirmado via `git log`: rename `episodio_piloto4.html ->
  musicbox.html`) — sem isto o script continuaria a não encontrar nada em
  Downloads mesmo com porta e caminho correctos. Confirmado que
  `musicbox.html` tem mesmo o marcador `BUILD [0-9-]*` que o script já lia
  no fim (linha inalterada), portanto é de facto o alvo certo.
- `pkill -f "python3 -m http.server 8000"` + reiniciar sempre o servidor —
  **removido**, substituído pelo mesmo padrão de "só arranca se não
  estiver a correr" (`lsof -i :8002`) usado em `iniciar_editor.command`.
  Forçar reinício a cada execução fazia sentido com um `http.server`
  efémero e sem estado; com `_servidor_escrita.py` (processo persistente,
  partilhado com o resto do Studio, com endpoints de escrita) matá-lo sem
  necessidade interromperia uma sessão de edição em curso — mesmo
  problema que já aconteceu por acidente nesta sessão com `pkill -f
  "_servidor_escrita.py"` genérico (ver decisão de 2026-08-21 sobre
  `ORIGEM_PERMITIDA`).

Resto da lógica (copiar de Downloads para app/, apagar de Downloads,
abrir no browser, mostrar o `BUILD`) mantida sem alterações — só o
transporte (porta/servidor) e os caminhos mudaram.

Validado com `bash -n` — sem erros de sintaxe. `chmod +x` mantido. Não
corrido interactivamente (copiaria/apagaria um ficheiro real de Downloads
e arrancaria um servidor em background — sem necessidade para validação
de sintaxe, e só faz sentido correr com um `musicbox.html` real à espera
em Downloads).

## 2026-08-21 — Prompt mais restritivo sobre a semente + fallback com mensagem clara

Pedido explícito do utilizador, duas correcções à funcionalidade de
"Gerar com IA": (1) o prompt enviado à IA deve proibir explicitamente o
artista da semente nas 6 faixas restantes (não só implicitamente, via a
regra geral de "nenhum artista repetido"); (2) quando o fallback manual é
activado depois de 3 tentativas falhadas por artista repetido, mostrar uma
mensagem de erro clara em vez do prompt para copiar/colar.

**(1) `montarPromptIA()`** — a "Regra obrigatória" já existente ganhou uma
frase extra, só quando há artista da semente identificado (`semArtista`):
nomeia-o explicitamente como "JÁ É a semente... PROIBIDO voltar a
aparecer". A mesma frase foi acrescentada a
`af_montarPromptCorretivoArtistaRepetido()` (o prompt usado nas
retentativas automáticas), para o lembrete se manter mesmo depois da
primeira tentativa.

**(2)** Só a branch "esgotadas as 3 tentativas por artista repetido" em
`af_gerarFaixasIAServidor()` mudou — deixou de chamar `gerarPromptIA()`
(que mostrava o prompt para copiar/colar) e passou a mostrar directamente
"Não foi possível gerar automaticamente — tenta outra semente." (painel +
`notify`). Justificação registada no código: pedir à mesma IA, com a
mesma semente, já falhou 3 vezes a evitar o artista repetido — insistir
manualmente com o mesmo contexto tende a repetir o problema; a saída mais
fiável é tentar outra semente, não continuar a tentar corrigir a mesma. A
OUTRA branch de fallback (erro de rede/servidor a chamar `/gerar-faixas`,
sem relação com artista repetido) manteve `gerarPromptIA()` — nesse caso o
prompt continua a ser uma alternativa válida (o problema é o servidor não
responder, não a IA repetir artista).

Validado com `deno check` — sem erros de sintaxe.

## 2026-08-21 — Painel de progresso estruturado na tab "✦ Gerar com IA" (substitui o texto cinzento)

Pedido explícito do utilizador: substituir o texto cinzento simples
(`#np-ia-youtube-status`) por um painel de progresso visível em tempo
real, mostrando qual faixa está a ser gerada, tentativas de substituição
por artista repetido, e progresso dos trechos A/B (ex.: "3/7 trechos
gerados") — com estado por faixa.

**Problema de arquitectura a resolver primeiro:** o progresso "por faixa"
dos trechos A/B só existe na fase `af_gerarTrechosAutomaticoIA()`, que só
corre **depois** de "Criar playlist" — e `createPlaylist()` até agora
fechava o modal imediatamente ao clicar nesse botão. Para o painel poder
mesmo aparecer "no modal", `createPlaylist()` teve de deixar de fechar o
modal logo quando há trechos a gerar automaticamente (`idsParaGerarTrechos.length`)
— fica aberto, muda para a tab `ia` (`switchNPTab('ia')`), e só fecha +
navega para a Mesa de Montagem quando `af_gerarTrechosAutomaticoIA()`
terminar (`.then(...)`). Sem essa alteração, o pedido do utilizador seria
impossível de cumprir literalmente. Foi acrescentado um botão "→ Ver na
Mesa de Montagem" no painel para quem não quiser esperar — a geração
continua em segundo plano de qualquer forma (já era fire-and-forget desde
a funcionalidade de 2026-08-21 anterior), só a navegação é que fica à
escolha do utilizador.

**Implementação em `musicbox_studio.html`:**
- `AF_IA_PROGRESSO` — estado global (`{fase, mensagem, tentativaArtista,
  faixas}` ou `null`); `AF_CHAVE_PLAYLIST_EM_PROGRESSO` — chave da
  playlist cujos trechos estão a ser gerados, para a navegação automática
  saber para onde ir e para `af_verMontagemAgora()` (botão manual) evitar
  navegação dupla (idempotente: limpa a variável ao navegar, a
  continuação em `createPlaylist()` só navega se ainda for a mesma
  chave).
- `af_renderProgressoIA()` — desenha o painel a partir de
  `AF_IA_PROGRESSO` dentro de `#np-ia-progresso` (renomeado de
  `#np-ia-youtube-status` — deixou de ser só sobre o YouTube). Mensagem de
  topo, linha de tentativa (se houver), e uma lista com um ícone/cor por
  faixa (○ pendente / ◐ a gerar / ✓ pronto / ✗ falhou+erro) quando há
  `faixas`, com contagem "X/Y trechos gerados" e o botão "Ver na Mesa de
  Montagem".
- `af_definirProgressoIA(mensagem, fase)`/`af_limparProgressoIA()` —
  helpers para as fases sem lista de faixas (identificar/erro/limpar).
- `identificarEGerarIA()`, `af_gerarFaixasIAServidor()`, `gerarPromptIA()`
  — todos os `statusEl.textContent = ...` substituídos por chamadas ao
  painel; `af_gerarFaixasIAServidor()` passou a preencher
  `tentativaArtista` a partir da 2ª tentativa.
- `af_gerarTrechosAutomaticoIA(ids)` — constrói `AF_IA_PROGRESSO.faixas`
  no arranque (título/artista de cada id via `CATALOGO_BY_ID`, todas
  `pendente`), actualiza o estado da faixa actual antes/depois de cada
  `af_gerarTrechoCore()`, e re-renderiza a cada passo. Se o servidor cair
  a meio (`servidorEmFalha`), marca as faixas por tentar como `falhou`
  (antes ficavam silenciosamente por fazer) em vez de as deixar
  "pendente" para sempre.

**Testado isoladamente** (fora do browser, com um `document.getElementById`
simulado): 5 estados diferentes do painel (vazio, identificar, tentativa de
substituição, trechos em progresso, trechos com falha) — output HTML
inspeccionado manualmente, incluindo confirmação de que título com
`<script>` e artista com aspa (`O'Brien & Sons`) saem correctamente
escapados (`escapeHtml`/`escapeAttr`, já existentes, reaproveitados — sem
risco de XSS através de título/artista sugeridos pela IA).

Validado com `deno check` sobre o bloco `<script>` completo — sem erros de
sintaxe. **Não testado no browser real** o fluxo completo (modal a ficar
aberto durante a geração, actualização ao vivo do painel, botão "Ver na
Mesa de Montagem") — falta essa confirmação end-to-end (ver `TASKS.md`).

## 2026-08-21 — Feedback ao vivo na Mesa de Montagem durante a geração de trechos

Pedido explícito do utilizador: a Mesa de Montagem deve mostrar o estado
de cada faixa em tempo real enquanto `af_gerarTrechosAutomaticoIA()` corre
em segundo plano — contador no topo ("3/7 trechos gerados") + estado por
faixa (a gerar…/pronto/falhou) — porque antes, ao clicar "Ver na Mesa de
Montagem", não havia feedback nenhum aí.

**Bug encontrado e corrigido na funcionalidade anterior (2026-08-21, painel
de progresso):** `af_verMontagemAgora()` limpava
`AF_CHAVE_PLAYLIST_EM_PROGRESSO` ao navegar, para evitar dupla navegação
quando o lote terminasse depois. Mas isso cortava também a única ligação
que a Mesa de Montagem tinha para saber que playlist tinha um lote em
curso — exactamente o sintoma reportado. Corrigido separando as duas
responsabilidades: nova variável `AF_NAVEGACAO_JA_FEITA` (booleano) impede
a dupla navegação; `AF_CHAVE_PLAYLIST_EM_PROGRESSO` deixou de ser limpa ao
navegar — só é sobrescrita quando um novo lote arranca
(`createPlaylist()`) ou quando o modal é reaberto de raiz
(`limparResultadoIA()`).

**Implementação:**
- `af_estadoTrechoEmProgresso(id)` — devolve o estado de uma faixa no lote
  em curso, ou `null`. Só depende de `AF_IA_PROGRESSO.fase === 'trechos'` e
  de a faixa constar da lista — não depende de
  `AF_CHAVE_PLAYLIST_EM_PROGRESSO`, por isso continua correcto mesmo
  depois do utilizador já ter navegado.
- `trackMetaHtml(t)` — nova tag, sempre primeiro, com o estado (⏳/◐/✓/✗)
  quando `af_estadoTrechoEmProgresso` devolve algo.
- `renderMontagem()` — novo badge agregado no cabeçalho da playlist
  ("X/Y trechos gerados"), só quando `currentPlaylistKey ===
  AF_CHAVE_PLAYLIST_EM_PROGRESSO` e a fase for `'trechos'`. Desaparece
  sozinho quando a fase muda para `'concluido'`/`'erro'` no fim do lote —
  não precisa de nenhuma limpeza explícita de estado para isso.

Validado com `deno check`. Não testado no browser real — falta essa
confirmação (ver `TASKS.md`).

## 2026-08-21 — Nova chave ANTHROPIC_API_KEY definida a pedido do utilizador; `~/.zshrc` tinha 6 linhas conflituosas

O utilizador pediu para arrancar `_servidor_escrita.py` com uma chave
colada directamente no terminal (fora do âmbito deste repositório, mas
registado aqui porque afectou o processo do servidor usado para testar
esta sessão). Reiniciado o processo específico (nunca `pkill` genérico,
lição da sessão anterior) com a nova chave.

Pedido de seguida para persistir a chave em `~/.zshrc`. **Antes de
escrever, verificado o ficheiro e encontradas 6 linhas
`export ANTHROPIC_API_KEY=...` já existentes** (o ficheiro só tinha 9
linhas ao todo) — 4 eram placeholders nunca preenchidos
(`sk-ant-...`, `sk-ant-AQUI_A...`), e as outras 2 (idênticas entre si) uma
chave real mas DIFERENTE da colada nesta sessão. Como havia ambiguidade
real (qual chave manter) e o ficheiro é pessoal, fora deste repositório,
perguntado ao utilizador antes de mexer — confirmou usar a chave desta
sessão e limpar tudo. `~/.zshrc` reduzido às 3 linhas originais (`deno
env`, `PATH`, `fnm`) + uma única `export ANTHROPIC_API_KEY=...` com a
chave correcta. Backup do ficheiro anterior guardado em
`~/.zshrc.bak-20260821-171759`. Validado por hash (sem imprimir a chave em
lado nenhum) que abrir um novo terminal exporta exactamente o valor certo.

## 2026-08-21 — 5 modos de geração na tab "✦ Gerar com IA" (URL/Tema/Categoria/Semente múltipla/Playlist YouTube)

Pedido explícito do utilizador: além do modo URL do YouTube já existente,
adicionar 4 modos de geração ao modal "Nova Playlist → ✦ Gerar com IA",
cada um com o seu próprio prompt para `/gerar-faixas`, todos com a mesma
validação de artistas repetidos já existente. Nesta mesma leva, pedido
adicional (mid-turn): a validação deve também apanhar quando a "pessoa" do
mosaico é membro conhecido de uma banda já usada nas 7 faixas (ex.: "Ian
Curtis" quando "Joy Division" já está listado) — ver mais abaixo, é uma
regra só de prompt (não algorítmica).

**Arquitectura escolhida — um só "info do modo", tudo o resto reaproveitado:**
em vez de 5 fluxos paralelos, criado `af_infoModoGeracaoIA()` — função
central que, consoante `AF_MODO_GERACAO_IA`, devolve
`{faixasFixas, contextoTxt, artistasProibidosExtra, criteriosFixos?}`.
Todo o resto do pipeline existente (`montarPromptIA`,
`af_musicasIAComSemente`, `af_detectarArtistasRepetidos`,
`af_aplicarResultadoIA`, `af_gerarFaixasIAServidor` com retentativas,
`af_montarPromptCorretivoArtistaRepetido`) passou a consumir esta função
em vez de ler directamente os campos `np-ia-semente`/`np-ia-artista` —
zero duplicação de lógica entre modos.

**Os 5 modos** (sub-tabs `.np-modo-tab`/`.np-modo-content`, classe própria
para não colidir com `switchNPTab()` — ver `af_switchModoGeracaoIA`):
1. **URL** — comportamento original, inalterado (oEmbed → 1 faixa fixa).
2. **Tema/Mood** — texto livre (`np-ia-tema`), sem faixa fixa nenhuma; a
   IA continua a sugerir geo/decadas/genero livremente.
3. **Categoria** — 3 selects fixos (Década/Geo/Género, populados por
   `af_popularSelectsModoIA()` a partir de `OPCOES_DEC/GEO/GENERO`, mesmas
   tabelas do resto do modal). **Decisão tomada sem pedido explícito**: o
   prompt passa a dizer à IA para usar EXACTAMENTE esses três valores no
   JSON `"playlist"` em vez de lhos pedir para sugerir — simplifica
   (`aplicarMetadadosPlaylistIA` já mapeia o que a IA devolver, sem
   precisar de lógica nova) e garante que o resultado bate sempre certo
   com o que o utilizador escolheu.
4. **Semente múltipla** — até 3 pares título+artista
   (`np-ia-multi-titulo-N`/`np-ia-multi-artista-N`); todos entram como
   faixas fixas #1..#3 (generalização de `af_musicasIAComSemente`, que
   deixou de estar limitada a uma única semente) e ficam todos proibidos
   de repetir.
5. **Playlist YouTube** — cola um URL de playlist, "📥 Ler playlist"
   chama o novo `POST /listar-playlist-youtube`
   (`_servidor_escrita.py`, `yt-dlp --flat-playlist --playlist-end 30`,
   **nunca descarrega áudio/vídeo**, só lê metadados). **Decisão tomada
   sem pedido explícito**: os títulos ficam só como CONTEXTO — nunca
   entram como faixas fixas da playlist final (uma playlist do YouTube
   pode ter dezenas de vídeos; inserir todos não faz sentido) — mas os
   artistas continuam proibidos de repetir
   (`artistasProibidosExtra`, novo 3º parâmetro de
   `af_detectarArtistasRepetidos`, também usado no aviso do prompt).
   Testado que `%(uploader)s` do `yt-dlp --flat-playlist` vem
   frequentemente `NA`/vazio (confirmado com um canal real do YouTube) —
   por isso a separação "Artista - Título" é feita no cliente, reaproveitando
   `limparTituloYoutube`/`separarTituloArtista` (já existiam, usadas por
   `identificarEGerarIA`), com o uploader só como fallback. Lista editável
   (`af_renderPlaylistYoutubeLista`) com checkbox para excluir faixas
   antes de gerar (ex.: trailers numa playlist mista).

**Regra "membro de banda" no mosaico (pedido adicional mid-turn):**
adicionada ao prompt (`montarPromptIA`, ponto 2 das "Regras obrigatórias")
com o exemplo concreto pedido (Ian Curtis/Joy Division). **Limitação
conhecida e documentada, não escondida**: isto NÃO é validado
algoritmicamente (ao contrário da repetição exacta de nome, que
`af_detectarArtistasRepetidos` apanha e o fluxo automático tenta corrigir
sozinho) — não existe base de dados de membros de bandas no cliente; só a
própria IA tem esse conhecimento. Se a IA ignorar a instrução, não há
forma de o cliente apanhar isso e pedir retentativa automaticamente — fica
dependente da IA seguir a instrução, tal como a regra "nunca inventes
títulos/artistas" já dependia antes.

**Testes:**
- **26 testes isolados** (fora do browser, Deno, com DOM simulado) — os 5
  modos, incluindo `af_infoModoGeracaoIA`/`montarPromptIA` a produzirem o
  contexto/regras/critérios certos por modo, `af_musicasIAComSemente` a
  inserir 0/1/2 faixas fixas na ordem certa consoante o modo,
  `af_detectarArtistasRepetidos` a apanhar repetição via
  `artistasExternos`, e `separarTituloArtista`/`limparTituloYoutube` a
  separar um título de playlist típico. Todos a passar.
- **Endpoint `/listar-playlist-youtube` testado ao vivo** contra o
  servidor real a correr: URL de domínio inválido → 400; corpo vazio →
  400; pedido real contra um canal do YouTube (`@YouTube/videos`) → 200
  com 30 faixas (respeita `LISTAR_PLAYLIST_MAX_FAIXAS`).
- **Prompt do modo Tema testado ao vivo contra a API Anthropic real**
  (`POST /gerar-faixas`, mesmo servidor, `claude-sonnet-4-6`): a resposta
  real da IA repetiu de facto "Joy Division" entre 2 faixas (mesmo com a
  regra explícita no prompt) — confirma que a validação automática é
  genuinamente necessária, não só teórica. A resposta real (com a
  repetição) foi depois passada por `af_detectarArtistasRepetidos`, que a
  apanhou correctamente ("Joy Division" repete-se em "Love Will Tear Us
  Apart" e "Decades"). Não foi observado no teste nenhum caso real de
  violação da regra "membro de banda" (mosaico), por isso essa parte só
  tem cobertura da lógica de prompt, não de comportamento real da IA.

Validado com `deno check` sobre o bloco `<script>` completo e
`python3 -m py_compile` sobre `_servidor_escrita.py` — sem erros de
sintaxe. **Não testado no browser real** o fluxo de UI completo (trocar de
sub-tab, ler uma playlist real e rever/editar a lista, gerar nos 4 modos
novos) — falta essa confirmação end-to-end (ver `TASKS.md`).

## 2026-08-25 — Regra fixa de organização e nomenclatura: Duas Famílias (Format Book V11 §3)

Confirmado que a Bíblia do formato (V11, secção 3 "Sistema de Categorias")
já define a estrutura primária de organização das playlists — não é
"géneros OU anos" como escolha única, são **duas famílias paralelas**:

- **Família 1 — Décadas**: Anos 50 a Anos 2010, cada uma com os géneros
  predominantes dessa década.
- **Família 2 — Géneros Atemporais**: Jazz, Blues, Rock, Hip Hop, Soul &
  R&B, Dance & Electrónica, Cinema & Bandas Sonoras, Slot Local — géneros
  que atravessam décadas e não cabem numa só.

Dois níveis de produção usam estas famílias: **Standard** — o concorrente
escolhe uma categoria do painel, década OU género atemporal; **Premium**
— escolha dupla género+década, painel só acende combinações com conteúdo.

**Confirmado que o Sistema de Chaves já codifica isto**, sem ter sido
desenhado explicitamente para tal: no formato `[TIPO].[GEO].[DEC].[GENERO].[VOL]`,
`DEC=ALL` corresponde sempre a Família 2 (género atemporal — ex:
`STD.INT.ALL.SYN.001` "Synthwave", `STD.INT.ALL.CIN.001` "Cinema &
Música"), e `DEC=<década específica>` corresponde sempre a Família 1 (ex:
`STD.INT.80.MIX.001` "Anos 80", `STD.INT.70.ROC.001`). Não é preciso
nenhum campo novo — a família de uma playlist deriva-se directamente do
segmento `DEC` da sua chave.

**Regra de nomenclatura fixada** (campo `nome` em `playlists.json`),
resolvendo a inconsistência encontrada entre playlists antigas
(nomeadas à mão, funcionais) e playlists mais recentes geradas via
"Gerar com IA" (títulos longos/poéticos):

- `nome` — sempre funcional e curto, reflectindo a família: Família 1 →
  `"Anos XX — [tema/género]"`; Família 2 → só o nome do género/tema
  (`"Synthwave"`, `"Rock"`, `"Cinema & Música"`). Nunca títulos poéticos
  aqui.
- `descritivo` (campo já existente em `playlists.json`, hoje quase sempre
  vazio) — é aqui que entra o tom criativo/poético, como subtítulo, sem
  aparecer na lista principal da barra lateral do Studio.

**Nota:** foi precisamente nas playlists com nomes poéticos/fora do
padrão que apareceram os problemas de dados mais sérios encontrados nesta
sessão (playlist "Heartbeats in the Dark: Synth & Soul of the 2010s" com
8 ids inexistentes no catálogo; "Decade of Riffs" com vários bugs) — reforça
que a falta de disciplina de nomenclatura coincidiu com falta de disciplina
de dados, não é só uma questão estética.

**Acção decidida:** renomear as playlists fora do padrão (ver `TASKS.md`
para a lista concreta) e reorganizar a barra lateral do Studio para
agrupar primariamente por Família (Décadas / Géneros Atemporais),
substituindo o agrupamento actual por Tipo estrutural
(Standard/Solo/Retrato/Tributo) — este passa a aparecer como etiqueta
secundária por playlist, não como cabeçalho de grupo.

## 2026-08-25 — Imagem obrigatória em todas as posições + pesquisa Wikimedia automática em ADICIONAR FAIXA

*(Entrada escrita em 2026-08-26, retroactivamente — o código já tinha isto
implementado e commitado, mas os três comentários que o assinalam no
código apontam para "ver DECISIONS.md 2026-08-25" e a entrada
correspondente nunca tinha sido escrita aqui. Confirmado por leitura
directa do código em `~/MusicBox2026/musicbox_studio.html`, commit
`18fef08` de 2026-08-25 18:17.)*

**Contexto:** utilizador propôs mostrar a imagem da faixa ao lado do
concorrente quando este acerta, para **todas** as faixas (até então só
acontecia nalgumas). Validado como boa ideia — reforça o momento de
reconhecimento, e a infra-estrutura (`imagem` por faixa) já existia.
Ressalvas levantadas antes de implementar: (1) isto torna-se trabalho
contínuo — toda faixa nova passa a precisar de imagem, daí a decisão de
tornar isso obrigatório logo em ADICIONAR FAIXA, no momento da criação;
(2) não deve competir visualmente com "O Ícone" (Format Book: momento
raro, 36 peças, só 2 momentos no episódio) — o reveal normal mantém-se
discreto/pequeno, para o Ícone continuar a ser especial.

**Como o Studio já obtinha imagens antes desta decisão** (via grep ao
código, não assumido):
- **Standard:** upload manual local — utilizador escolhe um ficheiro do
  computador, grava directo em `app/`, associa a `t.imagem` (mesmo
  mecanismo da foto do apresentador).
- **Retrato Sonoro:** pesquisa automática via API pública do Wikimedia
  Commons (`abrirPesquisaImagem`/`executarPesquisaImagem`/
  `usarImagemWikimedia`, botão "🔍 Imagem") — pesquisa por texto
  (artista+título), grelha de resultados, grava o URL remoto do
  Wikimedia directamente em `t.imagem` (excepção conhecida e comentada
  no código: aqui `imagem` é um URL remoto, não um ficheiro local — o
  `validar_catalogo.py` acusa isto como "em falta" localmente, é
  esperado). Tem fallback de colar URL à mão (`usarImagemManual`) e um
  modo "fila" que percorre automaticamente todas as faixas sem imagem
  de uma playlist Retrato.

**Implementação (as três peças pedidas):**

1. **ADICIONAR FAIXA abre a pesquisa Wikimedia automaticamente.**
   `afAdicionarAoCatalogo()` — depois de gravar a faixa nova, chama-se
   sempre `abrirPesquisaImagem(entrada.id, artistaTexto, titulo)` (linha
   6428), sem condição — deixou de ser só um aviso de "falta imagem".
   Comentário no código (linhas 6405-6410): "em vez de só avisar que
   falta imagem, abre-se logo a pesquisa, pré-preenchida com
   artista+título". Detalhe técnico registado: a query de pesquisa em si
   usa `${artista} musician` (linha 3649) — o título aparece como
   etiqueta no painel, não está literalmente concatenado na caixa de
   pesquisa; o pré-preenchimento é real, só não é "artista+título"
   colados num único campo de texto.

2. **`verificarCompletudePlaylist()` estendida a todas as faixas.**
   Linhas 2724-2728, comentário no próprio código: "Imagem obrigatória em
   TODAS as posições, qualquer tipo de playlist... Corrigido em
   2026-08-25 depois de 'Anos 80' ter dado 'sem problemas' por engano —
   as 7 faixas Standard não tinham imagem, só não estavam a ser
   verificadas." `if (!t.imagem) falta.push('img')` (linha 2748) corre
   para qualquer posição, sem excepção por tipo de playlist — só o
   Retrato (e a excepção pontual `STD.INT.ALL.CIN.001`) fica de fora da
   exigência de `trecho_b`, **não** da exigência de imagem.

3. **Mosaico também exige imagem.** O mosaico entra na mesma lista de
   posições verificadas (`posicoes.push({..., ehMosaico: true})`, linha
   2736) e passa pelo mesmo `if (!t.imagem) falta.push('img')` — não há
   bypass para `ehMosaico`.

**Estado de teste:** código commitado (`18fef08`, "Reorganiza sidebar do
Studio..."), `git status` limpo neste ficheiro à data desta entrada. Não
confirmado nesta entrada se houve teste end-to-end no browser (ver
`TASKS.md` para o padrão habitual de itens "por confirmar visualmente"
usado no resto deste documento) — esta entrada documenta o que o código
faz, verificado por leitura directa, não um novo teste realizado agora.

## 2026-08-26 — Retrato Sonoro é excepção à regra "resposta = Artista/Banda"

Durante correcção de "membro individual em vez da banda" no campo
`artista` (mesma categoria de bug já corrigida em "We Will Rock You" →
"Queen"), foi identificado o caso `ret_03` — "Love of My Life", com
`artista: ["Freddie Mercury"]` em vez de "Queen".

**Decisão: manter "Freddie Mercury".** Não é o mesmo bug.

A série Retrato Sonoro (`ret_01`–`ret_08`) não segue a regra geral
"resposta esperada = Artista/Banda" — o conceito da série é retratar uma
pessoa/ícone através de uma canção que a define, não identificar quem
tocou a canção. Os outros 7 exemplos confirmam o padrão a 100%: Frank
Sinatra, Elvis Presley, Michael Jackson, Whitney Houston, Elton John,
António Variações, David Bowie — todos indivíduos, nenhuma banda. Trocar
"Freddie Mercury" por "Queen" só neste caso quebraria a consistência da
série inteira.

**Regra explícita a partir de agora:** dentro do Retrato Sonoro, a
resposta esperada é sempre a pessoa retratada, mesmo quando a canção é
creditada a uma banda (ex: Freddie Mercury em "Love of My Life", não
Queen). A regra geral "Artista/Banda" continua a aplicar-se a todos os
outros tipos de playlist (standard, mosaicos temáticos, etc.).

Registado para evitar que um audit futuro "corrija" isto por engano.
