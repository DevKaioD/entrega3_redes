import random

def gerar_mapa(altura, largura, dificuldade="medio", max_tentativas=100):
    """
    Gera um labirinto aleatório com paredes (#), caminho vazio ( ),
    ponto inicial (P) e ponto final (F).
    """
    if altura % 2 == 0:
        altura += 1
    if largura % 2 == 0:
        largura += 1

    tentativas = 0
    while tentativas < max_tentativas:
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
        if dificuldade == "facil":
            for y in range(1, altura - 1):
                for x in range(1, largura - 1):
                    if mapa[y][x] == "#" and random.random() < 0.3:
                        mapa[y][x] = " "
        elif dificuldade == "dificil":
            for y in range(1, altura - 1):
                for x in range(1, largura - 1):
                    if mapa[y][x] == " " and random.random() < 0.3:
                        mapa[y][x] = "#"

        # Verifica se o ponto final ainda está acessível
        if verificar_caminho_valido(mapa, start_x, start_y, end_x, end_y):
            return mapa

        tentativas += 1

    raise Exception("Não foi possível gerar um labirinto válido após várias tentativas.")

def verificar_caminho_valido(mapa, start_x, start_y, end_x, end_y):
    """
    Verifica se há um caminho válido do ponto inicial ao ponto final.
    """
    visitados = [[False for _ in range(len(mapa[0]))] for _ in range(len(mapa))]
    fila = [(start_x, start_y)]
    visitados[start_y][start_x] = True

    while fila:
        x, y = fila.pop(0)
        if x == end_x and y == end_y:
            return True

        for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < len(mapa[0]) and 0 <= ny < len(mapa):
                if mapa[ny][nx] != "#" and not visitados[ny][nx]:
                    visitados[ny][nx] = True
                    fila.append((nx, ny))

    return False

if __name__ == "__main__":
    mapa_teste = gerar_mapa(21, 21, "dificil")
    for linha in mapa_teste:
        print("".join(linha))