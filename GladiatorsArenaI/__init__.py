from sys import argv
from Simulator.simulator import game
from Simulator.versus import versus

if __name__ == '__main__':

        if len(argv) < 3:
            print "Modo: "
            print "     python __init__.py [learn|evaluate|versus] [lazy_bot|random_bot|normal_bot|ninja_bot]  <arquivo de pesos>"
            print "         learn: aplica o algoritmo de aprendizado (pode receber pesos ou gerar pesos iniciais aleatorios)"
            print "         evaluate: exibe o jogo, permite avaliar os pesos encontrados"
            print "         versus: semelhante ao modo evaluate, porem com duas IA's"
            print "         [lazy_bot|random_bot|normal_bot|ninja_bot]: modo do bot"
            print "         arquivo de pesos: deve conter os pesos iniciais para as features do sistema (pode ser omitido no modo learn)"
        else:
            if argv[1] == "learn":
                if len(argv) == 4:
                    game("learn", argv[3], argv[2])
                else:
                    print "\n\nGerando pesos aleatorios."
                    game("learn", None, argv[2])
            elif argv[1] == "evaluate":
                if len(argv) == 4:
                    game("evaluate", argv[3], argv[2])
                else:
                    print "\nArgumentos faltando"
                    exit()
            elif argv[1] == "versus":
                versus(argv[2], argv[3])
