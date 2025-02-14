# 🎮 Labirinto Multiplayer

Este é um jogo de labirinto multiplayer desenvolvido em Python, utilizando a biblioteca Pygame para a interface gráfica e sockets para a comunicação em rede entre os jogadores. O objetivo do jogo é navegar pelo labirinto e chegar ao ponto final antes do outro jogador.

## 🚀 Funcionalidades

- **Modo Singleplayer:** Jogue sozinho em um labirinto gerado aleatoriamente.
- **Modo Multiplayer:** Conecte-se a um servidor e jogue contra outro jogador em tempo real.
- **Geração de Labirintos:** Labirintos são gerados dinamicamente com diferentes níveis de dificuldade.
- **Histórico de Partidas:** Salve e visualize o histórico de partidas, incluindo tempo e resultado.

## 🛠️ Pré-requisitos

Antes de começar, você precisará ter instalado:

- **Python 3.8 ou superior**
- **Pygame** (para a interface gráfica)
- **Biblioteca padrão do Python** (`socket`, `threading`, `json`, `csv`, etc.)

### Instalação das Dependências

Para instalar o Pygame, execute o seguinte comando:

```bash
pip install pygame
```

## 🖥️ Como Executar

### Servidor

1. Navegue até o diretório do projeto.
2. Execute o servidor:

   ```bash
   python server.py
   ```

   O servidor estará aguardando conexões na porta `12345` e escutando em todas as interfaces de rede (`0.0.0.0`).

### Cliente

1. Navegue até o diretório do projeto.
2. Execute o cliente:

   ```bash
   python cliente.py
   ```

   O cliente se conectará automaticamente ao servidor e permitirá que você escolha entre os modos Singleplayer e Multiplayer.

## 🎲 Como Jogar

### Singleplayer

1. Escolha o modo **Singleplayer** no menu inicial.
2. Selecione a dificuldade do labirinto.
3. Use as teclas **W, A, S, D** para mover o jogador.
4. Encontre o ponto final (**F**) para vencer.

### Multiplayer

1. Escolha o modo **Multiplayer** no menu inicial.
2. Insira seu nome e aguarde a conexão com outro jogador.
3. Use as teclas **W, A, S, D** para mover o jogador.
4. Encontre o ponto final (**F**) antes do outro jogador para vencer.

## 📊 Histórico de Partidas

O jogo salva automaticamente o histórico de partidas em um arquivo `historico.csv`. Você pode visualizar o histórico no menu do jogo, filtrando por modo de jogo (Singleplayer ou Multiplayer) e ordenando por nome, tempo ou resultado.

## 🐛 Problemas Conhecidos

- **Desconexão no Multiplayer:** Em alguns casos, o segundo jogador pode ser desconectado ao entrar no jogo. Isso está sendo investigado.
- **Dados Inválidos:** O servidor pode receber dados inválidos dos clientes, causando erros de decodificação JSON.

## 🤝 Contribuição

Contribuições são bem-vindas! Siga os passos abaixo:

1. Faça um fork do projeto.
2. Crie uma branch para sua feature (`git checkout -b feature/nova-feature`).
3. Commit suas mudanças (`git commit -m 'Adiciona nova feature'`).
4. Faça um push para a branch (`git push origin feature/nova-feature`).
5. Abra um Pull Request.

## 📄 Licença

Este projeto está licenciado sob a Licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

---

### Estrutura do Projeto

```
labirinto-multiplayer/
├── server.py            # Código do servidor
├── cliente.py           # Código do cliente
├── labirinto.py         # Lógica de geração de labirintos
├── historico.csv        # Arquivo de histórico de partidas
├── README.md            # Este arquivo
└── LICENSE              # Licença do projeto
```

---

### Autor

- **Kaio** - [GitHub](https://github.com/DevKaioD)

---

Esse README está pronto para ser usado no seu repositório do GitHub. Se precisar de mais alguma coisa, estou à disposição! 😊
