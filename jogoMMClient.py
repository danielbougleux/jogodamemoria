import argparse
import pickle
import sys
import os
from constants import Codes
from socket import *


def cli() -> argparse.Namespace:
    
    parser = argparse.ArgumentParser(prog='JogoDaMemoriaCliente', description='Cliente do jogo da memória')
    
    parser.add_argument('-i', '--ip-address', type=str, default='localhost', help='O endereco ip do sevidor')
    parser.add_argument('-p', '--port', type=int, default=56211, help='A porta onde o servidor escuta')

    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)
    
    return parser.parse_args()

def limpaTela():
    
    os.system('cls' if os.name == 'nt' else 'clear')

# Imprime estado atual do tabuleiro
def imprimeTabuleiro(tabuleiro):

    # Limpa a tela
    limpaTela()

    # Imprime coordenadas horizontais
    dim = len(tabuleiro)
    sys.stdout.write("     ")
    for i in range(0, dim):
        sys.stdout.write("{0:2d} ".format(i))

    sys.stdout.write("\n")

    # Imprime separador horizontal
    sys.stdout.write("-----")
    for i in range(0, dim):
        sys.stdout.write("---")

    sys.stdout.write("\n")

    for i in range(0, dim):

        # Imprime coordenadas verticais
        sys.stdout.write("{0:2d} | ".format(i))

        # Imprime conteudo da linha 'i'
        for j in range(0, dim):

            # Peca ja foi removida?
            if tabuleiro[i][j] == '-':

                # Sim.
                sys.stdout.write(" - ")

            # Peca esta levantada?
            elif tabuleiro[i][j] >= 0:

                # Sim, imprime valor.
                sys.stdout.write("{0:2d} ".format(tabuleiro[i][j]))
            else:

                # Nao, imprime '?'
                sys.stdout.write(" ? ")

        sys.stdout.write("\n")

# Imprime o placar atual.
def imprimePlacar(placar):

    nJogadores = len(placar)

    print("Placar:")
    print("---------------------")
    for i in range(0, nJogadores):
        print("Jogador {0}: {1:2d}".format(i + 1, placar[i]))

if __name__ == '__main__':
    
    arguments = cli()

    clientSocket = socket(AF_INET,SOCK_STREAM)
    clientSocket.connect((arguments.ip_address,arguments.port))
    
    print('Aguardando Jogadores...')
    
    #recebe o id do cliente
    meu_id = -1
    tabuleiro = []
    placar = []
    
    while True:

        nova_msg= pickle.loads(clientSocket.recv(1024))

        if nova_msg['type'] == Codes.UPDATE:
            
            tabuleiro = nova_msg['tabuleiro']
            meu_id = nova_msg['id']
            placar = nova_msg['placar']

            imprimeTabuleiro(tabuleiro)
            imprimePlacar(placar)
            print(meu_id)
            
        elif nova_msg['type'] == Codes.PLAY:

            if nova_msg['jogador'] == meu_id:
                clientSocket.sendall(pickle.dumps(((0,1),(1,1))))
            else:
                print('Aguardando jogador {0}'.format(nova_msg['jogador']+1))

            break

    clientSocket.close()
    
    #pega o id da vez
    #se for o id vez joga
    #se não, recebe a jogada
    #atualiza o tabuleiro
    # atualiza o placar