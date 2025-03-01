# Autores: Pablo García Fernández, Yuriy Chaban Markevych
# El nombre de esta archivo y esta clase es en honor a Perry el Ornitorrinco, que merece su reconocimiento como buen agente que es

import random
from BaseAgent import  BaseAgent

class PerryElOrnitorrinco (BaseAgent):
    def __init__(self, id, name):
        super().__init__(id, name)

    def Update(self, perception):
        action = random.randint(0,4)
        disparar = False
        return action, disparar