import network
import socket
import time
from machine import Pin, PWM

# ─────────────────────────────────────────
# Config WiFi
# ─────────────────────────────────────────
SSID     = "MG LIVING 2.4"
PASSWORD = "Mgliving1234"

# ─────────────────────────────────────────
# Pines: botón, LED onboard, buzzer
# ─────────────────────────────────────────
boton  = Pin(16, Pin.IN, Pin.PULL_UP)
led    = Pin(15, Pin.OUT)
buzzer = PWM(Pin(18))
buzzer.freq(1900)
buzzer.duty_u16(0)

# ─────────────────────────────────────────
# Pines de chips (shift register + filas)
# ─────────────────────────────────────────
CLK_PIN   = Pin(27, Pin.OUT)
DATA_PIN  = Pin(13, Pin.OUT)
LED_FILA1 = Pin(0,  Pin.OUT)
LED_FILA2 = Pin(1,  Pin.OUT)
LED_FILA3 = Pin(28, Pin.OUT)

CLK_PIN.off()
DATA_PIN.off()
LED_FILA1.off()
LED_FILA2.off()
LED_FILA3.off()

# ─────────────────────────────────────────
# Tiempos
# ─────────────────────────────────────────
TIEMPO_PUNTO_RAYA = 300   # ms — umbral punto vs raya
TIEMPO_ESPACIO    = 1000  # ms — pausa que separa letras
unidad            = 0.2   # s  — también ajustable por HTTP

# ─────────────────────────────────────────
# Mapa LEDs
# ─────────────────────────────────────────
LED_BITS = {
    1:  1 << 0,   2:  1 << 1,   3:  1 << 2,   4:  1 << 3,
    11: 1 << 4,  10:  1 << 5,   9:  1 << 6,   5:  1 << 8,
    6:  1 << 9,   7:  1 << 10,  8:  1 << 11,  13: 1 << 14,
    12: 1 << 15,
}

FILA1 = ['A','C','E','G','I','K','M','O','Q','S','U','W','Y']
FILA2 = ['B','D','F','H','J','L','N','P','R','T','V','X','Z']
FILA3 = ['0','1','2','3','4','5','6','7','8','9','+','-']

# ─────────────────────────────────────────
# Morse
# ─────────────────────────────────────────
MORSE = {
    '.-':'A',   '-...':'B', '-.-.':'C', '-..':'D',
    '.':'E',    '..-.':'F', '--.':'G',  '....':'H',
    '..':'I',   '.---':'J', '-.-':'K',  '.-..':'L',
    '--':'M',   '-.':'N',   '---':'O',  '.--.':'P',
    '--.-':'Q', '.-.':'R',  '...':'S',  '-':'T',
    '..-':'U',  '...-':'V', '.--':'W',  '-..-':'X',
    '-.--':'Y', '--..':'Z',
    '-----':'0', '.----':'1', '..---':'2', '...--':'3',
    '....-':'4', '.....':'5', '-....':'6', '--...':'7',
    '---..':'8', '----.':'9', '.-.-.':'+', '-....-':'-',
}

# ─────────────────────────────────────────
# Estado global compartido
# ─────────────────────────────────────────
codigo_actual  = []      # símbolos del carácter en curso
morse_acumulado = ""     # string para el servidor HTTP

boton_presionado = False
boton_inicio_ms  = 0
pausa_inicio_ms  = 0

# ─────────────────────────────────────────
# Funciones de LEDs
# ─────────────────────────────────────────
def shift_out_16(valor):
    for i in range(15, -1, -1):
        DATA_PIN.value((valor >> i) & 1)
        CLK_PIN.on()
        time.sleep_us(100)
        CLK_PIN.off()
        time.sleep_us(100)

def apagar_todo():
    shift_out_16(0)
    LED_FILA1.off()
    LED_FILA2.off()
    LED_FILA3.off()

def mostrar_caracter(char):
    char = char.upper()
    apagar_todo()
    if char in FILA1:
        led_num = FILA1.index(char) + 1
        LED_FILA1.on()
    elif char in FILA2:
        led_num = FILA2.index(char) + 1
        LED_FILA2.on()
    elif char in FILA3:
        led_num = FILA3.index(char) + 1
        LED_FILA3.on()
    else:
        print("Símbolo no reconocido:", char)
        return
    shift_out_16(LED_BITS.get(led_num, 0))
    print("Mostrando:", char, "→ LED", led_num)

# ─────────────────────────────────────────
# Decodificar y mostrar letra completa
# ─────────────────────────────────────────
def procesar_letra():
    global morse_acumulado
    if not codigo_actual:
        return
    clave = ''.join(codigo_actual)
    letra = MORSE.get(clave, f'desconocido({clave})')
    print(f' → {letra}')
    codigo_actual.clear()
    morse_acumulado += clave + " "   # guarda los símbolos para el servidor
    if 'desconocido' not in letra:
        mostrar_caracter(letra)

# ─────────────────────────────────────────
# Leer botón (no bloqueante)
# ─────────────────────────────────────────
def revisar_boton():
    global boton_presionado, boton_inicio_ms, pausa_inicio_ms

    estado = boton.value()  # 0 = presionado

    if estado == 0 and not boton_presionado:
        # Flanco de bajada: empieza pulsación
        boton_presionado = True
        boton_inicio_ms  = time.ticks_ms()
        led.on()
        buzzer.duty_u16(15000)

    elif estado == 1 and boton_presionado:
        # Flanco de subida: termina pulsación
        boton_presionado = False
        duracion = time.ticks_diff(time.ticks_ms(), boton_inicio_ms)
        led.off()
        buzzer.duty_u16(0)

        simbolo = '.' if duracion < TIEMPO_PUNTO_RAYA else '-'
        codigo_actual.append(simbolo)
        print(simbolo, end='')
        pausa_inicio_ms = time.ticks_ms()   # reinicia el contador de pausa

    elif estado == 1 and not boton_presionado and codigo_actual:
        # Botón suelto: mide si ya pasó el tiempo de pausa entre letras
        if time.ticks_diff(time.ticks_ms(), pausa_inicio_ms) > TIEMPO_ESPACIO:
            procesar_letra()

# ─────────────────────────────────────────
# WiFi
# ─────────────────────────────────────────
def conectar_wifi():
    red = network.WLAN(network.STA_IF)
    red.active(True)
    red.connect(SSID, PASSWORD)
    print("Conectando al WiFi", end="")
    intentos = 0
    while not red.isconnected():
        print(".", end="")
        time.sleep(0.5)
        intentos += 1
        if intentos > 30:
            print("\nNo se pudo conectar")
            return None
    ip = red.ifconfig()[0]
    print(f"\nConectado IP: {ip}")
    return ip

# ─────────────────────────────────────────
# Servidor HTTP
# ─────────────────────────────────────────
def crear_servidor():
    srv = socket.socket()
    srv.bind(("", 80))
    srv.listen(5)
    srv.setblocking(False)
    return srv

def responder(cliente, cuerpo, estado="200 OK"):
    r = (
        f"HTTP/1.1 {estado}\r\n"
        f"Content-Type: text/plain\r\n"
        f"Content-Length: {len(cuerpo)}\r\n"
        f"\r\n"
        f"{cuerpo}"
    )
    cliente.send(r.encode())
    cliente.close()

def manejar_peticion(cliente):
    global morse_acumulado, unidad
    datos = ""
    try:
        while "\r\n" not in datos:
            chunk = cliente.recv(1024).decode()
            if not chunk:
                break
            datos += chunk
    except:
        pass

    if not datos:
        cliente.close()
        return

    partes = datos.split("\r\n")[0].split(" ")
    if len(partes) < 2:
        cliente.close()
        return

    ruta = partes[1]
    print(f"Petición: {ruta}")

    if ruta in ("/", "/index.html"):
        responder(cliente, "Servidor Morse activo OK")
    elif ruta == "/GET_MORSE":
        responder(cliente, morse_acumulado)
        morse_acumulado = ""
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

# ─────────────────────────────────────────
# Main
# ─────────────────────────────────────────
def main():
    apagar_todo()
    ip = conectar_wifi()
    if ip is None:
        return
    servidor = crear_servidor()
    print(f"Servidor HTTP listo en http://{ip}")
    print("Presiona el botón para escribir en Morse...")

    while True:
        # Atender petición HTTP si llega
        try:
            cliente, _ = servidor.accept()
            cliente.setblocking(True)
            manejar_peticion(cliente)
        except OSError:
            pass

        # Leer botón Morse
        revisar_boton()

        time.sleep_ms(10)

main()
