# import os
# set the number of threads for egglog
# os.environ.setdefault("RAYON_NUM_THREADS", "10")

from .utils import matker32, sq_exp, mat_gen_sq, mat_gen_mt, mat_gen_mt2, is_psd, is_psd_num, is_pd, mat_gen_fn
from .linear_solvers import gs, gs_explicit, triangular_solve, prob_gs, prob_exact_solve, exact_solve, get_mean, get_cov
from .multigrid import multigrid_m_class, two_grid_class, interpolator_nn_fn2, restrictor_nn_fn2, interpolator_nn, restrictor_nn, interpolator_nn_fn, restrictor_nn_fn

from .tracer import node, polytree, clear_node_value, apply_all, apply_linear_all, populate_node_val, Id, Shift, RShift, ScalarMultiply, Split, NodesSum, NodesSub, RNodesSub, MatMultiply, RMatMultiply, Solve, TriSolveL, A_mat, A_inv, Id_mat, downdate

from .tracer_inv import lapply_linear_all, apply_node, graph_reset_nx, clear_node_value_nx, add_extranode, to_nX, add_extranode_nX, func_VD_v2, func_DV_v2, func_VG_v2, func_VSM_v2, func_VG_VSM_v2
from .inv_egglog import Matrix, get_DV_expr, get_VD_expr, eval_expr, apply_fun, tracer_to_egraph

from .tracer_to_cagp import func_VD, func_DV, func_VG, func_VSM, func_VG_VSM, compiled_sis, compiled_sis_v2
from .cagp import CAGP


__all__ = [
    # utils
    "matker32", "sq_exp", "mat_gen_sq", "mat_gen_mt", "mat_gen_mt2",
    "is_psd", "is_psd_num", "is_pd", "mat_gen_fn",
    # multigrid
    "multigrid_m_class", "two_grid_class",
    "interpolator_nn", "interpolator_nn_fn", "interpolator_nn_fn2",
    "restrictor_nn", "restrictor_nn_fn", "restrictor_nn_fn2",
    # tracer
    "node", "polytree", "clear_node_value", "apply_all", "apply_linear_all",
    "populate_node_val", "Id", "Shift", "RShift", "ScalarMultiply", "Split",
    "NodesSum", "NodesSub", "RNodesSub", "MatMultiply", "RMatMultiply",
    "Solve", "TriSolveL", "A_mat", "A_inv", "Id_mat", "downdate",
    # solvers
    "gs", "gs_explicit", "triangular_solve", "prob_gs", "prob_exact_solve", "exact_solve", "get_mean", "get_cov",
    # tracer_inv
    "lapply_linear_all", "apply_node", "graph_reset_nx", "clear_node_value_nx", "add_extranode", "to_nX", "add_extranode_nX", "func_VD_v2", "func_DV_v2", "func_VG_v2", "func_VSM_v2", "func_VG_VSM_v2",
    # egraph
    "Matrix", "tracer_to_egraph", "get_VD_expr", "get_DV_expr", "eval_expr", "apply_fun",
    # sis
    "func_VD", "func_DV", "func_VSM", "func_VG", "func_VG_VSM",
    "compiled_sis", "compiled_sis_v2",
    # gp
    "CAGP", 
]