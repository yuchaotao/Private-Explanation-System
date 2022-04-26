#!/usr/bin/env python
import run

import pandas as pd

dataset = run.dataset
schema = run.schema
full_attributes = run.full_attributes
default = run.default

controls = [
#     [
#         ('agg', 'CNT')
#     ],
#     [
#         ('agg', 'SUM')
#     ],
#     [
#         ('rho_query', 0.01)
#     ],
#     [
#         ('rho_query', 1)
#     ],
#     [
#         ('rho_topk', 0.1)
#     ],
#     [
#         ('rho_topk', 2)
#     ],
#     [
#         ('rho_influ', 0.1)
#     ],
#     [
#         ('rho_influ', 2)
#     ],
#     [
#         ('rho_rank', 0.1)
#     ],
#     [
#         ('rho_rank', 10)
#     ],
#     [
#         ('gamma', 0.9)
#     ],
#     [
#         ('gamma', 0.99)
#     ],
#     [
#         ('scale', 0.1)
#     ],
#     [
#         ('scale', 0.5)
#     ],
#     [
#         ('split_factor', 0.5)
#     ],
#     [
#         ('split_factor', 0.1)
# #     ],
#     [
#         ('predicate_strategy', '2-way marginal')
#     ],
#     [
#         ('predicate_strategy', '3-way marginal')
#     ]
    [
        ('k', 10)
    ],
    [
        ('k', 20)
    ]
]


def main_experiment(reset = False):
    result_fname = './results_control.csv'
    
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
    
if __name__ == '__main__':
    main_experiment(reset = False)
