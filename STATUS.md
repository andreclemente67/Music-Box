# Music Box — Status

## Última actualização
2026-10-14 (vista "Início" do Studio)

## À espera de decisão do André

- **Encore redesenhado — implementado, piloto na dec00_01 (14 Out 2026)**: ver DECISIONS.md (entrada "implementado") e BIBLIA.md §5.4b para o detalhe completo, incluindo os 3 ajustes feitos ao implementar (âmbito restrito a `ficheiro_ext`; lê `video_local` em vez de `clip_b`; corte sem acerto continua aos 12s). `dec00_03` e as restantes 346 faixas mantêm o Encore antigo inalterado.
  - **Não testado automaticamente** — Playwright indisponível nesta máquina (`Error: Playwright does not support chromium/webkit/firefox on mac12` — macOS demasiado antigo para os browsers que o Playwright instala hoje; confirmado a tentar os 3 motores). Ficheiros novos confirmados acessíveis pelo servidor (`curl` 200: `catalogo.json`, `assets/audio_ext/dec00_01_{a,b}_ext.mp3`, `video_local`, `musicbox.html`) e sintaxe JS validada (`node --check`), mas o fluxo de jogo real (acerto no Trecho A, acerto no Trecho B, desvio áudio/vídeo) fica por testar manualmente — ver pendente abaixo.
  - **Bugs corrigidos (14 Out 2026, diagnóstico do André)**: (1) offset do vídeo faltava somar `inicio` do trecho do acerto (`video_offset_s` é calibrado contra a fonte áudio completa, não contra o início de um trecho) — vídeo arrancava ~142s adiantado num acerto no Trecho B da `dec00_01`; (2) passou a esperar `seeked`/`canplay` antes de `video.play()` (evita arrancar num frame antigo durante o seek); (3) sincronização generalizada ao Trecho A também (antes só o Trecho B ficava sincronizado); (4) removida a película preta de fundo por trás da caixa de 75% (`#encore-video-overlay.encore-ext` transparente). Ver DECISIONS.md (duas entradas de 14 Out), BIBLIA.md §5.4b. Só sintaxe validada (`node --check`), não testado no browser.
  - **Decidido e implementado (14 Out 2026)**: vídeo passa a tocar com o seu próprio som (relógio mestre do que se ouve) — mp3 do jogo com fade-out ~150ms no acerto, som do vídeo entra com fade-in ~150ms, ducking/rampa da voz aplica-se ao vídeo; removida a correcção contínua de `playbackRate` (só fazia sentido com o vídeo mudo). Ver DECISIONS.md, entrada "Resolvida a pendência do chipmunk...".
  - **Pendente**: André testar no browser, `http://localhost:8002/musicbox.html?playlist=STD.INT.00.MIX.001`, 3 casos na dec00_01 (posição 1): (1) acertar no Trecho A — vídeo deve arrancar com som próprio, posicionado correctamente, sem correcção de velocidade; (2) acertar no Trecho B — idem; confirmar que o mp3 do jogo sai e o som do vídeo entra sem "estalo"/corte seco, e que a voz (ROAR/"In the Box!!"/nome) se ouve bem por cima do som do vídeo (ducking), com rampa de volta ao normal no fim; (3) comparar com uma faixa sem `ficheiro_ext` (ex. `dec00_02`) — Encore antigo, deve continuar exactamente igual a antes (vídeo/foto a 100%, com película preta, `clip_b` com o seu som normal). Confirmar também o contador (segundos restantes), a caixa de 75% sem fundo preto, e que o corte "sem ninguém acertar" continua aos 12s.

- **B2 aplicado no catálogo — Anos 2000, pack a pack (14 Out 2026, tag `antes-b2-00`)**: aprovação do André, só `STD.INT.00.MIX.001`, só `trecho_b.inicio/fim` (ficheiro `.mp3` de produção não tocado — regeneração do áudio é tarefa à parte). **5 aplicadas** (todas "OK" no diagnóstico, `relatorios/diagnostico_b2_4packs_demo.md`): `dec00_02` 18–30→100–115, `dec00_04` 18–30→106–121, `dec00_05` 18–30→77–92, `dec00_06` 18–30→69–84, `dec00_07` 18–30→71–86. **2 não tocadas**: `dec00_01` e `dec00_03` — têm `clip_b`/`video_sincronizado` (Encore com vídeo sincronizado ao Trecho B actual), saltadas por regra explícita do pedido, não por bandeira do diagnóstico (ambas estavam "OK"). Nenhuma faixa do pack tinha bandeira de intensidade `<0,15` ou zona de saída. Diff cirúrgico de 10 linhas; `playlists.json`/`mp3_index.json`/`feedback.json` intocados.

- **+5 `fonte_audio` gravadas, aprovação do André (14 Out 2026, tag `antes-fontes-5b`)**: `80_03`, `dec00_02`, `dec00_04`, `dec00_07`, `dec60_04` — 4 URLs vindos de `_revisao_regeneracao.json` (já confirmados nessa revisão) e `dec00_02` de `scripts/propostas_fonte_4packs.json` (fonte "fallback", canal oficial Beyoncé). Diff cirúrgico de 5 linhas em `catalogo.json`, nada reformatado; `playlists.json`/`mp3_index.json`/`feedback.json` intocados. Cobertura geral sobe de 92 para **97/348 faixas (28%)**.
  - **`80_01` (Take On Me) resolvida (14 Out 2026)**: aprovada pelo André a alternativa Topic "Take on Me" (229s), `fonte_audio` gravada — `https://www.youtube.com/watch?v=MIgK3zOk0zg`. Cobertura sobe de 97 para **98/348 faixas (28%)**.

- **Implementada a vista "Início — O que falta fazer" no Studio (14 Out 2026)**: esboço aprovado pelo André (`Início — O que falta fazer-html.zip`, Downloads — guardado em `_obsoleto/esboco_inicio/`), implementado em `musicbox_studio.html` como **primeiro separador do menu**, sem tocar nos outros 8 nem na barra lateral (só acrescentada 1 linha de filtro, ver abaixo). Só leitura/navegação — nenhum botão escreve em `catalogo.json`/`playlists.json`.

  - **3 cartões**: "Aplicar" (faixas com `estado:"aprovado"` no manifesto da Revisão, por pack) → botão leva à vista Revisão (fluxo de aplicar já existente, por playlist — **não** foi criado "aplicar todas"); "Ouvir" (união de pendentes do manifesto + da aprovação em lote, `relatorios/aprovacao_lote_progresso.csv`) → idem, Revisão; "Completar" (faixas sem `fonte_audio` no catálogo) → **filtro novo** "Sem fonte de áudio" na barra lateral da Biblioteca (`filterByAsset('sem-fonte')`, mesma função já existente, só mais um `case`).
  - **"Outras pendências"**: sem imagem, inconclusivos do verificador (`relatorios/reavaliacao_falhas.csv` — só aparece se o fetch responder 200, senão a linha é omitida), não usadas em nenhuma playlist (reutiliza `playlistsUsing()`, já existente). A linha "Trecho B para revisão manual" foi **omitida de propósito** — só há amostra de 7 faixas analisadas, não o catálogo, mostrar um número aí seria enganador.
  - Números calculados no browser a partir dos mesmos dados/lógica de `scripts/diagnostico_studio_pendentes.py` (reutiliza `CATALOGO`/`PLAYLISTS`/`carregarRevisao()`/`playlistsUsing()`, já carregados no arranque do Studio) — não há endpoint novo no `_servidor_escrita.py`, os CSVs são lidos pela mesma rota GET genérica que já serve `_revisao_regeneracao.json`/`concorrentes.json`.
  - Testado: JS sem erros de sintaxe (`node --check`), estrutura HTML consistente (9 separadores ↔ 9 `view-*`, só "Início" com `active`), e os 4 ficheiros que a vista lê (`musicbox_studio.html`, `_revisao_regeneracao.json`, `relatorios/aprovacao_lote_progresso.csv`, `relatorios/reavaliacao_falhas.csv`) confirmados a responder 200 no servidor real. **Sem Playwright** — por pedido do André, a verificação visual/consola fica para ele no browser.

- **DECIDIDO — regra "refrão mais intenso" adoptada só onde não há Trecho B validado (11 Out 2026)**: teste cego feito pelo André na página do estudo, **2 audições nas 5 faixas dos Anos 80: regra nova 4, B actual 4, iguais 2** — empate técnico. **Decisão**: a regra passa a ser o método para gerar o Trecho B automaticamente **apenas nas faixas sem B definido ou sem B validado**; onde o B actual já foi ouvido e aprovado, mantém-se. Ver DECISIONS.md (critério completo e as duas ressalvas) e BIBLIA.md §13.2.

  - **A regra tende a escolher ocorrências tardias**: nas 7 faixas analisadas (5 dos Anos 80 + `dec00_01` + `dec00_06`), o B2 caiu sempre depois do B actual, mas em dois grupos distintos — **cinco claramente mais tarde** (`80_02` +20s, `80_05` +6s, `80_04` +96s, `80_06` +99s, `80_07` +129s) e **dois que coincidem na prática com o B existente** (`dec00_01` +2s, `dec00_06` +1s). Coerente com o critério (os últimos refrões são os mais cheios), mas a vigiar: um refrão final pode estar em fade ou ser menos canónico para reconhecimento. **Corrigido em 14 Out**: esta linha dizia +88s no `dec00_06`, valor que vinha de comparar o B2 com tempos desactualizados do catálogo (18–30s, 12s, quando o mp3 tem 15s) e de um B2 da versão anterior da regra; o valor real é +1s. **Os cinco dos Anos 80 dependem todos de correlação**, sem tempos no catálogo que os confirmem.
  - **Confluência baixa → revisão manual, não geração**: em `80_04` a janela vencedora tinha confluência 0.074 (contra 0.33–0.39 nas outras e 0.93 no Hey Ya!) — nenhuma janela dessa faixa é intensa nos dois eixos. Abaixo de um limiar **ainda a definir** (com diagnóstico, não escolhido no ar), a faixa fica marcada para revisão manual.
  - **Limiares de revisão manual fechados (14 Out 2026)**: o B2 **não** é gerado e a faixa vai para revisão manual se **acabar depois de 80% da duração** da música (zona de saída), se a **confluência for inferior a 0,15**, ou se a **localização do A/B por correlação for ambígua**. Nos dois packs diagnosticados só o `80_04` é apanhado pelos dois primeiros (acaba a 84%, confluência 0,074); o `80_07` fica à beira, a acabar a 77% — foi por isso que o limiar ficou no fim do trecho e não no início. **Registado, não implementado**: nenhuma geração está autorizada. Ver DECISIONS.md e BIBLIA.md §13.2.
  - **Três dos cinco desvios dos Anos 80 ficam sem base confirmada**: o teste de margem (14 Out) classifica como ambíguas as localizações do B actual de `80_04`, `80_06` e `80_07` — e o `80_06` já trazia aviso de pico fraco (2,6x) na corrida de 11 Out, que não foi trazido para a tabela na altura. Os desvios +96s, +99s e +129s dependem dessas localizações. Mantêm-se confirmados `80_02` +20s, `80_05` +6s, `dec00_01` +2s (do catálogo) e `dec00_06` +1s.
  - **+5 `fonte_audio` gravadas, aprovação do André (14 Out 2026)**: `dec00_03`, `dec00_05`, `dec50_02`, `dec50_03`, `dec60_02` — as 5 propostas limpas (Topic ou "Official Audio", ≤320s) de 11 sem fonte nos packs `STD.INT.80/00/50/60.MIX.001`, obtidas com o motor de 9 Out (`_servidor_escrita.py:_escolher_fonte_youtube`, sem cookies de conta pessoal, ritmo lento) e gravadas por edição cirúrgica do `catalogo.json` (diff de 5 linhas, nada reformatado). Tag de reversão: `antes-fontes-5`. Cobertura geral sobe de 87 para 92 faixas (~26%).

    **Ficam 6 faixas a ouvir no Studio, propositadamente fora desta gravação** (propostas em `scripts/propostas_fonte_4packs.json`, nenhuma escrita no catálogo):
    - `80_01` (Take On Me) — a proposta é "Take On Me (MTV Unplugged / Edit)", canal Topic mas versão acústica, não o original de 1985; **precisa de outra fonte**, não só confirmar esta.
    - `80_03` (The Power of Love) — 330s > 320s; confirmar se o excesso é intro/outro sem música ou se é mesmo o tema completo.
    - `dec00_02` (Crazy in Love), `dec00_04` (Seven Nation Army), `dec00_07` (Umbrella) — fonte "fallback" (canais de repostagem: Beyoncé/repost genérico, "EDM Music", "Taj Tracks"), nem Topic nem "Official Audio".
    - `dec60_04` (Like a Rolling Stone) — 368s > 320s, por confirmar.

  - **FECHADO POR AGORA, 14 Out 2026 — aplicação em massa adiada**: o método está decidido e os limiares fechados, mas **só 87 das 348 faixas do catálogo têm `fonte_audio`** (25%), e sem source a regra não corre. Das 87, só 51 têm o Trecho A no catálogo — as outras 36 precisariam de localização por correlação, que é precisamente onde está o risco de repetição errada. A cobertura também está espalhada: o melhor pack tem 5/7 (Anos 80, Anos 60, Anos 50) e seis packs têm 0, incluindo os dois de 8 faixas (`RET.INT.ALL.VOZ.001`, `LOGO-001`). Aplicar a regra agora tratava um quarto do catálogo e deixava o resto como está, por isso **o pré-requisito é a cobertura de `fonte_audio`, não a regra**. `catalogo.json` e `playlists.json` continuam intocados e nenhuma geração está autorizada. Contagem reproduzível: `python3 scripts/contar_fonte_audio.py`.
  - Página do estudo (continua disponível para mais audições, agora com ordem nova e equilibrada a cada audição e total acumulado automático): `http://localhost:8002/estudos/trecho_b_regra_energia/pagina.html`. A ordem estava a ser sorteada uma vez por faixa e congelada — a 2ª audição repetia o mesmo arranjo (a regra saiu em 1º lugar em 9 de 10), corrigido; o empate 4-4-2 mantém-se porque é o que foi ouvido.
  - Fica também em aberto, só a pedido: **gravar no catálogo os tempos de Trecho A/B recuperados por correlação** — 12 das 14 faixas dos dois packs vistos têm `inicio`/`fim` a `null` apesar de os mp3 existirem.

- **Resolvido — ecrã Revisão com 47 faixas "pendente" já aplicadas (11 Out 2026)**: diagnóstico pedido pelo André (Metal: "Breaking the Law"/metal_03 e "Paranoid"/metal_02 a mostrar 0:00/0:00, "ficheiro em falta", mas o cabeçalho já contava "3 regeneradas"). Confirmado: **as duas já tinham sido aprovadas e aplicadas** na aprovação em lote (`relatorios/aprovacao_lote_progresso.csv`: `aprovado`), com backup em `_backup_pre_regeneracao/` e ficheiro de produção já diferente do backup — o manifesto (`_revisao_regeneracao.json`) é que nunca foi actualizado de `"pendente"` para `"regenerado"` para estas duas, e a pré-audição que a Revisão tentava tocar (`_preview_revisao/metal_0{2,3}_*_proposta.mp3`) já tinha sido consumida/apagada na aplicação — por isso o 404/0:00. Varrida **toda** a Revisão com o mesmo critério (produção difere do backup pré-existente = já aplicada, independentemente de ter sido via `aprovar_lote.py` ou via a regeneração em bloco de playlists mais antiga desta sessão): mais **45 faixas** no mesmo estado, em 20 playlists (Pop, Rock, Soul, Natureza, Blues, Anos 60, Anos 80, PT, Gaming, TV/Cinema, Guitarra Solo, Brasil, Bateria, Clássica, Anos 50, Sintetizadores, Mix 005, Rock 70, Pop 002) — todas corrigidas para `"regenerado"` (nenhum ficheiro de áudio tocado, só o estado do manifesto; 0 casos de "pendente a sério com ficheiro em falta"). **Contagem real de pendentes por pack, depois da correcção — 12 no total**: `LOGO-001` (1: logo_01), `RET.PT.90.VOZ.001` (2: pt_07, ptbat_04), `STD.INT.80.MIX.001` (1: 80_03), `STD.INT.ALL.CLA.001` (1: cla_02), `STD.INT.ALL.GAM.001` (1: gam_01), `STD.INT.ALL.GTR.001` (1: solo_01), `STD.INT.ALL.ROC.001` (1: rock_03), `STD.PT.70.WLD.001` (1: zeca_afonso_grandola_vila_morena), `STD.PT.80.MIX.001` (2: pt80_02, pt80_04), `TRB.UK.ALL.ROC.001` (1: beatles_04).

- **Decisão de formato do André (11 Out 2026) — Encore com vídeo em ecrã inteiro, implementado e ligado ao jogo**: ver DECISIONS.md/BIBLIA.md §5.4b para o detalhe completo. Resumo: a antiga janela de decisão "▶ Encore" verde/vermelho (§5.4b, 2026-09-17) foi **removida** de `musicbox.html` e substituída por `iniciarEncoreComVideo()` — no fim da sequência de voz (nome→"In the Box!!"→roar), se a faixa tiver `clip_b` (vídeo+áudio do Trecho B já combinados, ver abaixo) e `video_sincronizado!==false`, mostra-o em ecrã inteiro (fade de 500ms na música de fundo, `FADE_ENCORE_VIDEO_MS`); sem `clip_b`, cai na foto do artista em ecrã inteiro por 4s (`ENCORE_FOTO_FALLBACK_MS`); sem nenhum dos dois, avança de imediato (como antes de existir Encore). A régie salta com Esc ou Espaço em qualquer dos dois casos. Campos novos no catálogo (via `catalogo_patch.json`): `video_local`, `video_offset_s`, `clip_b`, `video_sincronizado`. **Geradas as 2 primeiras `clip_b`** (`assets/clips_b/dec00_01.mp4`, `assets/clips_b/dec00_03.mp4`, 15s cada, H.264/AAC) a partir do Trecho B **de produção** (inalterado) de "Hey Ya!"/"Mr. Brightside" + o vídeo de demonstração do estudo, alinhados por correlação de forma de onda directamente contra o áudio do vídeo (não contra a fonte do estudo — essa não é garantidamente a mesma fonte da faixa de produção para `dec00_03`, que não tem `fonte_audio` registada). Testado com Google Chrome real via Playwright directamente no `musicbox.html` (chamada a `mostrarMomentoResposta(0,'correcto')` com `dec00_01`/`dec00_03` montados em `musicasActuais`, sem passar pela UI completa): nas duas faixas, overlay a aparecer ~4s depois do acerto (duração real da sequência de voz, roar incluído quando existe + pausa de 1,5s), vídeo a tocar os 15s completos e a avançar sozinho no fim (`dec00_01`: visível 4028→19620ms, ~15,6s; `dec00_03`: 4029→19111ms, ~15,1s); Espaço a meio do clip esconde o overlay e avança em <350ms. Sem erros de consola.

- **Resolvido — Encore do estudo Trecho B sem som/vídeo preso (11 Out 2026)**: `_servidor_escrita.py` nunca suportava pedidos `Range` (devolvia sempre o ficheiro completo com 200, nunca 206) nem transmitia em blocos (lia o ficheiro inteiro para memória antes de escrever qualquer byte). Para os vídeos de demonstração de 70-90MB isto tinha dois efeitos: o `<video>` do Encore não conseguia fazer seek (ficava à espera de descarregar sequencialmente até ao ponto pedido — "só começava quando o áudio acabava"), e nalguns casos o Chromium abortava a ligação antes de receber o primeiro byte e marcava o vídeo como `NETWORK_NO_SOURCE` (nunca mais tentava). Corrigido: `do_GET`/novo `do_HEAD` agora respeitam `Range` (206 + `Accept-Ranges`/`Content-Range`) e transmitem em blocos de 256KB directamente do disco. `pagina.html`: `<video>` passa a `preload="metadata"` (antes `auto`, que descarregava o ficheiro inteiro logo ao abrir a página) e o `encore()` espera por "seeked" **e** por "canplay"/`readyState>=3` antes de tocar os dois em simultâneo (antes só esperava "seeked", que com `preload="metadata"` pode disparar sem dados suficientes para tocar já). Testado com Google Chrome real via Playwright (o Chromium open-source que o Playwright trazia por omissão não decodifica H.264 — dava um falso "no supported streams" que não é o que o André vê): Hey Ya! e Mr. Brightside, vídeo e áudio arrancam no mesmo clique (~230ms), desvio ao vivo medido 22-34ms (Hey Ya!) e -6 a +5ms (Mr. Brightside), sempre abaixo do limiar de correcção de 40ms, incluindo num segundo Encore seguido no mesmo candidato. Vídeos de demonstração também foram re-descarregados e reencodados de novo (um único passo, antes tinham sido reencodados duas vezes em separado) — `video_offset_s` e os desvios por candidato em `dados/publico.json`/`dados/video_offsets.json` foram remedidos para o ficheiro novo (continuam todos dentro da tolerância de 0,1s).

- **Estudo "Trecho B = expoente da música" pronto para ouvir (11 Out 2026)**: playlist `STD.INT.00.MIX.001` (7 faixas), 4 candidatos a Trecho B por faixa (B1–B4, ordem aleatória, método não revelado), nada de produção tocado — tudo em `estudos/trecho_b_expoente/`. **Página de teste**: com o Studio a correr (`iniciar_editor.command`/porta 8002), abre `http://localhost:8002/estudos/trecho_b_expoente/pagina.html` — ouve às cegas, escolhe o melhor por faixa, o resumo final aparece na própria página (grava no browser, `localStorage`). 2 faixas (`dec00_01` Hey Ya!, `dec00_03` Mr. Brightside) têm também um botão "▶ Encore" de demonstração — vídeo oficial mudo sincronizado por cima do candidato escolhido (vídeo não está no catálogo, só para este estudo; nenhuma das 7 faixas tem campo `video`, ver `README.md` do estudo). `dec00_04` (Seven Nation Army) só tem 3 candidatos — a letra não tem refrão lírico claro, o método LRCLIB não produziu resultado. **IMPORTANTE: não abrir `estudos/trecho_b_expoente/dados/chave_*.json` antes de escolheres na página** — é aí que está escrito qual método gerou qual B; só a página fica cega, os ficheiros no disco não. Metodologia completa e limitações (nota sobre o método chroma, ver) no `README.md` do estudo. Commit `cd76770`, enviado.

- **Aprovação em lote das previews pendentes — tag de segurança `antes-aprovacao-lote` (11 Out 2026)**: reavaliadas de novo (nunca confiando em estado antigo) as 76 "pendente" com pré-audição já gerada, contra 6 salvaguardas (verificador OK em A/B, canal Topic/"Official Audio" reconfirmado agora, título sem Remix/Live/Acoustic/Version/Edit/Cover/Video/MV/Movie/Trailer/Scene/Teaser, A/B sem sobreposição e ~15s, duração da fonte ≤320s, nunca posição de playlist tributo). **42 aprovadas e aplicadas** (ficheiros substituídos, originais em `_backup_pre_regeneracao/`, `fonte_audio` registada via `catalogo_patch.json` — fundido automaticamente pelo `auto_fusao.sh` já em execução). **34 ficam pendentes**, por pack:

  - `LOGO-001` (1): `logo_01` — fonte "fallback" — nem canal Topic nem "Official Audio" (canal: '7clouds Rock', título: 'Nirvana - Smells Like Teen Spirit (Lyrics)')
  - `RET.PT.90.VOZ.001` (2): `pt_07` — fonte "fallback" — nem canal Topic nem "Official Audio" (canal: 'Shogun', título: 'Da Weasel Re-Tratamento'); `ptbat_04` — fonte "fallback" — nem canal Topic nem "Official Audio" (canal: 'Elísio Donas', título: "Ornatos Violeta - 'Capitão Romance', ao vivo no North Music Festival '22")
  - `STD.INT.10.MIX.001` (1): `a10_06` — fonte "fallback" — nem canal Topic nem "Official Audio" (canal: 'Golden Network', título: 'Lil Nas X - Old Town Road (Lyrics) feat Billy Ray Cyrus')
  - `STD.INT.10.SYN.001` (1): `new_order_blue_monday` — duração da fonte muito alta (450s > 320s) — por confirmar
  - `STD.INT.10.SYN.002` (2): `hurts_miracle` — fonte "fallback" — nem canal Topic nem "Official Audio" (canal: 'Hurts', título: 'Hurts - Miracle (Audio)'); `future_islands_seasons_waiting_on_you` — fonte "fallback" — nem canal Topic nem "Official Audio" (canal: 'BBC', título: 'Future Islands perform Seasons (Waiting On You) | Later... with Jools Holland - BBC')
  - `STD.INT.20.MIX.001` (3): `dec20_06` — título da fonte rejeitado: "Beyoncé - CUFF IT (WETTER REMIX) - EXPLICIT - Official Visualizer"; `dec20_05` — fonte "fallback" — nem canal Topic nem "Official Audio" (canal: '7clouds Rock', título: 'Miley Cyrus - Flowers (Lyrics)'); `dec20_02` — fonte "fallback" — nem canal Topic nem "Official Audio" (canal: 'Rap Samurai', título: 'Olivia Rodrigo - drivers license (Lyrics)')
  - `STD.INT.70.ROC.001` (1): `bat_08` — fonte "fallback" — nem canal Topic nem "Official Audio" (canal: 'TheWho', título: "The Who - Baba O'Riley (Shepperton Studios / 1978)")
  - `STD.INT.80.MIX.001` (1): `80_03` — duração da fonte muito alta (330s > 320s) — por confirmar
  - `STD.INT.ALL.BLU.001` (2): `blues_05` — fonte "fallback" — nem canal Topic nem "Official Audio" (canal: 'Gustavo Freire', título: 'Albert King and Stevie Ray Vaughan - Born Under A Bad Sign   (HD)'); `blues_01` — duração da fonte muito alta (324s > 320s) — por confirmar
  - `STD.INT.ALL.CLA.001` (1): `cla_02` — duração da fonte muito alta (656s > 320s) — por confirmar
  - `STD.INT.ALL.GAM.001` (1): `gam_01` — fonte "fallback" — nem canal Topic nem "Official Audio" (canal: 'Geek Music', título: 'THE LEGEND OF ZELDA - Main Theme By Koji Kondo | Nintendo')
  - `STD.INT.ALL.GTR.001` (1): `solo_01` — fonte "fallback" — nem canal Topic nem "Official Audio" (canal: 'BBC News', título: 'Jimmy Page: How Stairway to Heaven was written - BBC News')
  - `STD.INT.ALL.HIP.001` (1): `hip_01` — título da fonte rejeitado: "Rapper's Delight (Long Version)"
  - `STD.INT.ALL.JAZ.001` (2): `jazz_04` — duração da fonte muito alta (563s > 320s) — por confirmar; `jazz_06` — fonte "fallback" — nem canal Topic nem "Official Audio" (canal: 'Cancano Cancano', título: 'Nina Simone  Feeling Good')
  - `STD.INT.ALL.LAT.001` (2): `lat_05` — fonte "fallback" — nem canal Topic nem "Official Audio" (canal: 'Gipsy Kings', título: 'Gipsy Kings - Bamboléo (Audio)'); `lat_04` — fonte "fallback" — nem canal Topic nem "Official Audio" (canal: 'Musica Milagrosa', título: 'Marc Anthony - Vivir Mi Vida (Letra / Lyrics)')
  - `STD.INT.ALL.MET.001` (2): `metal_06` — fonte "fallback" — nem canal Topic nem "Official Audio" (canal: 'Jaspedood666', título: 'Pantera - Walk'); `metal_07` — fonte "fallback" — nem canal Topic nem "Official Audio" (canal: 'riot wav', título: 'Slipknot - Duality | Lyrics')
  - `STD.INT.ALL.NAT.001` (1): `nat_03` — título da fonte rejeitado: "1942 HITS ARCHIVE: White Christmas - Bing Crosby (1942 version) (a #1 record)"
  - `STD.INT.ALL.POP.001` (2): `pop_04` — fonte "fallback" — nem canal Topic nem "Official Audio" (canal: 'Young Pilgrim Music', título: 'ABBA - Dancing Queen (Lyrics)'); `pop_02` — título da fonte rejeitado: "Like a Prayer (7" Version)"
  - `STD.INT.ALL.ROC.001` (3): `rock_04` — duração da fonte muito alta (391s > 320s) — por confirmar; `rock_05` — duração da fonte muito alta (340s > 320s) — por confirmar; `rock_03` — fonte "fallback" — nem canal Topic nem "Official Audio" (canal: 'Wind Music', título: 'AC/DC - Highway to Hell (lyrics)')
  - `STD.PT.70.WLD.001` (1): `zeca_afonso_grandola_vila_morena` — fonte "fallback" — nem canal Topic nem "Official Audio" (canal: 'luiisfdias', título: 'Zeca Afonso - Grândola, Vila Morena')
  - `STD.PT.80.MIX.001` (2): `pt80_02` — fonte "fallback" — nem canal Topic nem "Official Audio" (canal: 'RTP', título: '1981 - Carlos Paião - Play Back'); `pt80_04` — fonte "fallback" — nem canal Topic nem "Official Audio" (canal: 'Rui Lopes', título: 'Trovante - 125 Azul')
  - `TRB.UK.ALL.ROC.001` (1): `beatles_04` — posição especial de playlist tributo (tipo "foto")

- **Playlists "tributo" ficavam "(sem playlist)" — corrigido (11 Out 2026)**: `carregar_mapa_playlists()` só lia `playlists.json`'s `musicas` — a playlist "Tribute Beatles" (`TRB.UK.ALL.ROC.001`, único universo tipo `tributo`) usa `posicoes[]`/`mosaico` em vez disso, por isso as 8 faixas `beatles_*` nunca tinham `playlistCodigo` em nenhum relatório/ecrã. Corrigido nos dois scripts (`verificar_trechos.py`, `gerar_previews_defeitos.py`), ver `DECISIONS.md` 2026-10-11 para a regra completa (só posições tipo `audio`/`foto` seguem o motor automático; `trivia`/`solo`/`cover`/`riff`/`bateria`/`mosaico` ficam "formato especial"). Confirmado que nenhuma outra playlist do catálogo tem este problema (só `tributo`, um caso único). `_revisao_regeneracao.json` corrigido retroactivamente: só `beatles_04` fica no ecrã Revisão (playlistCodigo certo); `beatles_03/05/06/08/recap` removidos (pré-audições órfãs ficam em `_preview_revisao/`, não apagadas). Commit `23978cc`, enviado.

- **Ecrã Revisão — 2 bugs reais corrigidos (10/11 Out 2026)**: 1) sidebar "Playlists a rever" ficava vazia (às vezes sem nada, às vezes parcial) — o lote de pré-audições de 9 Out escreveu `playlistCodigo: null` nas 10 faixas sem playlist, e o `.sort((a,b) => a.nome.localeCompare(b.nome))` da sidebar rebentava com `nome: null` — excepção silenciosa (só na consola do browser) que impedia a sidebar E a actualização pós-geração de qualquer faixa (`revisaoAtualizarLeve`). Corrigido: `playlistCodigo`/`nome` nunca null (fallback `'(sem playlist)'`), manifesto e script geram sempre a string. 2) "Corrigir URL manualmente" → "Gerar pré-audição desta URL" não dava feedback nenhum — na prática era o MESMO bug (a chamada ao servidor funcionava bem, confirmado por `curl` directo, mas a actualização visual pós-sucesso rebentava pela mesma excepção); aproveitado para acrescentar feedback próprio e persistente (`⏳ a gerar…`/`✗ falhou: ...`) junto ao campo de URL, em vez de só o aviso genérico de 2,5s. Também: `/gerar-preview-revisao` passa a limpar `&list=`/`&start_radio=`/`&t=` do URL antes de descarregar (mesma receita já usada em `/gerar-faixa`, só lá existia) e o log do servidor passa a sem buffer (`python3 -u`, nos 3 `.command` de arranque) — sem isto, `tail`/`grep` ao log mostravam conteúdo horas desactualizado, dificultando qualquer diagnóstico futuro. "Don't Let Me Down" (`beatles_04`) já tem a pré-audição correcta (Official Audio remasterizado, não o vídeo de ensaio) — por aprovar no Studio. Commit `b751666`, enviado (`git push`).

- **Pré-audições dos 95 "defeito real" geradas e carregadas no ecrã Revisão (9 Out 2026)**: para cada faixa, o motor novo (Topic > Official Audio, nunca Video/MV/Live/Movie/Trailer/Scene/Teaser) escolheu UMA fonte, gerou Trecho A/B de 15s e correu o verificador — **95/95 passaram** (0 "por rever"), carregadas em `_revisao_regeneracao.json` com `estado: "pendente"`, agrupadas por pack (ordem: playlists "prontas" com mais defeitos primeiro, depois rascunho/protótipo, depois sem playlist). **Nenhum ficheiro de produção foi tocado** — só `_preview_revisao/*_proposta.mp3`. Progresso faixa a faixa (retomável): `relatorios/previews_defeitos_progresso.csv`.

  | pack | previews prontas |
  |---|---|
  | `(sem playlist)` | 10 |
  | `STD.INT.ALL.ROC.001` | 5 |
  | `STD.INT.ALL.POP.001` | 5 |
  | `STD.INT.ALL.HIP.001` | 5 |
  | `STD.INT.80.MIX.001` | 4 |
  | `STD.US.ALL.AME.001` | 4 |
  | `STD.INT.ALL.MET.001` | 4 |
  | `STD.PT.ALL.MIX.001` | 3 |
  | `RET.PT.90.VOZ.001` | 3 |
  | `STD.INT.ALL.GTR.001` | 3 |
  | `STD.PT.80.MIX.001` | 3 |
  | `STD.INT.ALL.MIX.001` | 3 |
  | `STD.INT.ALL.GAM.001` | 3 |
  | `STD.INT.ALL.NAT.001` | 3 |
  | `STD.INT.00.MIX.001` | 3 |
  | `STD.INT.20.MIX.001` | 3 |
  | `STD.BR.ALL.MIX.001` | 2 |
  | `STD.PT.ALL.BAT.001` | 2 |
  | `STD.INT.10.SYN.001` | 2 |
  | `STD.INT.10.SYN.002` | 2 |
  | `STD.INT.ALL.TV.001` | 2 |
  | `STD.INT.50.MIX.001` | 2 |
  | `STD.INT.60.MIX.001` | 2 |
  | `STD.INT.ALL.BLU.001` | 2 |
  | `STD.INT.ALL.SOU.001` | 2 |
  | `STD.INT.ALL.CLA.001` | 2 |
  | `STD.INT.ALL.LAT.001` | 2 |
  | `STD.INT.ALL.JAZ.001` | 2 |
  | `STD.INT.10.MIX.001` | 1 |
  | `STD.INT.ALL.MIX.005` | 1 |
  | `STD.INT.70.ROC.001` | 1 |
  | `STD.PT.70.WLD.001` | 1 |
  | `STD.INT.ALL.POP.002` | 1 |
  | `STD.PT.ALL.FAD.001` | 1 |
  | `LOGO-001` | 1 |
  | **TOTAL** | **95** |

  **⚠ 3 faixas passaram o verificador automático mas a fonte escolhida não é áudio puro — ouvir com atenção extra antes de aprovar**: `solo_01` (documentário BBC "How Stairway to Heaven was written", não a música), `beatles_04` (vídeo de ensaio "The Beatles: Get Back"), `beatles_03` ("The End Lesson by Mike Pachelli", vídeo de aula de guitarra). O filtro de título não apanha estes casos (sem "Video"/"Movie"/etc. literal no título) — o verificador passou porque o excerto de 15s escolhido calhou a soar parecido, não porque a fonte seja apropriada.

- **Verificador de trechos — reavaliação com múltiplos candidatos concluída (9 Out 2026)**: substitui a 1ª corrida (que só testava o 1º resultado do `ytsearch5`). Para as 128 "NÃO encontrado"/"ruído/diálogo" e as 31 "erro" da 1ª corrida, passou a testar até 5-6 candidatos por faixa (mesmo filtro de título, agora também rejeita "Movie"/"Trailer"/"Scene"/"Teaser") e as `*_mosaico` (formato `full`, sem `trecho_b`) passam a excluídas como "formato especial". Totais finais (323 faixas): **156 OK confirmado, 95 defeito real, 22 inconclusivo, 50 formato especial**. Tabela completa: `relatorios/reavaliacao_falhas.csv`; propostas de fonte alternativa das 43 faixas só OK num candidato diferente do 1º: `relatorios/propostas_fonte_audio.json` — **não aplicadas a catalogo.json**, ficam para revisão/aprovação.

  | pack | OK confirmado | defeito real | inconclusivo | formato especial |
  |---|---|---|---|---|
  | `(sem playlist)` | 11 | 10 | 4 | 27 |
  | `LOGO-001` | 7 | 1 | 0 | 0 |
  | `RET.INT.ALL.VOZ.001` | 0 | 0 | 0 | 8 |
  | `RET.PT.90.VOZ.001` | 4 | 3 | 0 | 1 |
  | `STD.BR.ALL.MIX.001` | 5 | 2 | 0 | 0 |
  | `STD.INT.00.MIX.001` | 4 | 3 | 0 | 0 |
  | `STD.INT.10.MIX.001` | 6 | 1 | 0 | 0 |
  | `STD.INT.10.SYN.001` | 4 | 2 | 0 | 0 |
  | `STD.INT.10.SYN.002` | 5 | 2 | 0 | 0 |
  | `STD.INT.20.MIX.001` | 4 | 3 | 0 | 0 |
  | `STD.INT.50.MIX.001` | 5 | 2 | 0 | 0 |
  | `STD.INT.60.MIX.001` | 5 | 2 | 0 | 0 |
  | `STD.INT.70.ROC.001` | 6 | 1 | 0 | 0 |
  | `STD.INT.80.MIX.001` | 2 | 4 | 1 | 0 |
  | `STD.INT.90.DNC.001` | 7 | 0 | 0 | 0 |
  | `STD.INT.ALL.BAT.001` | 0 | 0 | 0 | 7 |
  | `STD.INT.ALL.BLU.001` | 4 | 2 | 1 | 0 |
  | `STD.INT.ALL.CIN.001` | 0 | 0 | 0 | 7 |
  | `STD.INT.ALL.CLA.001` | 5 | 2 | 0 | 0 |
  | `STD.INT.ALL.GAM.001` | 4 | 3 | 0 | 0 |
  | `STD.INT.ALL.GTR.001` | 1 | 3 | 2 | 0 |
  | `STD.INT.ALL.HIP.001` | 2 | 5 | 0 | 0 |
  | `STD.INT.ALL.JAZ.001` | 5 | 2 | 0 | 0 |
  | `STD.INT.ALL.LAT.001` | 5 | 2 | 0 | 0 |
  | `STD.INT.ALL.MET.001` | 3 | 4 | 0 | 0 |
  | `STD.INT.ALL.MIX.001` | 3 | 3 | 1 | 0 |
  | `STD.INT.ALL.MIX.005` | 3 | 1 | 3 | 0 |
  | `STD.INT.ALL.NAT.001` | 3 | 3 | 1 | 0 |
  | `STD.INT.ALL.POP.001` | 2 | 5 | 0 | 0 |
  | `STD.INT.ALL.POP.002` | 4 | 1 | 2 | 0 |
  | `STD.INT.ALL.ROC.001` | 2 | 5 | 0 | 0 |
  | `STD.INT.ALL.SOU.001` | 5 | 2 | 0 | 0 |
  | `STD.INT.ALL.SYN.001` | 7 | 0 | 0 | 0 |
  | `STD.INT.ALL.TV.001` | 5 | 2 | 0 | 0 |
  | `STD.PT.70.WLD.001` | 3 | 1 | 3 | 0 |
  | `STD.PT.80.MIX.001` | 4 | 3 | 0 | 0 |
  | `STD.PT.ALL.BAT.001` | 2 | 2 | 1 | 0 |
  | `STD.PT.ALL.FAD.001` | 3 | 1 | 1 | 0 |
  | `STD.PT.ALL.MIX.001` | 2 | 3 | 0 | 0 |
  | `STD.PT.ALL.WLD.001` | 2 | 0 | 2 | 0 |
  | `STD.US.ALL.AME.001` | 2 | 4 | 0 | 0 |
  | **TOTAL** | **156** | **95** | **22** | **50** |

  **2 bugs reais do verificador, encontrados e corrigidos a meio desta reavaliação**: 1) só gravava resultados no fim — um `TimeoutExpired` não tratado a meio matou o processo e perdeu 58 faixas já calculadas (corrigido: grava a cada faixa, retoma sozinho sem repetir trabalho); 2) o YouTube começou a bloquear com "Sign in to confirm you're not a bot" a meio da corrida (volume de pedidos desta sessão), contaminando 27 resultados com falsos "defeito"/"inconclusivo" (corrigido: retentativa automática com `--cookies-from-browser chrome`, mesmo padrão já usado em `gerar_faixa.py`; as 27 foram todas reprocessadas depois da correcção).

  **Caso especial**: `logo_01` não é "defeito de conteúdo" — o `trecho_a.ficheiro` está mesmo em falta no disco.

  **22 inconclusivo**: sem candidato fiável para concluir nada (pesquisa sem resultados, timeout, ou download bloqueado em todos os candidatos) — não são "sem problema", só não há dados suficientes. Lista em `relatorios/reavaliacao_falhas.csv` (categoria "inconclusivo").

  **defeito real (95, por pack — todos os candidatos testados falharam):**
  - `(sem playlist)`: beatles_03, beatles_04, beatles_05, beatles_06, beatles_08, beatles_recap, donna_summer_i_feel_love, gnr_dunas, maurice_jarre_lara_s_theme_somewhere_m, rush_tom_sawyer
  - `LOGO-001`: logo_01
  - `RET.PT.90.VOZ.001`: pt_07, ptbat_02, ptbat_04
  - `STD.BR.ALL.MIX.001`: bra001_04, bra001_06
  - `STD.INT.00.MIX.001`: dec00_03, dec00_05, dec00_06
  - `STD.INT.10.MIX.001`: a10_06
  - `STD.INT.10.SYN.001`: new_order_blue_monday, talk_talk_it_s_my_life
  - `STD.INT.10.SYN.002`: future_islands_seasons_waiting_on_you, hurts_miracle
  - `STD.INT.20.MIX.001`: dec20_02, dec20_05, dec20_06
  - `STD.INT.50.MIX.001`: dec50_05, dec50_06
  - `STD.INT.60.MIX.001`: dec60_01, dec60_03
  - `STD.INT.70.ROC.001`: bat_08
  - `STD.INT.80.MIX.001`: 80_03, 80_04, 80_05, 80_07
  - `STD.INT.ALL.BLU.001`: blues_01, blues_05
  - `STD.INT.ALL.CLA.001`: cla_02, cla_06
  - `STD.INT.ALL.GAM.001`: gam_01, gam_02, gam_07
  - `STD.INT.ALL.GTR.001`: solo_01, solo_05, solo_07
  - `STD.INT.ALL.HIP.001`: hip_01, hip_02, hip_03, hip_04, hip_07
  - `STD.INT.ALL.JAZ.001`: jazz_04, jazz_06
  - `STD.INT.ALL.LAT.001`: lat_04, lat_05
  - `STD.INT.ALL.MET.001`: metal_02, metal_03, metal_06, metal_07
  - `STD.INT.ALL.MIX.001`: buena_vista_social_club_tres_palabras, sarah_mclachlan_surfacing, thelonious_monk_crepuscule_avec_pauline
  - `STD.INT.ALL.MIX.005`: america_a_horse_with_no_name
  - `STD.INT.ALL.NAT.001`: nat_02, nat_03, nat_04
  - `STD.INT.ALL.POP.001`: pop_01, pop_02, pop_03, pop_04, pop_05
  - `STD.INT.ALL.POP.002`: christina_aguilera_reflection
  - `STD.INT.ALL.ROC.001`: rock_03, rock_04, rock_05, rock_06, rock_07
  - `STD.INT.ALL.SOU.001`: soul_01, soul_07
  - `STD.INT.ALL.TV.001`: tv_01, tv_05
  - `STD.PT.70.WLD.001`: zeca_afonso_grandola_vila_morena
  - `STD.PT.80.MIX.001`: pt80_02, pt80_04, pt80_06
  - `STD.PT.ALL.BAT.001`: ptbat_03, ptbat_07
  - `STD.PT.ALL.FAD.001`: amalia_rodrigues_estranha_forma_de_vida
  - `STD.PT.ALL.MIX.001`: pt_02, pt_03, pt_05
  - `STD.US.ALL.AME.001`: ame_03, ame_05, ame_06, ame_07
- **Varrimento do catálogo por fontes "videoclipe" (8 Out 2026, diagnóstico, só metadados)**: motivado por `a10_04` e por **dec00_01** ("Hey Ya!", OutKast — Faixa 1 do pack "Anos 2000"/`STD.INT.00.MIX.001`, `trecho_a.ficheiro = "dec00_01_a.mp3"`, inicio 0/fim 12), cujo Trecho A o André reportou começar com conversa. `dec00_01` tem `video: null` — veio da "Revisão YouTube" de Ago/Set (backup committado em `_backup_pre_regeneracao/dec00_01_a.mp3`) e a fonte usada nessa altura não ficou registada no catálogo, por isso **não aparece neste varrimento** (que só consegue avaliar faixas com campo `video` preenchido) — ponto a investigar à parte. Varridos os 348 ids do catálogo: 88 têm `video` preenchido; destes, **53 estão com o vídeo indisponível/privado no YouTube** (confirmado por `yt-dlp --skip-download`, repetido em série — não é falha de rede/concorrência), sobram 35 com metadados válidos. Dessas 35, **27 têm título "Official Video"/"Music Video" e/ou duração bem acima do habitual para um single** — candidatas a ter sido cortadas do videoclipe em vez do áudio, tal como `a10_04`:
  - `STD.INT.10.MIX.001` (Anos 2010): `a10_01` Work (454s!), `a10_02` Shape of You, `a10_03` Uptown Funk, `a10_05` Rolling in the Deep, `a10_06` Old Town Road — só `a10_07` (Bad Guy) e `a10_04` (já corrigido) ficam de fora.
  - `STD.INT.80.MIX.001` (Anos 80): `80_01/02/04/05/06/07` — praticamente o pack todo.
  - `RET.INT.ALL.VOZ.001` (Retrato): `ret_01/03/04/05/06`.
  - `STD.INT.ALL.BAT.001` (Batera): `bat_01/02/07`.
  - `STD.INT.ALL.CIN.001` (Cinema): `cinema_01/02/05` — **aviso**: aqui a duração alta pode ser genuína (temas instrumentais/clássicos longos por natureza, ex. Star Wars/Stairway to Heaven), o sinal de duração sozinho dá falsos positivos nestes casos; só o sinal de título ("Official Video") é fiável sem referência à duração real do single.
  - `STD.US.ALL.AME.001`: `ame_05` Take It Easy.
  - Sem playlist associada: `cinema_mosaico`, `pedro_abrunhosa_socorro`.
  - **Nada suspeito** nas restantes 8 válidas: `beatles_01/02`, `a10_07`, `ame_01/04`, `cinema_03`, `syn001_05`.
  - Limitação do método: sem `fpcalc`/chromaprint instalado, isto é só heurística de título+duração dos metadados do YouTube — não confirma conteúdo real do ficheiro já cortado (só ouvir resolve isso, como aconteceu com `a10_04`).
  - Downloads temporários apagados no fim; nada alterado em `catalogo.json`/`.mp3`.

- **Resolvido — "Blinding Lights" (a10_04) refeito a partir do Official Audio (8 Out 2026)**: Trecho A tocava uma música de Justin Bieber em vez de The Weeknd (erro na geração original do pack, commit inicial `2df29b9`). Primeira tentativa de correcção usou o videoclipe oficial (`4NRXx6U8ABQ`) como fonte — **descartada**: o André ouviu a pré-audição e detectou ruído de carros da cena do videoclipe por cima da música (o `volumedetect` não apanhou isto — só mede intensidade, não distingue música de ruído/fala). Refeito a partir de **"The Weeknd - Blinding Lights (Official Audio)"** (`https://www.youtube.com/watch?v=fHI8X4OXluQ`, 203s, bate com a duração do single ~3:20). Trecho A = 4s–19s (intro/1.ª estrofe), Trecho B = 72s–87s (refrão) — ambos ouvidos e aprovados pelo André antes de substituir, 15,00s confirmado por `ffprobe` em cada. `catalogo.json`: novo campo `fonte_audio` com o novo URL (`video` mantém-se `4NRXx6U8ABQ`, inalterado a pedido; inicialmente escrito em `sources.audio`, uniformizado para `fonte_audio` no mesmo dia — ver abaixo). **Notas para o resto do pack**:
  - `a10_*`: Trecho A das outras 6 faixas (`a10_01/02/03/05/06/07`) tem duração legada 19–30s (vs. os 15s fixos do `a10_04` refeito e o padrão actual do resto do catálogo, `DECISIONS.md` 10 Ago 2026) — normalizar para 15s (a decidir).
  - Fontes de áudio: usar sempre **Official Audio**, nunca o videoclipe — videoclipes oficiais podem ter cena/ruído sem música no início ou por cima da música, e o `volumedetect` não detecta isso; é preciso ouvir antes de aprovar qualquer corte. Regra formalizada em `DECISIONS.md` 2026-10-08.

- **Resolvido — "Hey Ya!" (dec00_01) refeito a partir do Official Audio (8 Out 2026)**: Trecho A começava com diálogo do videoclipe (Faixa 1 do pack "Anos 2000"/`STD.INT.00.MIX.001`). Refeito a partir de **"Hey Ya! — Outkast"** (`https://www.youtube.com/watch?v=-7XnDlYY9qw`, canal Topic "Provided to YouTube by Legacy Recordings", 236s, bate com o single ~3:55). Trecho A = 0s–15s (ajustado 5s mais cedo a pedido do André após ouvir a 1ª preview), Trecho B = 142s–157s (refrão) — ambos ouvidos e aprovados antes de substituir, 15,00s confirmado por `ffprobe`. `catalogo.json`: `trecho_a.fim` 12→15, `trecho_b.inicio/fim` 18/30→142/157, novo campo `fonte_audio`. Servido por `_servidor_escrita.py` (porta 8002) directamente do disco, sem cache (`Cache-Control: no-store` em toda a resposta) — não precisa de rebuild/reinício.
- **`fonte_audio` uniformizado (8 Out 2026)**: `a10_04` e `dec00_01` usam agora o mesmo campo de topo `fonte_audio` (string, URL) — `sources.audio` volta a `null` em todo o catálogo, deixa de ser usado para isto.
- **Apóstrofos (catalogo.json)**: scan completo confirma **0 entradas afectadas** — o bug (`escapeAttr` a cortar apóstrofos em `value="..."`) era só de visualização no ecrã de revisão da IA, nunca chegou a ser gravado no catálogo. Nada para aprovar nem escrever; já corrigido (ver commit "Fix(studio): preservar apóstrofos nas sugestões da IA").
- **Push concluído 6 Out 2026** (`8a205cd..81c0408`, 100 commits + LFS); necessário `git config http.postBuffer 524288000` por HTTP 400 num push de ~188MB.

- **Arrumação do repositório — aplicada (6 Out 2026)**: `creditos_imagem.md` commitado; `MusicBox_Format_Bible_V3_28.docx` e `"Notas Music Box/"` movidos para `_arquivo/` (sem decisões por copiar — o docx só chega ao Capítulo 28 com datas até 8 Ago 2026, tudo já reflectido na Bíblia actual; a pasta de notas só tinha um link do YouTube); os 8 ficheiros de backup committed sem referência (`git rm --cached`) + 2381 `.bak` mais antigos de `backups_catalogo/` (mantidos os 10 mais recentes) + `.wav` de teste antigos também movidos para `_arquivo/` (fora do git, `_arquivo/` agora no `.gitignore`) — nada apagado do disco. `NOTAS -  POR FAZER.docx` tinha um pedido em aberto — "quero auditoria total a todas as faixas Trechos, Imagens etc em todo o catálogo" — **feito em 6 Out 2026**, ver `docs/auditoria_catalogo_2026-10-06.md` (83 problemas, todos "cosmético" — 0 bloqueiam o jogo ou afectam o piloto); o ficheiro `.docx` foi depois movido para `_arquivo/`, como os restantes. Tamanho do projecto antes/depois: 2,1GB/2,1GB (nada apagado, só reorganizado); `git status` limpo (só `mp3_index.json`, outra sessão); jogo e Studio testados a carregar sem erros.

- **Revisão YouTube — 101 faixas revistas, só 26 aplicadas (6 Out 2026, diagnóstico)**: `_revisao_regeneracao.json` tem 71 "aprovado" (ouvidas e aprovadas no Studio, preview em `_preview_revisao/`, ainda NÃO aplicadas — catálogo/mp3 de produção intocados), 26 "regenerado" (script já trocou os `.mp3`, playlists Anos 2000/6, Anos 2010 Synth II/6, Anos 2020/7, Hip Hop/7) e 4 "rejeitado". Confirmado por `git log`: nenhuma das 71 pendentes teve a entrada em `catalogo.json` alterada desde a data do preview (4 Out) — nenhuma desactualizada. Nenhum ficheiro de áudio é partilhado por mais de uma faixa. **Ponto de atenção**: Hip Hop está marcado "regenerado" mas os `.mp3` de produção actuais vêm do commit `4c6cf1b` ("hip_* reprocessados", 4 Out, depois do estado "regenerado" ter sido escrito) — não é claramente o resultado aprovado no ecrã de Revisão; confirmar por audição antes de dar como aplicado. **Risco de dados**: os 40 ficheiros de backup (20 faixas: `dec20_01..07`, `hip_01..07`, `hurts_miracle`/`chromatics_tick_of_the_clock`/`arctic_monkeys_do_i_wanna_know`/`grimes_oblivion`/`disclosure_latch`/`lcd_soundsystem_home`) em `_backup_pre_regeneracao/` nunca foram commitados (ficaram cobertos pela regra `.gitignore` adicionada depois da 1ª aplicação) — só existem em disco; se perdidos, os originais pré-regeneração dessas 20 faixas são irrecuperáveis (ao contrário de "Anos 2000", cujos 6 backups estão commitados). Proposta de ordem de aplicação das 13 playlists pendentes (uma a uma, com backup + commit por playlist) à espera de aprovação do André — ver conversa de 6 Out 2026.
- **Salvaguarda extra dos backups (6 Out 2026)**: `_backup_pre_regeneracao/` copiada (`cp -R`) para `~/Documents/MusicBox_backups/_backup_pre_regeneracao_2026-10-06/` (fora do git e do Dropbox) — 52 ficheiros, 15.832.396 bytes, confirmado igual em origem e destino.
- **Jazz aplicada (6 Out 2026)**: `_aplicar_regeneracao_playlist.py STD.INT.ALL.JAZ.001` — 4 faixas (`jazz_01`, `jazz_02`, `jazz_03`, `jazz_05`) passam a "regenerado"; 8 originais em `_backup_pre_regeneracao/`; `catalogo.json` sem alterações (confirmado por `git diff --stat`); commit `0328725`.
- **Anos 50, Gaming, TV/Cinema aplicadas (7 Out 2026)**: mesmo script, uma playlist por vez, cada uma com `catalogo.json` inalterado (confirmado) e commit próprio — Anos 50 (3 faixas: `dec50_03/04/07`; `dec50_02` ficou "rejeitado", intocada; `a811c44`), Gaming (3 faixas: `gam_03/04/06`; `gam_01`/`gam_07` "rejeitado", intocadas; `b7bd732`), TV/Cinema (5 faixas: `tv_01/03/04/06/07`; `626e43c`). Salvaguarda externa (`~/Documents/MusicBox_backups/_backup_pre_regeneracao_2026-10-06/`) actualizada com os 22 backups novos destas 3 playlists + os 8 do Jazz que tinham ficado de fora na cópia anterior — agora 82 ficheiros / 24.140.006 bytes, confirmado igual em origem e destino.
- **Rock, Latina, Soul, Natureza, Clássica, Anos 60, Blues, Metal, Pop aplicadas (7 Out 2026)**: mesmo script, uma playlist por vez, cada uma com `catalogo.json` inalterado (confirmado) e commit próprio — Rock (5 faixas; `ef1d497`), Latina (6; `f7ec8f6`), Soul (6; `7679ea7`), Natureza (6; `f565965`), Clássica (5; `cla_02` "rejeitado" intocada; `0d75aa9`), Anos 60 (7; `34b0f4d`), Blues (7; `0970509`), Metal (7; `e700ba5`), Pop (7; `05a1d5d`). Salvaguarda externa actualizada com os 112 backups novos — agora 194 ficheiros / 55.426.643 bytes, confirmado igual em origem e destino. **As 13 playlists pendentes do diagnóstico de 6 Out estão todas aplicadas.** Só falta confirmar por audição o ponto de atenção do Hip Hop (regenerado antes desta sessão, sobreposto depois por `4c6cf1b`).

## 2026-10-05 (continuação pós-fecho) — Fototeca aplicada, Disney, filtros, Mosaico redesenhado

**Commits** (`84e2d08`..`HEAD`, mais antigo → mais recente):
- `02dac22` — Fototeca: 10 faixas herdam `imagem`+campos de licença da faixa de origem (proposta aprovada).
- `54c1992`/`5c26e4b` — playlist Disney (modo Elo, `STD.INT.ALL.POP.002`): feedback (`fb_045`) + índice de áudio + os 16 `.mp3` (via Git LFS) — trabalho da outra sessão, revisto e commitado por esta a pedido explícito do utilizador.
- `6a34808` — Studio: filtros activos da sidebar (Década/Estilo/Geo/Dificuldade/Tipo/Estado) e "✕ Limpar filtros" destacados a amarelo (`var(--accent)`); lista vazia mostra quais filtros estão a esconder resultados.
- `c7ea11c` — **Mosaico deixa de estar ligado às respostas certas** (Bíblia §5.11/§27.7, §9.8/§3.8 revistas): revelação automática dos 16 quadrados a intervalos regulares ao longo de 30s (`MOSAICO_DURACAO_MS`, finalmente alinhado com a Bíblia); acerto antes do fim = cascata de ~1s; ninguém acerta = fim automático aos 30s com rede de segurança que garante a imagem completa. Diagnóstico confirmou que a ligação visual Faixa→quadrado já não existia na grelha — só textos ("quadrado X conquistado") é que ainda a sugeriam, agora removidos. Pontuação/dinheiro não dependiam de quadrados — inalterados.

**Repositório remoto**: ver "À espera de decisão do André" acima — push nunca feito, falta credencial.

## 2026-10-05 (fecho de sessão) — Bíblia, curadoria, vozes por língua, Mosaico, Studio

**Commits** (`b965a4b`..`HEAD`, mais antigo → mais recente):
- `21ea7bc`/`8ba2757` — Bíblia (`BIBLIA.md`) entra no repositório (V3.29) e é reconciliada com `DECISIONS.md`, sobe a V3.30 (§30.9).
- `efc91ea`/`36401ea` — corrige entrada Alex/Oliver em `DECISIONS.md`; dicionário de pronúncia da narração do descritivo (`voz/pronuncia_descritivo.json`), 20 vozes regeneradas.
- `11aecfc` — escala de dificuldade 1-5 confirmada como oficial (§15.5), §27.13 marcada revista.
- `ca73de6`/`bab5a85` — `CLAUDE.md` com regras de poupança de contexto; dois blobs base64 (BEATLES_02) removidos de `musicbox.html` (515KB→249KB).
- `5f9c4bd`/`bbad1b3` — regra "unicidade de artista conta membros de banda" (Bíblia §27.2) + aviso não-bloqueante na Mesa de Montagem; corrige o caso real (Queen × 2 em "Anos 70 — Rock", `bat_02`→`bat_08`/Keith Moon).
- `3857622`/`0c47dc9` — nomes de artista por língua (`voz/pronuncia.json`: Duarte/Antonio/fr/es/it/de/ru/Vangelis+japoneses também em Duarte), 79 vozes regeneradas. **Bug real corrigido**: 1ª versão do índice de regeneração (`nome_index.json`) sem baseline prévio tinha regenerado as 348 vozes em vez de só as afectadas — corrigido antes de aplicar.
- `3ee3bed` — anúncio de voz no acerto do Mosaico (`voz/mosaico_<código>.wav`, 38 gerados) + wiring em `confirmarMosaicoAcerto()`. **Bug real corrigido**: playlists com chave legada em `COLLECTIONS` (ex. "ANOS80") usavam o nome de ficheiro errado — corrigido para `playlistCodigo`.
- `cf9370e` — apóstrofos preservados nas sugestões da IA no Studio (`escapeAttr`→`escapeHtml` em 21 campos `value=`); confirmado 0 entradas de `catalogo.json` realmente afectadas.
- `4ed1e91` — pré-escuta de voz (▶) junto ao artista/Mosaico na Mesa de Montagem, novo endpoint `/listar-voz`.
- `e65568d` — Fototeca: candidatas (faixas fora de playlists prontas) escondidas por defeito, filtro "Sem imagem".
- (Fototeca, herança de imagem, aprovada) — 10 faixas copiaram `imagem`+campos de licença da faixa de origem (`imagem_licenca_estado:"confirmar"` em todas, para a revisão de licenças antes do piloto). Restantes 12/22 faixas sem imagem não têm candidata a herdar — precisam de pesquisa de imagem nova: `fausto_topic_lembra_me_um_sonho_lindo`, `madredeus_povo_que_lavas_no_rio`, `peret_al_alba`, `francisco_fanhais_menino_do_bairro_negro`, `luis_cilia_trova_do_vento_que_passa`, `nightwish_sahara`, `the_doors_riders_on_the_storm`, `the_doors_riders_on_the_storm_2`, `tinariwen_touareg`, `tinariwen_cler_achel`, `chris_rea_the_road_to_hell`, `tame_impala_sahara`.

**À espera de decisão do André**: ver secção própria abaixo (apóstrofos — nada a aprovar; proposta de herança de imagem na Fototeca — 10 faixas).

**Confirmado alinhado**: `DECISIONS.md` e `BIBLIA.md` têm entrada para cada decisão de formato desta sessão (Encore/volumes, voz pós-acerto, Pergunta Bónus Décadas/Estilos, Géneros→Estilos, descritivos sem spoilers, dificuldade 1-5, unicidade de artista, vozes por língua, Mosaico) — nenhuma pendente de registo.

## À espera de decisão do André

- Rever os descritivos reescritos sem spoilers (commit `b075be2`) — tom e conteúdo.
- Rever as perguntas bónus geradas por IA (quando existirem).
- Rever as imagens com `imagem_licenca_estado: "confirmar"`.
- Rever versões de faixas cover vs. original (ex.: playlist Disney — "Kiss the Girl", "Be Our Guest").
- Substituir as vozes edge-tts por voz licenciada ou locutor real.
- Uniformizar artistas duplicados no catálogo (ex.: José Afonso / Zeca Afonso).
- Limpar as 3 versões da playlist Deserto (`.002`/`.003`/`.004`).
- A posição "Baterista" da Anos 70 — Rock (`bat_08`, Keith Moon) reaproveita o áudio de banda (`rock_06`, Baba O'Riley) — antes do piloto, preparar um Trecho A/B próprio onde a bateria do Keith Moon se destaque.

## 2026-10-05 (continuação) — Narração do descritivo, Substituir na Montagem, família "Estilos"

**Commits** (`26f4613`..`HEAD`, mais antigo → mais recente):
- `26f4613`/`cbf53a1` — toggle de narração (preparado) + edge-tts marcado como só-protótipo (`DECISIONS.md`).
- `a670648`/`b075be2`/`657011e` — gerador `gerar_vozes_descritivo.py` (Duarte, edge-tts), descritivos sem spoilers reescritos (3 playlists: TV, Videojogos, Blues), voz gerada para as 40 playlists com `descritivo_apresentador`.
- `0375f88`/`f9e69fc` — 1ª versão da narração (automática) + botão "Gerar voz do descritivo" no Studio (endpoint `/gerar-voz-descritivo`).
- `82ec047` — lista de faixas + Mosaico escondida por defeito no ecrã de Verificação Rápida (evita spoiler).
- `78067d3` — sistema de estados aprovada/gravada: decisão de adiar, registada.
- `647f176` — "✎ Substituir" (3 alternativas da IA) também na Mesa de Montagem, para playlists já guardadas — não só na criação.
- `a6dd968` — **narração redesenhada**: deixa de ser automática — botão "🔊 Apresentação" manual (toca/pára, repetível), nunca bloqueia "▶ Iniciar Playlist"; toggle ON/OFF removido; `.topo` "⚙ Studio" → "Music Box Editor" (ícone sliders).
- família "Géneros" → "Estilos" no texto visível (`FAMILIA_GENEROS` continua a existir como identificador, só o valor mostrado mudou) — `DECISIONS.md` tem o detalhe completo.
- Pergunta Bónus nas famílias Décadas/Estilos (Faixa 4, `FAIXA_BONUS_MUSICAL`) — implementada no jogo e no Studio, 46 perguntas geradas por IA e gravadas, botão "✓ Revisto" no Studio (`2fd1b17`).
- `08ddc11` — **sinal sonoro da Pergunta Bónus**: `efeitos/bonus.wav` ("ding-ding-DING", 3 notas de sino ascendentes), toca uma vez quando o painel do BONUS_MODE aparece (Décadas/Estilos Faixa 4, Especiais Faixas 3/6); testado com Playwright, verificação graciosa sem ficheiro.

**Pendente desta sessão, ainda por fazer:**
- Nomes por língua (Duarte/Antonio/fr/es/it/de/ja/ru/el) — implementado, `voz/pronuncia.json`, 75 vozes regeneradas. Pendente: confirmar Vangelis (grego soa mal, a testar Alex vs. Duarte/"Vanguélis") e os 3 japoneses (Koji Kondo/Nobuo Uematsu/Yoko Shimomura, a testar romaji-Alex vs. fonética PT-Duarte) — ficam em Alex até decisão.
- Anúncio de voz no acerto do Mosaico — implementado (`voz/mosaico_<codigo>.wav`, 38 gerados, mesmas regras de voz por língua). Nota: nenhum mosaico tem hoje `pessoa` vazia (0/38, confirmado por scan) — o exemplo citado (STD.INT.ALL.MIX.004) não existe nos dados actuais.
- `BIBLIA.md`: no repositório desde V3.29 (`21ea7bc`); reconciliado com `DECISIONS.md` e subido para V3.30 (ver §30.9). §27.13 vs §15.5 resolvido — escala de dificuldade oficial é 1-5 (§15.5); §27.13 marcada revista/substituída.

## 2026-10-04/05 — Sessão 4-5 Out 2026

**Commits de hoje** (mais antigo → mais recente):
- `6148955` — fix(audio): 80_01 (Take On Me, a-ha) — remove silêncio residual no início do Trecho A.
- `571681e` — feat(audio): frase única de anúncio "[Artista] — In the Box!" (302 ficheiros de voz gerados) + fix da colisão em `CATALOGO_POR_FICHEIRO_A` por ficheiro de áudio partilhado.
- `07e0993` — docs: actualiza `DECISIONS.md` com o trabalho de 2026-09-17 a 2026-10-04 (ficheiro estava parado desde 28 Ago).
- `b7ba9bf` — feat(studio): painel direito colapsável na Mesa de Montagem + estilo âmbar para faixas substituídas (antes tachado, confundia-se com rejeição).
- `cf6fccc` — feat(studio+app): `elo_explicacao` pedido em todas as faixas da geração inicial (não só substituições), UI de "Gerar trechos" deixa claro que é automático, botões de acção global movidos para o topo da Mesa de Montagem, `MOMENTO_RESPOSTA_MS` 2000→4000.
- `1527512` — feat(app+studio): botão "ℹ Saber mais" no ecrã de escolha de playlist (prévia do descritivo sem seleccionar) + campo `nota_editorial` por faixa, por posição, em `playlists.json`.
- `ed41535` — fix(studio): guardar deixa de bloquear por playlists novas ainda não gravadas em disco (`PLAYLISTS_CHAVES_DISCO`).
- `1b3e16a` — UI: botão "ℹ Saber mais" compacto (ícone-só, 24×24 circular) nos cards de playlist + "Studio" renomeado para "Music Box Editor".
- `41cbe84` — UI: ícone outline (sliders, estilo Lucide) a substituir o emoji 🎛 no botão "Music Box Editor".
- `f67b080` — Áudio: voz Alex r205 (nome natural) + "In the Box!!" partilhado em ficheiro único, ducking com fade suave.
- `9ab2f86` — Docs: Status — decisão final da voz pós-acerto.
- `fda4fe0` — Fix: referências à nova pasta `voz/` + verificação única do roar (evita 404 repetido por acerto).
- `76dd455` — UI: Décadas em painel estilo Studio (linhas densas + árvore por década) — substitui a 1ª tentativa em cards verticais, descartada sem commit.
- `4c6cf1b` — Dados: playlist "Areias do Tempo" (Elo Deserto, `STD.INT.ALL.MIX.005`) + faixas novas — **trabalho da outra sessão, commitado por esta a pedido explícito do utilizador** (excepção pontual à separação habitual, ver nota no fim desta secção).
- `bd1e9c9` — Dados: renomear "Anos 2010+" para "Anos 2010" em `playlists.json`/`musicbox.html`.
- `4cf5701` — UI: filhos de grupo (painel por categoria) sem repetir o título da linha-mãe.
- `a69ad22` — UI: Géneros e Especiais no painel estilo Studio (generalização de `af_renderPainelDecadas` → `af_renderPainelCategoria`) + limpeza de código morto (`.playlist-card`/`.categoria-carrossel`, `ordenarChavesPorFamilia()`).
- `142d5aa` — Áudio: duck 0.25 na voz, 0.45 na janela Encore (`VOL_ENCORE`, novo), 0.75 no Trecho B — "meio-termo" entre o comportamento antigo e a proposta testada em `propostas/sample_*.wav`.
- `d05edeb` — Tools: `gerar_vozes_nome_artista.py` (gerador reutilizável, Alex r205) + os 302 `voz/nome_*.wav` + `efeitos/in_the_box.wav` convertidos de 192kHz para 44.1kHz (sem regenerar a voz).
- `f31857a` — Fix: favicon inline em `musicbox.html`/`musicbox_studio.html` — elimina o 404 "fantasma" (confirmado ser `/favicon.ico`, invisível aos eventos de rede do Playwright, só visível na consola).

**Verificação tarefa a tarefa:**

- ✅ Botão "i" circular 24×24 nos cards de playlist (`1b3e16a`) — inclui o fix de especificidade CSS `#teste-lista .btn-saber-mais` (a regra `#teste-lista button`, mais específica, estava a sobrepor o círculo para quadrado).
- ✅ "Studio" → "Music Box Editor" com ícone SVG outline sliders (`1b3e16a` + `41cbe84`).
- ✅ **Voz pós-acerto — decisão final e implementada (`f67b080`)**: investigação feita — a voz é gerada **offline** com o comando `say` (macOS) + efeito festivo em `ffmpeg` (pitch/volume), **não** `speechSynthesis` do browser. Proposta de comandos embutidos `[[pbas +N]]`/`[[pmod +N]]` **ABANDONADA** — sintaxe com "+" não documentada pela Apple, comandos inválidos são ignorados em silêncio pelo motor de fala (sem erro, sem aviso). **Nova arquitectura em produção**: 3 ficheiros encadeados no browser (`testeTocarSequenciaSom()`) — `voz/nome_<id>.wav` (302 ficheiros, voz **Alex, rate 205**, tom natural, sem efeito) → pausa 120ms → `efeitos/in_the_box.wav` (ficheiro único partilhado, "In the Box!!" eufórico, voz Alex rate 235 + compressão/reverb) → `efeitos/roar.wav` (ainda não existe — sequência salta-o graciosamente até existir). Nenhuma voz "Enhanced"/"Premium" está instalada nesta máquina — todas as comparações (Alex/Samantha/Daniel/Oliver) foram com vozes "compact". 302 ficheiros antigos (`_preview_voz_artista_*.wav`) removidos do repositório, backup local em `_backup_voz_2026-10-04/` (fora do git).
- ✅ **Ducking da música pós-acerto — implementado (`f67b080`)**: `VOL_MUSICA=0.75`/`VOL_DUCK=0.25`/`FADE_DOWN_MS=300`/`FADE_UP_MS=600`, constantes no topo do script. `fadeVolume()`/`cancelarFadeVolume()` com `requestAnimationFrame`, cancelável por token. Rede de segurança testada (interrupção a meio do fade repõe o volume de imediato, nunca fica preso em `VOL_DUCK`). Bug real apanhado e corrigido em teste: timestamp do `requestAnimationFrame` podia ser anterior ao `performance.now()` síncrono, dando `t` negativo no 1º frame do fade e o volume ultrapassava 1.0 — corrigido com `Math.max(0, ...)` no clamp.
- ❌ Roar — pasta `efeitos/` existe mas só tem `in_the_box.wav`; `roar.wav` ainda não existe. Utilizador vai descarregar um efeito livre (Pixabay/Freesound CC0).
- ✅ **Painel estilo Studio — Décadas, Géneros e Especiais (`76dd455`, `4cf5701`, `a69ad22`)**: linhas densas (não cards verticais — essa 1ª versão foi descartada a meio, sem commit), agrupamento por segmento do código (3º para Décadas/cronológico, 4º para Géneros/alfabético, Especiais nunca agrupa), árvore com conectores CSS (├/└), chevron a rodar, "i" sem iniciar a playlist. Função única `af_renderPainelCategoria()` partilhada pelos 2 sítios (grelha de teste + Escolha de Universo real) e pelas 3 famílias — substituiu `.playlist-card`/carrossel/`ordenarChavesPorFamilia()`, removidos por serem código morto. Fallback de códigos legados sem pontos (ex. `TRB-BEA-001`) generalizado para 2º segmento por "-". Lista completa de códigos não-conformes ao formato `TIPO.GEO.DEC.GEN.NNN` dada ao utilizador (não migrados).
- ✅ "Anos 2010+" → "Anos 2010" em todo o projecto (`bd1e9c9`) — `playlists.json`/`musicbox.html` actualizados; `episodio_piloto2/3.html` e `backups/` deixados de fora (fora do âmbito pedido / ficheiros históricos).
- ✅ **Volume pós-acerto "meio-termo" (`142d5aa`)**: nova constante `VOL_ENCORE=0.45` — duck a `VOL_DUCK` (0.25) durante nome+"In the Box!!", sobe a `VOL_ENCORE` (fade 300ms) durante a pausa + janela de decisão do Encore, só sobe a `VOL_MUSICA` (fade 600ms) quando o Trecho B arranca mesmo. Testado com Playwright nos dois caminhos (Encore escolhido/não escolhido), volumes medidos por passo batem certo com o esperado. **Bug real encontrado e corrigido**: `iniciarFaixa()` repunha `audio.volume=1` (resquício de antes de `VOL_MUSICA` existir) em vez de `VOL_MUSICA` — a música normal de cada Faixa nova tocava sempre a volume máximo, não ao nível "normal" pretendido.
- ✅ **Gerador de vozes + 44.1kHz (`d05edeb`)**: `gerar_vozes_nome_artista.py` na raiz (sem argumentos = só as que faltam; `--todos` com backup; `--id <id>`), testado (duração igual ao original, diferença de microssegundos). Os 302 `voz/nome_*.wav` + `efeitos/in_the_box.wav` convertidos de 192kHz para 44.1kHz mono (resample, voz não regenerada) — maior diferença de duração medida: 0.01ms (limite pedido: 10ms).
- ✅ **Favicon inline (`f31857a`)**: 404 "fantasma" confirmado ser `/favicon.ico` (pedido automático do Chromium, invisível a `page.on('response')`/`requestfailed` a nível de página — só apareceu com um listener a nível de **contexto**, e mesmo assim sem corresponder a nenhum evento de rede, consistente com ser um pedido interno do browser). Favicon SVG inline (🎵) adicionado às duas páginas — confirmado com Playwright que o erro de consola desaparece.
- 🟡 **Diagnóstico do Encore (não commitado — é só análise)**: tempos reais medidos (acerto→avanço automático sem escolha: ~4.6s); janela fixa de 1.5s (`TESTE_JANELA_DECISAO_TRECHO_B_MS`, `musicbox.html:2832`) + 400ms vermelho; confirmado que `MOMENTO_RESPOSTA_MS` (4s, `cf6fccc`) não colide — só se aplica a faixas sem Trecho A/B real. Proposta de `PAUSA_ANTES_ENCORE_MS≈500ms` (atraso entre o fim do "In the Box!!" e a janela verde abrir) dada ao utilizador, **não aplicada**.

**Pendentes que transitam** (de sessões anteriores, ainda por resolver):
- Aprovação de áudio via YouTube para "Areias do Tempo" (`STD.INT.ALL.MIX.005`) — por confirmar.
- Fototeca: recuperar imagens de playlists entretanto apagadas.
- Rejeições do modo Elo guardadas em sessão (nunca persistidas em `feedback.json`, perdem-se ao fechar o separador).

**Pedidos recebidos 5 Out, ainda não começados** (❌ — zero código escrito):
- Fototeca: candidatas escondidas por defeito + filtro "Sem imagem" + diagnóstico (faixas sem imagem, por categoria aprovada/rascunho/solta) + proposta de preenchimento por artista (sem escrever em `catalogo.json`).
- Pré-escuta de voz no Studio (▶ junto ao nome do artista, toca `voz/nome_<id>.wav`).
- Narração do descritivo ao abrir uma playlist (`gerar_vozes_descritivo.py` + wiring no jogo + regeneração no Studio).
- `PAUSA_ANTES_ENCORE_MS` — proposta dada (~500ms, ver acima), não aplicada.
- Mensagem do utilizador "have an on off button fot track description" recebida sem contexto suficiente (que descrição, onde) — por esclarecer antes de agir.

**⚡ WORKFLOW** — houve duas sessões do Claude Code em paralelo na mesma pasta durante grande parte dos dias 4-5 Out. **Regra**: uma sessão trata de `musicbox.html`/`musicbox_studio.html`/áudio, outra trata de dados (`catalogo.json`/`playlists.json`/`feedback.json`/`mp3_index.json`/ficheiros `.mp3`). Nunca as duas no mesmo ficheiro ao mesmo tempo. **Excepção pontual em 5 Out**: a pedido explícito do utilizador, esta sessão validou (`python3 -m json.tool`) e commitou directamente o trabalho pendente da outra sessão nos 4 ficheiros de dados + `.mp3` novos (`4c6cf1b`) — leu o conteúdo só o suficiente para escrever a mensagem do commit, não editou nada. Confirmado no fim que `playlists.json` ficou sem alterações pendentes.

**⚡ WORKFLOW (regra nova, 5 Out 2026)**: toda decisão de formato (regra de jogo, estrutura de dados, comportamento visível ao público ou à régie) actualiza, no mesmo commit, tanto `DECISIONS.md` (registo técnico, cronológico) como `BIBLIA.md` (o capítulo/secção afectado, marcado "(revisto em &lt;data&gt;)"). Decisões puramente técnicas/de ferramenta (ex. porta do servidor, chave de API) continuam só em `DECISIONS.md`. Ver `BIBLIA.md` §30.9 para a primeira reconciliação formal entre os dois ficheiros.

**Nota**: `hip_01..07_a/b.mp3` e os `.mp3` novos mencionados acima (parte de "Areias do Tempo") já foram commitados em `4c6cf1b` — já não há nada pendente nesses ficheiros.

## 2026-08-29 — Tags secundárias aplicadas a 21 playlists (`universos_secundarios`)
Plano proposto (36 playlists analisadas via `_dados_36_playlists.txt`) e
aprovado pelo utilizador sem alterações — aplicado tal e qual via
`_aplicar_tags_secundarias.py` (scratchpad). Preenche apenas o campo
`universos_secundarios` (eixo interno de metadados, nunca visível no
jogo); nenhum ID/código publicado foi alterado. As 3 Famílias jogáveis
(Décadas/Géneros/Especiais) e os 28 Universos canónicos mantêm-se
inalterados.

21 playlists actualizadas: `LOGO-001` (Guitarra), `STD.INT.00.MIX.001`
(Estados Unidos), `STD.INT.10.SYN.001` (Reino Unido, Alternative/Indie),
`STD.INT.10.SYN.002` (Alternative/Indie), `STD.INT.20.MIX.001` (Estados
Unidos), `STD.INT.50.MIX.001` (Estados Unidos), `STD.INT.60.MIX.001`
(Estados Unidos), `STD.INT.80.MIX.001` (Reino Unido, Synth),
`STD.INT.ALL.BAT.001` (Reino Unido), `STD.INT.ALL.BLU.001` (Estados
Unidos), `STD.INT.ALL.CIN.001` (Instrumental), `STD.INT.ALL.GAM.001`
(Instrumental), `STD.INT.ALL.HIP.001` (Estados Unidos),
`STD.INT.ALL.JAZ.001` (Estados Unidos), `STD.INT.ALL.MET.001` (Estados
Unidos), `STD.INT.ALL.MIX.001` (Ambient, Reino Unido),
`STD.INT.ALL.POP.001` (Estados Unidos), `STD.INT.ALL.SOU.001` (Estados
Unidos, Funk/Disco), `STD.INT.ALL.SYN.001` (França), `STD.INT.ALL.TV.001`
(Estados Unidos), `STD.US.ALL.AME.001` (Country/Folk, Acústico).

Estas tags usam também os códigos reservados nesta ronda (não aplicados
a nenhum dropdown/UI ainda, só reservados para uso futuro): Géneros —
ALT, FUK, REG, COU; Geografia — BR, US, UK, ES, FR, IT, AF, JP, LATAM;
Som/Performance — KEY, RIF, INR, OUT, ACO, LIV, COV, INS; Especiais —
AMB.

**Validado**: `playlists.json` continua JSON válido; `git diff` confirma
que só o campo `universos_secundarios` foi adicionado/alterado em 21
entradas (nenhuma outra chave tocada); `deno check` limpo em
`musicbox_studio.html` e `musicbox.html` (nenhum `.html` foi alterado
neste passo, mas confirmado por precaução).

## 2026-08-29 — Campo `sources` implementado (schema definido pelo utilizador) + confirmação de década
Schema definido pelo utilizador: `sources: {audio, imagem, data_recolha}`
— proveniência básica por faixa. Adicionado a todas as 284 faixas de
`catalogo.json` (`_adicionar_sources.py`, scratchpad):
- `imagem`: inferido de `imagem_fonte` (já existia, 100% das faixas
  preenchido).
- `data_recolha`: inferido de `imagem_data_captura` (fallback `data`).
- `audio`: **deixado `null` em todas as faixas retroactivamente** — não
  existe nenhum campo no catálogo actual que registe iTunes vs YouTube
  por faixa (confirmado: `_construir_playlist.py` calculava isto em
  memória — `e["_fonte_audio"]` — mas `_aplicar_playlist.py` nunca o
  persistia em `catalogo.json`, perdia-se sempre). Sem sinal fiável
  para inferir retroactivamente sem adivinhar, como pedido.

**Corrigido o root cause para faixas futuras**: `_aplicar_playlist.py`
(scratchpad, script usado para todas as playlists criadas nesta sessão)
actualizado para gravar `sources.audio` a partir de `_fonte_audio` a
partir de agora — deixa de se perder essa informação em playlists
novas.

**Confirmação sobre o Mosaico "Anos 2010 — Synth II"**: `decadas` de
`arcade_fire_my_body_is_a_cage` **já estava `["2000s"]`** — não
precisou de correcção, só confirmação (o campo já reflectia a data real
de lançamento, 2007; a divergência é só temática/editorial da playlist,
não um erro de dados).

Validado: JSON válido; `deno check` (exit 0, nenhum `.html` alterado).

## 2026-08-29 — Resolvida a discrepância "4 vs 10" da Fototeca (investigação de histórico git)
Pedido do utilizador: perceber o que aconteceu às outras 6 faixas da
"lista antiga de 10" que a revisão de 28 Ago só encontrou 4.
**Resposta: já tinham sido corrigidas na mesma sessão, antes mesmo de
eu começar a auditar — não é um gap real.**

Reconstruído via `git show <commit>:catalogo.json` em cada commit que
tocou o catálogo: no commit `3e797e8` (26 Ago, 17:38 — "Adiciona
cascata de imagens de artista... aplica 139 imagens melhoradas"), o
catálogo tinha mesmo **exactamente 10** faixas com `imagem_fonte`
iTunes: `a10_01, a10_03, pt80_04, pt80_06, bra001_mosaico, syn001_02,
ptbat_mosaico, beatles_03, beatles_04, disclosure_latch` — esta é, com
alta confiança, a origem real da "lista de 10". Logo no commit
**seguinte**, `1c47fdd` ("Checkpoint: recuperação de imagens apagadas
acidentalmente"), 6 dessas 10 (`a10_01, a10_03, syn001_02, beatles_03,
beatles_04, disclosure_latch`) já aparecem com `imagem_fonte:
"theaudiodb"` — confirmado que continuam assim, com retratos reais,
no catálogo actual. As 4 restantes (`pt80_04, pt80_06, bra001_mosaico,
ptbat_mosaico`) mantiveram-se iTunes até à revisão de 28 Ago (ver
entrada anterior), que as reviu/melhorou.

Conclusão: a contagem "10" estava correcta na altura em que foi feita;
6 delas foram corrigidas numa sessão anterior (mesmo dia, poucos
commits depois); as 4 finais foram as que a auditoria de 28 Ago
encontrou e reviu. Nada por resolver aqui.

## 2026-08-29 — Botão "👁 Revelar" no Mosaico da Mesa de Montagem
Novo botão no cartão do Mosaico (`slotCardHtml`, `kind==='mosaico'` +
tem imagem) — pré-visualiza a imagem já totalmente nítida, reaproveitando
o mini-player flutuante já existente (`previewImagem()`, o mesmo usado
pelo ícone 🖼 na Biblioteca), sem simular a mecânica de revelação
progressiva do jogo, como pedido.

Aplica-se a Standard e Retrato (ambos usam `slotCardHtml('mosaico', ...)`
em `renderSlotsSimples`) — **e também ao "Mosaico / Recap" das playlists
Tributo**, que reaproveita a mesma função de card do Mosaico
(`renderPosicoesTributo` chama `slotCardHtml('mosaico', ...)` no fim,
para o Recap final tipo "Abbey Road (Recap)"). Não removi essa extensão
— é o mesmo mecanismo de pré-visualização a fazer sentido no mesmo
sítio, mas fica documentado aqui porque o pedido original mencionava só
Standard/Retrato. Confirmado que playlists Retrato Sonoro sem Mosaico
(regra 30-Jul) continuam sem o botão, correctamente.

Validado: `deno check` (exit 0); teste real em Chrome
(`_teste_revelar_mosaico.js`, scratchpad) — clique no Mosaico de "Jazz"
abre o mini-player com a imagem certa ("Strange Fruit"); "Vozes
Lendárias" (Retrato Sonoro) confirmado sem Mosaico, sem botão; Tributo
Beatles mostra o botão no Recap, comportamento descrito acima.

## 2026-08-29 — Botão "Ver na app" na Mesa de Montagem
`musicbox.html` ganha suporte a abrir directamente numa playlist
específica via `?playlist=<chave>` (ex.
`musicbox.html?playlist=STD.INT.ALL.JAZ.001`) — não existia antes.
Nova IIFE `af_abrirPlaylistPorURL()` no fim do script: lê o parâmetro,
espera `catalogoPronto`, e reaproveita `testarPlaylist()` (mesmo
mecanismo do botão "◎ Testar uma Playlist" já existente) — chave
inexistente cai de volta ao ecrã inicial normal, sem rebentar.

No Studio, reaproveitado o botão "▶ App" já existente
(`af_abrirApp()`, cabeçalho geral) em vez de criar uma função
duplicada — agora inclui o parâmetro `?playlist=` quando há uma
playlist aberta, e abre sempre numa aba nova (`_blank`, nunca perde o
estado da Mesa de Montagem). Novo botão "▶ Ver na app" adicionado
directamente no cabeçalho de cada playlist na Mesa de Montagem
(`renderMontagem()`) — aplica-se a todos os tipos (Standard, Retrato,
Tributo, Vídeo), chama a mesma `af_abrirApp()`.

Validado: `deno check` (exit 0) em ambos os ficheiros; teste real em
Chrome via puppeteer-core (`_teste_ver_na_app.js`, scratchpad) — URL
directo abre e já está a tocar a playlist certa (`modoTeste:true`,
`faseGeral:"faixa"`); chave inexistente cai no ecrã inicial sem erro;
clique no botão "▶ Ver na app" (playlist Hip Hop aberta no Studio) abre
mesmo uma aba nova com a playlist certa a tocar.

## 2026-08-29 — Tooltips em controlos não óbvios (UX, item de baixa prioridade)
Passagem leve, não exaustiva ("sem pressa" — pedido de baixa
prioridade): a maioria dos botões de preenchimento automático já tinha
`title` detalhado (Auto em toda a playlist, Auto-match MP3, Gerar
trechos em falta) — adicionados os 3 que faltavam mesmo nesse grupo
("Preencher com este artista", "Preencher automaticamente" ×2, uma
ocorrência por cada formato de playlist) + os 3 rótulos de Família na
sidebar (explicam que abrem o Mapa da Biblioteca, não óbvio só pelo
ícone 🗺). Resto da UI deixado como está — cobertura exaustiva não fazia
parte do pedido.

## 2026-08-29 — Exportar créditos de imagem
Nova função `af_exportarCreditosImagem()` (botão "↓ Descarregar
créditos_imagem.md" na tab Exportar) — gera uma tabela Markdown com
id/título/artista/fonte/crédito/licença/URL de origem de cada imagem em
uso no catálogo. Cobre TODAS as fontes (TheAudioDB, Wikimedia/Wikipedia
via `usarImagemWikimedia()`, pesquisa web geral, ficheiros manuais),
não só Wikimedia como o nome da função original sugeria. Só leitura,
nunca altera `catalogo.json`; download directo via `downloadBlob()`
(não é ficheiro de dados da app, não precisa do servidor de escrita).

Validado: `deno check` (exit 0); teste real em Chrome (interceptando
`downloadBlob` para inspecionar o conteúdo sem accionar o download) —
284/284 faixas com imagem exportadas correctamente, tabela com o
número certo de linhas.

## 2026-08-29 — "Anos 2010 — Synth II": discrepância encontrada + 2 bugs reais corrigidos
Pedido do utilizador dizia "faltam 6 faixas + mosaico" em
`STD.INT.10.SYN.002` — **não confirmado**: as 7 músicas e o Mosaico já
estavam todos completos em `playlists.json`/`catalogo.json`, com áudio
e imagem reais (confirmado local + carregamento real no jogo via
`COLLECTIONS['STD.INT.10.SYN.002']`, 7/7 faixas com Trecho A/B). Não
sei a origem da contagem "6 faltam" — nada no repositório a
documentava.

Ao verificar, encontrados e corrigidos **dois bugs reais** que nada
tinham a ver com a contagem de faixas:
1. **Mosaico (`arcade_fire_my_body_is_a_cage`) em formato errado** —
   tinha `trecho_a`/`trecho_b` separados (12s+10s) em vez de um único
   ficheiro contínuo de ~30s (regra 27.7, mesmo bug já visto e corrigido
   nas 6 playlists de 27 Ago) — `elegivel_mosaico` também estava
   `false`, inconsistente com ser mesmo usado como Mosaico. Regenerado
   como `arcade_fire_my_body_is_a_cage_full.mp3` (confirmado ~30s via
   `afinfo`), campos actualizados, ficheiros antigos removidos.
2. **Mosaico com "pessoa" errada** — `pessoa: "Samuel T. Herring"`
   (vocalista dos Future Islands) associado à faixa "My Body Is a
   Cage", que é dos **Arcade Fire**, sem ligação nenhuma a Herring —
   parece cópia do Mosaico de `STD.INT.10.SYN.001` (esse sim, uma
   faixa real dos Future Islands) sem actualizar o nome ao mudar de
   faixa. Corrigido para `"Win Butler"` (vocalista/compositor dos
   Arcade Fire, confirmado por pesquisa antes de aplicar).

Também adicionado `duracao_estimada` (estava ausente, tal como no seu
par `STD.INT.10.SYN.001`, não tocado — fora do âmbito deste pedido).

Nota independente já registada em `TASKS.md`: "My Body Is a Cage" é de
2007, usada numa playlist "Anos 2010" — décadas divergente, não
corrigida (decisão editorial, não um bug técnico).

Validado: JSON válido; `deno check` (exit 0, nenhum ficheiro `.html`
alterado); teste real em Chrome confirma a playlist completa (7/7 +
Mosaico) e o par pessoa/faixa do Mosaico agora coerente.

## 2026-08-29 — Revisão da Fototeca: faixas com imagem via fallback iTunes
Pedido do utilizador referia "10 faixas" — **discrepância encontrada e
reportada**: uma varrimento completo de `catalogo.json` (por
`imagem_fonte` a conter "itunes" E por URL em `mzstatic.com`/
`itunes.apple.com`) só encontra **4** faixas realmente marcadas via
iTunes: `pt80_04`, `pt80_06`, `bra001_mosaico`, `ptbat_mosaico`. Não há
registo de uma lista de 10 em nenhum ficheiro do projecto
(`TASKS.md`/`DECISIONS.md`/`STATUS.md`) — pode ser uma contagem antiga
de outra fonte não documentada aqui. Revistas as 4 encontradas:

- **`pt80_04`** (Trovante) e **`pt80_06`** (Fernando Tordo): imagem
  antiga era capa de álbum iTunes (`imagem_credito` já dizia
  explicitamente "não retrato do artista"), substituída por foto real
  via pesquisa web (`GET /buscar-imagens-cascata`, revista manualmente
  antes de aplicar) — Trovante: foto da banda (Diário de Coimbra, "50
  anos"); Fernando Tordo: retrato (Revista Rua).
- **`bra001_mosaico`** (Elis Regina & Adoniran Barbosa, dueto): mesma
  situação — substituída pelo retrato real de Elis Regina via
  TheAudioDB. Não foi encontrada nenhuma foto conjunta dos dois — fica
  documentado explicitamente no `imagem_credito` que só um dos dois
  artistas está representado.
- **`ptbat_mosaico`** (Alexandre Frazão): **imagem NÃO substituída** —
  já é uma foto real (baterista com t-shirt Zildjian, consistente com o
  seu patrocínio confirmado por pesquisa), só o `imagem_fonte` estava
  errado (dizia `itunes_artist`, mas `imagem_credito` já indicava
  upload manual) — corrigido para `manual`, `imagem_url_origem` posto a
  `null` (fonte original do ficheiro não está registada em lado
  nenhum).

Nenhuma das 4 estava marcada `imagem_licenca_estado: "livre"` — regra
de protecção respeitada, nada bloqueado. Todos os novos URLs
confirmados a carregar (HTTP 200) antes de aplicar.

## 2026-08-28 — Correcção de 2 gaps concretos da auditoria total (decadas vazio + imagem em falta)
Fora da lista de 10 pendências já enviada — pedido isolado sobre 2
achados específicos da Parte 1 (auditoria total):

- **`decadas: []` vazio corrigido (2 faixas)**, ano confirmado por
  pesquisa antes de aplicar:
  - `the_durutti_column_sketch_for_summer` → `["1980s"]` ("Sketch for
    Summer", 1980, álbum de estreia *The Return of the Durutti Column*,
    Factory Records).
  - `future_islands_seasons_waiting_on_you` → `["2010s"]` ("Seasons
    (Waiting on You)", single de 2014, álbum *Singles*) — consistente
    com o uso desta faixa nas playlists "Anos 2010 — Synth".
- **`beatles_05` ("Something (cover)", Tribute Beatles) — imagem
  associada**: sem imagem nenhuma antes; aplicada a mesma foto de banda
  já usada nas outras 5 posições "The Beatles" desta playlist
  (`beatles_01/02/03/04/06`, via `GET /buscar-imagem-artista?artista=The
  Beatles` — TheAudioDB, mesmo URL que as outras já tinham), por
  consistência editorial (o "cover" testa reconhecer a música dos
  Beatles, não o artista da versão cover, que fica genérico "Outro
  artista"). `imagem_licenca_estado: "confirmar"` — não havia imagem
  prévia marcada `"livre"` nesta faixa, nada a proteger.

**Reverificação das 3 imagens afectadas pelo rate-limit da Wikimedia**
(`solo_mosaico`, `bra001_03`, `hip_mosaico`): todas as 3 confirmadas a
carregar normalmente agora (HTTP 200, JPEG real, tamanhos plausíveis
245KB-1.9MB) — confirma que eram mesmo falsos positivos do rate-limit
temporário, sem nenhum problema real. Nada a corrigir.

Validado: `python3 -m json.tool`/JSON válido; `deno check` (exit 0) em
ambos os ficheiros (nenhum JS alterado nesta correcção, só
catalogo.json).

## 2026-08-28 — Parte 3: 4º tipo de Playlist "Vídeo" (Bíblia §29.2)
`STD.INT.ALL.CIN.001` ("Cinema & Música") reclassificada de
`tipo: "standard"` para `tipo: "video"` em `playlists.json` — só o
campo `tipo`, código/chave/id inalterados (não pedido). Correcção
associada em `catalogo.json`: `cinema_mosaico` ("The Godfather Theme",
Nino Rota) não tinha `video`/`clip`/`filme`/`compositor` nenhum (achado
na auditoria da Parte 1) — preenchido com
`https://www.youtube.com/watch?v=e2A27akHfAM` (vídeo oficial do tema,
confirmado por pesquisa), `filme: "The Godfather"`,
`compositor: "Nino Rota"`, igualando o padrão das outras 7 faixas da
playlist. Todas as 8 posições (7 + Mosaico) têm agora `video`.

`musicbox_studio.html`:
- Filtro de Tipo ganha a 4ª opção "Vídeo" (`<option value="video">`).
- `renderSidebar()`: nova secção "Vídeo" (grupo/render loop/
  `LABEL_TIPO`, ao lado de Solo/Retrato/Tributo).
- `expectedCount('video')` → 7 (mesma forma do Standard: 7 músicas +
  Mosaico), para a validação "N/7 posições" continuar a funcionar.
- Badge de tipo na Mesa de Montagem ganha estilo próprio
  (`.tipo-video`, vermelho) em vez de cair no estilo genérico "audio".
- Mapa da Biblioteca: `af_calcularMapaBiblioteca()`/`af_chipTipo()`/
  `af_renderCartaoUniverso()` passam a contar e mostrar chips "Vídeo"
  (dot vermelho, `.mapa-dot.vid`), incluídos também na legenda.
- Player/link de vídeo na Mesa de Montagem: **já existia** — cada
  posição com `t.video` preenchido mostra um botão "▶ YouTube"
  (`trackMetaHtml()`), não gated por tipo — funciona automaticamente
  para todas as 8 posições de Cinema & Música agora que têm o campo.

`musicbox.html`: nenhuma alteração necessária — `UNIVERSOS_EXTERNOS`
(onde Cinema está registada) é agnóstico a `tipo`, e a derivação de
Família/Universo já não dependia deste campo para playlists não-
Retrato. Confirmado que `COLLECTIONS.CINEMA` continua a carregar
normalmente (7 músicas + Mosaico, Família ESPECIAIS/Universo Cinema).

Validado: `deno check` (exit 0) em ambos os ficheiros; teste real em
Chrome via puppeteer-core (`_teste_tipo_video.js`, scratchpad) —
filtro Tipo=Vídeo devolve só `STD.INT.ALL.CIN.001`; secção "Vídeo" na
sidebar; cartão "Cinema" no Mapa mostra `1 playlist` + chip Vídeo;
Mesa de Montagem mostra badge "Video" (vermelho) e 8 botões
"▶ YouTube" (uma por posição); jogo real confirma `COLLECTIONS.CINEMA`
inalterado (7 músicas, Mosaico, Família ESPECIAIS). Screenshot em
scratchpad/tipo_video_montagem.png.

## 2026-08-28 — Parte 2: Escolha única por Ronda + Pontuação plana (Bíblia §10.10/§11.2)
`musicbox.html` — duas alterações às regras do motor:

- **Escolha única por Ronda**: `iniciarEscolhaCollection()` reescrita —
  P1=Blind Draw, P2=Motor (automático), P3=Escolha, P4=Motor, P5=Motor,
  por cada Ronda (`playlistNaRonda` 1-5), substituindo a lógica antiga
  em que o líder do ranking geral escolhia em 4 das 5 Playlists. P3 é
  decidida pelo vencedor de P2 (nova `vencedorMotorEscolha()`): mais
  pontos ganhos nessa Playlist especificamente, não o total acumulado;
  empate desempatado por menor tempo de resposta acumulado
  (`TEMPO_RESPOSTA_MOTOR_ESCOLHA`, alimentado em `acertouFaixa()` a
  partir do `tempoRestante` já existente). Estado armado no início de
  P2 (`PONTOS_ANTES_MOTOR_ESCOLHA` = snapshot de `pontos[]`), lido no
  início de P3.
- **Pontuação plana**: removida a excepção `PONTOS_FAIXA5` (5ª Faixa
  valia 200) — as 7 Faixas Regulares valem sempre `PONTOS_FAIXA` (100).
  `PONTOS_MOSAICO` (200) inalterado. (Ronda 4, sistema de € separado,
  não tocada — fora do âmbito deste pedido.)

Validado: `deno check` (exit 0); teste real em Chrome via
puppeteer-core (`_teste_motor_escolha.js`, scratchpad, usando as
funções reais do jogo — `iniciarEscolhaCollection`/`acertouFaixa`, não
mocks) — ciclo completo de uma Ronda (P1-P5): P1 "BLIND DRAW" auto-
seleccionou `STD.INT.50.MIX.001`; P2 "MOTOR" armou o rasto
correctamente; simulado concorrente 3 a ganhar +200 pts em P2 (2
faixas) contra concorrente 1 a ganhar +100 (1 faixa), apesar de
concorrente 1 ser o líder do ranking GERAL (600 vs 200 pts totais); P3
mostrou correctamente "Concorrente 3 ESCOLHE A FAMÍLIA" — confirma que
é o vencedor de P2, não o líder geral, que escolhe; P4 e P5 ambos
"MOTOR". Faixa 5 e Faixa 3 confirmadas a valer ambas exactamente +100.

## 2026-08-28 — Códigos de género reservados realinhados (JAZ/SOU/HIP/CLA)
Decisão do utilizador (ver DECISIONS.md): em vez de renomear as 4
playlists já publicadas, realinhados os códigos "reservados" no
Studio para corresponderem aos códigos reais já em uso —
`JZZ→JAZ`, `SOL→SOU`, `HHP→HIP`, `CLX→CLA` — nas 5 estruturas que os
usavam: `OPCOES_GENERO` (filtro de Género + modal "Propor Nova Chave"),
`CHAVE_GENERO_PARA_PALAVRAS` (usado por `criteriosDaChave`/
`faixaCorrespondeCriterios` para "Preencher automaticamente"),
`CHAVE_GENERO_PARA_QUERY` (constrói a frase de pesquisa a partir da
chave), `MIGRACAO_CHAVES` (mapping informativo no modal de migração) e
`montarPromptIA()` (lista de códigos válidos passada à IA ao gerar uma
playlist nova — evita que a IA volte a inventar um código diferente
para o mesmo género). `playlists.json` e os ids das 4 playlists reais
mantêm-se intocados, como pedido.

Validado: `deno check` (exit 0); teste real em Chrome via
puppeteer-core (`_teste_codigos_realinhados.js`, scratchpad) — filtrar
Género por JAZ/SOU/HIP/CLA encontra agora directamente
`STD.INT.ALL.JAZ.001`/`SOU`/`HIP`/`CLA` pela etiqueta dominante (antes
só apareciam via `universos_secundarios` explícito).

## 2026-08-28 — Etiquetas secundárias de Universo (Bíblia §27.14b)
Novo campo opcional `universos_secundarios` (array de nomes canónicos de
Universo, ex. `["Rock", "Anos 80"]`) em playlists.json — vazio/ausente
por omissão, sem preenchimento retroactivo das playlists existentes.
Só para uso interno no Studio; a etiqueta dominante (derivada do código
estruturado da playlist, como sempre) continua a ser a única mostrada
no ecrã de escolha do jogo.

- **Filtros do Studio**: `af_playlistPassaFiltros()` (Década/Género)
  passa a considerar também `universos_secundarios` — uma playlist
  aparece se QUALQUER etiqueta (dominante ou secundária) bater com o
  filtro. Novo `DEC_CODIGO_DO_NOME`/`GENERO_CODIGO_DO_NOME` (inverso de
  `DECADA_NOME`/`GENERO_UNIVERSO_*`) converte o nome canónico guardado
  em `universos_secundarios` para o código curto que os filtros usam.
- **Mapa da Biblioteca**: `af_calcularMapaBiblioteca()` agora também
  agrega referências secundárias por Universo; cartões "por criar" com
  pelo menos 1 referência secundária mostram uma nota subtil
  ("↳ N playlist(s) com esta etiqueta secundária"), sem contar para o
  X/N de cobertura, que continua baseado só na etiqueta dominante.
- **Jogo (musicbox.html)**: confirmado — o loader de `COLLECTIONS` só
  copia `nome, descritivo, playlistCodigo, universo, temBonus,
  dificuldade, musicas, mosaico` de cada playlist; `universos_secundarios`
  nunca é copiado, logo estruturalmente não pode chegar ao ecrã de
  escolha mesmo que esteja presente. Nenhuma alteração necessária ali.

**Aviso separado, não relacionado com esta funcionalidade**: ao
implementar a conversão nome→código, descobri que os 4 géneros criados
em 2026-08-28 (Jazz, Soul & R&B, Hip Hop, Clássica) usam nos seus
códigos reais `GENERO=JAZ/SOU/HIP/CLA`, que **não coincidem** com os
códigos reservados nas opções do filtro/modal "Propor Nova Chave"
(`JZZ`/`SOL`/`HHP`/`CLX`, ver `OPCOES_GENERO`). Isto significa que
filtrar a sidebar por Género "JZZ — Jazz" (por exemplo) não encontra
`STD.INT.ALL.JAZ.001` pela etiqueta dominante — só passa a aparecer via
`universos_secundarios` se alguém lhe atribuir explicitamente essa
etiqueta. Pré-existente a esta sessão de trabalho, não corrigido aqui
(decisão estrutural — renomear os códigos das 4 playlists reais
afectaria ids/ficheiros já publicados — fica para confirmação do
utilizador, ver DECISIONS.md).

Validado: `deno check` (exit 0) em ambos os ficheiros; teste real em
Chrome via puppeteer-core (`_teste_universos_secundarios2.js`,
scratchpad, tudo em memória — nada gravado em disco) — filtro Género=ROC
passou a incluir `STD.INT.90.DNC.001` com `universos_secundarios:
["Rock"]`; filtro Década=80 passou a incluir `STD.INT.ALL.HIP.001` com
`universos_secundarios: ["Anos 80"]`; cartão "Slot Local" simulado como
"por criar" com 1 referência secundária mostra correctamente a nota
"↳ 1 playlist com esta etiqueta secundária" sem contar como coberto.

## 2026-08-28 — 10 playlists novas: cobertura total dos 28 Universos (4 Décadas + 6 Géneros)
Confirmado primeiro, via Mapa da Biblioteca + `playlists.json` directo,
que só faltavam 4 Décadas (Anos 50/60/2000/2020 — "Anos 70" já estava
coberta por `STD.INT.70.ROC.001`) e 6 Géneros (Jazz, Blues, Soul & R&B,
Hip Hop, Clássica, Latin) = 10 playlists, não 12.

Criadas as 10 via pipeline real (`/gerar-faixa` + iTunes,
`/buscar-imagem-artista`), mesmo padrão de 27 Ago: 7 faixas + Mosaico
contínuo de 30s por playlist, `duracao_estimada` preenchida, verificação
prévia da regra 27.8b (máx. 3 playlists/artista) contra a Biblioteca
real antes de escolher as faixas. **100% de sucesso em 80/80 faixas**
(áudio + imagem), zero falhas, zero violações da regra 27.8b (Eagles,
Michael Jackson e agora também Taylor Swift ficam exactamente no limite
de 3 — dentro da regra). Commit + push individual por playlist, `0 0`
confirmado 10 vezes:
- `13dfd98` Anos 50 — As Origens do Rock
- `250bb0f` Anos 60 — Revolução Sonora
- `065eb31` Anos 2000 — Viragem do Milénio
- `5c76396` Anos 2020 — A Geração Streaming
- `38ba68d` Jazz — Standards Essenciais
- `fcb96a1` Blues — Raízes do Delta
- `99ae16f` Soul & R&B — A Voz da Alma
- `8bc383e` Hip Hop — Do Bronx ao Mundo
- `4c7bdd5` Clássica — Grandes Compositores
- `e10c10b` Latin — Ritmos do Mundo Latino

**Bug encontrado e corrigido no fim (`0d720c4`)**: `af_universoDePlaylist()`
em `musicbox_studio.html` não conhecia os 6 novos códigos de género
(JAZ/BLU/SOU/HIP/CLA/LAT) — devolvia `universo: null` para essas
playlists, fazendo o Mapa da Biblioteca mostrar Géneros 7/13 em vez de
13/13 (a Família continuava correta, só faltava o mapeamento ao
Universo específico). `GENERO_FAMILIA` em `musicbox.html` já tinha
fallback seguro (sempre GÉNEROS por omissão), mas os códigos foram
adicionados lá também por consistência. Confirmado após a correcção,
via puppeteer-core em Chrome real: **Mapa da Biblioteca mostra 28/28
Universos cobertos** (Décadas 8/8, Géneros 13/13, Especiais 7/7); jogo
real confirma as 10 playlists carregadas via auto-discovery com família
correta. `deno check` (exit 0) em ambos os ficheiros no fim de tudo.

## 2026-08-28 — Correcção estrutural ao bug do auto-save (verificação de versão antes de escrever)
Pedido do utilizador, bloqueante para a criação das 12 playlists em
falta para cobertura total de Décadas/Géneros. Antes: a cada 60s,
`exportPlaylists()` sobrescrevia `playlists.json` incondicionalmente com
o estado em memória da aba, mesmo que o ficheiro em disco tivesse
mudado entretanto (outra aba, edição directa, fusão automática) — causa
de perdas de dados já documentadas nesta sessão (LOGO-001, imagens da
"Never Sleep Again").

Agora: `_servidor_escrita.py` ganha `GET /versao?ficheiro=X` (devolve o
`mtime` actual em disco) e `POST /escrever?...&esperado_mtime=...`
(recusa com 409 se o mtime actual não bater com o esperado — comparação
atómica do lado do servidor, sem janela de corrida entre um GET e um
POST separados). `musicbox_studio.html` guarda o mtime em
`AF_VERSAO_PLAYLISTS` ao carregar (`loadData()`) e a cada escrita bem
sucedida. Numa escrita AUTOMÁTICA em conflito: cancela, mostra um aviso
persistente no topo da página (não desaparece sozinho — só ao recarregar
ou ao guardar manualmente com sucesso) e não sobrescreve nada, nem
sequer os fallbacks (File System API/Blob). Numa escrita MANUAL
("↓ Guardar playlists.json") em conflito: mostra um modal a pedir
confirmação explícita ("Substituir mesmo assim") antes de prosseguir.

Validado: `python3 -m py_compile _servidor_escrita.py` e `deno check`
sobre o `<script>` de `musicbox_studio.html` (exit 0); teste real em
Chrome via puppeteer-core (`_teste_conflito_autosave.js`, scratchpad) —
simulou uma alteração externa real ao ficheiro em disco (mtime + conteúdo
diferentes) e confirmou: (1) escrita automática recusada, aviso
persistente visível, ficheiro no disco continua com a versão externa
(não sobrescrito às cegas); (2) escrita manual abre o modal de
confirmação; (3) "Cancelar" mantém o ficheiro intacto; (4) "Substituir
mesmo assim" escreve com sucesso e sincroniza `AF_VERSAO_PLAYLISTS` com o
novo mtime. `playlists.json` reposto ao estado original no fim do teste
(`git diff` confirma zero alterações residuais).

## 2026-08-28 — Sidebar do Studio colapsável + Mapa da Biblioteca (substitui a reorganização Família→Tipo anterior)
Instrução anterior (agrupar a sidebar por Família→Tipo como estrutura
primária) foi **anulada** pelo utilizador. Reposta a estrutura anterior
(Tipo→Década, ex. "Standard > Anos 70 > Anos 70 — Rock", commit
`7fb6f40~1`) para a lista completa de playlists, agora atrás de um
toggle colapsável (`AF_SIDEBAR_PLAYLISTS_EXPANDIDO`, persistido em
`localStorage['af_sidebar_playlists_expandido']`). Por omissão a
sidebar só mostra os filtros existentes (inalterados) + os 3 rótulos de
Família (DÉCADAS/GÉNEROS/ESPECIAIS) + o toggle "▾ Ver todas as
playlists (N)" — sem a lista completa visível, como pedido. Se houver
filtros/pesquisa activos, a lista aparece automaticamente mesmo
colapsada (para os filtros nunca ficarem "invisíveis").

Novo "Mapa da Biblioteca" (modal `#modal-mapa-biblioteca`, aberto ao
clicar num rótulo de Família): fluxograma raiz "MUSIC BOX — BIBLIOTECA"
→ 3 colunas (Décadas/Géneros/Especiais), cada uma com barra de
progresso e um cartão por Universo canónico (lista fixa dos 28 do Cap.
7.10 — `UNIVERSOS_CANONICOS`), calculado dinamicamente a partir de
`playlists.json` real via `af_universoDePlaylist()` (mesma lógica de
derivação de código estruturado das Partes 1/2 anteriores, agora também
devolvendo o Universo específico, não só a Família). Cartão com
playlist(s): selo dourado/verde com a contagem + chips por Tipo
(Standard/Retrato/Tributo); sem nenhuma: selo tracejado "por criar".
Clicar num cartão coberto chama `af_focarUniverso()` — fecha o modal,
expande a sidebar e restringe a lista às playlists desse Universo
(`AF_UNIVERSO_FOCO`), com os filtros existentes do Studio continuando a
aplicar-se por cima (chip "Universo: X ✕" para limpar o foco; "Limpar
filtros" também o remove). Estética reaproveitada das variáveis CSS já
existentes do Studio (`--bg`/`--bg2`/`--bg3`, `--accent` dourado,
`--mono`), não copiadas do protótipo de referência fornecido pelo
utilizador (usado só para orientação de layout).

Números reais calculados nesta sessão (2026-08-28): Décadas 4/8, Géneros
7/13, Especiais 7/7 — total 18/28 Universos cobertos, 26 playlists.
Validado: `deno check` (exit 0); teste real em Chrome via puppeteer-core
(`_teste_sidebar_colapsavel.js` + `_teste_persistencia.js`, scratchpad)
— confirma o estado colapsado por omissão, a expansão manual mostrando
exactamente "Standard > Anos 70 > Anos 70 — Rock", persistência via
localStorage sobrevivendo a um reload real da página, abertura do Mapa
com os números acima, e o fluxo completo de foco num Universo (cartão
"Rock" → sidebar restringe a `STD.INT.ALL.ROC.001` +
`TRB.UK.ALL.ROC.001`, as 2 playlists reais desse Universo). Screenshot em
scratchpad/mapa_biblioteca.png.

## 2026-08-28 — Parte 3: playlistCodigo em falta corrigido (5 playlists)
Varrimento completo de `playlists.json` encontrou 5 playlists sem o
campo `playlistCodigo` (causa do "(undefined)" no ecrã "Testar uma
Playlist"): `STD.INT.ALL.MIX.001` (Ambient & Introspectivo),
`STD.INT.10.SYN.001`/`STD.INT.10.SYN.002` (Anos 2010 — Synth/Synth II,
os dois casos "Anos 2010 — Synth" reportados), `STD.INT.70.ROC.001`
(Anos 70 — Rock, reportado), e `STD.INT.90.DNC.001` (Never Sleep Again:
A Club Anthem Odyssey, o caso original que motivou a Parte 3). Corrigido
em todas com `playlistCodigo` = a própria chave do objecto — mesma
convenção usada nas outras 21 playlists já correctas. Validado: JSON
continua válido (`python3 -m json.tool`); teste real em Chrome via
puppeteer-core (`_teste_playlistcodigo.js`, scratchpad) — 0 botões com
"undefined" no ecrã "Testar uma Playlist" (antes eram pelo menos os 4
reportados pelo utilizador), e as 4 playlists reportadas mostram agora o
código correcto.

## 2026-08-28 — Parte 2: removida restrição de Ronda para a família ESPECIAIS
`musicbox.html`: removida a regra "Especiais só a partir da Ronda 2"
(bíblia 3.2.1, já revogada pela Bíblia actualizada — 7.10/27.12). O ecrã
de escolha de família (Passo 1 de 2) mostra agora sempre 3 opções —
DÉCADAS/GÉNEROS/ESPECIAIS — desde a Playlist 1 da Ronda 1.
`FAMILIA_COLECAO` (mapa estático, só cobria 14 chaves legadas — as 12
playlists descobertas automaticamente de playlists.json ficavam
invisíveis no selector de família) substituído por `familiaDeChave()` +
`familiaDeUniversoCodigo()`, que derivam a família a partir do código
estruturado da playlist (mesma lógica de `af_familiaDePlaylist()` do
Studio, Parte 1). Validado: `deno check` (exit 0); teste real em Chrome
via puppeteer-core (`_teste_familia_jogo.js`, scratchpad) — Ronda 1,
Playlist 2: os 3 botões de família aparecem todos activos (nenhum
`disabled`); clicar em ESPECIAIS mostra os universos reais (Retrato
Sonoro, Geografia, Logótipos, Televisão, Ativadores Psicológicos, etc.),
sem cair no fallback "pool toda" nem em erro de página. Screenshot em
scratchpad/familia_especiais_ronda1.png.

## 2026-08-28 — Parte 1: sidebar do Studio reorganizada por Família (DÉCADAS/GÉNEROS/ESPECIAIS)
`renderSidebar()` em `musicbox_studio.html` reescrita para agrupar
primeiro por Família (nova função `af_familiaDePlaylist`), depois por
Tipo (Standard/Retrato/Tributo), depois lista as playlists. Ver
DECISIONS.md 2026-08-28 para a lógica completa de classificação.
Validado: `deno check` (exit 0) sobre o `<script>` extraído; teste real
em Chrome via puppeteer-core (`_teste_sidebar_familia.js`, scratchpad) —
confirma as 26 playlists agrupadas correctamente (DÉCADAS: 6, GÉNEROS: 10,
ESPECIAIS: 10) e que o filtro "Tipo = Retrato" continua a funcionar por
cima da nova estrutura (devolve exactamente as 3 playlists Retrato,
espalhadas por 2 famílias diferentes — Vozes Lendárias/Portuguesas e
Logótipos, todas em ESPECIAIS). Screenshot em
scratchpad/sidebar_familia.png.

## 2026-08-27 — "Bateria Portuguesa" reclassificada para o universo "Solistas"
`STD.PT.ALL.BAT.001` tinha `universo: "Geografia"` apesar de ser
conceptualmente uma playlist de Solo de Bateria, tal como a internacional
(`STD.INT.ALL.BAT.001`) — causa raiz de as suas 7 faixas terem `artista` =
banda em vez do baterista. Corrigido `universo` para `"Solistas"` em
`playlists.json` e no literal `COLLECTIONS.PT_BAT` de `musicbox.html`
(sobreposto em runtime pelo `playlists.json`, mas actualizado por
consistência de código-fonte). Não muda a "família" mostrada no ecrã de
escolha de playlist do jogo (continua `FAMILIA_GENEROS`, mapeamento
separado do `universo`).

Das 7 faixas (`ptbat_01`–`07`), 5 tiveram `artista` corrigido para o
baterista real (confirmado por texto sourced da Wikipedia PT, não por
memória): `ptbat_02` Kalú/Xutos & Pontapés, `ptbat_03` Tóli César
Machado/GNR, `ptbat_04` Kinörm/Ornatos Violeta, `ptbat_06` Hélio
Morais/Linda Martini, `ptbat_07` Salvador Seabra/Capitão Fausto — todas
com `banda` preenchido, mesmo padrão de `solo_*`/`bat_*`. Nenhuma tem foto
da pessoa disponível (TheAudioDB/Wikipedia/Wikimedia Commons sem
resultado para nenhum dos 5 nomes) — ficou a foto da banda, com
`imagem_risco_ambiguidade: true`.

`ptbat_01` (UHF) e `ptbat_05` (RAMP) ficaram deliberadamente por
confirmar — identidade do baterista específico não determinável com
confiança a partir da Wikipedia (múltiplos bateristas sem datas claras).
`artista` mantido como a banda, `imagem_risco_ambiguidade: true` +
`nota_curadoria` novo campo a explicar o motivo. Detalhe em `TASKS.md`
("Pendente (sessão 2026-08-27)").

`af_verificarConsistenciaArtistaBanda()` (Studio, aba ASSETS) corrida
antes e depois — 0 faixas sinalizadas depois da reclassificação.

## 2026-08-21 — 5 modos de geração em "Gerar com IA" (URL/Tema/Categoria/Semente múltipla/Playlist YouTube)
Além do modo URL já existente: **Tema/Mood** (texto livre), **Categoria**
(Década+Geo+Género fixos), **Semente múltipla** (até 3 título+artista,
todos entram como faixas fixas), **Playlist YouTube** (novo endpoint
`POST /listar-playlist-youtube` — `yt-dlp --flat-playlist`, nunca
descarrega áudio — lista editável, usada só como contexto/artistas
proibidos, nunca como faixas fixas). Tudo centralizado em
`af_infoModoGeracaoIA()`; `montarPromptIA`/`af_musicasIAComSemente`/
`af_detectarArtistasRepetidos`/retentativas generalizados para todos os
modos sem duplicar lógica. Prompt ganhou também regra explícita: a pessoa
do mosaico não pode ser membro conhecido de nenhuma banda já nas 7 faixas
(ex. Ian Curtis/Joy Division) — só regra de prompt, não validada
algoritmicamente (limitação conhecida, documentada).

26 testes isolados (todos os modos) + endpoint novo testado ao vivo + um
teste real contra a API Anthropic que apanhou uma repetição genuína de
artista gerada pela IA ("Joy Division" 2x), confirmando que a validação é
mesmo necessária. `deno check`/`py_compile` sem erros. **Falta testar no
browser** o fluxo de UI completo — ver `TASKS.md`. Detalhe em
`DECISIONS.md`.

## 2026-08-21 — Feedback ao vivo na Mesa de Montagem durante geração de trechos
Corrigido: depois de "Ver na Mesa de Montagem", não havia nenhum feedback
visual do progresso. Agora mostra contador no topo ("3/7 trechos gerados")
+ estado por faixa (a gerar…/pronto/falhou), ao vivo. Corrigido também um
bug introduzido na funcionalidade anterior: `af_verMontagemAgora()` limpava
a variável que ligava a Mesa de Montagem ao lote em curso — separada em
duas variáveis (`AF_NAVEGACAO_JA_FEITA` vs `AF_CHAVE_PLAYLIST_EM_PROGRESSO`).
`deno check` sem erros. Detalhe em `DECISIONS.md`.

## 2026-08-21 — ~/.zshrc limpo (tinha 6 linhas ANTHROPIC_API_KEY conflituosas)
Fora do repositório, mas registado por relevância: `~/.zshrc` tinha 6
linhas `export ANTHROPIC_API_KEY=...` acumuladas (4 placeholders nunca
preenchidos + 2 chaves reais diferentes). Perguntado ao utilizador antes
de limpar — confirmado usar a chave da sessão actual. Reduzido a uma única
linha; backup em `~/.zshrc.bak-20260821-171759`. Detalhe em `DECISIONS.md`.

## 2026-08-21 — Painel de progresso estruturado + prompt mais restritivo + fallback claro (Gerar com IA)
Texto cinzento simples da tab "✦ Gerar com IA" substituído por um painel
estruturado (`#np-ia-progresso`, `af_renderProgressoIA`): mostra a fase
actual, tentativas de substituição por artista repetido, e estado por
faixa (○ pendente/◐ a gerar/✓ pronto/✗ falhou) com contagem "X/Y trechos
gerados". Para isto aparecer mesmo "no modal" durante a geração dos
trechos A/B (que só corre depois de "Criar playlist"), `createPlaylist()`
deixou de fechar o modal logo nesse caso — fica aberto a mostrar o
progresso, com um botão "→ Ver na Mesa de Montagem" para quem não quiser
esperar. Prompt (`montarPromptIA`) e o corretivo de retentativas ganharam
uma frase explícita a proibir o artista da semente nas 6 faixas. Fallback
após 3 tentativas falhadas por artista repetido deixou de mostrar o prompt
para copiar/colar — mostra directamente "Não foi possível gerar
automaticamente — tenta outra semente." (o outro fallback, por falha de
rede/servidor, continua a mostrar o prompt, sem alteração).

Testado isoladamente (fora do browser) o `af_renderProgressoIA` com 5
estados diferentes, incluindo confirmação de escape correcto de
`<script>`/aspas em título/artista. Validado com `deno check`. **Falta
testar no browser** o fluxo completo — ver `TASKS.md`. Detalhe em
`DECISIONS.md`.

## 2026-08-21 — `ATUALIZAR.command` actualizado (porta 8000 + caminho antigo + ficheiro antigo)
`iniciar_studio.command`/`iniciar_musicbox.command` já estavam ambos em
8002 (não precisaram de correcção). Encontrado um terceiro script,
`ATUALIZAR.command`, ainda com `$HOME/MusicBox/app` (caminho antigo),
`$HOME/Descargas` (pasta que não existe neste Mac) e porta 8000 +
`episodio_piloto2.html` (versão antiga do ficheiro). Corrigido, com
confirmação do utilizador: caminho dinâmico, `$HOME/Downloads`, alvo
actualizado para `musicbox.html`, e passou a reaproveitar
`_servidor_escrita.py` (porta 8002) só arrancando se não estiver a correr
— já não mata/reinicia o servidor a cada execução. Validado com `bash -n`.
Detalhe em `DECISIONS.md`.

## 2026-08-21 — Nenhum artista repetido na playlist gerada por IA (mosaico incluído)
Validação nova: playlist gerada por IA é rejeitada se algum artista se
repetir entre as 7 faixas principais ou com o mosaico (`artista` E
`pessoa` do mosaico contam). Fluxo automático (`af_gerarFaixasIAServidor`)
tenta corrigir sozinho pedindo à IA para substituir, até 3 tentativas
(`af_montarPromptCorretivoArtistaRepetido`); se não resolver, não importa
— pré-preenche "Colar resposta JSON" com a última resposta para corrigir à
mão. Fluxo manual rejeita da mesma forma em `af_aplicarResultadoIA`.
`af_normalizarArtista` reaproveita `afSlug()` já existente. Testado
isoladamente (fora do browser) com casos sintéticos — todos a passar; não
ignora artigos ("The Beatles" ≠ "Beatles", limitação conhecida). Validado
com `deno check`. **Falta testar no browser** o fluxo real com chamada à
API — ver `TASKS.md`. Detalhe em `DECISIONS.md`.

## 2026-08-21 — `iniciar_musicbox.command` recriado para porta 8002
Estava apagado da árvore de trabalho desde antes desta sessão (`git
status` já mostrava `D iniciar_musicbox.command`). Recriado do zero (não
restaurado do `HEAD` antigo, que apontava para `~/MusicBox/app`/porta
8000/Chrome incógnito — desactualizado) para abrir
`http://localhost:8002/musicbox.html` via `_servidor_escrita.py`, mesmo
padrão do `iniciar_editor.command` mas sem `auto_fusao.sh`/
`_servidor_librosa.py` (específicos do Studio). `chmod +x` aplicado.
`iniciar_studio.command` não existe — `iniciar_editor.command` já cumpre
esse papel, já actualizado para 8002 mais abaixo nesta página. Validado
com `bash -n`. Detalhe em `DECISIONS.md`.

## 2026-08-21 — "Identificar + Gerar" chama /gerar-faixas directamente (sem copiar/colar)
O botão "🔍 Identificar + Gerar" (modal Nova Playlist, tab IA) deixou de só
mostrar o prompt para copiar/colar em claude.ai — agora chama `POST
/gerar-faixas` directamente e importa o resultado automaticamente
(`af_gerarFaixasIAServidor` → `af_aplicarResultadoIA`, extraído de
`importarResultadoIA`). Se o servidor falhar, cai para o fluxo manual
antigo (prompt + colar resposta), que continua disponível. Substitui a
decisão de 2026-08-13 de manter esse endpoint por usar. Validado com
`deno check`. **Falta testar no browser** com `ANTHROPIC_API_KEY`
definida — ver `TASKS.md`. Detalhe em `DECISIONS.md`.

## 2026-08-21 — Filtros rápidos + pesquisa na sidebar de Playlists
Adicionados à sidebar "Playlists": pesquisa por nome + filtros Década/
Género/Geo/Dificuldade/Tipo/Estado, todos combinando por E lógico.
Década/Género/Geo vêm da chave estruturada da playlist; Estado é derivado
(`af_playlistEstado` — não existe campo próprio, "pronta" = todas as
posições preenchidas e nenhuma faixa referenciada em 'rascunho' no
catálogo). Botão "Limpar filtros" só aparece com algum filtro activo.
Validado com `deno check`. **Falta testar no browser** — ver `TASKS.md`.
Detalhe em `DECISIONS.md`.

## 2026-08-21 — Geração automática de trechos A/B após "Gerar com IA" com semente do YouTube
Quando "Criar playlist" converte o resultado da tab "✦ Gerar com IA" em
faixas-rascunho e a semente veio de um URL do YouTube (não só texto livre
no campo semente), `createPlaylist()` dispara automaticamente, em segundo
plano, `POST /gerar-faixa` para cada faixa gerada (6 sugestões + semente +
mosaico), sempre por artista+título — sem confirmação por faixa, o
utilizador só valida no final na Mesa de Montagem. Sem semente do YouTube,
continua a exigir o botão manual "⬇ Gerar trechos" por faixa, como antes.

Novas funções em `musicbox_studio.html`: `af_gerarTrechoCore` (núcleo
extraído de `gerarTrechosViaServidor`, que passou a chamá-lo — botão manual
sem alterações de comportamento) e `af_gerarTrechosAutomaticoIA` (corre em
sequência, nunca em paralelo; aborta o lote se o próprio servidor não
responder, mas continua se só uma faixa falhar a gerar). `NP_IA_RESULTADO`
ganhou o campo `sementeYoutubeUrl`. Detalhe completo em `DECISIONS.md`.

Validado com `deno check` sobre o bloco `<script>` — sem erros de sintaxe.
**Falta validação no browser** (sem acesso a browser real neste ambiente):
gerar uma playlist via IA com um URL real do YouTube como semente e
confirmar que os trechos A/B aparecem de facto, sem intervenção manual, na
Mesa de Montagem (ver `TASKS.md`).

## 2026-08-21 — `ORIGEM_PERMITIDA` e `iniciar_editor.command` para 8002
`_servidor_escrita.py`: `ORIGEM_PERMITIDA` mudou de `http://localhost:8000`
para `http://localhost:8002`. `iniciar_editor.command`: já não arranca
`python3 -m http.server 8000` (redundante desde o `do_GET`, ver abaixo); o
`open` final passa a abrir `http://localhost:8002/musicbox_studio.html`.
Não existe `iniciar_studio.command` — o script actual chama-se
`iniciar_editor.command`, confirmado por pesquisa em todo o repositório.

**Atenção — servidor real interrompido durante o teste:** ao validar esta
alteração, `pkill -f "_servidor_escrita.py"` matou sem querer um processo
`_servidor_escrita.py` que já estava a correr (não o de teste, que falhou
a arrancar por a porta já estar ocupada). Se tinhas o Studio aberto a
depender dele, reinicia com `./iniciar_editor.command` ou `python3
_servidor_escrita.py`. Porta 8002 confirmada livre, sem processos
pendurados. Detalhe em `DECISIONS.md`.

## 2026-08-21 — `do_GET` em `_servidor_escrita.py`: ficheiros estáticos na porta 8002
Adicionado `do_GET` a `app/_servidor_escrita.py`, a pedido do utilizador,
para servir os ficheiros estáticos de `app/` (HTML, JSON, imagens, áudio)
directamente na porta 8002 — a app deixa de precisar de `python3 -m
http.server` na porta 8000 em paralelo para ser vista no browser. Protecção
contra path traversal (`os.path.realpath` + verificação de que o caminho
fica dentro de `APP_DIR`, 403 caso contrário), `Content-Type` via
`mimetypes.guess_type`, 404 para ficheiros inexistentes. Endpoints `POST`
existentes (`/escrever`, `/upload`, `/gerar-faixas`, `/gerar-faixa`) não
foram tocados. Detalhe completo em `DECISIONS.md` — incluindo o que ficou
por fazer (referências a `http://localhost:8000` ainda presentes em
`musicbox_studio.html`, não alteradas por não terem sido pedidas).

Validado com `python3 -m py_compile` e testado com `curl` a correr o
servidor real: GET a ficheiros existentes → 200 com Content-Type correcto;
GET a ficheiro inexistente → 404; path traversal (`../`) → 403; `POST
/escrever` confirmado sem regressão.

## 2026-08-13 — `_servidor_escrita.py` (porta 8002)
Novo servidor local (`app/_servidor_escrita.py`, stdlib puro) que passa a
ser a via principal de "Guardar playlists.json" no Studio — escreve
directamente em `app/` sem pedir autorização de pasta no browser (a File
System Access API pedia-a a cada refresh; detalhe completo em
`DECISIONS.md`). `iniciar_studio.command` arranca-o em background na porta
8002. Validado com `curl` (whitelist de ficheiros, JSON inválido, escrita
real com verificação de `md5`, CORS) e `deno check`/`py_compile` — sem
acesso a browser real neste ambiente, por isso falta confirmação visual no
Studio (ver `TASKS.md`).

## Estado geral do projecto
Aplicação web para gestão de catálogo musical, episódios, blocos de áudio, chaves e integração com a API do MusicBrainz (ver `CLAUDE.md`).

## Tarefa em curso
Nenhuma de momento — ver `TASKS.md` para "Próximas tarefas".

## Alterações realizadas nesta sessão
Em `app/musicbox_studio.html`, na mesa de montagem (Montagem):
- Novo botão "⏱ Definir início" nas posições com faixa atribuída (slots simples e posições de tributo), junto ao nome/artista da faixa.
- Ao clicar, abre um mini-painel inline. **Só tem o campo Início (s)** — `trecho_a.fim` é calculado automaticamente como `início + 15s` (`TIMING_DURACAO_FIXA`), sem campo próprio nem validação de duração mínima (a versão anterior tinha campo Fim + validação de 15s mínimos; ambos foram removidos a pedido do utilizador por já não fazerem sentido com a duração fixa).
- Ao guardar, actualiza `trecho_a.inicio`/`trecho_a.fim` do CATALOGO em memória e a posição faz refresh, mostrando a etiqueta **"A: 20s"** (só o início, sem o fim).
- Novas funções: `timingLabelHtml`, `toggleTimingEditor`, `timingEditorHtml`, `saveTimingEditor`, `exportCatalogoPatch`. Novo estado: `timingEditorSlot`, `CATALOGO_PATCH`.
- `exportPlaylists()` passa a descarregar também `catalogo_patch.json` (array com as entradas de faixa modificadas nesta sessão) sempre que houver alterações pendentes ao catálogo, além do `playlists.json` habitual.
- CSS: `.timing-row`, `.timing-btn`, `.timing-editor` (+ `input[type=number]`), `.meta-tag.timing`. CSS de validação (`.timing-error`, `input.invalid`) foi removido junto com a validação.

Também actualizados `TASKS.md` (tarefa concluída) e `DECISIONS.md` (registo da exceção arquitetural: esta funcionalidade altera CATALOGO em memória, o que contraria o ponto 1 do cabeçalho do ficheiro — decisão documentada, não escreve `catalogo.json` em disco).

Criado `app/REGRAS_OPERADORES.md` — compilação de regras editoriais e técnicas para operadores do Studio, uso interno (destino confirmado com o utilizador: equipa, não licenciados). Reúne regras já existentes em `CODIGOS.md`, `DECISIONS.md`, `validar_catalogo.py`, `SESSAO_2026_08_10.md` e no cabeçalho de `musicbox_studio.html` — não inventa regras novas.

**Divergência resolvida** (registada em `DECISIONS.md`, 2026-08-10): confirmado pelo utilizador que todas as playlists têm exactamente 8 posições, independentemente do tipo — no "tributo" a flexibilidade é o tipo de conteúdo de cada posição, não a quantidade. O validador estava correcto; corrigido o cabeçalho de arquitetura em `musicbox_studio.html` (ponto 2) e `app/REGRAS_OPERADORES.md` §1.4 para reflectir isto.

Dois novos botões na mesa de montagem, abaixo da posição 01 quando esta tem faixa atribuída:
- **"Preencher com este artista"** (só `retrato`): pesquisa no CATALOGO faixas com o mesmo artista (interseção do array `artista`), ordena por menor década, preenche `musicas[1..7]`. Nunca toca na posição 01. Notifica "X faixas encontradas para [artista]". Novas funções: `menorDecada`, `preencherComArtista`. CSS: `.fill-artista-btn`.
- **"Preencher automaticamente"** (`standard`/`retrato`/`tributo`): deriva critérios de geografia/década/género a partir da **chave** da playlist (não existem esses campos directamente em `playlists.json` — decisão confirmada com o utilizador) e ordena por `nivel` (mais fácil primeiro). Em `tributo` só mexe em posições `tipo:"audio"`; em `standard` só preenche `musicas` (não o mosaico). O mapeamento GENERO→subgéneros do catálogo é uma aproximação por substring, não uma tabela oficial — sinalizado como heurística em `DECISIONS.md` e `REGRAS_OPERADORES.md`. Novas funções: `criteriosDaChave`, `faixaCorrespondeCriterios`, `preencherAutomaticamente`; novas tabelas `CHAVE_GEO_PARA_GEOGRAFIA`, `CHAVE_DEC_PARA_DECADA`, `CHAVE_GENERO_PARA_PALAVRAS`. CSS: `.fill-auto-btn`.

`DECISIONS.md` e `app/REGRAS_OPERADORES.md` (§1.4, §2.4) actualizados com ambas as funcionalidades.

**Novos ficheiros:** `app/auto_fusao.sh`, `app/_fundir_catalogo.py`, `app/iniciar_studio.command` (este último não existia — criado porque era o pedido: `auto_fusao.sh` "iniciado pelo iniciar_studio.command"). `iniciar_studio.command` arranca o servidor local, inicia `auto_fusao.sh` em background (destacado do Terminal via `nohup`+`disown`) e abre o browser.

`auto_fusao.sh` monitoriza `~/Downloads/catalogo_adicionar.json` (loop de 2s) e funde-o automaticamente em `catalogo.json`, apaga o ficheiro de Downloads e imprime `"Fundido: X faixas"` — **única fusão automática (sem revisão manual) de todo o projecto**, pedida explicitamente pelo utilizador; todo o resto continua "download + fusão manual obrigatória". Por ser a única excepção e por apagar o ficheiro de origem, foram acrescentadas protecções não pedidas mas necessárias: nunca sobrescreve `id` já existente, só apaga o ficheiro após fusão bem sucedida (JSON inválido fica em Downloads para inspecção), faz backup timestamped de `catalogo.json` em `app/backups_catalogo/` antes de cada escrita, espera o ficheiro estabilizar antes de o ler, regista tudo em `app/auto_fusao.log`, e usa lockfile para não correr duas instâncias em simultâneo. Detalhe completo em `DECISIONS.md`.

## Validado
- `deno check` sobre o bloco `<script>` extraído de `musicbox_studio.html` — sem erros de sintaxe (exit 0), repetido após cada alteração desta sessão.
- `auto_fusao.sh`/`iniciar_studio.command` validados com `bash -n`; `_fundir_catalogo.py` com `python3 -m py_compile` — sem erros.
- `_fundir_catalogo.py` e o loop completo de `auto_fusao.sh` testados de ponta a ponta em ambiente isolado (pasta `Downloads`/`catalogo.json` falsas, não os ficheiros reais): faixa nova é fundida e o ficheiro de origem é removido; `id` duplicado é ignorado com aviso; entrada sem `id` é ignorada; JSON inválido não é apagado nem funde nada. Confirmado que não ficou nenhum processo de teste pendurado.
- Não foi possível testar no browser nesta sessão (sem acesso a servidor HTTP local) — recomenda-se testar manualmente: `python3 -m http.server` na pasta `app/`, e validar em concreto: (1) o painel "Definir início" só com campo Início; (2) "Preencher com este artista" numa playlist Retrato; (3) "Preencher automaticamente" numa playlist standard, numa retrato e numa tributo (incluindo o caso de posições tributo não-audio ficarem intocadas); (4) qualidade real das correspondências de género (heurística por substring pode ter falsos positivos); (5) `iniciar_studio.command` a correr de facto por duplo-clique no Finder (só foi corrido via `bash -n`, nunca invocado como duplo-clique real).

## Problemas encontrados
- Falta validação manual no browser de todas as funcionalidades desta sessão (ver acima).
- `iniciar_studio.command` nunca foi corrido como duplo-clique real no Finder — só validado sintaticamente. Recomenda-se um primeiro arranque supervisionado antes de confiar nele sem vigilância.

## Concluído (histórico, ver TASKS.md)
- [x] Estrutura inicial do Studio
- [x] Catálogo musical
- [x] Sistema de Chaves [TIPO].[GEO].[DEC].[GENERO].[VOL] (2026-08-10)
- [x] Botão "Definir início" para trecho_a.inicio na mesa de montagem (2026-08-10)
- [x] Compilação de regras editoriais e técnicas para operadores — `app/REGRAS_OPERADORES.md`, uso interno (2026-08-10)
- [x] Resolvida divergência standard/retrato/tributo: todas as playlists têm exactamente 8 posições (2026-08-10)
- [x] Botão "Preencher com este artista" (Retrato) na mesa de montagem (2026-08-10)
- [x] Botão "Preencher automaticamente" (qualquer tipo) na mesa de montagem (2026-08-10)
- [x] `auto_fusao.sh` + `iniciar_studio.command` — fusão automática de catalogo_adicionar.json (2026-08-10)

## 2026-08-28 — Mapa da Biblioteca: navegação termina sempre na Mesa de Montagem
Pedido explícito do utilizador: qualquer caminho de cliques a partir do
Mapa da Biblioteca deve terminar na Mesa de Montagem de uma playlist
específica, nunca preso num ecrã intermédio.

`af_focarUniverso()` agora bifurca por contagem: Universo com
exactamente 1 playlist → `af_abrirNaMontagem()` (nova função:
`switchTabProgrammatic('montagem')` + `selectPlaylistFilter()`) salta
directo para lá, sem passar pela lista filtrada. Universo com 2+
mantém a lista filtrada na sidebar como antes, mas os itens dessa lista
(`af_renderItemPlaylist`, só quando `AF_UNIVERSO_FOCO` está activo)
passam a usar `af_abrirNaMontagem()` em vez de `selectPlaylistFilter()`
simples — antes só abria a Mesa de Montagem se essa view já estivesse
activa, o que falhava a partir da Biblioteca (o ponto de entrada normal
do Mapa). Fora do foco de Universo, o clique normal na sidebar mantém
o comportamento antigo (só filtra a tabela da Biblioteca), inalterado.

Validado: `deno check` (exit 0); teste real em Chrome via
puppeteer-core (`_teste_mapa_navegacao.js`, scratchpad) — Caso 1
("Ativadores Psicológicos", 1 playlist): clique no cartão leva direito
à Mesa de Montagem com `STD.INT.ALL.NAT.001` aberta, modal fechado, sem
ecrã intermédio. Caso 2 ("Retrato Sonoro", 3 playlists): clique no
cartão mostra a lista filtrada (3 playlists, chip "Universo: Retrato
Sonoro"), continua na Biblioteca; clicar numa dessas 3 (2ª da lista)
abre a Mesa de Montagem com essa playlist específica
(`RET.PT.90.VOZ.001`). Screenshot em
scratchpad/mapa_navegacao_caso2.png.
