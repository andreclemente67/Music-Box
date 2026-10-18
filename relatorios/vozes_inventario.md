# Inventário de ficheiros de voz (só leitura)

**Aviso prévio**: o pedido mencionava "16 já confirmados" e "~307 por processar" — não encontrei esses números em lado nenhum (STATUS.md/DECISIONS.md/BIBLIA.md) nem eles correspondem ao que os ficheiros em disco mostram. Os números abaixo vêm directamente de contar ficheiros em `voz/`/`efeitos/` contra `catalogo.json`/`playlists.json` — por favor confirma se o pedido original era sobre outra coisa (ex. feedback/QA de qualidade de pronúncia, não existência de ficheiro — ver nota no fim).

## Por tipo

| Tipo | Ficheiro(s) | Existem | Precisos | Em falta |
|---|---|---|---|---|
| ROAR (roar de multidão) | `efeitos/roar.wav` | **0** | 1 (partilhado por todas as faixas) | **1 — em falta** |
| "In the Box!!" | `efeitos/in_the_box.wav` | 1 | 1 | 0 |
| Pergunta Bónus (efeito sonoro) | `efeitos/bonus.wav` | 1 | — (uso à parte, não entra nesta sequência) | — |
| Nomes (`nome_<id>.wav`) | 348 ficheiros | 348 | 348 (1 por faixa do catálogo) | **0** |
| Mosaico (`mosaico_<código>.wav`) | 38 ficheiros | 38 | 38 (1 por playlist com `mosaico`) | **0** |
| Apresentação (`descritivo_<código>.wav`) | 41 ficheiros | 41 | 41 (1 por playlist) | **0** |
| Perguntas (Tributo, tipo `trivia`) | — | — | **nenhum** | **não aplicável** |

**Perguntas (trivia) — não é um ficheiro de voz em falta, é por desenho**: confirmado no código (`musicbox.html`, tratamento de `pos.tipo === 'trivia'`) — "Sem áudio — pergunta visível para o apresentador". A única posição `trivia` do catálogo (`beatles_02`, Tribute Beatles) mostra o texto da pergunta no ecrã para o apresentador ler em voz alta; nunca houve um ficheiro de voz planeado para isto.

**Conclusão principal**: ao contrário do que o pedido assumia, `nome_<id>.wav`/`mosaico_<código>.wav`/`descritivo_<código>.wav` estão **100% completos** — 0 em falta nos três. O único ficheiro de voz/efeito genuinamente em falta é `efeitos/roar.wav` (1 ficheiro) — e mesmo esse já tem fallback seguro no código (`roarDisponivel===false` salta direto para "In the Box!!", nunca trava o jogo).

## "16 confirmados" — leitura mais próxima que encontrei

`voz/pronuncia.json` tem **22** excepções manuais de voz por artista (não 16) — atribuem uma voz edge-tts específica a um artista em vez do default (`Alex r205`) ou da regra de prefixo PT/BR. Destas 22, o STATUS.md (sessão anterior) marca **4 como "por confirmar"**: Vangelis e os 3 compositores japoneses de videojogos (Koji Kondo, Nobuo Uematsu, Yoko Shimomura) — ficam em Alex até o André decidir entre a voz grega/japonesa nativa (testadas e rejeitadas, "soam estranhas") ou a fonética em PT (Duarte). Isso deixa **18** excepções já fechadas — perto de 16, mas não exacto; não encontrei uma lista de exactamente 16 em lado nenhum.

## "~307 por processar" — leitura mais próxima que encontrei

Das 348 faixas do catálogo, **269** usam a voz default `Alex r205` (sem regra de prefixo PT/BR nem excepção manual) e **79** têm voz atribuída especificamente (22 por excepção de artista + o resto por prefixo de playlist PT/BR). Isto é "faltam decidir/confirmar uma voz dedicada" (cobertura ainda genérica), **não** "falta gravar/gerar o ficheiro" — o ficheiro `nome_<id>.wav` já existe e já toca para as 348, só a maioria usa a voz inglesa default em vez de uma voz dedicada à língua/nacionalidade do artista.

## Ordem sugerida de processamento (com base no que está genuinamente em falta/pendente)

1. **`efeitos/roar.wav`** — único ficheiro realmente em falta; rápido de resolver (gravar ou encontrar um efeito sonoro de "roar de multidão/estúdio" royalty-free) e desbloqueia o som completo da sequência de Encore em todas as faixas.
2. **As 4 vozes "por confirmar"** (Vangelis + 3 japoneses) — decisão pendente do André, ouvir as alternativas já geradas antes de fechar.
3. **Revisão dos 269 "Alex default"** (se for esse o objectivo real do pedido) — não é geração de ficheiros novos (já existem), é uma passagem de QA por língua/nacionalidade do artista para decidir se algum merece voz dedicada como os 22 já feitos; não há lista pronta disto, teria de ser construída a pedido (ex. agrupar por geografia/língua do artista em `catalogo.json`).
