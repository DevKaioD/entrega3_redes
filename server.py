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
partidas_lock = threading.Lock()  # Lock para sincronizar acesso ao dicionário de partidas

# Carrega o histórico existente ou cria um novo arquivo
if os.path.exists("historico.csv"):
    with open("historico.csv", "r") as arquivo:
        leitor = csv.reader(arquivo)
        historico = list(leitor)
else:
    historico = [["Jogador", "Resultado", "Tempo", "Modo"]]

def salvar_historico(nome_jogador, resultado, tempo, modo):
    """Salva o resultado de uma partida no histórico."""
    with partidas_lock:
        historico.append([nome_jogador, resultado, tempo, modo])
        with open("historico.csv", "w", newline="") as arquivo:
            escritor = csv.writer(arquivo)
            escritor.writerows(historico)

def gerar_mapa_partida():
    """Gera um mapa para uma nova partida."""
    return gerar_mapa(21, 21, "dificuldade2")

def conexao_ativa(conn):
    try:
        conn.sendall(b'')  # Tenta enviar um byte vazio
        return True
    except:
        return False

def gerenciar_partida(id_partida):
    with partidas_lock:
        partida = partidas.get(id_partida)
        if not partida:
            print(f"Partida {id_partida} não encontrada.")
            return
        jogadores = partida["jogadores"]
        mapa = partida["mapa"]

    posicoes = [[1, 1], [19, 1]]  # Posições iniciais dos jogadores

    try:
        # Envia o mapa e o ID do jogador para cada cliente
        for i, conn in enumerate(jogadores):
            try:
                conn.sendall(json.dumps({"mapa": mapa, "id_jogador": i}).encode('utf-8'))
            except Exception as e:
                print(f"Erro ao enviar mapa para jogador {i + 1}: {e}")
                return

        start_time = time.time()  # Tempo de início da partida

        # Lógica da partida
        while True:
            # Verifica se todos os jogadores ainda estão conectados
            if not all(conexao_ativa(conn) for conn in jogadores):
                print(f"Partida {id_partida} encerrada devido à desconexão de um jogador.")
                break

            jogadores_ativos = jogadores[:]
            for i, conn in enumerate(jogadores_ativos):
                if not conexao_ativa(conn):
                    print(f"Jogador {i + 1} desconectado.")
                    jogadores.remove(conn)
                    continue

                try:
                    conn.setblocking(False)  # Define o socket como não bloqueante
                    data = conn.recv(1024).decode('utf-8')

                    # Verifica se os dados estão vazios
                    if not data:
                        print(f"Jogador {i + 1} desconectado.")
                        jogadores.remove(conn)
                        break

                    # Tenta decodificar os dados como JSON
                    try:
                        dados_recebidos = json.loads(data)  # Decodifica os dados recebidos
                        if not isinstance(dados_recebidos, dict) or "x" not in dados_recebidos or "y" not in dados_recebidos:
                            raise ValueError("Formato de dados inválido")
                        nova_posicao = [dados_recebidos["x"], dados_recebidos["y"]]  # Extrai a posição
                    except (json.JSONDecodeError, ValueError) as e:
                        print(f"Dados inválidos recebidos do jogador {i + 1}: {data} - Erro: {e}")
                        # Envia uma mensagem de erro para o cliente
                        try:
                            conn.sendall(json.dumps({"erro": "Dados inválidos. Envie um JSON com 'x' e 'y'."}).encode('utf-8'))
                        except Exception as e:
                            print(f"Erro ao enviar mensagem de erro para jogador {i + 1}: {e}")
                        continue  # Ignora dados inválidos e continua o loop

                    # Verifica se a nova posição é válida
                    if (
                        0 <= nova_posicao[0] < len(mapa[0]) and 
                        0 <= nova_posicao[1] < len(mapa) and 
                        mapa[nova_posicao[1]][nova_posicao[0]] != "#"
                    ):
                        posicoes[i] = nova_posicao  # Atualiza a posição do jogador

                    # Verifica se o jogador venceu
                    if mapa[posicoes[i][1]][posicoes[i][0]] == "F":
                        end_time = time.time()
                        tempo_total = end_time - start_time
                        nome_jogador = f"Jogador {i + 1}"  # Substitua pelo nome real do jogador
                        salvar_historico(nome_jogador, "Vitória", tempo_total, "multi")
                        print(f"Partida {id_partida}: Jogador {nome_jogador} venceu!")

                        # Envia mensagem de fim de jogo para ambos os jogadores
                        for c in jogadores:
                            try:
                                c.sendall(json.dumps({"fim": True, "vencedor": i}).encode('utf-8'))
                            except Exception as e:
                                print(f"Erro ao enviar mensagem de fim para jogador: {e}")
                        break

                except BlockingIOError:
                    # Não há dados disponíveis no momento, continua o loop
                    pass
                except Exception as e:
                    print(f"Erro ao receber dados do jogador {i + 1}: {e}")
                    jogadores.remove(conn)
                    break

            # Encerra a partida se um jogador desconectar ou vencer
            if len(jogadores) < 2:
                print(f"Partida {id_partida} encerrada devido à desconexão de um jogador.")
                break

    except Exception as e:
        print(f"Erro na partida {id_partida}: {e}")
    finally:
        # Fecha as conexões e remove a partida
        with partidas_lock:
            for conn in jogadores:
                try:
                    conn.close()
                except Exception as e:
                    print(f"Erro ao fechar conexão: {e}")
            if id_partida in partidas:
                del partidas[id_partida]
            print(f"Partida {id_partida} encerrada.")

def descobrir_servidor():
    """Servidor de descoberta UDP."""
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_socket:
        udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        udp_socket.bind(('', BROADCAST_PORT))

        print(f"Servidor de descoberta aguardando solicitações na porta {BROADCAST_PORT}...")

        while True:
            try:
                data, addr = udp_socket.recvfrom(1024)
                if data.decode() == "DISCOVERY_REQUEST":
                    print(f"Recebida solicitação de descoberta de {addr}")
                    udp_socket.sendto("DISCOVERY_RESPONSE".encode(), addr)
            except Exception as e:
                print(f"Erro no servidor de descoberta: {e}")

def iniciar_servidor():
    """Inicia o servidor TCP para conexões dos clientes."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as servidor:
        servidor.bind((HOST, PORT))
        servidor.listen()
        print(f"Servidor aguardando conexões em {HOST}:{PORT}...")

        while True:
            try:
                conn, endereco = servidor.accept()
                print(f"Nova conexão de {endereco}")

                # Recebe o nome do jogador
                nome_jogador = conn.recv(1024).decode()
                print(f"Jogador conectado: {nome_jogador}")

                # Envia uma confirmação para o cliente
                conn.sendall("NOME_RECEBIDO".encode())

                # Adiciona o jogador a uma partida
                with partidas_lock:
                    global proximo_id_partida
                    if proximo_id_partida not in partidas:
                        partidas[proximo_id_partida] = {"jogadores": [], "mapa": gerar_mapa_partida()}
                        partidas[proximo_id_partida]["jogadores"].append(conn)
                        print(f"Partida {proximo_id_partida} criada. Aguardando segundo jogador...")
                    else:
                        partidas[proximo_id_partida]["jogadores"].append(conn)
                        print(f"Partida {proximo_id_partida} iniciada com dois jogadores.")
                        threading.Thread(target=gerenciar_partida, args=(proximo_id_partida,)).start()
                        proximo_id_partida += 1
            except Exception as e:
                print(f"Erro ao aceitar conexão: {e}")

if __name__ == "__main__":
    discovery_thread = threading.Thread(target=descobrir_servidor)
    discovery_thread.daemon = True
    discovery_thread.start()

    iniciar_servidor()
