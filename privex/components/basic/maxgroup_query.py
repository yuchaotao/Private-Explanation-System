from privex.components.basic.query import Query
from privex.components.basic.predicate import Predicate
from privex.components.basic import GaussianMechanism

import logging
logger = logging.getLogger(__name__)

class MaxgroupQuery():
    def __init__(self, groupby_query, group_agg, related_groups = None):
        self.groupby_query = groupby_query
        self.group_agg = group_agg
        self.related_groups = related_groups
        
    def get_sensitivity(self, dataset):
        attr = self.groupby_query.attr_agg
        agg = self.groupby_query.agg
        return dataset.get_sens(attr, agg)
        
    def evaluation(self, dataset):
        query_answers = self.groupby_query.evaluation(dataset)
        if self.related_groups is not None:
            vals = [
                info['res']['query_answer']['val']
                for query, info in query_answers.items()
                if info['group'] in self.related_groups
            ]
        else:
            vals = [
                info['res']['query_answer']['val']
                for query, info in query_answers.items()
            ]
        #logger.debug(vals)
        if self.group_agg == 'min':
            val = min(vals)
        elif self.group_agg == 'max':
            val = max(vals)
        res = {
            'query_answer': {
                'val': val,
                'sigma': None
            },
            'basic_query_answers': None
        }
        return res
    
    def noisy_evaluation(self, dataset, rho):
        res = self.evaluation(dataset)
        sensitivity = self.get_sensitivity(dataset)
        gm = GaussianMechanism(
            res['query_answer']['val'],
            rho,
            sensitivity
        )
        val = gm()
        sigma = gm.sigma
        res = {
            'query_answer': {
                'val': val,
                'sigma': sigma
            },
            'basic_query_answers': None
        }
        return res
        
    def __call__(self, dataset, rho = None):
        if rho is not None:
            return self.noisy_evaluation(dataset, rho)
        else:
            return self.evaluation(dataset)
    
    def to_stringified_function(self, counter):
        return (f'x[{counter}]', [self], counter + 1)