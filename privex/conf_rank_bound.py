import numpy as np
from typing import Sequence
from tqdm import tqdm

from privex.basic import Predicate, Schema

import logging
logger = logging.getLogger(__name__)

class PrivRankBound():
    def __init__(self, df, predicates_with_scores, rho, sensitivity):
        self.df = df
        self.predicates_with_scores = predicates_with_scores
        self.sorted_impacts = sorted(
            predicates_with_scores.values(),
            reverse=True
        )
        self.rho = rho
        self.sensitivity = sensitivity
    
    def rank_bound_score(self, predicate, t):
        '''
        It corresponds to I(p) - I(top(t)) in the paper.
        '''
        return self.predicates_with_scores[predicate] - self.sorted_impacts[t-1]
    
    def find_upper_bound(self, predicate, gamma):
        '''
        It is a noisy binary search.
        '''
        psize = len(self.predicates_with_scores)
        N = np.ceil(np.log2(psize+1)).astype(int)
        sigma = 2.0 * self.sensitivity / np.sqrt(2*(self.rho / N))
        xi = sigma * np.sqrt(2 * np.log(N / (1-gamma)))
        
        low, high = 1, psize
        while high > low:
            t = np.ceil((low+high)/2).astype(int)
            S = self.rank_bound_score(predicate, t)
            S_hat = S + np.random.normal(scale=sigma)
            if S_hat > xi:
                high = max(t-1, 1)
            else:
                low = t
        return high
    
    def find_lower_bound(self, predicate, gamma):
        '''
        It is a noisy binary search.
        '''
        psize = len(self.predicates_with_scores)
        N = np.ceil(np.log2(psize+1)).astype(int)
        sigma = 2.0 * self.sensitivity / np.sqrt(2*(self.rho / N))
        xi = sigma * np.sqrt(2 * np.log(N / (1-gamma)))
        
        low, high = 1, psize
        while high > low:
            t = np.floor((low+high)/2).astype(int)  # here exists change
            S = self.rank_bound_score(predicate, t)
            S_hat = S + np.random.normal(scale=sigma)
            if S_hat < -xi:  # here exists change
                low = min(t+1, psize)  # here exists change
            else:
                high = t  # here exists change
        return high
    
    def ci_bounds(self, predicate, gamma):
        rlb = self(predicate, gamma, 'lower')
        rub = self(predicate, gamma, 'upper')
        return (rlb, rub)
    
    def __call__(self, predicate, gamma, which_side = 'upper'):
        if which_side == 'upper':
            return self.find_upper_bound(predicate, gamma)
        elif which_side == 'lower':
            return self.find_lower_bound(predicate, gamma)
            