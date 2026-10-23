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
