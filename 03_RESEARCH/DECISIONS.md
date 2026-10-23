# DECISIONS.md — registro de decisões (ADR curto)

Formato: ID | data | decisão | alternativas | evidência | status.

## D-01 — Raiz de execução = pasta v2 existente (sem subpasta `run_`)
- Data: 2026-10-22
- Decisão: usar `HybridPanda_v2_20261022_1616` como OUTPUT_ROOT efetivo do protocolo v3 em vez de criar `run_<timestamp>` novo.
- Motivo: STEP 1 já concluído nela (manifestos, baseline, clones, ERC/DRC baseline); recriar violaria "não duplicar trabalho" e quebraria referências. Estrutura de pastas é a mesma exigida pelo v3.
- Status: ATIVA.

## D-02 — MCU STM32H725ZGT6 (LQFP144), modo Direct SMPS
- Data: 2026-10-22
- Decisão do usuário (fixa): família/parte = STM32H725. Decisão técnica derivada: encapsulamento LQFP144, não TFBGA100 nem LQFP100.
- Alternativas rejeitadas:
  - TFBGA100 (H723/H725): firmware `stm32h7/clock.h:30-47` força **LDO** nesse pacote; a biblioteca KiCad e DS13311 Tab.8 mostram **ausência de GPIOF/GPIOG** → PF7–PF11, PG9–PG11 (HW_TYPE straps, FDCAN3, STB bus0, VOLT_S) inexistem → paridade 1:1 com `red.h` impossível.
  - LQFP100: idem (sem PF/PG) e PKGR não reconhecido pelo firmware → `while(true)`.
  - UFBGA169: tem SMPS e todos os pinos, mas BGA 0,5 mm é inviável para montagem/4 camadas no formato Black Panda.
- Evidência: `02_REFERENCE\panda\board\stm32h7\clock.h`, `03_RESEARCH\kicad_lib_STM32H723VGHx_pins.txt`, `03_RESEARCH\P3_tabela_pinos_LQFP144_vs_firmware.md` (39/39 pinos presentes, AF confirmadas, cruzamento com lib KiCad: 0 divergências).
- Consequências: alimentação do core via SMPS interno (indutor 2,2 µH + caps conforme DS Tab.16); VDDLDO ainda alimentado; `-DSTM32H725xx` já é o build padrão do red panda.
- Status: ATIVA.

## D-03 — Remoção do GPS NEO-M8M
- Decisão: não portar o bloco GPS do Black Panda (red panda não tem GPS; firmware não usa UART para GPS no H7). Área liberada para LQFP144 + SMPS.
- Status: ATIVA (ainda não executada no esquemático).

## D-04 — Terminação 120 Ω
- Decisão provisória: footprints de terminação selecionável **não populados** por padrão (ponto de conexão no City é em derivação do harness, barramento já terminado). Justificar por canal na Fase 4.
- 2026-10-23: **CONFIRMADA** por fonte oficial — hardware\harness\v3\Harness_Box.pdf mostra R6/R7/R8 120 Ω dentro da harness box (CAN0' e CAN2/CAN2'') → o lado panda não termina. Manter footprints DNP para bancada (sem harness box).
- Status: ATIVA.

## D-05 — Premissa P1 (CAN-FD no City 2023 BR) REFUTADA; prosseguir mesmo assim
- Evidência: opendbc `HONDA_CITY_7G = HondaBoschPlatformConfig(..., BOSCH_RADARLESS)`, CAN clássico 500 kbit/s. Usuário optou por continuar com H7 (FDCAN é retrocompatível; black panda FW descontinuado).
- Status: ATIVA.

## D-06 — Plataforma host do openpilot (smartphone vs. dispositivo dedicado tipo comma 4)
- Data: 2026-10-22
- Status: **PENDENTE — não decidir sem o usuário.** Opções: (a) smartphone/dispositivo externo; (b) hardware dedicado rodando openpilot localmente com tela, câmeras, IMU, GPS (modelo comma four). Ao retomar, levantar requisitos no clone do openpilot (system/hardware/*, pandad, camadas tici/comma four) e produzir comparativo para a decisão.

## D-07 — Termo "openflow" = openpilot
- Interpretação registrada conforme protocolo v3 (0x00 Constantes).
- Status: ATIVA.

## D-08 — Straps HW_TYPE para RED (id1 = 0)
- Data: 2026-10-23
- Decisão: PF7, PF8, PF9, PF10 ligados a GND (resistor 0 Ω/direto; firmware lê com pull-up interno, `stm32h7/board.h:25-29`). PD4, PD5, PD6 deixados NC (id2 ≠ 3 garantido, pois PD7 é saída STB e flutua alto na leitura). Alternativa rejeitada: resistores de pull-down "fracos" (valor real do red panda NV; 0 Ω elimina margem de erro).
- Evidência: HRS_red_panda.md §1.
- Status: ATIVA.

## D-09 — STB dos transceivers com pull-up externo (fail-safe silencioso)
- Data: 2026-10-23
- Decisão: cada linha STB (PG11, PB3, PD7, PB4) com pull-up 10 kΩ para 3,3 V, para que os transceivers fiquem em standby desde o reset até `board_init` (early_gpio_float deixa tudo flutuando, `stm32h7_config.h:95`). Valor do red panda NV; 10 kΩ é prática comum e não conflita com saída push-pull.
- Status: ATIVA.

## D-10 — Clone do openpilot sem objetos Git LFS
- Data: 2026-10-23
- Fato: checkout falhava (1255 arquivos) por LFS → `huggingface.co/commaai/openpilot-lfs.git` responde 403, não por long paths. Solução: `GIT_LFS_SKIP_SMUDGE=1`, `filter.lfs.smudge --skip`; 253 ponteiros LFS mantidos como texto. Clone limpo em ff47f484, submódulos iniciados (depth 1).
- Implicação: nenhuma análise de hardware/host depende de binários LFS. Registrado em LICENSES.md.
- Status: ATIVA.

## D-11 — Versão do firmware panda de referência
- Data: 2026-10-23
- Fato: openpilot ff47f484 pina o submódulo panda em **a5919516**, enquanto o clone `02_REFERENCE\panda` está em **408e14d4** (master). Decisão: HRS baseado em 408e14d4 (mais recente); antes do STEP 8 (bring-up) comparar `board/boards/red.h`, `stm32h7/*` entre os dois commits e registrar diff (esperado: nenhum impacto em pinos).
- Status: ATIVA (diff pendente).

## D-12 — Caminho SBU → ADC não pode ser direto em PC4
- Data: 2026-10-23
- Fato: DS13311 Tab. 8: PC4 é **TT_ha** (3,6 V máx.), PA1 é FT_ha; a linha SBU chega a 5 V quando o relé é acionado (Harness_Box.pdf / harness.h). Decisão: divisor resistivo ou resistor série + clamp em ambos SBU1/SBU2 (simetria), dimensionado para que 240 Ω → "baixo", 1 kΩ → "baixo", aberto → "alto" em relação a 1650 mV e ao VIL digital. Valores finais no STEP 4.
- Status: ATIVA (dimensionamento pendente).
## D-13 — Pinagem do conector P1 (TYPE-C-31-M-04) mantida igual ao baseline
- Data: 2026-10-23
- Fato: netlist do baseline: bus0 xcvr→B10/B11, bus1-normal→B2/B3, bus1-OBD→A2/A3, bus2→A10/A11, SBU1=A8, SBU2=B8. Pinout oficial do lado harness (OBD-C.sch.pdf): CAN0=A2/A3, CAN1=A10/A11, CAN2=B2/B3, CAN3=B10/B11. O cabo USB-C full-featured cruza TX1(A2/A3)↔RX1(B11/B10), RX2(A11/A10)↔TX2(B2/B3) e SBU1↔SBU2; harness.h:71-75 confirma o cruzamento SBU ("SBU1->SBU2 is the normal orientation connection per USB-C cable spec"). Resultado: panda bus0→CAN0 carro, bus1-normal→CAN1 radar, bus1-OBD→CAN3 comma power, bus2→CAN2 câmera — coerente com o firmware red (red.h:31-61, can_common.h:130-134).
- Decisão: não alterar a pinagem de P1; só trocar os pinos do MCU nos transceivers. Cruzamento do cabo é inferência da spec USB-C [I]; o comportamento flipped é tratado pelo firmware em qualquer caso.
- Evidência: STEP3_engenharia_reversa_tabela_hibrida.md §g-1.
- Status: ATIVA.

## D-14 — VDD33USB = 3V3 externo; VDD50USB ligado a VDD33USB
- Data: 2026-10-23
- Fato: firmware red habilita apenas `PWR_CR3_USB33DEN` (stm32h7/clock.h:121); `USBREGEN` só em tres.h:106. Regulador USB interno OFF ⇒ DS13311 l.1459-1460 e tabela de condições de operação (l.8453-8455): VDD33USB alimentado externamente com 3,3 V e VDD50USB = VDD33USB.
- Decisão: VDD33USB (91) e VDD50USB (90) ambos no trilho +3V3, com 100 nF cada.
- Status: ATIVA.

## D-15 — Correção de rótulo normal/OBD do FDCAN2 (errata interna)
- Data: 2026-10-23
- Fato: red.h:36-61 e black.h:33-57: `(mode==NORMAL) != flipped` → **PB5/PB6 = normal (xcvr 2, STB PB3/PC13)**; senão **PB12/PB13 = OBD (xcvr 4, STB PB4/PB10)**. firmware_pins.json e HRS §3/§5 tinham os rótulos invertidos; corrigidos nesta data (grupos trocados, pinos inalterados — parity_check black_f4 continua 35/35).
- Status: ATIVA.
## D-16 — Condicionamento SBU → ADC: 10 kΩ série + BAT54S (clamp) em PC4 e PA1
- Data: 2026-10-23
- Fato: PC4 é TT_ha (3,6 V abs. máx., DS13311 Tab. 8); SBU chega a 5 V com relé acionado. Divisor resistivo rejeitado: com o pull-up de 10 kΩ existente (R23/R24 → 3V3) o caso "aberto" cairia ≈ 1,65 V ≈ limiar do firmware (1650 mV) e o caso 5 V ainda excederia 3,6 V em PC4 sem clamp. Escolhido: 10 kΩ série (R28/R29) + BAT54S (D13/D14: COM no nó ADC, K → 3V3, A → GND) em ambos os canais (simetria).
- Riscos: clamp em 3,3 + Vf ≈ 3,55 V — marginal vs. 3,6 V (corrente limitada a ≈ (5−3,55)/10k = 145 µA → Vf baixo); impedância de fonte do ADC ≈ 20 kΩ (ADC do H7 tolera com tempo de amostragem longo — firmware usa `ADC_SMPR` padrão; **NV**, validar no bring-up: ler SBU com 240 Ω / 1 kΩ / aberto / 5 V).
- Status: ATIVA (validação no STEP 8).

## D-17 — Nets CAN renomeadas CANx_* → BUS0/BUS1N/BUS1O/BUS2_* (EN → STB)
- Data: 2026-10-23
- Fato: a numeração CANx do baseline não coincide com a numeração de bus do firmware (bus0 = CAN2_, bus1 normal = CAN3_, bus1 OBD = CAN1_, bus2 = CAN0_). Para o STEP 5–9 e para o verificador, os nomes de net seguem o firmware. P1 inalterado (D-13).
- Status: ATIVA.

## D-18 — Folha A1, U7 em (701,04; 266,70), blocos de suporte em x 787–813 e regiões liberadas
- Data: 2026-10-23
- Fato: o símbolo STM32H725ZGTx (±48,26 × ±93,98 mm) não cabe na região do F413 em A2. Folha ampliada para A1 (841 × 594); MCU e coluna de suporte à direita (x ≥ 600), pull-ups STB e banco de desacoplamento na região liberada do F413, PWR_FLAGs na região do GPS. Gerado por `step4_build_schematic.py` (determinístico, idempotente a partir de `HybridPanda.kicad_sch.baseline`).
- Status: ATIVA.

## D-19 — Três pinos VCAP interligados; ERC power_out↔power_out rebaixado para aviso
- Data: 2026-10-23
- Fato: DS13311 §6.3.2: VCAP ×3 ligados entre si com 2 × 2,2 µF (ESR < 100 mΩ). O símbolo KiCad declara VCAP como `power_out`; a matriz padrão do ERC marca power_out↔power_out como erro. Alterado `erc.pin_map[8][8] = 1` (aviso) no `HybridPanda.kicad_pro` — único efeito colateral: outros curtos entre power_out passariam a aviso; nenhum outro par existe no projeto (ERC: só os 2 pares VCAP).
- Status: ATIVA.

## D-20 — Transceivers TJA1042TK/3 reaproveitados (CAN FD 5 Mbit/s confirmado)
- Data: 2026-10-23
- Fato: datasheet NXP TJA1042 (R3v2 §3.1, [F]): "timing guaranteed for data rates up to 5 Mbit/s in the CAN FD fast phase"; pinagem HVSON8 TXD1/GND2/VCC3/RXD4/VIO5/CANL6/CANH7/STB8 igual ao footprint do baseline. Alternativas documentadas: TCAN1042HGV-Q1 (provável pino-compatível, NV), MCP2562FD (NV), TCAN1044V (NÃO pino-compatível). Substitui a hipótese "Substituído" da tabela híbrida (STEP 3 §f/§g). A linha "Transceivers" passa a **Reaproveitado**.
- Status: ATIVA.
