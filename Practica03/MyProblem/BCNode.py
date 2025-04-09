from AStar.Node import Node

#Clase que implementa un nodo de BattleCity
#A parte de los datos por defecto, implementamos el método 
#IsEqual que nos ayudará a detectar cuando dos nosdos son iguales
class BCNode(Node):
    def __init__(self, parent, g, value, x, y):
        super().__init__(parent, g)
        self.value = value
        self.x = int(x)
        self.y = int(y)
    
    def __repr__(self):
        return f"BCNode(x={self.x}, y={self.y})"

    def __eq__(self, other):
        if other == None:
            return False
        #dos nodos son iguales cuando sus coordenadas x e y son iguales.
        return self.x == other.x and self.y == other.y

    def __hash__(self):
        return hash((self.x, self.y))