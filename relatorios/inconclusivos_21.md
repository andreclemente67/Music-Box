# 21 "inconclusivo" (relatorios/reavaliacao_falhas.csv) — razão provável + acção sugerida

Levantamento só de leitura — nada alterado, nenhuma reavaliação corrida.

## Grupo 1 — timeout da pesquisa (3 faixas)
`80_01` (STD.INT.80.MIX.001), `solo_02`, `solo_03` (STD.INT.ALL.GTR.001): "pesquisa no YouTube excedeu 45s".

**Razão provável**: lentidão pontual de rede/YouTube no momento da corrida, não um problema da faixa em si (`80_01` já tem fonte confirmada noutro contexto — ver `relatorios/proposta_b2_80.md`). **Acção sugerida**: repetir só estas 3, sem mudar nada — é provável que resolvam só por reexecução.

## Grupo 2 — candidatos encontrados, mas todos rejeitados pelo filtro de título (1 faixa)
`ptbat_05` (STD.PT.ALL.BAT.001): "nenhum candidato passou o filtro de título".

**Razão provável**: os 5 resultados do `ytsearch5` tinham todos palavras proibidas no título (Remix/Live/Acoustic/Video/etc.). **Acção sugerida**: rever manualmente os 5 candidatos (não gravados neste CSV, só o resultado "sem_filtro" teria o 1º) — decidir se algum serve apesar do título, ou procurar à mão por "Official Audio"/Topic.

## Grupo 3 — zero resultados na pesquisa (15 faixas)
`boris_vian_le_deserteur`, `quilapayun_el_pueblo_unido_jamas_se`, `fausto_a_luta_e_alegria` (STD.PT.70.WLD.001); `jose_afonso_primavera` (STD.PT.ALL.FAD.001); `amalia_rodrigues_estranha_forma_de_vida_2`, `jose_afonso_senhor_meu_jesus_cristo` (STD.PT.ALL.WLD.001); `darude_sand_storm`, `oasis_wonderwall_3`, `hans_zimmer_dune_main_theme` (sem playlist); `oasis_wonderwall_4`, `ennio_morricone_son_of_a_desert_wind`, `darude_sand_storm_2` (STD.INT.ALL.MIX.005); `peabo_bryson_regina_bell_a_whole_new_world`, `toni_basil_mickey` (STD.INT.ALL.POP.002); `randy_newman_you_ve_got_a_friend_in_m` (sem playlist).

**Razão provável**: a consulta usada é literalmente `"{artista} {titulo}"` do catálogo — vários destes ids sugerem o problema está na consulta, não na música: nomes com apóstrofo/acentos (`you've got a friend in m...` — título cortado, parece truncado no próprio id), dois artistas concatenados (`peabo_bryson_regina_bell_a_whole_new_world` — "Peabo Bryson Regina Bell A Whole New World" não é como o vídeo se chama, falta o "&"), ou duplicados com sufixo numérico (`oasis_wonderwall_3/4`, `darude_sand_storm/_2`) cuja faixa gémea pode já ter fonte — a consulta devia ser igual à da gémea. `hans_zimmer_dune_main_theme`/`darude_sand_storm`/`toni_basil_mickey` são títulos comuns e muito pesquisados — zero resultados é estranho, mais provável falha pontual da pesquisa do que ausência real no YouTube.

**Acção sugerida**: não é um problema do motor de classificação — é a consulta. Rever a consulta por faixa (corrigir truncamentos, juntar nomes de artista com "&"/"e", confirmar título exacto) e tentar de novo manualmente; para os duplicados numerados, verificar primeiro se a faixa "base" (sem sufixo) já tem `fonte_audio` e, se sim, considerar reutilizá-la em vez de pesquisar de novo.

## Grupo 4 — candidato encontrado, download bloqueado (2 faixas)
`marconi_union_weightless` (STD.INT.ALL.MIX.001): 1 candidato, `fpcalc` excedeu 120s a analisar. `nat_06` (STD.INT.ALL.NAT.001): 3 candidatos, todos com "HTTP Error 403: Forbidden" a descarregar.

**Razão provável**: `nat_06` com 403 em todos os candidatos sugere bloqueio específico desses vídeos (geo-restrição, direitos de autor, ou precisam de login) — não é falta de rede geral, já que outras faixas da mesma corrida passaram. `marconi_union_weightless` com timeout no `fpcalc` (não no download) pode ser um ficheiro corrompido/incompleto ou just lentidão pontual. **Acção sugerida**: `nat_06` — procurar fontes alternativas (os 3 candidatos testados podem não ser os únicos no YouTube); `marconi_union_weightless` — tentar reanalisar isoladamente antes de assumir bloqueio.
