from privex.basic import GaussianMechanism, Predicate, Query, Question, Domain, Schema
from privex.basic import generate_explanation_predicates
from privex.impact_function import ImpactFunction
from privex.conf_interval import monte_carlo_ci, analytical_ci, gaussian_ci
from privex.conf_rank_bound import PrivRankBound
from privex.private_topk import noisy_topk

import pandas as pd
import numpy as np
from typing import Sequence
import heapq

import logging
logger = logging.getLogger(__name__)

class ExplanationSession():
    def __init__(self, df, schema, gamma, predicates, random_seed = None):
        '''
        gamma: the confidence level
        '''
        self.df = df
        self.schema = schema
        self.gamma = gamma
        self.predicates = predicates
        self.random_seed = random_seed
        
        self.reference_predicate = Predicate(None)
        self.predicates_with_scores = None
        
        if self.random_seed is not None:
            np.random.seed(random_seed)
        
    def submit_queries(self, queries: Sequence[Query], rho_query):
        self.queries = queries
        self.rho_per_query = rho_query / len(queries)
        
        self.raw_query_results = {
            query: query(self.df)
            for query in queries
        }
        
        self.query_results = {
            query: query(self.df, self.rho_per_query)
            for query in queries
        }
        
    def show_query_results(self):
        query_result_df = pd.DataFrame([
            {
                'index': i+1,
                'query': str(query),
                'answer': self.query_results[query]['ores']
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
        
    def question_ci(self):
        question = self.question
        fstr = 'o[0] / o[1] - o[2] / o[3]'
        
        o = [
            self.query_results[question.q1]['osum'],
            self.query_results[question.q1]['ocnt'],
            self.query_results[question.q2]['osum'],
            self.query_results[question.q2]['ocnt'],
        ]
        basic_sigma = GaussianMechanism.basic_sigma(
            self.rho_per_query / 2
        )
        attr_sens = question.q1.qsum_sens
        sigmas = [ 
            attr_sens * basic_sigma,
            basic_sigma
        ] * 2
        ci = analytical_ci(fstr, o, sigmas, self.gamma)
        return ci
    
#     def question_impact(self):
#         question = self.question
#         o_1 = self.raw_query_results[question.q1]
#         o_2 = self.raw_query_results[question.q2]
#         impact = (o_1['ores'] - o_2['ores']) * min(o_1['ocnt'], o_2['ocnt'])
#         return impact
    
    def question_impact_ci(self):
        question = self.question
        fstr = '(o[0] / o[1] - o[2] / o[3])*min(o[1], o[3])'
        
        o = [
            self.query_results[question.q1]['osum'],
            self.query_results[question.q1]['ocnt'],
            self.query_results[question.q2]['osum'],
            self.query_results[question.q2]['ocnt'],
        ]
        basic_sigma = GaussianMechanism.basic_sigma(
            self.rho_per_query / 2
        )
        attr_sens = question.q1.qsum_sens
        sigmas = [ 
            attr_sens * basic_sigma,
            basic_sigma
        ] * 2
        ci = analytical_ci(fstr, o, sigmas, self.gamma)
        return ci
    
    def submit_explanation_request(self, k, rho_expl):
        predicates = self.predicates
        assert k <= len(predicates)
        
        impact_function = ImpactFunction(self.df, self.question)
        
        N = len(predicates)
        # Split the budget ... need to explore the optimal split ...
        w_topk = 1/2*(np.log(N)**2)
        w_ci = 1/2
        w_rank = 3 * np.log2(N)
        #w_topk = w_rank = max(w_topk, w_rank)
        w = w_topk + w_ci + w_rank
        
        rho_topk = rho_expl * (w_topk / w)
        rho_ci = rho_expl * (w_ci / w)
        rho_rank = rho_expl * (w_rank / w)
        
        logger.debug(f'total rho_expl is {rho_expl}')
        logger.debug(f'rho_topk is {rho_topk}')
        logger.debug(f'rho_ci is {rho_ci}')
        logger.debug(f'rho_rank is {rho_rank}')
        
        if self.predicates_with_scores is None:
            predicates_with_scores = {
                predicate: impact_function(predicate)
                for predicate in predicates
            }

            # Add the reference predicate into the pool
            reference_predicate = self.reference_predicate
            predicates_with_scores[reference_predicate] = impact_function(reference_predicate)
            self.predicates_with_scores = predicates_with_scores
        else:
            predicates_with_scores = self.predicates_with_scores
        
        logger.debug(f'{len(predicates_with_scores)} predicates and their impacts have been loaded.')
        logger.debug(f'Impact Function sensitivity is {impact_function.sensitivity}')
        logger.debug(f'\n{pd.DataFrame(predicates_with_scores.values()).describe()}')
        
        # Find the noisy top-k predicates
        topk_predicates = noisy_topk(
            k, 
            {pred: v for pred, v in predicates_with_scores.items() if pred != self.reference_predicate}, 
            rho_topk, 
            impact_function.sensitivity
        )
        logger.debug(topk_predicates)
        
        # Find the CI of predicate impacts
        topk_ci = []
        rho_per_predicate_ci = rho_ci / k
        for predicate in topk_predicates:
            gm = GaussianMechanism(
                predicates_with_scores[predicate],
                rho_per_predicate_ci,
                impact_function.sensitivity
            )
            o = gm()
            sigma = gm.sigma
            ci = gaussian_ci(o, sigma, self.gamma)
            topk_ci.append(ci)
        
        
        # Find the rank bound of predicate
        topk_rb = []
        priv_rank_bound = PrivRankBound(
            self.df,
            predicates_with_scores,
            rho_rank / (k+1) / 2,
            impact_function.sensitivity
        )
        for predicate in topk_predicates:
            rb = priv_rank_bound.ci_bounds(predicate, self.gamma)
            topk_rb.append(rb)
            
        # Collect the info of the reference
        reference_ci = self.question_impact_ci()
        reference_rb = priv_rank_bound.ci_bounds(self.reference_predicate, self.gamma)
        topk_predicates.append(self.reference_predicate)
        topk_ci.append(reference_ci)
        topk_rb.append(reference_rb)
        
        self.topk_predicates = topk_predicates
        self.topk_ci = topk_ci
        self.topk_rb = topk_rb
    
    def baseline_submit_explanation_request(self, k, rho_expl):
        predicates = self.predicates
        assert k <= len(predicates)
        
        rho = rho_expl / (len(predicates)+1)
        logger.debug(f'rho for each predicate {rho}')
        
        impact_function = ImpactFunction(self.df, self.question)
        
        if self.predicates_with_scores is None:
            predicates_with_scores = {
                predicate: impact_function(predicate)
                for predicate in predicates
            }

            # Add the reference predicate into the pool
            reference_predicate = self.reference_predicate
            predicates_with_scores[reference_predicate] = impact_function(reference_predicate)
            self.predicates_with_scores = predicates_with_scores
        else:
            predicates_with_scores = self.predicates_with_scores
            
        predicates_with_noisy_scores = {
            predicate: GaussianMechanism(
                val,
                rho,
                impact_function.sensitivity
            )()
            for predicate, val in predicates_with_scores.items()
        }
        
        topk_predicates = heapq.nlargest(
            k, 
            self.predicates, 
            key=predicates_with_noisy_scores.get
        )
        topk_predicates.append(self.reference_predicate)
        
        topk_ci = []
        for predicate in topk_predicates:
            o = predicates_with_noisy_scores[predicate]
            sigma = impact_function.sensitivity * GaussianMechanism.basic_sigma(rho)
            topk_ci.append(
                gaussian_ci(o, sigma, self.gamma)
            )
        
        # a simple rank bound algorithm
        def simple_rank_bound(predicates_with_noisy_scores, topk_predicates, sigma):
            rb = []
            gamma = np.power(self.gamma, 1 / len(predicates_with_noisy_scores))
            wider_ci = {
                predicate: gaussian_ci(o, sigma, gamma)
                for predicate, o in predicates_with_noisy_scores.items()
            }
            wider_ci_l, wider_ci_r = zip(*wider_ci.values())
            for predicate in topk_predicates:
                l, r = wider_ci[predicate]
                rlb = np.sum(np.array(wider_ci_l) >= r) + 1
                rub = len(wider_ci) - np.sum(np.array(wider_ci_r) <= l)
                rb.append((rlb, rub))
            return rb
        topk_rb = simple_rank_bound(predicates_with_scores, topk_predicates, sigma)
        
        self.topk_predicates = topk_predicates
        self.topk_ci = topk_ci
        self.topk_rb = topk_rb     

    def show_explanation_table(self):
        topk_predicates = self.topk_predicates
        topk_ci = self.topk_ci
        topk_rb = self.topk_rb
        
        # Construct the explanation table
        gammastr = f'{self.gamma*100:.0f}'
        explanation_table = pd.DataFrame({
            'predicates': topk_predicates,
            f'Imp {gammastr}-CI L': [x[0] for x in topk_ci],
            f'Imp {gammastr}-CI R': [x[1] for x in topk_ci],
            f'Rnk {gammastr}-CI L': [x[0] for x in topk_rb], 
            f'Rnk {gammastr}-CI R': [x[1] for x in topk_rb], 
        })
        explanation_table = explanation_table.sort_values(
            by=[
                f'Rnk {gammastr}-CI R',
                f'Imp {gammastr}-CI R',
            ],
            ascending = [True, False]
        ).reset_index(drop=True)
        return explanation_table
    
    def measure_explanation_table(self):
        topk_predicates = self.topk_predicates
        topk_ci = self.topk_ci
        topk_rb = self.topk_rb
        k = len(topk_predicates) - 1
        
        predicates_with_scores = self.predicates_with_scores
        
        #measure topk predicates
        true_topk_predicates = heapq.nlargest(
            k, 
            self.predicates, 
            key=predicates_with_scores.get
        )
        true_kth_largest_impact = predicates_with_scores[true_topk_predicates[-1]]
        topk_gap = true_kth_largest_impact - min([predicates_with_scores[pred] for pred in topk_predicates if pred != self.reference_predicate])
        
        #measure topk ci
        imp_coverage_prob = np.mean([
            ci[0] <= predicates_with_scores[predicate] <= ci[1]
            for predicate, ci in zip(topk_predicates, topk_ci)
        ])
        imp_ci_width = np.mean([
            ci[1] - ci[0]
            for predicate, ci in zip(topk_predicates, topk_ci)
        ])
        
        #measure topk rank bound
        impacts = np.fromiter(predicates_with_scores.values(), dtype=float)
        impacts[::-1].sort() # sort in descending order
        # @NOTE: assuming there is no tie. What if there is a tie? How do we define rank bound?
        rnk_coverage_prob = np.mean([
            impacts[rb[1]-1] <= predicates_with_scores[predicate] <= impacts[rb[0]-1]
            for predicate, rb in zip(topk_predicates, topk_rb)
        ])
        rnk_ci_width = np.mean([
            impacts[rb[0]-1] - impacts[rb[1]-1]
            for predicate, rb in zip(topk_predicates, topk_rb)
        ])
        
        report = {
            'topk_gap': topk_gap,
            'imp_coverage_prob': imp_coverage_prob,
            'imp_ci_width': imp_ci_width,
            'rnk_coverage_prob': rnk_coverage_prob,
            'rnk_ci_width': rnk_ci_width
        }
        return report 
        