from typing import Any, Dict
import heapq
import numpy as np

from privex.components.basic.gaussian_mechanism import GaussianMechanism

def topk_of_noises(candidates_with_scores: Dict[Any, float], k, rho, sensitivity):
    N = len(candidates_with_scores)
    rho_per_candidate = rho / N
    gaussian_scores = {
        candidate: GaussianMechanism(
            score,
            rho_per_candidate,
            sensitivity
        )()
        for candidate, score in candidates_with_scores.items()
    }
    topk = heapq.nlargest(k, gaussian_scores.keys(), key=gaussian_scores.get)
    return topk