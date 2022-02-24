from typing import Any, Dict
import heapq
import numpy as np
from tqdm import tqdm

import logging
logger = logging.getLogger(__name__)

from privex.basic import gumbel_noise

def noisy_topk(k, candidates_with_scores: Dict[Any, float], rho, sens=1):
    # bounded range DP, which implies 1/8 \eps^2-zCDP
    epsilon = np.sqrt(8*rho/k)
    gumbel_scores = {
        candidate: score + gumbel_noise(2*sens/epsilon)
        for candidate, score in candidates_with_scores.items()
    }
    topk = heapq.nlargest(k, gumbel_scores.keys(), key=gumbel_scores.get)
    return topk