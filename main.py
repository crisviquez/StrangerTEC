import network
import socket
import time
from machine import Pin

#======================================#
#Config WIFI
SSID = "Familia-Ramirez"
PASSWORD = "d53dca4678"

BOTON_PIN = 16
unidad = 0.2

boton = Pin(BOTON_PIN, Pin.IN, Pin.PULL_UP)
led = Pin("LED", Pin.OUT)

morse_acumulado = ""

#=======================================#
def conectar_wifi():
    red = network.WLAN(network.STA_IF)
    red.active(True)
    red.connect(SSID, PASSWORD)

    print("Conectando al WIFI", end="")
    intentos = 0
    while not red.isconnected():
        print(".", end="")
        time.sleep(0.5)
        intentos += 1
        if intentos > 30:
            print("\nNo se pudo conectar")
            return None
        
    ip = red.ifconfig()[0]
    print(f"\nConectado IP:{ip}")
    led.on()
    return ip

#=======================================#
def crear_servidor():
    # Crea un socket TCP que escucha en el puerto 80 (HTTP estándar)
    servidor = socket.socket()
    servidor.bind(("", 80))   # "" significa "escuchar en todas las IPs"
    servidor.listen(5)        # Acepta hasta 5 conexiones en cola
    return servidor


def responder(cliente, cuerpo, estado="200 OK"):
    # Arma una respuesta HTTP mínima válida
    respuesta = (
        f"HTTP/1.1 {estado}\r\n"
        f"Content-Type: text/plain\r\n"
        f"Content-Length: {len(cuerpo)}\r\n"
        f"\r\n"
        f"{cuerpo}"
    )
    cliente.send(respuesta.encode())
    cliente.close()


def manejar_peticion(cliente):
    global morse_acumulado, unidad

    # Lee la primera línea del request HTTP, ej: "GET /GET_MORSE HTTP/1.1"
    datos = cliente.recv(1024).decode()
    linea = datos.split("\r\n")[0]          # "GET /GET_MORSE HTTP/1.1"
    ruta  = linea.split(" ")[1]             # "/GET_MORSE"

    print(f"Petición recibida: {ruta}")

    if ruta == "/GET_MORSE":
        # La PC esta preguntando que morse se capturo
        responder(cliente, morse_acumulado)
        morse_acumulado = ""   # Limpia despues de entregar

    elif ruta == "/LED_ON":
        led.on()
        responder(cliente, "OK")

    elif ruta == "/LED_OFF":
        led.off()
        responder(cliente, "OK")

    elif ruta.startswith("/SET_UNIDAD_"):
        ms = int(ruta.split("_")[-1])
        unidad = ms / 1000
        responder(cliente, f"Unidad={unidad}s")

    else:
        responder(cliente, "Ruta no encontrada", "404 Not Found")

# ─── DETECCIÓN DEL BOTÓN ─────────────────────────────────────

def leer_boton():
    """
    Detecta UNA presión completa del botón y la convierte en punto o raya.
    Retorna "." o "-" o None si no hubo presión.

    Recuerda: con PULL_UP el botón lee 0 cuando está presionado.
    """
    global unidad

    # Si el botón no está presionado, no hacemos nada
    if boton.value() == 1:
        return None

    # El botón está presionado: medimos cuánto tiempo dura
    inicio = time.time()
    while boton.value() == 0:
        time.sleep(0.01)   # Espera en pequeños intervalos
    duracion = time.time() - inicio

    # Clasifica según la unidad de tiempo configurada
    if duracion < unidad * 2:
        return "."   # Presión corta = punto
    else:
        return "-"   # Presión larga = raya


# ─── BUCLE PRINCIPAL ─────────────────────────────────────────

def main():
    global morse_acumulado

    ip = conectar_wifi()
    if ip is None:
        return
    servidor = crear_servidor()
    print(f"Servidor HTTP listo en http://{ip}")

    # El socket no bloquea: si no hay conexión entrante, sigue al botón
    servidor.setblocking(False)

    while True:
        # 1. Revisa si la PC mandó una petición HTTP
        try:
            cliente, _ = servidor.accept()
            cliente.setblocking(True)
            manejar_peticion(cliente)
        except OSError:
            pass   # No había conexión, está bien

        # 2. Revisa si el botón fue presionado
        simbolo = leer_boton()
        if simbolo is not None:
            morse_acumulado += simbolo
            print(f"Morse acumulado: {morse_acumulado}")

        time.sleep(0.01)


main()
