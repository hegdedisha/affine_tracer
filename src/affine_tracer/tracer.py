from __future__ import annotations

import numpy as np
import scipy
from icecream import ic
from plum import dispatch

from .inv_egglog import Matrix

# this is connected, directed. Is is also cyclic? - no
class polytree(object):

    def __init__(self, nodes = None):
        self.tag_val = 97
        self.nodes = [node(operator=1, operation=Id, parent_tree=self, tag = chr(self.tag_val))]
        self.last_node = chr(self.tag_val)
        self.tag_val = self.tag_val + 1
        pass

    def list_node_details(self):
        for node in self.nodes:
            print('tag', node.tag)
            print('ancestors',node.list_ans())
            print('descendents',node.list_des())

    def list_node_values(self):
        for node in self.nodes:
            print('tag', node.tag)
            print('operation',node.operation)
            print('operator',node.operator)
            print('value',node.value)

    def add_node(self, new_node):
        self.nodes = self.nodes + [new_node]
        self.last_node = chr(self.tag_val)
        new_node.tag = self.last_node
        new_node.parent_tree = self
        # ic(new_node.tag)
        self.tag_val = self.tag_val + 1
        # ic(self.nodes)
        pass

    
    def clear_node_value(self, nodes = None):
        if nodes is None:
            nodes = self.nodes
        for node in nodes:
            if node.val_use >= len(node.descendents):
                node.value = None

    def reset(self):
        for node in self.nodes:
            node.value = None
            node.val_use = 0

    pass

class node():

    __array_priority__ = 1000

    # saves memory?
    __slots__ = ('operation', 'operator', 'ancestors', 'descendents', 'tag', 'parent_tree', 'value', 'val_use', 'expr', 'swap')

    def __init__(self, operator, operation, parent_tree = None, tag = None, ancestors = [], descendents = []):
        self.operation = operation
        self.operator = operator
        self.ancestors = ancestors
        self.descendents = descendents
        self.tag = tag
        self.parent_tree = parent_tree
        self.value = None
        self.val_use = 0
        self.expr = None
        self.swap = False
        pass

    def list_ans(self):
        ls = []
        # ic('---------------------------------------------')
        for ans in self.ancestors:
            ls = ls + [ans.tag]
        return ls
    
    def list_des(self):
        ls = []
        # ic
        # ic('---------------------------------------------')
        for des in self.descendents:
            # ic(des.tag)
            ls = ls + [des.tag]
        # ic('---------------------------------------------')
        # ic(ls)
        return ls

    @dispatch   
    def __radd__(self, a: node):
        # ic('node addition')
        new_node = node(operator = [self, a], operation=NodesSum, ancestors= [self, a])
        self.parent_tree.add_node(new_node)
        a.descendents = a.descendents + [new_node]
        self.descendents =  self.descendents + [new_node]
        return new_node
    
    @dispatch
    def __radd__(self, a: np.ndarray):
        new_node = node(a, Shift, ancestors= [self])
        self.parent_tree.add_node(new_node)
        self.descendents = self.descendents + [new_node]
        return new_node

    @dispatch
    def __radd__(self, a: float):
        new_node = node(a, Shift, ancestors= [self])
        self.parent_tree.add_node(new_node)
        self.descendents = self.descendents + [new_node]
        return new_node
    
    @dispatch
    def __radd__(self, a: int):
        new_node = node(a, Shift, ancestors= [self])
        self.parent_tree.add_node(new_node)
        self.descendents = self.descendents + [new_node]
        return new_node

    @dispatch   
    def __add__(self, a: node):
        # ic('node addition')
        # ic(self.descendents)
        # ic(self.tag)
        # ic(a.descendents)
        # ic(a.tag)
        new_node = node(operator = [self, a], operation=NodesSum, ancestors= [self, a])
        self.parent_tree.add_node(new_node)
        a.descendents = a.descendents + [new_node]
        self.descendents =  self.descendents + [new_node]
        # ic(self.descendents)
        # ic(a.descendents)
        return new_node
    
    @dispatch   
    def __add__(self, a: np.ndarray):
        new_node = node(a, Shift, ancestors= [self])
        self.parent_tree.add_node(new_node)
        self.descendents = self.descendents + [new_node]
        return new_node
    
    @dispatch   
    def __add__(self, a: float):
        new_node = node(a, Shift, ancestors= [self])
        self.parent_tree.add_node(new_node)
        self.descendents = self.descendents + [new_node]
        return new_node
    
    @dispatch   
    def __add__(self, a: int):
        new_node = node(a, Shift, ancestors= [self])
        self.parent_tree.add_node(new_node)
        self.descendents = self.descendents + [new_node]
        return new_node
    
    def __mul__(self, a):
        new_node = node(a, ScalarMultiply, ancestors= [self])
        # ic('scmul')
        self.parent_tree.add_node(new_node)
        self.descendents = self.descendents + [new_node]
        return new_node
        # -----------------------------------------------
        # return new_node
    
    def __rmul__(self, a):
        new_node = node(a, ScalarMultiply, ancestors= [self])
        # ic('scmul')
        self.parent_tree.add_node(new_node)
        self.descendents = self.descendents + [new_node]
        return new_node
    
    def __matmul__(self, A):
        new_node = node(A, MatMultiply, ancestors= [self])
        # ic('scmul')
        self.parent_tree.add_node(new_node)
        self.descendents = self.descendents + [new_node]
        return new_node
        # -----------------------------------------------
        # return new_node
    
    def __rmatmul__(self, A):
        new_node = node(A, RMatMultiply, ancestors= [self])
        # ic('scmul')
        self.parent_tree.add_node(new_node)
        self.descendents = self.descendents + [new_node]
        return new_node

    @dispatch   
    def __rsub__(self, a: node):
        # ic('node addition')
        new_node = node(operator = [self, a], operation=RNodesSub, ancestors= [self, a])
        self.parent_tree.add_node(new_node)
        a.descendents = a.descendents + [new_node]
        self.descendents =  self.descendents + [new_node]
        return new_node
    
    @dispatch
    def __rsub__(self, a: np.ndarray):
        new_node = node(a, RShift, ancestors= [self])
        self.parent_tree.add_node(new_node)
        self.descendents = self.descendents + [new_node]
        return new_node

    @dispatch
    def __rsub__(self, a: float):
        new_node = node(a, RShift, ancestors= [self])
        self.parent_tree.add_node(new_node)
        self.descendents = self.descendents + [new_node]
        return new_node
    
    @dispatch
    def __rsub__(self, a: int):
        new_node = node(a, RShift, ancestors= [self])
        self.parent_tree.add_node(new_node)
        self.descendents = self.descendents + [new_node]
        return new_node

    @dispatch   
    def __sub__(self, a: node):
        # ic('node addition')
        # ic(self.descendents)
        # ic(self.tag)
        # ic(a.descendents)
        # ic(a.tag)
        new_node = node(operator = [self, a], operation=NodesSub, ancestors= [self, a])
        self.parent_tree.add_node(new_node)
        a.descendents = a.descendents + [new_node]
        self.descendents =  self.descendents + [new_node]
        # ic(self.descendents)
        # ic(a.descendents)
        return new_node
    
    @dispatch   
    def __sub__(self, a: np.ndarray):
        new_node = node(-a, Shift, ancestors= [self])
        self.parent_tree.add_node(new_node)
        self.descendents = self.descendents + [new_node]
        return new_node
    
    @dispatch   
    def __sub__(self, a: float):
        new_node = node(-a, Shift, ancestors= [self])
        self.parent_tree.add_node(new_node)
        self.descendents = self.descendents + [new_node]
        return new_node
    
    @dispatch   
    def __sub__(self, a: int):
        new_node = node(-a, Shift, ancestors= [self])
        self.parent_tree.add_node(new_node)
        self.descendents = self.descendents + [new_node]
        return new_node

    def __neg__(self):
        new_node = node(-1, ScalarMultiply, ancestors= [self])
        self.parent_tree.add_node(new_node)
        self.descendents = self.descendents + [new_node]
        return new_node

def clear_node_value(node):
    if node.val_use >= len(node.descendents):
        node.value = None
        # ic(node.tag)
        # ic('-----------------------------------')
    pass


#more functions


def apply_all(graph: polytree, v):
    node = graph.nodes[0]
    v_app = v

    for node in graph.nodes:
        # ic(node.tag)
        # ic(node.descendents)
        # ic(len(node.descendents))
        v_app = node.operation.apply(node, v_app)
        
        # if len(node.descendents) > 1:
        #     ic(node.value)
        for ans in node.ancestors:
            clear_node_value(ans)
        node.value = v_app
    
    graph.reset()

    return v_app

def apply_linear_all(graph: polytree, v):
    node = graph.nodes[0]
    v_app = v

    for node in graph.nodes:
        v_app = node.operation.apply_linear(node, v_app)
        # ic(node.tag)
        # ic(node.descendents)
        # ic(len(node.descendents))
        # if len(node.descendents) > 1:
        #     ic(node.value)
        for ans in node.ancestors:
            clear_node_value(ans)
            pass
        node.value = v_app
    graph.reset()
    return v_app

def populate_node_val(node_local, value):
    if node_local.value is None:
        node_local.value = value
    else:
        node_local.value = node_local.value + value
    pass


#operation functions

class ScalarMultiply():
    def __init__(self):
        pass

    def apply(a, v):
        # ans_v = len(a.ancestors)
        # ic(ans_v)
        # if ans_v == 0:
        #     return a.operator * v
        # else:
        # ic(a.tag)
        # ic(a.operation)
        # ic('SCM')
        # ic(a.ancestors)
        # ic(a.ancestors[0].value)
        a.ancestors[0].val_use = a.ancestors[0].val_use + 1
        # if a.ancestors[0].val_use >= len(a.ancestors[0].descendents):
        #     a.ancestors[0].value = None
        return a.operator * a.ancestors[0].value
    
    def apply_linear(a, v):
        a.ancestors[0].val_use = a.ancestors[0].val_use + 1
        return a.operator * a.ancestors[0].value

    #done here
    def lapply_linear(a, graph):
        # ic('Scalar Multiply!')
        val_here = a.operator * a.value
        populate_node_val(next(graph.predecessors(a)), val_here)
        pass

    

    def build_expr(node_local, expr, val_dict, Adim):
        expr = node_local.ancestors[0].expr

        val = node_local.operator
        name = str(node_local.tag)
        mat = Matrix.named(name, row = 1, col = 1)
        val_dict[name] = val
        
        expr = mat @ expr 
        node_local.expr = expr

        return expr, val_dict
        
    pass



class Id():
    def __init__(self):
        pass

    def apply(a, v):
        a.value = v
        return v
    
    def apply_linear(a, v):
        a.value = v
        return v
    
    def lapply_linear(a, graph):
        val_here = a.value
        if len(list(graph.predecessors(a))) == 0:
            pass
        else:
            populate_node_val(next(graph.predecessors(a)), val_here)
        pass

    #this is done
    def build_expr(node_local, expr, val_dict, Adim):
        # Id_mat = Matrix.identity()
        expr = expr
        node_local.expr = expr
        return expr, val_dict
    
    pass

class Shift():
    def __init__(self):
        pass

    def apply(a, v):
        a.ancestors[0].val_use = a.ancestors[0].val_use + 1
        # if a.ancestors[0].val_use >= len(a.ancestors[0].descendents):
        #     a.ancestors[0].value = None
        return a.operator + a.ancestors[0].value

    def apply_linear(a, v):
        a.ancestors[0].val_use = a.ancestors[0].val_use + 1
        return a.ancestors[0].value
    
    #done here
    def lapply_linear(a, graph):
        # ic('Shift!')
        val_here = a.value
        populate_node_val(next(graph.predecessors(a)), val_here)
        pass
    
    def build_expr(node_local, expr, val_dict, Adim):
        expr = node_local.ancestors[0].expr
        if isinstance(node_local.operator, A_mat):
            mat = Matrix.sym('Amat', row = Adim, col = Adim)
        else:
            val = node_local.operator
            name = str(node_local.tag)
            # ic(val)
            # try:
            #     mat = Matrix.named(name, row = val.shape[0], col = val.shape[1])
            # except:
            #     mat = Matrix.named(name, row = val.shape[0], col = 1)
            val_dict[name] = val
        # expr = expr + mat 
        expr = expr
        node_local.expr = expr

        return expr, val_dict
    pass


class NodesSum():

    def __init__(self):
        pass

    def apply(a, v):
        node1 = a.operator[0]
        node2 = a.operator[1]

        ans_v = len(a.ancestors)
        if ans_v == 0:
            raise ValueError('Node sum needs ancestors')
        # ic('NodeSum')
        # ic(node1.value)
        # ic(node2.value)

        node1.val_use = node1.val_use + 1
        node2.val_use = node2.val_use + 1

        # if node1.val_use >= len(node1.descendents):
        #     node1.value = None
        # if node2.val_use >= len(node2.descendents):
        #     node2.value = None

        return node1.value + node2.value
    
    def apply_linear(a, v):
        node1 = a.operator[0]
        node2 = a.operator[1]

        ans_v = len(a.ancestors)
        if ans_v == 0:
            raise ValueError('Node sum needs ancestors')
        # ic('NodeSum')
        # ic(node1.value)
        # ic(node2.value)

        node1.val_use = node1.val_use + 1
        node2.val_use = node2.val_use + 1

        return node1.value + node2.value
    
    # done
    def lapply_linear(a, graph):

        val_here = a.value
        node_list = [a.operator[0], a.operator[1]]
        for node_local in node_list:
            # ic(node_local.tag)
            # ic(node_local.value)
            populate_node_val(node_local, val_here)

        pass
    
    def build_expr(node_local, expr, val_dict, Adim):
        expr1 = node_local.operator[0].expr
        expr2 = node_local.operator[1].expr

        expr = expr1 + expr2
        node_local.expr = expr

        return expr, val_dict

    pass


class RMatMultiply():
    def __init__(self):
        pass

    def apply(a, v):
        a.ancestors[0].val_use = a.ancestors[0].val_use + 1
        # if a.ancestors[0].val_use >= len(a.ancestors[0].descendents):
        #     a.ancestors[0].value = None
        return a.operator @ a.ancestors[0].value
    
    def apply_linear(a, v):
        a.ancestors[0].val_use = a.ancestors[0].val_use + 1
        return a.operator @ a.ancestors[0].value

    # done I think
    def lapply_linear(a, graph):
        # next(graph.predecessors(a)).val_use = next(graph.predecessors(a)).val_use + 1
        # return next(graph.predecessors(a)).value @ a.operator
        val_here = a.value @ a.operator
        populate_node_val(next(graph.predecessors(a)), val_here)
        pass

    def build_expr(node_local, expr, val_dict, Adim):
        expr = node_local.ancestors[0].expr
        # ic(node_local.operator)
        # ic(node_local.operator is A_mat)
        # ic(isinstance(node_local.operator, A_mat))
        if isinstance(node_local.operator, A_mat):
            mat = Matrix.sym('Amat', row = Adim, col = Adim)
        else:
            val = node_local.operator
            name = str(node_local.tag)
            # mat = Matrix.named(name, row = val.shape[0], col = val.shape[1])
            try:
                mat = Matrix.named(name, row = val.shape[0], col = val.shape[1])
            except:
                mat = Matrix.named(name, row = val.shape[0], col = 1)
            val_dict[name] = val
        expr = mat @ expr 
        node_local.expr = expr

        return expr, val_dict

    pass

class MatMultiply():
    def __init__(self):
        pass

    def apply(a, v):
        a.ancestors[0].val_use = a.ancestors[0].val_use + 1
        # if a.ancestors[0].val_use >= len(a.ancestors[0].descendents):
        #     a.ancestors[0].value = None
        return a.ancestors[0].value @ a.operator
    
    def apply_linear(a, v):
        a.ancestors[0].val_use = a.ancestors[0].val_use + 1
        return a.ancestors[0].value @ a.operator
    
    # this is done as well
    def lapply_linear(a, graph):
        # next(graph.predecessors(a)).val_use = next(graph.predecessors(a)).val_use + 1
        # return a.operator @ next(graph.predecessors(a)).value
        val_here = a.operator @ a.value
        populate_node_val(next(graph.predecessors(a)), val_here)
        pass
    
    def build_expr(node_local, expr, val_dict, Adim):
        expr = node_local.ancestors[0].expr
        if isinstance(node_local.operator, A_mat):
            mat = Matrix.sym('Amat', row = Adim, col = Adim)
        else:
            val = node_local.operator
            name = str(node_local.tag)
            # mat = Matrix.named(name, row = val.shape[0], col = val.shape[1])
            try:
                mat = Matrix.named(name, row = val.shape[0], col = val.shape[1])
            except:
                mat = Matrix.named(name, row = val.shape[0], col = 1)
            val_dict[name] = val
        expr = expr @ mat 
        node_local.expr = expr

        return expr, val_dict
    pass

class NodesSub():
    def __init__(self):
        pass

    def apply(a, v):
        node1 = a.operator[0]
        node2 = a.operator[1]

        ans_v = len(a.ancestors)
        if ans_v == 0:
            raise ValueError('Node sum needs ancestors')
        # ic('NodeSum')
        # ic(node1.value)
        # ic(node2.value)

        node1.val_use = node1.val_use + 1
        node2.val_use = node2.val_use + 1

        # if node1.val_use >= len(node1.descendents):
        #     node1.value = None
        # if node2.val_use >= len(node2.descendents):
        #     node2.value = None

        return node1.value - node2.value
    
    def apply_linear(a, v):
        node1 = a.operator[0]
        node2 = a.operator[1]

        ans_v = len(a.ancestors)
        if ans_v == 0:
            raise ValueError('Node sum needs ancestors')
        # # ic('NodeSum')
        # ic('################################################################')
        # ic(node1)
        # ic(node2)
        # ic(type(node1.value))
        # ic(node1.tag)
        # ic(type(node2.value))

        # ic(node2.value)
        # ic(node1.value)

        node1.val_use = node1.val_use + 1
        node2.val_use = node2.val_use + 1

        return node1.value - node2.value
    
    #done
    def lapply_linear(a, graph):
        # node1 = a.operator[0]
        # node2 = a.operator[1]
        # ic(node1.tag)
        # ic(node1.tag, node1.value)
        # ic(node2.tag, node2.value)

        # ans_v = len(list(graph.predecessors(a)))
        # if ans_v < 2:
        #     raise ValueError('Node sum needs two descendents')
        # # ic('NodeSum')
        # # ic(node1.value)
        # # ic(node2.value)

        # node1.val_use = node1.val_use + 1
        # node2.val_use = node2.val_use + 1

        # return node1.value - node2.value
        val_here = a.value
        node1 = a.operator[0]
        node2 = a.operator[1]
        # node_list = [a.operator[0], a.operator[1]]
        # for node_local in node_list:
        #     ic(node_local.tag)
        #     ic(node_local.value)
        #     populate_node_val(node_local, val_here)
        populate_node_val(node1, val_here)
        populate_node_val(node2, -val_here)

        pass
    
    
    
    def build_expr(node_local, expr, val_dict, Adim):
        expr1 = node_local.operator[0].expr
        expr2 = node_local.operator[1].expr

        expr = expr1 - expr2
        node_local.expr = expr

        return expr, val_dict
    pass

class RNodesSub():
    def __init__(self):
        pass

    def apply(a, v):
        node1 = a.operator[0]
        node2 = a.operator[1]

        ans_v = len(a.ancestors)
        if ans_v == 0:
            raise ValueError('Node sum needs ancestors')
        # ic('NodeSum')
        # ic(node1.value)
        # ic(node2.value)

        node1.val_use = node1.val_use + 1
        node2.val_use = node2.val_use + 1

        # if node1.val_use >= len(node1.descendents):
        #     node1.value = None
        # if node2.val_use >= len(node2.descendents):
        #     node2.value = None

        return node2.value - node1.value
    
    def apply_linear(a, v):
        node1 = a.operator[0]
        node2 = a.operator[1]

        ans_v = len(a.ancestors)
        if ans_v == 0:
            raise ValueError('Node sum needs ancestors')
        # ic('NodeSum')
        # ic(node1.value)
        # ic(node2.value)

        node1.val_use = node1.val_use + 1
        node2.val_use = node2.val_use + 1

        return node2.value - node1.value
    
    #done here
    def lapply_linear(a, graph):
        # node1 = a.operator[0]
        # node2 = a.operator[1]
        

        # ns_v = len(list(graph.predecessors(a)))
        # if ans_v < 2:
        #     raise ValueError('Node sum needs two descendents')
        # # ic('NodeSum')
        # # ic(node1.value)
        # # ic(node2.value)

        # node1.val_use = node1.val_use + 1
        # node2.val_use = node2.val_use + 1

        # return node2.value - node1.value
        val_here = a.value
        node1 = a.operator[0]
        node2 = a.operator[1]
        # node_list = [a.operator[0], a.operator[1]]
        # for node_local in node_list:
        #     ic(node_local.tag)
        #     ic(node_local.value)
        #     populate_node_val(node_local, val_here)
        populate_node_val(node1, -val_here)
        populate_node_val(node2, val_here)

        pass
    

    def build_expr(node_local, expr, val_dict, Adim):
        expr1 = node_local.operator[0].expr
        expr2 = node_local.operator[1].expr

        expr = expr2 - expr1
        node_local.expr = expr

        return expr, val_dict
    pass

class RShift():
    def __init__(self):
        pass

    def apply(a, v):
        # ans_v = len(a.ancestors)
        # ic(ans_v)
        # ic(a.operator)
        # ic('RShift - check this')
        # ic(a.operator)
        # ic(a.ancestors[0].value)
        # ic(a.operator + a.ancestors[0].value)
        a.ancestors[0].val_use = a.ancestors[0].val_use + 1
        # if a.ancestors[0].val_use >= len(a.ancestors[0].descendents):
        #     a.ancestors[0].value = None
        return a.operator - a.ancestors[0].value
    
    def apply_linear(a, v):
        a.ancestors[0].val_use = a.ancestors[0].val_use + 1
        return - a.ancestors[0].value
    
    def lapply_linear(a, v):
        a.ancestors[0].val_use = a.ancestors[0].val_use + 1
        return - a.ancestors[0].value
    
    #done here
    def lapply_linear(a, graph):
        # next(graph.predecessors(a)).val_use = next(graph.predecessors(a)).val_use + 1
        # return - next(graph.predecessors(a)).value
        val_here = -a.value 
        populate_node_val(next(graph.predecessors(a)), val_here)
        pass
    
    def build_expr(node_local, expr, val_dict, Adim):
        if isinstance(node_local.operator, A_mat):
            mat = Matrix.sym('Amat', row = Adim, col = Adim)
        else:
            val = node_local.operator
            name = str(node_local.tag)
            # mat = Matrix.named(name, row = val.shape[0], col = val.shape[1])
            try:
                mat = Matrix.named(name, row = val.shape[0], col = val.shape[1])
            except:
                mat = Matrix.named(name, row = val.shape[0], col = 1)
            val_dict[name] = val
        # expr = mat - expr
        expr = - expr
        node_local.expr = expr

        return expr, val_dict
    pass

class Solve():
    def __init__(self):
        pass

    def apply(a, v):
        a.ancestors[0].val_use = a.ancestors[0].val_use + 1
        # if a.ancestors[0].val_use >= len(a.ancestors[0].descendents):
        #     a.ancestors[0].value = None
        return np.linalg.solve(a.operator, a.ancestors[0].value)
    
    def apply_linear(a, v):
        a.ancestors[0].val_use = a.ancestors[0].val_use + 1
        return np.linalg.solve(a.operator, a.ancestors[0].value)
    
    #done
    def lapply_linear(a, graph):
        # a.descendents[0].val_use = a.descendents[0].val_use + 1
        # return np.linalg.solve(a.operator.T, a.ancestors[0].value.T).T
        # next(graph.predecessors(a)).val_use = next(graph.predecessors(a)).val_use + 1
        # # return a.operator @ next(graph.predecessors(a)).value
        # return np.linalg.solve(a.operator.T, next(graph.predecessors(a)).value.T).T
        val_here = np.linalg.solve(a.operator.T, a.value.T).T
        populate_node_val(next(graph.predecessors(a)), val_here)
        pass


    def build_expr(node_local, expr, val_dict, Adim):
        expr = node_local.ancestors[0].expr
        # ic('-----------------------------from ProbMG file------------------------------')
        # ic(node_local.operator)
        if isinstance(node_local.operator, A_mat):
            # ic('-----------------------------A_inv_op------------------------------')
            mat = Matrix.sym('Amat', row = Adim, col = Adim)
            expr = mat.A_inverse() @ expr 
        else:
            val = node_local.operator
            name = str(node_local.tag)
            # mat = Matrix.named(name, row = val.shape[0], col = val.shape[1])
            try:
                mat = Matrix.named(name, row = val.shape[0], col = val.shape[1])
            except:
                mat = Matrix.named(name, row = val.shape[0], col = 1)
            val_dict[name] = val
            expr = mat.inverse() @ expr 
            # ic(name)
        node_local.expr = expr

        return expr, val_dict

    pass

class TriSolveL():
    def __init__(self):
        pass

    def apply(a, v):
        a.ancestors[0].val_use = a.ancestors[0].val_use + 1
        # if a.ancestors[0].val_use >= len(a.ancestors[0].descendents):
        #     a.ancestors[0].value = None
        return scipy.linalg.solve_triangular(a.operator, a.ancestors[0].value,lower=True)
    
    def apply_linear(a, v):
        a.ancestors[0].val_use = a.ancestors[0].val_use + 1
        return scipy.linalg.solve_triangular(a.operator, a.ancestors[0].value,lower=True)

    #done as well
    def lapply_linear(a, graph):
        val_here = scipy.linalg.solve_triangular(a.operator.T, a.value.T, lower=False).T
        populate_node_val(next(graph.predecessors(a)), val_here)
        pass

    # ---------------------------------------------change this?--------------------------------------------------------
    def build_expr(node_local, expr, val_dict, Adim):
        expr = node_local.ancestors[0].expr
        # ic('-----------------------------from ProbMG file------------------------------')
        # ic(node_local.operator)
        if isinstance(node_local.operator, A_mat):
            # ic('-----------------------------A_inv_op------------------------------')
            mat = Matrix.sym('Amat', row = Adim, col = Adim)
            expr = mat.A_inverse() @ expr 
        else:
            val = node_local.operator
            name = str(node_local.tag)
            # mat = Matrix.named(name)
            try:
                mat = Matrix.named(name, row = val.shape[0], col = val.shape[1])
            except:
                mat = Matrix.named(name, row = val.shape[0], col = 1)
            val_dict[name] = val
            # ic(name)
            expr = mat.ltrisolve() @ expr 
        node_local.expr = expr

        return expr, val_dict

    pass

class Split:
    def __init__(self):
        pass

    def apply(a, v):
        ic('Not Implemented')
        pass

    def apply_linear(a, v):
        ic('Not Implemented')
        pass

    # check this!! - done now
    def lapply_linear(a, graph, v):
        val_here = scipy.linalg.solve_triangular(a.operator.T, a.value.T, lower=False).T
        populate_node_val(next(graph.predecessors(a)), val_here)
        raise NotImplementedError('Split operation is not implemented yet - This node should not exist')

    def build_expr(node_local, expr, val_dict, Adim):
        ic('Not Implemented')
        pass


class A_mat():
    __array_priority__ = 999

    def __init__(self, A):
        self.A = A
        pass

    @dispatch
    def __matmul__(self, B: np.ndarray):
        # ic(B)
        # ic('Aop - mult')
        return self.A @ B
    
    # @dispatch
    # def __matmul__(self, B: tape):
    #     return NotImplemented
    
    @dispatch
    def __matmul__(self, B: node):
        return NotImplemented
    
    @dispatch
    def __matmul__(self, B: A_inv):
        return NotImplemented
    
    @dispatch
    def __matmul__(self, B: downdate):
        return NotImplemented
    
    @dispatch
    def __rmatmul__(self, B: np.ndarray):
        return B @ self.A
    
    # @dispatch
    # def __rmatmul__(self, B: tape):
    #     return NotImplemented
    
    @dispatch
    def __rmatmul__(self, B: node):
        return NotImplemented
    
    @dispatch
    def __rmatmul__(self, B: A_inv):
        return NotImplemented
    
    @dispatch
    def __rmatmul__(self, B: downdate):
        return NotImplemented
    
    # def __matmul__(self, B: scipy.sparse.lil_matrix):
    #     ic('Amat matml')
    #     return self.A @ B
    
    # def __rmatmul__(self, B: scipy.sparse.lil_matrix):
    #     ic('Amat matml')
    #     return B @ self.A 

    # def __tril__(self):

    # @dispatch
    # def __matmul__(self, B: np.ndarray):
    #     ic('change here')
    #     return self.A @ B
    
    # @dispatch
    # def __matmul__(self, B: tape):
    #     ic('change here? - tape')
    #     return self.A @ B
    
    # @dispatch
    # def __matmul__(self, B: A_mat):
    #     ic('change here - inv')
    #     return np.eye(self.A.shape[0])

class Id_mat():
    def __init__(self, d):
        self.d = d
        pass

class A_inv():
    __array_priority__ = 1001

    def __init__(self,A) -> None:
        self.A = A
        pass

    @dispatch
    def __matmul__(self, B: Id_mat):
        return A_inv

    @dispatch
    def __matmul__(self, A: A_mat):
        # tape?
        return np.eye(A.A.shape[0])
    
    @dispatch
    def __matmul__(self, B):
        # ic('A_inv mult - fix this')
        raise ValueError('Cant do this')

    @dispatch
    def __rmatmul__(self, B: Id_mat):
        # ic('should reach here')
        return A_inv

    @dispatch
    def __rmatmul__(self, A: A_mat):
        # tape?
        # ic('A @ Ainv')
        return np.eye(A.A.shape[0])
    
    @dispatch
    def __rmatmul__(self, B):
        # ic('A_inv mult - do something')
        # ic(B)
        raise ValueError('Cant do this')

    def __sub__(self, b):
        # ic('Ainv - sub')
        return downdate(self, b)
    
    def __add__(self, b):
        # ic('Ainv - add - check this')
        return downdate(self, -b)
    
    @property
    def T(self):
        return self

class downdate():
    def __init__(self, Ainv: A_inv, D: np.ndarray):
        self.Ainv = Ainv
        self.D = D

    def __add__(self, b):
        # ic(b)
        # ic('downdate - add - check signs')
        return downdate(self.Ainv, self.D - b)
    
    def __sub__(self, b):
        # ic(b)
        # ic('downdate - add - check signs')
        return downdate(self.Ainv, self.D + b)

    def __matmul__(self, A: A_mat):
        # ic('downdate - matmul')
        return np.eye(self.D.shape[0]) - (self.D @ A.A)
    
    def __rmatmul__(self, A: A_mat):
        # ic('downdate - matmul')
        return np.eye(self.D.shape[0]) - (A.A @ self.D)

    def transpose(self):
        return downdate(self.Ainv, self.D.T)
    
    @property
    def T(self):
        return downdate(self.Ainv, self.D.T)
