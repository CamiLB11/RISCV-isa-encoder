# Resultados de validación

La siguiente tabla muestra la comparación entre la codificación generada por la herramienta desarrollada y la obtenida mediante el toolchain oficial de RISC-V.

El ensamblado de referencia se realizó utilizando `riscv64-unknown-elf-as` con `-march=rv32i` y `-mabi=ilp32`, y posteriormente se obtuvo la codificación mediante `riscv64-unknown-elf-objdump -d`.

| # | Instrucción | Encoder propio | Toolchain | Resultado |
|---:|---|---|---|---|
| 1 | `add x1, x2, x3` | `0x003100b3` | `0x003100b3` | OK |
| 2 | `add x10, x0, x31` | `0x01f00533` | `0x01f00533` | OK |
| 3 | `add x31, x31, x1` | `0x001f8fb3` | `0x001f8fb3` | OK |
| 4 | `sub x1, x2, x3` | `0x403100b3` | `0x403100b3` | OK |
| 5 | `sub x15, x20, x5` | `0x405a07b3` | `0x405a07b3` | OK |
| 6 | `sub x30, x0, x31` | `0x41f00f33` | `0x41f00f33` | OK |
| 7 | `and x1, x2, x3` | `0x003170b3` | `0x003170b3` | OK |
| 8 | `and x10, x15, x20` | `0x0147f533` | `0x0147f533` | OK |
| 9 | `and x31, x0, x31` | `0x01f07fb3` | `0x01f07fb3` | OK |
| 10 | `or x1, x2, x3` | `0x003160b3` | `0x003160b3` | OK |
| 11 | `or x12, x8, x25` | `0x01946633` | `0x01946633` | OK |
| 12 | `or x31, x31, x0` | `0x000fefb3` | `0x000fefb3` | OK |
| 13 | `addi x1, x2, 100` | `0x06410093` | `0x06410093` | OK |
| 14 | `addi x10, x5, -100` | `0xf9c28513` | `0xf9c28513` | OK |
| 15 | `addi x31, x0, 2047` | `0x7ff00f93` | `0x7ff00f93` | OK |
| 16 | `andi x1, x2, 255` | `0x0ff17093` | `0x0ff17093` | OK |
| 17 | `andi x15, x20, -500` | `0xe0ca7793` | `0xe0ca7793` | OK |
| 18 | `andi x31, x31, -2048` | `0x800fff93` | `0x800fff93` | OK |
| 19 | `lw x1, 100(x2)` | `0x06412083` | `0x06412083` | OK |
| 20 | `lw x10, -100(x5)` | `0xf9c2a503` | `0xf9c2a503` | OK |
| 21 | `lw x31, 2047(x0)` | `0x7ff02f83` | `0x7ff02f83` | OK |
| 22 | `lb x1, 50(x2)` | `0x03210083` | `0x03210083` | OK |
| 23 | `lb x20, -500(x10)` | `0xe0c50a03` | `0xe0c50a03` | OK |
| 24 | `lb x31, -2048(x31)` | `0x800f8f83` | `0x800f8f83` | OK |
| 25 | `sw x1, 100(x2)` | `0x06112223` | `0x06112223` | OK |
| 26 | `sw x10, -100(x5)` | `0xf8a2ae23` | `0xf8a2ae23` | OK |
| 27 | `sw x31, 2047(x0)` | `0x7ff02fa3` | `0x7ff02fa3` | OK |
| 28 | `sb x1, 50(x2)` | `0x02110923` | `0x02110923` | OK |
| 29 | `sb x20, -500(x10)` | `0xe1450623` | `0xe1450623` | OK |
| 30 | `sb x31, -2048(x31)` | `0x81ff8023` | `0x81ff8023` | OK |
| 31 | `beq x1, x2, 8` | `0x00208463` | `0x00208463` | OK |
| 32 | `beq x10, x5, -16` | `0xfe5508e3` | `0xfe5508e3` | OK |
| 33 | `beq x31, x0, 4094` | `0x7e0f8fe3` | `0x7e0f8fe3` | OK |
| 34 | `bne x1, x2, 16` | `0x00209863` | `0x00209863` | OK |
| 35 | `bne x20, x10, -32` | `0xfeaa10e3` | `0xfeaa10e3` | OK |
| 36 | `bne x31, x31, -4096` | `0x81ff9063` | `0x81ff9063` | OK |

## Resumen

- Total de casos: 36
- Casos correctos: 36
- Casos incorrectos: 0

Los 36 casos de prueba coincidieron con la codificación obtenida mediante el toolchain oficial de RISC-V.
