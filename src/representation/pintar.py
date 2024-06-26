from treelib import Node, Tree
class TreeMio:
    def __init__(self, expr, parent):
        tree = Tree()

    def crearHijo(self,hijo,padre):
        self.create_node(hijo, hijo, parent=padre)
        
    def crearPadre(self,padre):
        self.create_node(padre, padre)    

    def pintarTree(self):   
        self.show()
