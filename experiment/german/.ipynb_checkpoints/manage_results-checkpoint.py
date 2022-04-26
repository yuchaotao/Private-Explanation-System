#!/usr/bin/env python
import pandas as pd

import german

default = german.default

parameters = [
    'agg',
    'rho_query',
    'rho_topk',
    'rho_influ',
    'rho_rank',
    'gamma',
    'scale',
    'split_factor',
    'k',
    'predicate_strategy'
]

questions = [
    [
        ('attr_group', 'status'),
        ('group_a', '... < 0 DM'),
        ('group_b', 'no checking account')
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
]

control_to_record_mapping = {
    'attr_group': 'Agb',
    'group_a': 'g1',
    'group_b': 'g2'
}

def extract_parameter_exp():
    results_controls = pd.read_csv('results_controls.csv')
    results_predicate = pd.read_csv('results_predicate.csv')
    results_controls = pd.concat([results_controls, results_predicate])
    results_default = pd.read_csv('results_default.csv')
    for param in parameters:
        results_specific = results_controls.query(f'`{param}` != "{default[param]}"')
        to_extract = pd.concat([results_default, results_specific])
        to_extract['data'] = 'German'
        to_extract.to_csv(f'./results/{param}.csv', index=False)
        
def extract_questions_exp():
    results_questions = pd.read_csv('results_questions.csv')
    results_default = pd.read_csv('results_default.csv')
    results_questions = pd.concat([results_default, results_questions])
    m = control_to_record_mapping
    
    to_extract = []
    for i, control in enumerate(questions):
        query = ' and '.join(f'(`{m[key]}` == "{val}")' for key, val in control)
        df = results_questions.query(query).copy()
        df['index'] = i+1
        df['data'] = 'German'
        to_extract.append(df)
        
    to_extract = pd.concat(to_extract)
    to_extract.to_csv(f'./results/questions.csv', index=False)
        
if __name__ == '__main__':
    extract_parameter_exp()
    extract_questions_exp()