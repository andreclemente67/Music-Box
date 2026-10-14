#!/usr/bin/env python3
"""Acrescenta a DECISIONS.md e STATUS.md os limiares de revisão manual
do B2 fechados em 14 Out 2026. Só documentação, não toca em dados.

Correr com:  python3 tmp/registar_limiares.py
"""
import os

APP = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DECISAO = """
## 2026-10-14 — B2 vai para revisão manual: fim > 80% da duração ou confluência < 0,15

Limiares fechados pelo André, a fechar a ressalva que a decisão de 11 Out
deixara em aberto ("limiar a definir com diagnóstico"). Uma faixa **não**
recebe Trecho B gerado automaticamente, vai para revisão manual, se:

1. **o trecho escolhido acabar depois de 80% da duração da música** —
   zona de saída: o último refrão pode já estar em fade, com outro por
   cima ou com o arranjo a desmontar-se, e nada disso serve para
   reconhecimento. A regra de ≥30s de música depois trava o caso
   extremo, não este;
2. **a confluência de intensidade da janela vencedora for inferior a
   0,15** — nenhuma janela da faixa é intensa nos dois eixos ao mesmo
   tempo, venceu "a menos má", e isso é uma escolha sem fundamento;
3. **a localização do Trecho A ou B por correlação for ambígua**, nas
   faixas sem tempos no catálogo (ver a entrada do teste de margem,
   mesma data).

Diagnóstico que fundamentou os valores (os dois packs com `fonte_audio`,
7 faixas analisáveis de 14 — critério actual, repetição ≥70% +
confluência pelo mínimo):

| faixa | duração | B actual | B2 | B2 em % | confluência | marcas |
|---|---|---|---|---|---|---|
| `80_02` Sweet Child O' Mine | 356s | 111–126s | 131–146s | 37–41% | 0,356 | |
| `80_04` Don't You Want Me | 241s | 92–107s | 188–203s | 78–84% | 0,074 | **fim 84% + confluência 0,074** |
| `80_05` The Final Countdown | 309s | 114–129s | 120–135s | 39–44% | 0,328 | |
| `80_06` Every Breath You Take | 228s | 50–65s | 149–164s | 65–72% | 0,346 | localização do B actual ambígua |
| `80_07` Billie Jean | 294s | 84–99s | 213–228s | 72–77% | 0,391 | localização do B actual ambígua |
| `dec00_01` Hey Ya! | 236s | 142–157s | 144–159s | 61–68% | 0,927 | |
| `dec00_06` In the End | 216s | 68–83s | 69–84s | 32–39% | 0,303 | catálogo desactualizado (12s vs mp3 de 15s) |

**Só o `80_04` é apanhado pelos dois primeiros limiares** — e é
precisamente a faixa onde o B2 já se sabia arbitrário. O `80_07` fica à
beira (acaba a 77%), o que é o argumento para o limiar ser no fim do
trecho e não no início: a 75% de início nenhuma destas faixas entrava,
apesar de duas acabarem acima dos 72%.

**Consequência para os desvios registados**: o teste de margem (mesma
data) classifica como ambíguas as localizações do B actual de `80_04`,
`80_06` e `80_07`, e o `80_06` já vinha com aviso de pico fraco (2,6x no
B, 2,9x no A) na corrida de 11 Out. Os desvios dessas três faixas
(+96s, +99s, +129s) ficam portanto **sem base confirmada** até os tempos
serem determinados de outra forma — ouvindo, ou gravando-os no catálogo.
Os desvios de `80_02` (+20s), `80_05` (+6s), `dec00_01` (+2s, do
catálogo) e `dec00_06` (+1s) mantêm-se.

Os limiares ficam **registados, não implementados**: nenhuma geração
automática está autorizada, e a aplicação aos packs continua a depender
de diagnóstico e aprovação. `catalogo.json` e `playlists.json`
intocados.
"""

NOTA_STATUS = """  - **Limiares de revisão manual fechados (14 Out 2026)**: o B2 **não** é gerado e a faixa vai para revisão manual se **acabar depois de 80% da duração** da música (zona de saída), se a **confluência for inferior a 0,15**, ou se a **localização do A/B por correlação for ambígua**. Nos dois packs diagnosticados só o `80_04` é apanhado pelos dois primeiros (acaba a 84%, confluência 0,074); o `80_07` fica à beira, a acabar a 77% — foi por isso que o limiar ficou no fim do trecho e não no início. **Registado, não implementado**: nenhuma geração está autorizada. Ver DECISIONS.md e BIBLIA.md §13.2.
  - **Três dos cinco desvios dos Anos 80 ficam sem base confirmada**: o teste de margem (14 Out) classifica como ambíguas as localizações do B actual de `80_04`, `80_06` e `80_07` — e o `80_06` já trazia aviso de pico fraco (2,6x) na corrida de 11 Out, que não foi trazido para a tabela na altura. Os desvios +96s, +99s e +129s dependem dessas localizações. Mantêm-se confirmados `80_02` +20s, `80_05` +6s, `dec00_01` +2s (do catálogo) e `dec00_06` +1s.
"""


def acrescentar_decisao():
    p = os.path.join(APP, 'DECISIONS.md')
    texto = open(p, encoding='utf-8').read()
    if '2026-10-14 — B2 vai para revisão manual' in texto:
        print('DECISIONS.md: entrada já existe, nada feito')
        return
    open(p, 'a', encoding='utf-8').write(DECISAO)
    print('DECISIONS.md: entrada acrescentada')


def acrescentar_status():
    p = os.path.join(APP, 'STATUS.md')
    texto = open(p, encoding='utf-8').read()
    if 'Limiares de revisão manual fechados' in texto:
        print('STATUS.md: nota já existe, nada feito')
        return
    marca = '  - **PENDENTE — aplicação aos packs**'
    assert texto.count(marca) == 1, f'marca encontrada {texto.count(marca)} vezes'
    open(p, 'w', encoding='utf-8').write(texto.replace(marca, NOTA_STATUS + marca))
    print('STATUS.md: nota acrescentada antes do pendente da aplicação')


if __name__ == '__main__':
    acrescentar_decisao()
    acrescentar_status()
