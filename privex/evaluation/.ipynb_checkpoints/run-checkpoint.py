#!/usr/bin/env python
import sys
sys.path.append('../')

import pandas as pd
import numpy as np
import pprint
import heapq
import time
import datetime
import pickle

from privex.components.basic import Schema, Dataset, GroupbyQuery, Question
from privex.components.utils import generate_explanation_predicates
from privex.framework.solution import ExplanationSession

import logging
logger = logging.getLogger(__name__)

def size_of_interval_intersection(i1, i2):
    l1, u1 = i1
    l2, u2 = i2
    return max(min(u1, u2) - max(l1, l2), 0)

def size_of_interval(interval):
    return interval[1] - interval[0]

def jaccard_similarity(i1, i2):
    w1 = i1[1] - i1[0]
    w2 = i2[1] - i2[0]
    wi = size_of_interval_intersection(i1, i2)
    jac = wi / (w1 + w2 - wi)
    return jac

def get_influence_at_rank_i(es, i):
    return es.predicates_with_influences[
        es.sorted_predicates[i-1]
    ]

def get_score_at_rank_i(es, i):
    return es.predicates_with_scores[
        es.sorted_predicates[i-1]
    ]

def get_rank(es, explanation_predicate):
    return es.sorted_predicates.tolist().index(explanation_predicate) + 1

def error_noise_quantification(es, rho, gamma):
    question_ci = es.question_ci
    logger.info(f'true question: {es.question.evaluation(es.dataset)}')
    logger.info(f'question_point: {es.question_point}')
    logger.info(f'question_ci: {question_ci}')
    groundtruth_ci = es.phase_2_ground_truth_ci(rho, gamma)
    logger.info(f'groundtruth_ci: {groundtruth_ci}')
    
    
    percentage_of_missing = 1 - size_of_interval_intersection(
        question_ci, groundtruth_ci) / size_of_interval(groundtruth_ci)
    logger.info(f'percentage_of_missing: {percentage_of_missing}')
    percentage_of_extra = ((size_of_interval(question_ci) - 
        size_of_interval_intersection(
            question_ci, groundtruth_ci)) / np.abs(es.question.evaluation(es.dataset)))
    logger.info(f'percentage_of_extra: {percentage_of_extra}')
    error = (percentage_of_missing + percentage_of_extra) / 2
    
#     jac = jaccard_similarity(question_ci, groundtruth_ci)
#     error = 1 - jac
    logger.info(f'noise quantification error: {error}')
    return error

def error_topk_selection(es, k):
    influences = es.predicates_with_influences
    
    true_kth_influence = get_influence_at_rank_i(es, k)
    logger.info(f'topk true top_k influence: {[get_influence_at_rank_i(es, i+1) for i in range(k)]}')
    logger.info(f'topk true top_k score: {[get_score_at_rank_i(es, i+1) for i in range(k)]}')
    
    noisy_topk_influences = sorted(
        [influences[explanation_predicate]
        for explanation_predicate in es.topk_explanation_predicates],
        reverse=True
    )
    noisy_topk_scores = sorted(
        [es.predicates_with_scores[explanation_predicate]
        for explanation_predicate in es.topk_explanation_predicates],
        reverse=True
    )
    noisy_kth_influence = noisy_topk_influences[-1]
    logger.info(f'topk noisy top_k influence: {noisy_topk_influences}')
    logger.info(f'topk noisy top_k score: {noisy_topk_scores}')
    
    kth_gap = np.abs(true_kth_influence - noisy_kth_influence)
    #error = kth_gap / np.abs(true_kth_influence)
    error = kth_gap / np.abs(get_influence_at_rank_i(es, 1) - get_influence_at_rank_i(es, 0))
    return error

def error_influence_ci(es):
    errors = []
    for explanation_predicate, ci in zip(
        es.topk_explanation_predicates, 
        es.topk_influence_ci
    ):
        true_influence = es.predicates_with_influences[
            explanation_predicate
        ]
        logger.info(f'infci true_influence: {true_influence}')
        logger.info(f'infci ci: {ci[0], ci[1]}')
        error = max(
            np.abs(ci[0] - true_influence),
            np.abs(ci[1] - true_influence)
        # ) / np.abs(true_influence)
        ) / np.abs(get_influence_at_rank_i(es, 1) - get_influence_at_rank_i(es, 0))
        errors.append(error)
    error = np.mean(errors)
    return error

def error_rank_ci(es):
    errors = []
    for explanation_predicate, ci in zip(
        es.topk_explanation_predicates, 
        es.topk_rank_ci
    ):
        true_rank = get_rank(es, explanation_predicate)
        logger.info(f'rankci true_rank: {true_rank}')
        logger.info(f'rankci ci: {ci[0], ci[1]}')
        
        true_influence = es.predicates_with_influences[
            explanation_predicate
        ]
        logger.info(f'rankci true_influence: {true_influence}')
        logger.info(f'rankci influence ci: {get_influence_at_rank_i(es, ci[0]), get_influence_at_rank_i(es, ci[1])}')
        logger.info(f'rankci influence range: {get_influence_at_rank_i(es, 1) - get_influence_at_rank_i(es, 0)}')
        error = max(
            np.abs(ci[0] - true_rank),
            np.abs(ci[1] - true_rank)
        ) / len(es.sorted_predicates)
        errors.append(error)
    error = np.mean(errors)
    return error


def error_rank_ci_old(es):
    errors = []
    for explanation_predicate, ci in zip(
        es.topk_explanation_predicates, 
        es.topk_rank_ci
    ):
        true_influence = es.predicates_with_influences[
            explanation_predicate
        ]
        logger.info(f'rankci true_influence: {true_influence}')
        logger.info(f'rankci ci: {get_influence_at_rank_i(es, ci[0]), get_influence_at_rank_i(es, ci[1])}')
        logger.info(f'rankci influence range: {get_influence_at_rank_i(es, 1) - get_influence_at_rank_i(es, 0)}')
        error = max(
            np.abs(get_influence_at_rank_i(es, ci[0]) - true_influence),
            np.abs(get_influence_at_rank_i(es, ci[1]) - true_influence)
        ) / np.abs(get_influence_at_rank_i(es, 1) - get_influence_at_rank_i(es, 0))
        errors.append(error)
    error = np.mean(errors)
    return error

def run(dataset, scale, full_attributes, rho_query, agg, attr_agg, attr_group, group_a, group_b, rho_topk, rho_influ, rho_rank, gamma, predicate_strategy, k, split_factor, reps):
    rho_expl = rho_topk + rho_influ + rho_rank
    attributes = [attr for attr in full_attributes if attr != attr_group]
    predicates = generate_explanation_predicates(attributes, dataset.schema, predicate_strategy)
    dataset = Dataset(dataset.df.sample(frac=scale), dataset.schema)
    es = ExplanationSession(dataset, gamma, predicates)
    logger.info(f'loaded dataset with {len(dataset.df)} rows and columns {list(dataset.schema.domains.keys())}.')
    
    # Phase 1
    t_start = time.time()
    groupby_query = GroupbyQuery(
        agg = agg,
        attr_agg = attr_agg,
        predicate = None,
        attr_group = attr_group,
        schema = dataset.schema
    )
    es.phase_1_submit_query(groupby_query, rho_query)
    logger.info(f'submited queries with rho = {rho_query}')
    t_end = time.time()
    t_phase_1 = t_end - t_start
    
    # Phase 2
    t_start = time.time()
    question = Question.from_group_comparison(groupby_query, (group_a,), (group_b,))
    es.phase_2_submit_question(question)
    es.phase_2_prepare_question_ci()
    t_end = time.time()
    t_phase_2 = t_end - t_start
    
    # Phase 3
    t_start = time.time()
    es.phase_3_submit_explanation_request()
    es.phase_3_prepare_explanation(k, {'rho_topk': rho_topk, 'rho_influ': rho_influ, 'rho_rank': rho_rank}, split_factor)
    t_end = time.time()
    t_phase_3 = t_end - t_start
    
    # Evaluation
    error_nq    = error_noise_quantification(es, rho_query, gamma)
    error_topk  = error_topk_selection(es, k)
    error_infci = error_influence_ci(es)
    error_rnkci = error_rank_ci(es)
    
    report = {
        'timestamp': pd.Timestamp.now(),
        'scale': scale,
        'Aagg': attr_agg,
        'Agb': attr_group,
        'agg': agg,
        'predicate_strategy': predicate_strategy,
        'predicate_size': len(predicates),
        'g1': group_a,
        'g2': group_b,
        'gs1': len(dataset.df.query(f'`{attr_group}` == "{group_a}"')),
        'gs2': len(dataset.df.query(f'`{attr_group}` == "{group_b}"')),
        'k': k,
        'split_factor': split_factor,
        'gamma': gamma,
        'rho_query': rho_query,
        'rho_expl': rho_expl,
        'rho_topk': es.rho_topk,
        'rho_influ': es.rho_influence_ci,
        'rho_rank': es.rho_rank_ci,
        'error_nq': error_nq,
        'error_topk': error_topk,
        'error_infci': error_infci,
        'error_rnkci': error_rnkci,
        't_phase_1': t_phase_1,
        't_phase_2': t_phase_2,
        't_phase_3': t_phase_3,
        'runtime': t_phase_1 + t_phase_2 + t_phase_3
    }
    report['mings'] = min(report['gs1'], report['gs2'])
    
    with open('test.pkl', 'wb') as outp:
         pickle.dump(es.predicates_with_influences, outp, pickle.HIGHEST_PROTOCOL)
    
    reports = []
    reports.append(report)
    for i in range(reps-1):
        # Phase 1
        t_start = time.time()
        es.phase_1_submit_query(groupby_query, rho_query)
        t_end = time.time()
        t_phase_1 = t_end - t_start
        
        # Phase 2
        t_start = time.time()
        es.phase_2_prepare_question_ci()
        t_end = time.time()
        t_phase_2 = t_end - t_start
        
        # Phase 3
        es.phase_3_prepare_explanation(k, {'rho_topk': rho_topk, 'rho_influ': rho_influ, 'rho_rank': rho_rank}, split_factor)
        
        # Evaluation
        error_nq    = error_noise_quantification(es, rho_query, gamma)
        error_topk  = error_topk_selection(es, k)
        error_infci = error_influence_ci(es)
        error_rnkci = error_rank_ci(es)
        
        new_report = report.copy()
        new_report['t_phase_1'] = t_phase_1
        new_report['t_phase_2'] = t_phase_2
        new_report['runtime'] = t_phase_1 + t_phase_2 + t_phase_3
        new_report['error_nq'] = error_nq
        new_report['error_topk'] = error_topk
        new_report['error_infci'] = error_infci
        new_report['error_rnkci'] = error_rnkci
        
        reports.append(new_report)
    return reports


df = pd.read_csv('../../data/ipums/ipumscps.csv')
schema = Schema.from_json('../../data/ipums/ipumscps.json')
dataset = Dataset(df, schema)
full_attributes = ['RELATE', 'SEX', 'MARST', 'RACE', 'CITIZEN', 'CLASSWKR', 'EDUC']

default = {
    'scale': 1.0,
    'rho_query': 0.1,
    'agg': 'AVG',
    'attr_agg': 'INCTOT',
    'attr_group': 'SEX', # 'MARST',
    'group_a': 'Male', # 'Married, spouse present',
    'group_b': 'Female', # 'Never married/single',
    'rho_topk': 0.5,
    'rho_influ': 0.5,
    'rho_rank': 1.0,
    'gamma': 0.95,
    'predicate_strategy': '1-way marginal',
    'k': 5,
    'split_factor': 0.9,
    'reps': 10
}
