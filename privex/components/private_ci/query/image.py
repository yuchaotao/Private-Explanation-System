import numpy as np
from itertools import product
from scipy.special import erfinv
from scipy.optimize import minimize

import logging
logger = logging.getLogger(__name__)

def image(fun, answers, sigmas, gamma):
    n = len(answers)
#     beta = np.power(gamma, 1/n)
    beta = (gamma - 1) / n + 1
    bounds = [
        (
            answers[i] - np.sqrt(2) * sigmas[i] * erfinv(beta),
            answers[i] + np.sqrt(2) * sigmas[i] * erfinv(beta),
        )
        for i in range(n)
    ]
    logger.info(f'answers: {answers}')
    logger.info(f'sigmas: {sigmas}')
    logger.info(f'bounds: {bounds}')
#     logger.info(f'manual ci: {(bounds[0][0] / bounds[1][1] - bounds[2][1] / bounds[3][0], bounds[0][1] / bounds[1][0] - bounds[2][0] / bounds[3][1])}')
#     logger.info(f'fun ci l: {fun([bounds[0][0], bounds[1][1], bounds[2][1], bounds[3][0]])}')
#     logger.info(f'fun ci u: {fun([bounds[0][1], bounds[1][0], bounds[2][0], bounds[3][1]])}')
    L1, U1 = find_function_range_over_bounded_support(fun, bounds)
    L2, U2 = find_function_range_on_bounds(fun, bounds)
    ci = (min(L1, L2), max(U1, U2))
    return ci

def find_function_range_over_bounded_support(fun, bounds):
    '''
    Important: If there is a division, the denominator must be of single sign.
    '''
    o = np.mean(bounds, axis=1)
    n = len(o)
    #bounds = Bounds([x[0] for x in bounds], [x[1] for x in bounds], keep_feasible=True)
    #bounds = [bound if bound[0] < bound[1] else None for bound in bounds]
    Lres = minimize(lambda x:  fun(x), o, bounds=bounds)
    Rres = minimize(lambda x: -fun(x), o, bounds=bounds)
    L =  Lres.fun if Lres.success else -np.inf
    U = -Rres.fun if Rres.success else np.inf
    return L, U

def find_function_range_on_bounds(fun, bounds):
    res = [fun(x) for x in product(*bounds)]
    L = min(res)
    U = max(res)
    return L, U