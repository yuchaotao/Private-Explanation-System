import sys
sys.path.append('../')

import json
import pandas as pd

from privex.basic import Schema, Domain

def generate_schema(df):
    '''
    columns = ['PU_Zone', 'PU_Borough', 'PU_Hour', 'PU_Day', 'DO_Zone', 'DO_Borough', 'DO_Hour', 'DO_Day', 'trip_speed']
    '''
    domains = {}
    # Categorical attributes
    cat_columns = ['PU_Zone', 'PU_Borough', 'PU_Hour', 'PU_Day', 'DO_Zone', 'DO_Borough', 'DO_Hour', 'DO_Day']
    for col in cat_columns:
        vals = [str(x) for x in df[col].unique()]
        vmin = None
        vmax = None
        domain = Domain(col, vmin, vmax, vals)
        domains[col] = domain
        
    domains['trip_speed'] = Domain('trip_speed', 0, 80, None)
    schema = Schema(domains)
    return schema

def main():
    taxi_feb_2019_p = pd.read_csv('preprocessed_yellow_tripdata_2019-02.csv')
    schema = generate_schema(taxi_feb_2019_p)
    schema.to_json('preprocessed_yellow_tripdata_2019-02.json')
    
if __name__ == '__main__':
    main()