import threading
import socket
import argparse
import os

class Server(threading.Thread):
    
    def __init__(self, host, port):
        super().__init__()
        self.connections = []
        self.host = host
        self.port = port
        
        
    def run(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((self.host, self.port))
        
        sock.listen(1)
        print("Ouvindo no", sock.getsockname())
      
        while True:
            
            #Aceitando nova conexão
            sc, sockname = sock.accept()
            print(f"Aceitando uma nova conexão de {sc.getpeername()} para {sc.getsockname()}")
            
            #Cria uma nova thread
            
            
            server_socket = ServerSocket(sc, sockname, self)
            
            #Começando uma nova thread
            server_socket.start()
            
            #Adicionando thread para ativar conexão
            self.connections.append(server_socket)
            print("Ready to recieve messages from", sc.getpeername())
        
    def broadcast(self, message, source):
        for connection in self.connections:
            
            #Envie para todos clientes conectados aceite o source cliente
            if connection.sockname != source:
                connection.send(message)
    
    def remove_conenection(self, connection):
        self.connections.remove(connection)
        
        
class ServerSocket(threading.Thread):
    
    def __init__(self, sc, sockname, server):
        super().__init__()
        self.sc = sc
        self.sockname = sockname
        self.server = server
        
    def run(self):
        
        while True:
            message = self.sc.recv(1024).decode("ascii")
            
            if message:
                print(f"{self.sockname} disse {message}")
                self.server.broadcast(message, self.sockname)
                
            else: 
                print(f"{self.sockname} tem fechado a conexão")
                self.sc.close()
                server.remove_connetion(self)
                return
            
    def send(self, message):
        
        self.sc.sendall(message.encode("ascii"))
        
def exit(server):
    
    while True:
        ipt = input("")
        if ipt == "q":
            print("Fechando todas conexões...")
            for connetion in server.connections:
                connetion.sc.close()
                
                print("Desligando o servidor....")
                os.exit(0)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Chatroom Server")
    parser.add_argument("host", help = "Interface the server listens at")
    parser.add_argument("-p", metavar= "PORT", type=int , default=1060, help = "TCP port(default 1060)")
    
    args = parser.parse_args()
    
    
    #Criar e começar a thread do servidor
    server = Server(args.host, args.p)
    server.start()
    
    exit = threading.Thread(target=exit, args = (server,))
    exit.start()