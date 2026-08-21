# Music Box — Tarefas

## Em curso

- [ ] Confirmar no browser (não testável neste ambiente) que "Guardar playlists.json" no Studio já não pede autorização de pasta — deve escrever via `_servidor_escrita.py` (porta 8002) sem diálogo nenhum. Ver `DECISIONS.md` 2026-08-13.
- [ ] Testar no browser os 5 modos de "✦ Gerar com IA" (URL/Tema/Categoria/Semente múltipla/Playlist YouTube) — trocar sub-tabs, ler uma playlist real do YouTube e rever/editar a lista, gerar em cada modo, confirmar retentativas por artista repetido e o fallback claro após 3 tentativas. Só validado com testes isolados fora do browser + 1 chamada real à API. Ver `DECISIONS.md` 2026-08-21.
- [ ] Testar no browser o feedback ao vivo na Mesa de Montagem durante a geração de trechos A/B (contador + estado por faixa, incluindo depois de clicar "Ver na Mesa de Montagem" antes do lote terminar). Ver `DECISIONS.md` 2026-08-21.

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