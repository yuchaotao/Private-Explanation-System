class Domain():
    '''
        Encodes the domain values of an attribute
    '''
    def __init__(self, attr, vmin, vmax, vals):
        self.attr = attr
        self.vmin = vmin
        self.vmax = vmax
        self.vals = vals
        
    def as_dict(self):
        return {
            'attr': self.attr,
            'vmin': self.vmin,
            'vmax': self.vmax,
            'vals': self.vals
        }
    
    def __repr__(self):
        return str(self.as_dict())
    
    __str__ = __repr__