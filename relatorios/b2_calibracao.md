# Calibração do B2 — que métricas separam "B2 melhor" de "B actual melhor"?

Amostra: 13 pares avaliados pelo André (`relatorios/b2_avaliacao_andre.csv`). **Amostra pequena — nada aqui é estatisticamente significativo**, são só observações directas dos números e uma proposta de filtro a testar com mais dados, não uma regra fechada.

## Dados usados (de `analise_refrao.py`, via `relatorios/proposta_b2_50_60.md`/`proposta_b2_80.md`)

| id | resultado | confiança | LRCLIB confirmado | posição relativa (início B2 / duração) | desvio (s) |
|---|---|---|---|---|---|
| dec60_02 | B2 melhor | 0,473 | sim | 0,24 | +35 |
| dec60_05 | B2 melhor | 0,605 | sim | 0,52 | +68 |
| dec50_01 | Igual | 0,649 | não (sem filtro LRCLIB) | 0,55 | +53 |
| dec50_02 | Igual | 0,559 | sim | 0,50 | +49 |
| dec50_03 | Igual | 0,523 | sim | 0,42 | +51 |
| dec50_04 | Igual | 0,422 | sim | 0,41 | +81 |
| dec60_01 | Igual | 1,000 | sim | 0,63 | +75 |
| dec60_04 | Igual | 0,602 | sim | 0,58 | +192 |
| dec60_06 | Igual | 0,625 | sim | 0,64 | +92 |
| 80_01 | Igual | 0,595 | sim | 0,30 | -1 |
| dec50_06 | B actual melhor | 0,467 | **não disponível (LRCLIB 503)** | 0,48 | +74 |
| dec50_07 | B actual melhor | 0,220 | **não disponível (LRCLIB 503)** | 0,51 | +52 |
| dec60_03 | B actual melhor | 0,380 | sim | 0,34 | +68 |

## Observações, por métrica

**Confiança (energia — min(onset, alta))**: média de "B actual melhor" = 0,36; média de "B2 melhor" = 0,54; média de "Igual" = 0,62 — ordem certa (actual melhor < B2 melhor < igual), mas **os grupos tocam-se**: o mínimo de "B2 melhor" (0,473) é quase igual ao máximo de "B actual melhor" (0,467), e "Igual" tem um caso (`dec50_04`, 0,422) mais baixo que os dois "B2 melhor". Direcção certa, não é um corte limpo.

**LRCLIB (confirmação por letra)**: 2 das 3 "B actual melhor" não tiveram LRCLIB disponível (503, não é "a letra não confirmou", é "a pesquisa falhou") — só `dec60_03` teve LRCLIB confirmado e ainda assim perdeu para o actual. Nas outras 10, LRCLIB esteve disponível em 9 (só `dec50_01` não, e ficou "Igual", não "B2 melhor"). **Padrão fraco e com poucos casos** (3) para confiar, mas aponta: sem confirmação por letra, mais hipótese de o B2 não convencer.

**Posição relativa (início do B2 / duração da faixa)**: sem padrão — "B2 melhor" tem uma faixa muito cedo (0,24) e outra a meio (0,52); "Igual" e "B actual melhor" espalham-se por toda a gama (0,30 a 0,64). Não separa nada aqui.

**Desvio temporal (B2 − B actual)**: confirmado (ver DECISIONS.md "B2 formalizado...") — não separa: desvios grandes (`dec60_04` +192, Igual) e pequenos (`dec60_02` +35, B2 melhor) aparecem nos dois lados sem relação com o resultado.

**Repetição** (score de repetição harmónica ≥70% do máximo da faixa, usado como filtro de entrada): não disponível separadamente nos relatórios já gerados para os 13 pares (só a janela vencedora fica registada, não o valor de repetição de cada candidato) — não foi possível avaliar esta métrica sem reprocessar as faixas; fica por fazer se for importante.

## Proposta de filtro (não aplicado, para testar com mais avaliações)

Dado que nenhuma métrica isolada separa bem, e a confiança é a que mais se aproxima: **só propor B2 para revisão quando confiança ≥ 0,45 E (LRCLIB confirmado OU confiança ≥ 0,6)**. Resultado nesta amostra: exclui as **3 "B actual melhor"** correctamente (`dec50_06` fica de fora por não ter LRCLIB nem confiança ≥0,6, mesmo com confiança 0,467 ≥0,45; `dec50_07` e `dec60_03` ficam de fora já na 1ª condição, confiança <0,45). Não exclui nenhum "B2 melhor". **Mas exclui também 1 dos 8 "Igual"** (`dec50_04`, confiança 0,422 <0,45) — um falso negativo: um B2 tão bom como o actual que o filtro teria escondido da revisão. **Ressalva forte**: com só 13 pares, 1 falso negativo e grupos que se tocam na fronteira (0,467 vs 0,473), este filtro está provavelmente ajustado ao ruído desta amostra — só vale a pena fixá-lo a sério depois de testar contra mais avaliações do André, e mesmo assim como filtro de "menos prioridade", não de exclusão total.
