from privex.core.meta_private_ci_of_question import MetaPrivateCIofQuestion
from privex.components.basic.question import Question
from privex.components.basic.gaussian_mechanism import GaussianMechanism
from privex.components.private_ci.query.bootstrap import bootstrap

import logging
logger = logging.getLogger(__name__)

class PrivateCIofQuestion(MetaPrivateCIofQuestion):
    
    def __call__(self, dataset, question, noisy_query_answers, sigmas, gamma):
        fstr, x, _ = question.to_stringified_function(counter = 0)
        fun = lambda x: eval(fstr)
        answers = [noisy_query_answers[query] for query in x]
        sigmas = [sigmas[query] for query in x]
        ci = bootstrap(fun, answers, sigmas, gamma)
        return ci