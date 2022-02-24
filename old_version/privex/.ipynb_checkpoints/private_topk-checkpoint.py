from typing import Any, Dict
import heapq
import numpy as np
from tqdm import tqdm

import logging
logger = logging.getLogger(__name__)

from privex.basic import GaussianMechanism, Query, Domain, Schema
from privex.basic import ImpactFunction
from privex.basic import gumbel_noise
from privex.basic import generate_explanation_predicates

def noisy_topk_predicates_by_attributes(k, attributes, schema, df, question, rho, sens):
    '''
    Need to know the sensitivity of impact_function
    '''
    impact_function = ImpactFunction(df, question)
    predicates = generate_explanation_predicates(attributes, schema)
    predicates_with_scores = {
        predicate: impact_function(predicate)
        for predicate in predicates
    }
    topk_predicates = noisy_topk(k, predicates_with_scores, rho, sens)
    return topk_predicates    

def noisy_topk_predicates(k, predicates, impact_function, rho):
    predicates_with_scores = {
        predicate: impact_function(predicate)
        for predicate in predicates
    }
    sems = impact_function.sensitivity
    topk_predicates = noisy_topk(k, predicates_with_scores, rho, sens)
    return topk_predicates

def noisy_topk(k, candidates_with_scores: Dict[Any, float], rho, sens=1):
    epsilon = np.sqrt(2*rho)
    gumbel_scores = {
        candidate: score + gumbel_noise(2*sens/epsilon)
        for candidate, score in candidates_with_scores.items()
    }
    topk = heapq.nlargest(k, gumbel_scores.keys(), key=gumbel_scores.get)
    return topk

def subsample_and_rank_aggregate_topk(k, predicates, df, question, rho, N = None):
    if N is None:
        N = max(int(len(df) / 100), 1)
    subsamples = np.array_split(
        df.sample(frac=1),
        N
    )
    predicates_with_scores = {
        predicate: 0
        for predicate in predicates
    }
    for i in tqdm(range(N)):
        subsample = subsamples[i]
        impact_function = ImpactFunction(subsample, question)
        predicates_with_impacts = {
            predicate: impact_function(predicate)
            for predicate in predicates
        }
        '''Borda Method'''
        for i, predicate in enumerate(
            predicate 
            for predicate, _ in sorted(
                predicates_with_impacts.items(), 
                key = lambda x: x[1]
            )
        ):
            predicates_with_scores[predicate] += i
    logger.info(predicates_with_scores)
    topk_predicates = noisy_topk(k, predicates_with_scores, rho, sens=len(predicates))
    return topk_predicates