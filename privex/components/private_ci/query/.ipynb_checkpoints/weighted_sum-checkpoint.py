from privex.components.private_ci.gaussian_ci import gaussian_ci

import numpy as np

def weighted_sum(answers, weights, sigmas, gamma, c = 0):
    answer = np.dot(answers, weights) + c
    sigma = np.linalg.norm(np.multiply(weights, sigmas), ord=2)
    ci = gaussian_ci(answer, sigma, gamma)
    return ci