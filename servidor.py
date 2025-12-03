import socket
import threading
import tkinter as tk
from tkinter import scrolledtext, ttk

# =============================================================================
# CONFIGURACIÓN GENERAL Y ESTÉTICA
# =============================================================================
COLOR_HEADER = "#2C3E50"   # Encabezados
COLOR_BG_MAIN = "#ECF0F1"  # Fondo
COLOR_ACCENT = "#27AE60"   # Botón Iniciar
COLOR_STOP = "#C0392B"     # Botón Detener
COLOR_LOGS_BG = "#1E1E1E"  # Fondo Terminal
COLOR_LOGS_FG = "#00FF00"  # Texto Terminal
COLOR_WARNING = "#F39C12"  # Alertas de seguridad

DEFAULT_HOST = "0.0.0.0"   # Escucha en todas las interfaces de red
DEFAULT_PORT = 6000

# =============================================================================
# CONFIGURACIÓN DE SEGURIDAD (REQ: FIREWALL/BLOQUEO)
# =============================================================================
# Lista de prefijos de IP permitidos (Allowlist).
# Cualquier IP que no empiece con estos números será rechazada.
# "127.0.0.1" es el equipo local.
# "192.168." es común en casas.
# "10." es común en escuelas/oficinas grandes (o ITSON).
IPS_PERMITIDAS = ["127.0.0.1", "192.168.", "10.", "172."]

# Variables globales de estado del servidor
server_socket = None
server_running = False

# =============================================================================
# LÓGICA DE CONTROL DEL SERVIDOR
# =============================================================================

def iniciar_servidor():
    """
    Valida la configuración, bloquea la interfaz para evitar cambios 
    y lanza el hilo principal del servidor.
    """
    global server_running
    host = entrada_ip.get()
    try:
        port = int(entrada_port.get())
    except ValueError:
        log_tecnico(">> ERROR: Puerto inválido.")
        return

    # Actualización visual de la GUI
    btn_iniciar.config(state=tk.DISABLED)
    btn_detener.config(state=tk.NORMAL, bg=COLOR_STOP)
    entrada_ip.config(state=tk.DISABLED)
    entrada_port.config(state=tk.DISABLED)
    
    server_running = True
    
    # IMPORTANTE: El servidor se ejecuta en un hilo separado (threading)
    # para no congelar la ventana gráfica principal.
    hilo = threading.Thread(target=ejecutar_servidor, args=(host, port))
    hilo.daemon = True  # El hilo muere si se cierra la ventana principal
    hilo.start()

def detener_servidor():
    """
    Detiene el bucle del servidor y cierra el socket activo.
    Restaura los controles de la interfaz gráfica.
    """
    global server_running, server_socket
    if server_running and server_socket:
        log_tecnico("[SYSTEM] Deteniendo servidor...")
        server_running = False
        try:
            # Al cerrar el socket, se interrumpe el bloqueo de .accept()
            server_socket.close()
        except Exception:
            pass

    # Restaurar estado visual
    btn_iniciar.config(state=tk.NORMAL, text="▶ INICIAR")
    btn_detener.config(state=tk.DISABLED, bg="#95a5a6")
    entrada_ip.config(state=tk.NORMAL)
    entrada_port.config(state=tk.NORMAL)
    log_chat("--- SISTEMA APAGADO ---")

# =============================================================================
# FUNCIONES DE LOGGING (SALIDA A GUI)
# =============================================================================

def log_chat(mensaje):
    """Muestra mensajes limpios en la columna izquierda (Chat)."""
    txt_chat.config(state=tk.NORMAL)
    txt_chat.insert(tk.END, mensaje + "\n")
    txt_chat.see(tk.END)
    txt_chat.config(state=tk.DISABLED)

def log_tecnico(mensaje, alerta=False):
    """
    Muestra logs técnicos y tráfico HTTP en la columna derecha (Terminal).
    Si alerta=True, resalta el texto en color naranja (para seguridad).
    """
    txt_logs.config(state=tk.NORMAL)
    
    if alerta:
        txt_logs.insert(tk.END, mensaje + "\n", "warning")
    else:
        txt_logs.insert(tk.END, mensaje + "\n")
        
    txt_logs.see(tk.END)
    txt_logs.config(state=tk.DISABLED)

# =============================================================================
# LÓGICA DE RED Y PROTOCOLOS (CORE DEL PROYECTO)
# =============================================================================

def verificar_seguridad(ip_cliente):
    """
    Simula un Firewall de capa de aplicación
    Verifica si la IP entrante está en la lista blanca.
    
    Args:
        ip_cliente (str): La dirección IP del cliente conectado.
    Returns:
        bool: True si es permitida, False si debe bloquearse.
    """
    for prefijo in IPS_PERMITIDAS:
        if ip_cliente.startswith(prefijo):
            return True
    return False

def ejecutar_servidor(host, port):
    """
    Función principal que implementa el servidor TCP/HTTP.
    Maneja el ciclo de vida: Bind -> Listen -> Accept -> Recv -> Send.
    """
    global server_socket
    try:
        # Creación del socket TCP (SOCK_STREAM)
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((host, port))
        server_socket.listen()
        
        log_chat(f"--- SERVIDOR EN LÍNEA ---")
        log_tecnico(f"[FIREWALL] Política activa: Solo redes locales.")
        log_tecnico(f"[SYSTEM] Escuchando en {host}:{port}")

        while server_running:
            try:
                # 1. ESPERA DE CONEXIÓN
                conn, addr = server_socket.accept()
                ip_cliente = addr[0]

                # 2. VERIFICACIÓN DE SEGURIDAD (SIMULACIÓN DE FIREWALL)
                if not verificar_seguridad(ip_cliente):
                    log_tecnico(f"[SECURITY ALERT] Conexión BLOQUEADA desde {ip_cliente}", alerta=True)
                    conn.close() # Cierre forzado
                    continue     # Ignorar esta conexión
                
                # 3. Procesamiento de conexión permitida
                with conn:
                    log_tecnico(f"\n[EVENT] Conexión aceptada: {ip_cliente}")
                    
                    # Recepción de datos crudos
                    data = conn.recv(1024).decode("utf-8", "ignore")
                    
                    # --- PETICIÓN HTTP ---
                    log_tecnico(f"[RX RAW DATA] >>\n{data.strip()}\n{'-'*30}") 
                    # ----------------------------------------------------------------

                    # 4. PROCESAR MENSAJE
                    mensaje_cliente = "(Sin mensaje)"

                    for linea in data.split("\r\n"):
                        if linea.lower().startswith("user-message:"):
                            mensaje_cliente = linea.split(":", 1)[1].strip()
                            break

                    if mensaje_cliente != "(Sin mensaje)":
                        log_chat(f"{mensaje_cliente}")

                    # 5. RESPUESTA HTTP
                    cuerpo = f"Servidor recibió: '{mensaje_cliente}'"
                    body_bytes = cuerpo.encode("utf-8")
                    
                    header = (
                        "HTTP/1.1 200 OK\r\n"
                        "Content-Type: text/plain; charset=utf-8\r\n"
                        f"Content-Length: {len(body_bytes)}\r\n"
                        "\r\n"
                    )
                    
                    # Envío final
                    conn.sendall(header.encode("utf-8") + body_bytes)  
                    log_tecnico(f"[TX RESPONSE] >>\n{header.strip()}") 
            
            except OSError:
                # Ocurre cuando se cierra el socket manualmente
                break

    except Exception as e:
        if server_running:
            log_tecnico(f"[ERROR] {e}")
    finally:
        if server_socket:
            server_socket.close()

# =============================================================================
# CONSTRUCCIÓN DE LA INTERFAZ GRÁFICA (GUI)
# =============================================================================
root = tk.Tk()
root.title("SERVIDOR SEGURO - REDES")
root.geometry("1000x550")
root.configure(bg=COLOR_BG_MAIN)

# --- Panel Superior (Configuración) ---
frame_top = tk.Frame(root, bg=COLOR_HEADER, pady=15, padx=15)
frame_top.pack(fill=tk.X)

tk.Label(frame_top, text="IP:", bg=COLOR_HEADER, fg="white").pack(side=tk.LEFT)
entrada_ip = tk.Entry(frame_top, width=12, justify="center")
entrada_ip.insert(0, DEFAULT_HOST)
entrada_ip.pack(side=tk.LEFT, padx=5)

tk.Label(frame_top, text="Puerto:", bg=COLOR_HEADER, fg="white").pack(side=tk.LEFT)
entrada_port = tk.Entry(frame_top, width=6, justify="center")
entrada_port.insert(0, str(DEFAULT_PORT))
entrada_port.pack(side=tk.LEFT, padx=5)

btn_detener = tk.Button(frame_top, text="⏹ DETENER", command=detener_servidor, 
                        bg="#95a5a6", fg="white", font=("Verdana", 9, "bold"), bd=0, padx=10, state=tk.DISABLED)
btn_detener.pack(side=tk.RIGHT, padx=(5, 0))

btn_iniciar = tk.Button(frame_top, text="▶ INICIAR", command=iniciar_servidor, 
                        bg=COLOR_ACCENT, fg="white", font=("Verdana", 9, "bold"), bd=0, padx=15)
btn_iniciar.pack(side=tk.RIGHT)

# --- Panel Principal (Dividido) ---
panel = tk.PanedWindow(root, orient=tk.HORIZONTAL, sashrelief=tk.FLAT, sashwidth=4, bg="#BDC3C7")
panel.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

# Columna 1: Chat Visual
frame_chat = tk.Frame(panel, bg="white")
tk.Label(frame_chat, text="CHAT", bg="#ECF0F1", font=("Verdana", 8, "bold"), anchor="w", padx=5).pack(fill=tk.X)
txt_chat = scrolledtext.ScrolledText(frame_chat, width=40, font=("Verdana", 10), state=tk.DISABLED, padx=10, pady=10)
txt_chat.pack(fill=tk.BOTH, expand=True)
panel.add(frame_chat, stretch="always")

# Columna 2: Monitor
frame_logs = tk.Frame(panel, bg=COLOR_LOGS_BG)
tk.Label(frame_logs, text="TERMINAL (PROTOCOLOS Y SEGURIDAD)", bg="#333", fg="white", font=("Consolas", 8, "bold"), anchor="w", padx=5).pack(fill=tk.X)
txt_logs = scrolledtext.ScrolledText(frame_logs, width=40, bg=COLOR_LOGS_BG, fg=COLOR_LOGS_FG, 
                                     font=("Consolas", 9), state=tk.DISABLED, padx=10, pady=10)
txt_logs.tag_config("warning", foreground=COLOR_WARNING) 

txt_logs.pack(fill=tk.BOTH, expand=True)
panel.add(frame_logs, stretch="always")

root.mainloop()