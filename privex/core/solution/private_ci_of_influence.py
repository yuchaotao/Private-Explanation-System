from privex.core.meta_private_ci_of_influence import MetaPrivateCIofInfluence
from privex.components.basic.gaussian_mechanism import GaussianMechanism
from privex.components.private_ci.query.image import image
from privex.components.private_ci.gaussian_ci import gaussian_ci

import numpy as np

import logging
logger = logging.getLogger(__name__)

class PrivateCIofInfluence(MetaPrivateCIofInfluence):
    
    def ci_avg(self, explanation_predicate, influence_function, rho, gamma):
        dataset = influence_function.dataset
        fstr, x, _ = (influence_function
            .to_stringified_function(
                explanation_predicate, 
                counter = 0
            )
        )
        fun = lambda x: eval(fstr)
        rho_per_query = rho / len(x)
        query_answers = [query(dataset, rho_per_query) for query in x]
        answers = [
            res['query_answer']['val']
            for res in query_answers
        ]
        sigmas = [
            res['query_answer']['sigma']
            for res in query_answers
        ]
        #logger.debug(fstr)
        #logger.debug(str(answers))
        #logger.debug(str(sigmas))
        ci = image(fun, answers, sigmas, gamma)
        return ci
    
    def ci_cnt_sum(self, explanation_predicate, influence_function, rho, gamma):
        question = influence_function.question
        weights = list(question.weights.values())
        
        sensitivity = 2 * np.linalg.norm(weights, ord=1) * question.groupby_query.sensitivity
        influence = influence_function(explanation_predicate)['influence']
        gs = GaussianMechanism(influence, rho, sensitivity) 
        answer = gs()
        sigma = gs.sigma
        
        ci = gaussian_ci(answer, sigma, gamma)
        return ci
    
    def __call__(self, explanation_predicate, influence_function, rho, gamma):
#         if influence_function.question.groupby_query.agg == 'AVG':
#             return self.ci_avg(explanation_predicate, influence_function, rho, gamma)
#         else:
#             return self.ci_cnt_sum(explanation_predicate, influence_function, rho, gamma)
        question = influence_function.question
        weights = list(question.weights.values())
        
        sensitivity = influence_function.score_sensitivity()
        influence = influence_function(explanation_predicate)['score']
        gs = GaussianMechanism(influence, rho, sensitivity) 
        answer = gs()
        sigma = gs.sigma
        
        ci = gaussian_ci(answer, sigma, gamma)
        return ci

        