# RESUME - Passo 3 (SI/PI HIGH) - estado em que a sessao foi interrompida

Branch main, commit anterior a5d60b8 (passo 2). Este commit = passo 3 WIP (placa consistente).

## Estado da placa (04_PROJECT/HybridPanda)
- DRC (06_REPORTS/corr/drc_step3c.json): total 180, clearance 0, unconnected 0.
  Delta vs baseline step7 (184): silk_over_copper +1 (silk do P1 sobre pad 1 do R1 em 133.2,53.96),
  lib_footprint_mismatch -1, text_height -3. Categorias herdadas inalteradas (hole_clearance 8 P1,
  starved_thermal 18, copper_edge 2, silk_edge 4, silk_overlap 4, drill_out_of_range 1).
- ERC do esquema: 0 (corr_gate.py erc) apos corr_step3_sch.py. Esquema e PCB carregam no kicad-cli.
- step7_validate.py e final_audit.py NAO foram re-executados apos o passo 3 PCB (rodar antes de fechar).

## Itens de proposed_changes.md
Aplicados (esquema + PCB):
- Item 4: R1 1k 0402 -> 10k R_0603, vertical em (134.0,53.4) F.Cu (pad GND em baixo ligado ao trilho GND do
  shell do P1; pad 2 na rede Net-(D15-A) ligado a D2.2 e Q4.4). Pad 1 com ligacao solida ao plano.
- Item 5: D15 BZT52C12 SOD-123 em B.Cu (133.9,50.45), K=12V_Protected (vias 134.75,48.6/49.425),
  A=gate via via (134.7,51.5). Rede Net-(D2-A) renomeada para Net-(D15-A).
- Item 8/18/19: R20/R21 22R movidos para B.Cu junto aos pads 100/101 do U7 (114.25, 43.15/44.25);
  vias (113.635,42.75)/(113.635,44.78) para In1; par acoplado In1 0.2 mm / gap 0.3 em y 45.1/45.6 ate
  (128.8,45.1)/(127.9,45.65); U13 USBLC6-2SC6 SOT-23-6 em F.Cu (128.85,41.2) rot 180, flow-through
  (pads 1-6 e 3-4 unidos por trilho curto), saida para U3.2/U3.3; GND via (126.9,41.2); VBUS via
  (128.85,43.55) -> B.Cu -> via (129.78,46.5) no trilho USB_PWR. Stitch GND F.Cu cortado em (127.47,49.64)
  com via nova; via GND (129.12,43.42) removida.
- Item 11: +5V ate U1.6 alargado (In1 1.0 / 0.5, F.Cu 0.5) + via (117.3,55.0).
Parcial:
- Item 6: C4/C12 valor 10uF no esquema e PCB, mas footprint fisico continua C_0805 (1206 nao cabe).
  PENDENTE: reverter o campo Footprint de C4/C12 no .kicad_sch para Capacitor_SMD:C_0805_2012Metric
  (hoje esta C_1206 -> gera schematic_parity/lib mismatch) e documentar o desvio (peca 10uF 50V X5R 0805,
  ex. Murata GRM21BR61H106KE43).
Pendente / nao aplicado:
- Item 16 (no SW / posicao de L4): exige mover blocos grandes. Documentar como nao aplicado.
- silk_over_copper P1 x R1: avaliar encurtar o segmento de silk do P1 ou aceitar (warning).

## Scripts
- 05_SCRIPTS/corr_step3_sch.py (esquema, ja aplicado), corr_step3_pcb.py --from-backup (replay completo a
  partir de %TEMP%/hp_backup/step3), corr_step3_u13link.py (trilhos 1-6 / 3-4 do U13), corr_gate.py
  (drc --tag X | erc | backup stepN), tools/net_dump.py.
- Backups fora do repo: %TEMP%/hp_backup/step3 (estado pos-passo-2). Se o TEMP for perdido, usar
  `git show a5d60b8:04_PROJECT/HybridPanda/HybridPanda.kicad_pcb`.

## Proximos comandos (ordem)
1. Editar .kicad_sch: C4/C12 Footprint -> C_0805_2012Metric; `python -u corr_gate.py erc`.
2. `python -u step7_validate.py` e `python -u final_audit.py` (shorts 0, vip 0); `corr_gate.py drc --tag step3d`.
3. Commit "pcb: step 3 - SI/PI HIGH items applied".
4. Passo 4 (BOM): 47uF 0805 +5V -> peca 10 V de BOM_HYBRIDPANDA_v1.csv; C8 10uF 0402->0603 se recomendado;
   U1 TPS2553 so como alternativa documentada; atualizar hybrid_BOM.csv / BOM_JLCPCB.csv e valores no esquema.
5. Passo 5 (MEDIUM, sem re-floorplan): thermals (U6 EP, C40, D6, U7 VSS/pad 104), C38 NRST, D8/D5, CAN 0.25 mm,
   U3 shell GND, regras de drc_audit.json, P1 hole clearance.
6. Final: final_audit + DRC + step7 + step8_fabricate.py (exports); docs RELATORIO_FINAL.md, PROGRESS.md,
   DECISIONS.md (D-34+), 06_REPORTS/CORRECOES_APLICADAS.md. Sem push.

## Fechamento do passo 3 (sessao seguinte)
- Item 6: campo Footprint de C4/C12 revertido para C_0805_2012Metric (corr_step3_c4c12.py); peca BOM 10uF 50V X5R 0805.
- tracks_crossing (U13.2 GND x link USB_R_D+ em F.Cu, herdado do 3c) corrigido por corr_step3_u13gnd.py: trilho D+ do conector
  movido para y=38.4, GND do U13.2 sai para cima ate via (128.85,39.2). DRC step3e: total 179, clearance 0, unconnected 0.
- Item 16: DEFERIDO. A posicao proposta para D12 (109.3,38.6 rot 90) colide com U6; a zona SW e o unico cobre largo entre
  U6.8 e D12.1 (apaga-la deixaria 0.4 mm para a corrente do indutor); aproximar L4 exige realocar C4/C6/C7/L4 (re-floorplan).
  C37.2->PH < 2 mm impossivel (BOOT pino 1 e PH pino 8 em lados opostos do DDA). Ver CORRECOES_APLICADAS.md.
- step7_validate.py: falhas []; final_audit.py: shorts 0, vip 0, hole_hits 8 (P1, herdado).
