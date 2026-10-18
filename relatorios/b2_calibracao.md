# Calibração do B2 — que métricas separam "B2 melhor" de "B actual melhor"?

Amostra: **18 pares** avaliados pelo André (`relatorios/b2_avaliacao_andre.csv`) — 13 de Anos 50/60/80, mais 5 de Anos 2000 acrescentados em 18 Out 2026. **Amostra pequena — nada aqui é estatisticamente significativo**, são só observações directas dos números, não uma regra fechada.

## Dados usados (de `analise_refrao.py`, via `relatorios/proposta_b2_50_60.md`/`proposta_b2_80.md`/`relatorios/diagnostico_b2_4packs_demo.md`)

| id | resultado | confiança | LRCLIB confirmado | posição relativa (início B2 / duração) | desvio (s) |
|---|---|---|---|---|---|
| dec60_02 | B2 melhor | 0,473 | sim | 0,24 | +35 |
| dec60_05 | B2 melhor | 0,605 | sim | 0,52 | +68 |
| dec00_02 | B2 melhor | 0,697 | não registado* | 0,49 | +82 |
| dec00_05 | B2 melhor | **0,295** | não registado* | 0,46 | +59 |
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
| dec00_04 | B actual melhor | 0,329 | não registado* | 0,51 | +88 |
| dec00_06 | B actual melhor | 0,303 | não registado* | 0,39 | +51 |
| dec00_07 | B actual melhor | 0,371 | não registado* | 0,34 | +53 |

\* O diagnóstico original do Anos 2000 (`diagnostico_b2_4packs_demo.md`) não registou a confirmação por LRCLIB separadamente — só a confiança final.

## Observações, por métrica

**Confiança (energia — min(onset, alta))** — **actualizado com os 5 novos pontos, muda a leitura anterior**: `dec00_05` é "B2 melhor" com confiança **0,295** — mais baixa que TODOS os 6 casos "B actual melhor" (0,220 a 0,467, excepto o próprio `dec50_07` a 0,220). Isto **invalida a separação quase limpa que parecia existir com 13 pares** (onde o mínimo de "B2 melhor" já tocava o máximo de "B actual melhor"; agora o mínimo de "B2 melhor" fica mesmo dentro da gama de "B actual melhor"). Médias por grupo: "B actual melhor" 0,35; "B2 melhor" 0,52; "Igual" 0,62 — a ordem média ainda é a mesma, mas a sobreposição entre grupos é grande demais para servir de filtro sozinha.

**LRCLIB (confirmação por letra)**: não registado para os 5 novos pontos (o diagnóstico original do Anos 2000 não gravou esta coluna) — não é possível reforçar nem contrariar a observação anterior (2 de 3 "B actual melhor" sem LRCLIB) com os dados novos.

**Posição relativa (início do B2 / duração da faixa)**: continua sem padrão com os 5 novos pontos — "B2 melhor" agora tem 0,24/0,46/0,49/0,52 (espalhado), "B actual melhor" tem 0,34/0,34/0,39/0,48/0,51/0,51 (também espalhado). Não separa.

**Desvio temporal (B2 − B actual)**: confirmado de novo — `dec00_02` (B2 melhor) tem o 2º maior desvio da amostra toda (+82s) e `dec00_06` (B actual melhor) tem um dos mais pequenos (+51s). Continua sem relação com o resultado.

**Repetição** (score de repetição harmónica ≥70% do máximo da faixa): continua não disponível nos relatórios já gerados (só a janela vencedora fica registada) — fica por fazer se for importante.

## Conclusão revista (18 pares)

Com mais dados, a métrica que parecia mais promissora (confiança) **deixou de separar os grupos de forma utilizável** — `dec00_05` por si só mostra que uma proposta de baixa confiança pode ser claramente melhor que o actual, e `dec50_06` mostra que uma de confiança parecida pode ser claramente peor. **Não há, nesta amostra, nenhuma métrica do `analise_refrao.py` (energia, repetição, letra, posição, desvio) que separe com confiança "B2 melhor" de "B actual melhor"** — a proposta de filtro da versão anterior deste relatório (confiança ≥0,45 E LRCLIB/confiança≥0,6) esconderia agora 2 dos 4 "B2 melhor" (`dec00_05` e, por extensão do mesmo limiar, risco igual em casos futuros parecidos), o que é demasiado caro para um filtro automático. **Fica sem proposta de filtro nova** — a única regra que esta amostra sustenta com confiança é a já fechada em BIBLIA.md/DECISIONS.md: ouvir sempre faixa a faixa, nunca decidir por uma métrica só.
