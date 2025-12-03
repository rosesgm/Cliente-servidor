import socket
import tkinter as tk
from tkinter import scrolledtext, messagebox

# =============================================================================
# CONFIGURACIÓN VISUAL Y VALORES POR DEFECTO
# =============================================================================
COLOR_HEADER = "#2C3E50"   # Azul oscuro
COLOR_BG_MAIN = "#ECF0F1"  # Fondo gris
COLOR_BTN_SEND = "#2980B9" # Botón azul brillante

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 6000
DEFAULT_NAME = "Usuario"

# =============================================================================
# LÓGICA DE COMUNICACIÓN CLIENTE (TCP + HTTP)
# =============================================================================

def enviar():
    """
    Captura el input del usuario, genera una petición HTTP MANUAL,
    envía los datos por TCP y procesa la respuesta del servidor.
    """
    # 1. Obtener datos de la GUI
    host = entrada_ip.get()
    try:
        port = int(entrada_port.get())
    except ValueError:
        messagebox.showerror("Error", "Puerto inválido")
        return

    nombre = entrada_nombre.get()
    mensaje_texto = entrada_mensaje.get()
    if not mensaje_texto: return

    # Formato de mensaje encapsulado para el servidor
    mensaje_final = f"[{nombre}] {mensaje_texto}"
    
    # 2. CONSTRUCCIÓN DEL PROTOCOLO HTTP (REQ: Capa de Aplicación)
    # No usamos librerías como 'requests', construimos el string crudo
    # para demostrar entendimiento del protocolo.
    request = (
        "GET / HTTP/1.1\r\n"
        f"Host: {host}\r\n"
        f"User-Message: {mensaje_final}\r\n" # Header personalizado
        "\r\n"
    )

    try:
        # 3. Establecimiento de conexión TCP
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
            client.settimeout(5) # Evitar que se cuelgue si no hay respuesta
            client.connect((host, port))
            
            # Envío de bytes
            client.sendall(request.encode("utf-8"))
            
            # 4. Recepción de respuesta
            data_raw = client.recv(4096).decode("utf-8", "ignore")
            
            # Separar cabeceras HTTP del cuerpo del mensaje
            try:
                headers, body = data_raw.split("\r\n\r\n", 1)
            except ValueError:
                body = data_raw
            
            # --- LIMPIEZA DE DATOS (UX) ---
            # El servidor envía: "Servidor recibió: '[Nombre] Hola'"
            # Limpiamos el texto para mostrarlo amigablemente en el chat.
            prefix = "Servidor recibió: "
            if body.startswith(prefix):
                body = body[len(prefix):] 
            
            body = body.strip("'") # Quitar comillas remanentes

            # 5. Actualizar interfaz gráfica
            log_chat(f"Yo: {mensaje_texto}", "me")
            log_chat(f"Servidor: {body}", "srv")

        # Limpiar campo de entrada tras envío exitoso
        entrada_mensaje.delete(0, tk.END)

    except Exception as e:
        messagebox.showerror("Error", f"No se pudo conectar.\n\n{e}")

def log_chat(texto, tipo):
    """Muestra el mensaje en la ventana de chat con formato visual."""
    txt_chat.config(state=tk.NORMAL)
    prefix = " ➤ " if tipo == "me" else " ✉ "
    txt_chat.insert(tk.END, prefix + texto + "\n\n")
    txt_chat.see(tk.END)
    txt_chat.config(state=tk.DISABLED)

# =============================================================================
# INTERFAZ GRÁFICA (GUI)
# =============================================================================
root = tk.Tk()
root.title("CLIENTE")
root.geometry("500x600")
root.configure(bg=COLOR_BG_MAIN)

# --- Cabecera de Configuración ---
frame_top = tk.Frame(root, bg=COLOR_HEADER, pady=15, padx=15)
frame_top.pack(fill=tk.X)

# Fila 1: Datos de Conexión
frame_inputs = tk.Frame(frame_top, bg=COLOR_HEADER)
frame_inputs.pack(fill=tk.X)
tk.Label(frame_inputs, text="IP:", bg=COLOR_HEADER, fg="white").pack(side=tk.LEFT)
entrada_ip = tk.Entry(frame_inputs, width=15, justify="center")
entrada_ip.insert(0, DEFAULT_HOST)
entrada_ip.pack(side=tk.LEFT, padx=5)
tk.Label(frame_inputs, text="Port:", bg=COLOR_HEADER, fg="white").pack(side=tk.LEFT)
entrada_port = tk.Entry(frame_inputs, width=6, justify="center")
entrada_port.insert(0, str(DEFAULT_PORT))
entrada_port.pack(side=tk.LEFT, padx=5)

# Fila 2: Datos de Usuario
frame_user = tk.Frame(frame_top, bg=COLOR_HEADER)
frame_user.pack(fill=tk.X, pady=(5,0))
tk.Label(frame_user, text="Usuario:", bg=COLOR_HEADER, fg="white").pack(side=tk.LEFT)
entrada_nombre = tk.Entry(frame_user, width=20)
entrada_nombre.insert(0, DEFAULT_NAME)
entrada_nombre.pack(side=tk.LEFT, padx=5)

# --- Área de Visualización (Chat) ---
frame_chat = tk.Frame(root, bg="white", padx=10, pady=10)
frame_chat.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
txt_chat = scrolledtext.ScrolledText(frame_chat, font=("Verdana", 10), state=tk.DISABLED, bd=0)
txt_chat.pack(fill=tk.BOTH, expand=True)

# --- Área de Envío ---
frame_send = tk.Frame(root, bg=COLOR_BG_MAIN, pady=10, padx=10)
frame_send.pack(fill=tk.X)
entrada_mensaje = tk.Entry(frame_send, font=("Verdana", 11), bd=2, relief=tk.FLAT)
entrada_mensaje.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10), ipady=5)
# Vincular tecla ENTER a la función de envío
entrada_mensaje.bind("<Return>", lambda event: enviar())

btn_enviar = tk.Button(frame_send, text="ENVIAR", command=enviar, bg=COLOR_BTN_SEND, fg="white", font=("Verdana", 9, "bold"), bd=0, padx=20)
btn_enviar.pack(side=tk.RIGHT)

root.mainloop()