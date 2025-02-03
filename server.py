# server.py
import socket
import threading
import random

# Definição do labirinto (0 = caminho, 1 = parede, E = saída)
LABIRINTO = [
    [1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 1, 1, 0, 1],
    [1, 0, 1, 'E', 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 1, 1]
]

# Posição inicial do jogador
POSICAO_INICIAL = (1, 1)

# Armazena os jogadores conectados
jogadores = {}

def handle_client(client_socket, addr, jogador):
    """ Lida com a conexão de um jogador """
    global jogadores

    print(f"Jogador {jogador} conectado: {addr}")

    # Envia posição inicial
    x, y = POSICAO_INICIAL
    client_socket.send(f"{x},{y}".encode())

    while True:
        try:
            comando = client_socket.recv(1024).decode().strip()
            if not comando:
                break

            # Processar movimento do jogador
            novo_x, novo_y = x, y
            if comando == "W": novo_x -= 1
            elif comando == "S": novo_x += 1
            elif comando == "A": novo_y -= 1
            elif comando == "D": novo_y += 1

            # Validação da nova posição
            if LABIRINTO[novo_x][novo_y] != 1:  # Se não for parede
                x, y = novo_x, novo_y

            # Envia nova posição
            client_socket.send(f"{x},{y}".encode())

            # Verifica se chegou na saída
            if LABIRINTO[x][y] == 'E':
                client_socket.send("WIN".encode())
                print(f"Jogador {jogador} venceu!")
                break

        except:
            break

    client_socket.close()
    del jogadores[jogador]
    print(f"Jogador {jogador} desconectado.")

def start_server():
    """ Inicia o servidor """
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("0.0.0.0", 5555))
    server.listen(2)  # Máximo de 2 jogadores

    print("Servidor esperando conexões...")
    jogador_id = 1

    while True:
        client_socket, addr = server.accept()
        jogadores[jogador_id] = client_socket
        thread = threading.Thread(target=handle_client, args=(client_socket, addr, jogador_id))
        thread.start()
        jogador_id += 1

start_server()
