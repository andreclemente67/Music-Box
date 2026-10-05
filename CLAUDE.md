# Regras de trabalho (poupança de contexto)

- Respostas curtas: resumo em ≤5 linhas, sem repetir o pedido.
- Playwright só quando pedido explicitamente, ou quando a mudança mexe em fluxo de jogo; nunca screenshots sem pedido.
- Nunca ler ficheiros inteiros grandes (`musicbox.html`, `catalogo.json`, `playlists.json`, `BIBLIA.md`): usar `grep -n` e ler só os intervalos de linhas necessários; limitar output (`head`); nunca imprimir base64.
- Nada de verificações duplicadas: testar uma vez.
- Uma tarefa de cada vez; parar nos pontos de escolha.
- Não editar `catalogo.json`/`playlists.json` sem aprovação.
- Cada decisão de formato actualiza `DECISIONS.md` e `BIBLIA.md` no mesmo commit.
- Commits pequenos.
