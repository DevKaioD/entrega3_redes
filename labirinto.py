import random

def gerar_mapa(altura, largura, dificuldade="dificuldade1"):
    """
    Gera um labirinto aleatório com paredes (#), caminho vazio ( ),
    ponto inicial (P) e ponto final (F).
    """
    if altura % 2 == 0:
        altura += 1
    if largura % 2 == 0:
        largura += 1

    mapa = [["#" for _ in range(largura)] for _ in range(altura)]
    start_x, start_y = 1, 1
    mapa[start_y][start_x] = "P"
    end_x, end_y = largura - 2, altura - 2
    mapa[end_y][end_x] = "F"

    def obter_vizinhos(x, y):
        direcoes = [(0, -2), (0, 2), (-2, 0), (2, 0)]
        vizinhos = []
        for dx, dy in direcoes:
            nx, ny = x + dx, y + dy
            if 0 < nx < largura - 1 and 0 < ny < altura - 1:
                vizinhos.append((nx, ny))
        return vizinhos

    def criar_caminho(x, y):
        direcoes = obter_vizinhos(x, y)
        random.shuffle(direcoes)
        for nx, ny in direcoes:
            if mapa[ny][nx] == "#":
                parede_x, parede_y = (x + nx) // 2, (y + ny) // 2
                mapa[parede_y][parede_x] = " "
                mapa[ny][nx] = " "
                criar_caminho(nx, ny)

    criar_caminho(start_x, start_y)

    # Garante que o ponto final esteja acessível
    if mapa[end_y - 1][end_x] == "#":
        mapa[end_y - 1][end_x] = " "
    if mapa[end_y][end_x - 1] == "#":
        mapa[end_y][end_x - 1] = " "

    # Ajusta a dificuldade
    if dificuldade == "dificuldade1":
        # Dificuldade 1: Menos paredes extras
        for y in range(1, altura - 1):
            for x in range(1, largura - 1):
                if mapa[y][x] == "#" and random.random() < 0.2:  # 20% de chance de remover parede
                    mapa[y][x] = " "
    elif dificuldade == "dificuldade2":
        # Dificuldade 2: Modo médio original (sem adicionar paredes extras)
        pass  # Não fazemos nada, mantendo o labirinto gerado inicialmente

    return mapa

if __name__ == "__main__":
    mapa_teste = gerar_mapa(21, 21, "dificuldade2")
    for linha in mapa_teste:
        print("".join(linha))