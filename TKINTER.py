from tkinter import *
import requests
import threading
import time
import random

# ─── Config global ────────────────────────────────────────────
PICO_IP = None
INTERVALO = 0.4

UNIDADES = {"A": 0.2, "B": 0.3}
unidad_actual = "A"

def Get_unidad():
    return UNIDADES[unidad_actual]

# ─── Palabras del juego ───────────────────────────────────────
PALABRAS = ["SI", "SOS", "NO", "AURA", "DAVO", "TRIPLET", "QUIEROKEKE", "MESSI", "COPILOT", "67"]

# ─── Diccionario morse ────────────────────────────────────────
# Mapa de simbolos morse a su letra/numero equivalente
MORSE_A_TEXTO = {
    ".-": "A",    "-...": "B",  "-.-.": "C",  "-..": "D",
    ".": "E",     "..-.": "F",  "--.": "G",   "....": "H",
    "..": "I",    ".---": "J",  "-.-": "K",   ".-..": "L",
    "--": "M",    "-.": "N",    "---": "O",   ".--.": "P",
    "--.-": "Q",  ".-.": "R",   "...": "S",   "-": "T",
    "..-": "U",   "...-": "V",  ".--": "W",   "-..-": "X",
    "-.--": "Y",  "--..": "Z",
    ".----": "1", "..---": "2", "...--": "3", "....-": "4",
    ".....": "5", "-....": "6", "--...": "7", "---..": "8",
    "----.": "9", "-----": "0",
    ".-.-.": "+", "-....-": "-",
}

def Decodificar_simbolo(simbolo):
    return MORSE_A_TEXTO.get(simbolo, '')

# Recibe un string tipo ".- . ---" y lo convierte letra por letra
def Decodificar_cadena(morse):
    resultado = ''
    for simbolo in morse.split():
        resultado += Decodificar_simbolo(simbolo)
    return resultado

print(Decodificar_cadena('.- . ---')) # testing

# ─── HTTP ─────────────────────────────────────────────────────
def Enviar_comando(ruta):
    if PICO_IP is None:
        return None
    
    try:
        r = requests.get(f'{PICO_IP}/{ruta}', timeout=4)
        clean_r = r.text.strip()
        return clean_r
    except Exception as e:
        print(f'Error de conexion: {e}')
        return None

def Conectar(Ent_ip, Lbl_conexion):
    global PICO_IP
    ip = Ent_ip.get().strip()
    if not ip:
        Lbl_conexion.config(text='Ingresa una IP', fg=COLOR_ACENTO)
        return

    PICO_IP = f'http://{ip}'
    # Manda LED_ON como ping para verificar que la Pico responde
    respuesta = Enviar_comando('LED_ON')
    if respuesta is not None:
        Lbl_conexion.config(text=f'Conectado a {ip}', fg=COLOR_VERDE)
    else:
        Lbl_conexion.config(text='No se pudo conectar', fg=COLOR_ACENTO)
        PICO_IP = None

def Cambiar_unidad(Var_unidad, Lbl_vel_info):
    global unidad_actual
    unidad_actual = Var_unidad.get()
    u = Get_unidad()
    Lbl_vel_info.config(text=f'1U={u:.1f}s  -  raya>={u*2:.1f}s  -  letra>{u*3:.1f}s  -  palabra>{u*7:.1f}s')

def Iniciar_Juego(Ent_j1, Ent_j2, Lbl_error):
    global nombre_j1, nombre_j2
    nombre_j1 = Ent_j1.get().strip()
    nombre_j2 = Ent_j2.get().strip()
    if not nombre_j1:
        Lbl_error.config(text="Ingresa el nombre del Jugador 1")
        return
    if not nombre_j2:
        Lbl_error.config(text="Ingresa el nombre del Jugador 2")
        return

    Lbl_nombre1.config(text=nombre_j1)
    Lbl_nombre2.config(text=nombre_j2)
    CambiarPantalla(Contenedor_Pantalla_Juego)

def CambiarPantalla(nueva):
    global pantalla_actual
    pantalla_actual.pack_forget()
    nueva.pack(fill=BOTH, expand=True)
    pantalla_actual = nueva

# Colores y estilos
BG = "#0f0f1a"
COLOR_PANEL = "#1a1a2e"
COLOR_ACENTO = "#e94560"
COLOR_ACENTO2 = "#0f3460"
COLOR_TEXTO = "#eaeaea"
COLOR_GRIS = "#555577"
COLOR_VERDE = "#2ecc71"
COLOR_AMARILLO = "#f1c40f"
FUENTE = 'Minecraft'
FONT_TITLE = (FUENTE, 22, "bold")
FONT_GRANDE   = (FUENTE, 16, "bold")
FONT_MEDIANA   = (FUENTE, 12)
FONT_PUEQUENA = (FUENTE, 10)

nombre_j1 = ''
nombre_j2 = ""

Lbl_morse_raw = None
Lbl_boton_texto = None
Lbl_simbolos = None
Lbl_char_actual = None
Lbl_teclado_texto = None
Lbl_estado_tec = None


# ======== VENTANA PRINCIPAL ===============
VENTANA = Tk()
Contenedor_Pantalla_Config = Frame(VENTANA, bg=BG)
Contenedor_Pantalla_Config.pack(fill=BOTH, expand=True)
pantalla_actual = Contenedor_Pantalla_Config

VENTANA.title('STRANGER TEC')
VENTANA.configure(bg=BG)
VENTANA.resizable(False, False)

for w in Contenedor_Pantalla_Config.winfo_children():
    w.destroy()

Lbl_titulo = Label(Contenedor_Pantalla_Config, text='BATALLA MORSE', font=FONT_TITLE, fg=COLOR_ACENTO, bg=BG)
Lbl_subtitulo = Label(Contenedor_Pantalla_Config, text='Configuracion Inicial', font=FONT_PUEQUENA, fg=COLOR_GRIS, bg=BG)
Lbl_separador1 = Label(Contenedor_Pantalla_Config, text='=' * 60, font=FONT_PUEQUENA, fg=COLOR_GRIS, bg=BG)

Lbl_titulo.pack(pady=(24,4))
Lbl_subtitulo.pack()
Lbl_separador1.pack(pady=4)

Lbl_seccion_jugadores = Label(Contenedor_Pantalla_Config, text='JUGADORES', font=FONT_GRANDE, fg=COLOR_TEXTO, bg=BG)
Lbl_seccion_jugadores.pack()

Frm_jugadores = Frame(Contenedor_Pantalla_Config, bg=BG)
Lbl_jugador1 = Label(Frm_jugadores, text='Jugador 1:', fg=COLOR_ACENTO, bg=BG, font=FONT_MEDIANA)
Ent_jugador1 = Entry(Frm_jugadores, width=18, bg=COLOR_PANEL, fg=COLOR_TEXTO, insertbackground=COLOR_TEXTO, font=FONT_MEDIANA, relief=FLAT, bd=4)
Lbl_jugador2 = Label(Frm_jugadores, text='Jugador 2:', fg=COLOR_ACENTO, bg=BG, font=FONT_MEDIANA)
Ent_jugador2 = Entry(Frm_jugadores, width=18, bg=COLOR_PANEL, fg=COLOR_TEXTO, insertbackground=COLOR_TEXTO, font=FONT_MEDIANA, relief=FLAT, bd=4)

Frm_jugadores.pack(pady=8)
Lbl_jugador1.grid(row=0, column=0, sticky='e', padx=6, pady=8)
Ent_jugador1.grid(row=0, column=1, padx=6)
Lbl_jugador2.grid(row=1, column=0, sticky="e", padx=6, pady=8)
Ent_jugador2.grid(row=1, column=1, padx=6)

Lbl_separador2 = Label(Contenedor_Pantalla_Config, text='=' * 60, font=FONT_PUEQUENA, fg=COLOR_GRIS, bg=BG)
Lbl_separador2.pack(pady=4)

Lbl_text_pico = Label(Contenedor_Pantalla_Config, text='CONEXION PICO W', font=FONT_GRANDE, fg=COLOR_TEXTO, bg=BG)
Lbl_text_pico.pack()

Frm_ip = Frame(Contenedor_Pantalla_Config, bg=BG)
Frm_ip.pack(pady=6)
Lbl_ip = Label(Frm_ip, text="IP:", fg=COLOR_TEXTO, font=FONT_MEDIANA, bg=BG)
Lbl_ip.pack(side=LEFT)
Ent_ip = Entry(Frm_ip, width=16, bg=COLOR_PANEL, fg=COLOR_TEXTO, insertbackground=COLOR_TEXTO, relief=FLAT, bd=4, font=FONT_MEDIANA)
Ent_ip.pack(side=LEFT, padx=10)

Lbl_conexion = Label(Contenedor_Pantalla_Config, text='Sin conectar', fg=COLOR_GRIS, bg=BG, font=FONT_PUEQUENA)
Lbl_conexion.pack()

def FUNC_Btn_conectar():
    global Lbl_conexion, Ent_ip
    Conectar(Ent_ip, Lbl_conexion)
Btn_conectar = Button(Contenedor_Pantalla_Config, text='Conectar', bg=COLOR_ACENTO2, fg=COLOR_TEXTO,
                      relief=FLAT, padx=12, pady=4, command=FUNC_Btn_conectar, font=FONT_MEDIANA)
Btn_conectar.pack(pady=4)

Lbl_separador3 = Label(Contenedor_Pantalla_Config, text='=' * 50, font=FONT_PUEQUENA, fg=COLOR_GRIS, bg=BG)
Lbl_separador3.pack(pady=4)
Lbl_seccion_velocidad = Label(Contenedor_Pantalla_Config, text='VELOCIDAD DE UNIDAD', font=FONT_GRANDE, fg=COLOR_TEXTO, bg=BG)
Lbl_seccion_velocidad.pack()

Var_unidad = StringVar(value=unidad_actual)
unidad0 = Get_unidad()
Lbl_vel_info = Label(Contenedor_Pantalla_Config, fg=COLOR_GRIS, bg=BG, font=FONT_PUEQUENA,
                     text=f'1U={unidad0:.1f}s  -  raya>={unidad0*2:.1f}s  -  letra>{unidad0*3:.1f}s  -  palabra>{unidad0*7:.1f}s')
Frm_vel = Frame(Contenedor_Pantalla_Config, bg=BG)

def FUNC_Rbt_a():
    global Var_unidad, Lbl_vel_info
    Cambiar_unidad(Var_unidad, Lbl_vel_info)
Rbt_a = Radiobutton(Frm_vel, text='A (0.2 s/unidad)', variable=Var_unidad, value='A',
                    bg=BG, fg=COLOR_TEXTO, selectcolor=COLOR_PANEL, font=FONT_MEDIANA,
                    command=FUNC_Rbt_a)

def FUNC_Rbt_b():
    global Var_unidad, Lbl_vel_info
    Cambiar_unidad(Var_unidad, Lbl_vel_info)
Rbt_b = Radiobutton(Frm_vel, text='B (0.3 s/unidad)', variable=Var_unidad, value='B',
                    bg=BG, fg=COLOR_TEXTO, selectcolor=COLOR_PANEL, font=FONT_MEDIANA,
                    command=FUNC_Rbt_b)

Frm_vel.pack(pady=6)
Rbt_a.pack(side=LEFT, padx=12)
Rbt_b.pack(side=LEFT, padx=12)
Lbl_vel_info.pack(pady=2)

Lbl_separador4 = Label(Contenedor_Pantalla_Config, text='=' * 50, font=FONT_PUEQUENA, fg=COLOR_GRIS, bg=BG)
Lbl_separador4.pack(pady=4)
Lbl_error = Label(Contenedor_Pantalla_Config, text='', fg=COLOR_ACENTO, bg=BG, font=FONT_PUEQUENA)
Lbl_error.pack()

def FUNC_Btn_iniciar():
    global Ent_jugador1, Ent_jugador2, Lbl_error
    Iniciar_Juego(Ent_jugador1, Ent_jugador2, Lbl_error)

Btn_iniciar = Button(Contenedor_Pantalla_Config, text="▶  INICIAR JUEGO", bg=COLOR_ACENTO,
                     fg='white', font=FONT_GRANDE, relief=FLAT,
                     padx=20, pady=8, command=FUNC_Btn_iniciar)
Btn_iniciar.pack(pady=(4,24))


# ─── Ventana flotante: tabla de referencia morse ──────────────
# Se abre aparte de la ventana principal, no bloquea el juego (Toplevel)
def Abrir_referencia_morse():
    # Si ya hay una ventana abierta la trae al frente en vez de abrir otra
    if hasattr(Abrir_referencia_morse, 'ventana') and Abrir_referencia_morse.ventana.winfo_exists():
        Abrir_referencia_morse.ventana.lift()
        return

    ref = Toplevel(VENTANA)
    ref.title('Referencia Morse')
    ref.configure(bg=BG)
    ref.resizable(False, False)
    Abrir_referencia_morse.ventana = ref  # guardamos referencia para el check de arriba

    Lbl_ref_titulo = Label(ref, text='CODIGO MORSE', font=FONT_GRANDE, fg=COLOR_ACENTO, bg=BG)
    Lbl_ref_titulo.pack(pady=(16, 4))
    Lbl_ref_sep = Label(ref, text='=' * 44, font=FONT_PUEQUENA, fg=COLOR_GRIS, bg=BG)
    Lbl_ref_sep.pack(pady=2)

    # Contenedor principal con dos columnas: letras y numeros/simbolos
    Frm_ref_cuerpo = Frame(ref, bg=BG)
    Frm_ref_cuerpo.pack(padx=20, pady=8)

    Frm_letras  = Frame(Frm_ref_cuerpo, bg=BG)
    Frm_nums    = Frame(Frm_ref_cuerpo, bg=BG)
    Frm_letras.grid(row=0, column=0, padx=16, sticky='n')
    Frm_nums.grid(row=0,   column=1, padx=16, sticky='n')

    # Cabeceras
    Label(Frm_letras, text='LETRA', width=6,  font=FONT_PUEQUENA, fg=COLOR_GRIS, bg=BG).grid(row=0, column=0)
    Label(Frm_letras, text='MORSE', width=10, font=FONT_PUEQUENA, fg=COLOR_GRIS, bg=BG).grid(row=0, column=1)
    Label(Frm_nums,   text='CHAR',  width=6,  font=FONT_PUEQUENA, fg=COLOR_GRIS, bg=BG).grid(row=0, column=0)
    Label(Frm_nums,   text='MORSE', width=10, font=FONT_PUEQUENA, fg=COLOR_GRIS, bg=BG).grid(row=0, column=1)

    # Recorre el diccionario y separa letras de numeros/simbolos
    fila_letras = 1
    fila_nums   = 1
    for simbolo, char in MORSE_A_TEXTO.items():
        if char.isalpha() and fila_letras < 20:
            Label(Frm_letras, text=char,    width=6,  font=FONT_MEDIANA, fg=COLOR_TEXTO,   bg=BG).grid(row=fila_letras, column=0, pady=1)
            Label(Frm_letras, text=simbolo, width=10, font=FONT_MEDIANA, fg=COLOR_AMARILLO, bg=BG).grid(row=fila_letras, column=1, pady=1)
            fila_letras += 1
        else:
            Label(Frm_nums, text=char,    width=6,  font=FONT_MEDIANA, fg=COLOR_TEXTO,   bg=BG).grid(row=fila_nums, column=0, pady=1)
            Label(Frm_nums, text=simbolo, width=10, font=FONT_MEDIANA, fg=COLOR_AMARILLO, bg=BG).grid(row=fila_nums, column=1, pady=1)
            fila_nums += 1

    Lbl_ref_sep2 = Label(ref, text='=' * 44, font=FONT_PUEQUENA, fg=COLOR_GRIS, bg=BG)
    Lbl_ref_sep2.pack(pady=(4, 16))


#---------- PANTALLA JUEGO ------------
def Actualizar_display_teclado():
    global respuesta_teclado
    secuencia = ''.join(tec_simbolos)

    if secuencia:
        texto_simbolos = secuencia
        texto_char = Decodificar_simbolo(secuencia)
    else:
        texto_simbolos = "·"
        texto_char = ""

    Lbl_simbolos.config(text=texto_simbolos)
    Lbl_char_actual.config(text=texto_char)

    texto_actual = ''.join(tec_texto)
    Lbl_teclado_texto.config(text=texto_actual)
    respuesta_teclado = texto_actual
    
def Confirmar_caracter():
    global tec_timer_char

    if tec_timer_char is not None:
        VENTANA.after_cancel(tec_timer_char)
        tec_timer_char = None
    
    secuencia = ''.join(tec_simbolos)
    if secuencia:
        char = Decodificar_simbolo(secuencia)
        tec_texto.append(char)
        tec_simbolos.clear()
        Lbl_estado_tec.config(text=f'{secuencia} → {char}', fg=COLOR_VERDE)
    Actualizar_display_teclado()

def Confirmar_palabra():
    global tec_timer_palabra
    tec_timer_palabra = None
    Confirmar_caracter()

    # Si el ultimo caracter no es espacio, se agrega para separar palabras
    if tec_texto and tec_texto[-1] != ' ':
        tec_texto.append(' ')

    Actualizar_display_teclado()
    Lbl_estado_tec.config(text='- espacio entre palabras -', fg=COLOR_GRIS)

def Espacio_presionado(evento):
    global tec_presionado, tec_t_inicio
    global tec_timer_char, tec_timer_palabra
    if tec_presionado:
        return
    
    # Cancela timers activos antes de empezar una nueva pulsacion
    if tec_timer_char is not None:
        VENTANA.after_cancel(tec_timer_char)
        tec_timer_char = None
    
    if tec_timer_palabra is not None:
        VENTANA.after_cancel(tec_timer_palabra)
        tec_timer_palabra = None

    tec_presionado = True
    tec_t_inicio = time.time()
    Lbl_estado_tec.config(text='● Presionando...', fg=COLOR_ACENTO)

def Espacio_al_soltar(evento):
    global tec_presionado, tec_timer_char, tec_timer_palabra

    if not tec_presionado:
        return
    
    duracion = time.time() - tec_t_inicio
    tec_presionado = False
    unidad = Get_unidad()

    # Menos de 2 unidades = punto, igual o mas = raya
    if duracion < unidad * 2:
        simbolo = '.'
    else:
        simbolo = '-'
    
    tec_simbolos.append(simbolo)
    Actualizar_display_teclado()

    if simbolo == '.':
        Lbl_estado_tec.config(text=f'Punto ({duracion:.2f}s)', fg=COLOR_GRIS)
    else:
        Lbl_estado_tec.config(text=f'Raya ({duracion:.2f}s)', fg=COLOR_GRIS)

    # after() es el timer de tkinter, no bloquea el hilo principal
    tec_timer_char    = VENTANA.after(int(unidad * 3 * 1000), Confirmar_caracter)
    tec_timer_palabra = VENTANA.after(int(unidad * 7 * 1000), Confirmar_palabra)

def Actualizar_label_boton():
    Lbl_boton_texto.config(text=respuesta_boton)

def Cambiar_color_nombre():
    Lbl_morse_raw.config(fg=COLOR_ACENTO)

# Corre en un hilo separado para no congelar la UI mientras espera la respuesta HTTP
def Loop_polling():
    global respuesta_boton
    while True:
        time.sleep(INTERVALO)
        if PICO_IP is None:
            continue
        morse = Enviar_comando('GET_MORSE')
        if morse:
            respuesta_boton += Decodificar_cadena(morse)
            # after(0, ...) es la forma segura de tocar widgets desde un hilo externo
            Lbl_morse_raw.after(0, Cambiar_color_nombre)
            Lbl_boton_texto.after(0, Actualizar_label_boton)

def Reiniciar_pantalla_juego():
    global respuesta_boton, respuesta_teclado, palabra_actual
    global tec_presionado, tec_t_inicio, tec_timer_char, tec_timer_palabra

    respuesta_boton   = ''
    respuesta_teclado = ''
    palabra_actual    = random.choice(PALABRAS)
    tec_presionado    = False
    tec_t_inicio      = 0.0
    tec_simbolos.clear()
    tec_texto.clear()
    tec_timer_char    = None
    tec_timer_palabra = None

    Lbl_nombre1.config(text=nombre_j1)
    Lbl_nombre2.config(text=nombre_j2)
    Lbl_obj_palabra.config(text=palabra_actual)
    Lbl_morse_raw.config(text='Esperando...', fg=COLOR_GRIS)
    Lbl_boton_texto.config(text='')
    Lbl_simbolos.config(text='·')
    Lbl_char_actual.config(text='')
    Lbl_teclado_texto.config(text='')
    Lbl_estado_tec.config(text='Presiona espacio', fg=COLOR_GRIS)

    VENTANA.bind("<KeyPress-space>",   Espacio_presionado)
    VENTANA.bind("<KeyRelease-space>", Espacio_al_soltar)

Contenedor_Pantalla_Juego = Frame(VENTANA, bg=BG)
respuesta_boton   = ''
respuesta_teclado = ''
palabra_actual    = random.choice(PALABRAS)

tec_presionado = False
tec_t_inicio   = 0.0
tec_simbolos   = []
tec_texto      = []
tec_timer_char    = None
tec_timer_palabra = None

# Header
Frm_header = Frame(Contenedor_Pantalla_Juego, bg=COLOR_PANEL)
Frm_header.pack(fill=X)
Lbl_titulo = Label(Frm_header, text='BATALLA MORSE', font=FONT_TITLE, fg=COLOR_ACENTO, bg=COLOR_PANEL)
Lbl_titulo.pack(pady=10)

# Palabra objetivo
Lbl_obj_subtitulo = Label(Contenedor_Pantalla_Juego, text='PALABRA OBJETIVO', font=FONT_PUEQUENA, fg=COLOR_GRIS, bg=BG)
Lbl_obj_subtitulo.pack(pady=(16,2))
Lbl_obj_palabra = Label(Contenedor_Pantalla_Juego, text=palabra_actual, font=(FUENTE, 36, "bold"), fg=COLOR_ACENTO, bg=BG)
Lbl_obj_palabra.pack()
Lbl_separador5 = Label(Contenedor_Pantalla_Juego, text="=" * 60, font=FONT_PUEQUENA, fg=COLOR_GRIS, bg=BG)
Lbl_separador5.pack(pady=4)

# Area jugadores
Frm_arena = Frame(Contenedor_Pantalla_Juego, bg=BG)
Frm_arena.pack(fill=BOTH, expand=True, padx=10)

Frm_col1 = Frame(Frm_arena, bg=COLOR_PANEL)
Frm_col2 = Frame(Frm_arena, bg=COLOR_PANEL)
Frm_col1.grid(row=0, column=0, padx=8, pady=4, sticky="nsew")
Frm_col2.grid(row=0, column=1, padx=8, pady=4, sticky="nsew")
Frm_arena.columnconfigure(0, weight=1)
Frm_arena.columnconfigure(1, weight=1)

# Jugador 1 - recibe datos desde la Pico via HTTP polling
Lbl_nombre1 = Label(Frm_col1, text=nombre_j1, font=FONT_GRANDE, fg=COLOR_ACENTO, bg=COLOR_PANEL)
Lbl_nombre1.pack(pady=(12,2))
Lbl_tipo1 = Label(Frm_col1, text='[BOTON FISICO]', font=FONT_PUEQUENA, fg=COLOR_GRIS, bg=COLOR_PANEL)
Lbl_tipo1.pack()
Lbl_morse_raw = Label(Frm_col1, text='Esperando...', font=(FUENTE, 11), fg=COLOR_GRIS, bg=COLOR_PANEL)
Lbl_morse_raw.pack(pady=(8,2))
Lbl_recivido = Label(Frm_col1, text='Texto Recibido:', font=FONT_PUEQUENA, fg=COLOR_GRIS, bg=COLOR_PANEL)
Lbl_recivido.pack()
Lbl_boton_texto = Label(Frm_col1, text='', font=(FUENTE, 20, "bold"), fg=COLOR_TEXTO, bg=COLOR_PANEL, wraplength=180)
Lbl_boton_texto.pack(pady=(2,12))

# Jugador 2 - usa la barra espaciadora como boton morse
Lbl_nombre2 = Label(Frm_col2, text=nombre_j2, font=FONT_GRANDE, fg=COLOR_AMARILLO, bg=COLOR_PANEL)
Lbl_nombre2.pack(pady=(12,2))
Lbl_tipo2 = Label(Frm_col2, text='[BARRA ESPACIADORA]', font=FONT_PUEQUENA, fg=COLOR_GRIS, bg=COLOR_PANEL)
Lbl_tipo2.pack()
Lbl_sim_sub = Label(Frm_col2, text='Simbolo actual:', font=FONT_PUEQUENA, fg=COLOR_GRIS, bg=COLOR_PANEL)
Lbl_sim_sub.pack(pady=(8,0))
Lbl_simbolos = Label(Frm_col2, text='.', font=(FUENTE, 14), fg=COLOR_ACENTO2, bg=COLOR_PANEL)
Lbl_simbolos.pack()
Lbl_char_sub = Label(Frm_col2, text='Caracter', font=FONT_PUEQUENA, fg=COLOR_GRIS, bg=COLOR_PANEL)
Lbl_char_sub.pack()
Lbl_char_actual = Label(Frm_col2, text='', font=(FUENTE, 22, "bold"), fg=COLOR_AMARILLO, bg=COLOR_PANEL)
Lbl_acum_sub = Label(Frm_col2, text='Texto acumulado:', font=FONT_PUEQUENA, fg=COLOR_GRIS, bg=COLOR_PANEL)
Lbl_acum_sub.pack()
Lbl_teclado_texto = Label(Frm_col2, text='', font=(FUENTE, 20, "bold"), fg=COLOR_TEXTO, bg=COLOR_PANEL, wraplength=180)
Lbl_teclado_texto.pack(pady=(2,2))
Lbl_estado_tec = Label(Frm_col2, text='Presiona espacio', font=FONT_PUEQUENA, fg=COLOR_GRIS, bg=COLOR_PANEL)
Lbl_estado_tec.pack(pady=(0,12))

# Botones inferiores: resultado y referencia morse
Lbl_separador6 = Label(Contenedor_Pantalla_Juego, text='=' * 60, font=FONT_PUEQUENA, fg=COLOR_GRIS, bg=BG)
Lbl_separador6.pack(pady=4)

Frm_botones_juego = Frame(Contenedor_Pantalla_Juego, bg=BG)
Frm_botones_juego.pack(pady=(4, 20))

def FUNC_Btn_resultado():
    Confirmar_caracter()
    Poblar_pantalla_puntajes()
    CambiarPantalla(Contenedor_Pantalla_Puntaje)
    VENTANA.unbind("<KeyPress-space>")
    VENTANA.unbind("<KeyRelease-space>")

Btn_resultado = Button(Frm_botones_juego, text='CALCULAR RESULTADO', command=FUNC_Btn_resultado,
                       bg=COLOR_VERDE, fg="#0f0f1a", font=FONT_GRANDE, relief=FLAT,
                       padx=16, pady=8)
Btn_resultado.pack(side=LEFT, padx=8)

# Abre la ventana flotante de referencia sin interrumpir el juego
Btn_referencia = Button(Frm_botones_juego, text='REFERENCIA MORSE', command=Abrir_referencia_morse,
                        bg=COLOR_ACENTO2, fg=COLOR_TEXTO, font=FONT_GRANDE, relief=FLAT,
                        padx=16, pady=8)
Btn_referencia.pack(side=LEFT, padx=8)

VENTANA.bind("<KeyPress-space>",   Espacio_presionado)
VENTANA.bind("<KeyRelease-space>", Espacio_al_soltar)

hilo = threading.Thread(target=Loop_polling, daemon=True)
hilo.start()


# =========== PANTALLA RESULTADOS ===========
def Calcular_puntos(objetivo, respuesta):
    puntos = 0
    for i, char in enumerate(objetivo):
        if i < len(respuesta) and respuesta[i] == char:
            puntos += 1
    return puntos

def Mostrar_comparacion(padre, etiqueta, texto, objetivo, color_label):
    Frm_fila = Frame(padre, bg=BG)
    Lbl_etiqueta = Label(Frm_fila, text=f'{etiqueta:<14}', font=(FUENTE, 11), fg=color_label, bg=BG)
    Frm_fila.pack(anchor='w', pady=1)
    Lbl_etiqueta.pack(side=LEFT)

    if not texto:
        Lbl_vacio = Label(Frm_fila, text='(vacio)', font=(FUENTE, 11), fg=COLOR_GRIS, bg=BG)
        Lbl_vacio.pack(side=LEFT)
        return
    
    # Colorea verde si el caracter coincide con el objetivo, rojo si no
    for i, char in enumerate(texto):
        if char == " ":
            Label(Frm_fila, text=" ", font=(FUENTE, 14, "bold"), bg=BG).pack(side=LEFT)
            continue
        if i < len(objetivo) and objetivo[i] == char:
            color = COLOR_VERDE
        else:
            color = COLOR_ACENTO
        Label(Frm_fila, text=char, font=(FUENTE, 14, "bold"), fg=color, bg=BG).pack(side=LEFT)

def Poblar_pantalla_puntajes():
    # Limpia el frame antes de rellenarlo para que sirva en rondas sucesivas
    for w in Contenedor_Pantalla_Puntaje.winfo_children():
        w.destroy()

    objetivo  = palabra_actual.replace(' ', '')
    r_boton   = respuesta_boton.replace(' ', '').upper()
    r_teclado = respuesta_teclado.replace(' ', '').upper()

    puntos1 = Calcular_puntos(objetivo, r_boton)
    puntos2 = Calcular_puntos(objetivo, r_teclado)

    Lbl_titulo_respuesta = Label(Contenedor_Pantalla_Puntaje, text='RESULTADO', font=FONT_TITLE, fg=COLOR_ACENTO, bg=BG)
    Lbl_titulo_respuesta.pack(pady=(24,4))
    Lbl_objetivo = Label(Contenedor_Pantalla_Puntaje, text=f'Palabra objetivo:  {palabra_actual}', font=FONT_GRANDE, fg=COLOR_TEXTO, bg=BG)
    Lbl_objetivo.pack(pady=4)
    Lbl_separador7 = Label(Contenedor_Pantalla_Puntaje, text='=' * 55, font=FONT_PUEQUENA, fg=COLOR_GRIS, bg=BG)
    Lbl_separador7.pack(pady=4)

    Frm_tabla = Frame(Contenedor_Pantalla_Puntaje, bg=BG)
    Frm_tabla.pack(pady=8)

    Lbl_tabla_vacio = Label(Frm_tabla, text='',          width=4,  font=FONT_MEDIANA, fg=COLOR_GRIS, bg=BG)
    Lbl_tabla_jug   = Label(Frm_tabla, text='Jugador',   width=18, font=FONT_MEDIANA, fg=COLOR_GRIS, bg=BG)
    Lbl_tabla_resp  = Label(Frm_tabla, text='Respuesta', width=20, font=FONT_MEDIANA, fg=COLOR_GRIS, bg=BG)
    Lbl_tabla_pts   = Label(Frm_tabla, text='Puntos',    width=8,  font=FONT_MEDIANA, fg=COLOR_GRIS, bg=BG)
    Lbl_tabla_vacio.grid(row=0, column=0, padx=4, pady=2)
    Lbl_tabla_jug.grid(row=0,   column=1, padx=4, pady=2)
    Lbl_tabla_resp.grid(row=0,  column=2, padx=4, pady=2)
    Lbl_tabla_pts.grid(row=0,   column=3, padx=4, pady=2)

    if puntos1 > puntos2:
        color_pts1, color_pts2 = COLOR_VERDE, COLOR_TEXTO
    elif puntos1 < puntos2:
        color_pts1, color_pts2 = COLOR_TEXTO, COLOR_VERDE
    else:
        color_pts1, color_pts2 = COLOR_VERDE, COLOR_VERDE

    Lbl_icono1    = Label(Frm_tabla, text='J1',            width=4,  font=FONT_GRANDE,  fg=COLOR_ACENTO,  bg=BG)
    Lbl_nombre1   = Label(Frm_tabla, text=nombre_j1,       width=18, font=FONT_MEDIANA, fg=COLOR_ACENTO,  bg=BG, anchor='n')
    Lbl_respuesta1= Label(Frm_tabla, text=r_boton or '—',  width=20, font=(FUENTE, 12), fg=COLOR_TEXTO,   bg=BG, anchor='n')
    Lbl_pts1      = Label(Frm_tabla, text=str(puntos1),    width=8,  font=FONT_GRANDE,  fg=color_pts1,    bg=BG)
    Lbl_icono1.grid(row=1, column=0, padx=4)
    Lbl_nombre1.grid(row=1, column=1, padx=4)
    Lbl_respuesta1.grid(row=1, column=2, padx=4)
    Lbl_pts1.grid(row=1, column=3, padx=4)

    Lbl_icono2    = Label(Frm_tabla, text='J2',              width=4,  font=FONT_GRANDE,  fg=COLOR_ACENTO,   bg=BG)
    Lbl_nombre2   = Label(Frm_tabla, text=nombre_j2,         width=18, font=FONT_MEDIANA, fg=COLOR_ACENTO,   bg=BG, anchor='n')
    Lbl_respuesta2= Label(Frm_tabla, text=r_teclado or '—',  width=20, font=(FUENTE, 12), fg=COLOR_TEXTO,    bg=BG, anchor='n')
    Lbl_pts2      = Label(Frm_tabla, text=str(puntos2),      width=8,  font=FONT_GRANDE,  fg=color_pts2,     bg=BG)
    Lbl_icono2.grid(row=2, column=0, padx=4)
    Lbl_nombre2.grid(row=2, column=1, padx=4)
    Lbl_respuesta2.grid(row=2, column=2, padx=4)
    Lbl_pts2.grid(row=2, column=3, padx=4)

    Lbl_separador8 = Label(Contenedor_Pantalla_Puntaje, text='=' * 55, font=FONT_PUEQUENA, fg=COLOR_GRIS, bg=BG)
    Lbl_separador8.pack(pady=4)

    Lbl_comparacion_title = Label(Contenedor_Pantalla_Puntaje, text='Comparacion caracter a caracter', font=FONT_MEDIANA, fg=COLOR_GRIS, bg=BG)
    Lbl_comparacion_title.pack(pady=(4,2))

    Frm_comparacion = Frame(Contenedor_Pantalla_Puntaje, bg=BG)
    Frm_comparacion.pack(pady=4)
    Mostrar_comparacion(Frm_comparacion, 'Objetivo',  objetivo,  objetivo, COLOR_GRIS)
    Mostrar_comparacion(Frm_comparacion, nombre_j1,   r_boton,   objetivo, COLOR_ACENTO)
    Mostrar_comparacion(Frm_comparacion, nombre_j2,   r_teclado, objetivo, COLOR_AMARILLO)

    Lbl_separador9 = Label(Contenedor_Pantalla_Puntaje, text='=' * 55, font=FONT_PUEQUENA, fg=COLOR_GRIS, bg=BG)
    Lbl_separador9.pack(pady=4)

    if puntos1 > puntos2:
        ganador, color_g = nombre_j1, COLOR_ACENTO
    elif puntos2 > puntos1:
        ganador, color_g = nombre_j2, COLOR_AMARILLO
    else:
        ganador, color_g = 'EMPATE', COLOR_VERDE

    Lbl_ganador_text = Label(Contenedor_Pantalla_Puntaje, text='GANADOR', font=FONT_PUEQUENA, fg=COLOR_GRIS, bg=BG)
    Lbl_ganador_text.pack()
    Lbl_ganador = Label(Contenedor_Pantalla_Puntaje, text=f'🏆  {ganador}', font=(FUENTE, 28, "bold"), fg=color_g, bg=BG)
    Lbl_ganador.pack(pady=4)

    Lbl_separador10 = Label(Contenedor_Pantalla_Puntaje, text='=' * 55, font=FONT_PUEQUENA, fg=COLOR_GRIS, bg=BG)
    Lbl_separador10.pack(pady=4)

    Frm_botones = Frame(Contenedor_Pantalla_Puntaje, bg=BG)
    Frm_botones.pack(pady=(4, 24))

    def FUNC_Btn_otra_ronda():
        Reiniciar_pantalla_juego()
        CambiarPantalla(Contenedor_Pantalla_Juego)

    def FUNC_Btn_nueva_config():
        CambiarPantalla(Contenedor_Pantalla_Config)

    Btn_otra   = Button(Frm_botones, text='OTRA RONDA',   command=FUNC_Btn_otra_ronda,
                        bg=COLOR_ACENTO2, fg=COLOR_TEXTO, font=FONT_MEDIANA, relief=FLAT, padx=12, pady=6)
    Btn_config = Button(Frm_botones, text='NUEVA CONFIG', command=FUNC_Btn_nueva_config,
                        bg=COLOR_PANEL,   fg=COLOR_TEXTO, font=FONT_MEDIANA, relief=FLAT, padx=12, pady=6)
    Btn_otra.pack(side=LEFT, padx=8)
    Btn_config.pack(side=LEFT, padx=8)

Contenedor_Pantalla_Puntaje = Frame(VENTANA, bg=BG)

VENTANA.mainloop()
