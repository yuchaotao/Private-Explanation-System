from privex.core.meta_private_ci_of_rank import MetaPrivateCIofRank
from privex.components.private_ci.rank.noisy_binary_search import noisy_binary_search

class PrivateCIofRank(MetaPrivateCIofRank):
    
    def __call__(self, explanation_predicate, predicates_with_scores, rho, score_sensitivity, gamma, split_factor = 0.9):
        ci = noisy_binary_search(
            explanation_predicate, 
            predicates_with_scores, 
            rho, 
            score_sensitivity,
            gamma, 
            split_factor
        )
        return ci