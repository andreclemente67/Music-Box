# Pergunta Bónus — novo desenho (correcções do André, 20 Out 2026)

**Nota**: este ficheiro não existia no repositório (nem em `git log`, nem em disco) —
esta é a primeira versão, já com as correcções de 20 Out incorporadas. Só desenho —
`musicbox.html` e `catalogo.json` continuam inalterados; nada disto está implementado.

Este desenho substitui, para as faixas que tiverem o campo `bonus` (ver §1), o
mecanismo actual de Pergunta Bónus verbal do apresentador (BIBLIA.md §3.6/§5.3/§5.7)
por um clip pré-gravado próprio. **Em aberto**: se isto coexiste com o mecanismo
actual (`temBonus`, Faixas 3/6 dos Universos temáticos, Faixa 4 de Décadas/Estilos)
ou o substitui por completo — ver secção 4.

## 1. Dados e ficheiros

O vídeo/áudio do Bónus é um **ficheiro próprio**, independente dos ficheiros das
faixas normais:

- **Sem relação com os vídeos do Encore** — sem `video_offset_s`, sem sincronização
  com Trecho A/B, sem ligação a `clip_b`/`video_local`. É um clip autónomo de **12s**.
- Campo novo na faixa: `bonus`, objecto com:
  - `tipo`: `"audio"` ou `"video"`
  - `ficheiro`: caminho do clip de 12s
  - `titulo`: título do Bónus (editorial)
  - `pergunta`: texto da pergunta (para o apresentador ler/confirmar)
  - `resposta`: texto da resposta certa (referência da régie para validar)
  - `pontos`: valor creditado no mealheiro, **por faixa** (não um valor fixo global
    — permite variar o valor conforme a dificuldade/duração da pergunta)
- Ficheiros em `assets/bonus/` — audio e vídeo separados dos assets das faixas
  normais (`assets/audio_ext/`, `assets/clips_b/`, etc.), mesma lógica de pastas
  dedicadas já usada para esses.

## 2. Quem responde — ordem e punição

1. **Primeiro a responder**: quem acertou a Faixa (mesmo privilégio que o mecanismo
   actual, BIBLIA.md §5.3/§9.2 "a Pergunta Bónus é privilégio de quem reconheceu o
   áudio").
2. **Se errar, não é punido** — sem perda de pontos nem de mealheiro, só perde a
   oportunidade (confirma a sugestão do André).
3. **Roubo**: se quem acertou a Faixa errar o Bónus, qualquer outro concorrente
   **não-mutado** pode responder a seguir. Concorrentes em MUTE continuam excluídos
   da fase Bónus, tal como hoje (§9.2, "concorrentes em MUTE mantêm-se silenciados
   também durante essa fase").
4. **Ordem dos que roubam**: **sem ordem fixa pré-definida** — a régie escolhe
   livremente a quem dá a palavra entre os elegíveis, exactamente como já faz hoje
   para validar Trecho A/B (não há fila automática no código; é sempre decisão
   humana da régie, que depois marca Correcto/Erro).
5. **Erros de quem rouba**: **não são punidos** — mesma regra do ponto 2, estendida
   a cada tentativa de roubo (ninguém perde pontos/mealheiro por errar o Bónus,
   seja o vencedor da Faixa, seja quem rouba a seguir).
6. **Pontos do Bónus**: creditados no mealheiro de quem acertar (vencedor da Faixa
   ou quem rouba), nunca no ranking — mantém a Independência de Fluxos já fechada
   em BIBLIA.md §5.3/§5.7/§11.3 (o Bónus só move o mealheiro, nunca o ranking dos
   +100 pontos da Faixa, nem gera MUTE). Valor = `bonus.pontos` dessa faixa.
7. **Se ninguém acertar** (vencedor da Faixa + todos os que roubam erram, ou
   nenhum concorrente elegível quer responder): ninguém recebe mealheiro desta
   Bónus, segue-se para o NEW_SLOT normalmente — sem penalização adicional a
   ninguém, consistente com a Independência de Fluxos.

## 3. Máquina de estados do botão

1. **Disponível (a piscar)**: assim que a Faixa activa tem `bonus` definido, o
   botão aparece a piscar — sinaliza à régie "esta Faixa tem Bónus, ainda não
   armado". A régie pode armar em qualquer momento da Faixa (Trecho A, Trecho B,
   ou durante o Encore), antes de este terminar.
2. **Régie clica o botão** → pára de piscar, fica fixo ("armado"). Este clique
   **não** faz tocar o clip — só compromete/arma o disparo automático a seguir.
   Se a régie nunca clicar antes do fim do Encore dessa Faixa, o Bónus **não
   toca** nessa Faixa (fica saltado) — dá à régie controlo editorial sobre em
   que Faixas usar o Bónus, mesmo que a Faixa o tenha definido no catálogo.
3. **Disparo automático**: no fim do Encore dessa Faixa (mesmo instante em que
   hoje se despacha o NEW_SLOT, ver BIBLIA.md §5.4b/§5.5), se o botão estiver
   armado, o clip de 12s (áudio ou vídeo, mesmo tratamento visual do Encore se
   for vídeo — ecrã inteiro) toca sozinho, sem novo clique da régie.
4. **Depois do clip**: pergunta `bonus.pergunta` fica disponível para o
   apresentador formular (texto de referência, like `descritivo_apresentador`);
   a régie recolhe a resposta e valida Correcto/Erro por concorrente (ver secção 2).
5. **Reposição**: o botão volta ao estado "a piscar" só na Faixa seguinte que
   também tenha `bonus` definido; Faixas sem `bonus` não mostram o botão (escondido,
   mesmo padrão de `display:none` dos outros botões condicionais do rodapé).

**A confirmar com o André antes de implementar**: (a) o clip de 12s é tocado
*em vez* da pergunta verbal, ou *antes* dela (teaser temático + depois o
apresentador pergunta em voz alta)? (b) este novo mecanismo aplica-se a todas as
faixas com `bonus` no catálogo, substituindo por completo `temBonus`/Faixas 3-6/
Faixa 4 (família Especiais vs. Décadas/Estilos, BIBLIA.md §3.6), ou os dois
mecanismos coexistem por universo? (c) o que mostra o ecrã da régie enquanto o
botão está "a piscar" mas ainda não foi armado — algum aviso visual extra além do
próprio piscar?

## 4. Impacto nos documentos existentes (ainda não feito)

Esta secção fica como lista de trabalho para quando o desenho for aprovado e
passar a implementação — **nada disto foi tocado ainda**:

- BIBLIA.md §3.6/§5.3/§5.7/§9.2/§11.3 — precisam de reconciliar o mecanismo verbal
  actual com este novo clip pré-gravado (ver pergunta (b) acima).
- `catalogo.json` — schema novo `bonus` por faixa (tipo/ficheiro/titulo/pergunta/
  resposta/pontos).
- `musicbox.html` — botão novo (piscar/armado), listener do fim do Encore a
  despachar o clip, lógica de roubo (não-mutados, sem punição de erro).
- `assets/bonus/` — pasta nova, ficheiros a produzir/recolher por faixa.
