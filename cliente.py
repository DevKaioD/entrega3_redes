import socket
import pygame
import time
import json

# Configurações iniciais
LARGURA_TELA, ALTURA_TELA = 800, 600
TAMANHO_CELULA = 40
FPS = 30
CORES = {
    "parede": (0, 0, 0),
    "caminho": (255, 255, 255),
    "inicio": (0, 255, 0),
    "fim": (255, 0, 0),
    "jogador": (0, 0, 255),
    "jogador2": (255, 165, 0),
}
ARQUIVO_HISTORICO = "historico_tempos.json"

# Inicializa o Pygame
pygame.init()
tela = pygame.display.set_mode((LARGURA_TELA, ALTURA_TELA))
pygame.display.set_caption("Jogo do Labirinto")
fonte = pygame.font.Font(None, 36)
clock = pygame.time.Clock()

def carregar_historico():
    try:
        with open(ARQUIVO_HISTORICO, "r") as arquivo:
            return json.load(arquivo)
    except FileNotFoundError:
        return []

def salvar_historico(novo_tempo):
    historico = carregar_historico()
    historico.append(novo_tempo)
    historico.sort()  # Ordena do menor para o maior tempo
    historico = historico[:5]  # Mantém apenas os 5 melhores tempos
    with open(ARQUIVO_HISTORICO, "w") as arquivo:
        json.dump(historico, arquivo)

def desenhar_historico():
    historico = carregar_historico()
    y = 200
    tela.blit(fonte.render("Melhores Tempos:", True, (0, 0, 0)), (50, y))
    for tempo in historico:
        y += 30
        tela.blit(fonte.render(f"{tempo:.2f}s", True, (0, 0, 0)), (50, y))

def conectar_ao_servidor():
    try:
        cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        cliente.connect(("localhost", 12345))
        return cliente
    except ConnectionRefusedError:
        print("Erro: Não foi possível conectar ao servidor.")
        pygame.quit()
        exit()

def desenhar_mapa(mapa, jogador_pos, jogador2_pos=None):
    for y, linha in enumerate(mapa):
        for x, celula in enumerate(linha):
            cor = CORES["caminho"] if celula == " " else CORES["parede"]
            if celula == "I":
                cor = CORES["inicio"]
            elif celula == "F":
                cor = CORES["fim"]
            pygame.draw.rect(tela, cor, (x * TAMANHO_CELULA, y * TAMANHO_CELULA, TAMANHO_CELULA, TAMANHO_CELULA))

    # Desenha os jogadores
    pygame.draw.rect(tela, CORES["jogador"], (jogador_pos[0] * TAMANHO_CELULA, jogador_pos[1] * TAMANHO_CELULA, TAMANHO_CELULA, TAMANHO_CELULA))
    if jogador2_pos:
        pygame.draw.rect(tela, CORES["jogador2"], (jogador2_pos[0] * TAMANHO_CELULA, jogador2_pos[1] * TAMANHO_CELULA, TAMANHO_CELULA, TAMANHO_CELULA))

def main():
    cliente = conectar_ao_servidor()
    rodando = True

    # Tela de seleção
    modo = None
    while modo not in ["1", "2"]:
        tela.fill((255, 255, 255))

        # Desenha o título e as instruções
        titulo = fonte.render("Selecione o modo de jogo:", True, (0, 0, 0))
        opcao1 = fonte.render("1 - Singleplayer", True, (0, 0, 0))
        opcao2 = fonte.render("2 - Multiplayer", True, (0, 0, 0))

        tela.blit(titulo, (50, 50))
        tela.blit(opcao1, (50, 100))
        tela.blit(opcao2, (50, 150))

        # Desenha o histórico de tempos
        desenhar_historico()

        pygame.display.flip()

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                exit()
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_1:
                    modo = "1"
                elif evento.key == pygame.K_2:
                    modo = "2"

    cliente.sendall(modo.encode())

    try:
        dados_mapa = cliente.recv(8192).decode()
        mapa = json.loads(dados_mapa)
    except json.JSONDecodeError:
        print("Erro: Não foi possível carregar o mapa do servidor.")
        pygame.quit()
        exit()

    jogador_pos = [1, 1]
    jogador2_pos = None

    if modo == "2":
        jogador2_pos = [1, 1]

    inicio_tempo = time.time()

    while rodando:
        tela.fill((255, 255, 255))

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                rodando = False

        # Movimentação do jogador
        teclas = pygame.key.get_pressed()
        nova_pos = jogador_pos[:]
        if teclas[pygame.K_w]:
            nova_pos[1] -= 1
        if teclas[pygame.K_s]:
            nova_pos[1] += 1
        if teclas[pygame.K_a]:
            nova_pos[0] -= 1
        if teclas[pygame.K_d]:
            nova_pos[0] += 1

        if mapa[nova_pos[1]][nova_pos[0]] != "#":
            jogador_pos = nova_pos

        # Envia posição para o servidor no modo multiplayer
        if modo == "2":
            try:
                cliente.sendall(json.dumps(jogador_pos).encode())
                resposta_servidor = cliente.recv(1024).decode()
                jogador2_pos = json.loads(resposta_servidor)
            except (ConnectionResetError, json.JSONDecodeError):
                print("Erro na comunicação com o servidor.")
                rodando = False

        # Verifica condição de vitória para jogador 1
        if mapa[jogador_pos[1]][jogador_pos[0]] == "F":
            tempo_total = time.time() - inicio_tempo
            salvar_historico(tempo_total)
            tela.fill((255, 255, 255))
            mensagem = fonte.render(f"Você venceu! Tempo: {tempo_total:.2f}s", True, (0, 255, 0))
            tela.blit(mensagem, (50, 50))
            pygame.display.flip()
            pygame.time.delay(3000)
            rodando = False

        # Verifica condição de vitória para jogador 2
        if modo == "2" and jogador2_pos and mapa[jogador2_pos[1]][jogador2_pos[0]] == "F":
            tela.fill((255, 255, 255))
            mensagem = fonte.render("O jogador 2 venceu!", True, (255, 165, 0))
            tela.blit(mensagem, (50, 50))
            pygame.display.flip()
            pygame.time.delay(3000)
            rodando = False

        # Desenha o mapa e jogadores
        desenhar_mapa(mapa, jogador_pos, jogador2_pos)

        # Exibe o tempo decorrido
        tempo_decorrido = time.time() - inicio_tempo
        texto_tempo = fonte.render(f"Tempo: {tempo_decorrido:.2f}s", True, (0, 0, 0))
        tela.blit(texto_tempo, (600, 10))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()
