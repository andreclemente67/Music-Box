# Diagnóstico Trecho A / B2 — 4 packs de demo (14 Out 2026)

Só diagnóstico, nada escrito em `catalogo.json`/`playlists.json`. Motor: `analise_refrao.py` +
`gerar_b2_teste_regra.py --pack <id> --todas` (sem `--gerar-mp3`), um processo por pack, em paralelo.
Limiares desta tabela (mais estritos que os de produção, BIBLIA §13.2 usa 80%): B2 marcado **ZONA DE
SAÍDA** se acabar depois de **75%** da duração; **INTENSIDADE BAIXA** se confluência <0,15.

| Pack | Faixa | Duração | Trecho A actual | B actual | B2 proposto | B2 em % | Intensidade | Situação |
|---|---|---|---|---|---|---|---|---|
| STD.INT.80.MIX.001 | 80_01 | 228.5s | 0–12s (catálogo) | 70–80s (correlação) | 69–84s | 37% | 0.595 | OK |
| STD.INT.80.MIX.001 | 80_02 | 356.1s | ambíguo (correlação) | — | — | — | — | SEM TRECHO A |
| STD.INT.80.MIX.001 | 80_03 | 330.1s | ambíguo (correlação) | — | — | — | — | SEM TRECHO A |
| STD.INT.80.MIX.001 | 80_04 | 240.5s | ambíguo (correlação) | — | — | — | — | SEM TRECHO A |
| STD.INT.80.MIX.001 | 80_05 | 309.0s | ambíguo (correlação) | — | — | — | — | SEM TRECHO A |
| STD.INT.80.MIX.001 | 80_06 | 228.4s | ambíguo (correlação) | — | — | — | — | SEM TRECHO A |
| STD.INT.80.MIX.001 | 80_07 | 294.2s | ambíguo (correlação) | — | — | — | — | SEM TRECHO A |
| STD.INT.00.MIX.001 | dec00_01 | 235.5s | 0–15s (catálogo) | 142–157s (catálogo) | 144–159s | 68% | 0.927 | OK |
| STD.INT.00.MIX.001 | dec00_02 | 236.7s | 0–12s (catálogo) | 18–30s (catálogo) | 100–115s | 49% | 0.697 | OK |
| STD.INT.00.MIX.001 | dec00_03 | 222.2s | 0–12s (catálogo) | 18–30s (catálogo) | 88–103s | 46% | 0.259 | OK |
| STD.INT.00.MIX.001 | dec00_04 | 238.3s | 0–12s (catálogo) | 18–30s (catálogo) | 106–121s | 51% | 0.329 | OK |
| STD.INT.00.MIX.001 | dec00_05 | 199.1s | 0–12s (catálogo) | 18–30s (catálogo) | 77–92s | 46% | 0.295 | OK |
| STD.INT.00.MIX.001 | dec00_06 | 216.3s | 0–12s (catálogo) | 18–30s (catálogo) | 69–84s | 39% | 0.303 | OK |
| STD.INT.00.MIX.001 | dec00_07 | 254.1s | 0–12s (catálogo) | 18–30s (catálogo) | 71–86s | 34% | 0.371 | OK |
| STD.INT.50.MIX.001 | dec50_01 | 129.9s | 0–12s (catálogo) | 18–30s (catálogo) | 71–86s | 66% | 0.649 | OK |
| STD.INT.50.MIX.001 | dec50_02 | 133.9s | 0–12s (catálogo) | 18–30s (catálogo) | 67–82s | 61% | 0.559 | OK |
| STD.INT.50.MIX.001 | dec50_03 | 162.6s | 0–12s (catálogo) | 18–30s (catálogo) | 69–84s | 52% | 0.523 | OK |
| STD.INT.50.MIX.001 | dec50_04 | 242.8s | 0–12s (catálogo) | 18–30s (catálogo) | 99–114s | 47% | 0.422 | OK |
| STD.INT.50.MIX.001 | dec50_05 | 139.6s | 0–12s (catálogo) | 18–30s (catálogo) | 31–46s | 33% | **0.000** | INTENSIDADE BAIXA <0,15 |
| STD.INT.50.MIX.001 | dec50_06 | 190.5s | 0–12s (catálogo) | 18–30s (catálogo) | 92–107s | 56% | 0.467 | OK |
| STD.INT.50.MIX.001 | dec50_07 | 138.4s | 0–12s (catálogo) | 18–30s (catálogo) | 70–85s | 61% | 0.220 | OK |
| STD.INT.60.MIX.001 | dec60_01 | 148.7s | 0–12s (catálogo) | 18–30s (catálogo) | 93–108s | 73% | 1.000 | OK |
| STD.INT.60.MIX.001 | dec60_02 | 223.4s | 0–12s (catálogo) | 18–30s (catálogo) | 53–68s | 30% | 0.473 | OK |
| STD.INT.60.MIX.001 | dec60_03 | 255.4s | 0–12s (catálogo) | 18–30s (catálogo) | 86–101s | 40% | 0.380 | OK |
| STD.INT.60.MIX.001 | dec60_04 | 359.9s | 0–12s (catálogo) | 18–30s (catálogo) | 210–225s | 63% | 0.602 | OK |
| STD.INT.60.MIX.001 | dec60_05 | 164.5s | 0–12s (catálogo) | 18–30s (catálogo) | 86–101s | 61% | 0.605 | OK |
| STD.INT.60.MIX.001 | dec60_06 | 172.4s | 0–12s (catálogo) | 18–30s (catálogo) | 110–125s | 73% | 0.625 | OK |
| STD.INT.60.MIX.001 | dec60_07 | 153.8s | 0–12s (catálogo) | 18–30s (catálogo) | 47–62s | 40% | **0.032** | INTENSIDADE BAIXA <0,15 |

## Resumo

- **OK (B2 gerável, sem bandeira)**: 20 faixas
- **A rever (intensidade <0,15)**: 2 — `dec50_05` (That'll Be the Day, intensidade 0.000), `dec60_07` (White Rabbit, 0.032)
- **Sem Trecho A (revisão manual, sem B2 possível)**: 6 — `80_02` a `80_07` (exceto `80_01`), todas com `trecho_a.inicio/fim` a `null` no catálogo e correlação ambígua (margem do pico rival <25%)
- **Nenhuma faixa ultrapassou 75% de zona de saída** nesta amostra (máximo: `dec60_01`/`dec60_06`, 73%)

**Nota**: em `STD.INT.00/50/60.MIX.001`, o "B actual" de quase todas as faixas é `18–30s` (catálogo) —
valor genérico/placeholder, não um Trecho B curado faixa a faixa; por isso o B2 diverge ~50-90s em
quase todas (esperado, não é uma falha da regra). Em `80_01` e `dec00_01`, onde o B actual já tem
tempos reais, o B2 coincide ou quase (sobreposição 100% e 87%).
