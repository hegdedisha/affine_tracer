import numpy as np
import scipy
from icecream import ic

def interpolator_nn_fn2(u_0, g_f, g_c, no = 4,  P = None):
    if P is None:
       P = interpolator_nn(g_f, g_c, no)
    # ic(P.shape)
    # ic(u_0.shape)
    u = P @ u_0
    return u

def restrictor_nn_fn2(u_0, g_f, g_c, no = 1, Sigma_l=None, R = None):
    if R is None:
        R = restrictor_nn(g_f, g_c, no)
    u = R @ u_0
    return u

# %%
# restrictor - nearest neighbour
# from a grid of fine points g_f to g_c
# grids - each row is a different point
def restrictor_nn(g_f, g_c, no = 1):
    # ic(g_c.shape)
    R = scipy.sparse.lil_matrix((g_c.shape[0], g_f.shape[0]))
    # ic(R.shape)
    # ic(g_f.shape)
    kdtree = scipy.spatial.KDTree(g_f)
    for i in range(g_c.shape[0]):
        # ic(g_c[i,:])
        # ic(no)
        dist , idx = kdtree.query(g_c[i,:], k= no)
        R[i, idx] = 1
    return R

def restrictor_nn_fn(u_0, Sigma_0, g_f, g_c, no = 1, Sigma_l=None, R = None):
    if R is None:
        R = restrictor_nn(g_f, g_c, no)
    u = R @ u_0
    if Sigma_l is None:
        Sigma = R @ Sigma_0 @ R.T
        return u, Sigma
    else:
       Sigma_l = R @ Sigma_l
       Sigma = R @ Sigma_0 @ R.T
       return u, Sigma, Sigma_l
    
# interpolator - nearest neighbour
# from a grid of coarse points g_c to g_f
# this does not work for no = 1
def interpolator_nn(g_f, g_c, no = 2):
    P = scipy.sparse.lil_matrix((g_f.shape[0], g_c.shape[0]))
    kdtree = scipy.spatial.KDTree(g_c)
    for i in range(g_f.shape[0]):
        dist, idx = kdtree.query(g_f[i,:], k = no)
        # ic(dist)
        # ic(dist == 0)
        if any(dist == 0):
            P[i, idx[dist==0]] = 1
        else:
            weights = (1/dist)/(np.sum(1/dist))
            P[i, idx] = weights
    return P


def interpolator_nn_fn(u_0, Sigma_0, g_f, g_c, no = 4, Sigma_l=None, P = None):
    if P is None:
       P = interpolator_nn(g_f, g_c, no)
    u = P @ u_0
    if Sigma_l is None:
        Sigma = P @ Sigma_0 @ P.T
        return u, Sigma
    else:
       Sigma_l = P @ Sigma_l
       Sigma = P @ Sigma_0 @ P.T
       return u, Sigma, Sigma_l

# %%
class multigrid_m_class:
    def __init__(self,grids,matrices,presmoother,postsmoother,interpolator,restrictor, interpolator_mat,restrictor_mat, exact_solve):
        self.grids = grids
        self.matrices = matrices
        self.presmoother = presmoother
        self.postsmoother = postsmoother
        self.restrictor = restrictor
        self.interpolator = interpolator
        self.exact_solve = exact_solve
        self.interpolator_mat = interpolator_mat
        self.restrictor_mat = restrictor_mat
        grids_len = len(grids)
        # ic(grids_len)
        self.P_mat = [None]*(grids_len-1)
        self.R_mat = [None]*(grids_len-1)
        # ic('----------------')
        # ic(self.P_mat[1])
        # ic(len(self.P_mat))
        for i in range(grids_len-1):
            # ic(i)
            g_f = grids[i]
            g_c = grids[i+1]
            self.P_mat[i] = self.interpolator_mat(g_f,g_c)
            self.R_mat[i] = self.restrictor_mat(g_f,g_c)
        # ic(self.P_mat[1])
        pass

    def v_cycle(self,grids,matrices,b, u_0, h, m_pres = 1, m_poss = 2, level = 0):
        # print(h)
        # ic(h)
        # ic('~~~~~~~~')
        
        # ic(self.P.shape)
        # ic(self.R.shape)
        # ic(u_0.shape)
        # ic(level)
        P = self.P_mat[level]
        R = self.R_mat[level]
        u = u_0
        A = matrices[0]
        # A2 = matrices[1]
        g_f = grids[0]
        g_c = grids[1]
        #presmoothing
        # ic(type(u))
        u = self.presmoother(A, b, u, m_max = m_pres)
        # u.eval = True
        # ic(type(u))
        # print(length_tape(u))
        # ic(type(u))
        # ic(u)
        #computing the residual
        r = b - (A@u)
        # ic(type(r))
        #restricting
        # self.P = self.interpolator_mat(g_f,g_c)
        # self.R = self.restrictor_mat(g_f,g_c)
        r2 = self.restrictor(r, g_f, g_c, R = R)
        # ic(type(r2))
        #exact solve in coarse grid
        if len(matrices) > 1:
            A2 = matrices[1]
        else:
            try:
                A2 = R @ A @ P
                matrices = [matrices[0], A2]
                # ic(matrices)
            except:
                A2 = R @ A.A @ P
                matrices = [matrices[0], A2] 
                # fix this ----------------------------------------------------------------------------------------------------------------------------------------------------------
        if h == 2:
            # ic(type(A2))
            # ic(type(r2))
            e2 = self.exact_solve(A2, r2)
        else:
            # ic(matrices[1].shape)
            # ic(r2.shape)
            e2 = self.v_cycle(grids[1:], matrices[1:], r2, np.zeros(matrices[1].shape[0]), h-1, m_pres=m_pres, m_poss = m_poss, level = level + 1)
        #interpolating
        # ic(type(e2))
        # ic(e2.shape)
        # ic(self.P.shape)
        e = self.interpolator(e2, g_f, g_c, P = P)
        # ic(type(e))
        # ic(e)
        # ic(e.tape)
        #updating the iterate
        # print(length_tape(e))
        # ic(u.eval)
        u = u + e
        # u.val = True
        # print(length_tape(u))
        # ic(type(u))
        # ic(u)
        #postsmoothing
        u = self.postsmoother(A, b, u, m_max = m_poss) 
        # print(length_tape(u))

        # ic(type(u))
        return u
    
    def iter_cycle(self, grids, matrices, b, u, h, m_max = 100, tol = 1e-6, m_pres = 1, m_poss = 2):
        A = matrices[0]
        self.reslist = np.zeros(m_max) + tol
        self.trace = np.zeros(m_max)
        # ic(u.Sigma.shape)
        # print(length_tape(u))
        for m in range(m_max):
            u = self.v_cycle(grids, matrices, b, u, h, m_pres = m_pres, m_poss = m_poss)
            # ic(type(u))

            # res = np.linalg.norm(A@u - b)
            # self.reslist[m] = res
            # if res < tol:
            #     break
            # ic(m)
            # print(type(u))
            # print(length_tape(u))
        self.m = m
        return u


class two_grid_class:
    def __init__(self,grids,matrices,presmoother,postsmoother,interpolator,restrictor, interpolator_mat,restrictor_mat, exact_solve):
        self.grids = grids
        self.matrices = matrices
        self.presmoother = presmoother
        self.postsmoother = postsmoother
        self.restrictor = restrictor
        self.interpolator = interpolator
        self.interpolator_mat = interpolator_mat
        self.restrictor_mat = restrictor_mat
        self.exact_solve = exact_solve
        pass

    def v_cycle(self,grids,matrices,b, u_0, Sigma_0, m_max = 100, tol = 1e-6, m_pres = 1, m_poss = 1):
        u = u_0
        Sigma = Sigma_0
        A = matrices[0]
        # A2 = matrices[1]
        g_f = grids[0]
        g_c = grids[1]
        P = self.interpolator_mat(g_f,g_c)
        R = self.restrictor_mat(g_f,g_c)
        self.reslist = np.zeros(m_max) + tol
        self.trace = np.zeros(m_max)
        # ic(g_c.shape)
        for m in range(m_max):
            #presmoothing
            # ic(u.shape)
            # ic(Sigma.shape)
            u, Sigma = self.presmoother(A, b, u, Sigma, m_max = m_pres)
            # np.linalg.cholesky(Sigma)
            # ic(np.linalg.norm(Sigma))
            # ic(u.shape)
            # ic(np.linalg.eigvalsh(Sigma))
            # ic(is_psd(Sigma))
            #computing the residual
            r = b - (A@u)
            # ic(np.linalg.norm(r))
            Sigma_r_l = A @ Sigma
            Sigma_r =  Sigma_r_l @ A.T
            # ic(np.linalg.norm(Sigma_r))
            # ic(r.shape)
            #restricting
            
            # P = R.T
            r2, Sigma_r2, Sigma_r2_l = self.restrictor(r, Sigma_r, g_f, g_c, Sigma_l=Sigma_r_l, R = R)
            # ic(np.linalg.norm(Sigma_r2))
            # ic(r2.shape)
            #exact solve in coarse grid
            # ic(A2.shape)
            # R = restrictor_nn(g_f, g_c)
            # P = interpolator_nn(g_f,g_c)
            if len(matrices) > 1:
                A2 = matrices[1]
            else:
                # ic('here?')
                A2 = R @ A @ P
                matrices = [matrices[0], A2]
            # e2, Sigma_e2, Sigma_e2_l = prob_exact_solve(A2, r2, Sigma_r2, Sigma_r2_l)
            # ic(np.linalg.norm(r2))
            e2, Sigma_e2, Sigma_e2_l = self.exact_solve(A2, r2, Sigma_r2, Sigma_r2_l)
            # ic(np.linalg.norm(Sigma_e2))
            # ic(np.linalg.norm(e2 - np.linalg.solve(A2,r2)))
            # ic(e2.shape)
            #interpolating
            e, Sigma_e, Sigma_e_l = self.interpolator(e2, Sigma_e2, g_f, g_c, Sigma_l=Sigma_e2_l, P = P)
            # ic(np.linalg.norm(Sigma_e))
            # ic(e.shape)
            #updating the iterate
            # ic(np.linalg.norm(Sigma_e_l))
            u, Sigma = u + e, Sigma + Sigma_e - Sigma_e_l - Sigma_e_l.T
            # ic(np.linalg.norm(Sigma))
            # ic(is_psd(Sigma))
            # np.linalg.cholesky(Sigma)
            # ic(np.linalg.norm(e))
            #postsmoothing
            u, Sigma = self.postsmoother(A, b, u, Sigma, m_max = m_poss)
            # ic(np.linalg.norm(Sigma))
            # ic(is_psd(Sigma))
            # np.linalg.cholesky(Sigma)
            # plt.plot(u)
            # ic(np.linalg.norm(A@u - b))
            res = np.linalg.norm(A@u - b)
            self.reslist[m] = res
            self.trace[m] = np.trace(Sigma)
            if res < tol:
                break
        self.m = m
        return u, Sigma