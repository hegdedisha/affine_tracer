import numpy as np
import scipy
from plum import dispatch
from icecream import ic

from .tracer import A_mat, node, TriSolveL, Solve, polytree, apply_all, apply_linear_all

# check if this version of gs is actually correct
@dispatch
def gs(A: A_mat, b:np.ndarray, u_0, m_max = 100, tol = 1e-6):
    # print('gs1')
    # M = -scipy.linalg.solve_triangular(np.tril(A),np.triu(A,k=1),lower=True)
    # M = -scipy.linalg.solve_triangular(np.tril(A),np.triu(A,k=1),lower=True)
    # M = M.astype(np.float64)
    # ic(np.tril(A).shape)
    # ic(b.shape)
    # ic('A_mat gs')
    Nb = scipy.linalg.solve_triangular(np.tril(A.A),b,lower=True)
    u = u_0
    # print(length_tape(u))
    # -------------------------------------------------------is this correct??------------------------------------------
    trilAinv = np.linalg.inv(np.tril(A.A))
    for i in range(m_max):
        # ic(type(u))
        # ic(type(M))
        # ic(A @ u)
        # ic(np.linalg.inv(np.tril(A.A)).shape)
        # ic(np.linalg.inv(np.tril(A.A)) @ A)
        # ic(A.shape)
        u = u - (trilAinv @ (A @ u)) + (Nb)
        # u = (M @ u) + (Nb)
    # print(length_tape(u))
    return u

@dispatch
def gs(A: np.ndarray, b:np.ndarray, u_0, m_max = 100, tol = 1e-6):
    # print('gs2')
    M = -scipy.linalg.solve_triangular(np.tril(A),np.triu(A,k=1),lower=True)
    # M = -scipy.linalg.solve_triangular(np.tril(A),np.triu(A,k=1),lower=True)
    # M = M.astype(np.float64)
    # ic(np.tril(A).shape)
    # ic(b.shape)
    Nb = scipy.linalg.solve_triangular(np.tril(A),b,lower=True)
    u = u_0
    # print(length_tape(u))
    for i in range(m_max):
        # ic(type(u))
        # ic(type(M))
        # ic(A @ u)
        # ic(np.linalg.inv(np.tril(A.A)).shape)
        # ic(np.linalg.inv(np.tril(A.A)) @ A)
        # ic(A.shape)
        # u = u - (np.linalg.inv(np.tril(A)) @ (A @ u)) + (Nb)
        u = (M @ u) + (Nb)
    # print(length_tape(u))

    return u


@dispatch
def gs(A: A_mat, b:node, u_0, m_max = 100, tol = 1e-6):
    # ic('---------------------gs4-2----------------------------------------')
    # M = -scipy.linalg.solve_triangular(np.tril(A),np.triu(A,k=1),lower=True)
    # M = M.astype(np.float64)
    # ic(np.tril(A).shape)
    # ic(b.shape)
    #add a tape operation here
    Nb = triangular_solve(np.tril(A.A), b, lower = 'True')
    # print(length_tape(Nb))
    # Nb = scipy.linalg.solve_triangular(np.tril(A),b,lower=True)
    u = u_0
    for i in range(m_max):
        # ic(type(u))
        # ic(type(M))
        # u = (M @ u) + (Nb)
        u = u - (np.linalg.inv(np.tril(A.A)) @ (A @ u)) + (Nb)
        # print(length_tape(u))
    return u

@dispatch
def gs(A: np.ndarray, b:node, u_0, m_max = 100, tol = 1e-6):
    ic('---------------------gs4----------------------------------------')
    # M = -scipy.linalg.solve_triangular(np.tril(A),np.triu(A,k=1),lower=True)
    # M = M.astype(np.float64)
    # ic(np.tril(A).shape)
    # ic(b.shape)
    #add a tape operation here
    Nb = triangular_solve(np.tril(A), b, lower = 'True')
    # print(length_tape(Nb))
    # Nb = scipy.linalg.solve_triangular(np.tril(A),b,lower=True)
    u = u_0
    for i in range(m_max):
        # ic(type(u))
        # ic(type(M))
        # u = (M @ u) + (Nb)
        u = u - (np.linalg.inv(np.tril(A)) @ (A @ u)) + (Nb)
        # print(length_tape(u))
    return u

@dispatch
def gs_explicit(A: A_mat, b:np.ndarray, u_0, m_max = 1, tol = 1e-6):
    Nb = scipy.linalg.solve_triangular(np.tril(A.A),b,lower=True)
    u = u_0
    tril = np.tril(A.A)
    for i in range(m_max):
        u = u - (triangular_solve(tril, (A @ u))) + (Nb)
    return u

@dispatch
def gs_explicit(A: np.ndarray, b:np.ndarray, u_0, m_max = 1, tol = 1e-6):
    Nb = scipy.linalg.solve_triangular(np.tril(A),b,lower=True)
    u = u_0
    tril = np.tril(A)
    for i in range(m_max):
        u = u - (triangular_solve(tril, (A @ u))) + (Nb)
    return u

@dispatch
def gs_explicit(A: A_mat, b:node, u_0, m_max = 1, tol = 1e-6):
    
    u = u_0
    tril = np.tril(A.A)
    for i in range(m_max):
        if i == 0: 
            Nb = triangular_solve(np.tril(A.A), b, lower = 'True')
        u = u - (triangular_solve(tril, (A @ u))) + (Nb)
    return u

@dispatch
def gs_explicit(A: np.ndarray, b:node, u_0, m_max = 1, tol = 1e-6):
    u = u_0
    tril = np.tril(A)
    for i in range(m_max):
        if i == 0:
            Nb = triangular_solve(np.tril(A), b, lower = 'True')
        u = u - (triangular_solve(tril, (A @ u))) + (Nb)
    return u

@dispatch
def gs_explicit(A: A_mat, b:node, u_0: node, m_max = 1, tol = 1e-6):
    u = u_0
    tril = np.tril(A.A)
    for i in range(m_max):
        if i == 0:
            Nb = triangular_solve(np.tril(A.A), b, lower = 'True')
        u = u - (triangular_solve(tril, (A @ u))) + (Nb)
    # raise TypeError('gs_explicit with node u_0 not implemented yet')
    return u

@dispatch
def gs_explicit(A: np.ndarray, b:node, u_0: node, m_max = 1, tol = 1e-6):
    u = u_0
    tril = np.tril(A)
    for i in range(m_max):
        if i == 0:
            Nb = triangular_solve(np.tril(A), b, lower = 'True')
        u = u - (triangular_solve(tril, (A @ u))) + (Nb)
    # raise TypeError('gs_explicit with node u_0 not implemented yet')
    return u

@dispatch
def triangular_solve(A:A_mat, b: node, lower = 'True'):
    # ic('wrong place')
    new_node = node(A, TriSolveL, ancestors= [b])
    # ic('scmul')
    b.parent_tree.add_node(new_node)
    b.descendents = b.descendents + [new_node]
    return new_node

@dispatch
def triangular_solve(A:np.ndarray, b: node, lower = 'True'):
    # ic('not wrong place')

    # ic(type(A))
    # ic(type(b))
    new_node = node(A, TriSolveL, ancestors= [b])
    # ic('scmul')
    
    b.parent_tree.add_node(new_node)
    b.descendents = b.descendents + [new_node]
    return new_node

    # new_node = node(A, Solve, ancestors= [b])
    # # ic('scmul')
    # b.parent_tree.add_node(new_node)
    # b.descendents = b.descendents + [new_node]
    # return new_node

@dispatch
def triangular_solve(A:np.ndarray, b: np.ndarray, lower = 'True'):
    return scipy.linalg.solve_triangular(A, b, lower = lower)


#prob_gs
def prob_gs(A, b, u_0, Sigma_0, m_max = 100, tol = 1e-6):
    # ic(np.linalg.matrix_rank(np.tril(A))) 
    # ic(np.linalg.matrix_rank(np.triu(A,k=1))) 
    A = A.astype(np.float64)
    M = -scipy.linalg.solve_triangular(np.tril(A),np.triu(A,k=1),lower=True)
    M = M.astype(np.float64)
    # eigvals, eigvecs = np.linalg.eigh(M)
    # eigvals_clipped = np.clip(eigvals, 0, None)
    # M = eigvecs @ np.diag(eigvals_clipped) @ eigvecs.T
    Nb = scipy.linalg.solve_triangular(np.tril(A),b,lower=True)
    u = u_0
    Sigma = Sigma_0
    for i in range(m_max):
        # ic(type(u))
        # ic(type(M))
        u = (M @ u) + (Nb)        
        # ic(np.linalg.norm(u))
        # ic(is_psd(Sigma))
        # ic(is_pd(Sigma))
        Sigma = M @ (Sigma @ M.T)
        # plt.semilogy(np.linalg.eigvals(M))
        # plt.show()
        # ic(np.linalg.matrix_rank(M)) 
        # ic(is_psd(Sigma))
        # ic(np.linalg.eigvals(M))
        # np.linalg.cholesky(M)
        # np.linalg.cholesky(Sigma)
        # ic(i)
        # ic(np.linalg.norm(A@u - b))
        # ic(np.trace(Sigma))
        # ic(np.linalg.norm(Nb))
    return u, Sigma

def prob_exact_solve(A,b_0,Sigma_b0, Sigma_b0_l):
    e = np.linalg.solve(A,b_0)
    # ic(np.linalg.norm(e))
    # ic(np.linalg.norm(b_0))
    # ic(np.linalg.norm(A))
    B = np.linalg.solve(A,Sigma_b0)
    Sigma_e = np.linalg.solve(A.T,B.T).T
    Sigma_e_l = np.linalg.solve(A,Sigma_b0_l)
    return e, Sigma_e, Sigma_e_l


# %%
@dispatch
def exact_solve(A,b_0:np.ndarray):
    # ic(type(b_0))
    e = np.linalg.solve(A,b_0)
    return e

# @dispatch
# def exact_solve(A, b_0:tape):
#     tape_new = tape([SolveOperator(A)] + b_0.tape)
#     return tape_new

@dispatch
def exact_solve(A, b:node):
    # ic(A)
    # ic(np.linalg.cond(A))
    # ic(np.sort(np.linalg.eigvals(A)))
    # np.linalg.cholesky(A)
    # plt.imshow(A)
    # plt.colorbar()
    # plt.show()
    new_node = node(A, Solve, ancestors= [b])
    # ic('scmul')
    b.parent_tree.add_node(new_node)
    b.descendents = b.descendents + [new_node]
    return new_node

# @dispatch
# def exact_solve(A, b:node):
#     print('here!')
#     pass


def get_mean(tracer, pr_mean):
    return apply_all(tracer, pr_mean)

def get_cov(tracer, pr_cov):
    M = apply_linear_all(tracer, pr_cov)
    Sigma_mg = M @ pr_cov @ M.T
    return Sigma_mg