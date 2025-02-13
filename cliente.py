import pygame
import socket
import sys
import csv
import time
import json
from labirinto import gerar_mapa

# Cores
BRANCO = (255, 255, 255)
PRETO = (0, 0, 0)
VERDE = (0, 255, 0)
VERMELHO = (255, 0, 0)
AZUL = (0, 0, 255)

# Configurações do jogo
LARGURA, ALTURA = 625, 625
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

# Movimento usando WASD
teclas_movimento = {
    pygame.K_w: (0, -1),  # Cima
    pygame.K_s: (0, 1),   # Baixo
    pygame.K_a: (-1, 0),  # Esquerda
    pygame.K_d: (1, 0),   # Direita
}

# Função para desenhar o mapa na tela
def desenhar_mapa(mapa, jogador_pos, outro_jogador_pos=None):
    tela.fill(PRETO)  # Limpa a tela com a cor preta
    for y, linha in enumerate(mapa):
        for x, bloco in enumerate(linha):
            # Define a cor do bloco com base no conteúdo
            if bloco == " ":
                cor = BRANCO  # Caminho livre
            elif bloco == "#":
                cor = VERMELHO  # Parede
            elif bloco == "F":
                cor = VERDE  # Ponto final
            else:
                cor = PRETO  # Outros casos (não deve acontecer)
            pygame.draw.rect(tela, cor, (x * TAMANHO_BLOCO, y * TAMANHO_BLOCO, TAMANHO_BLOCO, TAMANHO_BLOCO))

    # Desenha o jogador
    pygame.draw.rect(tela, VERDE, (jogador_pos[0] * TAMANHO_BLOCO, jogador_pos[1] * TAMANHO_BLOCO, TAMANHO_BLOCO, TAMANHO_BLOCO))

    # Desenha o outro jogador (se existir)
    if outro_jogador_pos:
        pygame.draw.rect(tela, AZUL, (outro_jogador_pos[0] * TAMANHO_BLOCO, outro_jogador_pos[1] * TAMANHO_BLOCO, TAMANHO_BLOCO, TAMANHO_BLOCO))

    pygame.display.flip()  # Atualiza a tela

# Tela inicial para escolher o modo de jogo
def tela_selecao():
    fonte = pygame.font.Font(None, 50)
    single_text = fonte.render("1. Singleplayer", True, BRANCO)
    multi_text = fonte.render("2. Multiplayer", True, BRANCO)
    historico_text = fonte.render("3. Histórico", True, BRANCO)
    sair_text = fonte.render("4. Sair", True, BRANCO)
    
    while True:
        tela.fill(PRETO)
        tela.blit(single_text, (LARGURA // 2 - single_text.get_width() // 2, ALTURA // 2 - 120))
        tela.blit(multi_text, (LARGURA // 2 - multi_text.get_width() // 2, ALTURA // 2 - 60))
        tela.blit(historico_text, (LARGURA // 2 - historico_text.get_width() // 2, ALTURA // 2))
        tela.blit(sair_text, (LARGURA // 2 - sair_text.get_width() // 2, ALTURA // 2 + 60))
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
                elif evento.key == pygame.K_4:
                    pygame.quit()
                    sys.exit()

# Tela para escolher a dificuldade
def tela_dificuldade():
    fonte = pygame.font.Font(None, 50)
    dificuldade1_text = fonte.render("1. Dificuldade 1", True, BRANCO)
    dificuldade2_text = fonte.render("2. Dificuldade 2", True, BRANCO)
    
    while True:
        tela.fill(PRETO)
        tela.blit(dificuldade1_text, (LARGURA // 2 - dificuldade1_text.get_width() // 2, ALTURA // 2 - 60))
        tela.blit(dificuldade2_text, (LARGURA // 2 - dificuldade2_text.get_width() // 2, ALTURA // 2))
        pygame.display.flip()

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_1:
                    return "dificuldade1"
                elif evento.key == pygame.K_2:
                    return "dificuldade2"

# Tela pós-vitória
def tela_pos_vitoria():
    fonte = pygame.font.Font(None, 50)
    voltar_text = fonte.render("1. Voltar ao Menu", True, BRANCO)
    historico_text = fonte.render("2. Ver Histórico", True, BRANCO)
    sair_text = fonte.render("3. Sair", True, BRANCO)
    
    while True:
        tela.fill(PRETO)
        tela.blit(voltar_text, (LARGURA // 2 - voltar_text.get_width() // 2, ALTURA // 2 - 60))
        tela.blit(historico_text, (LARGURA // 2 - historico_text.get_width() // 2, ALTURA // 2))
        tela.blit(sair_text, (LARGURA // 2 - sair_text.get_width() // 2, ALTURA // 2 + 60))
        pygame.display.flip()

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_1:
                    return "menu"
                elif evento.key == pygame.K_2:
                    return "historico"
                elif evento.key == pygame.K_3:
                    return "sair"

# Função para salvar o histórico
def salvar_historico(nome_jogador, resultado, tempo, modo):
    with open("historico.csv", "a", newline="") as arquivo:
        escritor = csv.writer(arquivo)
        escritor.writerow([nome_jogador, resultado, tempo, modo])

# Função para exibir o histórico na tela
def exibir_historico_tela():
    fonte = pygame.font.Font(None, 30)  # Fonte para o texto do histórico
    tela.fill(PRETO)  # Limpa a tela com a cor preta

    # Variáveis para controle de rolagem
    scroll_y = 0
    linha_altura = 30
    max_linhas_visiveis = (ALTURA - 150) // linha_altura  # Espaço para botões e pesquisa

    try:
        with open("historico.csv", "r") as arquivo:
            leitor = csv.reader(arquivo)
            historico = list(leitor)
            if len(historico) > 1:  # Verifica se há dados além do cabeçalho
                # Filtros
                fonte_filtro = pygame.font.Font(None, 24)
                filtro_single_text = fonte_filtro.render("1. Singleplayer", True, BRANCO)
                filtro_multi_text = fonte_filtro.render("2. Multiplayer", True, BRANCO)
                filtro_todos_text = fonte_filtro.render("3. Todos", True, BRANCO)
                tela.blit(filtro_single_text, (50, 10))
                tela.blit(filtro_multi_text, (250, 10))
                tela.blit(filtro_todos_text, (450, 10))
                pygame.display.flip()

                # Aguarda o jogador escolher um filtro
                filtro_escolhido = None
                while filtro_escolhido is None:
                    for evento in pygame.event.get():
                        if evento.type == pygame.QUIT:
                            pygame.quit()
                            sys.exit()
                        if evento.type == pygame.KEYDOWN:
                            if evento.key == pygame.K_1:
                                filtro_escolhido = "single"
                            elif evento.key == pygame.K_2:
                                filtro_escolhido = "multi"
                            elif evento.key == pygame.K_3:
                                filtro_escolhido = "todos"
                            elif evento.key == pygame.K_ESCAPE:
                                return

                # Aplica o filtro
                if filtro_escolhido != "todos":
                    historico = [historico[0]] + [linha for linha in historico[1:] if linha[3] == filtro_escolhido]

                # Ordenação
                fonte_ordenacao = pygame.font.Font(None, 24)
                ordenar_nome_text = fonte_ordenacao.render("4. Ordenar por Nome", True, BRANCO)
                ordenar_tempo_text = fonte_ordenacao.render("5. Ordenar por Tempo", True, BRANCO)
                ordenar_modo_text = fonte_ordenacao.render("6. Ordenar por Modo", True, BRANCO)
                tela.blit(ordenar_nome_text, (50, 50))
                tela.blit(ordenar_tempo_text, (250, 50))
                tela.blit(ordenar_modo_text, (450, 50))
                pygame.display.flip()

                # Aguarda o jogador escolher uma ordenação
                ordenacao_escolhida = None
                while ordenacao_escolhida is None:
                    for evento in pygame.event.get():
                        if evento.type == pygame.QUIT:
                            pygame.quit()
                            sys.exit()
                        if evento.type == pygame.KEYDOWN:
                            if evento.key == pygame.K_4:
                                ordenacao_escolhida = "nome"
                            elif evento.key == pygame.K_5:
                                ordenacao_escolhida = "tempo"
                            elif evento.key == pygame.K_6:
                                ordenacao_escolhida = "modo"
                            elif evento.key == pygame.K_ESCAPE:
                                return

                # Aplica a ordenação
                if ordenacao_escolhida == "nome":
                    historico[1:] = sorted(historico[1:], key=lambda x: x[0])  # Ordena por nome
                elif ordenacao_escolhida == "tempo":
                    historico[1:] = sorted(historico[1:], key=lambda x: float(x[2]))  # Ordena por tempo
                elif ordenacao_escolhida == "modo":
                    historico[1:] = sorted(historico[1:], key=lambda x: x[3])  # Ordena por modo

                # Pesquisa
                fonte_pesquisa = pygame.font.Font(None, 24)
                pesquisa_text = fonte_pesquisa.render("Digite o nome do jogador e pressione ENTER:", True, BRANCO)
                tela.blit(pesquisa_text, (50, 90))
                pygame.display.flip()

                # Captura o nome do jogador para pesquisa
                nome_pesquisa = ""
                pesquisando = True
                while pesquisando:
                    for evento in pygame.event.get():
                        if evento.type == pygame.QUIT:
                            pygame.quit()
                            sys.exit()
                        if evento.type == pygame.KEYDOWN:
                            if evento.key == pygame.K_RETURN:
                                pesquisando = False
                            elif evento.key == pygame.K_BACKSPACE:
                                nome_pesquisa = nome_pesquisa[:-1]
                            else:
                                nome_pesquisa += evento.unicode

                    # Exibe o nome digitado
                    tela.fill(PRETO, (50, 120, LARGURA - 100, 30))
                    texto_digitado = fonte_pesquisa.render(nome_pesquisa, True, BRANCO)
                    tela.blit(texto_digitado, (50, 120))
                    pygame.display.flip()

                # Aplica a pesquisa
                if nome_pesquisa.strip():
                    historico = [historico[0]] + [linha for linha in historico[1:] if nome_pesquisa.lower() in linha[0].lower()]

                # Exibe o histórico com numeração e formatação
                fonte = pygame.font.Font(None, 23)
                y = 150  # Posição vertical inicial para o texto
                for i, linha in enumerate(historico[1:], start=1):  # Ignora o cabeçalho
                    texto = f"{i}. Jogador: {linha[0]}, Resultado: {linha[1]}, Tempo: {float(linha[2]):.2f}s, Modo: {linha[3]}"
                    texto_renderizado = fonte.render(texto, True, BRANCO)
                    tela.blit(texto_renderizado, (50, y - scroll_y))  # Aplica a rolagem
                    y += linha_altura  # Move para a próxima linha

                # Controle de rolagem
                if y > ALTURA - 50:  # Se o histórico for maior que a tela
                    scroll_ativo = True
                else:
                    scroll_ativo = False

            else:
                texto = "Nenhum histórico de partidas encontrado."
                texto_renderizado = fonte.render(texto, True, BRANCO)
                tela.blit(texto_renderizado, (50, 50))
    except FileNotFoundError:
        texto = "Nenhum histórico de partidas encontrado."
        texto_renderizado = fonte.render(texto, True, BRANCO)
        tela.blit(texto_renderizado, (50, 50))

    # Botão para voltar ao menu
    fonte_botao = pygame.font.Font(None, 40)
    voltar_texto = fonte_botao.render("Voltar ao Menu (ESC)", True, BRANCO)
    tela.blit(voltar_texto, (LARGURA // 2 - voltar_texto.get_width() // 2, ALTURA - 50))
    pygame.display.flip()

    # Aguarda o jogador pressionar ESC para voltar ao menu
    while True:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    return
            if evento.type == pygame.MOUSEBUTTONDOWN and scroll_ativo:
                if evento.button == 4:  # Scroll up
                    scroll_y = max(0, scroll_y - linha_altura)
                elif evento.button == 5:  # Scroll down
                    scroll_y = min(y - (ALTURA - 150), scroll_y + linha_altura)
                # Redesenha o histórico com a nova posição de rolagem
                tela.fill(PRETO)
                y = 150
                for i, linha in enumerate(historico[1:], start=1):
                    texto = f"{i}. Jogador: {linha[0]}, Resultado: {linha[1]}, Tempo: {float(linha[2]):.2f}s, Modo: {linha[3]}"
                    texto_renderizado = fonte.render(texto, True, BRANCO)
                    tela.blit(texto_renderizado, (50, y - scroll_y))
                    y += linha_altura
                tela.blit(voltar_texto, (LARGURA // 2 - voltar_texto.get_width() // 2, ALTURA - 50))
                pygame.display.flip()

# Função principal do jogo
def main():
    while True:
        modo_jogo = tela_selecao()

        if modo_jogo == "single":
            dificuldade = tela_dificuldade()
            try:
                mapa = gerar_mapa(21, 21, dificuldade)
            except Exception as e:
                print(e)
                fonte = pygame.font.Font(None, 50)
                erro_text = fonte.render("Erro ao gerar o labirinto. Tente novamente.", True, VERMELHO)
                tela.blit(erro_text, (LARGURA // 2 - erro_text.get_width() // 2, ALTURA // 2))
                pygame.display.flip()
                pygame.time.wait(3000)
                continue

            # Lógica do jogo singleplayer
            jogador_pos = [1, 1]
            start_time = time.time()
            rodando = True
            while rodando:
                for evento in pygame.event.get():
                    if evento.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()

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

                                # Salva o histórico
                                nome_jogador = "Jogador 1"  # Substitua por um nome real ou input do usuário
                                salvar_historico(nome_jogador, "Vitória", tempo_total, "single")

                                # Exibe o menu pós-vitória
                                escolha = tela_pos_vitoria()
                                if escolha == "menu":
                                    break
                                elif escolha == "historico":
                                    exibir_historico_tela()
                                elif escolha == "sair":
                                    pygame.quit()
                                    sys.exit()

                desenhar_mapa(mapa, jogador_pos)

        elif modo_jogo == "multi":
            try:
                client.sendall("start_multi".encode())
                data = client.recv(4096).decode()
                mapa = json.loads(data)
            except Exception as e:
                print(f"Erro ao conectar ao servidor: {e}")
                continue

            # Lógica do jogo multiplayer
            jogador_pos = [1, 1]
            outro_jogador_pos = None
            start_time = time.time()
            rodando = True
            while rodando:
                for evento in pygame.event.get():
                    if evento.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()

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

                                # Salva o histórico
                                nome_jogador = "Jogador 2"  # Substitua por um nome real ou input do usuário
                                salvar_historico(nome_jogador, "Vitória", tempo_total, "multi")

                                # Exibe o menu pós-vitória
                                escolha = tela_pos_vitoria()
                                if escolha == "menu":
                                    break
                                elif escolha == "historico":
                                    exibir_historico_tela()
                                elif escolha == "sair":
                                    pygame.quit()
                                    sys.exit()

                desenhar_mapa(mapa, jogador_pos, outro_jogador_pos)

        elif modo_jogo == "historico":
            exibir_historico_tela()

# Inicia o jogo
if __name__ == "__main__":
    main()