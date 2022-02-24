import sys
sys.path.append('../')

import pandas as pd

from privex.basic import Schema, Query, Question
from privex.basic import generate_explanation_predicates
from privex.explanation_session import ExplanationSession

def main():
    df = pd.read_csv('../data/adult.csv')
    schema = Schema.from_json('../data/adult.json')
    gamma = 0.95
    es = ExplanationSession(df, schema, gamma)
    
    # Phase 1
    queries = [
        Query('education == "Doctorate" and `class` == ">50K"', 'count', None),
        Query('education == "Doctorate"', 'count', None),
        Query('education == "Prof-school" and `class` == ">50K"', 'count', None),
        Query('education == "Prof-school"', 'count', None),
    ]
    rho_query = 10.0
    es.submit_queries(queries, rho_query)
    print(es.show_query_results())
    
    # Pre-Phase 2
    fstr = 'o[0] / o[1]'
    print(fstr, es.check_query_results(fstr))
    fstr = 'o[2] / o[3]'
    print(fstr, es.check_query_results(fstr))
    
    # Phase 2
    question = Question('o[0] / o[1] - o[2] / o[3]', 'low', es.queries)
    ci = es.submit_question(question)
    print(question)
    print(f'The {gamma*100:.0f}% confidence interval is ', ci)
    
    # Phase 3
    k = 1
    attributes = ['marital-status']
    predicates = generate_explanation_predicates(attributes, schema, strategy='independent')
    rho_expl = 1500.0
    explanation_table = es.submit_explanation_request(k, predicates, rho_expl)
    print(explanation_table)
    
    
if __name__ == '__main__':
    main()