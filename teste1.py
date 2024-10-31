import threading
import socket
import argparse
import sys

class Server(threading.Thread):
    
    def __init__(self, host, port):
        super().__init__()
        self.connections = []
        self.host = host
        self.port = port
        self.running = True  # Flag para o controle de execução
        
    def run(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))
        
        self.sock.listen(1)
        print("Ouvindo no", self.sock.getsockname())
      
        while self.running:
            try:
                sc, sockname = self.sock.accept()
                print(f"Aceitando uma nova conexão de {sc.getpeername()} para {sc.getsockname()}")
                
                server_socket = ServerSocket(sc, sockname, self)
                server_socket.start()
                self.connections.append(server_socket)
                print("Pronto para receber mensagens de", sc.getpeername())
            except OSError:
                break  # Sai do loop caso o socket seja fechado
        
    def broadcast(self, message, source):
        for connection in self.connections:
            if connection.sockname != source:
                connection.send(message)
    
    def remove_connection(self, connection):
        self.connections.remove(connection)

    def stop(self):
        self.running = False
        for connection in self.connections:
            connection.sc.close()
        self.sock.close()  # Fecha o socket principal

class ServerSocket(threading.Thread):
    
    def __init__(self, sc, sockname, server):
        super().__init__()
        self.sc = sc
        self.sockname = sockname
        self.server = server
        
    def run(self):
        while True:
            try:
                message = self.sc.recv(1024).decode("ascii")
                
                if message:
                    print(f"{self.sockname} disse {message}")
                    self.server.broadcast(message, self.sockname)
                else:
                    # Quando a mensagem é vazia, significa que o cliente desconectou
                    print(f"{self.sockname} fechou a conexão")
                    self.sc.close()
                    self.server.remove_connection(self)
                    return
            except ConnectionResetError:
                # Captura desconexões abruptas do cliente
                print(f"Conexão com {self.sockname} foi interrompida")
                self.sc.close()
                self.server.remove_connection(self)
                return
            except OSError:
                # Captura erros de soquetes fechados
                break
            
    def send(self, message):
        try:
            self.sc.sendall(message.encode("ascii"))
        except OSError:
            print(f"Erro ao enviar mensagem para {self.sockname}")

def exit(server):
    while True:
        ipt = input("")
        if ipt.lower() == "q":
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
    exit_thread.join()  # Aguarda o término da thread de saída antes de encerrar o script