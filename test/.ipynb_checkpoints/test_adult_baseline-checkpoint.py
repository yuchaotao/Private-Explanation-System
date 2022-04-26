#!/usr/bin/env python
import sys
sys.path.append('../')

import pandas as pd
import pprint

from privex.components.basic import Schema, Dataset, GroupbyQuery, Question
from privex.components.utils import generate_explanation_predicates
from privex.framework.baseline import ExplanationSession

import logging
logger = logging.getLogger(__name__)

def main():
    df = pd.read_csv('../data/adult.csv')
    schema = Schema.from_json('../data/adult.json')
    dataset = Dataset(df, schema)
    gamma = 0.95
    attributes = ['marital-status', 'occupation', 'age', 'relationship', 'race', 'workclass', 'sex', 'native-country']
    predicates = generate_explanation_predicates(attributes, schema, strategy='1-way marginal')
    #redicates = predicates[:10]
    #predicates += generate_explanation_predicates(attributes, schema, strategy='2-way marginal')
    es = ExplanationSession(dataset, gamma, predicates)
    
    # Show Data
#     with pd.option_context('display.max_rows', None, 'display.max_columns', None, 
# 'display.max_colwidth', 1000, 'display.width', None):
    print(df[attributes + ['education', 'high_income']].head(10))
    
    # Phase 1
    groupby_query = GroupbyQuery(
        agg = 'AVG',
        attr_agg = 'high_income',
        predicate = None,
        attr_group = 'education',
        schema = schema
    )
    rho_query = 10.0
    es.phase_1_submit_query(groupby_query, rho_query)
    print(f'submiited queries with rho = {rho_query}')
    with pd.option_context('display.max_rows', None, 'display.max_columns', None, 
'display.max_colwidth', 1000):
        print(es.phase_1_show_query_results())
    
    # Phase 2
    question = Question.from_group_comparison(groupby_query, 'Prof-school', 'Doctorate')
    es.phase_2_submit_question(question)
    es.phase_2_prepare_question_ci()
    ci = es.phase_2_show_question_ci()
    print('question: ', question.to_natural_language())
    print(f'The {gamma*100:.0f}% confidence interval of the difference is ', ci)
    
    # Phase 3
    k = 5
    logger.debug(f'Length of predicates is {len(predicates)}')
    rho_expl = 10000.0
    es.phase_3_submit_explanation_request()
    es.phase_3_prepare_explanation(k, rho_expl)
    with pd.option_context('display.max_rows', None, 'display.max_columns', None, 
'display.max_colwidth', 1000, 'display.width', None):
        print(es.phase_3_show_explanation_table())
    #pprint.pprint(es.measure_explanation_table())
    
if __name__ == '__main__':
    main()