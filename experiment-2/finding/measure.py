import pandas as pd
import numpy as np
import pprint
import heapq
import time
import datetime
import pickle

import logging
logger = logging.getLogger(__name__)

import run

import sys
sys.path.append('../../')
sys.path.append('../')

import german.default as german_default

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

def get_predicates_with_influences(intermediates):
    predicates_with_influences_and_scores = intermediates['InfluScores']
    return {
        predicate: combined['influence'] 
        for predicate, combined in predicates_with_influences_and_scores.items()
    }

def get_predicates_with_scores(intermediates):
    predicates_with_influences_and_scores = intermediates['InfluScores']
    return {
        predicate: combined['score'] 
        for predicate, combined in predicates_with_influences_and_scores.items()
    }

def get_sorted_predicates(intermediates):
    predicates_with_influences_and_scores = intermediates['InfluScores']
    return np.array(sorted(
        predicates_with_influences_and_scores.keys(),
        key = lambda x: predicates_with_influences_and_scores[x]['influence'],
        reverse=True
    ))

def get_influence_at_rank_i(intermediates, i):
    return get_predicates_with_influences(intermediates)[
        get_sorted_predicates(intermediates)[i-1]
    ]

def get_score_at_rank_i(intermediates, i):
    return get_predicates_with_scores(intermediates)[
        get_sorted_predicates(intermediates)[i-1]
    ]

def get_rank(intermediates, explanation_predicate):
    return get_sorted_predicates(intermediates).tolist().index(explanation_predicate) + 1

def precision_at_k(intermediates):
    noisy_top_k = set(intermediates['Topk'])
    k = len(noisy_top_k)
    true_top_k = set(get_sorted_predicates(intermediates)[:k])
    precision = len(noisy_top_k & true_top_k) / k
    return precision
    

def error_noise_quantification(intermediates, rho, gamma):
    question_ci = intermediates['QuestionCI']
#     logger.info(f'true question: {es.question.evaluation(es.dataset)}')
#     logger.info(f'question_point: {es.question_point}')
#     logger.info(f'question_ci: {question_ci}')
    groundtruth_ci = intermediates['GroundQuestionCI']
#     logger.info(f'groundtruth_ci: {groundtruth_ci}')
    
    
    percentage_of_missing = 1 - size_of_interval_intersection(
        question_ci, groundtruth_ci) / size_of_interval(groundtruth_ci)
    logger.info(f'percentage_of_missing: {percentage_of_missing}')
    percentage_of_extra = ((size_of_interval(question_ci) - 
        size_of_interval_intersection(
            question_ci, groundtruth_ci)) / intermediates['GroundQuestionPoint'])
    logger.info(f'percentage_of_extra: {percentage_of_extra}')
    error = (percentage_of_missing + percentage_of_extra) / 2
    
#     jac = jaccard_similarity(question_ci, groundtruth_ci)
#     error = 1 - jac
    logger.info(f'noise quantification error: {error}')
    return error

def error_topk_selection(intermediates, k):
    influences = get_predicates_with_influences(intermediates)
    
    true_kth_influence = get_influence_at_rank_i(intermediates, k)
#     logger.info(f'topk true top_k influence: {[get_influence_at_rank_i(es, i+1) for i in range(k)]}')
#     logger.info(f'topk true top_k score: {[get_score_at_rank_i(es, i+1) for i in range(k)]}')
    
    noisy_topk_influences = sorted(
        [influences[explanation_predicate]
        for explanation_predicate in intermediates['Topk']],
        reverse=True
    )
    noisy_topk_scores = sorted(
        [get_predicates_with_scores(intermediates)[explanation_predicate]
        for explanation_predicate in intermediates['Topk']],
        reverse=True
    )
    noisy_kth_influence = noisy_topk_influences[-1]
    logger.info(f'topk noisy top_k influence: {noisy_topk_influences}')
    logger.info(f'topk noisy top_k score: {noisy_topk_scores}')
    
    kth_gap = np.abs(true_kth_influence - noisy_kth_influence)
    #error = kth_gap / np.abs(true_kth_influence)
    error = kth_gap / np.abs(get_influence_at_rank_i(intermediates, 1) - get_influence_at_rank_i(intermediates, 0))
    return error

def error_influence_ci(intermediates):
    errors = []
    for explanation_predicate, ci in zip(
        intermediates['Topk'], 
        intermediates['InfluCI']
    ):
        true_influence = get_predicates_with_influences(intermediates)[
            explanation_predicate
        ]
        logger.info(f'infci true_influence: {true_influence}')
        logger.info(f'infci ci: {ci[0], ci[1]}')
        error = max(
            np.abs(ci[0] - true_influence),
            np.abs(ci[1] - true_influence)
        # ) / np.abs(true_influence)
        ) / np.abs(get_influence_at_rank_i(intermediates, 1) - get_influence_at_rank_i(intermediates, 0))
        errors.append(error)
    error = np.mean(errors)
    return error

def error_rank_ci(intermediates):
    errors = []
    for explanation_predicate, ci in zip(
        intermediates['Topk'], 
        intermediates['RankCI']
    ):
        true_rank = get_rank(intermediates, explanation_predicate)
        logger.info(f'rankci true_rank: {true_rank}')
        logger.info(f'rankci ci: {ci[0], ci[1]}')
        
        true_influence = get_predicates_with_influences(intermediates)[
            explanation_predicate
        ]
        logger.info(f'rankci true_influence: {true_influence}')
        logger.info(f'rankci influence ci: {get_influence_at_rank_i(intermediates, ci[0]), get_influence_at_rank_i(intermediates, ci[1])}')
        logger.info(f'rankci influence range: {get_influence_at_rank_i(intermediates, 1) - get_influence_at_rank_i(intermediates, 0)}')
        error = max(
            np.abs(ci[0] - true_rank),
            np.abs(ci[1] - true_rank)
        ) / len(get_sorted_predicates(intermediates))
        errors.append(error)
    error = np.mean(errors)
    return error

if __name__ == '__main__':
    default = german_default.default
    default = {**run.DEFAULT, **default} 
    setting = default
    hashed = run.hash_setting(setting)
    fprefix = f'./intermediates/{hashed}'
    fname = fprefix + '-0.pkl'
    with open(fname, 'rb') as finp:
        intermediates = pickle.load(finp)
    print(error_noise_quantification(intermediates, setting['rho_query'], setting['gamma']))
    print(error_topk_selection(intermediates, setting['k']))
    print(error_influence_ci(intermediates))
    print(error_rank_ci(intermediates))