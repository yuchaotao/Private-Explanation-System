#!/usr/bin/env python
import sys
sys.path.append('../../')

import privex.evaluation.run as run
from privex.components.basic import Schema, Dataset, GroupbyQuery, Question

import pandas as pd

import logging
logger = logging.getLogger(__name__)

df = pd.read_csv('../../data/credit/german.csv')
schema = Schema.from_json('../../data/credit/german.json')

dataset = Dataset(df, schema)
full_attributes = ['checking-account', 'duration', 'credit-history', 'purpose', 'credit-amount', 'saving-account', 'employment', 'installment-rate', 'sex-marst', 'debtors', 'residence', 'property', 'age', 'installment-plan', 'housing', 'existing-credits', 'job', 'maintenance-people', 'telephone', 'foreign-worker']
default = run.default
default['attr_agg'] = 'good-credit'
default['attr_group'] = 'checking-account'
default['group_a'] = 'no checking account'
default['group_b'] = 'no balance or debit'

for option in ['rho_query', 'rho_topk', 'rho_influ', 'rho_rank']:
    default[option] = default[option] * 10000

default['reps'] = 1

def main_experiment(reset = False):
    result_fname = './results_default.csv'
    
    if reset:
        f = open(result_fname, 'w')
        f.close()
        result = None
    else:
        result = pd.read_csv(result_fname)
        
    setting = default.copy()
    print(list(dataset.schema.domains.keys()))
    reports = run.run(
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
        reps =                   setting['reps']
    )
    
    new_result = pd.DataFrame(reports)
    if result is None:
        result = new_result
    else:
        result = pd.concat([result, new_result])
        
    result.to_csv(result_fname, index=False)
    
if __name__ == '__main__':
    main_experiment(reset = True)
