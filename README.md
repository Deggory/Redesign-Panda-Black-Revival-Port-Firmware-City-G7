> **Development history repository.** This repository is kept as the raw working tree of the project (numbered folders, process manifests).
> The organized release repository, with the same content under a clean layout, submodules and a full README, is
> **https://github.com/kriptomad/openpilot-honda-city-brasil** - use that one.
>
> Repositorio de historico de desenvolvimento. A versao organizada (release) esta em https://github.com/kriptomad/openpilot-honda-city-brasil.

# Redesign Panda Black Revival + Port Firmware City G7

Projeto de Bruno Costa (kriptomad): manter a panda preta (STM32F4) viva e levar o Honda City G7 2023 (Brasil)
para o openpilot/flowpilot, mais o redesenho da placa com STM32H725 (Hybrid Panda, CAN-FD).
Nada foi validado em hardware ou no carro ate agora. Documentacao em PT-BR (ASCII).

## Onde esta cada coisa

| Frente | Repositorio / branch | Estado |
|---|---|---|
| Placa Hybrid Panda (KiCad 10, STM32H725ZGT6 LQFP144) | este repo, `04_PROJECT/HybridPanda/` | DRC 0 clearance / 0 unconnected; correcoes dos audits em andamento (passos 1-3 de 5 aplicados, ver `06_REPORTS/corr/RESUME_STEP3.md`) |
| Firmware panda para a Hybrid Panda (target `panda_h7_hybrid`) | [kriptomad/panda@hybrid-h725](https://github.com/kriptomad/panda/tree/hybrid-h725) | compila RELEASE/DEBUG, MISRA 0; relatorio em `03_RESEARCH/HYBRID_FW_PORT.md` |
| Panda preta (F4) no panda master atual (pandarevive) | [kriptomad/panda@revive-f4](https://github.com/kriptomad/panda/tree/revive-f4) | test.sh verde; escopo em `03_RESEARCH/PANDAREVIVE_SCOPE.md` |
| City G7 no openpilot v0.9.9 (ultima release com panda preta) | [kriptomad/openpilot@v0.9.9-cityg7-blackpanda](https://github.com/kriptomad/openpilot/tree/v0.9.9-cityg7-blackpanda) + [kriptomad/opendbc@firmwarecityg7-v0.9.9](https://github.com/kriptomad/opendbc/tree/firmwarecityg7-v0.9.9) | port completo, 2 auditorias, CI verde no fork; docs em `09_FIRMWARECITYG7_BLACKPANDA/` |
| City G7 no flowpilot (APK standalone, Poco F3) | [kriptomad/flowpilot-city-g7@flowpilot-city-g7-brazil](https://github.com/kriptomad/flowpilot-city-g7/tree/flowpilot-city-g7-brazil) | port feito, firmware F4 compilado; APK via GitHub Actions; docs em `10_FLOWPILOT/` |

## Pastas deste repo

- `01_INPUTS/`, `02_REFERENCE/` - referencias originais (red/black panda, datasheets).
- `03_RESEARCH/` - pesquisa, decisoes, relatorios de firmware (`HYBRID_FW_PORT.md`, `PANDAREVIVE_SCOPE.md`).
- `04_PROJECT/HybridPanda/` - esquematico e PCB KiCad.
- `05_SCRIPTS/` - scripts de geracao, verificacao e correcao (KiCad python, DRC gate).
- `06_REPORTS/` - auditorias (SI/PI, footprint vs datasheet, BOM com pecas reais), DRC/ERC, correcoes.
- `09_FIRMWARECITYG7_BLACKPANDA/` - port do City para v0.9.9: LEIA-ME, auditorias, patches `git format-patch`, tools.
  Guia de gravacao da panda preta (placa do Lukas, DFU, 3 arvores de firmware): `FLASH_BLACK_PANDA_CITY_G7.md` (EN) / `.pt-BR.md`; binarios `revive-f4` em `panda_fw_out_revive_f4/`.
- `10_FLOWPILOT/` - escopo, relatorio do port, firmware F4 do flowpilot (`panda_fw_out/`), shims de teste Windows.

Espelho historico: [kriptomad/PandaH7Openpilot](https://github.com/kriptomad/PandaH7Openpilot).
