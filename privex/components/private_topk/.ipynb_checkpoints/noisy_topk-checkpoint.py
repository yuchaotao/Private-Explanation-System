from typing import Any, Dict
import heapq
import numpy as np

import logging
logger = logging.getLogger(__name__)

def noisy_topk(candidates_with_scores: Dict[Any, float], k, rho, sensitivity):
    # bounded range DP, which implies 1/8 \eps^2-zCDP
    epsilon = np.sqrt(8*rho/k)
    logger.info(f'gumbel scale: {2*sensitivity/epsilon}')
    gumbel_scores = {
        candidate: score + gumbel_noise(2*sensitivity/epsilon)
        for candidate, score in candidates_with_scores.items()
    }
    topk = heapq.nlargest(k, gumbel_scores.keys(), key=gumbel_scores.get)
    
    topk_scores = [candidates_with_scores[c] for c in topk]
    gumbel_topk_scores = [gumbel_scores[c] for c in topk]
    logger.info(f'topk_scores: {topk_scores}')
    logger.info(f'gumbel_topk_scores: {gumbel_topk_scores}')
    
    sorted_candidates = np.array(sorted(
            candidates_with_scores.keys(),
            key = candidates_with_scores.get,
            reverse=True
        ))
    true_topk = sorted_candidates[:k]
    true_topk_scores = [candidates_with_scores[c] for c in true_topk]
    gumbel_true_topk_scores = [gumbel_scores[c] for c in true_topk]
    logger.info(f'true_topk_scores: {true_topk_scores}')
    logger.info(f'gumbel_true_topk_scores: {gumbel_true_topk_scores}')
    
    return topk

def gumbel_noise(scale):
    return np.random.gumbel(scale=scale)