import numpy as np
from scipy.special import erfinv

def gaussian_ci(val, sigma, gamma):
    half_width = np.sqrt(2) * sigma * erfinv(gamma)

    ci = (
        val - half_width,
        val + half_width
    )
    return ci