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
