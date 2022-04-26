from typing import Any, Dict
import heapq
import numpy as np

from privex.components.basic.gaussian_mechanism import GaussianMechanism
from privex.components.private_ci.gaussian_ci import gaussian_ci

def rank_of_noises(predicate, predicates_with_scores, rho, score_sensitivity, gamma):
    N = len(predicates_with_scores)
    rho_per_candidate = rho / N
    predicates_with_noisy_scores = {
        predicate: GaussianMechanism(
            score,
            rho_per_candidate,
            score_sensitivity
        )()
        for predicate, score in predicates_with_scores.items()
    }
    sigma = GaussianMechanism.compute_sigma(rho_per_candidate, score_sensitivity)
    wider_gamma = np.power(gamma, 1 / N)
    wider_ci = {
        predicate: gaussian_ci(o, sigma, wider_gamma)
        for predicate, o in predicates_with_noisy_scores.items()
    }
    wider_ci_l, wider_ci_r = zip(*wider_ci.values())
    l, r = wider_ci[predicate]
    rlb = np.sum(np.array(wider_ci_l) > r) + 1
    rub = len(wider_ci) - np.sum(np.array(wider_ci_r) < l)
    rank_ci = (rlb, rub)
    return rank_ci