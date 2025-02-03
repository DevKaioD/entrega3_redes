# cliente.py
import socket
import os

def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(("127.0.0.1", 5555))

    # Recebe posição inicial
    posicao = client.recv(1024).decode().split(',')
    x, y = int(posicao[0]), int(posicao[1])

    while True:
        os.system("cls" if os.name == "nt" else "clear")
        print(f"Posição atual: ({x}, {y})")
        comando = input("Mover (W/S/A/D): ").strip().upper()
        
        if comando in ["W", "S", "A", "D"]:
            client.send(comando.encode())
            resposta = client.recv(1024).decode()

            if resposta == "WIN":
                print("Parabéns, você venceu!")
                break
            else:
                posicao = resposta.split(',')
                x, y = int(posicao[0]), int(posicao[1])
        else:
            print("Comando inválido!")

    client.close()

main()
