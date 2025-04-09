
#Nodo genérico de un algortimos de búsqueda heurística
class Node:

    def __init__(self,parent,g):
        self.parent = parent
        self.g = g
        self.h = 0.0

    def GetParent(self):
        return self.parent
    
    #comprueba que dos nodos son iguales (se necesita reimplementar)
    def __repr__(self):
        pass
    
    #comprueba que dos nodos son iguales (se necesita reimplementar)
    def __eq__(self, other):
        raise NotImplementedError("__eq__ debe ser reimplementado en la clase hija")
        return False
    

    def __hash__(self):
        pass
    
    #Establece el nodo padre para poder reconstruir el path solución
    def SetParent(self, p):
        self.parent = p

    #Calcula el coste estimado F = G+H
    def F(self):
        return self.g + self.h
    
    #establecemos el coste de llegar desde initi a este nodo (G)
    def SetG(self, g):
        self.g = g

    #Establecemos el valor de la heuristica, necesitaremos la clase problema que es la que sabe como calcularlo.
    def SetH(self, h):
        self.h = h
    
    #Devolvemos el valor del coste G
    def G(self):
        return self.g
    
    #Devolvemos el valor de la función euristica calculada H
    def H(self):
        return self.h
    
    def toString(self):
        return str(self.__repr__())