# Proposta B2 — Anos 80 (dry-run, nada gravado)

Gerado com `gerar_b2_teste_regra.py --pack STD.INT.80.MIX.001 --todas` (sem `--gerar-mp3`). **Nenhum ficheiro `.mp3` nem `catalogo.json` foi tocado.**

## Faixas com Trecho A registado (1 de 7)

| Faixa | Título | B actual | B2 proposto | Confiança | Concorda? |
|---|---|---|---|---|---|
| 80_01 | Take On Me | 70,1–79,9s (localizado por correlação, pico 7,5x — não vem do catálogo, que também o tinha em branco) | 69–84s | 0,595 (LRCLIB: confirmado) | **SIM — 100% de sobreposição** |

Único resultado do pack onde a regra do refrão mais intenso concorda com o Trecho B em uso. Não precisa de alteração.

## 6 faixas SEM Trecho A no catálogo (80_02 a 80_07)

`inicio`/`fim` de `trecho_a` estão a `null` em `catalogo.json` para estas 6 — os ficheiros `80_0{2..7}_a.mp3` existem em disco, mas os tempos de corte nunca foram gravados (nota já deixada no próprio script). Sem saber onde o Trecho A começa na fonte completa, o script também não consegue avaliar o Trecho B (precisa do fim do A para checar sobreposição) — por isso nenhuma das 6 tem proposta B2.

O script tentou recuperar os tempos sozinho (localizar o `_a.mp3` já cortado dentro da fonte completa, por correlação de áudio) e falhou nas 6, por ambiguidade — dois instantes da música parecem-se demais entre si:

| Faixa | Título | Candidatos empatados | Margem | Observação |
|---|---|---|---|---|
| 80_02 | Sweet Child O' Mine | 6s vs 291s | 13,4% | 6s é claramente o início (riff icónico); 291s é repetição tardia do mesmo riff |
| 80_03 | The Power of Love | 256s vs 264s | 9,5% | **os dois candidatos são tardios** — nenhum perto do início; caso genuinamente atípico |
| 80_04 | Don't You Want Me | 4s vs 167s | 10,4% | 4s é o início |
| 80_05 | The Final Countdown | 4s vs 260s | 0,0% (empate quase total) | 4s é o início; o sintetizador de abertura repete-se quase identico mais tarde |
| 80_06 | Every Breath You Take | 1s vs 17s | 20,8% | ambos muito perto do início (intro curta, repetição interna) |
| 80_07 | Billie Jean | 4s vs 10s | 14,2% | ambos muito perto do início (groove de baixo repete-se em 6s) |

## Opções para resolver (nenhuma aplicada — escolha do André)

1. **Regra de desempate por posição** (fix de código, barato): quando há ambiguidade, preferir sempre o candidato mais próximo de 0s — resolveria 80_02, 80_04, 80_05, 80_06, 80_07 de imediato (todos têm um candidato bem mais cedo). **Não resolve 80_03** (os dois candidatos são tardios, não há "o mais cedo é óbvio" para aplicar).
2. **Restringir a janela de busca** ao primeiro ~60–90s da fonte (Trecho A é sempre o início, por convenção de todo o resto do catálogo) — evita comparar contra repetições tardias em vez de só desempatar por elas. Mesma cobertura que a opção 1, mais robusto a futuros casos.
3. **Confirmação manual por audição**: o André ouve os primeiros segundos de `80_0X_a.mp3` e diz a que ponto da fonte completa corresponde — resolve as 6, incluindo 80_03, mas é trabalho manual faixa a faixa.
4. **Combinação 1+3**: aplicar a regra de posição às 5 fáceis e deixar só 80_03 para audição manual.

Em qualquer opção, o passo seguinte (gerar a proposta B2 de Trecho B para estas 6) só corre depois de `trecho_a.inicio`/`fim` estarem gravados no catálogo — que é uma alteração de dados, fora do âmbito desta tarefa (sem aprovação, não se grava nada).
