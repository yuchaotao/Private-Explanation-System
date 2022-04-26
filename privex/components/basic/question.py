from privex.components.basic.query import Query

from typing import Any, Dict, Tuple, List, Sequence

import logging
logger = logging.getLogger(__name__)

class Question():
    def __init__(self, groupby_query, weights: Dict[Query, float], c):
        self.groupby_query = groupby_query
        self.weights = weights
        self.c = c
        
    @staticmethod
    def from_group_comparison(groupby_query, group_A, group_B):
        ''' Why group_A >= group_B ?'''
        group_weights = {
            group_A: 1,
            group_B: -1
        }
        question = Question.from_group_weights(groupby_query, group_weights)
        return question
    
    @staticmethod
    def from_group_weights(groupby_query, group_weights, c = 0):
        '''Why group_weights * group_answers + c >= 0'''
        weights = {
            query: group_weights.get(info['group'], 0)
            for query, info in groupby_query.queries.items()
        }
        question = Question(groupby_query, weights, c)
        return question
    
    def get_related_groups(self):
        return [
            info['group'] for query, info in self.groupby_query.queries.items()
            if self.weights[query] != 0 
        ]
    
    def to_natural_language(self):
        weights = self.weights
        c = self.c
        query_A = [query for query, w in weights.items() if w == 1]
        query_B = [query for query, w in weights.items() if w == -1]
        if len(query_A) == 1 and len(query_B) == 1 and c == 0:
            return f'Why {query_A[0]} >= {query_B[0]}?'
        else:
            return [(q, w) for q, w in weights.items() if w != 0], c
        
    def convert_by_negp(self, predicate):
        new_gorupby_query, new_weights = (
            self
            .groupby_query
            .convert_by_negp(
                predicate, 
                self.weights
            )
        )
        return Question(
            new_gorupby_query, 
            new_weights, 
            self.c
        )
    
    def quick_evaluation(self, dataset):
        s = 0
        for query, weight in self.weights.items():
            if weight != 0:
                x = query.evaluation(dataset)['query_answer']['val']
                s += weight * x
        s -= self.c
        return s
        
    def evaluation(self, dataset):
        query_answers = self.groupby_query.evaluation(dataset)
        return self.evaluation_by_query_answers(query_answers)
        
    def evaluation_by_query_answers(self, query_answers):
        s = 0
        for query, info in query_answers.items():
            w = self.weights[query]
            x = info['res']['query_answer']['val']
            s += w * x
        s -= self.c
        return s
    
    def to_stringified_function(self, counter):
        '''
        Maintain the counter. 
        '''
        x = []
        fstr = ''
        for query in self.groupby_query.queries:
            weight = self.weights[query]
            if weight != 0:
                query_fstr, query_x, counter = query.to_stringified_function(counter)
                x += query_x
                fstr += f'+ ({weight} * ({query_fstr}))'
        fstr += f' - {self.c}'
        return (fstr, x, counter)
        