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

## 2026-08-27 — Pesquisa geral na web (DuckDuckGo) como último recurso da cascata de imagem

Regra permanente (Bíblia, Cap. 27.14): a cascata de imagem de artista
(`_theaudiodb_imagem_artista` → `_wikipedia_imagem_artista` →
`_itunes_imagem_artista`) tem cobertura fraca do Catálogo Local — músicos
portugueses menos conhecidos internacionalmente (ex.: Kalú/Xutos &
Pontapés, Fernando Tordo, Alexandre Frazão) raramente têm entrada em
TheAudioDB ou artigo próprio na Wikipedia. A API da Bing Image Search
(única alternativa prevista) foi descontinuada pela Microsoft em
2025-08-11 (ver `_bing_imagem_artista`), e o Google Custom Search JSON API
é pago e precisa de credenciais.

**Solução escolhida:** scraping do próprio motor de imagens da
DuckDuckGo (`duckduckgo.com/i.js`), sem chave nem custos — por trás,
devolve resultados do Bing na mesma, sem a API paga. Testado ao vivo em
2026-08-27 com 3 casos reais (Kalú+contexto, Fernando Tordo, Alexandre
Frazão), todos com resultados utilizáveis. É scraping não-documentado
oficialmente — pode parar de funcionar sem aviso se a DuckDuckGo mudar o
mecanismo; falha sempre para o lado seguro (lista vazia).

**Regra de segurança inegociável:** ao contrário das outras fontes da
cascata (aplicadas automaticamente por `af_aplicarMelhorImagemArtista()`
via `GET /buscar-imagem-artista`), os resultados da pesquisa geral **nunca
são aplicados automaticamente**. Só entram em
`_duckduckgo_imagens_artista()`, chamada exclusivamente por `GET
/buscar-imagens-cascata` (o endpoint da grelha de revisão manual no
painel "Trocar imagem" do Studio), e só quando TheAudioDB e Wikipedia não
devolvem nada. `/buscar-imagem-artista` (a cascata automática em lote)
nunca chama esta função — mantém-se TheAudioDB → Wikipedia → iTunes →
Bing (stub morto). Resultados desta fonte ficam marcados
`imagem_fonte: "web_geral"`, com selo 🌐 e aviso explícito no painel para
o curador confirmar bem antes de escolher.

Novo parâmetro opcional `contexto` em `GET /buscar-imagens-cascata`
(ex.: o campo `banda` da faixa) — desambigua nomes curtos/comuns antes de
consultar o DuckDuckGo (ex. "Kalú Xutos & Pontapés" em vez de só "Kalú").

## 2026-08-28 — DÉCADAS/GÉNEROS/ESPECIAIS como estrutura primária (pedido explícito, Bíblia 7.10/27.12)
As 3 famílias de Universos (DÉCADAS, GÉNEROS, ESPECIAIS) passam a ser a
estrutura de organização primária em todo o sistema, substituindo a
distinção antiga Standard/Solo/Retrato/Tributo como nível 1. A Bíblia já
foi actualizada pelo utilizador (7.10 e 27.12 removem a regra "Especiais
só a partir da Ronda 2" — as 3 famílias ficam disponíveis desde a
Playlist 1, em pé de igualdade).

**Parte 1 (Studio)**: `renderSidebar()` em `musicbox_studio.html` passa a
agrupar por Família (nível 1) → Tipo (nível 2: Standard/Retrato/Tributo)
→ playlists. Nova função `af_familiaDePlaylist(chave, pl)` deriva a
família a partir do código estruturado `[TIPO].[GEO].[DEC].[GENERO].[VOL]`
+ do campo `tipo` (retrato é sempre Especiais — Retrato Sonoro/Logótipos
são 2 dos 7 Universos Especiais canónicos). Regras chave, verificadas
contra as 26 playlists reais: GEO=PT + GENERO≠BAT/GTR → Especiais (Slot
Local se DEC=ALL, Cruzamento se DEC com valor); DEC≠ALL (fora do caso
GEO=PT) → Décadas; GENERO=MIX+GEO=INT+DEC=ALL → Especiais (Cruzamento);
resto por tabela GENERO→família (Rock/Pop/Metal/Americana/Synth/Dance/
Guitarra/Bateria→Géneros, Cinema/TV/Videojogos/Ativadores/Vozes→
Especiais). Filtros existentes (Década/Género/Geo/Dificuldade/Tipo/
Estado) mantidos, agora a filtrar por cima da nova estrutura.

**Parte 2 (Jogo)**: remover a restrição "Especiais só a partir da Ronda
2" em `musicbox.html` (`UNIVERSOS_ESPECIAIS`/`FAMILIA_COLECAO`) — ecrã de
escolha de família passa a mostrar sempre 3 opções.

**Parte 3**: corrigir `playlistCodigo` em falta em `playlists.json`.

## 2026-08-28 (correcção) — Reorganização Família→Tipo da sidebar ANULADA
A instrução de reorganizar a sidebar do Studio com Família (Décadas/
Géneros/Especiais) como agrupamento primário e Tipo como secundário
(registada acima) foi explicitamente anulada pelo utilizador no mesmo
dia. Substituída por: sidebar colapsável (lista completa de playlists
atrás de um toggle, oculta por omissão) + um "Mapa da Biblioteca"
separado (modal, aberto a partir de rótulos de Família na sidebar) para
a visão por Família/Universo. Ver entrada seguinte e STATUS.md.

## 2026-08-28 — Sidebar colapsável + Mapa da Biblioteca
Decisão de arquitectura registada por afectar a estrutura de navegação
do Studio (CLAUDE.md regra 8). Resumo (detalhe completo em STATUS.md):
- Sidebar volta ao agrupamento por Tipo→Década (o que já existia antes
  da tentativa de reorganização por Família), mas colapsada por omissão
  atrás de um toggle "Ver todas as playlists", persistido em
  localStorage. Filtros existentes inalterados.
- 3 rótulos de Família (Décadas/Géneros/Especiais) ficam sempre visíveis
  na sidebar, mesmo colapsada — abrem o novo "Mapa da Biblioteca".
- Mapa da Biblioteca: visão em fluxograma dos 28 Universos canónicos
  (Cap. 7.10 da Bíblia), cobertura calculada dinamicamente a partir de
  playlists.json real. Clicar num Universo coberto filtra a sidebar a
  essas playlists específicas (`AF_UNIVERSO_FOCO`), sem substituir os
  filtros existentes do Studio — ambos aplicam-se em conjunto.
- `af_universoDePlaylist(chave, pl)` (musicbox_studio.html) é a extensão
  de `af_familiaDePlaylist` (Parte 1, revogada como agrupamento mas
  mantida/generalizada como utilitário) — deriva tanto a Família como o
  Universo canónico específico a partir do código estruturado da
  playlist + do campo `tipo`.

## 2026-08-28 — Correcção estrutural ao bug do auto-save
Decisão registada por alterar o comportamento de escrita em disco do
Studio (CLAUDE.md regra 8), pedida explicitamente pelo utilizador como
bloqueante antes de continuar a criar playlists. Detalhe completo em
STATUS.md — resumo: `_servidor_escrita.py` ganha verificação de versão
(mtime) opcional em `POST /escrever`, comparada atomicamente do lado do
servidor contra o mtime que a aba tinha ao carregar; escritas
automáticas em conflito são recusadas e avisadas (nunca sobrescrevem às
cegas); escritas manuais em conflito pedem confirmação explícita ao
utilizador antes de prosseguir. Ficheiros que não passam por este
mecanismo (concorrentes.json, apresentador.json, catalogo_patch.json,
catalogo_adicionar.json, propostas_chaves.md) mantêm o comportamento
antigo, sem alteração — âmbito desta correcção é especificamente
playlists.json, o ficheiro documentadamente afectado pela corrida do
auto-save de 60s.

## 2026-08-28 — Aviso: 4 códigos de género reais não coincidem com OPCOES_GENERO
Descoberto ao implementar `universos_secundarios` (§27.14b), não
relacionado com essa funcionalidade — regista-se aqui por afectar dados
já publicados (CLAUDE.md regra 8, decisão a confirmar, não tomada
silenciosamente).

As 4 playlists de género criadas em 2026-08-28 usam `GENERO=JAZ` (Jazz),
`SOU` (Soul & R&B), `HIP` (Hip Hop), `CLA` (Clássica) nas suas chaves
estruturadas reais (`STD.INT.ALL.JAZ.001` etc.). A lista de códigos já
reservados no Studio (`OPCOES_GENERO`, usada no filtro de Género da
sidebar e no modal "Propor Nova Chave") tem, para os mesmos géneros,
`JZZ`, `SOL`, `HHP`, `CLX` — códigos diferentes, nunca coordenados
antes de criar as playlists (não existe um `CODIGOS.md` no repositório;
`OPCOES_GENERO` é a única lista de referência real).

Consequência prática: filtrar a sidebar por "JZZ — Jazz" (ou SOL/HHP/CLX)
não encontra as playlists reais correspondentes pela etiqueta
dominante — só passam a aparecer se alguém lhes atribuir explicitamente
essa etiqueta como `universos_secundarios`. A família/Universo no Mapa
da Biblioteca e no jogo continuam correctos (derivados directamente do
código real da chave, não de `OPCOES_GENERO`).

**Não corrigido nesta sessão** — duas opções para decidir:
1. Renomear as 4 chaves das playlists (`STD.INT.ALL.JAZ.001` →
   `...JZZ...`, etc.) + os ids das faixas/ficheiros de áudio associados
   — alinha com `OPCOES_GENERO`, mas é uma alteração disruptiva a dados
   e ficheiros já publicados (contraria CLAUDE.md regra 5, "não alterar
   IDs... sem necessidade explícita").
2. Actualizar `OPCOES_GENERO` para usar JAZ/SOU/HIP/CLA em vez de
   JZZ/SOL/HHP/CLX — mais simples e não toca em dados publicados, mas
   muda o que está "reservado" para futuras playlists.
Recomendação: opção 2, mas fica para confirmação do utilizador antes de
qualquer alteração.

**Resolvido 2026-08-28**: utilizador confirmou a opção 2 — códigos
reservados realinhados para JAZ/SOU/HIP/CLA (não só em `OPCOES_GENERO`,
também em `CHAVE_GENERO_PARA_PALAVRAS`, `CHAVE_GENERO_PARA_QUERY`,
`MIGRACAO_CHAVES` e `montarPromptIA()` — todas as estruturas que
referenciavam os códigos antigos JZZ/SOL/HHP/CLX). Playlists já
publicadas mantidas intocadas. Ver STATUS.md.

## 2026-09-17 — §5.4b revisto: continuidade sonora pós-acerto + redesenho do "Encore"
Duas decisões ligadas, ambas no motor de jogo (`musicbox.html`), dentro
do redesenho da sequência pós-acerto (bloco "TESTE TEMPORÁRIO — NÃO
COMMITAR" na altura, commitado em 2026-10-04, ver abaixo).

**§5.4b — Continuidade Sonora Pós-Acerto**: a chamada em `acertouFaixa()`
tinha ficado `audio.pause()` desde uma iteração anterior da sequência de
teste, contradizendo directamente o próprio comentário/regra §5.4b ao
lado ("não parar o áudio corrente, continua a tocar"). Corrigido para
`audio.volume = 0.25` (reduz, não pára) durante a revelação; o volume só
volta a 1 quando a Faixa seguinte arranca de facto (`iniciarFaixa()`) —
cobre tanto o avanço automático como o "Encore" (que só chama
`carregarTrecho()`, nunca `iniciarFaixa()`, por isso o volume continua
reduzido durante o Trecho B do Encore, voltando ao normal só na Faixa
seguinte a sério).

**"▶ Encore" — nunca toca automaticamente**: redesenhado como uma JANELA
DE DECISÃO de 1.5s (`TESTE_JANELA_DECISAO_TRECHO_B_MS`) — verde enquanto
dentro da janela; clicar nessa janela escolhe tocar o Trecho B (~7s,
depois avança sozinho); não clicar faz o botão ficar vermelho e avançar
sozinho pouco depois (`TESTE_PAUSA_VERMELHO_MS`, só para o vermelho ser
mesmo visível). O Trecho B nunca arranca por si só em caso algum.

## 2026-09-18 — Sistema de Feedback e Aprendizagem + Modo Elo (Studio)
**Sistema de feedback** (`feedback.json`): regista, por sessão de
geração com IA, a decisão do curador por faixa (aceite/rejeitada/
substituída) e por mosaico, ligado à playlist via `feedback_id`. Serve
de contexto para a IA em gerações futuras — `montarPromptIA()` injecta
um bloco com os últimos 20 registos relevantes (filtrados por modo de
geração + parâmetro) antes da instrução principal, para a IA aprender
dos padrões já aceites/rejeitados pelo curador. `feedback_jogo` (tempo
de resposta, % de acerto, ritmo dramático) fica `null` até haver
episódios reais lançados com essa playlist — não é inferido nem
simulado. As 39 playlists já existentes antes deste sistema foram
registadas por backfill (`popular_feedback_inicial.py`) com
`modo_geracao: "manual"`, todas as faixas marcadas `aceite` na posição
em que já estavam.

**Modo Elo**: novo modo de geração na tab "✦ Gerar com IA" — o curador
dá uma palavra/frase curta (ex. "Deserto") e a IA explora ligações
variadas a esse elo (artista, título, letra, filme, imaginário, etc.)
em vez de um critério fixo de década/género. Limite do prompt
(`GERAR_FAIXAS_MAX_PROMPT`) subido de 4000 para 12000 caracteres — o
limite antigo rejeitava prompts deste modo (mais as instruções de
`descritivo_apresentador`/`nota_curadoria`, pedidas em todos os modos),
fazendo cair, por engano, no fallback manual (entretanto removido por
completo — ver 2026-09-18 mais abaixo, "Substituir").

**`elo_explicacao`**: campo que a IA preenche só no fluxo de
substituição de faixas (✎ Substituir, auto ou validação da sugestão do
curador) explicando a ligação ao elo — exclusivo do modo Elo, visível
só no Studio (Mesa de Montagem, `af_playlistCriadaPeloModoElo()` decide
pela `modo_geracao` do registo de feedback da playlist), nunca exposto
na app de jogo.

**`risco_elo`** (campo que sinalizaria o quão arriscada/óbvia é uma
ligação): **não implementado** — decisão explícita de resolver primeiro
editorialmente via instrução no prompt (ver entrada de 2026-09-19 a
seguir) antes de adicionar mais um campo de dados à estrutura.

## 2026-09-19 — Revisão da instrução do mosaico no modo Elo: ligação indirecta, não óbvia
Inversão deliberada da instrução original de 2026-09-18. Antes: pedia-se
à IA a imagem mais directa e imediatamente óbvia possível para o elo
(ex. "alguém fotografado com dunas, calor, horizonte árido" para
"Deserto") — na prática isto entrega o tema secreto da playlist ao
jogador antes da revelação, estragando a mecânica de charada do
mosaico. Agora: o mosaico deve ter ligação real ao elo mas
preferencialmente INDIRECTA — a imagem tem de ser reconhecível e
funcionar como charada por si só, só ficando "satisfatória" (a ligação
ao elo faz sentido) depois de revelada, nunca antes. Exemplo a evitar,
citado na própria instrução: Hans Zimmer/Dune para o elo "Deserto" — é
real, mas demasiado directo.

## 2026-10-04 — Frase única de anúncio "Versão B" + 302 ficheiros de voz gerados
Substituída a sequência de dois ficheiros separados pós-acerto ("in the
box" sintetizado + eco → voz limpa só com o nome do artista) por um
único ficheiro com a frase completa "[Artista] — In the Box!", voz
`say -v Alex -r 205`, com o mesmo efeito de entoação festiva já em uso
(pitch ascendente em duas zonas — 55% a +2%, 45% restantes a +6% — mais
volume +18%, duração final preservada por `atempo` a compensar
`asetrate`). Testado em A/B contra a versão anterior ("In the Box —
[Artista]"); a Versão B ("[Artista] — In the Box!") foi a escolhida.
`testeTocarSequenciaSom()` simplificada para tocar só este ficheiro e
avançar para a janela de decisão do Encore ao terminar — já não precisa
da lógica de overlap/preload que só fazia sentido para colar dois
ficheiros em sequência.

Ficheiro em disco: `_preview_voz_artista_<id>.wav` (id do catalogo.json).
Gerados para as 302 faixas de todas as séries standard/retrato/video do
catálogo. Excluídos de propósito:
- `beatles_*` — playlist Tributo (`TRB.UK.ALL.ROC.001`), estrutura de
  jogo diferente (posições foto/trivia/solo, sem o mecanismo de
  revelação Trecho A/B que este anúncio de voz pressupõe).
- `logo_*` / `LOGO-001` — pendente de revisão legal de direitos de
  marca dos logótipos usados (Bíblia §27.15), mesma razão por que esta
  playlist já estava excluída do Modo Teste.

## 2026-10-04 — Fix: colisão em CATALOGO_POR_FICHEIRO_A por ficheiro de áudio partilhado
`CATALOGO_POR_FICHEIRO_A` (ponte entre `catalogo.json` e as playlists
Standard, usada para a imagem do artista/banda no overlay de acerto/
erro) resolvia colisões de `trecho_a.ficheiro` partilhado por ORDEM DO
ARRAY do catálogo — "quem vem depois ganha", sem olhar a que playlist a
faixa pertence. Caso real: `80_02` (Guns N' Roses, playlist "Anos 80",
activa) e `logo_02` (mesma faixa física, playlist `LOGO-001`, excluída)
partilham o ficheiro `02_a.mp3`; como `logo_02` vem depois no array,
sobrescrevia sempre `80_02` — ao acertar a faixa 80_02 no jogo, o
sistema tentava carregar o ficheiro de voz/imagem de `logo_02` (404).

Fix: antes de construir o Map, calcula-se para cada id de faixa se
pertence a alguma playlist NÃO excluída
(`PLAYLIST_CODIGOS_EXCLUIDOS = new Set(['LOGO-001'])`, mesma lista
conceptual de exclusão do §27.15 usada em `mostrarTesteLista()` — ainda
não unificada num único sítio porque uma trabalha com o código da
playlist e a outra com a chave curta de `COLLECTIONS`, espaços de
chaves diferentes). Uma colisão só troca a entrada já guardada a favor
da nova quando esta pertence a uma playlist activa e a antiga não —
nunca ao contrário, independentemente da ordem no `catalogo.json`.
Varrido o catálogo completo: esta é a única colisão deste tipo
existente nos dados actuais.

## Convenção de teste — confirmar a porta 8002 antes de reportar erros
Processo parasita encontrado durante a sessão: um `python -m
http.server 8002` solto, sem suporte a POST, a ocupar a mesma porta que
`_servidor_escrita.py` (IPv6 vs IPv4 — a resolução de `localhost`
alternava entre os dois de forma imprevisível). Causava falhas
intermitentes e confusas em funcionalidades que dependem de POST (ex.
geração por IA a "cair sempre no fallback"). Convenção adoptada: correr
`lsof -i :8002` antes de qualquer teste e antes de reportar um erro
501/"falha a gerar" como bug de produto — só `_servidor_escrita.py`
deve lá estar.

## Playlist "Deserto" (modo Elo) — em curso, não finalizada
Primeira playlist gerada pelo modo Elo, usada como caso de teste de
referência para todo o fluxo (geração inicial, substituição de faixas e
de mosaico, validação de artista repetido, `elo_explicacao`). Ainda por
fazer antes de poder ser considerada uma playlist real: os ficheiros de
áudio gerados durante os testes (darude_sand_storm, eagles_hotel_
california_2, gnr_dunas, hans_zimmer_dune_main_theme, oasis_wonderwall_3,
sting_desert_rose_3, the_bangles_walk_like_an_egyptian, the_clash_rock_
the_casbah — soltos na raiz do projecto, ainda fora de `catalogo.json`)
têm de ser integrados no catálogo, e a playlist regenerada no Studio
depois do motor Elo estar estabilizado (a instrução do mosaico mudou
entretanto, ver 2026-09-19 acima — uma geração anterior a essa data
pode não reflectir a regra actual).

## 2026-10-04 — Abandonada a proposta de comandos embutidos `[[pbas]]`/`[[pmod]]` para "In the Box!"
Investigação pedida pelo utilizador antes de regenerar os 302 ficheiros
de voz com entoação diferente na parte "In the Box!" (mais aguda/
entusiasmada). Testada a sintaxe sugerida — `[[pbas +10]][[pmod +40]]`
(valores relativos, com "+") — directamente com `say -v Alex`: o
comando `say`/motor de fala do macOS **não gera erro nem aviso para
comandos embutidos inválidos — ignora-os em silêncio**, continuando a
falar o resto do texto normalmente. Como a sintaxe documentada da Apple
(Speech Synthesis Programming Guide) usa sempre **valores absolutos em
Hz** para `pbas`/`pmod`, não deltas relativos, não havia forma de saber
só pela duração do áudio se os comandos "+10"/"+40" estavam de facto a
ter efeito ou a ser descartados silenciosamente. `[[rate N]]` (sintaxe
absoluta, documentada) confirmou-se a funcionar (duração do áudio variou
de forma consistente com a mudança de velocidade).

Gerada uma amostra com valores absolutos (`[[pbas 150]][[pmod 60]]
[[rate 230]][[emph +]]`) para comparação directa com o actual — ver
`propostas/in_the_box_actual_80_01.wav` vs
`propostas/in_the_box_tunado_80_01.wav`. **Abandonada de qualquer
forma** — substituída pela arquitectura de 3 ficheiros abaixo, que
resolve o problema de forma mais robusta (controlo total sobre o "In
the Box!" em vez de depender de comandos embutidos de fiabilidade
incerta).

## 2026-10-04 — Nova arquitectura da voz pós-acerto: 3 ficheiros encadeados no browser
Substitui o modelo anterior (1 ficheiro por faixa, frase completa
"[Artista] — In the Box!" num só `.wav`, ver 2026-10-04 "Frase única de
anúncio" acima) por 3 ficheiros distintos, tocados em sequência no
browser (`testeTocarSequenciaSom()`), encadeados por eventos `ended`:

1. **`voz/nome_<id>.wav`** — só o nome do artista, voz natural de
   apresentador de TV, sem efeito festivo, sem pitch alterado. Um
   ficheiro por faixa (como antes), mas agora só com o nome.
2. **`efeitos/in_the_box.wav`** — um único ficheiro, **partilhado por
   todas as faixas** — "In the Box!" eufórico/comemorativo. Deixa de
   haver 302 cópias quase-idênticas desta parte da frase.
3. **`efeitos/roar.wav`** — roar de multidão/estúdio, sobreposto ao
   fim do "In the Box!" (~150ms de overlap).

Razão da mudança: a parte "In the Box!" era idêntica em todas as 302
faixas (só o nome do artista varia) — gerá-la 302 vezes, embutida em
cada ficheiro, desperdiça trabalho e torna impossível afiná-la
centralmente (mudar o tom exigia regenerar tudo outra vez). Com um
ficheiro único partilhado, afinar "In the Box!" ou trocar o roar passa
a ser uma alteração num sítio só.

Escolhida a voz do nome: **Oliver** (en_GB), de entre Alex (actual),
Samantha, Daniel e Oliver — comparados em `propostas/nome_<voz>_<n>.wav`
com os nomes "a-ha", "Red Hot Chili Peppers", "Earth, Wind & Fire".
Nenhuma voz "Enhanced"/"Premium" está instalada nesta máquina
(`say -v '?'` não lista nenhuma com essa qualidade) — todas as
comparações foram feitas com vozes "compact" (qualidade base do
sistema).

**Por fazer antes de regenerar os 302 nomes**: afinar o rate do Oliver
(Passo 1b, propostas em curso) e decidir "In the Box!" (gravação própria
do utilizador, se existir em `efeitos/in_the_box_takes/`, ou TTS
processado — Passo 2). Roar ainda não existe no projecto (pasta
`efeitos/` por criar) — utilizador vai obter um efeito livre (Pixabay/
Freesound CC0), nada foi descarregado automaticamente.

**Nota de revisão (5 Out 2026)**: o Oliver foi abandonado — a voz final
do nome do artista (e do "In the Box!!") é **Alex, rate 205**
(`say -v Alex -r 205`), a mesma já em uso antes desta entrada. Ver
`gerar_vozes_nome_artista.py` (script committado) e Bíblia §5.4b
(revisto em 5 Out 2026). Texto original acima mantido sem alterações,
como registo histórico do processo de comparação (Alex/Samantha/Daniel/
Oliver) que levou a esta decisão.

## 2026-10-05 — Narração do descritivo: edge-tts é só para protótipo

O `say` do macOS não tem nenhuma voz masculina em português instalada
(só Catarina/Joana pt_PT e Luciana pt_BR, todas femininas, todas
"compact" — confirmado com `say -v '?'`). O utilizador quer uma voz
masculina para a narração do `descritivo_apresentador`.

Instalado **edge-tts** (pacote Python, vozes neurais da Microsoft — o
mesmo motor do "Ler em voz alta" do Edge), num venv isolado do projecto
(`.venv-tts/`, fora do git) para não tocar no Python do sistema
("externally-managed-environment", PEP 668). Comparadas duas vozes
masculinas: `pt-PT-DuarteNeural` e `pt-BR-AntonioNeural` (amostras em
`propostas/desc_duarte.wav`/`desc_antonio.wav` + nomes de teste com
Duarte).

**AVISO — só para protótipo, não para a versão final/emissão real**:
- edge-tts precisa de ligação à internet em cada geração — cada frase é
  enviada ao serviço da Microsoft pela rede, não há modo offline.
- Os termos de uso para uso comercial/emissão de TV **não estão
  confirmados** — é um projecto open-source que reaproveita uma API não
  documentada oficialmente para esse fim pela Microsoft; o estatuto
  legal para este tipo de uso não foi verificado.
- A versão final (quando o programa for para emissão real) precisa de
  uma voz devidamente licenciada para esse fim (ex. ElevenLabs, com
  licença comercial) ou de um locutor real — decisão a tomar nessa
  altura, não agora.

Escolha da voz (Duarte/Antonio/outra) ainda pendente — amostras geradas,
a aguardar confirmação do utilizador antes de qualquer geração em massa
ou ligação ao jogo.

## 2026-10-05 — Sistema de estados (aprovada/gravada) adiado

Investigação (musicbox_studio.html): hoje não há nenhuma máquina de
estados que bloqueie a edição de playlists — `playlist_aprovada` em
`feedback.json` é escrito sempre a `true` na criação e nunca lido em
lado nenhum (campo morto); `af_playlistEstado()` só calcula um rótulo
`'rascunho'/'pronta'` para o filtro da barra lateral, não bloqueia nada;
`selectSlot()`/`pickTrack()`/`assignToSlot()`/`removeSlot()` (troca
manual de faixa numa posição já guardada) não têm nenhuma verificação de
estado. "✎ Substituir" (3 alternativas da IA) só existe hoje dentro do
assistente de criação de playlist nova (`NP_IA_RESULTADO`), não no
fluxo de edição normal de uma playlist já guardada.

Desenhada uma proposta completa de sistema de estados
(`rascunho`/`aprovada`/`gravada`, botão "🔓 Reabrir para edição" com
confirmação, re-validação ao reaprovar, marcação `substituida_de` com
cor âmbar, aviso de regenerar a voz do descritivo se a faixa trocada lá
for mencionada) — **decisão do utilizador: não implementar agora**.
Fica registada aqui como ideia para mais perto das gravações reais dos
episódios: nessa altura, a protecção mais importante é impedir editar
playlists com `feedback_jogo` já preenchido (ou seja, já usadas num
episódio gravado) — essas só devem poder ser duplicadas como nova versão
(ex. "Vol. 2" ou próximo `.NNN`), nunca editadas no lugar. `feedback_jogo`
(dentro do registo de `feedback.json` associado via `playlist_id`) já
existe e já é exactamente o sinal certo para essa protecção quando for
construída.

Implementado em vez disso, já: "✎ Substituir" (IA) também na Mesa de
Montagem para playlists já guardadas — ver commit "Studio: ✎ Substituir
com IA na Mesa de Montagem".

## 2026-10-05 — Família "Géneros" passa a "Estilos" (só interface)

Decisão do utilizador: a família de playlists "Géneros" (Décadas/Géneros/
Especiais) passa a chamar-se "Estilos" em todo o texto visível — "♪
ESTILOS (N)" nos painéis do jogo (`mostrarTesteLista()`/
`escolherUniversoDaFamilia()`), "Estilos Atemporais" na sidebar do
Studio, "Estilo (todos)" no filtro da Biblioteca, label "Estilo"/
"ESTILO" nos campos de género por faixa na criação/edição de faixas.

Só a interface muda — identificadores internos ficam (`FAMILIA_GENEROS`,
`GENERO_FAMILIA`, `OPCOES_GENERO`, `generoLabel`, `t.genero`/`t.generos`,
IDs de campos como `pl-filter-genero`/`af-generos`): comentário
acrescentado junto a cada `const FAMILIA_GENEROS` nos dois ficheiros a
explicar a decisão. `FAMILIA_GENEROS` passou a valer `'ESTILOS'` (o
texto mostrado), não `'GÉNEROS'` — o NOME da constante não mudou, só o
valor que ela guarda (confirmado não haver nenhuma comparação de string
literal `'GÉNEROS'` no código que isso pudesse partir).

Nenhum dado em `playlists.json`/`catalogo.json` guarda o nome da família
como valor — só `universo: "Género Musical"` (subtítulo descritivo,
campo diferente) e `nota_curadoria` (texto interno), nenhum alterado.

Deixados por mexer, deliberadamente: comentários de código que mencionam
"Géneros" conceptualmente (dezenas, em ambos os ficheiros) — são
documentação interna, não interface; e uma linha em
`musicbox_studio.html` (~7007) que usa "Género:" dentro de um prompt
enviado à IA, não texto mostrado a um humano.

## 2026-10-05 — Sinal sonoro da Pergunta Bónus

Decisão do utilizador: nova direcção pedida ("meia fanfarra, som curto,
tipo sino") depois de rejeitar as 3 primeiras propostas (A: arpejo
ascendente, B: fanfarra de 2 acordes, C: sting de suspense — nenhuma
escolhida). Geradas 3 variantes novas com ffmpeg (sem sox disponível no
sistema), timbre de sino sintetizado por partials inarmónicos
(`aevalsrc` com soma de senos em razões 1/2.0/2.76/4.0/5.4 e decaimentos
exponenciais distintos por partial — aproximação de sino metálico):
D (2 notas em quinta ascendente), E (acorde de fanfarra só de ataque +
camada de sino), F (3 notas rápidas "ding-ding-DING", última mais
forte). Escolhida a proposta **F** — copiada para `efeitos/bonus.wav`.

Toca no momento em que o painel do BONUS_MODE aparece (dentro do
`setTimeout` de `acertouFaixa()`, dispara `tocarSinalBonusPainel()`) —
distinto da sirene sintetizada já existente (`tocarSireneBonus()`, que
toca mais cedo, logo no acerto). Mesmo padrão de verificação única do
`roar.wav` (`bonusSomDisponivel`, checado uma vez no arranque): se o
ficheiro não existir, segue sem som e sem erro na consola.

Testado com Playwright nas Décadas (Faixa 4) e numa Especial (Faixas 3
e 6) — sinal toca exactamente uma vez por aparecimento do painel, zero
erros de JS.

## 2026-10-05 — Volumes pós-acerto e pausa antes do Encore (entrada em falta, adicionada na reconciliação com a Bíblia)

Decisão já implementada e commitada mais cedo nesta sessão, sem entrada
própria neste ficheiro até agora — adicionada ao reconciliar
`DECISIONS.md` com a Bíblia (ver §30.9).

`VOL_ENCORE = 0.45` ("meio-termo", `musicbox.html`): depois da sequência
de voz pós-acerto (nome → "In the Box!!" → roar) terminar, a música deixa
de voltar logo a `VOL_MUSICA` (0.75) — desce para este nível intermédio e
mantém-se aí durante toda a janela de decisão do Encore. Só sobe a
`VOL_MUSICA` quando o Trecho B realmente arranca (escolhido) ou quando a
Faixa seguinte arranca a sério (não escolhido).

`PAUSA_ANTES_ENCORE_MS = 1500`: a janela de decisão do Encore só aparece
1,5s depois do fim do último som da sequência de voz — a música (já em
VOL_ENCORE) continua a tocar normalmente durante essa pausa, nunca
parando. Cancelada sem deixar rasto em `esconderMomentoResposta()` se o
jogador avançar ou houver reset antes de disparar — mesmo padrão dos
outros timers pendentes pós-acerto (`testeTimeoutJanelaDecisao`,
`testeTimeoutCorteTrechoB`).

Testado com Playwright (1502ms medidos, cancelamento ao avançar
verificado). Ver Bíblia §5.4b (revisto em 5 Out 2026).

## 2026-10-05 — Descritivos sem spoilers: regra geral (substitui o registo como fix pontual)

Generalização de uma correcção editorial já aplicada a 3 playlists
(commit `b075be2`) para uma regra fechada, aplicável a todo o texto
editorial que antecede uma Playlist (`descritivo_apresentador`) e às
Perguntas Bónus (ver 2026-10-05 "Pergunta Bónus nas Décadas/Estilos"
acima):

**Regra fechada**: o descritivo do apresentador evoca o universo da
Playlist (época, ambiente, tema) sem nunca nomear o título, o artista, a
obra (filme, série, jogo) ou a pessoa de qualquer Faixa ou do Mosaico da
própria Playlist. Uma pista vaga é aceitável; uma pista que identifique
directamente a resposta não.

Registada na Bíblia em §18.7 e na nova §15.6 "Descritivos sem Spoilers"
(revisto/criado em 5 Out 2026, ver §30.9).

## 2026-10-05 — Escala de dificuldade: 1-5 confirmada como oficial (resolve a contradição §15.5/§27.13)

Decisão do utilizador: a escala oficial de dificuldade das Playlists é
**1 a 5** — confirmado ser a que o código (`musicbox.html`/
`musicbox_studio.html`, "Dif. X/5", `min="1" max="5"`), os dados
(`dificuldade` em `playlists.json`, valores 1 a 5 todos presentes) e a
interface já usam. A escala alternativa de "3 níveis" descrita em §27.13
da Bíblia nunca chegou a ser adoptada na prática.

§15.5 fica como está (já descreve "Calibragem 1-5"). §27.13 marcada
"(revisto em 5 Out 2026)" — texto original tachado, mantido como
registo histórico, com nota a apontar para §15.5 como a escala em
vigor.

## 2026-10-05 — Unicidade de artista: membro de banda conta como a banda (Bíblia §27.2)

Auditoria à Biblioteca encontrada por um caso real: "Anos 70 — Rock"
tinha Queen (Bohemian Rhapsody, Faixa 1) e Roger Taylor — creditado
pelo nome próprio, mas `banda: "Queen"` no catálogo — em "We Will Rock
You" (Faixa 2). A regra §27.2 já existia ("nunca dois artistas iguais
na mesma playlist") mas não cobria explicitamente membros de banda.

**Regra fechada**: um membro conhecido (passado ou presente) de uma
banda já presente numa playlist conta como essa banda — não pode
aparecer numa posição separada, nem como artista da Faixa, nem como
`pessoa` do Mosaico.

Scan completo à Biblioteca (todas as playlists não-Tributo, usando o
campo `banda` do catálogo quando existe, senão `artista[0]`) encontrou
mais 2 casos preexistentes, nenhum por membro de banda — duplicação
directa do mesmo artista: "Ambient & Introspectivo" (The Durutti
Column em Faixa 1 + Mosaico; Brian Eno em Faixa 3 + Faixa 6) e "Anos
2010 — Synth" (Future Islands em Faixa 1 + Mosaico). Ainda por corrigir
— fora do âmbito desta correcção pontual (só "Anos 70 — Rock").

**Implementado no Studio** (`musicbox_studio.html`): aviso não-bloqueante
na Mesa de Montagem (`af_avisoArtistasRepetidosHtml`/
`af_artistasRepetidosNaPlaylist`/`af_identidadeArtistaFaixa`, resolve via
`banda` do catálogo) — não bloqueia guardar. Prompts de "Gerar com IA"
(substituição de faixa, 4 ocorrências) actualizados para instruir
explicitamente a IA a tratar membros de banda como a própria banda —
antes só os prompts de substituição do Mosaico tinham essa instrução.

Testado com Playwright: aviso aparece para "Anos 70 — Rock" ("Artista
repetido: Queen (Faixa 1, Faixa 2)"), não aparece para uma playlist
limpa, zero erros de JS.

**Aplicado**: Faixa 2 de "Anos 70 — Rock" trocada de `bat_02` (Roger
Taylor/Queen) para `bat_08` (Keith Moon/The Who, novo na catalogo.json,
reaproveita o áudio de `rock_06` "Baba O'Riley" — sem ficheiro próprio
ainda, ver STATUS.md). Faixa 3 (Eric Clapton/Layla) mantida — não tem
ligação a Queen. Aviso confirmado desaparecido após a troca.

## 2026-10-05 — Nomes de artista por língua (voz/pronuncia.json)

Alex (voz inglesa, `say`) lê mal nomes de artistas noutras línguas.
**Regra fechada**: `voz/pronuncia.json` atribui voz edge-tts por
artista — `{"voz": "<id edge-tts>", "texto": "<grafia alternativa,
opcional>"}`. Prioridade: excepção manual (nome exacto em
`pronuncia.json`) > prefixo do código da playlist (`STD.PT.`/`RET.PT.`
→ `pt-PT-DuarteNeural`; `STD.BR.` → `pt-BR-AntonioNeural`, calculado
dinamicamente por `gerar_vozes_nome_artista.py`, não listado no
ficheiro) > Alex r205 (default, inalterado).

Excepções manuais fechadas: António Variações/Cesária Évora (Duarte,
fora de playlists PT); Boris Vian/Alain Oulman/Maurice Jarre/Claude
Debussy (`fr-FR-HenriNeural`); Peret/Los Del Río/Enrique Iglesias
(`es-ES-AlvaroNeural`); Quilapayún (`es-CL-LorenzoNeural`); Ennio
Morricone/Nino Rota/Antonio Vivaldi (`it-IT-DiegoNeural`); Ramin
Djawadi/Johann Pachelbel/Carl Orff (`de-DE-ConradNeural`); Pyotr Ilyich
Tchaikovsky (`ru-RU-DmitryNeural`, `texto` em cirílico: "Пётр Ильич
Чайковский"). José Feliciano/Michael Bublé/Beyoncé ficam deliberadamente
em Alex (já bem conhecidos em contexto anglófono).

**Resolvido (5 Out 2026)**: voz grega (Vangelis) e voz japonesa (Koji
Kondo/Nobuo Uematsu/Yoko Shimomura) testadas e rejeitadas ("soam
estranhas") — ambas passam para **Duarte**, com grafia fonética PT:
Vangelis → "Vanguélis"; Koji Kondo → "Côji Côndo"; Nobuo Uematsu → sem
alteração (grafia original já soa bem); Yoko Shimomura → "Ióco
Ximomura". Amostras em `propostas/vangelis_alt.wav`/
`japoneses_alt.wav`.

## 2026-10-05 — Anúncio de voz no acerto do Mosaico

**Diagnóstico**: `confirmarMosaicoAcerto(i)` (`musicbox.html`) nunca
teve anúncio de voz — só revelava a grelha, somava pontos e avançava
após 1200ms, sem tocar nada. Único caminho de código, partilhado pelo
fluxo real e pelo Modo Teste (`testarMosaico()` → `iniciarMosaico()` →
mesma função). Scan a `playlists.json`: **0 de 38 mosaicos têm `pessoa`
vazia** hoje — o exemplo citado (`STD.INT.ALL.MIX.004`, Hans Zimmer
"Dune") não existe nos dados actuais.

**Implementado**: `gerar_vozes_nome_artista.py --mosaicos` gera
`voz/mosaico_<código>.wav` a partir do campo `pessoa` de cada playlist
(mesmas regras de voz por língua de `voz/pronuncia.json`, índice
próprio em `voz/mosaico_index.json`) — 38/38 gerados. No jogo,
`confirmarMosaicoAcerto()` passa a: duck para `VOL_DUCK` → `voz/
mosaico_<código>.wav` → 120ms → `efeitos/in_the_box.wav` → fade de
`FADE_UP_MS` (600ms) para `VOL_MUSICA` → avanço já existente — o
Mosaico não tem Encore nem Trecho B, por isso este é o único sítio onde
o volume volta ao normal. Ficheiro de nome em falta: salta direito para
"In the Box!!" (nunca fica em silêncio) — verificação única em cache
por código (`mosaicoSomAnuncioDisponivelCache`, mesmo padrão de
`apresentacaoDisponivel()`).

**Bug real apanhado e corrigido antes de aplicar**: algumas playlists
vivem em `COLLECTIONS` sob uma chave curta legada (ex. `"ANOS80"`, não
`"STD.INT.80.MIX.001"`) — usar `collectionActual` directamente para o
nome do ficheiro de voz falhava silenciosamente para essas. Corrigido
para usar `COLLECTIONS[collectionActual].playlistCodigo`, que guarda
sempre o código estruturado (igual à chave para playlists já no formato
novo) — mesmo campo que `playlistCodigo` já usa noutros sítios.

Testado com Playwright: fluxo real e Modo Teste em "Anos 80" (Mark
Knopfler) — volume 0.75→0.25→0.75, sequência `mosaico_STD.INT.80.
MIX.001.wav` → `in_the_box.wav` confirmada; ficheiro inexistente toca
só `in_the_box.wav`, sem erro. Zero erros de JS nos três cenários.
`catalogo.json`/`playlists.json` não tocados.

**Implementado** (`gerar_vozes_nome_artista.py`): dois motores — `say`
(Alex, como antes) e edge-tts (as restantes vozes, mesmo filtro de
corte de silêncio + loudnorm). Índice `voz/nome_index.json` (novo,
`sha1(texto+voz)`) só regenera uma faixa se o texto OU a voz atribuída
mudou. **Bug real apanhado e corrigido antes de aplicar**: a 1ª versão
do índice tratava "nunca indexado" como "precisa de regenerar" mesmo
para faixas já correctas em Alex — numa base de 348 ficheiros sem
índice prévio (funcionalidade nova), isto teria regenerado as 348,
incluindo ~270 sem qualquer alteração real. Corrigido: na ausência de
entrada no índice, só regenera se a voz resolvida não for Alex (o
default histórico, sem necessidade de regenerar o que já existe) — a
1ª execução afectou correctamente só as 75 faixas com voz não-Alex.

Testado com Playwright: acerto na Faixa 1 de "Música Portuguesa"
(José Afonso) toca `voz/nome_pt_01.wav` (agora Duarte) seguido de
`efeitos/in_the_box.wav`, zero erros de JS.

## 2026-10-05 — Mosaico deixa de estar ligado às respostas certas

**Diagnóstico**: a duração do momento do Mosaico nunca teve uma regra
fechada aplicada no código — `animarRevelacaoGrelha()` usava um
`20000` (20s) solto, sem ligação a nada, enquanto a Bíblia §27.7 já
fixava "trecho único e contínuo de 30 segundos" desde 28 Ago 2026,
nunca aplicado a esta animação. O áudio do Mosaico (`infoMosaico.audio`)
toca o ficheiro completo sem corte — não é "Trecho A + Trecho B".

A ligação "Faixa ganha → quadrado do Mosaico" **já não existia na
grelha visual** — `renderM8Grelha()`/`animarRevelacaoGrelha()` já
revelavam os quadrados por ordem aleatória, independentes de
`quadradosGanhos` (um comentário no código, de uma tentativa anterior
revertida, confirma isto explicitamente). `quadradosGanhos` só
alimentava texto informativo ("Quadrados conquistados: X de 8",
removido) e os pontinhos de progresso da sidebar (`renderProgresso()`,
mantidos — não são sobre o Mosaico, são progresso geral da Playlist).
A fase 'mosaico_revelando' também não tinha fim automático por tempo —
só terminava por resposta certa ou pelo operador a clicar manualmente
"⏭ Revelação terminada" (`avancarRevelacao()`); só a Morte Súbita
(`mosaico_mortesubita`) tinha temporizador próprio.

**Pontuação/dinheiro**: `PONTOS_MOSAICO = 200` é um valor fixo, somado
em `confirmarMosaicoAcerto()` independentemente de quantos quadrados
estavam visíveis nesse momento — não depende do número de quadrados.
`dinheiro[]` (mealheiro) também não é tocado por `quadradosGanhos` em
nenhum sítio. Avança-se para a implementação, como já previsto.

**Bíblia**: §9.8 (ligação estrita Faixa→quadrado) e §5.11 (grelha 16,
1 por Faixa, máx. 7 reveláveis) descreviam exactamente a regra antiga,
agora substituída — texto original mantido tachado em ambas, como
registo histórico. §3.8/§27.7 actualizadas para reflectir a revelação
automática e os 30 segundos finalmente aplicados ao código.

**Implementado** (`musicbox.html`): `MOSAICO_DURACAO_MS = 30000`
(Bíblia §27.7). `animarRevelacaoGrelha()` revela os 16 quadrados (antes
só 14 de 16 — os últimos 2 ficavam sempre reservados) a intervalos
regulares (`30000/16`), guardando os timeouts para poderem ser
cancelados. Novo `mosaicoTimeoutFim` em `iniciarMosaico()` — fim
automático da fase ao fim de 30s se ninguém tiver acertado, chamando
`avancarRevelacao()` (antes só manual). `confirmarMosaicoAcerto()`
cancela a revelação automática pendente e chama a nova
`revelarMosaicoCascata()` — os quadrados que faltam abrem-se em
cascata ao longo de ~1s, em vez de aparecerem todos instantaneamente,
para a imagem ficar completa durante o anúncio do nome.
`avancarRevelacao()` chama `revelarMosaicoCompleto()` como rede de
segurança antes de decidir Morte Súbita ou fim sem vencedor — garante
"a imagem inteira no fim" em qualquer desfecho, mesmo com folga de
timing. Texto "quadrado X conquistado" removido do log de
`acertouFaixa()`; texto de estado do Mosaico já não menciona
"quadrados conquistados".

Fluxo real e Modo Teste partilham o mesmo código (`testarMosaico()` →
`iniciarMosaico()` → `confirmarMosaicoAcerto()`), sem alteração extra
necessária. Testado com Playwright: acerto a meio da revelação (4/16
visíveis aos ~8s, cascata completa os 16 após o acerto) e ninguém
acertar (fim automático aos 30s, imagem completa via a rede de
segurança) — zero erros de JS nos dois cenários.

## 2026-10-08 — Fonte de áudio dos trechos: sempre Official Audio, registada em `fonte_audio`

Confirmados dois casos reais de Trecho A cortado de um videoclipe oficial
em vez do áudio (`a10_04` "Blinding Lights" — ruído de carros da cena por
cima da música; `dec00_01` "Hey Ya!" — Trecho A começava com diálogo do
videoclipe). `volumedetect`/análise de volume não detecta este tipo de
problema — só ouvir a pré-audição antes de aprovar o corte.

**Regra**: a fonte de um trecho (re)gerado é sempre o **Official Audio**
— por ordem de preferência, canal "Topic"/upload direto da editora
("Provided to YouTube by ...") primeiro, "Official Audio" depois.
**Nunca o videoclipe** ("Official Video"/"Music Video"), mesmo que seja
o resultado mais visível numa pesquisa. O URL usado fica registado no
novo campo `fonte_audio` (string, nível de topo da faixa no
`catalogo.json`) — campo introduzido nesta decisão. `a10_04` tinha sido
corrigido antes desta regra ficar definida e usava `sources.audio`;
uniformizado no mesmo dia para `fonte_audio` — é o único campo a usar
daqui para a frente, `sources.audio` volta a ficar sempre `null`.

## 2026-10-11 — Playlists "tributo": só posições tipo "audio" seguem o motor de fonte automático

Diagnóstico pedido pelo André: as 8 faixas `beatles_*` (playlist "Tribute
Beatles", `TRB.UK.ALL.ROC.001`, único universo do catálogo tipo
`"tributo"`) apareciam sempre como "(sem playlist)" no ecrã Revisão e nos
relatórios do verificador. Causa: `playlists.json` guarda as faixas de
playlists `"tipo": "tributo"` num campo `posicoes` (um objecto por
posição, com `tipo` próprio — `audio`/`trivia`/`solo`/`foto`/`cover`/
`riff`/`capa`/`bateria` — e um `mosaico` ao nível da playlist), não no
`musicas` (lista plana de ids) que todas as outras playlists (standard/
retrato/video) usam. `carregar_mapa_playlists()` (`scripts/
verificar_trechos.py`, usada também por `scripts/
gerar_previews_defeitos.py`) só lia `musicas` — corrigido para ler
também `posicoes[].id` e `mosaico.id`, devolvendo também o `tipo` da
posição.

**Regra**: numa playlist tributo, só as posições `tipo == "audio"`
(e, por extensão, `"foto"` — não está na lista de exclusão porque
`beatles_04` ="Don't Let Me Down" tem áudio real, só o contexto da
pergunta é uma foto) seguem o motor de fonte automático (Topic >
Official Audio, verificador, etc.). As posições `trivia`/`solo`/`cover`/
`riff`/`bateria`/`capa`, e o `mosaico` da playlist, ficam "formato
especial — rever na BÍBLIA" — nunca recebem proposta automática (não são
trechos A/B comparáveis a uma música normal). Verificado que nenhuma
outra playlist do catálogo usa `posicoes` — standard/retrato/video usam
todas `musicas` normalmente; `tributo` é, para já, um caso único.

Corrigido retroactivamente em `_revisao_regeneracao.json`: `beatles_04`
(tipo `foto`) manteve-se com `playlistCodigo` corrigido para
`TRB.UK.ALL.ROC.001`; `beatles_03/05/06/08/recap` (solo/cover/riff/
bateria/mosaico) removidos do ecrã Revisão (as pré-audições já geradas
ficam órfãs em `_preview_revisao/`, não apagadas, sem efeito). Nota:
`beatles_02` (tipo `trivia`) já tinha `fonte_audio` escrito em
`catalogo.json` antes desta regra existir (lote dos 43, 9 Out) — não
revertido, fica para decisão à parte.

## 2026-10-11 — Sequência pós-acerto com vídeo do Trecho B em ecrã inteiro (decisão de formato, implementação por aprovar)

Decisão do André: depois de um acerto, a sequência passa a ser (1)
anúncio da solução (título/artista) + resposta + stinger "Music Box";
(2) entra o vídeo do Trecho B (o "expoente" da música, mesmo conceito
testado em `estudos/trecho_b_expoente/`) em **ecrã inteiro**,
sincronizado com o áudio limpo do Trecho B; (3) o vídeo pára quando o
Trecho B termina; (4) sem vídeo associado à faixa, ou sem sincronização
aprovada, cai sempre na foto do artista em ecrã inteiro (comportamento
actual, inalterado nesse caso).

Substitui a janela de decisão "▶ Encore" (verde/vermelho, 1,5s, nunca
tocava o Trecho B automaticamente — ver §5.4b, 2026-09-17) por um
Encore sempre com vídeo quando disponível.

**Implementado e ligado ao jogo no mesmo dia** (depois de diagnóstico e
proposta de integração em separado). Detalhes aprovados pelo André:

- Campos novos no `catalogo.json` (nível de topo da faixa, via
  `catalogo_patch.json`): `video_local` (ficheiro-fonte do vídeo, só
  para regenerar `clip_b` — nunca lido em jogo), `video_offset_s`
  (offset vídeo↔fonte, idem), `clip_b` (o mp4 de 15s já com vídeo+áudio
  combinados e verificados — o único campo que o jogo lê), e
  `video_sincronizado` (bool — `false` nunca mostra vídeo, cai sempre
  na foto).
- `musicbox.html`: `testeMostrarJanelaDecisaoTrechoB()`/
  `testeCliqueTrechoB()`/`testeArrancarTrechoBSemFF()` e o botão
  "▶ Encore" (`#btn-teste-trecho-b`) **removidos**. Nova função
  `iniciarEncoreComVideo(entradaCatalogo)`, chamada automaticamente no
  fim da sequência de voz (nome→"In the Box!!"→roar, depois da pausa
  `PAUSA_ANTES_ENCORE_MS`) — já não há botão nenhum para o operador
  clicar. `clip_b` + `video_sincronizado!==false` → vídeo em ecrã
  inteiro (`#encore-video-overlay`, novo, `z-index:700`, acima do
  `#momento-resposta`), áudio do próprio clip, avança no `ended`. Sem
  `clip_b` → foto do artista em ecrã inteiro por
  `ENCORE_FOTO_FALLBACK_MS` (4000ms). Nem `clip_b` nem foto → avança de
  imediato (como antes de existir Encore). Música de fundo (`audio`)
  desce a 0 com fade de `FADE_ENCORE_VIDEO_MS` (500ms) quando o Encore
  aparece, volta a `VOL_MUSICA` sozinha na Faixa seguinte
  (`iniciarFaixa()`, inalterado). A régie salta o Encore (vídeo ou foto)
  a qualquer momento com Esc ou Espaço, um só evento — sem precisar de
  clicar em nada. Pergunta Bónus (quando há) continua a disparar depois
  do Encore terminar (fluxo inalterado, `avancarParaProximaFaixaOuMosaico()`).
  Separação régie/ecrã de saída: **não entrou nesta decisão**, fica para
  uma decisão de arquitectura à parte — hoje é tudo a mesma página.
- Geradas as 2 primeiras `clip_b` (`assets/clips_b/dec00_01.mp4`,
  `assets/clips_b/dec00_03.mp4`, H.264/AAC, 15s) a partir do **Trecho B
  de produção, inalterado**, de "Hey Ya!"/"Mr. Brightside" + o vídeo de
  demonstração do estudo `estudos/trecho_b_expoente/` — alinhados por
  correlação de forma de onda directamente contra o áudio do próprio
  vídeo (não contra a fonte usada no estudo: `dec00_03` não tem
  `fonte_audio` registada em produção, não é garantido ser a mesma
  fonte que o estudo descarregou). Testado com Google Chrome real via
  Playwright directamente em `musicbox.html` (`mostrarMomentoResposta`
  com estado minimamente montado — sem passar pelo fluxo completo de
  UI): nas duas faixas, o vídeo aparece em ecrã inteiro ~4s depois do
  acerto (duração da sequência de voz + pausa), toca os 15s completos e
  avança sozinho no fim; Espaço a meio do clip esconde o overlay e
  avança em <350ms.

## 2026-10-11 — Regra "refrão mais intenso" para o Trecho B (EM ESTUDO, não adoptada)

Proposta de regra automática para escolher o Trecho B — o "expoente" da
música, usado no Encore depois de alguém acertar. **Não está adoptada**:
existe para ser ouvida às cegas contra o Trecho B actual antes de
qualquer decisão (ver STATUS.md para a página de audição e o estado).
Nada nesta entrada alterou produção, `catalogo.json` ou `playlists.json`.

Critério, tal como aprovado passo a passo pelo André ao longo de quatro
iterações (implementado em `analise_refrao.py`):

1. **Ocorrências do refrão por repetição harmónica** — `chroma_cens`
   agregada por beat + matriz de recorrência (afinidade, cosseno). Uma
   janela de 15s (a duração real do Trecho B) pontua alto se se parecer
   com partes *distantes* da música; é isso que distingue refrão de
   verso. Ocorrências sobrepostas reduzem-se à de maior score, com 15s
   de separação mínima.
2. **Filtro de repetição: só concorrem janelas com ≥70% da repetição
   máxima da faixa.** Sem este filtro, a intensidade escolhia a secção
   mais percussiva em vez do refrão — no Hey Ya! ganhava a coda do
   "shake it like a Polaroid picture" (186–201s), com o onset mais alto
   da faixa e a repetição **mais baixa** (6.0 contra 12–14.3 das zonas
   de refrão). A intensidade é para desempatar entre ocorrências do
   refrão, não para as escolher.
3. **Intensidade = MÍNIMO entre força de ataques (`onset_strength`) e
   energia acima de 2 kHz**, ambas normalizadas dentro da faixa. O
   mínimo e não a média, para exigir confluência nos dois eixos: com
   média 50/50, 3 dos 4 vencedores nos Anos 80 tinham uma componente a
   1.00 e a outra a ~0.05 — uma "intensidade 0.52" que era máximo num
   eixo e mínimo no outro. O valor do mínimo vencedor funciona como
   medida de confiança (Hey Ya! 0.93; Anos 80 entre 0.07 e 0.39).
4. **Cross-check pela letra sincronizada (LRCLIB)** — conta as linhas
   repetidas do tema que caem dentro da janela; havendo janelas
   confirmadas pela letra, a escolha restringe-se a essas. Conta
   **todas** as linhas repetidas (≥2 ocorrências), não só a mais
   frequente: um tema pode ter vários hooks, e usar só o mais frequente
   marcava 3 de 12 janelas no Hey Ya! (ignorando as 10 ocorrências de
   "hey ya" e as 2 de "alright alright...", esta última precisamente
   onde está o Trecho B actual) e fazia o cross-check decidir em vez da
   energia.
5. **Exclusões** — janelas que se sobreponham ao Trecho A, ou que
   deixem menos de 30s de música depois.

**RMS puro foi descartado** (era a métrica da primeira versão da regra):
em masterizações comprimidas não discrimina. No Hey Ya!, todos os
candidatos ficaram entre 0.3056 e 0.3415 (~11%) e o vencedor ganhava por
1.3% — ruído do limiter, não sinal.

**Tempos em falta no catálogo.** Metade das faixas tem
`trecho_a/b.inicio` e `.fim` a `null` apesar de os mp3 existirem (todo o
pack dos Anos 80, por exemplo), e sem eles não há filtro de sobreposição
com o A nem comparação com o B actual. `localizar_trecho()` recupera-os
por correlação do envelope de energia (RMS) do trecho contra o do
source: o envelope aguenta as diferenças de encoding e de volume entre o
mp3 de produção e o source re-descarregado, que uma correlação de
amostras não perdoaria. Devolve também a nitidez do pico (pico/mediana),
para se desconfiar quando o trecho não veio daquele source — medido em
`80_02` com o source certo: 9.8x (A) e 8.9x (B). **Por decisão do André
(11 Out), estes tempos só são usados em memória: gravá-los no catálogo
fica para um commit próprio, quando ele pedir.**

**Ambiente.** `librosa` não instala no Python 3.14 do sistema (o
`llvmlite` não compila nesta máquina). Os dois scripts correm com
`~/.venvs/musicbox-audio/bin/python` (3.12, com numpy/scipy/librosa) —
venv fora do repositório, como o `scripts/.venv/` do verificador de
trechos.
