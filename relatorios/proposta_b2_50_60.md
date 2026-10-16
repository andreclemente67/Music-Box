# Proposta B2 — Anos 50 e Anos 60 (dry-run, nada gravado)

Gerado com `gerar_b2_teste_regra.py --pack <id> --todas` (sem `--gerar-mp3`), motor `analise_refrao.py` (chroma CENS beat-sync + matriz de recorrência + RMS, cross-check LRCLIB). **Nenhum ficheiro `.mp3` nem `catalogo.json` foi tocado** — só leitura/análise.

Omitidas por instrução explícita do André: `dec50_05`, `dec60_07`.

Critério "cai depois do B actual": compara o início do B2 proposto com o fim do Trecho B actual (18–30s em todas as faixas deste pack) — em todas, o B2 cai muito depois.

## Anos 50 (`STD.INT.50.MIX.001`)

| Faixa | Título | B actual | B2 proposto | Confiança* | Cai depois do B actual? |
|---|---|---|---|---|---|
| dec50_01 | Rock Around the Clock | 18–30s | 71–86s | 0,649 (LRCLIB: não confirmado) | Sim (+53s) |
| dec50_02 | Hound Dog | 18–30s | 67–82s | 0,559 (LRCLIB: confirmado) | Sim (+49s) |
| dec50_03 | Johnny B. Goode | 18–30s | 69–84s | 0,523 (LRCLIB: confirmado) | Sim (+51s) |
| dec50_04 | Great Balls of Fire | 18–30s | 99–114s | 0,422 (LRCLIB: confirmado) | Sim (+81s) |
| dec50_06 | Mack the Knife | 18–30s | 92–107s | 0,467 (LRCLIB indisponível, HTTP 503 — só repetição harmónica) | Sim (+74s) |
| dec50_07 | Blue Suede Shoes | 18–30s | 70–85s | 0,220 (LRCLIB indisponível, HTTP 503 — só repetição harmónica) | Sim (+52s) |

**0 de 6 concordam com o B actual** (todas divergem, desvio +49s a +81s). `dec50_06`/`dec50_07` sem confirmação por letra (LRCLIB em baixo nesta corrida — 503), escolha só por repetição harmónica + energia.

## Anos 60 (`STD.INT.60.MIX.001`)

| Faixa | Título | B actual | B2 proposto | Confiança* | Cai depois do B actual? |
|---|---|---|---|---|---|
| dec60_01 | Respect | 18–30s | 93–108s | 1,000 (LRCLIB: confirmado) | Sim (+75s) |
| dec60_02 | (I Can't Get No) Satisfaction | 18–30s | 53–68s | 0,473 (LRCLIB: confirmado) | Sim (+35s) |
| dec60_03 | Good Vibrations | 18–30s | 86–101s | 0,380 (LRCLIB: confirmado) | Sim (+68s) |
| dec60_04 | Like a Rolling Stone | 18–30s | 210–225s | 0,602 (LRCLIB: confirmado) | Sim (+192s) |
| dec60_05 | My Girl | 18–30s | 86–101s | 0,605 (LRCLIB: confirmado) | Sim (+68s) |
| dec60_06 | Purple Haze | 18–30s | 110–125s | 0,625 (LRCLIB: confirmado) | Sim (+92s) |

**0 de 6 concordam com o B actual** (desvio +35s a +192s — `dec60_04` é caso extremo, o refrão mais intenso só aparece a 3:30 numa faixa de 6 min).

*Confiança = `intensidade` (min(score de onset, score de energia "alta")) entre as ocorrências do refrão já filtradas por repetição ≥70% do máximo da faixa e ≥30s de música depois. Quando há LRCLIB, a escolha exige confirmação lírica (linha de refrão repetida dentro da janela); sem LRCLIB, só repetição harmónica+RMS.

**Leitura geral**: em nenhuma das 12 faixas analisadas (50+60) a regra do refrão mais intenso concorda com o Trecho B actual (18–30s fixo, herdado de um padrão antigo de "~20s de música"). Todas as propostas caem bem mais tarde na faixa — padrão já visto noutros packs (ver `relatorios/diagnostico_b2_4packs_demo.md`). Nada aplicado; decisão de regenerar fica para o André.
