#!/usr/bin/env python3
"""
Codificador Educativo de Instrucciones RISC-V.
CE4301 Arquitectura de Computadores I — Proyecto Individual — 2026-II

La herramienta recibe una instrucción perteneciente al subconjunto RV32I
solicitado en el proyecto y genera su codificación de 32 bits.

Formatos soportados:
    R: add, sub, and, or
    I: addi, andi, lw, lb
    S: sw, sb
    B: beq, bne
"""

import sys
import re


SOPORTADAS = [
    "add", "sub", "and", "or",
    "addi", "andi",
    "lw", "lb",
    "sw", "sb",
    "beq", "bne"
]

# Información de codificación de las instrucciones RV32I soportadas

INSTRUCCIONES = {
    # Formato R
    "add": {
        "formato": "R",
        "opcode": 0b0110011,
        "funct3": 0b000,
        "funct7": 0b0000000
    },

    "sub": {
        "formato": "R",
        "opcode": 0b0110011,
        "funct3": 0b000,
        "funct7": 0b0100000
    },

    "and": {
        "formato": "R",
        "opcode": 0b0110011,
        "funct3": 0b111,
        "funct7": 0b0000000
    },

    "or": {
        "formato": "R",
        "opcode": 0b0110011,
        "funct3": 0b110,
        "funct7": 0b0000000
    },

    # Formato I - operaciones aritméticas
    "addi": {
        "formato": "I",
        "tipo": "aritmetica",
        "opcode": 0b0010011,
        "funct3": 0b000
    },

    "andi": {
        "formato": "I",
        "tipo": "aritmetica",
        "opcode": 0b0010011,
        "funct3": 0b111
    },

    # Formato I - cargas
    "lw": {
        "formato": "I",
        "tipo": "load",
        "opcode": 0b0000011,
        "funct3": 0b010
    },

    "lb": {
        "formato": "I",
        "tipo": "load",
        "opcode": 0b0000011,
        "funct3": 0b000
    },

    # Formato S - almacenamiento
    "sw": {
        "formato": "S",
        "opcode": 0b0100011,
        "funct3": 0b010
    },

    "sb": {
        "formato": "S",
        "opcode": 0b0100011,
        "funct3": 0b000
    },

    # Formato B - saltos condicionales
    "beq": {
        "formato": "B",
        "opcode": 0b1100011,
        "funct3": 0b000
    },

    "bne": {
        "formato": "B",
        "opcode": 0b1100011,
        "funct3": 0b001
    }
}

# Funciones auxiliares

def parse_register(register: str) -> int:
    """ Convierte un registro escrito como x0...x31 a su valor numérico. """

    register = register.strip().lower()

    if not re.fullmatch(r"x\d+", register):
        raise ValueError(f"Registro inválido: {register}")

    number = int(register[1:])

    if number < 0 or number > 31:
        raise ValueError(
            f"Registro fuera de rango: {register}. "
            "Los registros válidos son x0 a x31."
        )

    return number


def check_immediate(value: int, minimum: int, maximum: int):
    """ Comprueba que un inmediato esté dentro del rango permitido. """

    if value < minimum or value > maximum:
        raise ValueError(
            f"Inmediato fuera de rango: {value}. "
            f"Debe estar entre {minimum} y {maximum}."
        )


def twos_complement(value: int, bits: int) -> int:
    """ Representa un número dentro de una cantidad determinada de bits. 
    También permite obtener correctamente la representación en complemento a dos
    cuando el valor es negativo.
    """

    return value & ((1 << bits) - 1)


def split_operands(text: str):
    """ Separa operandos escritos con comas y elimina espacios innecesarios. """

    return [operand.strip() for operand in text.split(",")]


def parse_memory_operand(operand: str):
    """ Analiza operandos con la forma: inmediato(registro) """

    match = re.fullmatch(
        r"\s*([+-]?\d+)\s*\(\s*(x\d+)\s*\)\s*",
        operand.lower()
    )

    if not match:
        raise ValueError(
            f"Operando de memoria inválido: {operand}. "
            "Se esperaba una forma como 8(x6)."
        )

    immediate = int(match.group(1))
    rs1 = parse_register(match.group(2))

    return immediate, rs1

# Codificación por formato

def encode_r(rd: int, rs1: int, rs2: int,
             funct3: int, funct7: int, opcode: int) -> int:
    """
    Construye una instrucción de formato R.

    Bits:
        31-25 : funct7
        24-20 : rs2
        19-15 : rs1
        14-12 : funct3
        11-7  : rd
        6-0   : opcode
    """

    word = (
        (funct7 << 25)
        | (rs2 << 20)
        | (rs1 << 15)
        | (funct3 << 12)
        | (rd << 7)
        | opcode
    )

    return word


def encode_i(rd: int, rs1: int, immediate: int,
             funct3: int, opcode: int) -> int:
    """
    Construye una instrucción de formato I.

    Bits:
        31-20 : immediate[11:0]
        19-15 : rs1
        14-12 : funct3
        11-7  : rd
        6-0   : opcode
    """

    check_immediate(immediate, -2048, 2047)

    imm = twos_complement(immediate, 12)

    word = (
        (imm << 20)
        | (rs1 << 15)
        | (funct3 << 12)
        | (rd << 7)
        | opcode
    )

    return word


def encode_s(rs2: int, rs1: int, immediate: int,
             funct3: int, opcode: int) -> int:
    """
    Construye una instrucción de formato S.

    El inmediato de 12 bits se divide en dos partes:

        31-25 : immediate[11:5]
        11-7  : immediate[4:0]
    """

    check_immediate(immediate, -2048, 2047)

    imm = twos_complement(immediate, 12)

    imm_11_5 = (imm >> 5) & 0b1111111
    imm_4_0 = imm & 0b11111

    word = (
        (imm_11_5 << 25)
        | (rs2 << 20)
        | (rs1 << 15)
        | (funct3 << 12)
        | (imm_4_0 << 7)
        | opcode
    )

    return word


def encode_b(rs1: int, rs2: int, immediate: int,
             funct3: int, opcode: int) -> int:
    """
    Construye una instrucción de formato B.

    El inmediato del branch se distribuye así:

        bit 31    : immediate[12]
        bits 30-25: immediate[10:5]
        bits 11-8 : immediate[4:1]
        bit 7     : immediate[11]

    El bit 0 no se almacena porque el desplazamiento debe ser par.
    """

    check_immediate(immediate, -4096, 4094)

    if immediate % 2 != 0:
        raise ValueError(
            "El inmediato de una instrucción branch debe ser múltiplo de 2."
        )

    imm = twos_complement(immediate, 13)

    imm_12 = (imm >> 12) & 0b1
    imm_11 = (imm >> 11) & 0b1
    imm_10_5 = (imm >> 5) & 0b111111
    imm_4_1 = (imm >> 1) & 0b1111

    word = (
        (imm_12 << 31)
        | (imm_10_5 << 25)
        | (rs2 << 20)
        | (rs1 << 15)
        | (funct3 << 12)
        | (imm_4_1 << 8)
        | (imm_11 << 7)
        | opcode
    )

    return word

# Función principal de codificación

def encode_instruction(instruction: str) -> int:
    """ Recibe una instrucción como texto y retorna su codificación de 32 bits como un entero. """

    instruction = instruction.strip().lower()

    if not instruction:
        raise ValueError("La instrucción está vacía.")

    parts = instruction.split(maxsplit=1)

    mnemonic = parts[0]

    if mnemonic not in SOPORTADAS:
        raise ValueError(
            f"Instrucción no soportada: {mnemonic}. "
            f"Soportadas: {', '.join(SOPORTADAS)}"
        )

    if len(parts) != 2:
        raise ValueError("Faltan operandos en la instrucción.")

    operand_text = parts[1]
    info = INSTRUCCIONES[mnemonic]

    formato = info["formato"]

    # Formato R
    # add rd, rs1, rs2
    # sub rd, rs1, rs2
    # and rd, rs1, rs2
    # or  rd, rs1, rs2

    if formato == "R":

        operands = split_operands(operand_text)

        if len(operands) != 3:
            raise ValueError(
                f"{mnemonic} requiere 3 operandos: rd, rs1, rs2."
            )

        rd = parse_register(operands[0])
        rs1 = parse_register(operands[1])
        rs2 = parse_register(operands[2])

        return encode_r(
            rd,
            rs1,
            rs2,
            info["funct3"],
            info["funct7"],
            info["opcode"]
        )

    # Formato I

    elif formato == "I":

        # addi rd, rs1, imm
        # andi rd, rs1, imm
        if info["tipo"] == "aritmetica":

            operands = split_operands(operand_text)

            if len(operands) != 3:
                raise ValueError(
                    f"{mnemonic} requiere 3 operandos: rd, rs1, inmediato."
                )

            rd = parse_register(operands[0])
            rs1 = parse_register(operands[1])

            try:
                immediate = int(operands[2])
            except ValueError:
                raise ValueError(
                    f"Inmediato inválido: {operands[2]}"
                )

        # lw rd, imm(rs1)
        # lb rd, imm(rs1)
        else:

            operands = split_operands(operand_text)

            if len(operands) != 2:
                raise ValueError(
                    f"{mnemonic} requiere la forma rd, inmediato(rs1)."
                )

            rd = parse_register(operands[0])
            immediate, rs1 = parse_memory_operand(operands[1])

        return encode_i(
            rd,
            rs1,
            immediate,
            info["funct3"],
            info["opcode"]
        )

    # Formato S
    # sw rs2, imm(rs1)
    # sb rs2, imm(rs1)

    elif formato == "S":

        operands = split_operands(operand_text)

        if len(operands) != 2:
            raise ValueError(
                f"{mnemonic} requiere la forma rs2, inmediato(rs1)."
            )

        rs2 = parse_register(operands[0])
        immediate, rs1 = parse_memory_operand(operands[1])

        return encode_s(
            rs2,
            rs1,
            immediate,
            info["funct3"],
            info["opcode"]
        )

    # Formato B
    # beq rs1, rs2, imm
    # bne rs1, rs2, imm

    elif formato == "B":

        operands = split_operands(operand_text)

        if len(operands) != 3:
            raise ValueError(
                f"{mnemonic} requiere 3 operandos: rs1, rs2, inmediato."
            )

        rs1 = parse_register(operands[0])
        rs2 = parse_register(operands[1])

        try:
            immediate = int(operands[2])
        except ValueError:
            raise ValueError(
                f"Inmediato inválido: {operands[2]}"
            )

        return encode_b(
            rs1,
            rs2,
            immediate,
            info["funct3"],
            info["opcode"]
        )

    raise ValueError("Formato de instrucción desconocido.")

# Explicación visual

def explain_instruction(instruction: str, word: int) -> str:
    """ Genera una explicación visual de los campos que componen la instrucción. """

    instruction_normalized = instruction.strip().lower()
    mnemonic = instruction_normalized.split()[0]

    info = INSTRUCCIONES[mnemonic]
    formato = info["formato"]

    binary = f"{word:032b}"

    lines = []

    lines.append("=" * 72)
    lines.append("CODIFICADOR EDUCATIVO RISC-V RV32I")
    lines.append("=" * 72)
    lines.append(f"Instrucción : {instruction}")
    lines.append(f"Formato     : {formato}")
    lines.append(f"BINARIO         : {binary}")
    lines.append("")

    # Formato R

    if formato == "R":

        funct7 = (word >> 25) & 0x7F
        rs2 = (word >> 20) & 0x1F
        rs1 = (word >> 15) & 0x1F
        funct3 = (word >> 12) & 0x7
        rd = (word >> 7) & 0x1F
        opcode = word & 0x7F

        lines.append("Distribución de campos:")
        lines.append("")
        lines.append(" 31------25 24---20 19---15 14-12 11----7 6-------0")
        lines.append("+----------+-------+-------+-----+-------+---------+")
        lines.append("|  funct7  |  rs2  |  rs1  |funct3|  rd | opcode  |")
        lines.append("+----------+-------+-------+-----+-------+---------+")
        lines.append(
            f"| {funct7:07b}  | {rs2:05b} | {rs1:05b} |"
            f" {funct3:03b} | {rd:05b} | {opcode:07b} |"
        )
        lines.append("+----------+-------+-------+-----+-------+---------+")
        lines.append("")

        lines.append(
            f"funct7 [31:25] = {funct7:07b} ({funct7})"
        )
        lines.append(
            "  Campo adicional utilizado para distinguir operaciones."
        )

        lines.append(
            f"rs2    [24:20] = {rs2:05b} (x{rs2})"
        )
        lines.append(
            "  Segundo registro fuente."
        )

        lines.append(
            f"rs1    [19:15] = {rs1:05b} (x{rs1})"
        )
        lines.append(
            "  Primer registro fuente."
        )

        lines.append(
            f"funct3 [14:12] = {funct3:03b} ({funct3})"
        )
        lines.append(
            "  Campo que ayuda a seleccionar la operación específica."
        )

        lines.append(
            f"rd      [11:7] = {rd:05b} (x{rd})"
        )
        lines.append(
            "  Registro destino donde se almacena el resultado."
        )

        lines.append(
            f"opcode   [6:0] = {opcode:07b}"
        )
        lines.append(
            "  Identifica el tipo principal de operación."
        )

    # Formato I

    elif formato == "I":

        imm = (word >> 20) & 0xFFF
        rs1 = (word >> 15) & 0x1F
        funct3 = (word >> 12) & 0x7
        rd = (word >> 7) & 0x1F
        opcode = word & 0x7F

        signed_imm = imm

        if imm & 0x800:
            signed_imm -= 0x1000

        lines.append("Distribución de campos:")
        lines.append("")
        lines.append(" 31-------------20 19---15 14-12 11----7 6-------0")
        lines.append("+----------------+-------+-----+-------+---------+")
        lines.append("|   imm[11:0]    |  rs1  |funct3|  rd | opcode  |")
        lines.append("+----------------+-------+-----+-------+---------+")
        lines.append(
            f"| {imm:012b}   | {rs1:05b} |"
            f" {funct3:03b} | {rd:05b} | {opcode:07b} |"
        )
        lines.append("+----------------+-------+-----+-------+---------+")
        lines.append("")

        lines.append(
            f"imm    [31:20] = {imm:012b} ({signed_imm})"
        )
        lines.append(
            "  Valor inmediato de 12 bits usado por la instrucción."
        )

        lines.append(
            f"rs1    [19:15] = {rs1:05b} (x{rs1})"
        )
        lines.append(
            "  Registro fuente o registro base."
        )

        lines.append(
            f"funct3 [14:12] = {funct3:03b} ({funct3})"
        )
        lines.append(
            "  Ayuda a identificar la operación específica."
        )

        lines.append(
            f"rd      [11:7] = {rd:05b} (x{rd})"
        )
        lines.append(
            "  Registro destino."
        )

        lines.append(
            f"opcode   [6:0] = {opcode:07b}"
        )
        lines.append(
            "  Identifica el tipo principal de instrucción."
        )

    # Formato S

    elif formato == "S":

        imm_11_5 = (word >> 25) & 0x7F
        rs2 = (word >> 20) & 0x1F
        rs1 = (word >> 15) & 0x1F
        funct3 = (word >> 12) & 0x7
        imm_4_0 = (word >> 7) & 0x1F
        opcode = word & 0x7F

        imm = (imm_11_5 << 5) | imm_4_0

        signed_imm = imm

        if imm & 0x800:
            signed_imm -= 0x1000

        lines.append("Distribución de campos:")
        lines.append("")
        lines.append(" 31------25 24---20 19---15 14-12 11----7 6-------0")
        lines.append("+----------+-------+-------+-----+-------+---------+")
        lines.append("|imm[11:5] |  rs2  |  rs1  |funct3|imm[4:0]|opcode|")
        lines.append("+----------+-------+-------+-----+-------+---------+")
        lines.append(
            f"| {imm_11_5:07b}  | {rs2:05b} | {rs1:05b} |"
            f" {funct3:03b} | {imm_4_0:05b} | {opcode:07b} |"
        )
        lines.append("+----------+-------+-------+-----+-------+---------+")
        lines.append("")

        lines.append(
            f"imm[11:5] [31:25] = {imm_11_5:07b}"
        )
        lines.append(
            "  Parte superior del desplazamiento inmediato."
        )

        lines.append(
            f"rs2       [24:20] = {rs2:05b} (x{rs2})"
        )
        lines.append(
            "  Registro cuyo valor será almacenado en memoria."
        )

        lines.append(
            f"rs1       [19:15] = {rs1:05b} (x{rs1})"
        )
        lines.append(
            "  Registro base utilizado para calcular la dirección."
        )

        lines.append(
            f"funct3     [14:12] = {funct3:03b} ({funct3})"
        )
        lines.append(
            "  Determina el tipo o tamaño de almacenamiento."
        )

        lines.append(
            f"imm[4:0]    [11:7] = {imm_4_0:05b}"
        )
        lines.append(
            "  Parte inferior del desplazamiento inmediato."
        )

        lines.append(
            f"opcode       [6:0] = {opcode:07b}"
        )
        lines.append(
            "  Identifica una instrucción de almacenamiento."
        )

        lines.append("")
        lines.append(
            f"Inmediato completo: {imm:012b} ({signed_imm})"
        )

    # Formato B

    elif formato == "B":

        imm_12 = (word >> 31) & 0x1
        imm_10_5 = (word >> 25) & 0x3F
        rs2 = (word >> 20) & 0x1F
        rs1 = (word >> 15) & 0x1F
        funct3 = (word >> 12) & 0x7
        imm_4_1 = (word >> 8) & 0xF
        imm_11 = (word >> 7) & 0x1
        opcode = word & 0x7F

        imm = (
            (imm_12 << 12)
            | (imm_11 << 11)
            | (imm_10_5 << 5)
            | (imm_4_1 << 1)
        )

        signed_imm = imm

        if imm & 0x1000:
            signed_imm -= 0x2000

        lines.append("Distribución de campos:")
        lines.append("")
        lines.append(
            " 31 30----25 24---20 19---15 14-12 11---8 7 6------0"
        )
        lines.append(
            "+--+--------+-------+-------+-----+------+--+---------+"
        )
        lines.append(
            "|12| 10:5   | rs2   | rs1   |funct3| 4:1 |11| opcode |"
        )
        lines.append(
            "+--+--------+-------+-------+-----+------+--+---------+"
        )
        lines.append(
            f"|{imm_12} | {imm_10_5:06b} | {rs2:05b} | {rs1:05b} |"
            f" {funct3:03b} | {imm_4_1:04b} |{imm_11} | {opcode:07b} |"
        )
        lines.append(
            "+--+--------+-------+-------+-----+------+--+---------+"
        )
        lines.append("")

        lines.append(
            f"imm[12]       [31] = {imm_12}"
        )
        lines.append(
            "  Bit de signo del desplazamiento del branch."
        )

        lines.append(
            f"imm[10:5]  [30:25] = {imm_10_5:06b}"
        )
        lines.append(
            "  Parte del desplazamiento inmediato."
        )

        lines.append(
            f"rs2        [24:20] = {rs2:05b} (x{rs2})"
        )
        lines.append(
            "  Segundo registro que se compara."
        )

        lines.append(
            f"rs1        [19:15] = {rs1:05b} (x{rs1})"
        )
        lines.append(
            "  Primer registro que se compara."
        )

        lines.append(
            f"funct3     [14:12] = {funct3:03b} ({funct3})"
        )
        lines.append(
            "  Determina la condición que debe evaluarse."
        )

        lines.append(
            f"imm[4:1]    [11:8] = {imm_4_1:04b}"
        )
        lines.append(
            "  Parte del desplazamiento inmediato."
        )

        lines.append(
            f"imm[11]         [7] = {imm_11}"
        )
        lines.append(
            "  Otro bit del desplazamiento inmediato."
        )

        lines.append(
            f"opcode        [6:0] = {opcode:07b}"
        )
        lines.append(
            "  Identifica una instrucción de branch."
        )

        lines.append("")
        lines.append(
            f"Desplazamiento completo: {signed_imm}"
        )

    lines.append("")
    lines.append(f"Palabra binaria completa: {binary}")
    lines.append(f"Palabra hexadecimal: 0x{word:08x}")
    lines.append("=" * 72)

    return "\n".join(lines)

# Programa principal

def main():

    if len(sys.argv) != 2:
        print(
            f'Uso: {sys.argv[0]} "<instruccion>"',
            file=sys.stderr
        )

        print(
            f'Ejemplo: {sys.argv[0]} "add x5, x6, x7"',
            file=sys.stderr
        )

        sys.exit(2)

    instruction = sys.argv[1]

    try:
        word = encode_instruction(instruction) & 0xFFFFFFFF

        print(explain_instruction(instruction, word))

        # Esta línea es para la validación automática.
        print(f"HEX: 0x{word:08x}")

    except ValueError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
