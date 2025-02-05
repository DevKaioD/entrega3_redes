import socket
import threading
import json
import time
from labirinto import gerar_mapa

# Configurações do servidor
HOST = '127.0.0.1'
PORT = 12345

# Lista de jogadores e histórico de partidas
jogadores = {}
historico_single = []
historico_multi = []

def salvar_historico_single(nome_jogador, tempo):
    historico_single.append({"jogador": nome_jogador, "tempo": tempo})
    with open("historico_single.json", "w") as arquivo:
        json.dump(historico_single, arquivo)

def salvar_historico_multi(nomes_jogadores, tempos):
    # Salva ranqueados por tempo
    dados = sorted(zip(nomes_jogadores, tempos), key=lambda x: x[1])
    historico_multi.append(dados)
    with open("historico_multi.json", "w") as arquivo:
        json.dump(historico_multi, arquivo)

def gerenciar_cliente(conn, endereco):
    print(f"Jogador conectado: {endereco}")
    nome = conn.recv(1024).decode('utf-8')
    jogadores[conn] = {"nome": nome, "posicao": [1, 1]}

    try:
        while True:
            mensagem = conn.recv(1024).decode('utf-8')
            if not mensagem:
                break
            dados = json.loads(mensagem)
            acao = dados.get("acao")

            if acao == "solicitar_mapa":
                dificuldade = dados.get("dificuldade")
                ALTURA, LARGURA = 21, 21
                if dificuldade == "medio":
                    ALTURA, LARGURA = 31, 31
                elif dificuldade == "dificil":
                    ALTURA, LARGURA = 41, 41
                mapa = gerar_mapa(ALTURA, LARGURA)
                conn.sendall(json.dumps({"mapa": mapa}).encode('utf-8'))

            elif acao == "movimento":
                jogadores[conn]["posicao"] = dados.get("nova_posicao")
                # Envia atualizações para todos os clientes no multiplayer
                for jogador_conn in jogadores:
                    jogador_conn.sendall(json.dumps({"jogadores": jogadores}).encode('utf-8'))

            elif acao == "finalizar":
                tempo = dados.get("tempo")
                if dados.get("modo") == "single":
                    salvar_historico_single(nome, tempo)
                else:
                    salvar_historico_multi([jogadores[j]["nome"] for j in jogadores], [dados.get("tempo")])
                break

    except Exception as e:
        print(f"Erro com o jogador {endereco}: {e}")
    finally:
        print(f"Jogador desconectado: {endereco}")
        del jogadores[conn]
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