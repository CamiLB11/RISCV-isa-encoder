import subprocess
import tempfile
import os
import re
import sys


CASOS_FILE = "casos_prueba.txt"
RUN_SCRIPT = "./run.sh"

AS = "riscv64-unknown-elf-as"
OBJDUMP = "riscv64-unknown-elf-objdump"


def leer_casos():
    """ Lee casos_prueba.txt e ignora comentarios y líneas vacías. """

    casos = []

    with open(CASOS_FILE, "r", encoding="utf-8") as archivo:
        for linea in archivo:
            linea = linea.strip()

            if not linea:
                continue

            if linea.startswith("#"):
                continue

            casos.append(linea)

    return casos


def obtener_hex_encoder(instruccion):
    """ Ejecuta programa mediante run.sh y extrae la línea: HEX: 0x........ """

    resultado = subprocess.run(
        [RUN_SCRIPT, instruccion],
        capture_output=True,
        text=True
    )

    if resultado.returncode != 0:
        raise RuntimeError(
            f"Nuestro encoder falló con:\n{instruccion}\n\n"
            f"{resultado.stderr}"
        )

    match = re.search(
        r"^HEX:\s*(0x[0-9a-fA-F]{8})$",
        resultado.stdout,
        re.MULTILINE
    )

    if not match:
        raise RuntimeError(
            f"No se encontró la línea HEX para:\n{instruccion}"
        )

    return match.group(1).lower()


def obtener_hex_toolchain(instruccion):
    """ Ensambla una instrucción con el toolchain oficial y obtiene
    su codificación mediante objdump. 
    Para beq y bne se utiliza una etiqueta local colocada a la
    distancia indicada por el inmediato.
    """

    with tempfile.TemporaryDirectory() as temp_dir:

        archivo_s = os.path.join(temp_dir, "prueba.s")
        archivo_o = os.path.join(temp_dir, "prueba.o")

        instruccion_limpia = instruccion.strip()

        branch_match = re.fullmatch(
            r"(beq|bne)\s+(x\d+)\s*,\s*(x\d+)\s*,\s*(-?\d+)",
            instruccion_limpia,
            re.IGNORECASE
        )

        direccion_instruccion = 0

        if branch_match:

            mnemonico = branch_match.group(1).lower()
            rs1 = branch_match.group(2)
            rs2 = branch_match.group(3)
            offset = int(branch_match.group(4))

            lineas = [
                ".text",
                ".option norvc"
            ]

            if offset > 0:

                direccion_instruccion = 0

                lineas.append(
                    f"{mnemonico} {rs1}, {rs2}, destino"
                )

                espacio = offset - 4

                if espacio > 0:
                    lineas.append(f".space {espacio}")

                lineas.append("destino:")

            elif offset < 0:

                lineas.append("destino:")
                lineas.append(f".space {-offset}")

                direccion_instruccion = -offset

                lineas.append(
                    f"{mnemonico} {rs1}, {rs2}, destino"
                )

            else:

                direccion_instruccion = 0

                lineas.append("destino:")
                lineas.append(
                    f"{mnemonico} {rs1}, {rs2}, destino"
                )

            codigo_asm = "\n".join(lineas) + "\n"

        else:

            direccion_instruccion = 0

            codigo_asm = (
                ".text\n"
                ".option norvc\n"
                + instruccion_limpia
                + "\n"
            )

        with open(archivo_s, "w", encoding="utf-8") as archivo:
            archivo.write(codigo_asm)

        ensamblado = subprocess.run(
            [
                AS,
                "-march=rv32i",
                "-mabi=ilp32",
                archivo_s,
                "-o",
                archivo_o
            ],
            capture_output=True,
            text=True
        )

        if ensamblado.returncode != 0:
            raise RuntimeError(
                f"El ensamblador falló con:\n{instruccion}\n\n"
                f"{ensamblado.stderr}"
            )

        desensamblado = subprocess.run(
            [
                OBJDUMP,
                "-d",
                archivo_o
            ],
            capture_output=True,
            text=True
        )

        if desensamblado.returncode != 0:
            raise RuntimeError(
                f"objdump falló con:\n{instruccion}\n\n"
                f"{desensamblado.stderr}"
            )

        # Se busca la instrucción por su dirección, no por su mnemónico para evitar problemas con alias de objdump como:
        # sub -> neg
        # addi -> li
        # andi -> zext.b
        # beq -> beqz

        direccion_hex = f"{direccion_instruccion:x}"

        patron = re.compile(
            rf"^\s*{re.escape(direccion_hex)}:\s+([0-9a-fA-F]{{8}})\s+",
            re.MULTILINE
        )

        match = patron.search(desensamblado.stdout)

        if not match:
            raise RuntimeError(
                f"No se pudo obtener la codificación de objdump para:\n"
                f"{instruccion}\n\n"
                f"Dirección esperada: 0x{direccion_hex}\n\n"
                f"Salida de objdump:\n{desensamblado.stdout}"
            )

        return "0x" + match.group(1).lower()


def main():

    try:
        casos = leer_casos()
    except FileNotFoundError:
        print(f"ERROR: No se encontró {CASOS_FILE}")
        sys.exit(1)

    if len(casos) != 36:
        print(
            f"ADVERTENCIA: se encontraron {len(casos)} casos, "
            "pero se esperaban 36."
        )

    print("=" * 100)
    print("VALIDACIÓN DEL CODIFICADOR RISC-V CONTRA EL TOOLCHAIN OFICIAL")
    print("=" * 100)
    print()

    exitosos = 0
    fallidos = 0

    resultados = []

    for numero, instruccion in enumerate(casos, start=1):

        try:
            encoder_hex = obtener_hex_encoder(instruccion)
            toolchain_hex = obtener_hex_toolchain(instruccion)

            coincide = encoder_hex == toolchain_hex

            if coincide:
                estado = "OK"
                exitosos += 1
            else:
                estado = "FAIL"
                fallidos += 1

            resultados.append(
                (
                    numero,
                    instruccion,
                    encoder_hex,
                    toolchain_hex,
                    estado
                )
            )

            print(
                f"[{numero:02d}/36] {estado:<4} "
                f"{instruccion:<28} "
                f"Encoder: {encoder_hex}   "
                f"Toolchain: {toolchain_hex}"
            )

        except Exception as error:

            fallidos += 1

            resultados.append(
                (
                    numero,
                    instruccion,
                    "ERROR",
                    "ERROR",
                    "FAIL"
                )
            )

            print(
                f"[{numero:02d}/36] FAIL {instruccion}"
            )

            print(f"          {error}")

    print()
    print("=" * 100)
    print("RESUMEN")
    print("=" * 100)

    print(f"Total de casos : {len(casos)}")
    print(f"Correctos      : {exitosos}")
    print(f"Incorrectos    : {fallidos}")

    if fallidos == 0 and len(casos) == 36:
        print()
        print("RESULTADO FINAL: 36/36 CASOS COINCIDEN CON EL TOOLCHAIN OFICIAL.")
    else:
        print()
        print("RESULTADO FINAL: existen casos que deben revisarse.")

    # Crear evidencia en Markdown

    with open(
        "resultados_validacion.md",
        "w",
        encoding="utf-8"
    ) as archivo:

        archivo.write("# Resultados de validación\n\n")

        archivo.write(
            "La siguiente tabla muestra la comparación entre la "
            "codificación generada por la herramienta desarrollada y "
            "la obtenida mediante el toolchain oficial de RISC-V.\n\n"
        )

        archivo.write(
            "El ensamblado de referencia se realizó utilizando "
            "`riscv64-unknown-elf-as` con `-march=rv32i` y "
            "`-mabi=ilp32`, y posteriormente se obtuvo la codificación "
            "mediante `riscv64-unknown-elf-objdump -d`.\n\n"
        )

        archivo.write(
            "| # | Instrucción | Encoder propio | Toolchain | Resultado |\n"
        )

        archivo.write(
            "|---:|---|---|---|---|\n"
        )

        for (
            numero,
            instruccion,
            encoder_hex,
            toolchain_hex,
            estado
        ) in resultados:

            archivo.write(
                f"| {numero} | `{instruccion}` | "
                f"`{encoder_hex}` | `{toolchain_hex}` | "
                f"{estado} |\n"
            )

        archivo.write("\n")

        archivo.write("## Resumen\n\n")

        archivo.write(
            f"- Total de casos: {len(casos)}\n"
        )

        archivo.write(
            f"- Casos correctos: {exitosos}\n"
        )

        archivo.write(
            f"- Casos incorrectos: {fallidos}\n"
        )

        if fallidos == 0 and len(casos) == 36:

            archivo.write(
                "\nLos 36 casos de prueba coincidieron con la "
                "codificación obtenida mediante el toolchain oficial "
                "de RISC-V.\n"
            )

    print()
    print(
        "Se generó el archivo resultados_validacion.md "
        "con la evidencia de las pruebas."
    )


if __name__ == "__main__":
    main()