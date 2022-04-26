from privex.components.basic.question import Question

from abc import ABC, abstractmethod

class MetaPrivateCIofRank(ABC):
    
    @abstractmethod
    def __call__(self, explanation_predicate, predicates_with_scores, rho, score_sensitivity, gamma, split_factor):
        pass