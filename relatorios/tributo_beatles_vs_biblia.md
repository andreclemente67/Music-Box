# Tributo Beatles — posições especiais vs. BIBLIA.md §29.1.3

Levantamento só de leitura (`playlists.json`/`catalogo.json` vs. BIBLIA.md) — nada alterado.

## O que a BIBLIA diz (§29.1.3, "Playlist Tributo")

> "As 8 posições são mistas e montadas por curadoria: podem ser áudio, trivia, solo, foto, cover, riff, bateria ou logo. Não há ordem fixa nem estrutura predefinida."

Só nomeia os 8 tipos possíveis — não descreve o schema de cada posição (campos) nem a mecânica de jogo de cada tipo.

## As 8 posições reais do Tribute Beatles (`TRB.UK.ALL.ROC.001`)

| pos | tipo | id | chave | pergunta/dica | mosaico (flag) |
|---|---|---|---|---|---|
| 1 | audio | beatles_01 | Come Together | — | true |
| 2 | trivia | beatles_02 | **The Beatles** | pergunta: "Back in the U.S.S.R." | false |
| 3 | solo | beatles_03 | The End | dica: 3 guitarristas alternam solos | true |
| 4 | foto | beatles_04 | Rooftop Concert | dica: última actuação ao vivo | false |
| 5 | cover | beatles_05 | Something | dica: composta por George Harrison | true |
| 6 | riff | beatles_06 | A Hard Day's Night | dica: acorde mais famoso do rock | true |
| 7 | **capa** | *(nenhum — id: null)* | Revolver | dica: arte de Klaus Voormann | false |
| 8 | bateria | beatles_08 | The End | dica: único solo de Ringo Starr | true |

Mosaico separado da playlist (posição 9, fora das 8): `beatles_recap` (categoria "album", "Abbey Road — The Beatles (1969)").

## O que difere da BIBLIA

1. **Tipo "capa" não está na lista da BIBLIA** — a Bíblia lista "logo" como um dos 8 tipos possíveis; a posição 7 real usa `tipo: "capa"`, que não aparece em lado nenhum do texto. `"logo"` nunca é usado nesta playlist. É possível que "logo" na Bíblia se refira na verdade ao Universo `LOGO-001` (playlist própria, não uma posição dentro de Tributo) — a Bíblia não distingue os dois.
2. **Posição sem id de catálogo** — a posição 7 (`capa`) não tem `id` (`null`), só `imagem` directa (`BEATLES_07_capa.jpg`) — nenhuma entrada em `catalogo.json`, nenhum áudio. A Bíblia não menciona que uma posição de Tributo pode não ter faixa nenhuma associada.
3. **Campo `chave` com semântica inconsistente no tipo `trivia`** — em todas as outras posições, `chave` é o título da música (ex. "Come Together", "The End"). Na posição 2 (`trivia`), `chave` é **o nome da banda** ("The Beatles") e o título da música-pista está em `pergunta` ("Back in the U.S.S.R."). A Bíblia não documenta esta troca de significado por tipo.
4. **Schema por posição não documentado** — a Bíblia só nomeia os tipos; não diz que cada posição carrega `dica`/`pergunta`/`chave`/`mosaico` (flag de elegibilidade ao Mosaico final, independente do Mosaico da playlist) nem que posições com `id` continuam a ter `trecho_a`/`trecho_b`/`full`/`imagem` completos em `catalogo.json`, exactamente como uma faixa Standard — a única diferença real está em como o Studio/jogo lê o campo `tipo`, não no schema de dados.
5. **Trivia com resposta óbvia** — não é uma divergência da Bíblia, mas um ponto a levantar ao André: a pergunta de trivia (posição 2) tem como resposta "The Beatles", a própria banda do tributo — pode valer a pena confirmar se é intencional (ex. a pergunta real é sobre outra coisa e "chave" é só a legenda da faixa, não a resposta mostrada ao jogador).
