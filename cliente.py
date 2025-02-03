import socket
import os

def main():
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(("127.0.0.1", 5555))

        posicao = client.recv(1024).decode()

        if posicao == "END":
            print("O jogo já terminou!")
            client.close()
            return

        posicao = posicao.split(',')
        x, y = int(posicao[0]), int(posicao[1])

        while True:
            os.system("cls" if os.name == "nt" else "clear")
            print(f"Posição atual: ({x}, {y})")
            comando = input("Mover (W/S/A/D): ").strip().upper()
            
            if comando in ["W", "S", "A", "D"]:
                client.send(comando.encode())
                
                try:
                    resposta = client.recv(1024).decode()

                    if resposta == "WIN":
                        print("🎉 Parabéns, você venceu! 🎉")
                        break
                    elif resposta == "END":
                        print("O jogo acabou! Outro jogador venceu.")
                        break
                    else:
                        posicao = resposta.split(',')
                        x, y = int(posicao[0]), int(posicao[1])
                
                except ConnectionAbortedError:
                    print("Erro: A conexão foi encerrada pelo servidor.")
                    break
                except ConnectionResetError:
                    print("Erro: O servidor caiu ou foi fechado inesperadamente.")
                    break
                
            else:
                print("Comando inválido!")

    except ConnectionRefusedError:
        print("Não foi possível conectar ao servidor. Verifique se ele está rodando.")
    finally:
        client.close()
        print("Conexão encerrada.")

main()
