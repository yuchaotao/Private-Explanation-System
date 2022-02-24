from typing import Any, Dict, Tuple, List, Sequence
from itertools import product
import numpy as np
import json
import os
import time
from scipy.optimize import minimize, Bounds

import logging
logger = logging.getLogger(__name__)

'''
def find_fn_path(fn):
    if fn.startswith('/'):
        return fn
    else:
        return os.path.join(os.getcwd(), fn)
'''

class Predicate():
    def __init__(self, attr_val_dict: Dict[str, Any]):
        self.attr_val_dict = attr_val_dict
        
    def __repr__(self):
        return ' and '.join(
            f'`{attr}` == "{val}"' 
            for attr, val in self.attr_val_dict.items()
        )
    
    __str__ = __repr__
        
class Domain():
    def __init__(self, attr, vmin, vmax, vals):
        self.attr = attr
        self.vmin = vmin
        self.vmax = vmax
        self.vals = vals
        
    def as_dict(self):
        return {
            'attr': self.attr,
            'vmin': self.vmin,
            'vmax': self.vmax,
            'vals': self.vals
        }
        
class Schema():
    def __init__(self, domains: Dict[str, Domain]):
        self.domains = domains
        
    def get_sens(self, attr, agg):
        '''
        @TODO: Support transformations ...
        '''
        if agg == 'count':
            return 1
        elif agg == 'sum':
            return max(
                np.abs(self.domains[attr].vmin),
                np.abs(self.domains[attr].vmax)
            )
        
    def to_json(self, fn):
        fp = open(fn, 'w')
        serializable_domains = {
            attr: domain.as_dict() 
            for attr, domain in self.domains.items()
        }
        json.dump(serializable_domains, fp)
    
    @staticmethod
    def from_json(fn):
        fp = open(fn, 'r')
        serializable_domains = json.load(fp)
        domains = {
            attr: Domain(**domain)
            for attr, domain in serializable_domains.items()
        }
        return Schema(domains)
        
class Query():
    def __init__(self, selection, agg, attr):
        self.selection = selection
        self.agg = agg
        self.attr = attr
        
    def __call__(self, df, dp: Tuple[float, Schema] = None):
        tstart = time.time()
        if self.selection is None:
            D = df
        else:
            D = df.query(self.selection)
        if self.attr is None:
            s = D.iloc[:, 0]
        else:
            s = D[self.attr]
        res = s.agg(self.agg)
        if dp is not None:
            rho, schema = dp
            res = GaussianMechanism(
                res,
                rho,
                schema.get_sens(
                    self.attr, 
                    self.agg
                )
            )()
        tend = time.time()
        #logger.debug(f'query elapsed {tend-tstart:.2f}s for {self}')
        return res
        
    def get_sens(self, schema):
        return schema.get_sens(self.attr, self.agg)
        
    def __repr__(self):
        return f'SELECT {self.agg}({self.attr}) FROM R WHERE {self.selection}'
    
    __str__ = __repr__
    
class Question():
    def __init__(self, fstr, qdir, queries):
        self.fstr = fstr
        self.qdir = qdir
        self.queries = queries
        
    def __repr__(self):
        return f'Why {self.fstr} is {self.qdir}er than what I expected?'
    
    __str__ = __repr__


def find_function_range_over_bounded_support(fstr, bounds):
    '''
    Important: If there is a division, the denominator must be of single sign.
    '''
    o = np.mean(bounds, axis=1)
    n = len(o)
    bounds = Bounds([x[0] for x in bounds], [x[1] for x in bounds], keep_feasible=True)
    #bounds = [bound if bound[0] < bound[1] else None for bound in bounds]
    Lres = minimize(lambda o:  eval(fstr), o, bounds=bounds)
    Rres = minimize(lambda o: -eval(fstr), o, bounds=bounds)
    L =  Lres.fun if Lres.success else -np.inf
    R = -Rres.fun if Rres.success else np.inf
    return L, R

def generate_explanation_predicates(attributes, schema, strategy = 'cross product'):
    if strategy == 'cross product':
        predicates = [
            Predicate(
                dict(
                    zip(
                        attributes, 
                        vals
                    )
                )
            )
            for vals in product(
                *
                [
                    schema.domains[attr].vals 
                    for attr in attributes
                ]
            )
        ]
    elif strategy == 'independent':
        predicates = [
                Predicate(
                    {
                        attr: val
                    }
                )    
            for attr in attributes
                for val in schema.domains[attr].vals 
        ]
    return predicates

def gumbel_noise(scale):
    return np.random.gumbel(scale=scale)

class GaussianMechanism():
    def __init__(self, val, rho, sens=1):
        self.val = val
        self.rho = rho
        self.sens = sens
        self.sigma = np.sqrt(np.divide(sens**2, 2*rho))
        
    def __call__(self):
        return self.val + np.random.normal(scale=self.sigma)
          
