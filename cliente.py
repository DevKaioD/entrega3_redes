import pygame
import socket

# Configurações do jogo
LARGURA, ALTURA = 600, 500
TAMANHO_BLOCO = 80
COR_FUNDO = (0, 0, 0)
COR_PAREDE = (255, 255, 255)
COR_JOGADOR = (0, 255, 0)
COR_SAIDA = (255, 0, 0)

# Inicializa o Pygame
pygame.init()
tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Labirinto Multiplayer")

# Configurações do socket
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(("127.0.0.1", 5555))

# Recebe posição inicial do servidor
posicao = client.recv(1024).decode().split(',')
x, y = int(posicao[0]), int(posicao[1])

# Estrutura do labirinto
LABIRINTO = [
    [1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 1, 1, 0, 1],
    [1, 0, 1, 'E', 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 1, 1]
]

# Mapear teclas para os comandos do servidor
TECLAS_MOVIMENTO = {
    pygame.K_w: "W",
    pygame.K_s: "S",
    pygame.K_a: "A",
    pygame.K_d: "D"
}

def desenhar_labirinto():
    tela.fill(COR_FUNDO)
    for linha in range(len(LABIRINTO)):
        for coluna in range(len(LABIRINTO[linha])):
            x_pos = coluna * TAMANHO_BLOCO
            y_pos = linha * TAMANHO_BLOCO

            if LABIRINTO[linha][coluna] == 1:
                pygame.draw.rect(tela, COR_PAREDE, (x_pos, y_pos, TAMANHO_BLOCO, TAMANHO_BLOCO))
            elif LABIRINTO[linha][coluna] == 'E':
                pygame.draw.rect(tela, COR_SAIDA, (x_pos, y_pos, TAMANHO_BLOCO, TAMANHO_BLOCO))

    pygame.draw.circle(tela, COR_JOGADOR, 
                       (y * TAMANHO_BLOCO + TAMANHO_BLOCO // 2, x * TAMANHO_BLOCO + TAMANHO_BLOCO // 2),
                       TAMANHO_BLOCO // 3)

    pygame.display.flip()

# Loop principal do jogo
rodando = True
while rodando:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            rodando = False

        elif evento.type == pygame.KEYDOWN:
            if evento.key in TECLAS_MOVIMENTO:
                client.send(TECLAS_MOVIMENTO[evento.key].encode())

                resposta = client.recv(1024).decode()

                if resposta == "WIN":
                    print("🎉 Parabéns, você venceu! 🎉")
                    rodando = False
                elif resposta == "END":
                    print("O jogo acabou! Outro jogador venceu.")
                    rodando = False
                else:
                    posicao = resposta.split(',')
                    x, y = int(posicao[0]), int(posicao[1])

    desenhar_labirinto()

pygame.quit()
client.close()
