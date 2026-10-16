# Reconciliação — 95 "defeito real" vs 42 aprovadas + 34 por ouvir

Diagnóstico só de leitura (STATUS.md/DECISIONS.md) — nada gravado.

## Os números, por ordem cronológica

1. **9 Out 2026** — reavaliação do verificador confirma **95 "defeito real"** em 348 faixas (156 OK, 95 defeito, 22 inconclusivo, 50 formato especial — `relatorios/reavaliacao_falhas.csv`). Pré-audições geradas para as 95, carregadas em `_revisao_regeneracao.json` com `estado: "pendente"`.
2. **11 Out 2026, 1ª correcção** — diagnóstico encontra **47 faixas** marcadas "pendente" no manifesto que já tinham sido aplicadas por outra via (`aprovar_lote.py` ou regeneração em bloco antiga) sem o manifesto ser actualizado — corrigidas para `"regenerado"` (0 ficheiros tocados, só o estado). Pelo menos 2 destas 47 pertencem ao conjunto dos 95 (Metal: `metal_02`/`metal_03` — ver `relatorios/bugs_studio_pendentes.md`); não há confirmação no STATUS.md de quantas das 47 vinham especificamente dos 95 vs. de outras "ondas" de revisão mais antigas (6–7 Out, cohort diferente — 101 faixas, `_revisao_regeneracao.json` tem várias origens misturadas no mesmo ficheiro).
3. **11 Out 2026, 2ª correcção** — reavaliadas as **76 "pendente" com pré-audição já gerada** contra 6 salvaguardas (verificador OK, canal Topic/Official Audio, título sem Remix/Live/etc., A/B sem sobreposição ~15s, fonte ≤320s, nunca posição tributo). Resultado: **42 aprovadas e aplicadas** + **34 ficam pendentes**.

## A soma que falta

`95 − 76 = 19` faixas dos 95 originais não entraram na reavaliação dos "76". Duas explicações confirmadas, uma por confirmar:

- **5 confirmadas — órfãs do bug de playlist "tributo"**: o pack `(sem playlist)` dos 95 incluía `beatles_03, beatles_04, beatles_05, beatles_06, beatles_08, beatles_recap` (6 entradas). A correcção do mapeamento de playlists tipo `tributo` (11 Out) manteve só `beatles_04` no ecrã Revisão (passou a ter `playlistCodigo` correcto, hoje em `TRB.UK.ALL.ROC.001` — é 1 dos 34 pendentes actuais) e **removeu as outras 5** (`beatles_03/05/06/08/recap`) do ecrã — não apagadas, só ficaram órfãs em `_preview_revisao/`, fora do fluxo de aprovação. **Isto corresponde exactamente aos "5 tributo" referidos no pedido.**
- **Resta explicar 14** (19 − 5). Hipótese mais provável, não confirmada por este diagnóstico: parte das 47 faixas corrigidas de "pendente"→"regenerado" na 1ª correcção (ponto 2 acima) pertencia ao conjunto dos 95 — ou seja, já tinham sido corrigidas por outra via antes de 9 Out, o verificador continuava a vê-las como "defeito" porque o CSV estático não foi reavaliado, e por isso entraram nos 95 e tiveram pré-audição gerada inutilmente; a 1ª correcção retirou-as de "pendente" antes da reavaliação dos 76 correr, por isso não entraram nela. Não há, no STATUS.md, a lista nominal das 47 para confirmar quantas são destas 14 — precisa de cruzar `relatorios/reavaliacao_falhas.csv` (lista dos 95, por pack) com o histórico de `_revisao_regeneracao.json` antes/depois da 1ª correcção.

## Resumo da equação

```
95 (defeito real, 9 Out)
 − 5  (beatles órfãos, bug tributo, removidos do ecrã)
 − 14 (hipótese: já corrigidos antes de 9 Out por outra via — NÃO CONFIRMADO)
 = 76 (entraram na reavaliação final, 11 Out)
 − 42 (aprovadas e aplicadas)
 − 34 (ficam pendentes)
 = 0
```

**O que falta para fechar com certeza**: confirmar a lista nominal das 47 faixas "pendente→regenerado" da 1ª correcção e cruzá-la com os IDs dos 95 — só assim os "14" deixam de ser hipótese. Não gravei nada; é só uma leitura adicional de `_revisao_regeneracao.json`/`relatorios/reavaliacao_falhas.csv` (ambos existentes, nenhum precisa de ser alterado).
