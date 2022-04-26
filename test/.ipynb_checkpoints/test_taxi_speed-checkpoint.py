#!/usr/bin/env python
import sys
sys.path.append('../')

import pandas as pd
import pprint

from privex.components.basic import Schema, Dataset, Predicate, GroupbyQuery, Question
from privex.components.utils import generate_explanation_predicates
from privex.framework.solution import ExplanationSession

import logging
logger = logging.getLogger(__name__)

def main():
    #nrows = 100000
    nrows = None
    df = pd.read_csv('../data/preprocessed_yellow_tripdata_2019-02-01.csv', nrows=nrows)
    logger.info(f'{len(df)} records have been loaded.')
    schema = Schema.from_json('../data/preprocessed_yellow_tripdata_2019-02.json')
    dataset = Dataset(df, schema)
    gamma = 0.95
    #attributes = ['PU_Zone', 'PU_Borough', 'PU_Hour', 'PU_WeekDay', 'DO_Zone', 'DO_Borough', 'DO_Hour', 'DO_WeekDay']
    #attributes = ['PU_Zone', 'PU_Hour', 'PU_WeekDay', 'DO_Zone', 'DO_Hour', 'DO_WeekDay']
    attributes = ['PU_Hour', 'DO_Zone']
    predicates = generate_explanation_predicates(attributes, schema, strategy='1-way marginal')
    #predicates = predicates[:10]
    #predicates += generate_explanation_predicates(attributes, schema, strategy='2-way marginal')
    es = ExplanationSession(dataset, gamma, predicates)
    
    # Show Data
#     with pd.option_context('display.max_rows', None, 'display.max_columns', None, 
# 'display.max_colwidth', 1000, 'display.width', None):
    #print(df[attributes + ['PU_Borough', 'DO_Borough', 'trip_speed']].head(10))
    
    # Phase 1
    groupby_query = GroupbyQuery(
        agg = 'AVG',
        attr_agg = 'trip_speed',
        predicate = Predicate('PU_Borough == "Manhattan"'),
        attr_group = 'PU_Zone',
        schema = schema
    )
    rho_query = 10.0
    es.phase_1_submit_query(groupby_query, rho_query)
    print(f'submiited queries with rho = {rho_query}')
    with pd.option_context('display.max_rows', None, 'display.max_columns', None, 
'display.max_colwidth', 1000):
        print(es.phase_1_show_query_results())
    
    # Phase 2
#     def weight_mapping(group):
#         if group[0] == group[1]:
#             return 0
#         if group[1] == 'Brooklyn':
#             return 1
#         if group[0] == 'Brooklyn':
#             return -6
#         return 0
    def weight_mapping(group):
        if group == ('SoHo', ):
            return -1
        if group == ('Financial District North',):
            return 1
        return 0
    group_weights = {
        group: weight_mapping(group)
        for group in groupby_query.groups
    }
    #print(group_weights)
    question = Question.from_group_weights(groupby_query, group_weights)
    es.phase_2_submit_question(question)
    es.phase_2_prepare_question_ci()
    ci = es.phase_2_show_question_ci()
    print('question: ', question.to_natural_language())
    print(f'The {gamma*100:.0f}% confidence interval of the difference is ', ci)
    
    # Phase 3
    k = 5
    logger.debug(f'Length of predicates is {len(predicates)}')
    rho_expl = 100000.0
    es.phase_3_submit_explanation_request()
    es.phase_3_prepare_explanation(k, rho_expl)
    with pd.option_context('display.max_rows', None, 'display.max_columns', None, 
'display.max_colwidth', 1000, 'display.width', None, 'display.expand_frame_repr', False):
        print(es.phase_3_show_explanation_table())
    #pprint.pprint(es.measure_explanation_table())
    
if __name__ == '__main__':
    main()