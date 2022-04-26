from privex.core.meta_private_ci_of_question import MetaPrivateCIofQuestion
from privex.components.basic.question import Question
from privex.components.basic.gaussian_mechanism import GaussianMechanism
from privex.components.private_ci.query.image import image
from privex.components.private_ci.query.weighted_sum import weighted_sum

import logging
logger = logging.getLogger(__name__)

class PrivateCIofQuestion(MetaPrivateCIofQuestion):
    def ci_avg(self, dataset, question, noisy_query_answers, sigmas, gamma):
        fstr, x, _ = question.to_stringified_function(counter = 0)
        fun = lambda x: eval(fstr)
        answers = [noisy_query_answers[query] for query in x]
        sigmas = [sigmas[query] for query in x]
        ci = image(fun, answers, sigmas, gamma)
        return ci
    
    def ci_cnt_sum(self, dataset, question, noisy_query_answers, sigmas, gamma):
        queries = list(noisy_query_answers.keys())
        answers = [noisy_query_answers[query] for query in queries]
        weights = [question.weights[query] for query in queries]
        sigmas = [sigmas[query] for query in queries]
        ci = weighted_sum(answers, weights, sigmas, gamma)
        return ci
    
    def __call__(self, dataset, question, noisy_query_answers, sigmas, gamma):
        if question.groupby_query.agg == 'AVG':
            return self.ci_avg(dataset, question, noisy_query_answers, sigmas, gamma)
        else:
            return self.ci_cnt_sum(dataset, question, noisy_query_answers, sigmas, gamma)