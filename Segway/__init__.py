import pyglet
import pymunk
from sys import argv

from game_elements.window import Game
from game_elements.versus import Versus
from AI_controller import Learner


if __name__ == '__main__':
        space = pymunk.Space()

        if len(argv) < 2:
            print "Modo: "
            print "     python __init__.py [learn|evaluate|versus] <arquivo de pesos>"
            print "         learn: aplica o algoritmo de aprendizado (pode receber pesos ou gerar pesos iniciais aleatorios)"
            print "         evaluate: exibe o jogo, permite avaliar os pesos encontrados"
            print "         arquivo de pesos: deve conter os pesps iniciais para as features do sistema"
        else:
            if argv[1] == "learn":
                if len(argv) == 3:
                    game = Game(space = space, run_pyglet = False, load = argv[2])
                else:
                    print "\n\nGerando pesos aleatorios."
                    game = Game(space = space, run_pyglet = False, load = None)
                while True:
                    game.update(1/60.0)
            elif argv[1] == "evaluate":
                if len(argv) == 3:
                    window = Game(space = space, run_pyglet = True, load = argv[2])
                else:
                    print "\nArquivo de pesos deve ser informado."
                    exit()
            elif argv[1] == "versus":
                game = Versus(space = space, load_p1 = argv[2], load_p2 = argv[3])
            pyglet.app.run()
