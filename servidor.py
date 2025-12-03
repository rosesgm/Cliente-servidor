import socket
import threading
import tkinter as tk
from tkinter import scrolledtext, ttk

# --- Configuración Visual ---
COLOR_HEADER = "#2C3E50"
COLOR_BG_MAIN = "#ECF0F1"
COLOR_ACCENT = "#27AE60"
COLOR_STOP = "#C0392B"
COLOR_LOGS_BG = "#1E1E1E"
COLOR_LOGS_FG = "#00FF00"
COLOR_WARNING = "#F39C12"

DEFAULT_HOST = "0.0.0.0"
DEFAULT_PORT = 6000

# --- CONFIGURACIÓN DE SEGURIDAD (FIREWALL) ---
# Lista de inicios de IP permitidos.
# "127.0.0.1" es tu propia PC.
# "192.168." es común en casas.
# "10." es común en escuelas/oficinas grandes.
IPS_PERMITIDAS = ["127.0.0.1", "192.168.", "10.", "172."]

# Variables globales
server_socket = None
server_running = False

def iniciar_servidor():
    global server_running
    host = entrada_ip.get()
    try:
        port = int(entrada_port.get())
    except ValueError:
        log_tecnico(">> ERROR: Puerto inválido.")
        return

    btn_iniciar.config(state=tk.DISABLED)
    btn_detener.config(state=tk.NORMAL, bg=COLOR_STOP)
    entrada_ip.config(state=tk.DISABLED)
    entrada_port.config(state=tk.DISABLED)
    
    server_running = True
    
    # Iniciar hilo
    hilo = threading.Thread(target=ejecutar_servidor, args=(host, port))
    hilo.daemon = True
    hilo.start()

def detener_servidor():
    global server_running, server_socket
    if server_running and server_socket:
        log_tecnico("[SYSTEM] Deteniendo servidor...")
        server_running = False
        try:
            server_socket.close()
        except Exception:
            pass

    btn_iniciar.config(state=tk.NORMAL, text="▶ INICIAR")
    btn_detener.config(state=tk.DISABLED, bg="#95a5a6")
    entrada_ip.config(state=tk.NORMAL)
    entrada_port.config(state=tk.NORMAL)
    log_chat("--- SISTEMA APAGADO ---")

def log_chat(mensaje):
    txt_chat.config(state=tk.NORMAL)
    txt_chat.insert(tk.END, mensaje + "\n")
    txt_chat.see(tk.END)
    txt_chat.config(state=tk.DISABLED)

def log_tecnico(mensaje, alerta=False):
    """Si alerta=True, pone el texto en color naranja"""
    txt_logs.config(state=tk.NORMAL)
    
    if alerta:
        txt_logs.insert(tk.END, mensaje + "\n", "warning")
    else:
        txt_logs.insert(tk.END, mensaje + "\n")
        
    txt_logs.see(tk.END)
    txt_logs.config(state=tk.DISABLED)

def verificar_seguridad(ip_cliente):
    """Retorna True si la IP es segura, False si se debe bloquear."""
    for prefijo in IPS_PERMITIDAS:
        if ip_cliente.startswith(prefijo):
            return True
    return False

def ejecutar_servidor(host, port):
    global server_socket
    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((host, port))
        server_socket.listen()
        
        log_chat(f"--- SERVIDOR EN LÍNEA ---")
        log_tecnico(f"[FIREWALL] Política activa: Solo redes locales.")
        log_tecnico(f"[SYSTEM] Escuchando en {host}:{port}")

        while server_running:
            try:
                conn, addr = server_socket.accept()
                ip_cliente = addr[0]

                # --- FILTRO DE SEGURIDAD ---
                if not verificar_seguridad(ip_cliente):
                    log_tecnico(f"[SECURITY ALERT] Conexión BLOQUEADA desde {ip_cliente}", alerta=True)
                    conn.close() # Cierra la conexión inmediatamente
                    continue # Vuelve a esperar otra conexión, ignorando esta
                # ---------------------------

                with conn:
                    log_tecnico(f"\n[EVENT] Conexión aceptada: {ip_cliente}")
                    
                    data = conn.recv(1024).decode("utf-8", "ignore")
                    
                    # Procesar mensaje
                    mensaje_cliente = "(Sin mensaje)"
                    for linea in data.split("\r\n"):
                        if linea.lower().startswith("user-message:"):
                            mensaje_cliente = linea.split(":", 1)[1].strip()
                            break

                    if mensaje_cliente != "(Sin mensaje)":
                        log_chat(f"{mensaje_cliente}")

                    # Respuesta
                    cuerpo = f"Servidor recibió: '{mensaje_cliente}'"
                    body_bytes = cuerpo.encode("utf-8")
                    header = (
                        "HTTP/1.1 200 OK\r\n"
                        "Content-Type: text/plain; charset=utf-8\r\n"
                        f"Content-Length: {len(body_bytes)}\r\n"
                        "\r\n"
                    )
                    conn.sendall(header.encode("utf-8") + body_bytes)
                    log_tecnico(f"[TX] Respuesta enviada OK")
            
            except OSError:
                break

    except Exception as e:
        if server_running:
            log_tecnico(f"[ERROR] {e}")
    finally:
        if server_socket:
            server_socket.close()

# --- GUI ---
root = tk.Tk()
root.title("SERVIDOR SEGURO - REDES")
root.geometry("1000x550")
root.configure(bg=COLOR_BG_MAIN)

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

panel = tk.PanedWindow(root, orient=tk.HORIZONTAL, sashrelief=tk.FLAT, sashwidth=4, bg="#BDC3C7")
panel.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

# Columna 1: Chat
frame_chat = tk.Frame(panel, bg="white")
tk.Label(frame_chat, text="CHAT", bg="#ECF0F1", font=("Verdana", 8, "bold"), anchor="w", padx=5).pack(fill=tk.X)
txt_chat = scrolledtext.ScrolledText(frame_chat, width=40, font=("Verdana", 10), state=tk.DISABLED, padx=10, pady=10)
txt_chat.pack(fill=tk.BOTH, expand=True)
panel.add(frame_chat, stretch="always")

# Columna 2: Logs
frame_logs = tk.Frame(panel, bg=COLOR_LOGS_BG)
tk.Label(frame_logs, text="TERMINAL (PROTOCOLOS Y SEGURIDAD)", bg="#333", fg="white", font=("Consolas", 8, "bold"), anchor="w", padx=5).pack(fill=tk.X)
txt_logs = scrolledtext.ScrolledText(frame_logs, width=40, bg=COLOR_LOGS_BG, fg=COLOR_LOGS_FG, 
                                     font=("Consolas", 9), state=tk.DISABLED, padx=10, pady=10)
txt_logs.tag_config("warning", foreground=COLOR_WARNING) 

txt_logs.pack(fill=tk.BOTH, expand=True)
panel.add(frame_logs, stretch="always")

root.mainloop()