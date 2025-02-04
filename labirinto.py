import random

def gerar_mapa(altura, largura):
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

    return mapa

if __name__ == "__main__":
    mapa_teste = gerar_mapa(21, 21)
    for linha in mapa_teste:
        print("".join(linha))
