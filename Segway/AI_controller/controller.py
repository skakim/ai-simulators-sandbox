# -*- coding: utf-8 -*-
import numpy
from .state import State
import random
import datetime, time

class Controller:
    def __init__(self, game, load, state):
        self.initialize_parameters(game, load, state)

    def initialize_parameters(self, game, load,state):
        self.state = state
        if load == None:
            self.parameters = numpy.random.normal(0, 1, 3*len(self.compute_features()))
        else:
            params = open(load, 'r')
            weights = params.read().split("\n")
            self.parameters = [float(x.strip()) for x in weights[0:-1]]


    def output(self, episode, performance):
       print "Performance do episodio #%d: %d" % (episode, performance)
       if episode > 0 and episode % 10 == 0:
           output = open("./params/%s.txt" % datetime.datetime.fromtimestamp(time.time()).strftime('%Y%m%d%H%M%S'), "w+")
           for parameter in self.parameters:
               output.write(str(parameter) + "\n")
#--------------------------------------------------------------------------------------------------------

    #FUNCAO A SER COMPLETADA. Deve utilizar os pesos para calcular as funções de preferência Q para cada ação e retorna
    #-1 caso a ação desejada seja esquerda, +1 caso seja direita, e 0 caso seja ação nula
    def take_action(self, state):
        return 0

    #FUNCAO A SER COMPLETADA. Deve calcular features expandidas do estados
    def compute_features(self):
        return [0]

    #FUNCAO A SER COMPLETADA. Deve atualizar a propriedade self.parameters
    def update(self, episode, performance):
        pass
