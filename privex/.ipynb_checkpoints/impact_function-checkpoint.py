from privex.basic import Query, Question, Predicate
from privex.basic import find_function_range_over_bounded_support

import numpy as np

class ImpactFunction():
    def __init__(self, df, question: Question):
        self.df = df
        self.question = question
        self.sensitivity = 2 * question.q1.qsum_sens
        
    def __call__(self, predicate: Predicate):
        D = self.df
        if predicate.attr_val_dict is None:
            negpD = D
        else:
            negpD = D.query(f'not ({predicate.sql()})')
        o1 = self.question.q1(negpD)
        o2 = self.question.q2(negpD)

        scaler = min(o1['ocnt'], o2['ocnt'])
        if self.question.comp == 'higher':
            indicator = o2['ores'] - o1['ores']
        elif self.question.comp == 'lower':
            indicator = o1['ores'] - o2['ores']
        impact = indicator * scaler
        return impact