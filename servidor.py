import socket as sock

HOST = "localhost" #127.0.0.1
PORTA = 9999

#IPV4 (primeiro parametro): AF_INET
#TCP (segundo parametro): SOCK_STREAM
#CRIAR O SOCKET DO SERVIDOR

s = sock.socket(sock.AF_INET, sock.SOCK_STREAM)

#FAZEMOS O "PLUG" DO IP DO SERVIDOR COM A PORTA (BIND)
s.bind((HOST, PORTA))

#COLOCAMOS O SERVIDOR NO MODO DE ESCUTA (LISTEN) - AGUARDANDO CONEXÕES
s.listen()
print(f"O servidor {HOST}:{PORTA} está aguardando conexões...")

#SERVIDOR PRECISA ACEITAR CONEXÃO

while True:

    conn, ender = s.accept()
    print(f"Conexão estabelecida com {ender}")

    while True:
        
        #Recebimento de mensagem
        dados = conn.recv(1024)
        # print(f"Cliente - {ender} >> {dados.decode()}")
        print(dados.decode())
        
        #Envio de mensagem (bytes)
        # conn.sendall(dados)

