from privex.components.basic.domain import Domain

from typing import Dict
import json
import numpy as np

class Schema():
    '''
        Encodes the domains of all attribtues
    '''
    def __init__(self, domains: Dict[str, Domain]):
        self.domains = domains
        
    def get_sens(self, attr, agg):
        '''
        @TODO: Support transformations ...
        '''
        if agg == 'CNT':
            return 1
        elif agg == 'SUM':
            return max(
                np.abs(self.domains[attr].vmin),
                np.abs(self.domains[attr].vmax)
            )
        else:
            return None
        
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
    
    def __repr__(self):
        return str(self.domains)
    
    __str__ = __repr__