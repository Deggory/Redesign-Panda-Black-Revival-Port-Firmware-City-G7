# RELATÓRIO FINAL — Hybrid Panda (Black Panda × STM32H725ZGT6 / firmware red panda)

Data: 2026-10-26 · Protocolo v3 (`08_DOCS\PROTOCOLO_v3_COMPLETO.md`), STEP 1–9 · Raiz: `C:\Users\costabr\Downloads\openpilot\HybridPanda_v2_20261022_1616` · Repositório: github.com/kriptomad/PandaH7Openpilot

## 1. Resumo e estado real

Objetivo: adaptar o projeto KiCad aberto **OpenBlackPanda** (lukasloetkolben, STM32F413, MIT) para correr o **firmware oficial do red panda** (commaai/panda, `stm32h7`, HW_TYPE RED) **sem modificação**, num **STM32H725ZGT6 LQFP-144**, mantendo formato, conectores e harness do Black Panda, para uso com openpilot num Honda City 2023 BR.

Estado em uma frase: **projeto eletrónico completo em análise estática (esquemático, PCB roteada, DRC/ERC, netlist, paridade de pinos com o firmware, pacote de fabricação gerado), com zero validação física.** Não é "pronto para fabricar", não é "validado", não é "funcional". A compatibilidade com o firmware do red panda está demonstrada **só por análise estática (paridade 36/36 pinos), sem compilação local e sem teste em hardware**.

| STEP | Estado | Prova principal |
|---|---|---|
| 1 Ambiente/base | FEITO | `00_MANIFESTS\original_BEFORE.sha256` (377 ficheiros), baseline ERC/DRC em `06_REPORTS` |
| 2 Ingestão / HRS | FEITO | `03_RESEARCH\HRS_red_panda.md`, `coverage_matrix.md` (61/61 requisitos provados), `02_REFERENCE` (clones só leitura, hashes em `reference_clones.sha256`) |
| 3 Eng. reversa / tabela híbrida | FEITO | `03_RESEARCH\STEP3_engenharia_reversa_tabela_hibrida.md`, `05_SCRIPTS\parity_check.py` + `firmware_pins.json` |
| 4 Esquemático | FEITO | `04_PROJECT\HybridPanda\HybridPanda.kicad_sch`, `STEP4_esquematico_H725.md`, ERC 0 erros |
| 5 PCB | FEITO | `HybridPanda.kicad_pcb` (= `.step5_final`), `STEP5_layout_H725.md`, DRC 0 não ligados / 0 clearance / 0 curtos |
| 6 Roteamento / impedância | FEITO (analítico) | `STEP6_roteamento_impedancia.md` |
| 7 Validação | FEITO — **nenhuma falha** | `STEP7_validacao.md`, `06_REPORTS\step7_validation.json` |
| 8 Fabricação | FEITO — **NÃO FABRICAR** | `07_FABRICATION\` + `LEIA-ME.txt` |
| 9 Bring-up / relatório | FEITO (documental) | `STEP9_bringup_e_teste_veiculo.md`, este ficheiro |

## 2. Resultado das premissas P1–P11

| P | Enunciado | Resultado | Fonte |
|---|---|---|---|
| P1 | Honda City 2023 BR usa CAN-FD | **REFUTADA** — `HONDA_CITY_7G = HondaBoschPlatformConfig(..., BOSCH_RADARLESS)`, CAN clássico, harness Bosch B. Decisão do utilizador: prosseguir com H7 na mesma (D-05) | `P1_veiculo_Honda_City_2023.md`; opendbc `car/honda/values.py` |
| P2 | commaai publica o hardware do red panda | **REFUTADA** — só firmware; esquemático/PCB do red panda não publicados | `P2_hardware_red_panda.md` |
| P3–P6 | Mapa de pinos do firmware red (GPIO, ADC, CAN, USB, clock) | CONFIRMADAS e extraídas com file:line | `P3_P4_P5_P6_firmware_pinmap.md`, `P3_tabela_pinos_LQFP144_vs_firmware.md`, HRS §2–§5, §8 |
| P7 | Pacote TFBGA100 serviria | **REFUTADA** — sem PF/PG; `clock.h` exige SMPS para LQFP144 | HRS §2; `kicad_lib_STM32H723VGHx_pins.txt`; D-02 |
| P8 | HW_TYPE por straps | CONFIRMADA — RED = PF7–PF10 a 0 (pull-up interno) | HRS §1; D-08 |
| P9 | Flash 1 MB necessária | CONFIRMADA → H725**ZG** | HRS §6 |
| P10 | Pinout OBD-C / SBU / harness | CONFIRMADA; PC4 = TT_ha, SBU condicionado (D-12, D-16) | `P10_OBDC_harness_SBU.md` |
| P11 | Transceivers do baseline servem para CAN FD | CONFIRMADA — TJA1042TK/3, 5 Mbit/s (D-20) | `R3v2_componentes_STEP4.md` |

## 3. HRS e matriz de cobertura
- `03_RESEARCH\HRS_red_panda.md` — requisitos de hardware extraídos do firmware (`board/boards/red.h`, `stm32h7/*`, `board/main.c`, …) com file:line, §1–§10 (inclui controlo F4 do Black Panda).
- `03_RESEARCH\coverage_matrix.md/.csv`, `06_REPORTS\coverage_matrix.json` — **61/61 requisitos provados, 0 não encontrados**.
- Controlo do método: perfil `black_f4` do `parity_check.py` sobre a netlist do Black Panda original = 35/35 OK (prova de que o verificador reconhece um projeto sabidamente funcional).

## 4. Tabela híbrida
`03_RESEARCH\STEP3_engenharia_reversa_tabela_hibrida.md` §(f): periférico × pino F413 (baseline) × pino exigido no H725 × rede × componente. Sem **PIN_PARITY_CONFLICT**. Paridade final (STEP 7, netlist do esquemático atual): **36/36 OK** (`06_REPORTS\parity_red_h7_hybrid_HybridPanda_netlist.md`).

## 5. BOM
- Esquemático: 114 referências, 48 linhas agrupadas (`06_REPORTS\hybrid_BOM.csv`; JLC: `07_FABRICATION\assembly\BOM_JLC.csv` + `CPL_JLC.csv`, 76 top / 38 bottom).
- Consistência BOM × esquemático × PCB: **0 divergências** (STEP 7).
- **114 referências sem MPN e sem código LCSC** — PROVISÓRIO. Itens com valor definido mas fabricante por confirmar: cristal 25 MHz (CL/15 pF), L5 DFE201610E 2,2 µH, FB1, condensadores VCAP/SMPS (ESR), ver `R3v2_componentes_STEP4.md` e `STEP4_esquematico_H725.md` §9.

## 6. Esquemático por bloco (`STEP4_esquematico_H725.md`)
MCU U7 LQFP-144 (Direct SMPS: L5 + C41/C42; VCAP ×3 interligados, D-19; VDDLDO; VDD33USB = 3V3, D-14) · cristal 25 MHz · straps HW_TYPE (D-08) · 4 transceivers TJA1042 (BUS0/BUS1N/BUS1O/BUS2, STB com pull-up, D-09/D-17; errata normal/OBD D-15) · USB-C P1 (pinagem do baseline, D-13) · OBD-C/harness com SBU → 10 kΩ + BAT54S → PC4/PA1 (D-12/D-16) · alimentação 12 V→5 V→3V3 do baseline · SWD J1 2×5 1,27 mm · LEDs/ventoinha/sensores do baseline. GPS NEO-M8M removido (D-03). Sem terminação 120 Ω (D-04).

## 7. Pinos e conectores
- Mapa dos 144 pads (77 ligados, 67 NC): `STEP4_esquematico_H725.md` §4; `P3_pinos_LQFP144.json`.
- Conectores: P1 USB-C (TYPE-C-31-M-04), OBD-C/harness (A2/A3 CAN0, A10/A11 CAN1, B2/B3 CAN2, B10/B11 CAN3, A8/B8 SBU, VIN/GND), J1 SWD — `STEP4` §5, `P10_OBDC_harness_SBU.md`.

## 8. Regras, stackup, furação, mecânica
- Regras (do baseline, mantidas): trilha/espaço mín 0,1375/0,1 mm; via 0,4/0,3 (vias do baseline 0,45/0,25 permanecem — 1 `drill_out_of_range` herdado); anel mín 0,05; furo mín 0,3.
- Stackup (gravado no ficheiro, **não confirmado com fabricante**): 4 camadas, F.Cu 35 µm / 0,2 mm / In1 17,5 µm / 1,065 mm / In2 17,5 µm / 0,2 mm / B.Cu 35 µm, εr 4,5 — total ≈ 1,59 mm. In2 = GND; In1 = +3V3 só sob o MCU.
- Furação: 232 furos (PTH 26, NPTH 2, vias 204); brocas 0,25–2,5 mm; 6 slots (P1); Excellon = PCB (232 = 232) — `07_FABRICATION\drill_table.md`.
- Mecânica: placa ampliada **+5 mm ao sul** (Edge.Cuts y_max 73,76 → 78,76 mm, D-24) → **as caixas STL do baseline não servem**; U7 em B.Cu (D-21) — altura do lado B aumenta (LQFP 1,6 mm + L5 1,0 mm).
- Impedância (STEP 6): CAN Zdiff ≈ 122–139 Ω estimados onde há referência In1; USB ≈ estimativa; **só analítico**.

## 9. Comandos executados e códigos de saída
Todos registados nos JSON de `06_REPORTS` (campo `commands`/`events` com `cmd`, `exit`, `seconds`) e em `05_SCRIPTS\README.md`:

| Fase | Comando | Exit | Log |
|---|---|---|---|
| 5a | `python.exe 05_SCRIPTS\step5_update_pcb.py` | 0 | `step5_update_pcb.json` |
| 5b | `python.exe 05_SCRIPTS\step5b_route.py --passes 60` (Freerouting 2.5.0, Java 25) | 0 | `step5b_route.json`, `step5b_freerouting.log` |
| 5c | `python.exe 05_SCRIPTS\step5c_fix_unrouted.py --rounds 6` | 0 | `step5c_fix.json` |
| 5d | `python.exe 05_SCRIPTS\step5d_silk.py` | 0 (DRC 0) | `step5d_silk.json`, `hybrid_DRC_step5_final.json` |
| 6 | `python.exe 05_SCRIPTS\step6_reports.py` | 0 | `step6_reports.json` |
| 7 | `python.exe 05_SCRIPTS\step7_validate.py` → `kicad-cli sch erc` 0, `pcb drc` 0, `sch export netlist` 0, `sch export bom` 0, `parity_check.py` 0, `Make-Manifest.ps1 -Step STEP7 -Original` 0 | 0 | `step7_validation.json`, `step7_*.log` |
| 8 | `python.exe 05_SCRIPTS\step8_fabricate.py` → gerbers 0, drill ×2 0, pdf ×9 0, **step 2** (ficheiro gerado; modelos VRML ignorados), bom 0, pos 0 | 0 | `step8_fabrication.json` |

`python.exe` = `C:\Users\costabr\AppData\Local\Programs\KiCad\10.0\bin\python.exe` (KiCad 10.0.7). Nenhum comando gravou fora da raiz (`hp_common.assert_inside_output`); `ORIGINAL vs BEFORE: IDENTICAL (377 files)` no manifesto STEP7.

## 10. Riscos (ordem de gravidade)
1. **PIN_PARITY_CONFLICT: nenhum.**
2. **Zero validação física** — nenhum protótipo; o firmware red panda nunca correu neste hardware.
3. **Assinatura do bootstub**: o bootstub release só aceita firmware assinado com a chave privada da comma (HRS §7). Placa de terceiros ⇒ compilar e gravar **bootstub + app em DEBUG** (`certs/debug`), via DFU; o openpilot/`pandad` pode recusar firmware não assinado — consequência operacional não verificada.
4. **Toolchain ARM ausente** → sem prova de compilação local (BLOQUEADO).
5. **USB_D± não acoplado** (4 vias, skew 2,5 mm) — FS 12 Mb/s tolera em geral, não validado.
6. **Impedância só estimada**; stackup não confirmado pelo fabricante.
7. **Consumo/térmica do H725** (SMPS, 550 MHz) com o regulador 5 V→3V3 do baseline: NÃO VERIFICADO (g-5).
8. **BOM PROVISÓRIA** (sem MPN/LCSC; ESR dos VCAP/SMPS crítico para o DS13311 §6.3).
9. **P1 refutada**: o City 2023 BR é CAN clássico — o projeto não traz ganho funcional face a um black panda para este veículo (decisão consciente do utilizador, D-05).
10. DRC herdado do baseline (hole_clearance P1 0,144 mm, courtyard D7/U9, vias 0,25) e 11 `starved_thermal` novas — ver `STEP5_layout_H725.md` §7.
11. Caixa mecânica do baseline incompatível (+5 mm).

## 11. Listas de honestidade
**NÃO VERIFICADO**: impedância/skew reais; consumo e térmica; enumeração USB/HW_TYPE; CAN FD em hardware; comportamento do `pandad` com firmware DEBUG; convenção de rotação do CPL para JLC; corpos 3D dos footprints VRML no STEP; ESR real dos condensadores escolhidos.
**BLOQUEADO**: compilação do firmware (sem `arm-none-eabi-gcc`/`scons`); firmware release assinado (chave privada comma); Git LFS do openpilot (403 — D-10, não necessário).
**BLOQUEADO_MANUAL**: escolha/compra de componentes com MPN/LCSC; confirmação do stackup com o fabricante; revisão visual de gerbers no GerbView; protótipo e bring-up (STEP 9); ligação ao veículo.
**NÃO EXECUTADO**: visualizador de gerber automatizado; TDR; testes de bancada; captura passiva no veículo; análise do host openpilot para D-06.

## 12. Fontes
`02_REFERENCE\REFERENCE_SOURCES.md` (proveniência); clones com hash: panda 408e14d4 (+ panda_full f62adf72, legado F4 f849893b), opendbc c3955753, openpilot ff47f484, hardware a42a4752, neo 9869dee9, panda_jungle b80539fc, harness_tester_challenge 069f7243, openpilot-docs 8a007654; ST DS13311 Rev 5 (STM32H725xE/G); OpenBlackPanda (cópia em `01_BASELINE`). Citações file:line nos documentos de `03_RESEARCH`.

## 13. Licenças
`08_DOCS\LICENSES.md`: baseline MIT (Lukas, 2023 — manter aviso nos derivados), commaai/panda, opendbc, openpilot MIT; `commaai/hardware` sem LICENSE (PDFs "you can copy this!" — não redistribuir fora do projeto); datasheet ST não redistribuída no pacote de fabricação.

## 14. Manifestos SHA-256 e índice
`00_MANIFESTS\`: `original_BEFORE.sha256` / `original_AFTER_STEP2…` / `original_AFTER_STEP7…` (ORIGINAL IDENTICAL), `OUTPUT_ROOT_STEP2/3/4/7/9_*.sha256`, `reference_clones.sha256`, `baseline_copy.sha256`. `INDEX.md` na raiz regenerado pelo `Make-Manifest.ps1`.

## 15. O que o utilizador precisa de fazer manualmente (lista curta)
1. Preencher MPN/LCSC na BOM (cristal CL, L5, FB1, condensadores com ESR) e reexportar (`step8_fabricate.py`).
2. Decidir USB_D±: rerotear manualmente como par acoplado em F.Cu (sem vias) ou aceitar o risco; depois `step7_validate.py` + `step8_fabricate.py`.
3. Confirmar stackup/impedância com o fabricante (4 camadas 1,59 mm, controlo de impedância para 120 Ω CAN / 90 Ω USB).
4. Abrir `07_FABRICATION\gerbers` no GerbView e rever visualmente (Edge.Cuts, máscara dos pads LQFP 0,5 mm, slots do P1).
5. Instalar `arm-none-eabi-gcc` + `scons`; compilar `02_REFERENCE\panda\board` (`scons -u -j8`) em DEBUG e guardar `panda_h7.bin.signed` + `bootstub.panda_h7.bin` para o STEP 9.
6. Só então: protótipo (1–2 unidades), bring-up de bancada (`STEP9_bringup_e_teste_veiculo.md`, 19 passos) e, se tudo passar, captura passiva no veículo com critérios de paragem.
7. Decisão D-06 (plataforma host openpilot) continua em aberto.
