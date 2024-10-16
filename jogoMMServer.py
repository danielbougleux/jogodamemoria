from socket import *
import sys
import random
import argparse
from time import sleep
import pickle
from constants import Codes
from typing import Tuple, List

serverName=''
serverPort=56211

def cli() -> argparse.Namespace:
    
    parser = argparse.ArgumentParser(prog='JogoDaMemoriaServer', description='Servidor do jogo da memória')
    
    parser.add_argument('-d', '--dimensao', type=int, default=4, help='A dimensao do tabuleiro do jogo')
    parser.add_argument('-n', '--numero_de_jogadores', type=int, default=2, help='A quantidade de jogadores a participarem de cada jogo')
    
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)
    
    args = parser.parse_args()
    
    if args.dimensao % 2 != 0 or args.dimensao >= 10:
        print('A dimensão deve ser um número par menor que 10')
        sys.exit(1)
    
    if args.numero_de_jogadores < 2:
        print('O numero de jogadores deve ser maior ou igual a 2')
        sys.exit(1)      
    
    return args  

# Cria um novo placar zerado.
def novoPlacar(nJogadores):

    return [0] * nJogadores

# Cria um novo tabuleiro com pecas aleatorias. 
# 'dim' eh a dimensao do tabuleiro, necessariamente
# par.
def novoTabuleiro(dim: int) -> List[List[int]]:

    # Cria um tabuleiro vazio.
    tabuleiro = []
    for i in range(0, dim):

        linha = []
        for j in range(0, dim):

            linha.append(0)

        tabuleiro.append(linha)

    # Cria uma lista de todas as posicoes do tabuleiro. Util para
    # sortearmos posicoes aleatoriamente para as pecas.
    posicoesDisponiveis = []
    for i in range(0, dim):

        for j in range(0, dim):

            posicoesDisponiveis.append((i, j))

    # Varre todas as pecas que serao colocadas no 
    # tabuleiro e posiciona cada par de pecas iguais
    # em posicoes aleatorias.
    for j in range(0, dim // 2):
        for i in range(1, dim + 1):

            # Sorteio da posicao da segunda peca com valor 'i'
            maximo = len(posicoesDisponiveis)
            indiceAleatorio = random.randint(0, maximo - 1)
            rI, rJ = posicoesDisponiveis.pop(indiceAleatorio)

            tabuleiro[rI][rJ] = i

            # Sorteio da posicao da segunda peca com valor 'i'
            maximo = len(posicoesDisponiveis)
            indiceAleatorio = random.randint(0, maximo - 1)
            rI, rJ = posicoesDisponiveis.pop(indiceAleatorio)

            tabuleiro[rI][rJ] = i

    return tabuleiro

if __name__ == "__main__":
    
    arguments = cli()
    
    serverSocket= socket(AF_INET,SOCK_STREAM)
    serverSocket.bind((serverName,serverPort))
    serverSocket.listen()
    
    tabuleiro = novoTabuleiro(arguments.dimensao)
    placar = novoPlacar(arguments.numero_de_jogadores)
    
    clients : List[socket] = []
    
    #Espera a conexao dos jogadores
    for i in range(arguments.numero_de_jogadores):

        connectionSocket, _ = serverSocket.accept()
        clients.append(connectionSocket)
    
    #Envia as informacoes de inicio do jogo
    for index,connection in enumerate(clients):

        msg={
            'type': Codes.UPDATE,
            'tabuleiro':tabuleiro,
            'placar': placar,
            'id':index
        }
        
        connection.sendall(pickle.dumps(msg))

    total_de_pares = arguments.dimensao**2 / 2
    pares_encontrados = 0
    jogador_atual = 0

    while pares_encontrados < total_de_pares:
        
        ##envia qual eh o jogador atual
        for connection in clients:
            connection.sendall(pickle.dumps({
                'type': Codes.PLAY,
                'jogador': jogador_atual
            }))
        
        #espera a jogada
        jogada: Tuple[Tuple[int, int]] = pickle.loads(clients[jogador_atual].recv(1024))

        coord1, coord2 = jogada
        i1, j1 = coord1
        i2, j2 = coord2

        print("Pecas escolhidas --> ({0}, {1}) e ({2}, {3})\n".format(i1, j1, i2, j2))

        break
        """
        if tabuleiro[i1][j1] == tabuleiro[i2][j2]:
            
            for connection in clients:
                connection.send(pickle.dumps('acertou'))

        else:

            for connection in clients:
                connection.send(pickle.dumps('errou'))

        sleep(5)
        """

    #Dizer qual é o proximo jogador
    #Receber a jogada
    #Transmitir a jogada
    #Atualiza seu tabuleiro e placar
    #repeat
    
    serverSocket.close()
