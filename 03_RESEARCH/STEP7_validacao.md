# STEP 7 — Validação automatizada (logs reais em `06_REPORTS`)

Data: 2026-10-28 08:55:51. Gerado por `05_SCRIPTS\step7_validate.py` (148 s).

## Resumo

- **Falhas persistentes**: nenhuma
- Nota: 119 referências sem MPN na BOM (PROVISÓRIO — ver STEP4/R3v2)

## 1. ERC (`hybrid_ERC_step7.json`)

- Erros: **0** · Avisos: 367
  - warning/endpoint_off_grid: 143
  - warning/lib_symbol_issues: 6
  - warning/lib_symbol_mismatch: 183
  - warning/pin_to_pin: 35

## 2. DRC (`hybrid_DRC_step7.json`) vs baseline (`baseline_DRC.json`)

- Itens não ligados: **0** · clearance: **0** · curtos: **0** · courtyards_overlap: 0 (baseline 1) · track_width: 0

| Tipo | Híbrida | Baseline |
|---|---|---|
| copper_edge_clearance | 2 | 3 |
| courtyards_overlap | 0 | 1 |
| drill_out_of_range | 1 | 1 |
| footprint_type_mismatch | 0 | 11 |
| hole_clearance | 8 | 8 |
| isolated_copper | 0 | 1 |
| lib_footprint_mismatch | 73 | 67 |
| silk_edge_clearance | 4 | 4 |
| silk_over_copper | 1 | 0 |
| silk_overlap | 4 | 3 |
| starved_thermal | 18 | 13 |
| text_height | 68 | 82 |

Violações cuja assinatura (tipo + itens) **não existe no baseline**: 31
- starved_thermal [error]: Thermal relief connection to zone incomplete (layer In1.Cu; zone min spoke count 2; actual 1) — Zone [GND] on F.Cu, B.Cu and 2 more, priority 0 <> PTH pad 9 [GND] of U6
- starved_thermal [error]: Thermal relief connection to zone incomplete (layer In1.Cu; zone min spoke count 2; actual 1) — Zone [GND] on F.Cu, B.Cu and 2 more, priority 0 <> PTH pad 9 [GND] of U6
- starved_thermal [error]: Thermal relief connection to zone incomplete (layer In1.Cu; zone min spoke count 2; actual 1) — Zone [GND] on F.Cu, B.Cu and 2 more, priority 0 <> PTH pad 9 [GND] of U6
- starved_thermal [error]: Thermal relief connection to zone incomplete (layer F.Cu; zone min spoke count 2; actual 1) — Zone [GND] on F.Cu, B.Cu and 2 more, priority 0 <> Pad 2 [GND] of U9 on F.Cu
- starved_thermal [error]: Thermal relief connection to zone incomplete (layer B.Cu; zone min spoke count 2; actual 1) — Zone [GND] on F.Cu, B.Cu and 2 more, priority 0 <> Pad 2 [GND] of C52 on B.Cu
- starved_thermal [error]: Thermal relief connection to zone incomplete (layer B.Cu; zone min spoke count 2; actual 1) — Zone [GND] on F.Cu, B.Cu and 2 more, priority 0 <> Pad 2 [GND] of C46 on B.Cu
- starved_thermal [error]: Thermal relief connection to zone incomplete (layer B.Cu; zone min spoke count 2; actual 1) — Zone [GND] on F.Cu, B.Cu and 2 more, priority 0 <> Pad 6 [GND] of U7 on B.Cu
- starved_thermal [error]: Thermal relief connection to zone incomplete (layer B.Cu; zone min spoke count 2; actual 1) — Zone [GND] on F.Cu, B.Cu and 2 more, priority 0 <> Pad 69 [GND] of U7 on B.Cu
- starved_thermal [error]: Thermal relief connection to zone incomplete (layer B.Cu; zone min spoke count 2; actual 1) — Zone [GND] on F.Cu, B.Cu and 2 more, priority 0 <> Pad 89 [GND] of U7 on B.Cu
- starved_thermal [error]: Thermal relief connection to zone incomplete (layer B.Cu; zone min spoke count 2; actual 1) — Zone [GND] on F.Cu, B.Cu and 2 more, priority 0 <> Pad 104 [GND] of U7 on B.Cu
- starved_thermal [error]: Thermal relief connection to zone incomplete (layer B.Cu; zone min spoke count 2; actual 1) — Zone [GND] on F.Cu, B.Cu and 2 more, priority 0 <> Pad 2 [GND] of C40 on B.Cu
- starved_thermal [error]: Thermal relief connection to zone incomplete (layer F.Cu; 1 spokes connected to isolated island) — Zone [GND] on F.Cu, B.Cu and 2 more, priority 0 <> Pad A1 [GND] of P1 on F.Cu
- lib_footprint_mismatch [warning]: Footprint 'SOT95P230X110-3N' does not match copy in library 'BlackPanda' — Footprint D7
- lib_footprint_mismatch [warning]: Footprint 'SOT95P230X110-3N' does not match copy in library 'BlackPanda' — Footprint D9
- lib_footprint_mismatch [warning]: Footprint 'SOT23-3' does not match copy in library 'BlackPanda' — Footprint Q1
- lib_footprint_mismatch [warning]: Footprint 'SOT95P230X110-3N' does not match copy in library 'BlackPanda' — Footprint D5
- lib_footprint_mismatch [warning]: Footprint 'SOT95P230X110-3N' does not match copy in library 'BlackPanda' — Footprint D6
- lib_footprint_mismatch [warning]: Footprint 'SOT23-3' does not match copy in library 'BlackPanda' — Footprint Q2
- lib_footprint_mismatch [warning]: Footprint 'SOT95P230X110-3N' does not match copy in library 'BlackPanda' — Footprint D8
- lib_footprint_mismatch [warning]: Footprint 'LED-ARRAY-SMD_4P-L2.2-W2.1-BR' does not match copy in library 'BlackPanda' — Footprint U5
- lib_footprint_mismatch [warning]: Footprint 'Fiducial_1mm_Mask2mm' does not match copy in library 'Fiducial' — Footprint FID2
- lib_footprint_mismatch [warning]: Footprint 'IND-SMD_L7.3-W6.8' does not match copy in library 'BlackPanda' — Footprint L3
- lib_footprint_mismatch [warning]: Footprint 'Fiducial_1mm_Mask2mm' does not match copy in library 'Fiducial' — Footprint FID3
- lib_footprint_mismatch [warning]: Footprint 'DIOM4325X250N' does not match copy in library 'BlackPanda' — Footprint D1
- lib_footprint_mismatch [warning]: Footprint 'Fiducial_1mm_Mask2mm' does not match copy in library 'Fiducial' — Footprint FID1
- lib_footprint_mismatch [warning]: Footprint 'USB-C-SMD_TYPE-C-USB-20' does not match copy in library 'BlackPanda' — Footprint P1
- lib_footprint_mismatch [warning]: Footprint 'Fiducial_1mm_Mask2mm' does not match copy in library 'Fiducial' — Footprint FID4
- lib_footprint_mismatch [warning]: Footprint 'Fiducial_1mm_Mask2mm' does not match copy in library 'Fiducial' — Footprint FID6
- lib_footprint_mismatch [warning]: Footprint 'Fiducial_1mm_Mask2mm' does not match copy in library 'Fiducial' — Footprint FID5
- silk_over_copper [warning]: Silkscreen clipped by solder mask — Segment of P1 on F.Silkscreen <> Pad 1 [GND] of R1 on F.Cu
- silk_overlap [warning]: Silkscreen clearance — Reference field of C23 <> Segment of Y1 on B.Silkscreen

Nota: quase todas as 'novas' são do mesmo tipo das herdadas (text_height/lib_footprint_mismatch/silk) com itens renomeados (U7, C38–C63, R28–R33, J1, L5, D13/D14, FB1) ou deslocados pela placa +5 mm; as de cobre relevantes estão discutidas em `STEP5_layout_H725.md` §7.

## 3. Netlist esquemático × PCB

- Componentes no esquemático: 119 · footprints no PCB: 119 · só no esquemático: — · só no PCB: —
- Pads comparados: 481 · **redes divergentes: 0** · footprints divergentes: 0 · valores divergentes: 0
- Pinos/pads sem correspondência (informativo, ex.: pinos NC do símbolo ou pads mecânicos): 1

## 4. BOM × esquemático × PCB (`hybrid_BOM.csv`)

- Referências na BOM: 119 · DNP no esquemático (excluídos): — · só na BOM: — · no esquemático e fora da BOM: —
- Valores BOM≠sch: 0 · footprints BOM≠pcb: 0 · **sem MPN (PROVISÓRIO)**: 119 → C1, C10, C11, C12, C14, C16, C17, C18, C19, C2, C20, C21, C23, C24, C26, C27, C28, C29, C3, C30, C31, C32, C33, C34, C37, C38, C39, C4, C40, C41, C42, C43, C44, C45, C46, C47, C48, C49, C5, C50, C51, C52, C53, C54, C55, C56, C57, C58, C59, C6, C60, C61, C62, C63, C64, C65, C7, C8, D1, D10, D11, D12, D13, D14, D15, D2, D5, D6, D7, D8, D9, FB1, J1, JP1, L3, L4, L5, P1, Q1, Q2, Q3, Q4, R1, R14, R15, R16, R17, R18, R19, R2, R20, R21, R23, R24, R26, R27, R28, R29, R3, R30, R31, R32, R33, R5, R6, R9, SW1, U1, U10, U11, U12, U13, U3, U5, U6, U7, U8, U9, Y1

## 5. Paridade firmware × hardware (`06_REPORTS\parity_red_h7_hybrid_HybridPanda_netlist.md`)

- Código de saída: 0 · estados: {'OK': 36} · **PIN_PARITY_CONFLICT: 0**

## 6. Skew / comprimentos / impedância

- Ver `03_RESEARCH\STEP6_roteamento_impedancia.md` e `06_REPORTS\step6_reports.json` (gerados por `step6_reports.py`). **O DRC do KiCad não verifica impedância**; os valores são estimativas analíticas (Hammerstad–Jensen) sobre o stackup declarado, não medidos.

## 7. Manifestos

- `Make-Manifest.ps1 -Step STEP7 -Original` exit 0:
  - OUTPUT_ROOT manifest: 20727 files -> C:\Users\costabr\Downloads\openpilot\HybridPanda_v2_20261022_1616\00_MANIFESTS\OUTPUT_ROOT_STEP7_20261028_0856.sha256
  - 02_REFERENCE unchanged vs reference_clones.sha256: False
  - ORIGINAL vs BEFORE: IDENTICAL (377 files)
  - INDEX.md rows: 14876

## 8. Comandos executados

| Comando | Exit | s | Log |
|---|---|---|---|
| `C:\Users\costabr\AppData\Local\Programs\KiCad\10.0\bin\kicad-cli.exe sch erc --format json --severity-all -o C:\Users\costabr\Downloads\openpilot\HybridPanda_v2` | 0 | 4.2 | step7_erc.log |
| `C:\Users\costabr\AppData\Local\Programs\KiCad\10.0\bin\kicad-cli.exe pcb drc --format json --severity-all --units mm -o C:\Users\costabr\Downloads\openpilot\Hyb` | 0 | 5.0 | step7_drc.log |
| `C:\Users\costabr\AppData\Local\Programs\KiCad\10.0\bin\kicad-cli.exe sch export netlist --format kicadxml -o C:\Users\costabr\Downloads\openpilot\HybridPanda_v2` | 0 | 0.8 | step7_netlist.log |
| `C:\Users\costabr\AppData\Local\Programs\KiCad\10.0\bin\kicad-cli.exe sch export bom --fields Reference,Value,Footprint,${QUANTITY},${DNP},MPN,Manufacturer,Datas` | 0 | 2.5 | step7_bom.log |
| `C:\Users\costabr\Downloads\openpilot\HybridPanda_v2_20261022_1616\05_SCRIPTS\.venv\Scripts\python.exe C:\Users\costabr\Downloads\openpilot\HybridPanda_v2_202610` | 0 | 0.7 | step7_parity.log |
| `powershell -NoProfile -ExecutionPolicy Bypass -File C:\Users\costabr\Downloads\openpilot\HybridPanda_v2_20261022_1616\05_SCRIPTS\Make-Manifest.ps1 -Step STEP7 -` | 0 | 134.7 | step7_manifest.log |
