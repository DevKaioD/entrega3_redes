import pygame
import socket
import sys
import json
import time
from labirinto import gerar_mapa

# Cores
BRANCO = (255, 255, 255)
PRETO = (0, 0, 0)
VERDE = (0, 255, 0)
VERMELHO = (255, 0, 0)
AZUL = (0, 0, 255)

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
    historico_text = fonte.render("3. Histórico", True, BRANCO)
    
    while True:
        tela.fill(PRETO)
        tela.blit(single_text, (LARGURA // 2 - single_text.get_width() // 2, ALTURA // 2 - 90))
        tela.blit(multi_text, (LARGURA // 2 - multi_text.get_width() // 2, ALTURA // 2 - 30))
        tela.blit(historico_text, (LARGURA // 2 - historico_text.get_width() // 2, ALTURA // 2 + 30))
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
                elif evento.key == pygame.K_3:
                    return "historico"

# Tela para escolher a dificuldade
def tela_dificuldade():
    fonte = pygame.font.Font(None, 50)
    facil_text = fonte.render("1. Fácil", True, BRANCO)
    medio_text = fonte.render("2. Médio", True, BRANCO)
    dificil_text = fonte.render("3. Difícil", True, BRANCO)
    
    while True:
        tela.fill(PRETO)
        tela.blit(facil_text, (LARGURA // 2 - facil_text.get_width() // 2, ALTURA // 2 - 60))
        tela.blit(medio_text, (LARGURA // 2 - medio_text.get_width() // 2, ALTURA // 2))
        tela.blit(dificil_text, (LARGURA // 2 - dificil_text.get_width() // 2, ALTURA // 2 + 60))
        pygame.display.flip()

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_1:
                    return "facil"
                elif evento.key == pygame.K_2:
                    return "medio"
                elif evento.key == pygame.K_3:
                    return "dificil"

# Modo selecionado
modo_jogo = tela_selecao()

# Geração do mapa
if modo_jogo == "single":
    dificuldade = tela_dificuldade()
    try:
        mapa = gerar_mapa(21, 21, dificuldade)
    except Exception as e:
        print(e)
        sys.exit()
elif modo_jogo == "multi":
    client.sendall("start_multi".encode())
    data = client.recv(4096).decode()
    mapa = json.loads(data)
elif modo_jogo == "historico":
    try:
        with open("historico.json", "r") as arquivo:
            historico = json.load(arquivo)
            for partida in historico:
                print(f"Jogador: {partida['jogador']}, Resultado: {partida['resultado']}, Tempo: {partida['tempo']}, Modo: {partida['modo']}")
    except FileNotFoundError:
        print("Nenhum histórico de partidas encontrado.")
    sys.exit()

def desenhar_mapa(mapa, jogador_pos, outro_jogador_pos=None):
    tela.fill(PRETO)
    for y, linha in enumerate(mapa):
        for x, bloco in enumerate(linha):
            cor = BRANCO if bloco == " " else VERMELHO if bloco == "#" else VERDE if bloco == "F" else PRETO
            pygame.draw.rect(tela, cor, (x * TAMANHO_BLOCO, y * TAMANHO_BLOCO, TAMANHO_BLOCO, TAMANHO_BLOCO))

    # Desenha o jogador
    pygame.draw.rect(tela, VERDE, (jogador_pos[0] * TAMANHO_BLOCO, jogador_pos[1] * TAMANHO_BLOCO, TAMANHO_BLOCO, TAMANHO_BLOCO))
    if outro_jogador_pos:
        pygame.draw.rect(tela, AZUL, (outro_jogador_pos[0] * TAMANHO_BLOCO, outro_jogador_pos[1] * TAMANHO_BLOCO, TAMANHO_BLOCO, TAMANHO_BLOCO))
    pygame.display.flip()

# Posição inicial do jogador
jogador_pos = [1, 1]
outro_jogador_pos = None

# Movimento usando WASD
teclas_movimento = {
    pygame.K_w: (0, -1),
    pygame.K_s: (0, 1),
    pygame.K_a: (-1, 0),
    pygame.K_d: (1, 0),
}

# Loop principal do jogo
rodando = True
start_time = time.time()
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
                    end_time = time.time()
                    tempo_total = end_time - start_time
                    print(f"Você venceu! Tempo: {tempo_total:.2f} segundos")
                    fonte = pygame.font.Font(None, 60)
                    vitoria_text = fonte.render("🎉 Você venceu! 🎉", True, BRANCO)
                    tela.blit(vitoria_text, (LARGURA // 2 - vitoria_text.get_width() // 2, ALTURA // 2))
                    pygame.display.flip()
                    pygame.time.wait(3000)
                    rodando = False

    desenhar_mapa(mapa, jogador_pos, outro_jogador_pos)

pygame.quit()