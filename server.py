import socket
import threading
import time  # ADICIONADO

LABIRINTO = [
    [1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 1, 1, 0, 1],
    [1, 0, 1, 'E', 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 1, 1]
]

POSICAO_INICIAL = (1, 1)

jogadores = {}
lock = threading.Lock()
jogo_encerrado = False  

def handle_client(client_socket, addr, jogador):
    global jogadores, jogo_encerrado

    print(f"Jogador {jogador} conectado: {addr}")

    x, y = POSICAO_INICIAL
    client_socket.send(f"{x},{y}".encode())

    while True:
        try:
            comando = client_socket.recv(1024).decode().strip()
            if not comando:
                break

            if jogo_encerrado:
                client_socket.send("END".encode())
                break

            novo_x, novo_y = x, y
            if comando == "W": novo_x -= 1
            elif comando == "S": novo_x += 1
            elif comando == "A": novo_y -= 1
            elif comando == "D": novo_y += 1

            if LABIRINTO[novo_x][novo_y] != 1:
                x, y = novo_x, novo_y

            client_socket.send(f"{x},{y}".encode())

            if LABIRINTO[x][y] == 'E':
                print(f"Jogador {jogador} venceu!")

                with lock:
                    jogo_encerrado = True  
                    try:
                        client_socket.send("WIN".encode())  # Envia "WIN" para o vencedor
                        time.sleep(1)  # <- ESPERA 1 SEGUNDO ANTES DE FECHAR!
                    except:
                        pass

                    for j_id, j_socket in jogadores.items():
                        if j_id != jogador:  
                            try:
                                j_socket.send("END".encode())  
                            except:
                                pass
                
                break  

        except:
            break

    client_socket.close()
    with lock:
        if jogador in jogadores:
            del jogadores[jogador]
    print(f"Jogador {jogador} desconectado.")

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("0.0.0.0", 5555))
    server.listen(2)

    print("Servidor esperando conexões...")
    jogador_id = 1

    while True:
        client_socket, addr = server.accept()

        if jogo_encerrado:
            client_socket.send("END".encode())
            client_socket.close()
            continue

        jogadores[jogador_id] = client_socket
        thread = threading.Thread(target=handle_client, args=(client_socket, addr, jogador_id))
        thread.start()
        jogador_id += 1

start_server()
