import pandas as pd
import numpy as np

def preprocess_table(df):
    tpickup = pd.to_datetime(df['tpep_pickup_datetime'])
    tdropoff = pd.to_datetime(df['tpep_dropoff_datetime'])
    df['trip_time'] = (
        (
            tdropoff
            - 
            tpickup
        )
        .dt.total_seconds().astype(int)
    )
    df['trip_speed'] = np.clip(
        df['trip_distance'] / df['trip_time'] * 3600,
        0,
        80
    )
    df['PU_Hour'] = tpickup.dt.hour
    df['PU_Day'] = tpickup.dt.day
    df['DO_Hour'] = tdropoff.dt.hour
    df['DO_Day'] = tdropoff.dt.day
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
    columns = ['PU_LocationID', 'PU_Hour', 'PU_Day', 'DO_LocationID', 'DO_Hour', 'DO_Day', 'trip_speed']
    df = df[columns]

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
    columns = ['PU_Zone', 'PU_Borough', 'PU_Hour', 'PU_Day', 'DO_Zone', 'DO_Borough', 'DO_Hour', 'DO_Day', 'trip_speed']
    df = df[columns]
    df = df.sample(frac=1)
    return df

def main():
    taxi_feb_2019 = pd.read_csv('yellow_tripdata_2019-02.csv')
    taxi_feb_2019_p = preprocess_table(taxi_feb_2019)
    taxi_feb_2019_p.to_csv('preprocessed_yellow_tripdata_2019-02.csv', index=False)
    
if __name__ == '__main__':
    main()