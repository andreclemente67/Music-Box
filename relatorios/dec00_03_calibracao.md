# dec00_03 (Mr. Brightside) — diagnóstico de calibração do offset de vídeo

**Nada gravado no catálogo nesta tarefa.** Resultado: a calibração **já existe e já está em produção**.

## Confirmação da fonte

`tmp_dl/dec00_03_full.mp3` e `estudos/trecho_b_expoente/cache/dec00_03.mp3` são **o mesmo ficheiro** (md5 `a4c067b0...`, 6.751.341 bytes, 222,2s) — o download de produção (`fonte_audio` do catálogo, `watch?v=l7MaKmKJqoc`) é a mesma fonte já usada no estudo de calibração. Não há divergência de fonte a resolver.

## Método (igual ao da dec00_01, `estudos/trecho_b_expoente/video_offset.py`)

1. Fingerprint (chromaprint/`fpcalc`) do áudio do vídeo vs. da fonte completa, janela deslizante de 20s, para localizar grosseiramente o alinhamento (evita ficar presa a uma intro sem música).
2. Refinamento por correlação cruzada de forma de onda (precisão de amostra, 1/22050s) numa janela de 15s à volta do ponto encontrado.
3. Verificação: aplica o offset aos 4 candidatos de Trecho B do estudo (B1–B4) e confirma por correlação que cada um sincroniza dentro de uma tolerância de 0,1s.

## Resultado já calculado (`estudos/trecho_b_expoente/dados/video_offsets.json`)

- **`video_offset_s = 3,597`** (confiança 0,981 — mais alta que a da dec00_01, 0,931)
- Janela do vídeo usada: 105s → corresponde a 101,403s na fonte
- Verificação de sincronização nos 4 candidatos B1–B4: desvios de 0,003s a 0,02s, **todos "sincronizado: true"**

Este valor **já está gravado em produção**: `catalogo.json` (`dec00_03`) já tem `video_offset_s: 3.597`, `video_local`, `clip_b` e `video_sincronizado: true`. Ou seja, a faixa já passou por este processo numa sessão anterior (11 Out 2026) — esta tarefa confirma que o valor está correcto e consistente com a fonte de produção actual, não propõe nada novo.

## Verificação por frame/SSIM

O check SSIM (comparação visual de frame) descrito nas decisões de 14 Out 2026 foi feito especificamente para a `dec00_01` (confirmação pontual de 0,997 num bug de offset do Encore), não existe um script reutilizável de SSIM no repositório (procurado, não encontrado) nem foi repetido para a `dec00_03`. A confirmação disponível para `dec00_03` é a de correlação de áudio sample-accurate acima (B1–B4, desvio ≤0,02s) — mesmo nível de confiança numérica que o caso dec00_01, só não tem o mesmo check visual adicional.

## Resposta directa

**Dá para calibrar sem regenerar os trechos** — e já está feito: `video_offset_s = 3,597`, gravado, com `trecho_a`/`trecho_b` de produção (`0–12s`/`18–30s`) inalterados. Nada para aprovar nesta tarefa.
