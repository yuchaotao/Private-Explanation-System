from privex.components.basic.question import Question

from abc import ABC, abstractmethod

class MetaPrivateCIofInfluence(ABC):
    
    @abstractmethod
    def __call__(self, explanation_predicate, influence_function, rho, gamma):
        pass