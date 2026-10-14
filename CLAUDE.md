# Regras de trabalho (poupança de contexto)

- Respostas curtas: resumo em ≤5 linhas, sem repetir o pedido.
- Playwright só quando pedido explicitamente, ou quando a mudança mexe em fluxo de jogo; nunca screenshots sem pedido.
- Nunca ler ficheiros inteiros grandes (`musicbox.html`, `catalogo.json`, `playlists.json`, `BIBLIA.md`): usar `grep -n` e ler só os intervalos de linhas necessários; limitar output (`head`); nunca imprimir base64.
- Nada de verificações duplicadas: testar uma vez.
- Uma tarefa de cada vez; parar nos pontos de escolha.
- Não editar `catalogo.json`/`playlists.json` sem aprovação.
- Cada decisão de formato actualiza `DECISIONS.md` e `BIBLIA.md` no mesmo commit.
- Commits pequenos.
- `mp3_index.json` e `feedback.json` são escritos pelo Studio; alterações não commitadas são trabalho do André no Studio, não de outra sessão.
- No início de cada sessão, lê a secção de pendentes do STATUS.md.
- No fim de cada tarefa, actualiza STATUS/DECISIONS/BÍBLIA quando houver decisões de formato.

# Gasto de utilização (regra do André, 14 Out 2026) — AVISAR SEMPRE

- Uma tarefa por sessão. No fim da tarefa, lembra o André: "Tarefa feita — faz /clear ou abre New session antes da próxima."
- Modelo por defeito: Sonnet. Se a sessão estiver noutro modelo, avisa no início.
- AVISA SEMPRE, em destaque, quando a sessão ficar comprida (muitas trocas, contexto grande ou várias tarefas seguidas): "⚠ Sessão longa — gasta muito. Faz /compact agora ou /clear e começa sessão nova."
- Nunca propor retomar sessões antigas; preferir sessão nova + STATUS.md.
