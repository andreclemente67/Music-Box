# Propostas de fonte_audio — 3 packs seguintes (modo PROPOSTA, nada gravado)

Depois dos 4 packs de demo (`STD.INT.80/00/50/60.MIX.001`, ver `scripts/propostas_fonte_4packs.json`), escolhidos os **3 packs com mais faixas em falta** entre os restantes: `STD.INT.ALL.CIN.001` (Cinema & Música), `STD.INT.ALL.BAT.001` (Solo de Bateria), `STD.PT.ALL.FAD.001` (Cancioneiro Português) — 7 faixas cada, empatados no topo (excluindo `RET.INT.ALL.VOZ.001` e `LOGO-001`, formatos diferentes de "canção com trecho_a/trecho_b" — ver nota no fim do script).

Motor: `scripts/propor_fontes_proximos3.py` (mesma lógica de `propor_fontes_4packs.py`, generalizada a 3 packs à escolha). 1ª tentativa de pesquisa só (sem `--cookies-from-browser`, a pedido), ritmo 8s entre faixas, `--skip-download` em todas as chamadas — **nenhum áudio descarregado, nenhuma escrita em catalogo.json/playlists.json**. Ficheiros: `scripts/propostas_fonte_std_int_all_cin_001.json`, `scripts/propostas_fonte_std_int_all_bat_001.json`, `scripts/propostas_fonte_std_pt_all_fad_001.json`.

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

## Nota sobre fiabilidade

A classificação "topic"/"official_audio" confirma só o **canal**, não que o **título devolvido** corresponda à música pedida nem que o **artista** esteja certo — `madredeus_povo_que_lavas_no_rio` é o caso mais claro: título bate perfeitamente, mas a fonte proposta é do canal de Amália Rodrigues, não de Madredeus. 11 das 21 propostas têm algum sinal de alerta (duração muito acima do single, título devolvido diferente do pedido, ou tipo de vídeo errado — aula/concerto/colectânea em vez do single de estúdio) — nenhuma destas deve ser aprovada sem ouvir primeiro. `cinema_02` (Star Wars) falhou por timeout nas duas tentativas (1ª + 1 retry, 16 Out) — não por ausência de resultados; continua sem proposta.
