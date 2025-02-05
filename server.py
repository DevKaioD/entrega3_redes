import socket
import threading
import json
from labirinto import gerar_mapa

# Configurações do servidor
HOST = '127.0.0.1'
PORT = 12345

# Lista de jogadores e histórico de partidas
jogadores = []
historico = []

# Geração do labirinto
ALTURA, LARGURA = 21, 21  # Dimensões do labirinto
mapa = gerar_mapa(ALTURA, LARGURA)

def salvar_historico(nome_jogador, resultado, tempo):
    historico.append({
        "jogador": nome_jogador,
        "resultado": resultado,
        "tempo": tempo
    })
    with open("historico.json", "w") as arquivo:
        json.dump(historico, arquivo)

def gerenciar_cliente(conn, endereco):
    print(f"Jogador conectado: {endereco}")
    jogadores.append(conn)

    try:
        conn.sendall(json.dumps(mapa).encode('utf-8'))  # Envia o mapa ao cliente
        while True:
            mensagem = conn.recv(1024).decode('utf-8')
            if not mensagem:
                break
            print(f"Mensagem do jogador {endereco}: {mensagem}")
            
            if mensagem == "FIM":
                salvar_historico(f"Jogador {endereco}", "Vitória", "2:30")
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
