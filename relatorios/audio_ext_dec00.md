# Áudio estendido Anos 2000 (dec00_02–dec00_07) — 0 aprovadas, 6 saltadas

Pedido do André (16 Out 2026): gerar `assets/audio_ext/<id>_{a,b}_ext.mp3` (Trecho + 10s Dmin, mesmo método da `dec00_01`: corte directo `ffmpeg -c copy` de `tmp_dl/<id>_full.mp3`, sem reencoder — herda bitrate/loudness automaticamente) para as 6 faixas restantes do pack Anos 2000.

Script: `scripts/gerar_audio_ext_dec00.py`. **Nada foi gravado em `catalogo.json`** (confirmado, diff vazio) nem criado em `assets/audio_ext/` para estas 6 — sem backup nem tag `antes-ext-00` (só se criam quando há pelo menos 1 faixa aprovada).

## Verificação prévia por correlação

Antes de cortar, cada Trecho A e B é confirmado por correlação de forma de onda entre o ficheiro curto já existente (`<id>_a.mp3`/`_b.mp3`) e `tmp_dl/<id>_full.mp3` no tempo `inicio` do catálogo (±1,5s de tolerância ao seek). Limiar: correlação normalizada ≥ 0,60.

**Controlo de validação do método**: `dec00_01` (fonte já confirmada noutras sessões) dá **0,99–1,00** nos dois trechos — confirma que o método funciona e que 0,60 é um limiar razoável para "mesma fonte".

**Resultado nas 6 faixas — todas saltadas**:

| Faixa | Trecho A | Trecho B | Nota |
|---|---|---|---|
| dec00_02 | 0,25 | 0,46 | nenhum dos dois bate |
| dec00_03 | 0,55 | 0,06 | A perto do limiar mas não o suficiente; B claramente não bate |
| dec00_04 | 0,48 | 0,08 | nenhum dos dois bate |
| dec00_05 | 0,48 | 0,25 | nenhum dos dois bate |
| dec00_06 | 0,18 | **0,98** | **B bate muito bem — só A falha** |
| dec00_07 | 0,16 | 0,25 | nenhum dos dois bate |

## Leitura

`tmp_dl/<id>_full.mp3` destas 6 faixas não corresponde com confiança ao que foi usado para cortar os `_a.mp3`/`_b.mp3` já em produção — provavelmente downloads mais recentes (de outra sessão/tarefa) de uma fonte diferente da que gerou os ficheiros curtos originais, não a mesma gravação. **Caso a destacar**: `dec00_06` tem o Trecho B a bater quase perfeitamente (0,98) mas o Trecho A falha (0,18) — sugere que o `full` pode mesmo ser a música certa, só com uma introdução diferente (mais longa/curta) da que o `inicio=0` do catálogo assume; vale uma confirmação manual à parte antes de descartar por completo.

**Nada a fazer agora** — a regra pedida ("se não for, salta e regista porquê") foi seguida à letra. Para avançar, o próximo passo seria confirmar manualmente (ouvir) `tmp_dl/dec00_0{2,3,4,5,6,7}_full.mp3` contra os ficheiros curtos antes de descarregar fontes novas, ou aceitar re-download dedicado por faixa.
