from privex.components.basic.question import Question

from abc import ABC, abstractmethod

class MetaPrivateCIofQuestion(ABC):
    
    @abstractmethod
    def __call__(self, dataset, question, noisy_query_answers, sigmas, gamma):
        pass