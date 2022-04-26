from privex.core.meta_private_ci_of_rank import MetaPrivateCIofRank
from privex.components.private_ci.rank.rank_of_noises import rank_of_noises

class PrivateCIofRank(MetaPrivateCIofRank):
    
    def __call__(self, explanation_predicate, predicates_with_scores, rho, score_sensitivity, gamma):
        ci = rank_of_noises(
            explanation_predicate, 
            predicates_with_scores, 
            rho, 
            score_sensitivity,
            gamma, 
        )
        return ci