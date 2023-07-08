from privex.components.basic.query import Query
from privex.components.basic.predicate import Predicate

from itertools import product
import pandas as pd

class GroupbyQuery():
    def __init__(self, agg, attr_agg, predicate, attr_group, schema):
        self.agg = agg
        self.attr_agg = attr_agg
        self.predicate = predicate
        self.attr_group_type = 'single' if type(attr_group) is str else 'sequence'
        self.attr_group = [attr_group] if self.attr_group_type == 'single' else attr_group
        self.schema = schema
        
        self.groups = list(product(*[
            schema.domains[attr].vals
            for attr in self.attr_group
        ]))
        self.queries = self.convert_to_queries(schema)
        
    @property
    def sensitivity(self):
        return self.schema.get_sens(self.attr_agg, self.agg)
        
    def get_df_groups(self, dataset):
        df = dataset.df
        if self.predicate is None:
            D = df
        else:
            D = df.query(self.predicate.to_sql())
        df_groups = dict(
            tuple(
                D.groupby(self.attr_group[0] if len(self.attr_group) == 1 else attr_group)
            )
        )
        # print(df_groups)
        return df_groups
        
    def convert_to_queries(self, schema):
        '''@TODO: Remove schema from input'''
        queries = {}
        for group in self.groups:
            combined_predicate = Predicate.conjunction(
                self.predicate,
                Predicate.from_dict({
                    self.attr_group[i]: group[i]
                    for i in range(len(self.attr_group))
                })
            )
            query = Query(
                self.agg,
                self.attr_agg,
                combined_predicate
            )
            queries[query] = {
                'group': group
            }
        return queries
    
    def convert_by_negp(self, predicate, weights = None):
        if weights is not None:
            new_groupby_query = GroupbyQuery(
                self.agg,
                self.attr_agg,
                Predicate.conjunction(self.predicate,
                    Predicate.negation(predicate)
                ),
                self.attr_group,
                self.schema
            )
            group_to_old_query = {
                info['group']: query
                for query, info in self.queries.items()
            }
            group_to_new_query = {
                info['group']: query
                for query, info in new_groupby_query.queries.items()
            }
            new_weights = {
                group_to_new_query[group]: weights[
                    group_to_old_query[group]
                ]
                for group in group_to_new_query
            }
            return (new_groupby_query, new_weights)
        else:
            new_groupby_query = GroupbyQuery(
                self.agg,
                self.attr_agg,
                Predicate.conjunction(self.predicate,
                    Predicate.negation(predicate)
                ),
                self.attr_group,
                self.schema
            )
            return new_groupby_query
    
    def convert_to_cnt(self):
        return GroupbyQuery(
            'CNT',
            self.attr_agg,
            self.predicate,
            self.attr_group,
            self.schema
        )
        
    def evaluation(self, dataset):
        schema = dataset.schema
        query_answers = {
            query: {
                'group': info['group']
            }
            for query, info in self.queries.items()
        }
        
        for query in self.queries:
            res = query(dataset)
            query_answers[query]['res'] = res
        return query_answers
    
    def noisy_evaluation(self, dataset, rho):
        schema = dataset.schema
        query_answers = {
            query: {
                'group': info['group']
            }
            for query, info in self.queries.items()
        }
        
        for query in self.queries:
            res = query(dataset, rho)
            query_answers[query]['res'] = res
        return query_answers
    
    def get_answer_table(self, dataset, rho):
        answer_table = []
        true_query_answers = self.evaluation(dataset)
        noisy_query_answers = self.noisy_evaluation(dataset, rho)
        for query in self.queries:
            group = ', '.join(true_query_answers[query]['group'])
            true_answer = true_query_answers[query]['res']['query_answer']['val']
            noisy_answer = noisy_query_answers[query]['res']['query_answer']['val']
            answer_table.append({
                'group': group,
                'true_answer': true_answer,
                'noisy_answer': noisy_answer
            })
        return answer_table, pd.DataFrame(answer_table)
    
    def __call__(self, dataset, rho = None):
        if rho is not None:
            return self.noisy_evaluation(dataset, rho)
        else:
            return self.evaluation(dataset)
        
    def __repr__(self):
        #return f'SELECT AVG({self.attr}) FROM R WHERE {self.predicate}'
        return f'{self.agg}({self.attr_agg}) WHERE {self.predicate} GROUP BY {self.attr_group}'
    
    __str__ = __repr__