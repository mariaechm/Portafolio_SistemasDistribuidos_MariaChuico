"""
APE 2 - Sistemas Distribuidos
Parte 2: CLIENTE (comunicación cliente-servidor mediante archivos)

El cliente NO conoce cómo funciona el servidor internamente; solo conoce:
  - El archivo donde debe dejar su petición:  ../comunicacion/entrada_servidor.txt
  - El archivo donde leerá la respuesta:      ../comunicacion/salida_servidor.txt
  - El formato de intercambio:                <id>|<texto>

Flujo:
  1. Solicita un mensaje al usuario.
  2. Lo escribe (agrega) en entrada_servidor.txt con un identificador único.
  3. Espera un tiempo (simulando la latencia de red).
  4. Lee la respuesta desde salida_servidor.txt buscando su identificador.
  5. Muestra el resultado en pantalla.
"""

import os
import sys
import time
import uuid
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CANAL_DIR = os.path.normpath(os.path.join(BASE_DIR, "..", "comunicacion"))

ARCHIVO_ENTRADA = os.path.join(CANAL_DIR, "entrada_servidor.txt")
ARCHIVO_SALIDA = os.path.join(CANAL_DIR, "salida_servidor.txt")

LATENCIA = 2.0        # espera inicial simulando latencia (segundos)
TIEMPO_MAXIMO = 10.0  # tiempo máximo de espera de la respuesta (segundos)
REINTENTO = 0.5       # intervalo entre lecturas de la salida


def log(texto):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] [CLIENTE] {texto}", flush=True)


def enviar(mensaje):
    """Escribe la petición en el archivo de entrada y devuelve su id."""
    os.makedirs(CANAL_DIR, exist_ok=True)
    id_msg = uuid.uuid4().hex[:8]
    mensaje = mensaje.replace("\n", " ").replace("|", "/")  # protege el formato
    with open(ARCHIVO_ENTRADA, "a", encoding="utf-8") as f:
        f.write(f"{id_msg}|{mensaje}\n")
    log(f"Mensaje enviado (id={id_msg}): '{mensaje}'")
    return id_msg


def buscar_respuesta(id_msg):
    """Busca en el archivo de salida la línea correspondiente a id_msg."""
    if not os.path.exists(ARCHIVO_SALIDA):
        return None
    with open(ARCHIVO_SALIDA, "r", encoding="utf-8") as f:
        for linea in f:
            if linea.startswith(id_msg + "|"):
                return linea.rstrip("\n").split("|", 1)[1]
    return None


def esperar_respuesta(id_msg):
    log(f"Esperando {LATENCIA:.1f} s (latencia simulada)...")
    time.sleep(LATENCIA)
    limite = time.time() + TIEMPO_MAXIMO
    while time.time() < limite:
        respuesta = buscar_respuesta(id_msg)
        if respuesta is not None:
            return respuesta
        time.sleep(REINTENTO)
    return None


def solicitar(mensaje):
    id_msg = enviar(mensaje)
    respuesta = esperar_respuesta(id_msg)
    if respuesta is None:
        log("No se recibió respuesta. ¿El servidor está en ejecución?")
    else:
        log(f"Respuesta recibida: '{respuesta}'")
    return respuesta


def main():
    # Modo no interactivo: python cliente.py "mensaje 1" "mensaje 2" ...
    if len(sys.argv) > 1:
        for mensaje in sys.argv[1:]:
            solicitar(mensaje)
        return

    log("Cliente iniciado. Escriba 'salir' para terminar.")
    while True:
        try:
            mensaje = input("Ingrese un mensaje: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if mensaje.lower() == "salir":
            break
        if not mensaje:
            log("No se envían mensajes vacíos.")
            continue
        solicitar(mensaje)
    log("Cliente finalizado.")


if __name__ == "__main__":
    main()
