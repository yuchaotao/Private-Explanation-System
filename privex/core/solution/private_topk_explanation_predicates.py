from privex.core.meta_private_topk_explanation_predicates import MetaPrivateTopkExplanationPredicates
from privex.components.private_topk.noisy_topk import noisy_topk
from privex.components.basic import Question

class PrivateTopkExplanationPredicates(MetaPrivateTopkExplanationPredicates):
    
    def __call__(self, predicates_with_scores, k, rho, score_sensitivity):
        return noisy_topk(predicates_with_scores, k, rho, score_sensitivity)