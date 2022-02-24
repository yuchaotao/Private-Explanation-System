import sys
sys.path.append('../')

import pandas as pd
import pprint

from privex.basic import Schema, Query, Question
from privex.basic import generate_explanation_predicates
from privex.explanation_session import ExplanationSession

import logging
logger = logging.getLogger(__name__)

def main():
    df = pd.read_csv('../data/adult.csv')
    schema = Schema.from_json('../data/adult.json')
    gamma = 0.95
    attributes = ['marital-status', 'occupation', 'age', 'relationship', 'race', 'workclass', 'sex', 'native-country']
    predicates = generate_explanation_predicates(attributes, schema, strategy='1-way marginal')
    predicates += generate_explanation_predicates(attributes, schema, strategy='2-way marginal')
    es = ExplanationSession(df, schema, gamma, predicates)
    
    # Phase 1
    q1 = Query('education == "Doctorate"', 'high_income', schema)
    q2 = Query('education == "Prof-school"', 'high_income', schema)
    rho_query = 10.0
    es.submit_queries([q1, q2], rho_query)
    with pd.option_context('display.max_rows', None, 'display.max_columns', None, 
'display.max_colwidth', 1000):
        print(es.show_query_results())
    
    # Phase 2
    question = Question(q1, 'lower', q2)
    es.submit_question(question)
    ci = es.question_ci()
    print(question)
    print(f'The {gamma*100:.0f}% confidence interval of the difference is ', ci)
    
    # Phase 3
    k = 5
    logger.debug(f'Length of predicates is {len(predicates)}')
    rho_expl = 200.0
    es.submit_explanation_request(k, rho_expl)
    with pd.option_context('display.max_rows', None, 'display.max_columns', None, 
'display.max_colwidth', 1000, 'display.width', None):
        print(es.show_explanation_table())
    pprint.pprint(es.measure_explanation_table())
    es.baseline_submit_explanation_request(k, rho_expl)
    with pd.option_context('display.max_rows', None, 'display.max_columns', None, 
'display.max_colwidth', 1000, 'display.width', None):
        print(es.show_explanation_table())
    pprint.pprint(es.measure_explanation_table())
    
    
if __name__ == '__main__':
    main()