"""
APE 2 - Sistemas Distribuidos
Parte 1: SERVIDOR (comunicación cliente-servidor mediante archivos)

El servidor se ejecuta de forma continua (simula un servicio activo):
  - Revisa periódicamente el archivo ../comunicacion/entrada_servidor.txt
  - Detecta si existe contenido nuevo (solo lee lo que se agregó desde la última revisión)
  - Procesa cada mensaje (lo convierte a MAYÚSCULAS y lo invierte)
  - Escribe el resultado en ../comunicacion/salida_servidor.txt

Formato de una línea en entrada_servidor.txt:   <id>|<mensaje>
Formato de una línea en salida_servidor.txt:    <id>|<resultado>

Condiciones cumplidas:
  * Ejecución continua (bucle while True con intervalo de sondeo).
  * No reprocesa el mismo mensaje: guarda la posición (offset) ya leída y
    un registro de los IDs procesados (estado_servidor.txt).
  * Maneja archivos vacíos o inexistentes sin fallar.
"""

import os
import time
from datetime import datetime

# Carpeta de comunicación: está FUERA del proyecto del servidor y del cliente.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CANAL_DIR = os.path.normpath(os.path.join(BASE_DIR, "..", "comunicacion"))

ARCHIVO_ENTRADA = os.path.join(CANAL_DIR, "entrada_servidor.txt")
ARCHIVO_SALIDA = os.path.join(CANAL_DIR, "salida_servidor.txt")
ARCHIVO_ESTADO = os.path.join(BASE_DIR, "estado_servidor.txt")  # IDs ya procesados

INTERVALO_REVISION = 1.0  # segundos entre cada revisión del archivo


def log(texto):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] [SERVIDOR] {texto}", flush=True)


def preparar_archivos():
    """Crea la carpeta y los archivos de comunicación si no existen."""
    os.makedirs(CANAL_DIR, exist_ok=True)
    for ruta in (ARCHIVO_ENTRADA, ARCHIVO_SALIDA, ARCHIVO_ESTADO):
        if not os.path.exists(ruta):
            open(ruta, "w", encoding="utf-8").close()


def cargar_ids_procesados():
    with open(ARCHIVO_ESTADO, "r", encoding="utf-8") as f:
        return {linea.strip() for linea in f if linea.strip()}


def registrar_id(id_msg):
    with open(ARCHIVO_ESTADO, "a", encoding="utf-8") as f:
        f.write(id_msg + "\n")


def procesar_mensaje(mensaje):
    """Lógica de negocio del servidor: mayúsculas + texto invertido."""
    return mensaje.upper()[::-1]


def leer_contenido_nuevo(offset):
    """
    Devuelve (lineas_completas, nuevo_offset).
    Solo lee desde 'offset' en adelante; si el archivo está vacío o no existe
    devuelve una lista vacía. Si el archivo fue vaciado (tamaño < offset)
    reinicia la lectura desde el inicio.
    """
    if not os.path.exists(ARCHIVO_ENTRADA):
        return [], 0

    tamano = os.path.getsize(ARCHIVO_ENTRADA)
    if tamano == 0:
        return [], 0              # archivo vacío: nada que hacer
    if tamano < offset:
        log("El archivo de entrada fue reiniciado; se vuelve a leer desde el inicio.")
        offset = 0
    if tamano == offset:
        return [], offset         # no hay contenido nuevo

    # Se lee en modo binario para que el offset sea exacto en bytes
    # (en Windows el modo texto convierte \n en \r\n y desfasa la posición).
    with open(ARCHIVO_ENTRADA, "rb") as f:
        f.seek(offset)
        datos = f.read()

    # Solo se procesan líneas completas (terminadas en \n); si el cliente
    # está escribiendo en este momento, la línea parcial se lee en la próxima vuelta.
    ultimo_salto = datos.rfind(b"\n")
    if ultimo_salto == -1:
        return [], offset
    completas = datos[: ultimo_salto + 1]
    nuevo_offset = offset + len(completas)
    lineas = completas.decode("utf-8", errors="replace").splitlines()
    return lineas, nuevo_offset


def main():
    preparar_archivos()
    procesados = cargar_ids_procesados()
    offset = 0
    log(f"Servicio iniciado. Escuchando: {ARCHIVO_ENTRADA}")
    log(f"Mensajes procesados previamente: {len(procesados)}")

    try:
        while True:
            lineas, offset = leer_contenido_nuevo(offset)
            for linea in lineas:
                linea = linea.strip()
                if not linea:
                    continue  # ignora líneas vacías
                if "|" not in linea:
                    log(f"Línea con formato inválido ignorada: {linea!r}")
                    continue

                id_msg, mensaje = linea.split("|", 1)
                if id_msg in procesados:
                    continue  # NO reprocesar el mismo mensaje

                resultado = procesar_mensaje(mensaje)
                with open(ARCHIVO_SALIDA, "a", encoding="utf-8") as f:
                    f.write(f"{id_msg}|{resultado}\n")

                procesados.add(id_msg)
                registrar_id(id_msg)
                log(f"Procesado id={id_msg}: '{mensaje}' -> '{resultado}'")

            time.sleep(INTERVALO_REVISION)
    except KeyboardInterrupt:
        log("Servicio detenido por el usuario.")


if __name__ == "__main__":
    main()
