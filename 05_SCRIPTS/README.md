# 05_SCRIPTS — ferramentas do projeto Hybrid Panda v2

Ambiente: `.venv` (Python 3.13, kiutils 1.4.8, pypdf, pymupdf). Executar sempre com `$env:PYTHONIOENCODING='utf-8'` e a partir de OUTPUT_ROOT.
Todos os scripts importam `hp_common.py`, que **recusa gravar** em `02_REFERENCE`, no ORIGINAL ou fora de OUTPUT_ROOT.

| Script | Função | Entrada | Saída |
|---|---|---|---|
| `hp_common.py` | caminhos (OUTPUT_ROOT, ORIGINAL, 02_REFERENCE), guarda de escrita, sha256, logging | — | — |
| `Make-Manifest.ps1 -Step STEPn [-Original]` | manifesto sha256 de OUTPUT_ROOT e (opcional) do ORIGINAL + verificação de 02_REFERENCE inalterado; regenera `INDEX.md` | árvore | `00_MANIFESTS\OUTPUT_ROOT_<STEP>_<ts>.sha256`, `original_AFTER_<STEP>_*.sha256` |
| `extract_ds_pins.py` | extrai tabela de pinos LQFP144 do DS13311 (texto) | `02_REFERENCE\datasheets\DS13313_text.txt` | `03_RESEARCH\P3_pinos_LQFP144.json` |
| `coverage_matrix.py` | prova cada requisito do HRS com `arquivo:linha` existente nos clones | `03_RESEARCH\HRS_red_panda.md`, `P10_*.md` | `03_RESEARCH\coverage_matrix.md/.csv`, `06_REPORTS\coverage_matrix.json` |
| `firmware_pins.json` | perfis de pinos exigidos pelo firmware: `red_h7` (panda 408e14d4) e `black_f4` (panda_legacy_f4 f849893b), com papel/grupo/fonte | — | — |
| `parity_check.py --netlist X.xml --profile red_h7|black_f4 [--mcu REF] [--h7-lib-pins]` | verificador de paridade estrutural MCU×firmware: todo pino exigido existe, está conectado, pares CAN RX/TX chegam ao mesmo transceiver e o STB chega ao mesmo componente; pinos de alimentação por `NOME#pad` | netlist kicadxml (`kicad-cli sch export netlist --format kicadxml`) | `06_REPORTS\parity_<perfil>_<netlist>.md/.json`; exit 0 OK, 1 divergências, 2 MCU não encontrado |

Controle do método: `parity_check.py --profile black_f4` sobre `06_REPORTS\baseline_BlackPanda_netlist.xml` → 35/35 OK (projeto que o firmware black aceita). O perfil `red_h7` só deve ser 0 sobre a netlist do `04_PROJECT` (STEP 4/7).

Avisos conhecidos: `coverage_matrix.py` imprime um "fatal: not a git repository" inofensivo ao tentar obter o commit da pasta de datasheets.

## STEP 4
- `sch_geom.py` — transformação de pinos (lib → folha) + selftest: `python 05_SCRIPTS\sch_geom.py <sch>`; no baseline 382 ancorados / 10 soltos (todos já soltos no original).
- `step4_bom_values.json` — valores/footprints consumidos pelo gerador (cristal, caps de carga, indutor, SWD, botão). Campos `status: PROVISORIO` exigem confirmação em datasheet.
- `step4_build_schematic.py` — gera o esquemático H725 a partir de `HybridPanda.kicad_sch.baseline` (criado na 1.ª execução a partir do primeiro backup). Apaga regiões F413/divisor 5 V/GPS, renomeia CAN→BUS, folha A1, MCU + blocos de suporte, PWR_FLAGs, `sym-lib-table`, `.kicad_pro` (pin_map VCAP). Aborta se houver fio solto ou colisão de nomes de net no mesmo ponto. Relatório: `06_REPORTS\step4_build_schematic.json`.
- `step4_verify.ps1` — build + netlist + ERC (`hybrid_ERC.json`) + selftest + `parity_check.py --profile red_h7`. Esperado: `ERC errors = 0`, `parity exit = 0`, `SEM DIVERGÊNCIA — OK=36`.
- `parity_check.py` — `PORT_RX` agora aceita nomes de pino `PB4(NJTRST)` (símbolo H7).

## STEP 5 (python do KiCad: `C:\Users\costabr\AppData\Local\Programs\KiCad\10.0\bin\python.exe`; filtrar stderr `swig|image handler|assert`)
Pipeline completo (idempotente): `step5_update_pcb.py` → `step5b_route.py --passes 60` (≈ 12 min, Java 25 + Freerouting 2.5.0) → `step5c_fix_unrouted.py --rounds 6` → `step5d_silk.py` (esconde a serigrafia das referências dos 37 componentes novos e reexecuta o DRC → `06_REPORTS\hybrid_DRC_step5_final.json`, `step5d_silk.json`; D-31).
- `step5_update_pcb.py` (5a) — reconstrói `HybridPanda.kicad_pcb` a partir de `.baseline`: remove F413/GPS, coloca U7 LQFP-144 em B.Cu (109,5; 56,6 rot 90), caps/VCAP/cristal/SMPS/SWD/BOOT0, amplia a placa +5 mm ao sul (fase E, D-24), renomeia nets, limpa fragmentos (respeitando o preenchimento das zonas, D-25). Relatório: `06_REPORTS\step5_update_pcb.json`. Apaga o snapshot `.step5a` antigo e grava um novo.
- `step5b_route.py [--passes N] [--no-freerouting] [--no-pre] [--pre-rounds N] [--inner-power]` (5b) — restaura `.step5a`; zona +3V3 In1 sob o MCU (clearance 0,254); trilhas críticas por script (VCAP, cristal, SMPS, desacoplamento) e vias GND/+3V3 do U7 (vias +3V3 só dentro do contorno da zona In1); **fase M** = desvio da trilha +5V In1 para x = 117,6 + via-in-pad GND do U1.2 (D-29); **fase R** = pré-rotas travadas B.Cu→via→F.Cu para os pares U7↔transceiver com posição de via livre (`PREROUTE` auto-descoberto; na prática BUS2_TX U7.122↔U9.1 e BUS2_RX U7.123↔U9.4; D-30); **fase P** = `step5c --pre` (só redes de potência, itens travados) antes do DSN; trava o baseline; exporta DSN sem zonas não-GND, com regras `via_*` = 0,16 (sem `wire_pin`, D-29) e `kicad_default use_via 500:300`; Freerouting headless; importa SES; destrava baseline; alarga trilhas do FR < 0,1375 (neck-down); limpeza final de fragmentos; refill. Relatório: `06_REPORTS\step5b_route.json`, log `step5b_freerouting.log`.
- `step5c_fix_unrouted.py [--rounds N] [--dry] [--pre]` (5c) — corretor orientado pelo DRC (`kicad-cli pcb drc --format json`): fecha `unconnected_items`, furos (`hole_to_hole`/`hole_clearance`) de vias destravadas, trilha FR × furo PTH (afunilamento) e `shorting_items`/`clearance` com item destravado do FR (remove via/trilha + stubs e religa na rodada seguinte); estratégias em D-26 (stitch, via-in-pad, trilha→pour, ilhas, A* local, rip-up), D-29 (`fix_clusters`: ponte entre agrupamentos de conectividade de GND/+3V3 isolados pelo roteamento In1/In2) e D-30 (ponte por trilha directa a item do agrupamento principal sem via nova; remoção de micro-segmentos < 0,02 mm). Relatório: `06_REPORTS\step5c_fix.json` (`step5c_pre.json` no modo `--pre`). Importável (usado pelo 5b via `PRELOADED_BOARD`/`AS_LIBRARY` + `main()`).
- Nunca editar o `.kicad_pcb` à mão entre 5a e 5c: o pipeline regenera tudo a partir de `.baseline`/`.step5a`.
- Resultado esperado (Freerouting é não-determinista: 3–9 não roteados após 5b): após 5c, **unconnected_items = 0**. DRC final: `06_REPORTS\hybrid_DRC_step5_final.json`; comparação com o baseline em `03_RESEARCH\STEP5_layout_H725.md`.

## STEP 6
- `step6_reports.py` — medições sobre a placa final (sem alterar nada): pares diferenciais CAN (BUS0/1N/1O/2 _H/_L) e USB (USB_D±, USB_R_D±) — comprimentos, skew, vias, larguras, gap; estimativa de Z0 microstrip (Hammerstad–Jensen, εr 4,5, prepreg 0,2 mm) e Zdiff; polígonos/áreas/agrupamentos dos planos GND/+3V3; totais de trilhas/vias. Escreve `06_REPORTS\step6_reports.json` e `03_RESEARCH\STEP6_roteamento_impedancia.md`.

## STEP 7
- `step7_validate.py` (python do KiCad) — corre e regista: `kicad-cli sch erc` → `06_REPORTS\hybrid_ERC_step7.json`; `kicad-cli pcb drc` → `hybrid_DRC_step7.json` (comparado por assinatura tipo+itens com `baseline_DRC.json`); netlist esquemático (kicadxml) × PCB (pcbnew: pad→rede, footprint, valor); BOM (`hybrid_BOM.csv` regenerada) × esquemático × PCB; `parity_check.py --profile red_h7` (python da `.venv`); `Make-Manifest.ps1 -Step STEP7 -Original`. Logs `step7_*.log`, resumo `step7_validation.json`, relatório `03_RESEARCH\STEP7_validacao.md`. Exit 0 sempre — as falhas ficam em `failures`.

## STEP 8
- `step8_fabricate.py` (python do KiCad) — gera `07_FABRICATION`: `gerbers\` (RS-274X, Protel ext., sem X2), `drill\` (Excellon PTH/NPTH separados + mapa PDF/Gerber X2), `assembly\` (`BOM_JLC.csv`, `CPL_JLC.csv` com origem = aux origin, `pos_kicad_both.csv`), `pdf\` (esquemático, cobre por camada, fab/assembly), `3d\HybridPanda.step`, `drill_table.md/.json` (PTH/NPTH/vias, anel anular mínimo), `gerber_check.json` (verificação sintática + contagem de furos Excellon × PCB — **não** substitui visualizador), `HybridPanda_gerbers_JLC.zip`, `LEIA-ME.txt` ("NÃO FABRICAR" + motivos lidos de `step7_validation.json`). Resumo `06_REPORTS\step8_fabrication.json`.

## STEP 9
- Sem script. Documentos: `03_RESEARCH\STEP9_bringup_e_teste_veiculo.md`, `08_DOCS\RELATORIO_FINAL.md`, `INDEX.md` (gerado pelo `Make-Manifest.ps1`).
