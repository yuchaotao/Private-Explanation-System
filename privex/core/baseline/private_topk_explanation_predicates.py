from privex.core.meta_private_topk_explanation_predicates import MetaPrivateTopkExplanationPredicates
from privex.components.private_topk.topk_of_noises import topk_of_noises
from privex.components.basic import Question

class PrivateTopkExplanationPredicates(MetaPrivateTopkExplanationPredicates):
    
    def __call__(self, predicates_with_scores, k, rho, score_sensitivity):
        return topk_of_noises(predicates_with_scores, k, rho, score_sensitivity)