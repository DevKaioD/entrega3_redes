import socket
import threading
import time
import csv
import os
import json
from labirinto import gerar_mapa

# Configurações do servidor
HOST = '127.0.0.1'
PORT = 12345

# Lista de jogadores e histórico de partidas
jogadores = []
historico = []

# Carrega o histórico existente ou cria um novo arquivo
if os.path.exists("historico.csv"):
    with open("historico.csv", "r") as arquivo:
        leitor = csv.reader(arquivo)
        historico = list(leitor)
else:
    historico = [["Jogador", "Resultado", "Tempo", "Modo"]]

def salvar_historico(nome_jogador, resultado, tempo, modo):
    historico.append([nome_jogador, resultado, tempo, modo])
    with open("historico.csv", "w", newline="") as arquivo:
        escritor = csv.writer(arquivo)
        escritor.writerows(historico)

def gerenciar_cliente(conn, endereco):
    print(f"Jogador conectado: {endereco}")
    jogadores.append(conn)

    try:
        # Aguarda dois jogadores para iniciar o multiplayer
        if len(jogadores) < 2:
            conn.sendall("Aguardando outro jogador...".encode('utf-8'))
            while len(jogadores) < 2:
                time.sleep(1)
        
        # Gera o mapa para o multiplayer (Dificuldade 2)
        mapa = gerar_mapa(21, 21, "dificuldade2")
        conn.sendall(json.dumps(mapa).encode('utf-8'))  # Envia o mapa ao cliente
        start_time = time.time()
        while True:
            mensagem = conn.recv(1024).decode('utf-8')
            if not mensagem:
                break
            print(f"Mensagem do jogador {endereco}: {mensagem}")
            
            if mensagem.startswith("FIM"):
                end_time = time.time()
                tempo_total = end_time - start_time
                nome_jogador = mensagem.split(":")[1] if ":" in mensagem else f"Jogador {endereco}"
                salvar_historico(nome_jogador, "Vitória", tempo_total, "multi")
                break
    except Exception as e:
        print(f"Erro com o jogador {endereco}: {e}")
    finally:
        print(f"Jogador desconectado: {endereco}")
        jogadores.remove(conn)
        conn.close()

def iniciar_servidor():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as servidor:
        servidor.bind((HOST, PORT))
        servidor.listen()
        print("Servidor aguardando conexões...")

        while True:
            conn, endereco = servidor.accept()
            thread = threading.Thread(target=gerenciar_cliente, args=(conn, endereco))
            thread.start()

if __name__ == "__main__":
    iniciar_servidor()