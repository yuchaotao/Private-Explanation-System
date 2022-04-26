import numpy as np
from scipy.stats import norm

import logging
logger = logging.getLogger(__name__)

def bootstrap(fun, answers, sigmas, gamma, B = 100):
    m = len(answers)
    y = np.array([answers[i] + np.random.normal(scale=sigmas[i], size=B) for i in range(m)])
    theta = np.array([fun(y[:, j]) for j in range(B)])
    theta_hat = fun(answers)
    z0 = norm.ppf((theta < theta_hat).sum() / B)
    ci = (
        np.quantile(theta, norm.cdf(2 * z0 + norm.ppf((1-gamma)/2))),
        np.quantile(theta, norm.cdf(2 * z0 + norm.ppf((1+gamma)/2)))
    )
    return ci