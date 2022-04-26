from privex.components.basic.predicate import Predicate

class ExplanationPredicate(Predicate):
    def __init__(self, predicate_str):
        super().__init__(predicate_str)
        
    @staticmethod
    def from_dict(attr_val_dict):
        predicate_str = ' and '.join(
            f'`{attr}` == "{val}"' 
            for attr, val in attr_val_dict.items()
        )
        return ExplanationPredicate(predicate_str)