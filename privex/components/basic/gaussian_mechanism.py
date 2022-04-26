import numpy as np

class GaussianMechanism():
    def __init__(self, val, rho, sens=1):
        self.val = val
        self.rho = rho
        self.sens = sens
        self.sigma = sens / np.sqrt(2*rho)
        
    @staticmethod
    def basic_sigma(rho):
        return 1 / np.sqrt(2*rho)
    
    @staticmethod
    def compute_sigma(rho, sens):
        return sens / np.sqrt(2*rho)
        
    def __call__(self):
        return self.val + np.random.normal(scale=self.sigma)