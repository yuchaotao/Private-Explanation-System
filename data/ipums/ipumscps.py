import sys
sys.path.append('../../')

import json
import pandas as pd
import numpy as np
import xmltodict

from privex.components.basic import Schema, Domain

code_columns =      ['RELATE', 'SEX', 'RACE', 'MARST', 'CITIZEN', 'CLASSWKR', 'EDUC']
post_code_columns = ['RELATE', 'SEX', 'RACE', 'MARST', 'CITIZEN', 'CLASSWKR', 'EDUC', 'OCC']
cat_columns =       ['RELATE', 'SEX', 'RACE', 'MARST', 'CITIZEN', 'CLASSWKR', 'EDUC', 'OCC', 'AGE']
final_columns =     ['MARST', 'OCC', 'RELATE', 'SEX', 'RACE', 'CITIZEN', 'CLASSWKR', 'AGE', 'EDUC', 'INCTOT']

def load_codebook():
    with open('cps_00005.xml', 'r') as file:
        my_xml = file.read()
    codebook = xmltodict.parse(my_xml)
    codebook_dict = {}
    
    for entry in codebook['codeBook']['dataDscr']['var']:
        column = entry['@ID']
        if column in code_columns:
            domain_dict = {int(item['catValu']): item['labl']  for item in entry['catgry']}
            codebook_dict[column] = domain_dict
            
    occ_codebook = pd.read_csv('OCC_codebook.csv', sep='\t')
    codebook_dict['OCC'] = {row.code: row.label for index, row in occ_codebook.iterrows()}
    return codebook_dict

def save_data():
    df = pd.read_csv('cps_00005.csv')
    subdf = df.query('2011 <= YEAR <= 2019 and 0 < INCTOT < 200000').copy()
    subdf['AGE'] = pd.cut(subdf['AGE'], bins=np.linspace(0, 100, 11).astype(int)).astype('str')
    
    codebook_dict = load_codebook()
    
    for col in code_columns:
        subdf[col] = subdf[col].apply(lambda row: codebook_dict[col][row])
        
    subdf[final_columns].to_csv('ipumscps.csv', index=False)
    
def save_schema():
    codebook_dict = load_codebook()
    df = pd.read_csv('ipumscps.csv')
    
    vals_dict = {col: list(codebook_dict[col].values()) for col in post_code_columns}
    vals_dict['AGE'] = [str(x) for x in df['AGE'].unique()]
    
    domains = {}
    for col in cat_columns:
        vals = vals_dict[col]
        vmin = None
        vmax = None
        domain = Domain(col, vmin, vmax, vals)
        domains[col] = domain
        
    domains['INCTOT'] = Domain('INCTOT', 0, 200000, None)
    schema = Schema(domains)
    schema.to_json('ipumscps.json')
    
save_data()
save_schema()