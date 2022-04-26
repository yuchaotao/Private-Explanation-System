import pandas as pd
import numpy as np
from tqdm import tqdm

import os

import sys
sys.path.append('../../')
from privex.components.basic import Schema, Domain

def preprocess_table(df, dayrange=None):
    tpickup = pd.to_datetime(df['tpep_pickup_datetime'])
    tdropoff = pd.to_datetime(df['tpep_dropoff_datetime'])
    
    if dayrange is not None:
        df = df[tpickup.between(*dayrange)].copy()
    
    df['trip_time'] = (
        (
            tdropoff
            - 
            tpickup
        )
        .dt.total_seconds().astype(int)
    )
#     df['trip_speed'] = np.clip(
#         df['trip_distance'] / df['trip_time'] * 3600,
#         0,
#         80
#     )
    df['trip_speed'] = df['trip_distance'] / df['trip_time'] * 3600
    df = df.query('0 < trip_speed < 40').copy()
    hour_intervals = [0, 7, 10, 14, 17, 20, 24]
    df['PU_Hour'] = pd.cut(tpickup.dt.hour, bins=hour_intervals, right=False)
    df['PU_Day'] = tpickup.dt.day
    df['PU_WeekDay'] = tpickup.dt.weekday
    df['DO_Hour'] = pd.cut(tdropoff.dt.hour, bins=hour_intervals, right=False)
    df['DO_Day'] = tdropoff.dt.day
    df['DO_WeekDay'] = tdropoff.dt.weekday
    df['PU_LocationID'] = df['PULocationID']
    df['DO_LocationID'] = df['DOLocationID']
    '''
    columns = ['passenger_count', 'trip_distance', 
               'PULocationID', 'DOLocationID',
               'payment_type', 'fare_amount', 'extra', 
               'mta_tax', 'tip_amount', 'tolls_amount', 
               'improvement_surcharge', 'total_amount',
               'congestion_surcharge', 'trip_time',
               'pu_hour', 'pu_day', 'do_hour', 'do_day']
    '''
#     columns = ['PU_LocationID', 'PU_Hour', 'PU_WeekDay', 'DO_LocationID', 'DO_Hour', 'DO_WeekDay', 'trip_speed']
#     df = df[columns]

    taxi_zone_lookup = pd.read_csv('taxi+_zone_lookup.csv')
    df = df.merge(
        taxi_zone_lookup.rename(
            columns = {
                'LocationID': 'PU_LocationID',
                'Borough': 'PU_Borough',
                'Zone': 'PU_Zone',
                'service_zone': 'PU_service_zone'
            }
        ), 
        on='PU_LocationID'
    ).merge(
        taxi_zone_lookup.rename(
            columns = {
                'LocationID': 'DO_LocationID',
                'Borough': 'DO_Borough',
                'Zone': 'DO_Zone',
                'service_zone': 'DOservice_zone'
            }
        ), 
        on='DO_LocationID'
    )
    if dayrange is None:
        columns = ['PU_Zone', 'PU_Borough', 'PU_Hour', 'PU_WeekDay', 'DO_Zone', 'DO_Borough', 'DO_Hour', 'DO_WeekDay', 'trip_speed']
    else:
        columns = ['PU_Zone', 'PU_Borough', 'PU_Hour', 'DO_Zone', 'DO_Borough', 'DO_Hour', 'trip_speed']
    df = df[columns]
    df = df.sample(frac=1)
    return df

def extract_imbalance():
    extracted = []
    for month in tqdm(["%.2d" % (i+1) for i in range(12)]):
        taxi_data = pd.read_csv(f'yellow_tripdata_2019-{month}.csv')
        taxi_data = preprocess_table(taxi_data)
        to_extract = taxi_data.query('(PU_Borough == "Brooklyn" and DO_Borough == "Queens") or (PU_Borough == "Queens" and DO_Borough == "Brooklyn")')
        extracted.append(to_extract)
        if month == '02':
            break
    extracted = pd.concat(extracted)
    extracted.to_csv('taxi_imbalance.csv', index=False)
    
def extract_speed():
    fname = 'taxi_speed.csv'

#     extracted = []
    for month in tqdm(["%.2d" % (i+1) for i in range(12)]):
        taxi_data = pd.read_csv(f'yellow_tripdata_2019-{month}.csv')
        taxi_data = preprocess_table(taxi_data)
        to_extract = taxi_data.query('PU_Zone == "Financial District North" or PU_Zone == "SoHo"')
#         extracted.append(to_extract)
        
        # if file does not exist write header 
        if not os.path.isfile('filename.csv'):
            to_extract.to_csv(fname, index=False)
        else: # else it exists so append without writing the header
            to_extract.to_csv(fname, mode='a', header=False, index=False)
            
#         if month == '02':
#             break
#     extracted = pd.concat(extracted)
#     extracted.to_csv('taxi_speed.csv', index=False)
    
    schema = generate_schema(extracted)
    schema.to_json('preprocessed_yellow_tripdata_2019-02.json')
    
    
def generate_schema(df):
    '''
    columns = ['PU_Zone', 'PU_Borough', 'PU_Hour', 'PU_Day', 'DO_Zone', 'DO_Borough', 'DO_Hour', 'DO_Day', 'trip_speed']
    '''
    domains = {}
    # Categorical attributes
    cat_columns = ['PU_Zone', 'PU_Borough', 'PU_Hour', 'PU_WeekDay', 'DO_Zone', 'DO_Borough', 'DO_Hour', 'DO_WeekDay']
    for col in cat_columns:
        vals = [str(x) for x in df[col].unique()]
        vmin = None
        vmax = None
        domain = Domain(col, vmin, vmax, vals)
        domains[col] = domain
        
    domains['trip_speed'] = Domain('trip_speed', 0, 40, None)
    schema = Schema(domains)
    return schema

def main():
    taxi_feb_2019 = pd.read_csv('yellow_tripdata_2019-02.csv')
    
#     taxi_feb_2019_p = preprocess_table(taxi_feb_2019, oneday=None)
#     taxi_feb_2019_p.to_csv('preprocessed_yellow_tripdata_2019-02.csv', index=False)
    
    taxi_feb_2019_p = preprocess_table(taxi_feb_2019, dayrange=('2019-02-01', '2019-02-02') )
    taxi_feb_2019_p.to_csv('preprocessed_yellow_tripdata_2019-02-01.csv', index=False)
    
if __name__ == '__main__':
    extract_imbalance()
    extract_speed()
