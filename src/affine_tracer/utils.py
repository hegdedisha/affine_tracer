import numpy as np
import scipy
from icecream import ic

def matker32(x1,x2,l=1, sig2 = 1):
    
    #dist = lambda p1, p2: np.linalg.norm(p1 - p2, axis=0)
    #r = np.asarray([[dist(p1,p2) for p2 in x1] for p1 in x2])
    r = scipy.spatial.distance.cdist(x1,x2).transpose()
    #given the distance r
    p1 = (np.sqrt(3)*r)/l
    p2 = np.exp(-p1)
    p3 = 1 + p1
    # ic(sig2)
    return(sig2 * p2 * p3)   
    
def sq_exp(x1,x2,l=1, sig2 = 1):
    r = scipy.spatial.distance.cdist(x1,x2).transpose()
    #given the distance r
    p1 = r**2/(l**2)
    p2 = np.exp(-p1/2)
    return(sig2 * p2)   

def mat_gen_sq(d,l,s=1):
    x = np.linspace(0,1,d)[:,None]
    A = sq_exp(x,x,l,s)
    x_sol = np.ones(d)
    b = A@x_sol
    return A, b, x_sol

def mat_gen_mt(d,l,s=1):
    x = np.linspace(0,1,d)[:,None]
    A = matker32(x,x,l,s)
    x_sol = np.ones(d)
    b = A@x_sol
    return A, b, x_sol

def mat_gen_mt2(x,l,s=1,x_sol=None):
    # ic(x.shape)
    A = matker32(x,x,l,s)
    if x_sol is None:
        x_sol = np.ones(A.shape[0])
    b = A@x_sol
    return A, b, x_sol

def is_psd(A):
    if all(np.linalg.eigvals(A) >= 0):
        return True
    else:
        return False
    
def is_psd_num(A):
    if all(np.linalg.eigvals(A) >= -1e-12):
        ic(np.trace(A))
        return True
    else:
        ic(max(np.linalg.eigvals(A)))
        ic(np.trace(A))
        return False
    
def is_pd(A):
    if all(np.linalg.eigvals(A) > 0):
        return True
    else:
        return False


def mat_gen_fn():
    np.random.seed(1)
    d = 40

    x_0 = np.zeros(d)
    Sigma_0 = np.eye(d)

    g_f = np.linspace(0,1,d)
    g_f = g_f[:,None]
    g_c = scipy.ndimage.zoom(g_f, zoom = (0.2,1), order= 0)
    grids = [g_f, g_c]

    x_sol = np.random.multivariate_normal(x_0,Sigma_0)
    A, b, x = mat_gen_mt2(g_f,0.05,x_sol=x_sol)
    A2, b2, x2 = mat_gen_mt2(g_c,0.1)
    matrices = [A, A2]  

    return grids, matrices, b