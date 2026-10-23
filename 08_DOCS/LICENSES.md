# LICENSES — inventário de licenças das referências usadas (2026-10-23)

| Fonte | Local | Commit | Licença | Arquivo | Uso neste projeto |
|---|---|---|---|---|---|
| lukasloetkolben/OpenBlackPanda (baseline) | 01_BASELINE\original_copy | (ver manifests) | MIT © 2023 Lukas | LICENSE_OpenBlackPanda.txt | Base do KiCad (schematic/PCB) derivado |
| commaai/panda | 02_REFERENCE\panda | 408e14d4 | MIT © 2016 Comma.ai, Inc. | LICENSE_panda_MIT.txt | Firmware = especificação de hardware; firmware a gravar |
| commaai/panda (full, histórico) | 02_REFERENCE\panda_full ; worktree panda_legacy_f4 @ f849893b | f62adf72 / f849893b | MIT | idem | Controle Black Panda F4 |
| commaai/opendbc | 02_REFERENCE\opendbc | c3955753 | MIT © 2020 Comma.ai, Inc. | LICENSE_opendbc.txt | Confirmação do veículo (P1) |
| commaai/openpilot | 02_REFERENCE\openpilot | ff47f484 | MIT © 2018 Comma.ai, Inc. | openpilot\LICENSE | Software host (pandad, hardware/, Honda) — D-06 |
| ↳ submódulos: opendbc_repo b3bd79a6, msgq_repo a95f3c1c, rednose_repo 8671c17c, teleoprtc_repo 1aa8fc43 | dentro de openpilot | — | MIT | cada repo | análise host |
| ↳ tinygrad_repo | openpilot\tinygrad_repo | 02e69816 | MIT © 2024 the tiny corp | tinygrad_repo\LICENSE | não usado |
| commaai/neo | 02_REFERENCE\neo | 9869dee9 (arquivado) | MIT © 2016 comma.ai | neo\LICENSE.neo | referência histórica de hardware comma |
| commaai/hardware | 02_REFERENCE\hardware | a42a4752 | **Sem arquivo LICENSE**; PDFs do harness v3 trazem "comma.ai — you can copy this!" | — | Pinout OBD-C, harness box, Honda Bosch B (P10). Tratar como "todos os direitos reservados, salvo permissão explícita nos PDFs"; **não redistribuir** os PDFs fora deste projeto |
| commaai/panda_jungle | 02_REFERENCE\panda_jungle | b80539fc (arquivado) | **Sem LICENSE** | — | Consulta apenas |
| commaai/harness_tester_challenge | 02_REFERENCE\harness_tester_challenge | 069f7243 | MIT © 2024 comma.ai | repo LICENSE | Consulta apenas |
| commaai/openpilot-docs | 02_REFERENCE\openpilot-docs | 8a007654 | **Sem LICENSE** | — | Consulta apenas |
| STMicroelectronics DS13311 Rev 5 (STM32H725xE/G) | 02_REFERENCE\datasheets\DS13313_STM32H725_ae.pdf | — | © ST; documento público, redistribuição sujeita aos termos ST | — | Pinagem/AF/elétrica. Não redistribuir o PDF no pacote de fabricação; citar número do documento |

## Obrigações
- Projetos derivados do baseline (04_PROJECT) devem manter o aviso MIT de Lukas (2023) e adicionar o próprio aviso.
- Firmware gravado = commaai/panda MIT: manter aviso; nenhuma modificação prevista (política: firmware oficial sem alteração).
- Chaves: `board/crypto/certs/debug` é pública (MIT); a chave release **não** é pública — ver HRS §7 (RESTRIÇÃO).

## Nota sobre Git LFS (openpilot)
`.lfsconfig` do openpilot aponta para `https://huggingface.co/commaai/openpilot-lfs.git` que responde 403 a clientes anônimos. O clone foi feito com `GIT_LFS_SKIP_SMUDGE=1` + `filter.lfs.smudge --skip`; 253 arquivos LFS (imagens, binários, modelos) ficaram como ponteiros. Nenhum deles é necessário para a análise de hardware/host (código-fonte é 100 % texto normal). Registrado em D-10.
