# Propostas de fonte_audio — 3 packs seguintes (modo PROPOSTA, nada gravado)

Depois dos 4 packs de demo (`STD.INT.80/00/50/60.MIX.001`, ver `scripts/propostas_fonte_4packs.json`), escolhidos os **3 packs com mais faixas em falta** entre os restantes: `STD.INT.ALL.CIN.001` (Cinema & Música), `STD.INT.ALL.BAT.001` (Solo de Bateria), `STD.PT.ALL.FAD.001` (Cancioneiro Português) — 7 faixas cada, empatados no topo (excluindo `RET.INT.ALL.VOZ.001` e `LOGO-001`, formatos diferentes de "canção com trecho_a/trecho_b" — ver nota no fim do script).

Motor: `scripts/propor_fontes_proximos3.py` (mesma lógica de `propor_fontes_4packs.py`, generalizada a 3 packs à escolha). 1ª tentativa de pesquisa só (sem `--cookies-from-browser`, a pedido), ritmo 8s entre faixas, `--skip-download` em todas as chamadas — **nenhum áudio descarregado, nenhuma escrita em catalogo.json/playlists.json**. Ficheiros: `scripts/propostas_fonte_std_int_all_cin_001.json`, `scripts/propostas_fonte_std_int_all_bat_001.json`, `scripts/propostas_fonte_std_pt_all_fad_001.json`.

**2º lote (18 Out 2026)**: `scripts/propor_fontes_pacote3.py` — os 3 packs seguintes com mais faixas em falta, excluindo os já feitos e os formatos "não-canção" (Retrato, Logótipos, **e Tributo**, pela mesma razão — posições mistas/especiais, não `trecho_a`/`trecho_b` uniforme): `STD.INT.ALL.SYN.001` (Synthwave, 7/7), `STD.PT.ALL.WLD.001` (Vozes da Terra, 7/7), `STD.INT.10.MIX.001` (Anos 2010, 6/7 — desempate alfabético do código entre 7 packs empatados a 6/7, sem outro critério disponível). Mesmas regras (sem cookies, só metadados, ritmo lento) + nova coluna **canal vs. artista** (ver nota no fim).

## Cinema & Música (`STD.INT.ALL.CIN.001`)

| Faixa | Título | Canal | Duração | Topic/Official? | ⚠ |
|---|---|---|---|---|---|
| cinema_01 | Blade Runner (Love Theme) | IONI | 296s | fallback | |
| cinema_02 | Star Wars | — | — | **falhou nas 2 tentativas (16 Out: timeout de novo, +1 retry único)** | ⚠ sem proposta — tentar mais tarde ou aumentar timeout |
| cinema_03 | The Pink Panther | Henry Mancini | 3610s (1h) | topic | ⚠ é uma colectânea, não o single |
| cinema_04 | Goldfinger | John Barry — Topic | 264s | topic | ok |
| cinema_05 | Inception (Time) | WaterTower Music | 276s | official_audio | ok |
| cinema_06 | The Mission | EuroArtsChannel | 539s | fallback | ⚠ é uma actuação/concerto, não o single |
| cinema_07 | Lawrence of Arabia | Maurice Jarre — Topic | 579s | topic | ⚠ é um medley de 3 temas, não só "Lawrence of Arabia" |

## Solo de Bateria (`STD.INT.ALL.BAT.001`)

| Faixa | Título | Canal | Duração | Topic/Official? | ⚠ |
|---|---|---|---|---|---|
| bat_01 | In the Air Tonight | Rewind Music | 337s | fallback | ⚠ canal de covers, não o original |
| bat_02 | We Will Rock You | East39 | 203s | fallback | ⚠ é uma actuação ao vivo de 2026, não a faixa de estúdio |
| bat_03 | Hot For Teacher | Drumeo | 1557s (26min) | fallback | ⚠ é um vídeo de análise/aula, não a música |
| bat_04 | Moby Dick | Jimmy Keys | 913s (15min) | fallback | ⚠ provavelmente o lado do álbum completo, não só o solo |
| bat_05 | The End | The Beatles | 142s | topic | ok |
| bat_06 | Walking on the Moon | Drumeo | 1049s (17min) | fallback | ⚠ é um vídeo de análise/aula, não a música |
| bat_07 | Sympathy for the Devil | ABKCO Records & Films | 112s | fallback | ⚠ 112s é curto para esta música (~6min) — pode ser um excerto |

## Cancioneiro Português (`STD.PT.ALL.FAD.001`)

| Faixa | Título | Canal | Duração | Topic/Official? | ⚠ |
|---|---|---|---|---|---|
| fausto_topic_lembra_me_um_sonho_lindo | Lembra-Me Um Sonho Lindo | Fausto — Topic | 386s | topic | ok |
| amalia_rodrigues_estranha_forma_de_vida | Estranha Forma de Vida | Amália Rodrigues — Official | 201s | topic | ok |
| sergio_godinho_gaivota | Gaivota | Sérgio Godinho TV | 265s | topic | ⚠ título devolvido é "A Noite Passada", não "Gaivota" — confirmar por audição |
| jose_afonso_primavera | Primavera | José Afonso — Topic | 288s | topic | título devolvido "Coro da Primavera" — provavelmente o mesmo tema, confirmar |
| madredeus_povo_que_lavas_no_rio | Povo Que Lavas no Rio | **Amália Rodrigues — Official** | 272s | topic | ⚠⚠ título bate, mas o canal é de Amália, não de Madredeus — artista errado |
| rui_veloso_electrico_28 | Eléctrico 28 | Rui Veloso — Topic | 231s | topic | ⚠ título devolvido "Um trolha d'Areosa" — música errada, confirmar antes de usar |
| dulce_pontes_cancao_do_mar | Canção do Mar | Dulce Pontes Oficial | 321s | fallback | ok (videoclipe oficial, não "Official Audio") |

## Synthwave (`STD.INT.ALL.SYN.001`)

Motor: `scripts/propor_fontes_pacote3.py` — acrescenta a verificação automática **canal vs. artista** (heurística de texto normalizado — nome do artista é substring do canal, ou vice-versa, ignorando "Topic"/"Official"/"Oficial"/"VEVO"/"Music"/"Records"; `None` = canal em falta).

| Faixa | Título | Canal | Canal bate artista? | Topic/Official? | Duração ≤320s? | ⚠ |
|---|---|---|---|---|---|---|
| syn001_01 | Midnight City (M83) | MusicIsLife | ❌ não | fallback | sim (242s) | ⚠ canal genérico, não o artista |
| syn001_02 | A Real Hero (Electric Youth & College) | clarencito | ❌ não | fallback | sim (268s) | ⚠ canal de upload de fã |
| syn001_03 | Turbo Killer (Carpenter Brut) | Carpenter Brut | ✅ sim | fallback | sim (209s) | ok, só não é Topic/Official |
| syn001_04 | Sunset (The Midnight) | The Midnight | ✅ sim | official_audio | sim (327s) | duração 327s ligeiramente acima do limiar (320s) |
| syn001_05 | Resonance (Home) | Home — Topic | ✅ sim | topic | sim (213s) | ok |
| syn001_06 | She Is Young... (Perturbator) | BlooodMusic | ❌ não | fallback | sim (305s) | ⚠ canal de terceiros |
| syn001_07 | Overdrive (Lazerhawk) | Lazerhawk — Topic | ✅ sim | topic | sim (271s) | ok |

## Vozes da Terra (`STD.PT.ALL.WLD.001`)

| Faixa | Título | Canal | Canal bate artista? | Topic/Official? | Duração ≤320s? | ⚠ |
|---|---|---|---|---|---|---|
| zeca_afonso_cancao_de_embalar | Canção de Embalar | José Afonso — Topic | ❌ **falso positivo** | topic | sim (242s) | heurística não reconhece "Zeca" = apelido de "José Afonso" — canal está certo |
| adriano_correia_de_olive_trova_do_vento_que_passa_2 | Trova do Vento que Passa | Adriano Correia de Oliveira — Topic | ✅ sim | topic | sim (200s) | ok |
| amalia_rodrigues_estranha_forma_de_vida_2 | Estranha Forma de Vida | Amália Rodrigues — Official | ✅ sim | topic | sim (201s) | ok |
| sergio_godinho_rosa_rezada | Rosa Rezada | — | — | — | — | **sem resultados na pesquisa** |
| jose_afonso_senhor_meu_jesus_cristo | Senhor Meu Jesus Cristo | Fe Hoje | ❌ não | fallback | sim (100s) | ⚠⚠ título devolvido é uma oração diferente, canal religioso genérico — música errada |
| peret_al_alba | Al Alba | Felice Santelli — Topic | ❌ não | topic | sim (185s) | ⚠⚠ título devolvido "Serenata al Alba del Dia" (erudito/clássico) — música e artista errados |
| francisco_fanhais_menino_do_bairro_negro | Menino do Bairro Negro | Sociedade Portuguesa de Autores | ❌ não | fallback | sim (267s) | ⚠ canal de direitos de autor, não o artista — confirmar |

## Anos 2010 (`STD.INT.10.MIX.001`)

6 faixas (a10_04 já tem `fonte_audio` doutra sessão, não entra aqui).

| Faixa | Título | Canal | Canal bate artista? | Topic/Official? | Duração ≤320s? | ⚠ |
|---|---|---|---|---|---|---|
| a10_01 | Work (Rihanna ft. Drake) | Rihanna | ✅ sim | fallback | **não (454s)** | ⚠ já conhecido (ver STATUS.md) — vídeo bem mais longo que o single |
| a10_02 | Shape of You (Ed Sheeran) | Latin City | ❌ não | fallback | sim (234s) | ⚠ canal de terceiros, título "(Lyrics)" |
| a10_03 | Uptown Funk (Mark Ronson ft. Bruno Mars) | Mark Ronson | ✅ sim | official_audio | sim (271s) | ok |
| a10_05 | Rolling in the Deep (Adele) | MUSICRAFT | ❌ não | fallback | sim (231s) | ⚠ canal de terceiros, título "(Lyrics)" |
| a10_06 | Old Town Road (Lil Nas X ft. Billy Ray Cyrus) | Golden Network | ❌ não | fallback | sim (154s) | ⚠ canal de terceiros, título "(Lyrics)" |
| a10_07 | Bad Guy (Billie Eilish) | Billie Eilish | ✅ sim | fallback | sim (206s) | canal certo, só não é Topic/Official — confirmar |

## Nota sobre fiabilidade

A classificação "topic"/"official_audio" confirma só o **canal**, não que o **título devolvido** corresponda à música pedida nem que o **artista** esteja certo — `madredeus_povo_que_lavas_no_rio` é o caso mais claro: título bate perfeitamente, mas a fonte proposta é do canal de Amália Rodrigues, não de Madredeus. 11 das 21 propostas do 1º lote têm algum sinal de alerta; nenhuma destas deve ser aprovada sem ouvir primeiro. `cinema_02` (Star Wars) falhou por timeout nas duas tentativas (1ª + 1 retry, 16 Out) — não por ausência de resultados; continua sem proposta.

**2º lote (Synthwave/Vozes da Terra/Anos 2010)** acrescenta a verificação automática canal-vs-artista pedida — apanhou `madredeus_povo_que_lavas_no_rio` correctamente (não repetido aqui, já estava no 1º lote) mas também tem **1 falso positivo confirmado**: `zeca_afonso_cancao_de_embalar` marca "não bate" porque a heurística de texto não sabe que "Zeca Afonso" é o apelido de "José Afonso" — o canal real está certo. A verificação é só um sinal de texto, nunca substitui ouvir a faixa.
