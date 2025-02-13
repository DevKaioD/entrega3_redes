import socket
import threading
import time
import csv
import json
import os
from labirinto import gerar_mapa

# Configurações do servidor
HOST = '0.0.0.0'  # Escuta em todas as interfaces de rede
PORT = 12345  # Porta para conexões TCP
BROADCAST_PORT = 5001  # Porta para descoberta UDP

# Estrutura para armazenar partidas e jogadores
partidas = {}  # Dicionário de partidas: {id_partida: {"jogadores": [conn1, conn2], "mapa": mapa}}
proximo_id_partida = 1  # Contador para IDs de partidas

# Carrega o histórico existente ou cria um novo arquivo
if os.path.exists("historico.csv"):
    with open("historico.csv", "r") as arquivo:
        leitor = csv.reader(arquivo)
        historico = list(leitor)
else:
    historico = [["Jogador", "Resultado", "Tempo", "Modo"]]

def salvar_historico(nome_jogador, resultado, tempo, modo):
    """Salva o resultado de uma partida no histórico."""
    historico.append([nome_jogador, resultado, tempo, modo])
    with open("historico.csv", "w", newline="") as arquivo:
        escritor = csv.writer(arquivo)
        escritor.writerows(historico)

def gerar_mapa_partida():
    """Gera um mapa para uma nova partida."""
    return gerar_mapa(21, 21, "dificuldade2")

def gerenciar_partida(id_partida):
    """Gerencia uma partida específica."""
    partida = partidas[id_partida]
    jogadores = partida["jogadores"]
    mapa = partida["mapa"]

    # Define posições iniciais dos jogadores
    posicoes = [[1, 1], [19, 19]]  # Jogador 1 no canto superior esquerdo, Jogador 2 no canto inferior direito

    try:
        # Envia o mapa para ambos os jogadores
        for conn in jogadores:
            conn.sendall(json.dumps(mapa).encode('utf-8'))

        start_time = time.time()  # Tempo de início da partida

        # Lógica da partida
        while True:
            for i, conn in enumerate(jogadores):
                # Recebe a posição atualizada do jogador
                try:
                    data = conn.recv(1024).decode('utf-8')
                    if data:
                        posicoes[i] = json.loads(data)  # Atualiza a posição do jogador
                except:
                    pass

                # Envia as posições de ambos os jogadores para cada cliente
                conn.sendall(json.dumps(posicoes).encode('utf-8'))

                # Verifica se o jogador venceu
                if mapa[posicoes[i][1]][posicoes[i][0]] == "F":
                    end_time = time.time()
                    tempo_total = end_time - start_time
                    nome_jogador = f"Jogador {i + 1}"  # Substitua pelo nome real do jogador
                    salvar_historico(nome_jogador, "Vitória", tempo_total, "multi")
                    print(f"Partida {id_partida}: Jogador {nome_jogador} venceu!")

                    # Envia mensagem de vitória para ambos os jogadores
                    for c in jogadores:
                        c.sendall("FIM".encode('utf-8'))
                    break

            # Encerra a partida se um jogador desconectar
            if not all(conn.fileno() != -1 for conn in jogadores):
                break

    except Exception as e:
        print(f"Erro na partida {id_partida}: {e}")
    finally:
        # Fecha as conexões e remove a partida
        for conn in jogadores:
            conn.close()
        del partidas[id_partida]
        print(f"Partida {id_partida} encerrada.")

def descobrir_servidor():
    """Servidor de descoberta UDP."""
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_socket:
        udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        udp_socket.bind(('', BROADCAST_PORT))

        print(f"Servidor de descoberta aguardando solicitações na porta {BROADCAST_PORT}...")

        while True:
            data, addr = udp_socket.recvfrom(1024)
            if data.decode() == "DISCOVERY_REQUEST":
                print(f"Recebida solicitação de descoberta de {addr}")
                udp_socket.sendto("DISCOVERY_RESPONSE".encode(), addr)

def iniciar_servidor():
    """Inicia o servidor TCP para conexões dos clientes."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as servidor:
        # Vincula o socket ao endereço e porta
        servidor.bind((HOST, PORT))
        # Começa a escutar conexões
        servidor.listen()
        print(f"Servidor aguardando conexões em {HOST}:{PORT}...")

        while True:
            # Aceita uma nova conexão
            conn, endereco = servidor.accept()
            print(f"Nova conexão de {endereco}")

            # Adiciona o jogador a uma partida
            global proximo_id_partida
            if proximo_id_partida not in partidas:
                # Cria uma nova partida
                partidas[proximo_id_partida] = {"jogadores": [], "mapa": gerar_mapa_partida()}
                partidas[proximo_id_partida]["jogadores"].append(conn)
                print(f"Partida {proximo_id_partida} criada. Aguardando segundo jogador...")
            else:
                # Adiciona o segundo jogador à partida existente
                partidas[proximo_id_partida]["jogadores"].append(conn)
                print(f"Partida {proximo_id_partida} iniciada com dois jogadores.")
                # Inicia uma thread para gerenciar a partida
                threading.Thread(target=gerenciar_partida, args=(proximo_id_partida,)).start()
                proximo_id_partida += 1  # Prepara o ID para a próxima partida

if __name__ == "__main__":
    # Inicia o servidor de descoberta em uma thread separada
    discovery_thread = threading.Thread(target=descobrir_servidor)
    discovery_thread.daemon = True
    discovery_thread.start()

    # Inicia o servidor principal
    iniciar_servidor()