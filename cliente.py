# cliente_gui.py
import socket
import tkinter as tk
from tkinter import scrolledtext

HOST = "127.0.0.1"  # Cambia a la IP del servidor si está en otra PC
PORT = 8000


def enviar():
    mensaje = entrada.get()
    if not mensaje:
        return

    # Petición HTTP sencilla con encabezado personalizado
    request = (
        "GET / HTTP/1.1\r\n"
        f"Host: {HOST}\r\n"
        f"User-Message: {mensaje}\r\n"
        "\r\n"
    )

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
        client.connect((HOST, PORT))
        client.sendall(request.encode("utf-8"))
        data = client.recv(4096).decode("utf-8", "ignore")

    salida.delete("1.0", tk.END)
    salida.insert(tk.END, data)


# --- Interfaz gráfica sencilla ---
root = tk.Tk()
root.title("Cliente TCP/IP + HTTP")

tk.Label(root, text="Escribe un mensaje:").pack(padx=10, pady=(10, 0))

entrada = tk.Entry(root, width=50)
entrada.pack(padx=10, pady=5)

tk.Button(root, text="Enviar al servidor",
          command=enviar).pack(padx=10, pady=5)

salida = scrolledtext.ScrolledText(root, width=60, height=15)
salida.pack(padx=10, pady=10)

root.mainloop()
