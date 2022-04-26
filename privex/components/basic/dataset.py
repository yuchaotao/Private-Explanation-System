class Dataset():
    def __init__(self, df, schema):
        self.df = df
        self.schema = schema
        
    def get_sens(self, attr, agg):
        return self.schema.get_sens(attr, agg)