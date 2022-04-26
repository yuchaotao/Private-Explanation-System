from privex.components.basic import ExplanationPredicate

from itertools import combinations, product

def generate_explanation_predicates(attributes, schema, strategy = 'cross product'):
    if strategy == 'cross product':
        predicates = [
            ExplanationPredicate.from_dict(
                dict(
                    zip(
                        attributes, 
                        vals
                    )
                )
            )
            for vals in product(
                *
                [
                    schema.domains[attr].vals 
                    for attr in attributes
                ]
            )
        ]
    elif strategy == '1-way marginal':
        predicates = [
                ExplanationPredicate.from_dict(
                    {
                        attr: val
                    }
                )    
            for attr in attributes
                for val in schema.domains[attr].vals 
        ]
    elif strategy == '2-way marginal':
        predicates = []
        for attribute_pair in combinations(attributes, 2):
            predicates += generate_explanation_predicates(
                attribute_pair, 
                schema, 
                strategy = 'cross product'
            )
    elif strategy == '3-way marginal':
        predicates = []
        for attribute_pair in combinations(attributes, 3):
            predicates += generate_explanation_predicates(
                attribute_pair, 
                schema, 
                strategy = 'cross product'
            )
    return predicates