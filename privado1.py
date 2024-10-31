import threading
import socket
import argparse
import sys

class Server(threading.Thread):
    
    def __init__(self, host, port):
        super().__init__()
        self.connections = {}
        self.host = host
        self.port = port
        self.running = True  # Flag para o controle de execução
        
    def run(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))
        
        self.sock.listen(5)
        print("Ouvindo no", self.sock.getsockname())
      
        while self.running:
            try:
                sc, sockname = self.sock.accept()
                print(f"Aceitando uma nova conexão de {sc.getpeername()} para {sc.getsockname()}")
                
                username = sc.recv(1024).decode("ascii")
                
                # Verifica se o nome de usuário já está em uso
                if username in self.connections:
                    sc.sendall("Nome de usuário já em uso. Por favor, escolha outro.".encode("ascii"))
                    sc.close()
                    continue

                self.connections[username] = sc
                print(f"{username} entrou no chat.")
                
                # Mensagem de boas-vindas
                self.broadcast(f"Bem-vindo(a), {username} entrou no chat!", "Servidor")
                
                server_socket = ServerSocket(sc, username, self)
                server_socket.start()
            except OSError:
                break  # Sai do loop caso o socket seja fechado
        
    def broadcast(self, message, source):
        for username, connection in self.connections.items():
            if username != source:
                connection.sendall(message.encode("ascii"))
    
    def send_private(self, message, recipient):
        if recipient in self.connections:
            self.connections[recipient].sendall(message.encode("ascii"))
        else:
            print(f"Usuário {recipient} não encontrado.")
    
    def remove_connection(self, username):
        if username in self.connections:
            del self.connections[username]
            # Notifica que o usuário saiu
            self.broadcast(f"{username} saiu do chat.", "Servidor")

    def stop(self):
        self.running = False
        for connection in self.connections.values():
            connection.close()
        self.sock.close()  # Fecha o socket principal

class ServerSocket(threading.Thread):
    
    def __init__(self, sc, username, server):
        super().__init__()
        self.sc = sc
        self.username = username
        self.server = server
        
    def run(self):
        while True:
            try:
                message = self.sc.recv(1024).decode("ascii")
                if message:
                    if message.startswith("/private"):  # Se for uma mensagem privada
                        _, recipient, *msg = message.split()
                        msg = " ".join(msg)
                        private_message = f"[Privado de {self.username}]: {msg}"
                        self.server.send_private(private_message, recipient)
                    else:
                        public_message = f"{self.username}: {message}"
                        self.server.broadcast(public_message, self.username)
                else: 
                    print(f"{self.username} fechou a conexão")
                    self.sc.close()
                    self.server.remove_connection(self.username)
                    return
            except Exception as e:
                print(f"Erro: {e}")
                break
            
def exit(server):
    while True:
        ipt = input("")
        if ipt == "q":
            print("Fechando todas conexões...")
            server.stop()  # Encerra o servidor e as conexões
            print("Desligando o servidor....")
            server.join()  # Aguarda o término da thread do servidor
            break  # Sai do loop, encerrando o `exit_thread`

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Chatroom Server")
    parser.add_argument("host", help="Interface the server listens at")
    parser.add_argument("-p", metavar="PORT", type=int, default=1060, help="TCP port (default 1060)")
    
    args = parser.parse_args()
    
    server = Server(args.host, args.p)
    server.start()
    
    exit_thread = threading.Thread(target=exit, args=(server,))
    exit_thread.start()
    exit_thread.join()