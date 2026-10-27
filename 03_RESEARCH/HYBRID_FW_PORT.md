# HYBRID_FW_PORT - Port do firmware panda (H7) para a Hybrid Panda

Data: 2026-10-27
Repositorio: clone `panda_hybrid` (origin kriptomad/panda, upstream commaai/panda master `1305b78c`),
branch `hybrid-h725`, commit `a8babfea38e278aa5fe35a2937a77f75564a57ce` (nao enviado / sem push).
Fonte de verdade dos pinos: `04_PROJECT\HybridPanda\HybridPanda.kicad_sch` -> netlist kicadxml
(`kicad-cli sch export netlist --format kicadxml`), componente U7 = STM32H725ZGT6 (LQFP144).
Nada aqui foi testado em hardware (ver secao 10).

## 1. Resumo executivo

- Todos os 39 pinos de sinal usados pelo firmware do red panda caem exatamente nos mesmos pinos
  no U7 da Hybrid Panda (CAN TX/RX x4, STB x4, SBU ADC x2, relay x2, VoltageSens, 5VOUT_S, USB_LOAD,
  LED x3, USB D+/D-, HSE, SWD, BOOT0). Nenhum pino precisa ser movido para ter a funcao alternativa.
- Com a PCB como esta (PF7..PF10 = GND -> id1 = 0) o firmware upstream detecta a placa como
  **HW_TYPE_RED_PANDA (7)** e todas as funcoes de `red.h` sao corretas para ela.
- Foi adicionado `HW_TYPE_HYBRID_PANDA = 11` com deteccao `id1 == 4` (PF9 aberto, PF7/PF8/PF10 em GND).
  Requer uma alteracao de strap na PCB (item PCR-1). Sem o strap, a placa continua funcionando como red panda.
- **Esquema de alimentacao: DIVERGENCIA CRITICA.** O firmware configura *Direct SMPS* em qualquer LQFP144
  (`PWR->CR3 = SMPSEN`, LDO desligado). Nesse modo a saida do SMPS (VFBSMPS, pino 17) deve estar ligada
  externamente a VCAP (pinos 68/103/140). Na netlist, `VFBSMPS` (C42, L5) e `VCAP` (C39, C40) sao redes
  **separadas**. Resultado esperado com a PCB atual + firmware upstream: o core fica sem alimentacao, o MCU
  nao arranca (travamento descrito no proprio `clock.h`). Correcao recomendada na PCB (PCR-2). Como fallback
  para placas ja fabricadas foi adicionado um alvo opcional `panda_h7_ldo` (`HYBRID_LDO=1`) que forca LDO.
- Build: `panda_h7`, `panda_h7_ldo` e `body_h7` compilam em DEBUG e RELEASE=1 (gcc 14.2.Rel1, -Werror).

## 2. Mapa completo de pinos do U7 (netlist)

Legenda: `n.c.` = pino sem rede; `-` = demais nos omitidos (GND/+3V3 com dezenas de capacitores).

| Pino | Nome | Rede | Outros nos da rede |
|------|------|------|--------------------|
| 1 | PE2 | LED_BLUE | R17.1 |
| 2 | PE3 | LED_GREEN | R18.1 |
| 3 | PE4 | LED_RED | R19.1 |
| 4 | PE5 | n.c. |  |
| 5 | PE6 | n.c. |  |
| 6 | VSS | GND | - |
| 7 | VDD | +3V3 | - |
| 8 | VBAT | +3V3 | - |
| 9 | PC13 | n.c. |  |
| 10 | PC14 | n.c. |  |
| 11 | PC15 | n.c. |  |
| 12 | VSS | GND | - |
| 13 | VDD | +3V3 | - |
| 14 | VSSSMPS | GND | - |
| 15 | VLXSMPS | VLXSMPS | C41.1 L5.1(1_1) |
| 16 | VDDSMPS | +3V3 | - |
| 17 | VFBSMPS | VFBSMPS | C42.1 L5.2(2_2) |
| 18 | VSS | GND | - |
| 19 | VDD | +3V3 | - |
| 20 | PF6 | n.c. |  |
| 21 | PF7 | GND | - |
| 22 | PF8 | GND | - |
| 23 | PF9 | GND | - |
| 24 | PF10 | GND | - |
| 25 | PH0 | HSE_IN | C23.1 Y1.1(1_1) |
| 26 | PH1 | HSE_OUT | C24.1 Y1.3(3_3) |
| 27 | NRST | NRST | C38.1 J1.10(Pin_10_10) |
| 28 | PC0 | n.c. |  |
| 29 | PC1 | n.c. |  |
| 30 | PC2_C | n.c. |  |
| 31 | PC3_C | n.c. |  |
| 32 | VDD | +3V3 | - |
| 33 | VSS | GND | - |
| 34 | VSSA | GND | - |
| 35 | VREF+ | VDDA | C43.1 C44.1 FB1.1 |
| 36 | VDDA | VDDA | C43.1 C44.1 FB1.1 |
| 37 | PA0 | n.c. |  |
| 38 | PA1 | SBU2_ADC | D14.3(COM_3) R29.2 |
| 39 | PA2 | n.c. |  |
| 40 | PA3 | n.c. |  |
| 41 | VSS | GND | - |
| 42 | VDD | +3V3 | - |
| 43 | PA4 | n.c. |  |
| 44 | PA5 | n.c. |  |
| 45 | PA6 | n.c. |  |
| 46 | PA7 | n.c. |  |
| 47 | PC4 | SBU1_ADC | D13.3(COM_3) R28.2 |
| 48 | PC5 | n.c. |  |
| 49 | PB0 | n.c. |  |
| 50 | PB1 | 5VOUT_S | R15.2 R16.1 |
| 51 | PB2 | n.c. |  |
| 52 | PF11 | VoltageSens | R2.2 R3.1 |
| 53 | PF14 | n.c. |  |
| 54 | PF15 | n.c. |  |
| 55 | VSS | GND | - |
| 56 | VDD | +3V3 | - |
| 57 | PE7 | n.c. |  |
| 58 | PE8 | n.c. |  |
| 59 | PE9 | n.c. |  |
| 60 | PE10 | n.c. |  |
| 61 | PE11 | n.c. |  |
| 62 | PE12 | n.c. |  |
| 63 | PE13 | n.c. |  |
| 64 | PE14 | n.c. |  |
| 65 | PE15 | n.c. |  |
| 66 | PB10 | n.c. |  |
| 67 | PB11 | n.c. |  |
| 68 | VCAP | VCAP | C39.1 C40.1 |
| 69 | VSS | GND | - |
| 70 | VDDLDO | +3V3 | - |
| 71 | VDD | +3V3 | - |
| 72 | PB12 | BUS1O_RX | U8.4(RXD_4) |
| 73 | PB13 | BUS1O_TX | U8.1(TXD_1) |
| 74 | PB14 | USB_LOAD | Q3.1(B_1) |
| 75 | PB15 | n.c. |  |
| 76 | PD8 | n.c. |  |
| 77 | PD9 | n.c. |  |
| 78 | PD10 | n.c. |  |
| 79 | VDD | +3V3 | - |
| 80 | VSS | GND | - |
| 81 | PD11 | n.c. |  |
| 82 | PD12 | n.c. |  |
| 83 | PD13 | n.c. |  |
| 84 | PD14 | n.c. |  |
| 85 | PD15 | n.c. |  |
| 86 | PG6 | n.c. |  |
| 87 | PG7 | n.c. |  |
| 88 | PG8 | n.c. |  |
| 89 | VSS | GND | - |
| 90 | VDD50USB | +3V3 | - |
| 91 | VDD33USB | +3V3 | - |
| 92 | VDD | +3V3 | - |
| 93 | PC6 | n.c. |  |
| 94 | PC7 | n.c. |  |
| 95 | PC8 | n.c. |  |
| 96 | PC9 | n.c. |  |
| 97 | PA8 | n.c. |  |
| 98 | PA9 | n.c. |  |
| 99 | PA10 | n.c. |  |
| 100 | PA11 | USB_D- | R20.1 |
| 101 | PA12 | USB_D+ | R21.2 |
| 102 | PA13 | SWDIO | J1.2(Pin_2_2) |
| 103 | VCAP | VCAP | C39.1 C40.1 |
| 104 | VSS | GND | - |
| 105 | VDDLDO | +3V3 | - |
| 106 | VDD | +3V3 | - |
| 107 | PA14 | SWCLK | J1.4(Pin_4_4) |
| 108 | PA15 | n.c. |  |
| 109 | PC10 | relay_SBU1 | Q2.1(B_1) |
| 110 | PC11 | relay_SBU2 | Q1.1(B_1) |
| 111 | PC12 | n.c. |  |
| 112 | PD0 | n.c. |  |
| 113 | PD1 | n.c. |  |
| 114 | PD2 | n.c. |  |
| 115 | PD3 | n.c. |  |
| 116 | PD4 | n.c. |  |
| 117 | PD5 | n.c. |  |
| 118 | VSS | GND | - |
| 119 | VDD | +3V3 | - |
| 120 | PD6 | n.c. |  |
| 121 | PD7 | BUS2_STB | R33.2 U9.8(STB_8) |
| 122 | PG9 | BUS2_TX | U9.1(TXD_1) |
| 123 | PG10 | BUS2_RX | U9.4(RXD_4) |
| 124 | PG11 | BUS0_STB | R30.2 U11.8(STB_8) |
| 125 | PG12 | n.c. |  |
| 126 | PG13 | n.c. |  |
| 127 | PG14 | n.c. |  |
| 128 | VSS | GND | - |
| 129 | VDD | +3V3 | - |
| 130 | PB3 | BUS1N_STB | R31.2 U10.8(STB_8) |
| 131 | PB4(NJTRST) | BUS1O_STB | R32.2 U8.8(STB_8) |
| 132 | PB5 | BUS1N_RX | U10.4(RXD_4) |
| 133 | PB6 | BUS1N_TX | U10.1(TXD_1) |
| 134 | PB7 | n.c. |  |
| 135 | BOOT0 | BOOT0 | R14.1 SW1.1(1_1) |
| 136 | PB8 | BUS0_RX | U11.4(RXD_4) |
| 137 | PB9 | BUS0_TX | U11.1(TXD_1) |
| 138 | PE0 | n.c. |  |
| 139 | PE1 | n.c. |  |
| 140 | VCAP | VCAP | C39.1 C40.1 |
| 141 | VSS | GND | - |
| 142 | PDR_ON | +3V3 | - |
| 143 | VDDLDO | +3V3 | - |
| 144 | VDD | +3V3 | - |

## 3. Mapeamento rede -> funcao de firmware (comparado com `board/boards/red.h`)

| Funcao firmware | Pino H725 | Rede | red.h | Hybrid | Observacao |
|---|---|---|---|---|---|
| FDCAN1 RX / TX (bus 0) | PB8 / PB9 | BUS0_RX / BUS0_TX | PB8/PB9 AF9 | igual | U11 TJA1042 -> P1 B10/B11 (CAN0 do harness, igual black panda) |
| FDCAN2 RX / TX "normal" (bus 1) | PB5 / PB6 | BUS1N_RX / BUS1N_TX | PB5/PB6 AF9 | igual | U10 -> P1 B3/B2 |
| FDCAN2 RX / TX "OBD" (bus 1 alt) | PB12 / PB13 | BUS1O_RX / BUS1O_TX | PB12/PB13 AF9 | igual | U8 -> P1 A3/A2 |
| FDCAN3 RX / TX (bus 2) | PG10 / PG9 | BUS2_RX / BUS2_TX | PG10/PG9 AF2 | igual | U9 -> P1 A10/A11 |
| transceiver 1 enable (STB) | PG11 | BUS0_STB | PG11 | igual | STB alto = standby; `set_gpio_output(!enabled)`; pull-up R30 10k |
| transceiver 2 enable (STB) | PB3 | BUS1N_STB | PB3 | igual | pull-up R31 |
| transceiver 3 enable (STB) | PD7 | BUS2_STB | PD7 | igual | pull-up R33; tambem bit 3 do id2 |
| transceiver 4 enable (STB) | PB4 | BUS1O_STB | PB4 | igual | pull-up R32 |
| SBU1 ADC | PC4 (ADC1_INP4) | SBU1_ADC | PC4 / ADC1 ch4 | igual | R28 10k em serie, BAT54S D13 clamp GND/3V3, SBU1 pull-up R24 10k p/ 3V3 |
| SBU2 ADC | PA1 (ADC1_INP17) | SBU2_ADC | PA1 / ADC1 ch17 | igual | R29 10k, D14 clamp, SBU2 pull-up R23 10k |
| relay SBU1 | PC10 | relay_SBU1 | PC10 | igual | Q2 DDTA143E (PNP pre-polarizado, E=+5V, C=SBU1) |
| relay SBU2 | PC11 | relay_SBU2 | PC11 | igual | Q1 idem |
| tensao 12V | PF11 (ADC1_INP2) | VoltageSens | ADC1 ch2 x11 | igual | divisor R3 10k / R2 1k = x11, de 12V_Protected |
| 5VOUT_S | PB1 (ADC1_INP5) | 5VOUT_S | PB1 analogico | igual | divisor 10k/10k de +5V |
| USB load switch | PB14 | USB_LOAD | PB14 OD + pull-up, nivel 1 | igual | Q3 PDTC114EU -> U1 AP22615 EN (R26 10k p/ +5V). Mesmo circuito do black panda |
| LED R / G / B | PE4 / PE3 / PE2 | LED_RED/GREEN/BLUE | {PE4,PE3,PE2} | igual | U5 anodo comum em +3V3 -> ativo em nivel baixo; `led_set` usa `!enabled` em open-drain |
| USB OTG_FS DM / DP | PA11 / PA12 | USB_D- / USB_D+ | PA11/PA12 AF10 | igual | 22R serie (R20/R21), conector USB-A U3 |
| VBUS sense | - | - | nao usado no H7 | - | o red panda tambem nao le VBUS |
| HSE | PH0 / PH1 | HSE_IN / HSE_OUT | 25 MHz | igual | Y1 25 MHz, `clock.h` espera 25 MHz (DIVM=5, N=48 -> 240 MHz) |
| SWDIO / SWCLK | PA13 / PA14 | SWDIO / SWCLK | - | igual | J1 2x5 1,27 mm (NRST no pino 10) |
| BOOT0 | pino 135 | BOOT0 | - | igual | R14 10k pull-down, SW1 para +3V3 |
| straps id1 | PF7, PF8, PF9, PF10 | GND | id1 = 0 (red) | 0 hoje / 4 com PCR-1 | ver secao 4 |
| straps id2 | PD4, PD5, PD6, (PD7) | n.c. | PD4..PD6 n.c. | igual | leitura com pull-up: 1,1,1 ; id2 != 3 => nunca "cuatro" |
| fan, siren, SOM, SPI, bootkick, IR, amp | - | - | `unused_*` | `unused_*` | ausentes na placa (`has_spi=false`, `has_fan=false`) |

Verificacao de funcoes alternativas (DS13311 / RM0468, mesmos pinos do red panda, ja em uso no
firmware upstream): PB8/PB9 FDCAN1 = AF9; PB5/PB6 e PB12/PB13 FDCAN2 = AF9; PG9/PG10 FDCAN3 = AF2;
PA11/PA12 OTG_FS = AF10; PC4 = ADC1_INP4; PA1 = ADC1_INP17; PF11 = ADC1_INP2; PB1 = ADC1_INP5.
Nenhum pino de CAN/USB/ADC esta fora da funcao alternativa necessaria.

Diferencas eletricas em relacao ao red panda que NAO afetam o firmware:
- Transceivers TJA1042TK/3 (red panda usa outro part CAN-FD) - mesma polaridade de STB.
- Alimentacao 12V -> TPS5450 (5V) -> XL1509 (3V3), P-FET Q4 HY12P03C2 com diodo D2/R1 (protecao
  de polaridade), AP22615 para a porta USB-A. Firmware nao controla Q4 nem o enable do XL1509 (EN em GND = sempre ligado).
- MCU STM32H725ZGT6 LQFP144 1 MB flash (red panda: H725 em outro encapsulamento). O linker ja usa FLASH = 1024K e
  app em 0x8020000; o layout de flash e compativel.

## 4. Deteccao de hardware

`board/stm32h7/board.h::detect_board_type()` le dois nibbles com pull-up interno:
`id1 = PF7 | PF8<<1 | PF9<<2 | PF10<<3`, `id2 = PD4 | PD5<<1 | PD6<<2 | PD7<<3`.

| Placa | id1 | id2 | condicao upstream |
|---|---|---|---|
| red panda | 0 (PF7..PF10 em GND) | qualquer | `id1 == 0` |
| red panda v2 (deprecado) | 1 | - | `id1 == 1` -> UNKNOWN |
| tres | 2 (so PF8 aberto) | - | `id1 == 2` |
| cuatro | - | 3 (PD4, PD5 abertos; PD6, PD7 em GND) | `id2 == 3` (testado antes do id1) |
| **Hybrid Panda (novo)** | **4 (so PF9 aberto)** | 7 ou 15 (PD4..PD6 n.c.) | `id1 == 4` |

Evidencia de nao-ambiguidade:
- id2 na Hybrid: PD4, PD5, PD6 sao `n.c.` (lidos como 1), PD7 e BUS2_STB com pull-up R33 10k (lido como 1
  quando a saida ainda nao foi configurada). id2 = 15 (ou 7 se PD7 for lido baixo) != 3 -> nunca cuatro.
- id1 = 4 exige exatamente PF9 aberto e PF7/PF8/PF10 em GND. Red (0) e tres (2) diferem em bits distintos;
  um unico curto/aberto acidental nao converte uma na outra (distancia de Hamming >= 1 bit, mas os valores
  1 e 3 ja estao reservados/invalidos, e 0->4 requer PF9 solto, que e o proprio strap).
- Hoje a PCB tem PF9 em GND (D-08) -> id1 = 0 -> red panda. Isso e funcionalmente correto (secao 3), logo o
  strap e opcional: ele so e necessario para que o host veja a placa como "hybrid" e nao como "red panda".

Implementado em `board/stm32h7/board.h` (ramo `id1 == 4U` -> `HW_TYPE_HYBRID_PANDA`, `&board_hybrid`).

## 5. Esquema de alimentacao do core (VCORE) - veredito

O que a netlist mostra (pinos de sistema do U7):

| Pino | Nome | Rede | Componentes |
|---|---|---|---|
| 14 | VSSSMPS | GND | - |
| 15 | VLXSMPS | VLXSMPS | C41 220 pF, L5 2,2 uH (pino 1) |
| 16 | VDDSMPS | +3V3 | - |
| 17 | VFBSMPS | VFBSMPS | C42 10 uF, L5 (pino 2) |
| 68, 103, 140 | VCAP | VCAP | C39, C40 2,2 uF |
| 70, 105, 143 | VDDLDO | +3V3 | - |
| 142 | PDR_ON | +3V3 | - |

O que o firmware faz (`board/stm32h7/clock.h`, chamado no bootstub e no app, antes de `detect_board_type()`):
`SYSCFG->PKGR` = LQFP144 -> `PACKAGE_WITH_SMPS` -> `PWR->CR3 = SMPSEN` (LDOEN = 0, BYPASS = 0) = "Direct SMPS".
Para TFBGA100 (H723 do tres/cuatro) -> `LDOEN`. O byte baixo de CR3 so pode ser escrito uma vez por power-on.

Requisito do modo Direct SMPS (RM0468 "Supply configuration" / DS13311 esquemas de alimentacao): o VCORE e
fornecido pelo SMPS, portanto **VFBSMPS deve ser ligado externamente aos pinos VCAP**; VDDLDO permanece em VDD.
Na Hybrid Panda `VFBSMPS` e `VCAP` sao redes diferentes -> no modo configurado pelo firmware o LDO esta
desligado e nenhum regulador alimenta VCAP -> **o core nao recebe tensao e o MCU nao arranca**. A D-02
("Direct SMPS") e a lista de componentes (L5, C41, C42) estao corretas, mas falta o link VFBSMPS -> VCAP.

Por que nao da para resolver em tempo de execucao por `hw_type`: `clock_init()` roda antes de qualquer GPIO
(bootstub.c:42-43, main.c:295-298), a escolha LDO/SMPS e o primeiro registrador escrito e e irreversivel ate o
proximo power-on. Upstream distingue red (H725, SMPS) de tres/cuatro (H723, LDO) apenas pelo encapsulamento
(`SYSCFG->PKGR`), nao pelo hw_type. Para uma LQFP144 alimentada por LDO so resta uma escolha em tempo de compilacao.

Opcoes:
1. **PCR-2 (recomendada)**: ligar VFBSMPS a VCAP na PCB (uma trilha ou link 0 ohm). Firmware upstream inalterado,
   binario `panda_h7` padrao (igual ao red panda). C42 10 uF passa a estar em paralelo com C39/C40 na rede VCAP.
2. Fallback firmware (implementado, opcional): alvo `panda_h7_ldo` (`HYBRID_LDO=1 scons`) com `-DPWR_FORCE_LDO`,
   que forca `PWR->CR3 = LDOEN` tambem em LQFP144. Com a PCB atual isso e eletricamente coerente (VDDLDO = 3V3,
   VCAP com 2x 2,2 uF, VDDSMPS = VDD; L5/C42 ficam sem funcao). Limitacoes: bootstub e app tem de vir do mesmo alvo;
   binario incompativel com red panda real; o bootrom DFU da ST pode escrever CR3 antes do bootstub (aviso no
   `clock.h`) - se escrever SMPS, a placa nao enumera em DFU e so pode ser gravada por SWD (J1). Nao testado.

## 6. Alteracoes de firmware (commit a8babfea, branch hybrid-h725)

| Arquivo | Alteracao |
|---|---|
| `board/boards/hybrid.h` (novo) | tabela de pinos no cabecalho; `hybrid_harness_config` (PC4/PA1, PC10/PC11, ADC1 ch4/ch17); `board_hybrid` reutilizando `red_init`, `red_enable_can_transceiver`, `red_set_can_mode`, `red_read_voltage_mV`, LEDs PE4/PE3/PE2; fan/siren/SOM/SPI/IR/amp = `unused_*`, `has_spi=false`, `has_fan=false`, `avdd_mV=3300` |
| `board/boards/board_declarations.h` | `HW_TYPE_HYBRID_PANDA 11U`, `extern struct board board_hybrid` |
| `board/stm32h7/board.h` | include `hybrid.h`; ramo `id1 == 4U` |
| `board/stm32h7/clock.h` | `#ifdef PWR_FORCE_LDO` -> trata como `PACKAGE_WITHOUT_SMPS` |
| `SConscript` | alvo opcional `panda_h7_ldo` quando `HYBRID_LDO` esta no ambiente |
| `python/__init__.py` | `HW_TYPE_HYBRID_PANDA = b'\x0b'`, incluido em `H7_DEVICES`/`SUPPORTED_DEVICES` |

Nao alterados: `tests/misra/*`, `.github/workflows/test.yaml`, `python/constants.py` (nao ha tabela de nomes por HW type).
Reuso das funcoes `red_*`: como todos os pinos coincidem, duplicar `red.h` so criaria divergencia futura; o
`hybrid.h` documenta cada pino e mantem a identidade propria (hw_type, struct, harness config).

## 7. Evidencia de build

Ambiente: Windows, Arm GNU Toolchain 14.2.Rel1 (arm-none-eabi-gcc 14.2.1), SCons 4.11.1, Python 3.13 venv
(`.venv_h`), opendbc local `b0ef909` (editable, `--ignore-requires-python`), helper nao versionado
`local_build_windows.scons` (pula `tests/libpanda`, forca plataforma posix). Flags upstream mantidas (`-Wall -Wextra
-Wstrict-prototypes -Werror -Os`). Unico aviso: `ld: section .data type changed to PROGBITS` (pre-existente).

DEBUG (`HYBRID_LDO=1 scons -f local_build_windows.scons -j8`):

| Saida | bytes |
|---|---|
| board/obj/panda_h7.bin.signed | 69640 |
| board/obj/bootstub.panda_h7.bin | 19920 |
| board/obj/panda_h7_ldo.bin.signed | 69608 |
| board/obj/bootstub.panda_h7_ldo.bin | 19888 |
| board/obj/body_h7.bin.signed | 66368 |

RELEASE=1 (`RELEASE=1 CERT=<debug cert> HYBRID_LDO=1`):

| Saida | bytes |
|---|---|
| board/obj/panda_h7.bin.signed | 67824 |
| board/obj/bootstub.panda_h7.bin | 19884 |
| board/obj/panda_h7_ldo.bin.signed | 67792 |
| board/obj/bootstub.panda_h7_ldo.bin | 19852 |
| board/obj/body_h7.bin.signed | 65208 |

`arm-none-eabi-size` (RELEASE): panda_h7 main.elf text 66448 / data 1216 / bss 433617; bootstub text 18336;
panda_h7_ldo main.elf text 66416. Flash de 1 MB (app a partir de 0x8020000) com folga.

Python: `ruff check python/__init__.py` -> "All checks passed". `mypy python/__init__.py --ignore-missing-imports`
-> 4 erros, identicos antes e depois da alteracao (`spi.py` SPI_DEVICES sem anotacao e `opendbc.INCLUDE_PATH`
nao resolvido pelo stub do mypy; ambiente, nao regressao). cppcheck/MISRA nao disponivel nesta maquina Windows
(`tests/misra/test_misra.sh` nao executado) - o novo codigo segue os padroes dos arquivos vizinhos (sufixo U,
sem funcoes novas, `static` para a config).

## 8. Pedidos de alteracao de PCB (PCR)

| ID | Prioridade | Alteracao | Motivo |
|---|---|---|---|
| PCR-1 | opcional | Retirar PF9 (pino 23) de GND e deixar aberto (ou 0 ohm DNP para GND, com footprint para pull-up 10k opcional) | strap `id1 == 4` -> `HW_TYPE_HYBRID_PANDA`. Sem isso a placa e vista como red panda (funcionalmente correto) |
| PCR-2 | **bloqueante** | Ligar a rede `VFBSMPS` (pino 17, C42) a rede `VCAP` (pinos 68/103/140, C39/C40) | firmware configura Direct SMPS em LQFP144; sem o link o core nao e alimentado. Alternativa: gravar `panda_h7_ldo` via SWD (fallback, nao testado) |
| PCR-3 | informativo | Nenhum pino de CAN/USB/ADC precisa ser movido | todas as funcoes alternativas conferem com o red panda |
| PCR-4 | informativo | Pull-ups: STB (R30-R33), SBU (R23/R24), BOOT0 pull-down (R14), USB EN (R26) presentes; nenhum pull-up em falta identificado | - |

Atualizar `DECISIONS.md` D-02 (Direct SMPS exige VFBSMPS->VCAP) e D-08 (strap PF9) no repositorio HybridPanda
(nao alterado por esta tarefa).

## 9. Alteracoes necessarias do lado openpilot

- `cereal/log.capnp` enum `PandaState.PandaType`: adicionar `hybridPanda @11;` (valores atuais: unknown 0 ... redPanda 7,
  redPandaV2 8, tres 9, cuatro 10). O `python/__init__.py` referencia esse enum.
- `selfdrive/pandad/panda.cc` / `pandad.py`: o tipo e lido do firmware (`get_type`) e convertido para o enum; incluir
  `hybridPanda` onde `redPanda` e tratado (ex.: lista de pandas "com harness", suporte CAN-FD, `is_internal` = false).
  Com PCR-1 nao aplicado nada disso e necessario (placa reportada como redPanda).
- Sem alteracao em `opendbc/safety`.

## 10. O que nao foi testado

- Tudo em hardware: boot/PWR (secao 5), deteccao de id1/id2, enumeracao USB, CAN-FD nos 4 transceivers, harness
  (SBU/relay), LEDs, leitura de 12V/5V, gravacao via DFU e via SWD, bootrom com `PWR_FORCE_LDO`.
- `tests/misra` (cppcheck) e `tests/libpanda` nao executados neste ambiente Windows.
- HITL/CI do upstream nao executados.
