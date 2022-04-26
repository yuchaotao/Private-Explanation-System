#!/usr/bin/env python
import sys
sys.path.append('../../')

import privex.evaluation.run as run
from privex.components.basic import Schema, Dataset, GroupbyQuery, Question

import pandas as pd

import logging
logger = logging.getLogger(__name__)

df = pd.read_csv('../../data/ipums/ipumscps.csv')
schema = Schema.from_json('../../data/ipums/ipumscps.json')

dataset = Dataset(df, schema)
full_attributes = ['RELATE', 'SEX', 'MARST', 'RACE', 'CITIZEN', 'CLASSWKR', 'EDUC']
default = run.default

default['attr_agg'] = 'INCTOT'
default['attr_group'] = 'SEX'
default['group_a'] = 'Male'
default['group_b'] = 'Female'

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

def exp_questions():
    controls = [
        [
            ('attr_group', 'RELATE'),
            ('group_a', 'Spouse'),
            ('group_b', 'Head/householder')
        ],
        [
            ('attr_group', 'RELATE'),
            ('group_a', 'Spouse'),
            ('group_b', 'Unmarried partner')
        ],
        [
            ('attr_group', 'RELATE'),
            ('group_a', 'Head/householder'),
            ('group_b', 'Child')
        ],
        [
            ('attr_group', 'RELATE'),
            ('group_a', 'Head/householder'),
            ('group_b', 'Parent')
        ],
        [
            ('attr_group', 'MARST'),
            ('group_a', 'Married, spouse present'),
            ('group_b', 'Never married/single')
        ],
        [
            ('attr_group', 'MARST'),
            ('group_a', 'Divorced'),
            ('group_b', 'Never married/single')
        ],
        [
            ('attr_group', 'RACE'),
            ('group_a', 'White'),
            ('group_b', 'Black')
        ],
        [
            ('attr_group', 'RACE'),
            ('group_a', 'Asian only'),
            ('group_b', 'White')
        ],
        [
            ('attr_group', 'CITIZEN'),
            ('group_a', 'Born in U.S'),
            ('group_b', 'Not a citizen')
        ],
        [
            ('attr_group', 'CITIZEN'),
            ('group_a', 'Naturalized citizen'),
            ('group_b', 'Born in U.S')
        ],
        [
            ('attr_group', 'CLASSWKR'),
            ('group_a', 'Wage/salary, private'),
            ('group_b', 'Self-employed, not incorporated')
        ],
        [
            ('attr_group', 'CLASSWKR'),
            ('group_a', 'Federal government employee'),
            ('group_b', 'State government employee')
        ],
        [
            ('attr_group', 'AGE'),
            ('group_a', '(40, 50]'),
            ('group_b', '(30, 40]')
        ],
        [
            ('attr_group', 'AGE'),
            ('group_a', '(60, 70]'),
            ('group_b', '(20, 30]')
        ],
        [
            ('attr_group', 'EDUC'),
            ('group_a', "Bachelor's degree"),
            ('group_b', 'High school diploma or equivalent')
        ],
        [
            ('attr_group', 'EDUC'),
            ('group_a', "Master's degree"),
            ('group_b', "Bachelor's degree")
        ]
    ]
    main_experiment(controls = controls, result_fname = './results_questions.csv', reset = True)
    
if __name__ == '__main__':
    exp_questions()