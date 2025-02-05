import pygame
import socket
import sys
from labirinto import gerar_mapa

# Cores
BRANCO = (255, 255, 255)
PRETO = (0, 0, 0)
VERDE = (0, 255, 0)
VERMELHO = (255, 0, 0)

# Configurações do jogo
LARGURA, ALTURA = 600, 600
TAMANHO_BLOCO = 30

# Conexão com o servidor
HOST = '127.0.0.1'
PORT = 12345
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Tentativa de conexão com o servidor
try:
    client.connect((HOST, PORT))
except Exception as e:
    print(f"Erro ao conectar ao servidor: {e}")
    sys.exit()

pygame.init()
tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Jogo Multiplayer")

# Tela inicial para escolher o modo de jogo
def tela_selecao():
    fonte = pygame.font.Font(None, 50)
    single_text = fonte.render("1. Singleplayer", True, BRANCO)
    multi_text = fonte.render("2. Multiplayer", True, BRANCO)
    
    while True:
        tela.fill(PRETO)
        tela.blit(single_text, (LARGURA // 2 - single_text.get_width() // 2, ALTURA // 2 - 60))
        tela.blit(multi_text, (LARGURA // 2 - multi_text.get_width() // 2, ALTURA // 2 + 10))
        pygame.display.flip()

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_1:
                    return "single"
                elif evento.key == pygame.K_2:
                    return "multi"

# Modo selecionado
modo_jogo = tela_selecao()

# Geração do mapa
if modo_jogo == "single":
    mapa = gerar_mapa(21, 21)
elif modo_jogo == "multi":
    client.sendall("start_multi".encode())
    data = client.recv(4096).decode()
    mapa = eval(data)

def desenhar_mapa(mapa, jogador_pos):
    tela.fill(PRETO)
    for y, linha in enumerate(mapa):
        for x, bloco in enumerate(linha):
            cor = BRANCO if bloco == " " else VERMELHO if bloco == "#" else VERDE if bloco == "F" else PRETO
            pygame.draw.rect(tela, cor, (x * TAMANHO_BLOCO, y * TAMANHO_BLOCO, TAMANHO_BLOCO, TAMANHO_BLOCO))

    # Desenha o jogador
    pygame.draw.rect(tela, VERDE, (jogador_pos[0] * TAMANHO_BLOCO, jogador_pos[1] * TAMANHO_BLOCO, TAMANHO_BLOCO, TAMANHO_BLOCO))
    pygame.display.flip()

# Posição inicial do jogador
jogador_pos = [1, 1]

# Movimento usando WASD
teclas_movimento = {
    pygame.K_w: (0, -1),
    pygame.K_s: (0, 1),
    pygame.K_a: (-1, 0),
    pygame.K_d: (1, 0),
}

# Loop principal do jogo
rodando = True
while rodando:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            rodando = False

        if evento.type == pygame.KEYDOWN:
            if evento.key in teclas_movimento:
                dx, dy = teclas_movimento[evento.key]
                novo_x, novo_y = jogador_pos[0] + dx, jogador_pos[1] + dy

                # Verifica se é possível se mover para a nova posição
                if mapa[novo_y][novo_x] != "#":
                    jogador_pos = [novo_x, novo_y]

                # Verifica vitória
                if mapa[novo_y][novo_x] == "F":
                    fonte = pygame.font.Font(None, 60)
                    vitoria_text = fonte.render("🎉 Você venceu! 🎉", True, BRANCO)
                    tela.blit(vitoria_text, (LARGURA // 2 - vitoria_text.get_width() // 2, ALTURA // 2))
                    pygame.display.flip()
                    pygame.time.wait(3000)
                    rodando = False

    desenhar_mapa(mapa, jogador_pos)

pygame.quit()
