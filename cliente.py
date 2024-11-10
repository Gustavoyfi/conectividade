import threading
import socket
import argparse
import sys
import tkinter as tk

class Send(threading.Thread):
    def __init__(self, sock, name, running_flag):
        super().__init__()
        self.sock = sock
        self.name = name
        self.running_flag = running_flag  
        
    def run(self):
        while self.running_flag.is_set():
            message = sys.stdin.readline()[:-1]
            if message == "QUIT":
                self.sock.sendall(f"Server: {self.name} saiu do chat".encode("ascii"))
                print("\nSaindo...")
                self.sock.close()
                self.running_flag.clear()
            else:
                self.sock.sendall(message.encode("ascii"))

class Receive(threading.Thread):
    def __init__(self, sock, name, messages, running_flag):
        super().__init__()
        self.sock = sock
        self.name = name
        self.messages = messages
        self.running_flag = running_flag
        
    def run(self):
        while self.running_flag.is_set():
            try:
                message = self.sock.recv(1024).decode("ascii")
                if message:
                    self.messages.insert(tk.END, message)
                    print(f"\r{message}\n{self.name}: ", end=" ")
                else:
                    print("\nPerda de conexão com o servidor!")
                    self.running_flag.clear()
                    self.sock.close()
            except OSError:
                break

class Client:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.name = None
        self.messages = None
        self.running_flag = threading.Event()
        self.running_flag.set()

    def start(self):
        print(f"Tentando conectar-se a {self.host}:{self.port}...")
        self.sock.connect((self.host, self.port))
        print(f"Conexão bem-sucedida com {self.host}:{self.port}")

        
        while True:
            self.name = input("Escolha seu nome: ").strip()
            self.sock.sendall(self.name.encode("ascii"))
            response = self.sock.recv(1024).decode("ascii")
            if response == "Nome de usuário já em uso. Por favor, escolha outro.":
                print(response)
            else:
                print(f"Bem-vindo(a), {self.name}! Preparado(a) para enviar e receber mensagens...")
                break

        send = Send(self.sock, self.name, self.running_flag)
        receive = Receive(self.sock, self.name, self.messages, self.running_flag)
        send.start()
        receive.start()

        print("Pronto! Saia do chat a qualquer momento digitando 'QUIT'\n")
        print(f"{self.name}: ", end="")

        return receive

    def send(self, textInput):
        message = textInput.get()
        textInput.delete(0, tk.END)
        self.messages.insert(tk.END, f"{self.name}: {message}")

        self.sock.sendall(message.encode("ascii"))

def main():
    parser = argparse.ArgumentParser(description="Chat Client")
    parser.add_argument("host", type=str, help="IP ou nome do servidor")
    parser.add_argument("port", type=int, help="Porta do servidor")
    args = parser.parse_args()

    client = Client(args.host, args.port)
    receive = client.start()
    
    window = tk.Tk()
    window.title("Chatroom Monstrão")
    
    fromMessage = tk.Frame(master=window)
    scrollBar = tk.Scrollbar(master=fromMessage)
    messages = tk.Listbox(master=fromMessage, yscrollcommand=scrollBar.set)
    scrollBar.pack(side=tk.RIGHT, fill=tk.Y, expand=False)
    messages.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    
    client.messages = messages
    receive.messages = messages
    
    fromMessage.grid(row=0, column=0, columnspan=2, sticky="nsew")
    fromEntry = tk.Frame(master=window)
    textInput = tk.Entry(master=fromEntry)
    
    textInput.pack(fill=tk.BOTH, expand=True)
    textInput.bind("<Return>", lambda x: client.send(textInput))
    textInput.insert(0, "Escreva sua mensagem aqui.")
    
    btnSend = tk.Button(
        master=window,
        text="Enviar",
        command=lambda: client.send(textInput)
    )
    
    fromEntry.grid(row=1, column=0, padx=10, sticky="ew")
    btnSend.grid(row=1, column=1, padx=10, sticky="ew")
    
    window.rowconfigure(0, minsize=500, weight=1)
    window.rowconfigure(1, minsize=50, weight=0)
    window.columnconfigure(0, minsize=500, weight=1)
    window.columnconfigure(1, minsize=200, weight=0)

    def on_closing():
        client.running_flag.clear()
        client.sock.close()
        window.destroy()

    window.protocol("WM_DELETE_WINDOW", on_closing)
    window.mainloop()

if __name__ == "__main__":
    main()
