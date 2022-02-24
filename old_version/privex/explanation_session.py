from privex.basic import GaussianMechanism, Predicate, Query, Question, Domain, Schema
from privex.basic import generate_explanation_predicates
from privex.impact_function import ImpactFunction
from privex.conf_interval import monte_carlo_ci, analytical_ci
from privex.conf_rank_bound import PrivRankBound
from privex.private_topk import subsample_and_rank_aggregate_topk

import pandas as pd
import numpy as np
from typing import Sequence

import logging
logger = logging.getLogger(__name__)

class ExplanationSession():
    def __init__(self, df, schema, gamma, random_seed = 0):
        '''
        gamma: the confidence level
        '''
        self.df = df
        self.schema = schema
        self.gamma = gamma
        self.random_seed = random_seed
        
        np.random.seed(random_seed)
        
    def submit_queries(self, queries: Sequence[Query], rho_query):
        self.queries = queries
        self.rho_per_query = rho_query / len(queries)
        
        self.raw_query_results = {
            query: query(self.df)
            for query in queries
        }
        
        self.query_results = {
            query: query(self.df, (self.rho_per_query, self.schema))
            for query in queries
        }
        
    def show_query_results(self):
        query_result_df = pd.DataFrame([
            {
                #'index': i,
                'query': str(query),
                'answer': self.query_results[query]
            } 
            for i, query in enumerate(self.queries)
        ])
        return query_result_df
    
    def check_query_results(self, fstr: str):
        '''
        Example of fstr: "o[0] / o[1]". Use "o[i]" to refer
        to the query result of the query with index i.
        '''
        o = [self.query_results[query] for query in self.queries]
        return eval(fstr)
    
    def submit_question(self, question: Question):
        self.question = question
        fstr = question.fstr
        
        o = [self.query_results[query] for query in self.queries]
        sigmas = [
            GaussianMechanism(
                None, 
                self.rho_per_query, 
                self.schema.get_sens(
                    query.attr, 
                    query.agg
                )
            ).sigma
            for query in self.queries
        ]
        ci_L, ci_R = analytical_ci(fstr, o, sigmas, self.gamma)
        return ci_L, ci_R
    
    def submit_explanation_request(self, k, predicates, rho_expl):
        rho_topk = rho_expl / 3
        rho_ci = rho_expl / 3
        rho_rank = rho_expl / 3
        N = 10
        
        impact_function = ImpactFunction(self.df, self.question)
        for predicate in predicates:
            logger.debug(f'{predicate}:{impact_function(predicate)}')
        #exit()
        
        # Find the noisy top-k predicates
        topk_predicates = subsample_and_rank_aggregate_topk(
            k, 
            predicates,  
            self.df, 
            self.question, 
            rho_topk,
            N
        )
        print(topk_predicates)
        #exit()
        
        # Find the CI of predicate impacts
        topk_ci = []
        impact_function = ImpactFunction(self.df, self.question)
        rho_per_query_ci = rho_ci / k / len(self.question.queries)
        for predicate in topk_predicates:
            ifquestion = impact_function.questionize(predicate)
            fstr = ifquestion.fstr
            o = [
                query(self.df, (rho_per_query_ci, self.schema)) 
                for query in ifquestion.queries
            ]
            #logger.debug(f'o: {o}')
            #logger.debug(f'noisy impact = {eval(fstr)}')
            o = [
                query(self.df) 
                for query in ifquestion.queries
            ]
            #logger.debug(f'o: {o}')
            #logger.debug(f'true impact = {eval(fstr)}')
            sigmas = [
                GaussianMechanism(
                    None, 
                    rho_per_query_ci, 
                    self.schema.get_sens(
                        query.attr, 
                        query.agg
                    )
                ).sigma
                for query in ifquestion.queries
            ]
            ci = analytical_ci(fstr, o, sigmas, self.gamma)
            topk_ci.append(ci)
        print(topk_ci)
            
        # Find the rank bound of predicate
        topk_rb = []
        priv_rank_bound = PrivRankBound(
            self.df,
            predicates,
            impact_function,
            self.schema,
            rho_rank / k
        )
        for predicate in topk_predicates:
            priv_rank_bound.debug(predicate, self.gamma)
            # Uncomment two lines below later
            #rb = priv_rank_bound(predicate, self.gamma)
            #topk_rb.append(rb)
        exit()
            
        # Construct the explanation table
        explanation_table = pd.DataFrame({
            'predicates': topk_predicates,
            f'{self.gamma*100:.0f}-CI left': [x[0] for x in topk_ci],
            f'{self.gamma*100:.0f}-CI right': [x[1] for x in topk_ci],
            f'{self.gamma*100:.0f}-confidence rank bound': topk_rb 
        })
        return explanation_table