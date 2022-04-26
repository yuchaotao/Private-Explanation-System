from privex.components.basic.dataset import Dataset
from privex.components.basic.groupby_query import GroupbyQuery
from privex.components.basic.maxgroup_query import MaxgroupQuery

import numpy as np

import logging
logger = logging.getLogger(__name__)

class InfluenceFunction():
    def __init__(self, dataset, question):
        # construct the predicate to include 
        # the tuples related to the question only
        question_predicate = 'or'.join(
            f'({query.predicate})'
            for query, weight in question.weights.items()
            if weight != 0
        )
        print(question_predicate)
        self.dataset = Dataset(
            dataset.df.query(question_predicate), 
            dataset.schema
        )
        logger.info(f'Dataset relative to the question has length {len(self.dataset.df)}')
        
        #self.dataset = dataset
        self.question = question
        
    def __call__(self, predicate):
        D = self.dataset
        qD = self.question.quick_evaluation(D)
        
        negpD = Dataset(
            D.df.query(f'not ({predicate.to_sql()})'),
            D.schema
        )
        qnegpD = self.question.quick_evaluation(negpD)
        
        related_groups = self.question.get_related_groups()
        if self.question.groupby_query.attr_group_type == 'single':
            related_groups = [group[0] for group in related_groups]
        df_groups = self.question.groupby_query.get_df_groups(self.dataset)
        related_df_groups = [
            df_group
            for group, df_group in df_groups.items() 
            if group in related_groups
        ]
        gsizes = [df_group.shape[0] for df_group in related_df_groups]
        negpgsizes = [
            df_group.query(f'not ({predicate.to_sql()})').shape[0]
            for df_group in related_df_groups
        ]
        
        influence = (qD - qnegpD) * min(negpgsizes) / (max(gsizes) + 1)
        
        agg = self.question.groupby_query.agg
        if agg in ['CNT', 'SUM']:
            score = influence
        elif agg == 'AVG':
            score = (qD - qnegpD) * min(negpgsizes)
        
        res = {
            'influence': influence,
            'score': score
        }
        
        return res
    
    def score_sensitivity(self):
        weights_one_norm = np.linalg.norm(
            np.array(list(self.question.weights.values())), 
            ord=1
        )
        agg = self.question.groupby_query.agg
        attr_agg = self.question.groupby_query.attr_agg
        attr_sum_sens = self.dataset.get_sens(attr_agg, 'SUM')
        sens_dict = {
            'CNT': 2 * weights_one_norm,
            'SUM': 2 * attr_sum_sens * weights_one_norm,
            'AVG': 8 * attr_sum_sens * weights_one_norm
        }
        return sens_dict[agg]
    
    def to_stringified_function(self, predicate, counter):
        fstr = ''
        x = []
        
        question_fstr, question_x, counter = self.question.to_stringified_function(
            counter)
        
        negp_question = self.question.convert_by_negp(predicate)
        negp_question_fstr, negp_question_x, counter = negp_question.to_stringified_function(counter)
        #logger.debug(str(negp_question.to_natural_language()))
        
        fstr = f'(({question_fstr}) - ({negp_question_fstr}))' 
        x = question_x + negp_question_x
        
        #for query in negp_question_x:
        #    logger.debug(str(query))
        
        cntgroupby_query = self.question.groupby_query.convert_to_cnt()
        negp_cntgroupby_query = cntgroupby_query.convert_by_negp(predicate)
        related_groups = self.question.get_related_groups()
        
        minnegpgroup_fstr, minnegpgroup_x, counter = MaxgroupQuery(
            negp_cntgroupby_query, 
            'min',
            related_groups
        ).to_stringified_function(counter)
        
        maxgroup_fstr, maxgroup_x, counter = MaxgroupQuery(
            cntgroupby_query, 
            'max',
            related_groups
        ).to_stringified_function(counter)
        
        fstr += f' * ({minnegpgroup_fstr}) / ({maxgroup_fstr})'
        x += minnegpgroup_x + maxgroup_x
        
        return (fstr, x, counter)