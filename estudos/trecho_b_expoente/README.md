# Estudo — Trecho B = "expoente" da música

Playlist `STD.INT.00.MIX.001` (Anos 2000), 11 Out 2026. **Nada de produção foi tocado** — tudo aqui é isolado, nunca escreve em `<id>_a/b.mp3` nem em `catalogo.json`.

## Como ver

Com o `_servidor_escrita.py` a correr (porta 8002):
`http://localhost:8002/estudos/trecho_b_expoente/pagina.html`

Ouve os B1–B4 de cada faixa às cegas e escolhe o melhor. Os nomes dos métodos só devem ser olhados (`dados/chave_<id>.json`) depois de teres escolhido.

## Os 4 métodos (`analisar.py`)

- **`itunes_alinhamento`** — o preview de 30s da iTunes Search API (escolhido editorialmente pela Apple como o excerto mais reconhecível) alinhado na faixa completa por fingerprint (chromaprint/fpcalc, distância de Hamming). Geralmente o mais fiável (confiança 0.90–0.99 nas 7 faixas).
- **`chroma_repeticao`** — chromagrama simples (STFT + 12 classes de altura, sem `librosa` — incompatível com Python 3.14 nesta máquina, ver `scripts/verificar_trechos.py`) + auto-semelhança: procura o par de instantes mais parecidos a ≥20s de distância, fica com o de maior energia (RMS). **Limitação conhecida**: deu similaridade ≈1.00 nas 7 faixas — ou estas faixas têm mesmo secções muito repetitivas, ou (mais provável) 12 dimensões normalizadas saturam facilmente; os offsets parecem plausíveis (nunca em silêncio nem no segundo 0), mas o método discrimina menos do que seria desejável. Resultado a tratar com mais reserva que os outros 3.
- **`lrclib_refrao`** — letra sincronizada da API pública [LRCLIB](https://lrclib.net) (sem chave, sem login); linha de texto mais repetida = refrão provável, usa a 2ª ocorrência. Falhou em 1/7 (`dec00_04`, "Seven Nation Army" — instrumental/sem refrão lírico claro na letra disponível).
- **`controlo_volume`** — o método já em produção (`sugerir_trechos.py`): pico de volume depois de A+20s. É o "controlo" do estudo, não um candidato novo.

## Offset de vídeo (`dados/video_offsets.json`)

Nenhuma das 7 faixas tem campo `video` no catálogo — a condição literal do pedido ("faixas com video vivo") dá zero faixas aplicáveis. Para ainda assim demonstrar a funcionalidade "Encore" (vídeo mudo sincronizado), fui buscar o videoclipe oficial de 2 faixas à parte (não estão no catálogo, só aqui): `dec00_01` (Hey Ya!) e `dec00_03` (Mr. Brightside). Offset calculado por fingerprint (mesma técnica do alinhamento iTunes, janela deslizante de 20s ao longo do vídeo para evitar secções de abertura sem música — `Hey Ya!` tem 68s de intro cinematográfica antes da música começar, confiança 0.94; `Mr. Brightside` só 3s de logotipo, confiança 0.98).

## Ritmo e cache

`analisar.py` nunca usa `--cookies-from-browser` (sem login, pedido explícito) — se o YouTube bloquear um pedido, a faixa fica por retomar numa próxima corrida (progresso em `dados/progresso.json`), nunca força sessão. Pausa de 4s entre descargas. Fontes completas em cache (`cache/`) — nunca descarrega duas vezes a mesma.
