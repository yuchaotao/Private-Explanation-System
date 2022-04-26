import numpy as np
from scipy.special import erfinv

from privex.basic import find_function_range_over_bounded_support

def monte_carlo_ci(fstr, o, sigmas, gamma, L = 1000):
    # ---- the rest should not use x ----
    n = len(o)
    beta = np.power(gamma, 1/n)
    C = [np.sqrt(2) * sigma * erfinv(beta) for sigma in sigmas]
    
    fstr.replace('o', 'ohat')
    y = [o[i] + np.random.uniform(-1, 1, size=L) * C[i] for i in range(n)]
    fhat = []
    for rep in range(L):
        ohat = y[rep, :]
        fhat.append(eval(fstr))
    L = np.min(fhat)
    R = np.max(fhat)
    return L, R

def analytical_ci(fstr, o, sigmas, gamma):
    n = len(o)
    beta = np.power(gamma, 1/n)
    bounds = [
        (
            o[i] - np.sqrt(2) * sigmas[i] * erfinv(beta),
            o[i] + np.sqrt(2) * sigmas[i] * erfinv(beta),
        )
        for i in range(n)
    ]
    L, R = find_function_range_over_bounded_support(fstr, bounds)
    return L, R

def gaussian_ci(o, sigma, gamma):
    half_width = np.sqrt(2) * sigma * erfinv(gamma)
    ci = (
        o - half_width,
        o + half_width
    )
    return ci