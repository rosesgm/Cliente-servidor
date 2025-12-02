# servidor.py
import socket

HOST = "0.0.0.0"   # Acepta conexiones de cualquier IP
PORT = 8000        # Puerto del servidor

def run_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.bind((HOST, PORT))
        server.listen()
        print(f"Servidor HTTP/TCP escuchando en {HOST}:{PORT}")

        while True:
            conn, addr = server.accept()
            with conn:
                data = conn.recv(1024).decode("utf-8", "ignore")
                print("Petición recibida:\n", data)

                # Buscar el encabezado personalizado "User-Message"
                mensaje = "sin mensaje"
                for linea in data.split("\r\n"):
                    if linea.lower().startswith("user-message:"):
                        mensaje = linea.split(":", 1)[1].strip()
                        break

                cuerpo = f"Mensaje recibido desde {addr[0]}:\n{mensaje}"
                body_bytes = cuerpo.encode("utf-8")

                # Respuesta HTTP sencilla
                response = (
                    "HTTP/1.1 200 OK\r\n"
                    "Content-Type: text/plain; charset=utf-8\r\n"
                    f"Content-Length: {len(body_bytes)}\r\n"
                    "\r\n"
                ).encode("utf-8") + body_bytes

                conn.sendall(response)

if __name__ == "__main__":
    run_server()
