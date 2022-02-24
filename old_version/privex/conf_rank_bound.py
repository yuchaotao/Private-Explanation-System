import numpy as np
from typing import Sequence
from tqdm import tqdm

from privex.basic import Predicate, ImpactFunction, Schema

import logging
logger = logging.getLogger(__name__)

class PrivRankBound():
    def __init__(self, df, predicates: Sequence[Predicate], impact_function: ImpactFunction, schema: Schema, rho):
        self.df = df
        self.predicates = predicates
        self.impact_function = impact_function
        self.schema = schema
        self.rho = rho
        
    def rank_bound_at_distance_d(self, predicate, d):
        '''
        It corresponds to B(p, d) in the paper.
        '''
        B = 0
        L, _ = self.impact_function.boundaries_at_distance_d(
                predicate, 
                d,
                self.schema
            )
        for other_predicate in self.predicates:
            _, R = self.impact_function.boundaries_at_distance_d(
                other_predicate, 
                d,
                self.schema
            )
            if R >= L:
                B += 1
        return B
    
    def rank_bound_score(self, predicate, t, max_d = None):
        '''
        It corresponds to \omega(p, t) in the paper.
        '''
        N = np.ceil(np.log2(len(self.predicates)+1)).astype(int)
        if max_d is None:
            # sigma: the noise scale used later in the binary search
            sigma = 2.0 / np.sqrt(2*(self.rho / N))
            max_d = max(10, int(10 * sigma))
        for d in tqdm(range(max_d)):
            B = self.rank_bound_at_distance_d(predicate, d)
            if B >= t:
                break
        return d
    
    def __call__(self, predicate, gamma):
        '''
        It is a noisy binary search.
        '''
        N = np.ceil(np.log2(len(self.predicates)+1)).astype(int)
        sigma = 2.0 / np.sqrt(2*(self.rho / N))
        xi = sigma * np.sqrt(2 * np.log(N / (1-gamma)))
        
        low, high = 1, len(self.predicates)
        while high > low:
            logger.x1(f'{low}, {high}')
            t = np.ceil((low+high)/2)
            S = self.rank_bound_score(predicate, t)
            S_hat = S + np.random.normal(scale=sigma)
            if S_hat > t:
                high = max(t-1, 1)
            else:
                low = t
        return high
    
    def debug(self, predicate, gamma):
        d = 1
        for other_predicate in self.predicates:
            L, R = self.impact_function.boundaries_at_distance_d(
                other_predicate, 
                d,
                self.schema
            )
            logger.debug(f'predicate {other_predicate} impact boundaries: {L}, {R}')
        for d in range(10):
            logger.debug(f'distance {d}: {self.rank_bound_at_distance_d(predicate, d)}')
        for t in range(len(self.predicates)):
            logger.debug(f'rank bound {t}: {self.rank_bound_score(predicate, t)}')