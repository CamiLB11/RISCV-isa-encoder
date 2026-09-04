# Documentación técnica
## Codificador Educativo de Instrucciones RISC-V RV32I

**Curso:** CE-4301 Arquitectura de Computadores I  
**Proyecto:** Codificador Educativo de Instrucciones RISC-V  
**Estudiante:** Camila Lizano Brenes  

---

## 1. Introducción

El objetivo de este proyecto fue implementar un codificador para un subconjunto de instrucciones de RISC-V RV32I. El programa recibe una instrucción escrita de forma similar a ensamblador y construye su representación binaria de 32 bits y su valor hexadecimal.

Además de realizar la codificación, se buscó que la herramienta fuera educativa. Por esta razón, no solamente se muestra la palabra final, sino también la separación de sus campos y una explicación de qué representa cada uno.

Se implementaron los formatos R, I, S y B. Para comprobar que la construcción de los bits fuera correcta, los resultados del programa se compararon con los obtenidos utilizando el assembler y `objdump` del toolchain de RISC-V.

---

## 2. Instrucciones implementadas

El proyecto implementa las 12 instrucciones indicadas en la especificación.

| Categoría | Formato | Instrucciones |
|---|---|---|
| Aritmética registro-registro | R | `add`, `sub`, `and`, `or` |
| Aritmética con inmediato | I | `addi`, `andi` |
| Carga desde memoria | I | `lw`, `lb` |
| Almacenamiento en memoria | S | `sw`, `sb` |
| Saltos condicionales | B | `beq`, `bne` |

Cada instrucción se identifica mediante su `opcode` y, dependiendo del caso, mediante `funct3` y `funct7`.

---

# 3. Arquitectura de la solución

La solución se desarrolló en Python. Se mantuvo `run.sh` como punto de entrada para respetar el formato de ejecución solicitado en la especificación.

Los archivos principales utilizados son:

```text
run.sh
    |
    v
encoder_skeleton.py
    |
    +--> lectura y separación de la instrucción
    |
    +--> validación de registros e inmediatos
    |
    +--> identificación del formato
    |
    +--> codificación R / I / S / B
    |
    +--> construcción de la palabra de 32 bits
    |
    +--> explicación visual
    |
    +--> BINARIO + HEX
```

Para las pruebas se agregaron además:

```text
casos_prueba.txt
        |
        v
    validar.py
       /   \
      /     \
     v       v
 ./run.sh   RISC-V assembler
     |            |
     v            v
Encoder        objdump
     \            /
      \          /
       v        v
        Comparación
            |
            v
resultados_validacion.md
```

Esta separación permitió mantener la codificación independiente del proceso de validación. Esto era importante porque no tendría sentido utilizar la salida del mismo encoder como valor esperado para comprobar si el encoder era correcto.

---

## 3.1 Punto de entrada: `run.sh`

El archivo `run.sh` funciona como único punto de entrada del proyecto.

La ejecución se realiza de la forma:

```bash
./run.sh "<instruccion>"
```

Por ejemplo:

```bash
./run.sh "add x5, x6, x7"
```

El script verifica que se haya recibido exactamente un argumento y posteriormente ejecuta `encoder_skeleton.py`, enviándole la instrucción.

Se utilizó este archivo como intermediario para que la forma de ejecutar el proyecto no dependa directamente del nombre del archivo Python.

---

## 3.2 Programa principal: `encoder_skeleton.py`

Este archivo contiene la lógica principal del codificador.

El procesamiento general de una instrucción sigue estos pasos:

1. Se recibe la instrucción como texto.
2. Se identifica el mnemónico.
3. Se verifica que la instrucción esté dentro de las 12 soportadas.
4. Se separan y procesan los operandos.
5. Se validan los registros y los inmediatos.
6. Se determina el formato de la instrucción.
7. Se construyen los campos correspondientes.
8. Los campos se colocan en sus posiciones dentro de una palabra de 32 bits.
9. Se genera la explicación visual.
10. Se imprime el resultado binario y hexadecimal.

---

# 4. Funciones y módulos principales

## 4.1 Tabla de instrucciones

La información necesaria para diferenciar las instrucciones se almacena en una estructura que contiene el formato, `opcode`, `funct3` y `funct7` cuando corresponde.

Esto evita tener los valores de codificación repetidos en distintas partes del programa y permite que la función principal consulte la información necesaria dependiendo del mnemónico recibido.

Por ejemplo, las instrucciones `add` y `sub` tienen el mismo `opcode` y `funct3`, pero se diferencian por `funct7`.

---

## 4.2 Procesamiento de registros

La función encargada de los registros recibe valores escritos como:

```text
x0
x5
x17
x31
```

Se verifica primero que tengan el formato correcto y posteriormente que el número se encuentre entre 0 y 31.

Esto es necesario porque RV32I posee 32 registros enteros y cada identificador de registro ocupa 5 bits dentro de la instrucción.

Por ejemplo:

```text
x5 = 00101
x6 = 00110
x31 = 11111
```

Si se recibe un registro fuera del rango permitido, el programa genera un error en lugar de producir una codificación incorrecta.

---

## 4.3 Procesamiento de inmediatos

Las instrucciones de formato I y S utilizan inmediatos de 12 bits con signo.

El rango utilizado es:

```text
-2048 a 2047
```

Cuando el inmediato es negativo se obtiene su representación en complemento a dos antes de colocarlo dentro de la palabra.

Por ejemplo, para un campo de 12 bits:

```text
-1 = 111111111111
```

En el formato B el desplazamiento tiene una distribución diferente y debe ser un valor par, debido a que el bit menos significativo no se almacena directamente en la instrucción.

---

## 4.4 Codificación de formato R

Las instrucciones implementadas en este formato son:

```text
add
sub
and
or
```

La estructura utilizada es:

```text
31        25 24    20 19    15 14    12 11     7 6       0
+-----------+--------+--------+---------+---------+---------+
|  funct7   |  rs2   |  rs1   | funct3  |   rd    | opcode |
+-----------+--------+--------+---------+---------+---------+
```

Para construir la palabra se colocan los campos en sus posiciones correspondientes:

```text
funct7 -> bits 31:25
rs2    -> bits 24:20
rs1    -> bits 19:15
funct3 -> bits 14:12
rd     -> bits 11:7
opcode -> bits 6:0
```

La implementación utiliza desplazamientos de bits y operaciones OR para unir los campos.

Conceptualmente, la construcción corresponde a:

```text
(funct7 << 25)
| (rs2 << 20)
| (rs1 << 15)
| (funct3 << 12)
| (rd << 7)
| opcode
```

---

## 4.5 Codificación de formato I

Las instrucciones de formato I implementadas son:

```text
addi
andi
lw
lb
```

La estructura es:

```text
31                    20 19    15 14    12 11     7 6       0
+-----------------------+--------+---------+---------+---------+
|       imm[11:0]       |  rs1   | funct3  |   rd    | opcode |
+-----------------------+--------+---------+---------+---------+
```

En `addi` y `andi` los operandos tienen la forma:

```text
rd, rs1, inmediato
```

Por ejemplo:

```text
addi x10, x5, -100
```

Para `lw` y `lb` se utiliza la forma:

```text
rd, inmediato(rs1)
```

Por ejemplo:

```text
lw x10, -100(x5)
```

Aunque la sintaxis de entrada cambia, ambos casos terminan construyendo una instrucción de formato I.

---

## 4.6 Codificación de formato S

Las instrucciones implementadas son:

```text
sw
sb
```

Su estructura es:

```text
31        25 24    20 19    15 14    12 11       7 6       0
+-----------+--------+--------+---------+-----------+---------+
| imm[11:5] |  rs2   |  rs1   | funct3  | imm[4:0] | opcode |
+-----------+--------+--------+---------+-----------+---------+
```

En este formato el inmediato se divide en dos partes.

Los bits superiores:

```text
imm[11:5]
```

se colocan en los bits 31 a 25, mientras que:

```text
imm[4:0]
```

se colocan en los bits 11 a 7.

Esto fue una diferencia importante con respecto al formato I, ya que el inmediato no se puede colocar directamente como un único campo.

---

## 4.7 Codificación de formato B

Las instrucciones implementadas son:

```text
beq
bne
```

La distribución utilizada es:

```text
31       30      25 24    20 19    15 14    12 11  8 7       6      0
+----------+--------+--------+--------+---------+------+--------+--------+
| imm[12]  |imm[10:5]| rs2   | rs1    | funct3  |imm[4:1]|imm[11]|opcode|
+----------+--------+--------+--------+---------+------+--------+--------+
```

Este fue el formato que requirió más cuidado porque los bits del inmediato no aparecen consecutivamente en la palabra.

La distribución utilizada fue:

```text
imm[12]   -> bit 31
imm[10:5] -> bits 30:25
imm[4:1]  -> bits 11:8
imm[11]   -> bit 7
```

El bit `imm[0]` no se almacena, por lo que el programa comprueba que el desplazamiento sea par.

El rango implementado para el desplazamiento es:

```text
-4096 a 4094
```

También se utiliza complemento a dos para representar desplazamientos negativos.

---

# 5. Campos de codificación utilizados

Los valores utilizados para las instrucciones son los siguientes:

| Instrucción | Formato | Opcode | funct3 | funct7 |
|---|---|---|---|---|
| `add`  | R | `0110011` | `000` | `0000000` |
| `sub`  | R | `0110011` | `000` | `0100000` |
| `and`  | R | `0110011` | `111` | `0000000` |
| `or`   | R | `0110011` | `110` | `0000000` |
| `addi` | I | `0010011` | `000` | No aplica |
| `andi` | I | `0010011` | `111` | No aplica |
| `lw`   | I | `0000011` | `010` | No aplica |
| `lb`   | I | `0000011` | `000` | No aplica |
| `sw`   | S | `0100011` | `010` | No aplica |
| `sb`   | S | `0100011` | `000` | No aplica |
| `beq`  | B | `1100011` | `000` | No aplica |
| `bne`  | B | `1100011` | `001` | No aplica |

Estos campos fueron consultados en el manual oficial de RISC-V y posteriormente se verificaron de forma práctica ensamblando instrucciones con el toolchain.

---

# 6. Decisiones de diseño

Durante la implementación tomé varias decisiones para mantener el programa sencillo y al mismo tiempo cumplir con el objetivo educativo del proyecto.

### Separar la codificación según el formato

En lugar de construir todas las instrucciones dentro de una sola función, se separó la lógica de los formatos R, I, S y B. Esto facilita entender qué campos utiliza cada tipo de instrucción y evita repetir operaciones.

### Mantener una tabla con los datos de las instrucciones

Los valores de `opcode`, `funct3` y `funct7` se almacenan como datos asociados a cada instrucción. De esta manera, la lógica para construir un formato no depende de tener una cadena grande de condiciones diferentes para cada mnemónico.

### Validar antes de codificar

Los registros, inmediatos y operandos se validan antes de construir la palabra final. Preferí generar un error ante una entrada inválida en lugar de truncar un valor y producir una codificación que podría parecer válida.

### Utilizar operaciones de bits

La palabra final se construye utilizando desplazamientos y OR a nivel de bits. Consideré que esta forma representa mejor lo que ocurre con los campos de una instrucción que construir primero una cadena de caracteres binarios.

### Separar el encoder de la validación

`validar.py` no forma parte del proceso normal de codificación. Su función es comprobar de forma independiente los resultados utilizando herramientas externas.

Esto permite tener dos caminos distintos:

```text
Instrucción -> encoder propio -> hexadecimal

Instrucción -> assembler -> objdump -> hexadecimal
```

y después comparar ambos resultados.

---

# 7. Salida educativa

La salida fue diseñada para que se pueda observar la codificación y no solamente el hexadecimal final.

Para cada instrucción se muestra:

- Instrucción recibida.
- Formato identificado.
- Palabra binaria de 32 bits.
- Separación visual de los campos.
- Posiciones de bits.
- Valores de registros e inmediatos.
- Explicación del propósito de cada campo.
- Palabra hexadecimal.
- Línea `HEX: 0xXXXXXXXX` para procesamiento automático.

A continuación se muestran ejemplos de los cuatro formatos.

---

## 7.1 Ejemplo de formato R

Entrada:

```bash
./run.sh "add x5, x6, x7"
```

Resultado principal:

```text
Instrucción : add x5, x6, x7
Formato     : R
BINARIO     : 00000000011100110000001010110011

funct7 [31:25] = 0000000
rs2    [24:20] = 00111 (x7)
rs1    [19:15] = 00110 (x6)
funct3 [14:12] = 000
rd      [11:7] = 00101 (x5)
opcode   [6:0] = 0110011

Palabra hexadecimal: 0x007302b3
HEX: 0x007302b3
```

En este caso `x6` y `x7` son los registros fuente y `x5` es el registro donde se almacena el resultado.

---

## 7.2 Ejemplo de formato I

Entrada:

```bash
./run.sh "addi x10, x5, -100"
```

Resultado principal:

```text
Instrucción : addi x10, x5, -100
Formato     : I
BINARIO     : 11111001110000101000010100010011

imm[11:0] = 111110011100 (-100)
rs1       = x5
funct3    = 000
rd        = x10
opcode    = 0010011

Palabra hexadecimal: 0xf9c28513
HEX: 0xf9c28513
```

Este ejemplo también permite comprobar el tratamiento de un inmediato negativo.

---

## 7.3 Ejemplo de formato S

Entrada:

```bash
./run.sh "sw x10, -100(x5)"
```

Resultado principal:

```text
Instrucción : sw x10, -100(x5)
Formato     : S
BINARIO     : 11111000101000101010111000100011

imm[11:5] = 1111100
rs2       = x10
rs1       = x5
funct3    = 010
imm[4:0]  = 11100
opcode    = 0100011

Palabra hexadecimal: 0xf8a2ae23
HEX: 0xf8a2ae23
```

Aquí se puede observar cómo el inmediato `-100` queda separado en dos campos diferentes.

---

## 7.4 Ejemplo de formato B

Entrada:

```bash
./run.sh "beq x10, x5, -16"
```

Resultado principal:

```text
Instrucción : beq x10, x5, -16
Formato     : B
BINARIO     : 11111110010101010000100011100011

imm[12]   = 1
imm[10:5] = 111111
rs2       = x5
rs1       = x10
funct3    = 000
imm[4:1]  = 1000
imm[11]   = 1
opcode    = 1100011

Palabra hexadecimal: 0xfe5508e3
HEX: 0xfe5508e3
```

En este caso el desplazamiento es negativo y sus bits deben colocarse en diferentes partes de la instrucción.

---

# 8. Validación contra el toolchain oficial

Para comprobar el funcionamiento no utilicé solamente los resultados generados por mi propio programa. Se utilizó un toolchain de RISC-V como referencia independiente.

Las herramientas utilizadas fueron:

```text
riscv64-unknown-elf-as
riscv64-unknown-elf-objdump
```

El assembler se configuró para generar código RV32I mediante:

```bash
-march=rv32i -mabi=ilp32
```

La validación se realizó utilizando `validar.py`.

Para cada caso, el script:

1. Lee una instrucción de `casos_prueba.txt`.
2. Ejecuta el codificador mediante `run.sh`.
3. Obtiene la línea `HEX:` generada por el programa.
4. Crea un archivo assembly temporal.
5. Lo ensambla como RV32I.
6. Ejecuta `objdump -d`.
7. Extrae la palabra hexadecimal obtenida por el toolchain.
8. Compara ambos resultados.

Se crearon 36 casos propios, correspondientes a tres casos por cada una de las 12 instrucciones.

Los casos incluyen distintos registros y, cuando corresponde, inmediatos positivos, negativos y valores límite.

El resultado final fue:

```text
Total de casos : 36
Correctos      : 36
Incorrectos    : 0

RESULTADO FINAL: 36/36 CASOS COINCIDEN CON EL TOOLCHAIN OFICIAL.
```

La tabla completa se encuentra en:

```text
resultados_validacion.md
```

Además, antes de realizar esta validación se probaron los 36 vectores incluidos en `vectores_ejemplo.txt`, obteniendo también:

```text
36/36 casos correctos
```

---

## 8.1 Consideraciones encontradas durante la validación

Durante las pruebas encontré dos detalles con `objdump` que fue necesario tomar en cuenta.

El primero apareció con las instrucciones de branch. Al utilizar directamente un número como destino, el assembler podía manejarlo como un destino/reubicación y la salida no era adecuada para comparar directamente el desplazamiento que esperaba el encoder.

Para resolverlo, en la validación de `beq` y `bne` se generan etiquetas locales ubicadas a la distancia indicada por el inmediato. De esta manera se puede comprobar exactamente el desplazamiento que se desea probar.

El segundo detalle fue que `objdump` puede mostrar algunas codificaciones utilizando alias. Por ejemplo, durante las pruebas aparecieron:

```text
sub  -> neg
addi -> li
andi -> zext.b
beq  -> beqz
```

La palabra de 32 bits seguía siendo correcta, pero buscar solamente el nombre original de la instrucción hacía que algunos casos aparecieran como fallidos.

Por esta razón, la versión final de `validar.py` identifica la palabra por la dirección correspondiente y compara directamente el hexadecimal. Después de realizar estas correcciones, los 36 casos coincidieron.

---

# 9. Instalación y preparación

## 9.1 Requisitos de la herramienta

Para ejecutar el codificador se necesita:

- Python 3.
- Bash.
- Linux o un entorno compatible con Bash. En Windows se puede utilizar WSL.

El programa no utiliza librerías externas de Python, por lo que no es necesario instalar paquetes mediante `pip`.

---

## 9.2 Instalación del toolchain RISC-V

El toolchain utilizado durante el desarrollo se instaló en Ubuntu/WSL mediante:

```bash
sudo apt update
sudo apt install gcc-riscv64-unknown-elf binutils-riscv64-unknown-elf
```

La instalación se puede comprobar con:

```bash
riscv64-unknown-elf-gcc --version
```

Aunque el nombre del toolchain contiene `riscv64`, para la validación se especifica RV32I utilizando las opciones:

```text
-march=rv32i
-mabi=ilp32
```

Por ejemplo:

```bash
riscv64-unknown-elf-as -march=rv32i -mabi=ilp32 prueba.s -o prueba.o
```

y para observar la codificación:

```bash
riscv64-unknown-elf-objdump -d prueba.o
```

---

## 9.3 Preparación del proyecto

Después de obtener los archivos del repositorio, se debe verificar que `run.sh` tenga permiso de ejecución:

```bash
chmod +x run.sh
```

No es necesaria ninguna instalación adicional de dependencias de Python.

La herramienta se ejecuta siempre mediante:

```bash
./run.sh "<instruccion>"
```

Ejemplo:

```bash
./run.sh "lw x5, 8(x6)"
```

Para ejecutar la validación propia se utiliza:

```bash
python3 validar.py
```

---

# 10. Manejo de errores

El programa realiza validaciones antes de construir la instrucción.

Entre los errores considerados se encuentran:

- Instrucción no soportada.
- Registro con formato incorrecto.
- Registro menor que `x0` o mayor que `x31`.
- Cantidad incorrecta de operandos.
- Inmediato fuera del rango representable.
- Sintaxis incorrecta en operandos de memoria.
- Desplazamiento impar para instrucciones de formato B.

Cuando se detecta alguno de estos casos se muestra un mensaje de error y no se genera una palabra que pueda confundirse con una codificación válida.

---

# 11. Resultados

Después de implementar y probar las 12 instrucciones, los resultados obtenidos fueron:

| Prueba | Resultado |
|---|---:|
| Instrucciones implementadas | 12/12 |
| Vectores de ejemplo | 36/36 |
| Casos propios creados | 36 |
| Casos propios contra toolchain | 36/36 |
| Formatos implementados | R, I, S y B |

Con estas pruebas se comprobó que el modelo genera la misma palabra de 32 bits que el toolchain para los casos utilizados, incluyendo registros diferentes, inmediatos negativos y valores límite.

---

# 12. Referencias

[1] Waterman, A., & Asanović, K. (2019). *The RISC-V Instruction Set Manual, Volume I: User-Level ISA, Document Version 20191213*. RISC-V Foundation.

[2] RISC-V International. *RISC-V Instruction Set Manual, Volume I: Unprivileged ISA*.

[3] Material y especificación del Proyecto Individual, CE-4301 Arquitectura de Computadores I, Instituto Tecnológico de Costa Rica.