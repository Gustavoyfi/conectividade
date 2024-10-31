import socket as sock

HOST = "127.0.0.1" #IP DO SERVIDOR
PORTA = 9999 #PORTA DO SERVIDOR

# CRIAR SOCKET IPV4/TCP
s = sock.socket(sock.AF_INET, sock.SOCK_STREAM)

#CLIENTE 
s.conncet((HOST, PORTA))

#CLIENTE ENVIA UMA MENSAGEM
# s.sendall(str.encode("BES - PUCPR - O MELHOR CURSO DO BRASIL"))
#Abram um input e envie a mensagem para o servidor

#Cliente le uma mensagem
dados = s.recv(1024)
print(f"Servidor >> {dados.decode()}")

nome = input("Informe seu nome: ")

while True:
    mensagem = input(" ")
    s.sendall(str.encode(f"{nome} >> {mensagem}"))

