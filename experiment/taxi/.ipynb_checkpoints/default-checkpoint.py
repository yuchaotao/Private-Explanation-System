#!/usr/bin/env python
import sys
sys.path.append('../../')

import privex.evaluation.run as run
from privex.components.basic import Schema, Dataset, GroupbyQuery, Question

import pandas as pd

import logging
logger = logging.getLogger(__name__)

# df = pd.read_csv('../../data/taxi/taxi_speed.csv')
# schema = Schema.from_json('../../data/taxi/taxi_speed.json')
df = pd.read_csv('../../data/preprocessed_yellow_tripdata_2019-02.csv')
schema = Schema.from_json('../../data/preprocessed_yellow_tripdata_2019-02.json')

dataset = Dataset(df, schema)
full_attributes = ['PU_Borough', 'PU_Zone', 'PU_Hour', 'PU_WeekDay', 'DO_Borough', 'DO_Zone', 'DO_Hour', 'DO_WeekDay']
default = run.default
default['attr_agg'] = 'tip_amount'
# default['attr_group'] = 'PU_Zone'
# default['group_a'] = 'Financial District North'
# default['group_b'] = 'SoHo'

# default['scale'] = 0.1
# default['attr_agg'] = 'tip_amount'
# default['attr_group'] = 'PU_Borough'
# default['group_a'] = 'Queens'
# default['group_b'] = 'Manhattan'

default['scale'] = 0.1
default['attr_agg'] = 'trip_time'
default['attr_group'] = 'PU_Borough'
default['group_a'] = 'Queens'
default['group_b'] = 'Manhattan'

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
