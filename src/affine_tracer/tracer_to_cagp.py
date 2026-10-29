import numpy as np
from icecream import ic

from .inv_egglog import eval_expr
from .tracer import apply_linear_all
from .tracer_inv import func_VD_v2, func_DV_v2, func_VG_v2, func_VSM_v2, func_VG_VSM_v2

def func_VD(V, ex_VD, val_dict):
    val_dict['V'] = V
    egg_DV = eval_expr(ex_VD, val_dict, cache_dict= None)
    return egg_DV

def func_DV(V, ex_DV, val_dict):
    val_dict['V'] = V
    egg_DV = eval_expr(ex_DV, val_dict, cache_dict= None)
    return egg_DV

def func_VSM(V, ex_DV, ex_VD, graph, val_dict):
    val_dict['V'] = V
    tr1 = func_DV(V, ex_DV, val_dict).T
    tr_int = func_VD(V, ex_VD, val_dict).T
    tr2 = apply_linear_all(graph, tr_int)
    return tr1 + tr2.T

def func_VG(V, A, ex_VD, val_dict):
    egg_VG = V - (func_VD(V , ex_VD, val_dict) @ A)
    return egg_VG

def func_VG_VSM(V, A, ex_VD, ex_DV, graph, val_dict):
    val_dict['V'] = V
    common_term = func_VD(V , ex_VD, val_dict)
    egg_VG = V - (common_term @ A)
    tr1 = func_DV(V, ex_DV, val_dict).T
    tr_int = common_term.T
    tr2 = apply_linear_all(graph, tr_int)
    egg_VSM = tr1 + tr2.T
    return egg_VG, egg_VSM

class compiled_sis():
    def __init__(self, tracer, ex_VD, ex_DV, val_dict):
        
        self.tracer = tracer
        self.ex_VD = ex_VD
        self.ex_DV = ex_DV
        self.val_dict = val_dict
        self.A = val_dict['Amat']
        
    def func_VG(self, V):
        # ------------use transpose-------------------
        # ic(V.T.shape)
        val = func_VG(V, self.A, self.ex_VD, self.val_dict)    
        return val

    def func_VSM(self, V):
        # ----------------use transpose----------------------
        # ic(V.T.shape)
        val = func_VSM(V, self.ex_DV, self.ex_VD, self.tracer, self.val_dict)
        return val
    
    def func_VG_VSM(self, V):
        val_VG, val_VSM = func_VG_VSM(V, self.A, self.ex_VD, self.ex_DV, self.tracer, self.val_dict)
        return val_VG, val_VSM
    

class compiled_sis_v2():
    def __init__(self, A, tracer_G, tracer_M, tracer_M_nX):
        
        self.A = A
        self.tracer = tracer_G
        self.tracer_M = tracer_M
        self.tracer_M_nX = tracer_M_nX

    def func_VG(self, V):
        # ------------use transpose-------------------
        # ic(V.T.shape)
        # val = func_VG(V, self.A, self.ex_VD, self.val_dict)
        # val = lapply_all(self.tracer, V)    
        # raise NotImplementedError("func_VG is not implemented in compiled_sis_v2")
        val = func_VG_v2(V, self.A, self.tracer_M_nX)
        return val
    

    def func_VSM(self, V):
        # ----------------use transpose----------------------
        # ic(V.T.shape)
        val = func_VSM_v2(V, self.tracer, self.tracer_M, self.tracer_M_nX)
        return val
    
    def func_VG_VSM(self, V):
        val_VG, val_VSM = func_VG_VSM_v2(V, self.A, self.tracer, self.tracer_M, self.tracer_M_nX)
        return val_VG, val_VSM