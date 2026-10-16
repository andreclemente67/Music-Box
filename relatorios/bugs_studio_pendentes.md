# Bugs do Studio — diagnóstico (sem correcção, sem dados alterados)

## 1. Propostas a cinzento, "0:00" / "ficheiro em falta", estado "pendente"
**Casos conhecidos**: Metal — "Breaking the Law" (`metal_03`), "Paranoid" (`metal_02`). Já diagnosticado e corrigido uma vez (11 Out 2026, ver STATUS.md) — registo aqui confirma a causa para não se repetir a investigação.

**Causa provável (confirmada em 11 Out para estes 2 casos)**: a faixa já tinha sido aprovada e aplicada via `aprovar_lote.py` (ou a regeneração em bloco mais antiga) — ficheiro de produção já substituído, backup em `_backup_pre_regeneracao/`. Mas esse passo de aplicação **não actualiza** `_revisao_regeneracao.json` de `"pendente"` para `"regenerado"`. O ecrã Revisão continua a tentar tocar a pré-audição em `_preview_revisao/<id>_proposta.mp3` — ficheiro já apagado/consumido no momento da aplicação — dá 404, e o ecrã mostra isso como "0:00"/"ficheiro em falta", apesar de a faixa já estar correcta em produção.

**Onde corrigir**: o passo de escrita do estado no manifesto devia acontecer no mesmo código que troca o `.mp3` — ou em `aprovar_lote.py`, ou no script de "regeneração em bloco de playlists" (o mais antigo, usado antes de `aprovar_lote.py` existir), ambos devem escrever `estado: "regenerado"` em `_revisao_regeneracao.json` atomicamente com a troca do ficheiro. A correcção de 11 Out foi só uma reparação pontual de dados (46 faixas, estado do manifesto) — **não** alterou nenhum dos dois scripts; por isso o mesmo bug pode voltar a aparecer sempre que uma aplicação passe por um caminho que não escreva no manifesto.

## 2. "Walk" (Pantera) — `metal_06`
**Não é bug** — é a salvaguarda a funcionar como esperado. A faixa está entre os 34 "por ouvir" porque o motor de escolha de fonte só encontrou um upload de fã no YouTube (canal "Jaspedood666", vídeo "Pantera - Walk") — não há canal Topic nem "Official Audio" disponível para esta música. Uma das 6 salvaguardas da aprovação em lote (11 Out 2026) exige exactamente essa confirmação de canal, por isso fica de fora da aprovação automática.

**Onde resolver**: não é código — é decisão humana. Ouvir a fonte fallback e decidir se a qualidade/fidelidade serve (upload de fã, pode ter pitch/velocidade alterados, qualidade de compressão inferior, ou cortes) ou procurar manualmente outra fonte (ex. álbum em streaming, se existir versão com canal oficial mais recente).

## Nota
Não foram encontrados mais casos deste tipo documentados no STATUS.md fora dos dois listados — se houver outras faixas a cinzento no ecrã actual do Studio além destas, precisam de diagnóstico à parte (este relatório não correu o Studio, só leu o histórico já registado).

---

## Actualização (16 Out 2026) — corrigido o código, sem tocar em dados

**Fix aplicado** (testado em dry-run, pasta temporária, nunca no manifesto/produção reais):
- `_aplicar_regeneracao_playlist.py`: gravava `_revisao_regeneracao.json` só **uma vez, no fim** do laço de uma playlist inteira — se o processo fosse interrompido a meio (crash, Ctrl-C), as faixas já trocadas em disco ficavam com o manifesto preso em estado antigo. Passa a gravar **depois de cada faixa** regenerada.
- `scripts/aprovar_lote.py`: `aplicar_aprovacao()` trocava o Trecho A e só depois o Trecho B — se a proposta do Trecho B estivesse em falta, o Trecho A já tinha sido trocado mas a excepção impedia o `estado` de passar a `"regenerado"` (troca parcial, mesma assinatura do bug). Passa a confirmar que **ambas** as propostas existem em disco antes de mover qualquer ficheiro.
- Teste (`teste_fix_manifesto.py`, pasta temporária): confirma que o manifesto grava a cada faixa (não só no fim) e que uma proposta em falta já não troca nada parcialmente. Os dois testes passaram; nada no repositório real foi tocado.

**Scan actual (só leitura) — faixas com estado desactualizado face à produção, hoje**:

Critério: `estado` não é `"regenerado"`/`"rejeitado"`, mas o ficheiro de produção já difere do backup (já foi trocado) ou a proposta já foi consumida.

- `STD.INT.00.MIX.001` (Anos 2000): `dec00_03`, `dec00_05` — estado `"aprovado"`, mas Trecho A e B de produção já diferem do backup (já trocados).
- `STD.INT.ALL.HIP.001` (Hip Hop): `hip_01` — mesmo padrão.
- `STD.INT.ALL.LAT.001` (Latina): `lat_04`, `lat_05` — mesmo padrão.
- `LOGO-001`: `logo_01` — **problema diferente**, não é o mesmo bug: `ficheiro_a` no manifesto (`LOGO_01.mp3`) não existe em lado nenhum do repositório (só há `LOGO_01.png`); `ficheiro_b` é `None`. Parece um caso à parte (ficheiro nunca chegou a existir, ou nome errado no manifesto) — fica por investigar separadamente, não é a mesma causa.

**Metal (`metal_02`/`metal_03`) já NÃO está afectada** — confirmado no manifesto actual: ambas já têm `estado: "regenerado"`, correctamente. O pedido original assumia que Metal ainda estaria por corrigir; não está — foi mesmo resolvida na correcção pontual de 11 Out 2026.

Nada destas 5 faixas foi corrigido agora (só leitura, como pedido). Resolver — se o André quiser — passa por confirmar manualmente cada caso e só então marcar `"regenerado"` (ou investigar `logo_01` à parte).
