import os

# Estructura (10 bytes):
#   offsets 0-3 -> firma "MINE" en ASCII
#   offsets 4-9 -> porcentaje de las 6 misiones
# Posición = 4 + misión - 1


def main():
    carpeta = os.getcwd()
    ruta = os.path.join(carpeta, "mine_progreso.bin")

    # TODO Crear archivo solamente si no existe
    if not os.path.exists(ruta):
        with open(ruta, "wb") as archivo:
            archivo.write(b"MINE" + bytes([20, 55, 90, 100, 10, 65]))

    # TODO Recuperar y validar el archivo
    with open(ruta, "rb") as archivo:
        antes = archivo.read()

    if len(antes) != 10 or antes[:4] != b"MINE":
        print("Archivo inválido: firma o tamaño incorrectos.")
        return

    entrada = input("Misión (1-6): ").strip()
    if not entrada.isdecimal():
        print("Misión inválida.")
        return

    mision = int(entrada)
    if mision < 1 or mision > 6:
        print("Misión inválida.")
        return

    entrada = input("Nuevo porcentaje (0-100): ").strip()
    if not entrada.isdecimal():
        print("Porcentaje inválido.")
        return

    nuevo = int(entrada)
    if nuevo < 0 or nuevo > 100:
        print("Porcentaje inválido.")
        return

    # TODO Localizar y actualizar la misión
    posicion = 4 + mision - 1
    anterior = antes[posicion]

    if nuevo > anterior:
        with open(ruta, "r+b") as archivo:
            archivo.seek(posicion)
            archivo.write(bytes([nuevo]))
        print("Actualización aceptada.")
    else:
        print("Se conserva el progreso anterior.")

    # TODO Volver a leer para verificar
    with open(ruta, "rb") as archivo:
        despues = archivo.read()

    intactos = True
    for i in range(4, 10):
        if i != posicion and antes[i] != despues[i]:
            intactos = False

    print(f"Misión {mision}: {anterior}% -> {despues[posicion]}%")
    print("Otras misiones intactas:", intactos)
    print("Progresos guardados:", list(despues[4:]))
    print("Archivo guardado en:", carpeta)


main()