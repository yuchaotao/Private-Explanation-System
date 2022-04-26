import sdv
from sdv.tabular import CTGAN
from sdv import Metadata

import pandas as pd

data = pd.read_csv('german.csv')

metadata = Metadata()

metadata.add_table(
    name='german',
    data=data
)

print(metadata)
print(metadata.get_table_meta('german'))

model = CTGAN()
model.fit(data)