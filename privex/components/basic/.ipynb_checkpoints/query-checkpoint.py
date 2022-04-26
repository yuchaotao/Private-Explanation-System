from privex.components.basic.gaussian_mechanism import GaussianMechanism
from privex.components.basic.predicate import Predicate

import pandas as pd
import numpy as np

import logging
logger = logging.getLogger(__name__)

class Query():
    '''
        This is an aggregation query with selection.
    '''
    
    def __init__(self, agg, attr_agg, predicate):
        self.agg = agg
        self.attr_agg = attr_agg
        self.predicate = predicate
        
        self.agg_mapping = {
            'CNT': 'count',
            'SUM': 'sum',
            'AVG': 'mean'
        }
        self.basic_queries = self.to_basic_queries()
        
    def get_sensitivity(self, dataset):
        sens_dict = {
            'CNT': 1,
            'SUM': dataset.get_sens(self.attr_agg, 'SUM'),
            'AVG': None
        }
        return sens_dict[self.agg]
        
    def convert_by_negp(self, predicate):
        predicate = Predicate.conjunction(
            self.predicate,
            Predicate.negation(predicate)
        )
        return Query(
            self.agg,
            self.attr_agg,
            predicate
        )
    
    def to_basic_queries(self):
        if self.agg in ['CNT', 'SUM']:
            basic_queries = [self]
        elif self.agg in ['AVG']:
            basic_queries = [
                Query('SUM', self.attr_agg, self.predicate),
                Query('CNT', self.attr_agg, self.predicate)
            ]
        return basic_queries
        
    def series_to_agg(self, dataset):
        df = dataset.df
        if self.predicate is None:
            D = df
        else:
            D = df.query(self.predicate.to_sql())
        if self.attr_agg is None:
            s = D.iloc[:, 0]
        else:
            s = D[self.attr_agg]
        return s
        
    def evaluation(self, dataset):
        s = self.series_to_agg(dataset)
        val = s.agg(self.agg_mapping[self.agg])
        res = {
            'query_answer': {
                'val': val if val is not np.nan else 0,
                'sigma': None
            },
            'basic_query_answers': None
        }
        return res
    
    def noisy_evaluation(self, dataset, rho):
        s = self.series_to_agg(dataset)
        basic_query_answers = []
        for basic_query in self.basic_queries:
            gm = GaussianMechanism(
                s.agg(self.agg_mapping[
                    basic_query.agg
                ]),
                rho / len(self.basic_queries),
                dataset.get_sens(
                    basic_query.attr_agg, 
                    basic_query.agg
                )
            )
            ans = {
                'val': gm(),
                'sigma': gm.sigma,
                'generator': gm,
            }
            basic_query_answers.append(ans)
        if self.agg in ['CNT', 'SUM']:
            query_answer = {
                'val': basic_query_answers[0]['val'],
                'sigma': gm.sigma,
                'generator': gm
            }
        elif self.agg == 'AVG':
            query_answer = {
                'val': basic_query_answers[0]['val'] 
                       / 
                       basic_query_answers[1]['val'],
                'sigma': None,
                'generator': (lambda basic_query_answers:
                    lambda :
                              basic_query_answers[0]['generator']()
                              /
                              basic_query_answers[1]['generator']()
                )(basic_query_answers)
            }
        res = {
            'query_answer': query_answer,
            'basic_query_answers': basic_query_answers
        }
        return res
        
    def __call__(self, dataset, rho = None):
        if rho is not None:
            res = self.noisy_evaluation(dataset, rho)
        else:
            res = self.evaluation(dataset)
        #logger.debug(f'{self}: {res}')
        return res
        
    def __repr__(self):
        #return f'SELECT AVG({self.attr}) FROM R WHERE {self.predicate}'
        return f'{self.agg}({self.attr_agg}) WHERE {self.predicate}'
    __str__ = __repr__
    
    def to_stringified_function(self, counter):
        agg = self.agg
        if agg in ['SUM', 'CNT']:
            return (f'x[{counter}]', [self], counter+1)
        elif agg == 'AVG':
            return (f'x[{counter}] / x[{counter+1}]', self.basic_queries, counter+2)