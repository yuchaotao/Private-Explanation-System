#!/usr/bin/env python
import sys
sys.path.append('../../')

import pandas as pd
import numpy as np
import pprint
from itertools import product

from privex.components.basic import Schema, Dataset, GroupbyQuery, Question
from privex.components.utils import generate_explanation_predicates
from privex.framework.solution import ExplanationSession as SolutionExplanationSession
from privex.framework.baseline import ExplanationSession as BaselineExplanationSession
from privex.evaluation import (
    evaluate_question_ci,
    evaluate_topk,
    evaluate_influence_ci,
    evaluate_rank_ci
)

import logging
logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')

logging.info('test')

def quick_experiment(ExplanationSession):
    df = pd.read_csv('../data/adult.csv')
    schema = Schema.from_json('../data/adult.json')
    dataset = Dataset(df, schema)
    gamma = 0.95
    attributes = ['marital-status', 'occupation', 'age', 'relationship', 'race', 'workclass', 'sex', 'native-country']
    predicates = generate_explanation_predicates(attributes, schema, strategy='1-way marginal')
    predicates = predicates[:10]
    #predicates += generate_explanation_predicates(attributes, schema, strategy='2-way marginal')
    es = ExplanationSession(dataset, gamma, predicates)
    
    groupby_query = GroupbyQuery(
        agg = 'AVG',
        attr_agg = 'high_income',
        predicate = None,
        attr_group = 'education',
        schema = schema
    )
    question = Question.from_group_comparison(groupby_query, 'Prof-school', 'Doctorate')
    
    k = 5
    explanation_predicate = np.random.choice(predicates)
    
    evaluate_question_ci(es, groupby_query, question, dataset, rho = 10, repetitions = 100)
    es.phase_3_submit_explanation_request()
    evaluate_topk(es, k, rho = 1000, repetitions = 100)
    evaluate_influence_ci(es, explanation_predicate, rho = 1000, repetitions = 100)
    evaluate_rank_ci(es, explanation_predicate, rho = 1000, repetitions = 100)
    
def experiment():
    df = pd.read_csv('../../data/adult.csv')
    schema = Schema.from_json('../../data/adult.json')
    dataset = Dataset(df, schema)
    gamma = 0.95
    attributes = ['marital-status', 'occupation', 'age', 'relationship', 'race', 'workclass', 'sex', 'native-country']
    predicates = generate_explanation_predicates(attributes, schema, strategy='1-way marginal')
    #predicates = predicates[:10]
    #predicates += generate_explanation_predicates(attributes, schema, strategy='2-way marginal')
    
    groupby_query = GroupbyQuery(
        agg = 'AVG',
        attr_agg = 'high_income',
        predicate = None,
        attr_group = 'education',
        schema = schema
    )
    question = Question.from_group_comparison(groupby_query, 'Prof-school', 'Doctorate')
    k = 5
    explanation_predicate = [
        predicate
        for predicate in predicates
        if predicate.predicate_str == '`age` == "(40, 50]"' 
    ][0]
    
    repetitions = 100
    rho_list_query = [1, 10, 100, 1000]
    rho_list_topk = [10, 100, 1000, 10000]
    rho_list_influence_ci = [10, 100, 1000, 10000]
    rho_list_rank_ci = [10, 100, 1000, 10000]
    explanation_sessions = {
        'solution': SolutionExplanationSession,
        'baseline': BaselineExplanationSession
    }
    gamma_list = [0.9, 0.95, 0.99]
    random_seed = 16324545
    
    question_ci_records = []
    topk_records = []
    influence_ci_records = []
    rank_ci_records = []
    for algorithm, ExplanationSession in explanation_sessions.items():
        es = ExplanationSession(dataset, gamma, predicates, random_seed)

        for rho, gamma in product(rho_list_query, gamma_list):
            es.gamma = gamma
            question_ci_evaluation = evaluate_question_ci(es, groupby_query, question, dataset, rho = rho, repetitions = repetitions)
            question_ci_evaluation.evaluation_records['rho'] = rho
            question_ci_evaluation.evaluation_records['algorithm'] = algorithm
            question_ci_evaluation.evaluation_records['gamma'] = gamma
            question_ci_records.append(
                question_ci_evaluation.evaluation_records
            )
            logging.info(f'{algorithm} / question_ci / rho-{rho} / gamma-{gamma}')
#             break

        es.phase_3_submit_explanation_request()

        for rho in rho_list_topk:
            topk_evaluation = evaluate_topk(es, k, rho = rho, repetitions = repetitions)
            topk_evaluation.evaluation_records['rho'] = rho
            topk_evaluation.evaluation_records['algorithm'] = algorithm
            topk_records.append(
                topk_evaluation.evaluation_records
            )
            logging.info(f'{algorithm} / topk / rho-{rho}')
#             break

        for rho, gamma in product(rho_list_influence_ci, gamma_list):
            es.gamma = gamma
            influence_ci_evaluation = evaluate_influence_ci(es, explanation_predicate, rho = rho, repetitions = repetitions)
            influence_ci_evaluation.evaluation_records['rho'] = rho
            influence_ci_evaluation.evaluation_records['algorithm'] = algorithm
            influence_ci_evaluation.evaluation_records['gamma'] = gamma
            influence_ci_records.append(
                influence_ci_evaluation.evaluation_records
            )
            logging.info(f'{algorithm} / influence_ci / rho-{rho} / gamma-{gamma}')
#             break

        for rho, gamma in product(rho_list_rank_ci, gamma_list):
            es.gamma = gamma
            rank_ci_evaluation = evaluate_rank_ci(es, explanation_predicate, rho = rho, repetitions = repetitions)
            rank_ci_evaluation.evaluation_records['rho'] = rho
            rank_ci_evaluation.evaluation_records['algorithm'] = algorithm
            rank_ci_evaluation.evaluation_records['gamma'] = gamma
            rank_ci_records.append(
                rank_ci_evaluation.evaluation_records
            )
            logging.info(f'{algorithm} / rank_ci / rho-{rho} / gamma-{gamma}')
#             break
#         break

    for category, records in {
        'question_ci': question_ci_records,
        'topk': topk_records,
        'influence_ci': influence_ci_records,
        'rank_ci': rank_ci_records,
    }.items():
        df = pd.concat(records)
        df.to_csv(f'records/{category}.csv', index=False)
    
if __name__ == '__main__':
    #quick_experiment(BaselineExplanationSession)
    #quick_experiment(SolutionExplanationSession)
    experiment()