from privex.core.meta_private_ci_of_influence import MetaPrivateCIofInfluence
from privex.components.basic.gaussian_mechanism import GaussianMechanism
from privex.components.private_ci.query.bootstrap import bootstrap

import logging
logger = logging.getLogger(__name__)

class PrivateCIofInfluence(MetaPrivateCIofInfluence):
    
    def __call__(self, explanation_predicate, influence_function, rho, gamma):
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
        ci = bootstrap(fun, answers, sigmas, gamma)
        return ci
        