import sys
sys.path.append('../../')
sys.path.append('../')

import german.default as german_default
import german.questions as german_questions
import german.parameters as german_parameters
import german.valid as german_valid

import ipums.default as ipums_default
import ipums.questions as ipums_questions
import ipums.parameters as ipums_parameters
import ipums.valid as ipums_valid

from privex.components.basic import Schema, Dataset, GroupbyQuery, Question
from privex.components.utils import generate_explanation_predicates
from privex.framework.solution import ExplanationSession

import pandas as pd
import numpy as np
import hashlib
import json
import glob

import logging
logger = logging.getLogger(__name__)

DEFAULT = {
    'scale': 1.0,
    'rho_query': 0.1,
    'agg': 'AVG',
    'rho_topk': 0.5,
    'rho_influ': 0.5,
    'rho_rank': 1.0,
    'gamma': 0.95,
    'predicate_strategy': '1-way marginal',
    'k': 5,
    'split_factor': 0.9,
    'reps': 10
}

def hash_setting(setting):
    dhash = hashlib.md5()
#     encoded = frozenset(setting.items())
#     hashed = hash(encoded)
    encoded = json.dumps(setting, sort_keys=True).encode()
    dhash.update(encoded)
    hashed = dhash.hexdigest()
    return hashed

def run(dataset, scale, full_attributes, rho_query, agg, attr_agg, attr_group, group_a, group_b, rho_topk, rho_influ, rho_rank, gamma, predicate_strategy, k, split_factor, reps, fprefix, topk_only):
    rho_expl = rho_topk + rho_influ + rho_rank
    attributes = [attr for attr in full_attributes if attr != attr_group]
    predicates = generate_explanation_predicates(attributes, dataset.schema, predicate_strategy)
    dataset = Dataset(dataset.df.sample(frac=scale), dataset.schema)
    es = ExplanationSession(dataset, gamma, predicates)
    logger.info(f'loaded dataset with {len(dataset.df)} rows and columns {list(dataset.schema.domains.keys())}.')
    
    # Phase 1
    groupby_query = GroupbyQuery(
        agg = agg,
        attr_agg = attr_agg,
        predicate = None,
        attr_group = attr_group,
        schema = dataset.schema
    )
    es.phase_1_submit_query(groupby_query, rho_query)
    
    # Phase 2
    question = Question.from_group_comparison(groupby_query, (group_a,), (group_b,))
    es.phase_2_submit_question(question)
    es.phase_2_prepare_question_ci()
    
    # Phase 3
    es.phase_3_submit_explanation_request()
    es.phase_3_prepare_explanation(k, {'rho_topk': rho_topk, 'rho_influ': rho_influ, 'rho_rank': rho_rank}, split_factor, topk_only)
    
    with open(f'{fprefix}-0.pkl', 'wb') as outp:
        es.store_important_intermediates(outp)
    
    for i in range(1, reps):
        # Phase 1
        es.phase_1_submit_query(groupby_query, rho_query)
        
        # Phase 2
        es.phase_2_prepare_question_ci()
        
        # Phase 3
        es.phase_3_prepare_explanation(k, {'rho_topk': rho_topk, 'rho_influ': rho_influ, 'rho_rank': rho_rank}, split_factor, topk_only)
        
        with open(f'{fprefix}-{i}.pkl', 'wb') as outp:
            es.store_important_intermediates(outp)


def main_experiment(default, controls = [], reset=False):
    df = pd.read_csv(default['dataset'])
    schema = Schema.from_json(default['schema'])
    dataset = Dataset(df, schema)
    full_attributes = default['full_attributes']
    
    default = {**DEFAULT, **default} 
#     print(default)
        
    new_result = []
    for setting_change in controls:
        setting = default.copy()
        for key, value in setting_change: 
            setting[key] = value
        hashed = hash_setting(setting)
        topk_only = setting['topk_only'] if 'topk_only' in setting else False
        fprefix = f'./intermediates/{hashed}'
        if len(glob.glob(fprefix + '*')) < setting['reps'] or reset == True:
            print(setting)
            print(fprefix)
            run(
                dataset =                dataset,
                scale =                  setting['scale'],
                full_attributes =        full_attributes,
                rho_query =              setting['rho_query'],
                agg =                    setting['agg'],
                attr_agg =               setting['attr_agg'],
                attr_group =             setting['attr_group'],
                group_a =                setting['group_a'],
                group_b =                setting['group_b'],
                rho_topk =               setting['rho_topk'],
                rho_influ =              setting['rho_influ'],
                rho_rank =               setting['rho_rank'],
                gamma =                  setting['gamma'],
                predicate_strategy =     setting['predicate_strategy'],
                k =                      setting['k'],
                split_factor =           setting['split_factor'],
                reps =                   setting['reps'],
                fprefix =                fprefix,
                topk_only =              topk_only
            )

default_dict = {
    'german': german_default,
    'ipums': ipums_default
}

questions_dict = {
    'german': german_questions,
    'ipums': ipums_questions
}

parameters_dict = {
    'german': german_parameters,
    'ipums': ipums_parameters
}


    
if __name__ == '__main__':
#     controls = [
#         []
#     ]
#     main_experiment(default = german_default.default, controls = controls)
    
#     main_experiment(default = german_default.default, controls = [[]])
#     main_experiment(default = german_default.default, controls = german_questions.controls)
#     main_experiment(default = german_default.default, controls = german_parameters.controls)
    
#     main_experiment(default = ipums_default.default, controls = [[]])
#     main_experiment(default = ipums_default.default, controls = ipums_questions.controls)
#     main_experiment(default = ipums_default.default, controls = ipums_parameters.controls)

#     for default in [ipums_default.default, german_default.default]:
#         controls = []
#         for rho in [0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1, 2, 5, 10]:
#             controls.append(
#                 [
#                     ('k', -1), ('rho_topk', rho), ('topk_only', True)
#                 ]
#             )
#             controls.append(
#                 [
#                     ('k', -1), ('rho_topk', rho), 
#                     ('predicate_strategy', '2-way marginal'), ('topk_only', True)
#                 ]
#             )
#         for predicate_strategy in ['1-way marginal', '2-way marginal', '3-way marginal']:
#             controls.append(
#                 [
#                     ('k', -1),
#                     ('predicate_strategy', predicate_strategy), ('topk_only', True)
#                 ]
#             )
#         main_experiment(default = default, controls = controls)
        
#     main_experiment(default = ipums_default.default, controls = [[('scale', 0.1)]])
#     print(german_parameters.controls)

#     for default, valid, invalid in zip(
#         [ipums_default.default, german_default.default], 
#         [ipums_valid.valid, german_valid.valid],
#         [ipums_valid.invalid, german_valid.invalid]
#     ):
#         controls = []
#         for rho in [0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1, 2, 5, 10]:
#             controls += [setting_change + [('rho_query', rho)] for setting_change in valid]
#             controls += [setting_change + [('rho_query', rho)] for setting_change in invalid]
#         main_experiment(default = default, controls = controls)

#     for default, valid, invalid in zip(
#         [ipums_default.default, german_default.default], 
#         [ipums_valid.valid, german_valid.valid],
#         [ipums_valid.invalid, german_valid.invalid]
#     ):
#         controls = []
#         for rho in [0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1, 2, 5, 10]:
#             controls += [setting_change + [('k', -1), ('rho_topk', rho), ('topk_only', True)] for setting_change in valid]
#             controls += [setting_change + [('k', -1), ('rho_topk', rho), ('topk_only', True)] for setting_change in invalid]
#         main_experiment(default = default, controls = controls)

    for default, questions in zip(
        [ipums_default.default, german_default.default], 
        [ipums_valid.questions, german_valid.questions],
    ):
        controls = []
        for rho in [0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1, 2, 5, 10]:
            controls += [setting_change + [('rho_influ', rho)] for setting_change in questions]
#             controls += [setting_change + [('rho_rank', rho)] for setting_change in questions]
        for gamma in np.r_[np.linspace(0.1, 0.9, 9), [0.95, 0.99]]:
            controls += [setting_change + [('gamma', gamma)] for setting_change in questions]
        main_experiment(default = default, controls = controls, reset=True) 

#     for default, questions in zip(
#         [ipums_default.default, german_default.default], 
#         [ipums_valid.questions, german_valid.questions],
#     ):
#         controls = []
# #         for k in [3, 4, 5, 6, 7, 8, 9, 10, 15, 20]:
#         for k in [5]:
#             controls += [setting_change + [('k', k)] for setting_change in questions]
#         main_experiment(default = default, controls = controls, reset=True) 

#     for default, valid, invalid in zip(
#         [ipums_default.default, german_default.default], 
#         [ipums_valid.valid, german_valid.valid],
#         [ipums_valid.invalid, german_valid.invalid]
#     ):
#         controls = []
#         for agg in ['CNT', 'SUM']:
#             controls += [setting_change + [('agg', agg)] for setting_change in valid]
#             controls += [setting_change + [('agg', agg)] for setting_change in invalid]
#         main_experiment(default = default, controls = controls)


#     for default, valid, invalid in zip(
#         [ipums_default.default, german_default.default], 
#         [ipums_valid.valid, german_valid.valid],
#         [ipums_valid.invalid, german_valid.invalid]
#     ):
#         controls = []
#         for q_setting_change in valid + invalid:
#             for rho in [0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1, 2, 5, 10]:
#                 controls.append(
#                     [
#                         ('rho_topk', rho), ('topk_only', True),
#                     ] + q_setting_change
#                 )
#             for k in [3, 4, 5, 6, 7, 8, 9, 10, 15, 20, 50]:
#                 controls.append(
#                     [
#                         ('k', k), ('topk_only', True),
#                     ] + q_setting_change
#                 )
#         main_experiment(default = default, controls = controls)