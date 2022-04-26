from privex.components.basic.question import Question

from abc import ABC, abstractmethod

class MetaPrivateTopkExplanationPredicates(ABC):
    
    @abstractmethod
    def __call__(self, predicates_with_scores, k, rho, score_sensitivity):
        pass