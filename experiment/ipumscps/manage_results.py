#!/usr/bin/env python
import pandas as pd

import exp

default = exp.default

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
        ('attr_group', 'SEX'),
        ('group_a', 'Male'),
        ('group_b', 'Female')
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

control_to_record_mapping = {
    'attr_group': 'Agb',
    'group_a': 'g1',
    'group_b': 'g2'
}

def extract_parameter_exp():
    results_controls = pd.read_csv('results_control.csv')
    results_default = pd.read_csv('results.csv').query(f'Agb == "SEX"')
    for param in parameters:
        results_specific = results_controls.query(f'`{param}` != "{default[param]}"')
        to_extract = pd.concat([results_default, results_specific])
        to_extract['data'] = 'IPUMS'
        to_extract.to_csv(f'./results/{param}.csv', index=False)
        
def extract_questions_exp():
    results_questions = pd.read_csv('results_questions.csv')
    results_default = pd.read_csv('results.csv').query(f'Agb == "SEX"')
    results_questions = pd.concat([results_default, results_questions])
    m = control_to_record_mapping
    
    to_extract = []
    for i, control in enumerate(questions):
        query = ' and '.join(f'(`{m[key]}` == "{val}")' for key, val in control)
        df = results_questions.query(query).copy()
        df['index'] = i+1
        df['data'] = 'IPUMS'
        to_extract.append(df)
        
    to_extract = pd.concat(to_extract)
    to_extract.to_csv(f'./results/questions.csv', index=False)
    
        
if __name__ == '__main__':
    extract_parameter_exp()
    extract_questions_exp()