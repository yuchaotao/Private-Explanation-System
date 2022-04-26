from typing import Any, Dict, Tuple, List, Sequence

class Predicate():
    def __init__(self, predicate_str):
        self.predicate_str = predicate_str
        
    def __repr__(self):
        return self.predicate_str 
    __str__ = __repr__
    
    def to_sql(self):
        return self.predicate_str 
    
    @staticmethod
    def from_dict(attr_val_dict: Dict[str, Any]):
        predicate_str = ' and '.join(
            f'`{attr}` == "{val}"' 
            for attr, val in attr_val_dict.items()
        )
        return Predicate(predicate_str)
    
    @staticmethod
    def conjunction(predicate_A, predicate_B):
        if predicate_A is None:
            return predicate_B
        elif predicate_B is None:
            return predicate_A
        else:
            predicate_str = f'({predicate_A}) and ({predicate_B})'
            return Predicate(predicate_str)
    
    @staticmethod
    def negation(predicate):
        predicate_str = f'(not ({predicate}))'
        return Predicate(predicate_str)