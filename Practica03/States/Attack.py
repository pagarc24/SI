from StateMachine.State import State
from States.AgentConsts import AgentConsts

#Estado que nos permite atacar un objetivos desde la celda adyacente.
# se espera que el agente ay esté orientado
#agent.directionToLook es seteado por ExecutePlan para indicarnos cual es la dirección
#donde está el enemigo a atacar
class Attack(State):

    def __init__(self, id):
        super().__init__(id)
        self.directionToLook = -1

    def Update(self, perception, map, agent):
        self.directionToLook=agent.directionToLook
        return 0, True

    def Transit(self,perception, map):
        target = perception[self.directionToLook]
        #si mi target ya no está vuelvo a ExecutePlan
        if target != AgentConsts.PLAYER or target != AgentConsts.COMMAND_CENTER:
            return "ExecutePlan"
        return self.id
    