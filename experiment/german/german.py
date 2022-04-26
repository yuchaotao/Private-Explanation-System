#!/usr/bin/env python
import sys
sys.path.append('../../')

import privex.evaluation.run as run
from privex.components.basic import Schema, Dataset, GroupbyQuery, Question

import pandas as pd

import logging
logger = logging.getLogger(__name__)

df = pd.read_csv('../../data/german/synthetic_german.csv')
schema = Schema.from_json('../../data/german/german.json')

dataset = Dataset(df, schema)
full_attributes = ['status', 'duration', 'credit-history', 'purpose', 'credit-amount', 'saving-account', 'employment', 'installment-rate', 'sex-marst', 'other-debtors', 'residence', 'property', 'age', 'other-installment-plans', 'housing', 'existing-credits', 'job', 'people-liable', 'telephone', 'foreign-worker']
default = run.default

default['attr_agg'] = 'good-credit'
default['attr_group'] = 'status'
default['group_a'] = '... < 0 DM'
default['group_b'] = 'no checking account'

# for option in ['rho_query', 'rho_topk', 'rho_influ', 'rho_rank']:
#     default[option] = default[option] * 1

# default['reps'] = 1
# default['scale'] = 0.1

def main_experiment(controls = [], result_fname = './results.csv', reset = False):
    if reset:
        f = open(result_fname, 'w')
        f.close()
        result = None
    else:
        result = pd.read_csv(result_fname)
        
    new_result = []
    for setting_change in controls:
        setting = default.copy()
        for key, value in setting_change: 
            setting[key] = value
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
        new_result += reports
        print(reports)
    
    new_result = pd.DataFrame(new_result)
    if result is None:
        result = new_result
    else:
        result = pd.concat([result, new_result])
        
    result.to_csv(result_fname, index=False)
    
def exp_default():
    controls = [
        []
    ]
    main_experiment(controls = controls, result_fname = './results_default.csv', reset = True)
    
def exp_predicate():
    controls = [
        [
            ('predicate_strategy', '2-way marginal')
        ],
        [
            ('predicate_strategy', '3-way marginal')
        ]
    ]
    main_experiment(controls = controls, result_fname = './results_predicate.csv', reset = True)
    
def exp_controls():
    controls = [
        [
            ('agg', 'CNT')
        ],
        [
            ('agg', 'SUM')
        ],
        [
            ('rho_query', 0.01)
        ],
        [
            ('rho_query', 1)
        ],
        [
            ('rho_topk', 0.1)
        ],
        [
            ('rho_topk', 2)
        ],
        [
            ('rho_influ', 0.1)
        ],
        [
            ('rho_influ', 2)
        ],
        [
            ('rho_rank', 0.1)
        ],
        [
            ('rho_rank', 10)
        ],
        [
            ('gamma', 0.9)
        ],
        [
            ('gamma', 0.99)
        ],
        [
            ('scale', 0.1)
        ],
        [
            ('scale', 0.5)
        ],
        [
            ('split_factor', 0.5)
        ],
        [
            ('split_factor', 0.1)
        ],
        [
            ('k', 10)
        ],
        [
            ('k', 20)
        ]
    ]
    main_experiment(controls = controls, result_fname = './results_controls.csv', reset = True)

def exp_questions():
    controls = [
        [
            ('attr_group', 'status'),
            ('group_a', '... >= 200 DM / salary for at least 1 year'),
            ('group_b', '0<= ... < 200 DM')
        ],
        [
            ('attr_group', 'duration'),
            ('group_a', '< 1 yr'),
            ('group_b', '1 <= ... < 4 yrs')
        ],
        [
            ('attr_group', 'duration'),
            ('group_a', '1 <= ... < 4 yrs'),
            ('group_b', '4 <= ... < 7 yrs')
        ],
        [
            ('attr_group', 'credit-history'),
            ('group_a',  'all credits at this bank paid back duly'),
            ('group_b',  'no credits taken/all credits paid back duly')
        ],
        [
            ('attr_group', 'credit-history'),
            ('group_a',  'no credits taken/all credits paid back duly'),
            ('group_b',  'delay in paying off in the past')
        ],
        [
            ('attr_group', 'purpose'),
            ('group_a', 'car (new)'),
            ('group_b', 'car (used)')
        ],
        [
            ('attr_group', 'purpose'),
            ('group_a', 'vacation'),
            ('group_b', 'business')
        ],
        [
            ('attr_group', 'purpose'),
            ('group_a', 'furniture/equipment'),
            ('group_b', 'domestic appliances')
        ],
        [
            ('attr_group', 'purpose'),
            ('group_a', 'retraining'),
            ('group_b', 'repairs')
        ],
        [
            ('attr_group', 'credit-amount'),
            ('group_a', '(2500, 5000]'),
            ('group_b', '(500, 2500]')
        ],
        [
            ('attr_group', 'credit-amount'),
            ('group_a', '(2500, 5000]'),
            ('group_b', '(5000, 10000]')
        ],
        [
            ('attr_group', 'saving-account'),
            ('group_a', '... <  100 DM'),
            ('group_b', 'unknown/no savings account')
        ],
        [
            ('attr_group', 'saving-account'),
            ('group_a', '... >= 1000 DM'),
            ('group_b', '... <  100 DM')
        ],
        [
            ('attr_group', 'employment'),
            ('group_a', '4 <= ... < 7 yrs'),
            ('group_b', '>= 7 yrs')
        ],
        [
            ('attr_group', 'employment'),
            ('group_a', '4 <= ... < 7 yrs'),
            ('group_b', '1 <= ... < 4 yrs')
        ],
        [
            ('attr_group', 'installment-rate'),
            ('group_a', '25% <= ... < 35%'),
            ('group_b', '20% <= ... < 25%')
        ],
        [
            ('attr_group', 'installment-rate'),
            ('group_a', '20% <= ... < 25%'),
            ('group_b', '< 20%')
        ],
        [
            ('attr_group', 'sex-marst'),
            ('group_a', 'female : single'),
            ('group_b', 'female : non-single or male : single')
        ],
        [
            ('attr_group', 'sex-marst'),
            ('group_a', 'male : married/widowed'),
            ('group_b', 'male : divorced/separated')
        ],
        [ # reasonable
            ('attr_group', 'other-debtors'),
            ('group_a', 'guarantor'),
            ('group_b', 'none')
        ],
        [
            ('attr_group', 'other-debtors'),
            ('group_a', 'none'),
            ('group_b', 'co-applicant')
        ],
        [ # intersting
            ('attr_group', 'residence'),
            ('group_a', '< 1 yr'),
            ('group_b', '>= 7 yrs')
        ],
        [
            ('attr_group', 'residence'),
            ('group_a', '4 <= ... < 7 yrs'),
            ('group_b', '1 <= ... < 4 yrs')
        ],
        [ # interesting
            ('attr_group', 'property'),
            ('group_a', 'unknown / no property'),
            ('group_b', 'car or other')
        ],
        [
            ('attr_group', 'property'),
            ('group_a', 'unknown / no property'),
            ('group_b', 'real estate')
        ],
        [ # interesting
            ('attr_group', 'age'),
            ('group_a', '(40, 50]'),
            ('group_b', '(50, 60]')
        ],
        [
            ('attr_group', 'age'),
            ('group_a', '(60, 70]'),
            ('group_b', '(50, 60]')
        ],
        [
            ('attr_group', 'other-installment-plans'),
            ('group_a', 'none'),
            ('group_b', 'stores')
        ],
        [
            ('attr_group', 'other-installment-plans'),
            ('group_a', 'stores'),
            ('group_b', 'bank')
        ],
        [ # maybe interesting
            ('attr_group', 'housing'),
            ('group_a', 'rent'),
            ('group_b', 'own')
        ],
        [
            ('attr_group', 'housing'),
            ('group_a', 'rent'),
            ('group_b', 'for free')
        ],
        [
            ('attr_group', 'existing-credits'),
            ('group_a', '1'),
            ('group_b', '>= 6')
        ],
        [
            ('attr_group', 'existing-credits'),
            ('group_a', '4-5'),
            ('group_b', '>= 6')
        ],
        [
            ('attr_group', 'people-liable'),
            ('group_a', '3 or more'),
            ('group_b', '0 to 2')
        ],
        [
            ('attr_group', 'telephone'),
            ('group_a', 'yes (under customer name)'),
            ('group_b', 'no')
        ],
        [ # interesting
            ('attr_group', 'foreign-worker'),
            ('group_a', 'yes'),
            ('group_b', 'no')
        ]
    ]
    main_experiment(controls = controls, result_fname = './results_questions.csv', reset = True)
    
if __name__ == '__main__':
    exp_default()