import sys
sys.path.append('../')

import json
import pandas as pd
import numpy as np
from sklearn.datasets import fetch_openml

from privex.basic import Schema, Domain

def save_data():
    adult = fetch_openml(name='adult', version=2)
    df = adult['frame'].copy()
    df['high_income'] = df['class'].apply(lambda row: 1 if row == '>50K' else 0)
    df['age'] = pd.cut(df['age'], bins=np.linspace(0, 100, 11).astype(int)).astype('str')
    df.to_csv('adult.csv', index=False)

def save_schema():
    '''
    ['age', 'workclass', 'fnlwgt', 'education', 'education-num', 'marital-status', 'occupation', 'relationship', 'race', 'sex', 'capital-gain', 'capital-loss', 'hours-per-week', 'native-country', 'class', 'high_income']
    '''
    df = pd.read_csv('adult.csv')
    domains = {}
    # Numerical attributes
    num_columns = ['fnlwgt', 'capital-gain', 'capital-loss', 'high_income']
    # Categorical attributes
    cat_columns = ['age', 'workclass', 'education', 'education-num', 'marital-status', 'occupation', 'relationship', 'race', 'sex', 'hours-per-week', 'native-country', 'class']
    for col in cat_columns:
        vals = [str(x) for x in df[col].unique()]
        vmin = None
        vmax = None
        domain = Domain(col, vmin, vmax, vals)
        domains[col] = domain
    for col in num_columns:
        vals = None
        vmin = df[col].min().item()
        vmax = df[col].max().item()
        domain = Domain(col, vmin, vmax, vals)
        domains[col] = domain
        
    schema = Schema(domains)
    schema.to_json('adult.json')
    
save_data()
save_schema()

