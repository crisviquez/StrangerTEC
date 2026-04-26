import tkinter as tk
import requests
import threading
import time

# ─── CONFIGURACIÓN ───────────────────────────────────────────
PICO_IP = None      # Se asigna cuando el usuario la ingresa
INTERVALO = 2.0     # Cada cuántos segundos se consulta la Pico W
# ─────────────────────────────────────────────────────────────


def enviar_comando(ruta):
    """Manda un GET a la Pico W y devuelve el texto de respuesta."""
    if PICO_IP is None:
        return None
    try:
        r = requests.get(f"{PICO_IP}/{ruta}", timeout=3)
        return r.text.strip()
    except Exception as e:
        print(f"Error de conexión: {e}")
        return None


# ─── POLLING EN SEGUNDO PLANO ────────────────────────────────

def iniciar_polling(label_morse, label_estado):
    """
    Corre en un hilo separado para no congelar la interfaz.
    Cada INTERVALO segundos le pregunta a la Pico qué morse capturó.
    """
    def loop():
        while True:
            time.sleep(INTERVALO)
            if PICO_IP is None:
                continue
            morse = enviar_comando("GET_MORSE")
            if morse:
                # Actualiza la interfaz desde el hilo secundario
                # usando after() para que sea thread-safe
                label_morse.after(0, lambda m=morse: label_morse.config(
                    text=f"Morse recibido: {m}"
                ))
                label_estado.after(0, lambda: label_estado.config(
                    text="Dato recibido de la Pico W", fg="green"
                ))

    hilo = threading.Thread(target=loop, daemon=True)
    hilo.start()


# ─── INTERFAZ GRÁFICA ────────────────────────────────────────

def construir_interfaz():
    global PICO_IP

    ventana = tk.Tk()
    ventana.title("Proyecto Pico W")
    ventana.resizable(False, False)

    # — Sección de conexión —
    tk.Label(ventana, text="Conexión con la Pico W",
             font=("Arial", 12, "bold")).pack(pady=(15, 5))

    frame_ip = tk.Frame(ventana)
    frame_ip.pack()

    tk.Label(frame_ip, text="IP:").pack(side=tk.LEFT)
    entrada_ip = tk.Entry(frame_ip, width=18)
    entrada_ip.pack(side=tk.LEFT, padx=5)

    label_conexion = tk.Label(ventana, text="Sin conectar", fg="gray")
    label_conexion.pack(pady=3)

    def conectar():
        global PICO_IP
        ip = entrada_ip.get().strip()
        if not ip:
            label_conexion.config(text="Ingresá una IP", fg="red")
            return
        PICO_IP = f"http://{ip}"
        # Prueba la conexión mandando un comando inofensivo
        resp = enviar_comando("LED_ON")
        if resp is not None:
            label_conexion.config(text=f"Conectado a {ip}", fg="green")
        else:
            label_conexion.config(text="No se pudo conectar", fg="red")
            PICO_IP = None

    tk.Button(ventana, text="Conectar", command=conectar).pack(pady=5)

    tk.Label(ventana, text="─" * 38, fg="gray").pack(pady=5)

    # — Sección de control del LED —
    tk.Label(ventana, text="Control LED",
             font=("Arial", 11, "bold")).pack()

    frame_led = tk.Frame(ventana)
    frame_led.pack(pady=5)

    tk.Button(frame_led, text="LED ON",  bg="yellow",
              command=lambda: enviar_comando("LED_ON")).pack(side=tk.LEFT, padx=8)
    tk.Button(frame_led, text="LED OFF", bg="gray", fg="white",
              command=lambda: enviar_comando("LED_OFF")).pack(side=tk.LEFT, padx=8)

    tk.Label(ventana, text="─" * 38, fg="gray").pack(pady=5)

    # — Sección de morse recibido —
    tk.Label(ventana, text="Morse del botón físico",
             font=("Arial", 11, "bold")).pack()

    label_morse = tk.Label(ventana, text="Morse recibido: —",
                           font=("Courier", 13), fg="navy")
    label_morse.pack(pady=5)

    label_estado = tk.Label(ventana, text="Esperando datos...", fg="gray")
    label_estado.pack(pady=3)

    tk.Label(ventana, text="─" * 38, fg="gray").pack(pady=5)

    # Arranca el hilo de polling
    iniciar_polling(label_morse, label_estado)

    ventana.mainloop()


construir_interfaz()