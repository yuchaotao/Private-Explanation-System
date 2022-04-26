#!/usr/bin/env python

import sys
sys.path.append('../../')
from privex.components.basic import Schema, Domain

import pandas as pd
import numpy as np


'''
    Parse the codebook
'''

codebook = open('parse_code.txt', 'r').readlines()
attrs = []
cat_domains = dict()
cat_attrs = []
num_attrs = []

i = 0
while i < len(codebook):
    line = codebook[i]
    attr, atype, size = line.strip().split(' ')
    size = int(size)
    if atype == 'cat':
        domain_dict = {}
        for domain_line in codebook[i+1:i+1+size]:
            domain_src, domain_dst = domain_line.strip().split('@')
            domain_dict[domain_src] = domain_dst
        cat_domains[attr] = domain_dict
        cat_attrs.append(attr)
    else:
        num_attrs.append(attr)
    attrs.append(attr)
    i += size + 1

# print(attrs)
# print(cat_attrs)
# print(num_attrs)
# print(cat_domains)

print(attrs)
print(cat_attrs)
print(num_attrs)


'''
    Transform the dataset
'''
dtype = {cat_attr: str for cat_attr in cat_attrs}

df = pd.read_csv('german.data', names=attrs, dtype = dtype, sep=' ')
for attr in cat_attrs:
    df[attr] = df[attr].apply(lambda row: cat_domains[attr][row])
    

bins = {
    'duration': np.arange(6)*12,
    'credit-amount': [0, 500, 2500, 5000, 10000, np.inf],
    'age': np.arange(9)*10
}
I = bins['credit-amount']
labels = {
    'duration': ['1 year'] + [f'{i} years' for i in range(2,6)],
    'credit-amount':  [f'({I[i]}, {I[i+1]}]' for i in range(4)] + ['>10000'],
    'age': [f'({i*10}, {(i+1)*10}]' for i in range(8)]
}

for num_attr in bins.keys():
    df[num_attr] = pd.cut(df[num_attr], bins[num_attr], labels=labels[num_attr]).astype(str)

# print(df[['duration', 'credit-amount', 'age']])
# exit(0)

df.to_csv('german.csv', index=False)

'''
    Construct the domain file
'''
domains = {}

# Categorical attributes
for col in cat_attrs:
    vals = [x for x in cat_domains[col].values()]
    vmin = None
    vmax = None
    domain = Domain(col, vmin, vmax, vals)
    domains[col] = domain
    
for col in num_attrs:
    vals = labels[col]
    vmin = None
    vmax = None
    domain = Domain(col, vmin, vmax, vals)
    domains[col] = domain
    
domains['good-credit'] = Domain('good-credit', 0, 1, None)

schema = Schema(domains)
schema.to_json('german.json')