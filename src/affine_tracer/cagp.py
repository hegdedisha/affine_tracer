import numpy as np
import scipy
from icecream import ic
import time

from .utils import matker32
from .tracer import A_mat, A_inv, polytree, apply_all, apply_linear_all
from .linear_solvers import gs, gs_explicit, exact_solve
from .multigrid import multigrid_m_class, interpolator_nn_fn2, restrictor_nn_fn2, interpolator_nn, restrictor_nn

class CAGP:
    def __init__(self, Xtrain, ytrain, sigma2, Xtest, l, sig_ker2 = 1,  m_0tr = None, m_0ts = None, ytest = None):
        ic('init')
        self.Xtrain = Xtrain
        self.ytrain = ytrain
        self.Xtrdim = Xtrain.shape[0]
        self.Xtest = Xtest
        self.Xtsdim = Xtest.shape[0]

        self.m_0tr = m_0tr
        self.m_0ts = m_0ts
        if m_0tr is None:
            self.m_0tr = np.zeros(self.Xtrdim)
        if m_0ts is None:
            self.m_0ts = np.zeros(self.Xtsdim)

        self.sigma2 = sigma2
        self.l = l
        self.sig_ker2 = sig_ker2
        self.comp_vec = ytest
        self.ytest = ytest

        self.b = ytrain - self.m_0tr

        self.V = matker32(self.Xtrain, self.Xtest, self.l, self.sig_ker2).T 
        self.G = matker32( self.Xtrain, self.Xtrain, self.l, self.sig_ker2) + (sigma2*np.eye(self.Xtrdim))
        self.CXtestXest = matker32(self.Xtest, self.Xtest, self.l, self.sig_ker2)

        if self.comp_vec is None:
            self.actual_values = self.V.T @ np.linalg.solve(self.G,self.b)
        else:
            self.actual_values = self.comp_vec

        pass
    
    def PLS_GS(self, m):
        self.times_gs = np.zeros(m+1)
        ts = time.time()
        self.m_list_gs = np.zeros((m+1, self.Xtsdim))
        self.kdiag_list_gs = np.zeros((m+1, self.Xtsdim))
        L = np.tril(self.G)
        U = np.triu(self.G, 1)
        D = np.diag(self.G)
        sqD = np.sqrt(D)[:,None]
        Z = scipy.linalg.solve_triangular(L.T, self.V ,lower=False,check_finite=False)
        f = scipy.linalg.solve_triangular(L,self.b,lower=True,check_finite=False)
        M = sqD * Z
        self.VDmV = M.T @ M
        self.xm = np.zeros(self.Xtrdim)
        self.vm = self.V.T @ self.xm
        self.m = self.m_0ts + self.vm
        self.k =  self.CXtestXest 
        self.rmse_gs = np.zeros(m+1)
        self.nll_gs = np.zeros(m+1)
        self.rmse_gs[0] = np.linalg.norm(self.m - self.actual_values)
        self.nll_gs[0] = sum(np.divide((self.m - self.actual_values)**2,2*(np.diag(self.k)+ self.sigma2))) + sum(np.log(2*np.pi*(np.diag(self.k)+ self.sigma2))/2)
        self.m_list_gs[0] = self.m
        self.kdiag_list_gs[0] = np.diag(self.k)
        self.times_gs[0] = time.time() - ts
        for i in range(m):
            ic(i)
            self.k =  self.CXtestXest - self.VDmV
            Z = scipy.linalg.solve_triangular(L.T, U.T @ Z ,lower=False,check_finite=False) 
            self.xm = -scipy.linalg.solve_triangular(L, U @ self.xm ,lower=True,check_finite=False) + f
            M = sqD * Z
            self.VDmV = self.VDmV + (M.T @ M)
            self.vm = self.V.T @ self.xm
            self.m = self.m_0ts + self.vm
            self.rmse_gs[i+1] = np.linalg.norm(self.m - self.actual_values)
            self.nll_gs[i+1] = sum(np.divide((self.m - self.actual_values)**2,2*(np.diag(self.k)+ self.sigma2))) + sum(np.log(2*np.pi*(np.diag(self.k)+ self.sigma2))/2)
            self.m_list_gs[i+1] = self.m
            self.kdiag_list_gs[i+1] = np.diag(self.k)
            self.times_gs[i+1] = time.time() - ts

        return self.m, self.k

    def PLS_CG(self, m, P = None):
        self.times_cg = np.zeros(m+1)
        ts = time.time()
        self.m_list_cg = np.zeros((m+1, self.Xtsdim))
        self.kdiag_list_cg = np.zeros((m+1, self.Xtsdim))
        if P is None:
            P = np.eye(self.Xtrdim)
        xm = np.zeros(self.Xtrdim)
        self.Dcg = np.eye(self.Xtrdim) - np.eye(self.Xtrdim)
        self.mcg = self.m_0ts + self.V.T @ xm 
        self.C_cg = self.CXtestXest - (self.V.T @ self.Dcg @ self.V)
        self.rmse_cg = np.zeros(m+1)
        self.nll_cg = np.zeros(m+1)
        self.rmse_cg[0] = np.linalg.norm(self.mcg - self.actual_values)
        self.nll_cg[0] = sum(np.divide((self.mcg - self.actual_values)**2,2*(np.diag(self.C_cg)+self.sigma2))) + sum(np.log(2*np.pi*(np.diag(self.C_cg)+self.sigma2))/2)
        self.Dcg = np.eye(self.Xtrdim) - np.eye(self.Xtrdim)
        self.m_list_cg[0] = self.mcg
        self.kdiag_list_cg[0] = np.diag(self.C_cg)
        self.times_cg[0] = time.time() - ts
        for i in range(m):
            ic(i)
            r = self.b - (self.G @ xm)
            s = P @ r
            alpha = np.dot(s,r)
            d = s - self.Dcg @ (self.G @ s)
            eta = np.dot(s, self.G @ d)
            self.Dcg = self.Dcg + ((1 / eta) * np.outer(d, d))
            xm = xm + (alpha / eta) * d
            self.mcg = self.m_0ts + self.V.T @ xm 
            self.C_cg = self.CXtestXest - (self.V.T @ self.Dcg @ self.V)
            self.rmse_cg[i+1] = np.linalg.norm((self.mcg) - self.actual_values)
            self.nll_cg[i+1] = sum(np.divide((self.mcg - self.actual_values)**2,2*(np.diag(self.C_cg)+self.sigma2))) + sum(np.log(2*np.pi*(np.diag(self.C_cg)+self.sigma2))/2)
            self.m_list_cg[i+1] = self.mcg
            self.kdiag_list_cg[i+1] = np.diag(self.C_cg)
            self.times_cg[i+1] = time.time() - ts
        return self.mcg, self.C_cg
    
    def PLS_SIS(self, m, compiled_sis):
        self.times_sis = np.zeros(m+1)
        ts = time.time()
        self.m_list_sis = np.zeros((m+1, self.Xtsdim))
        self.kdiag_list_sis = np.zeros((m+1, self.Xtsdim))  
        self.xmg = np.zeros(self.Xtrdim)
        self.mmg = self.m_0ts + (self.V.T @ self.xmg)
        self.VDmgVt = 0
        self.C_mg = self.CXtestXest
        self.VG = compiled_sis.func_VG(self.V.T)
        self.rmse_mg = np.zeros(m+1)
        self.nll_mg = np.zeros(m+1)
        self.VDVt = np.zeros(m+1)
        self.VDVt[0] = np.linalg.norm(self.VDmgVt)
        self.rmse_mg[0] = np.linalg.norm(self.mmg - self.actual_values)
        self.nll_mg[0] = sum(np.divide((self.mmg - self.actual_values)**2,2*(np.diag(self.C_mg)+ self.sigma2))) + sum(np.log(2*np.pi*(np.diag(self.C_mg)+ self.sigma2))/2)
        self.m_list_sis[0] = self.mmg
        self.kdiag_list_sis[0] = np.diag(self.C_mg)
        self.times_sis[0] = time.time() - ts
        self.VDmgVt = compiled_sis.func_VSM(self.V.T) @ self.V 
        for i in range(m):  
            ic(i)
            self.xmg = apply_all(compiled_sis.tracer, self.xmg)
            self.mmg = self.m_0ts + (self.V.T @ self.xmg)
            self.C_mg =  self.CXtestXest - self.VDmgVt
            self.rmse_mg[i+1] = np.linalg.norm(self.mmg - self.actual_values)
            self.nll_mg[i+1] = sum(np.divide((self.mmg - self.actual_values)**2,2*(np.diag(self.C_mg)+ self.sigma2))) + sum(np.log(2*np.pi*(np.diag(self.C_mg)+ self.sigma2))/2)    
            self.m_list_sis[i+1] = self.mmg
            self.kdiag_list_sis[i+1] = np.diag(self.C_mg)
            self.times_sis[i+1] = time.time() - ts
            if i != m-1:
                new_VG, tr2 = compiled_sis.func_VG_VSM(self.VG)
                self.VDmgVt = self.VDmgVt + (tr2 @ self.VG.T)
                self.VDVt[i+1] = np.linalg.norm(self.VDmgVt - self.VDVt[i])
                self.VG = new_VG
        return self.mmg, self.C_mg

    def full_post(self):
        self.mgp = self.m_0ts + self.V.T @ np.linalg.solve(self.G,self.b)
        self.kgp = self.CXtestXest - (self.V.T @ np.linalg.inv(self.G) @ self.V)
        self.rmse_full = np.linalg.norm(self.mgp - self.actual_values)
        self.nll_full = sum(np.divide((self.mgp - self.actual_values)**2,2*(np.diag(self.kgp)+ self.sigma2))) + sum(np.log(2*np.pi*(np.diag(self.kgp)+ self.sigma2))/2)
        return self.mgp, self.kgp


