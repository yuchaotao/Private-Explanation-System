from privex.basic import Query, Question, Predicate
from privex.basic import find_function_range_over_bounded_support

import numpy as np

class ImpactFunction():
    def __init__(self, df, question: Question):
        self.df = df
        self.question = question
        
        o = [
            query(df)
            for query in question.queries
        ]
        self.qfD = eval(question.fstr)
        
    def __call__(self, predicate: Predicate):
        D = self.df
        tstart = time.time()
        negpD = D.query(f'not ({predicate})')
        o = [
            query(negpD)
            for query in self.question.queries
        ]
        tend = time.time()
        #logger.debug(f'negpD and o takes {tend-tstart:.2f}s')
        qfnegpD = eval(self.question.fstr)
        #logger.debug(self.question.fstr)
        #logger.debug(o)
        #logger.debug(f'qfnegpD of {predicate} is : {qfnegpD}')

        qfD = self.qfD
        #logger.debug(f'{predicate}: {negpD.size}, {D.size}, {qfD}, {qfnegpD}')
        if self.question.qdir == 'high':
            return np.divide(negpD.size, D.size) * (qfD - qfnegpD)
        elif self.question.qdir == 'low':
            return np.divide(negpD.size, D.size) * (qfnegpD - qfD)
        
    def questionize(self, predicate):
        queries = [
            Query(f'not ({predicate})', 'count', None),
            Query(None, 'count', None)
        ]
        queries += self.question.queries
        queries += [
            Query(
                f'(not ({predicate})) and {query.selection}', 
                query.agg, 
                query.attr
            )
            for query in self.question.queries
        ]
        qfD_str = self.question.fstr.replace('o[', 'o[2+') 
        qfnegpD_str = self.question.fstr.replace('o[', f'o[2+{len(self.question.queries)}+') 
        if self.question.qdir == 'high':
            fstr = f'o[0] / o[1] * (({qfD_str}) - ({qfnegpD_str}))'
        elif self.question.qdir == 'low':
            fstr = f'o[0] / o[1] * (({qfnegpD_str}) - ({qfD_str}))'
        return Question(fstr, None, queries)
    
    def boundaries_at_distance_d(self, predicate, d, schema):
        impact_as_question = self.questionize(predicate)
        impact_fstr = impact_as_question.fstr
        impact_queries = impact_as_question.queries
        o = [impact_query(self.df) for impact_query in impact_queries]
        if d > 0:
            sens = [impact_query.get_sens(schema) for impact_query in impact_queries]
            bounds = [
                (
                    o[i] - sens[i] * d,
                    o[i] + sens[i] * d
                )
                for i in range(len(o))
            ]
            def temp():
                for o in product(*bounds):
                    one_impact = eval(impact_fstr)
                    logger.debug(f'one impact of {predicate} is {one_impact}')
            #logger.debug(bounds)
            #temp()
            L, R = find_function_range_over_bounded_support(impact_fstr, bounds)
        else:
            y = eval(impact_fstr)
            L, R = y, y
        return L, R