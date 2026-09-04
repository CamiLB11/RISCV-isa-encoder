# Codificador Educativo de Instrucciones RISC-V RV32I

## Descripción

Este proyecto consiste en el desarrollo de un codificador educativo para un subconjunto de instrucciones de la arquitectura RISC-V RV32I. La herramienta recibe una instrucción escrita en ensamblador y genera su representación de 32 bits tanto en binario como en hexadecimal.

Además de obtener la codificación, el programa muestra cómo se distribuyen los bits de acuerdo con el formato de la instrucción. La idea es que la salida no muestre únicamente el resultado final, sino que también permita visualizar los campos que forman la instrucción y entender qué representa cada uno.

El programa fue desarrollado en Python y se ejecuta desde la terminal mediante el archivo `run.sh`.

## Instrucciones soportadas

El codificador trabaja con 12 instrucciones de RV32I, distribuidas en cuatro formatos.

| Formato | Instrucciones |
|---|---|
| R | `add`, `sub`, `and`, `or` |
| I | `addi`, `andi`, `lw`, `lb` |
| S | `sw`, `sb` |
| B | `beq`, `bne` |

En total se implementaron:

- 4 instrucciones de formato R.
- 4 instrucciones de formato I.
- 2 instrucciones de formato S.
- 2 instrucciones de formato B.

## Estructura del proyecto

Los principales archivos del proyecto son:

```text
.
├── encoder_skeleton.py
├── run.sh
├── casos_prueba.txt
├── vectores_ejemplo.txt
├── validar.py
├── resultados_validacion.md
└── README.md
```

### `encoder_skeleton.py`

Contiene la implementación principal del codificador. Se encarga de interpretar la instrucción recibida, identificar su formato, validar los operandos y construir la palabra de 32 bits. También genera la salida educativa donde se muestran los campos de la instrucción, sus posiciones y sus valores.

### `run.sh`

Es el punto de entrada del programa. Recibe una instrucción como único argumento y ejecuta el codificador desarrollado en Python.

### `vectores_ejemplo.txt`

Contiene los vectores proporcionados con el proyecto. Se utilizaron como una primera comprobación del funcionamiento del codificador.

### `casos_prueba.txt`

Contiene 36 casos de prueba propios: tres casos diferentes para cada una de las 12 instrucciones implementadas.

### `validar.py`

Automatiza la validación de los casos propios. Para cada instrucción compara el resultado producido por el codificador con la codificación obtenida utilizando el toolchain de RISC-V.

### `resultados_validacion.md`

Contiene la evidencia de la comparación de los 36 casos de prueba contra el toolchain.

---

## Requisitos

Para ejecutar el codificador se necesita:

- Python 3.
- Bash.
- Un sistema Linux o WSL en Windows.

Para realizar la validación también se necesita el toolchain de RISC-V con:

- `riscv64-unknown-elf-as`
- `riscv64-unknown-elf-objdump`

El proyecto fue desarrollado y probado utilizando WSL con Ubuntu.

## Instalación del toolchain

En Ubuntu o WSL se puede instalar el toolchain utilizado para las pruebas con:

```bash
sudo apt update
sudo apt install gcc-riscv64-unknown-elf binutils-riscv64-unknown-elf
```

Se puede comprobar la instalación con:

```bash
riscv64-unknown-elf-gcc --version
```

Para las pruebas del proyecto el assembler se ejecuta específicamente para RV32I utilizando:

```bash
-march=rv32i -mabi=ilp32
```

## Preparación y ejecución del codificador

Primero se debe dar permiso de ejecución al archivo `run.sh` en caso de que sea necesario:

```bash
chmod +x run.sh
```

La herramienta se ejecuta de la siguiente manera:

```bash
./run.sh "<instruccion>"
```

Por ejemplo:

```bash
./run.sh "add x5, x6, x7"
```

La salida incluye:

- Formato de la instrucción.
- Representación binaria de 32 bits.
- Distribución visual de los campos.
- Valor de cada campo.
- Explicación de los campos.
- Representación hexadecimal.

Al final de cada ejecución se imprime una línea con el formato:

```text
HEX: 0xXXXXXXXX
```

Esta línea permite obtener fácilmente el resultado para realizar pruebas automáticas.

---

# Formatos implementados

## Formato R

El formato R se utiliza en este proyecto para:

- `add`
- `sub`
- `and`
- `or`

Su distribución es:

```text
31        25 24    20 19    15 14  12 11     7 6       0
+-----------+--------+--------+------+---------+---------+
|  funct7   |  rs2   |  rs1   |funct3|   rd   | opcode  |
+-----------+--------+--------+------+---------+---------+
```

Los campos `rs1` y `rs2` indican los registros fuente y `rd` corresponde al registro destino. Los campos `funct3` y `funct7`, junto con el `opcode`, permiten determinar la operación que se debe realizar.

### Ejemplo formato R

```bash
./run.sh "add x5, x6, x7"
```

Resultado:

```text
Formato: R
Binario: 00000000011100110000001010110011
HEX: 0x007302b3
```

---

## Formato I

En el proyecto se utiliza el formato I para instrucciones aritméticas y de carga:

- `addi`
- `andi`
- `lw`
- `lb`

Su distribución es:

```text
31                    20 19    15 14  12 11     7 6       0
+-----------------------+--------+------+---------+---------+
|       imm[11:0]       |  rs1   |funct3|   rd   | opcode  |
+-----------------------+--------+------+---------+---------+
```

El inmediato ocupa 12 bits. En el programa se valida que se encuentre dentro del rango permitido y, cuando es negativo, se representa utilizando complemento a dos.

En las instrucciones `lw` y `lb`, el inmediato funciona como desplazamiento con respecto al registro base.

### Ejemplo formato I

```bash
./run.sh "addi x10, x5, -100"
```

Resultado:

```text
Formato: I
Binario: 11111001110000101000010100010011
HEX: 0xf9c28513
```

---

## Formato S

El formato S se utiliza para:

- `sw`
- `sb`

Su distribución es:

```text
31        25 24    20 19    15 14  12 11      7 6       0
+-----------+--------+--------+------+----------+---------+
| imm[11:5] |  rs2   |  rs1   |funct3| imm[4:0] | opcode |
+-----------+--------+--------+------+----------+---------+
```

A diferencia del formato I, el inmediato no se encuentra en un único bloque. Los bits `imm[11:5]` se colocan en la parte superior de la instrucción y `imm[4:0]` se colocan entre `funct3` y `opcode`.

### Ejemplo formato S

```bash
./run.sh "sw x10, -100(x5)"
```

Resultado:

```text
Formato: S
Binario: 11111000101000101010111000100011
HEX: 0xf8a2ae23
```

---

## Formato B

El formato B se utiliza para las instrucciones de salto condicional:

- `beq`
- `bne`

La distribución del inmediato es diferente a los demás formatos:

```text
31          30      25 24    20 19    15 14  12 11       8 7       6      0
+-------------+--------+--------+--------+------+-----------+--------+--------+
|   imm[12]   |imm[10:5]|  rs2  |  rs1   |funct3| imm[4:1] | imm[11]| opcode |
+-------------+--------+--------+--------+------+-----------+--------+--------+
```

El bit 0 del desplazamiento no se almacena en la instrucción, por lo que el programa verifica que el desplazamiento utilizado sea par.

Para inmediatos negativos se utiliza su representación en complemento a dos antes de separar los bits correspondientes.

### Ejemplo formato B

```bash
./run.sh "beq x10, x5, -16"
```

Resultado:

```text
Formato: B
Binario: 11111110010101010000100011100011
HEX: 0xfe5508e3
```

---

# Obtención de los campos de codificación

Los valores de `opcode`, `funct3` y `funct7` utilizados para implementar las instrucciones fueron obtenidos de la documentación de la arquitectura RISC-V.

Cada instrucción se identifica utilizando una combinación de estos campos. Por ejemplo, las instrucciones `add` y `sub` utilizan el mismo `opcode` y `funct3`, pero se diferencian mediante el valor de `funct7`.

La implementación utiliza estos valores para construir la palabra de 32 bits mediante operaciones de desplazamiento y combinación de bits.

La referencia principal utilizada fue:

> RISC-V International. *The RISC-V Instruction Set Manual, Volume I: Unprivileged ISA.*

La documentación oficial se encuentra disponible en el sitio de RISC-V International.

---

# Validación

Para comprobar el funcionamiento del codificador se realizaron dos etapas de pruebas.

## Vectores proporcionados

Primero se ejecutaron los 36 vectores incluidos en `vectores_ejemplo.txt`.

Los resultados obtenidos por el programa coincidieron con los valores esperados en los 36 casos.

```text
36/36 vectores correctos
```

## Casos de prueba propios

Además se crearon 36 casos de prueba propios, correspondientes a tres casos para cada una de las 12 instrucciones.

En estos casos se utilizaron:

- Diferentes registros.
- Inmediatos positivos.
- Inmediatos negativos.
- Valores cercanos o iguales a los límites permitidos.

Para evitar validar el programa utilizando sus propios resultados, cada caso se ensambló independientemente utilizando:

```text
riscv64-unknown-elf-as
```

y posteriormente se obtuvo la codificación mediante:

```text
riscv64-unknown-elf-objdump -d
```

El script `validar.py` automatiza este proceso y compara ambas codificaciones.

Se ejecuta con:

```bash
python3 validar.py
```

El resultado final obtenido fue:

```text
Total de casos : 36
Correctos      : 36
Incorrectos    : 0

RESULTADO FINAL: 36/36 CASOS COINCIDEN CON EL TOOLCHAIN OFICIAL.
```

La tabla completa de resultados se encuentra en `resultados_validacion.md`.

Durante la validación también fue necesario considerar que `objdump` puede mostrar algunas instrucciones mediante alias, por ejemplo `neg`, `li`, `zext.b` o `beqz`. Por esta razón, la comparación utiliza directamente la codificación obtenida en la dirección correspondiente y no depende únicamente del nombre mostrado por el desensamblador.

Para las instrucciones de formato B se utilizaron etiquetas locales para generar exactamente el desplazamiento que se quería comprobar.

---

# Manejo de errores

El codificador incluye validaciones para evitar generar instrucciones incorrectas. Entre ellas se encuentran:

- Registros fuera del rango `x0` a `x31`.
- Instrucciones no soportadas.
- Cantidad o formato incorrecto de operandos.
- Inmediatos fuera del rango permitido.
- Desplazamientos impares en instrucciones de formato B.

Cuando se detecta una entrada inválida, el programa muestra un mensaje de error en lugar de generar una codificación incorrecta.

---

# Referencias

RISC-V International. *The RISC-V Instruction Set Manual, Volume I: Unprivileged ISA.*

Waterman, A., & Asanović, K. *The RISC-V Instruction Set Manual, Volume I: User-Level ISA.*

Documentación y material proporcionado para el proyecto individual del curso CE-4301 Arquitectura de Computadores I.