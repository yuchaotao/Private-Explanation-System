from privex.components.basic.groupby_query import GroupbyQuery
from privex.components.basic.question import Question
from privex.components.basic.influence_function import InfluenceFunction
from privex.components.basic.score_function import ScoreFunction
from privex.components.basic import GroupbyQuery, Question, InfluenceFunction

from abc import ABC, abstractmethod
import pandas as pd
import numpy as np
import heapq
from tqdm import tqdm
import time
import pickle

import logging
logger = logging.getLogger(__name__)

class MetaExplanationSession(ABC):
    def __init__(self, dataset, gamma, predicates, random_seed = None):
        '''
        gamma: the confidence level
        '''
        self.dataset = dataset
        self.gamma = gamma
        logger.info(f'{len(predicates)} predicates for the explanation.')
        self.predicates = predicates
        self.random_seed = random_seed
        
        self.predicates_with_influences_and_scores = None
        
        if self.random_seed is not None:
            np.random.seed(random_seed)
            
    @abstractmethod
    def private_ci_of_influence(self, explanation_predicate, influence_function, rho, gamma):
        pass
    
    @abstractmethod
    def private_ci_of_question(self, dataset, question, noisy_query_answers, sigmas, gamma):
        pass
    
    @abstractmethod
    def private_ci_of_rank(self, explanation_predicate, predicates_with_scores, rho, score_sensitivity, gamma):
        pass
    
    @abstractmethod
    def private_topk_explanation_predicates(self, predicates_with_scores, k, rho, score_sensitivity):
        pass
            
    def phase_1_submit_query(self, groupby_query: GroupbyQuery, rho, random_seed = None):
        if random_seed is not None:
            np.random.seed(random_seed)
            
        self.query_rho = rho
            
        t_start = time.time()
        self.groupby_query = groupby_query
        self.raw_query_answers = groupby_query(self.dataset)
        self.query_answers = groupby_query(self.dataset, rho)
        t_end = time.time()
        self.t_phase_1 = t_end - t_start
        
    def phase_1_show_query_results(self):
        query_result_df = pd.DataFrame([
            {
                'group': record['group'],
                'answer': record['res']['query_answer']['val']
            } 
            for record in self.query_answers.values()
        ])
        query_result_df = query_result_df.sort_values(by='answer')
        return query_result_df
    
    def phase_2_submit_question(self, question: Question):
        self.question = question
        
    def phase_2_prepare_question_ci(self, random_seed = None):
        if random_seed is not None:
            np.random.seed(random_seed)
            
        t_start = time.time()
        basic_query_answers = {
            basic_query: basic_query_answer
            for query, record in self.query_answers.items()
                for basic_query, basic_query_answer in zip(
                    query.basic_queries,
                    [
                        info['val'] 
                        for info in record['res']['basic_query_answers']
                    ]
                )
        }
        sigmas = {
            basic_query: sigma
            for query, record in self.query_answers.items()
                for basic_query, sigma in zip(
                    query.basic_queries,
                    [
                        info['sigma'] 
                        for info in record['res']['basic_query_answers']
                    ]
                )
        }
        self.question_ci = self.private_ci_of_question(
            self.dataset, 
            self.question, 
            basic_query_answers, 
            sigmas, 
            self.gamma
        )
        
        # compute the noisy question itself
        fstr, x, _ = self.question.to_stringified_function(counter = 0)
        fun = lambda x: eval(fstr)
        answers = [basic_query_answers[query] for query in x]
        self.question_point = fun(answers)
        
        t_end = time.time()
        self.t_phase_2 = t_end - t_start
        
        return self.question_ci, self.question_point
    
    def phase_2_show_question_ci(self):
        return self.question_ci
    
    def phase_2_show_question_point(self):
        return self.question_point
        
#     def phase_2_ground_truth_ci(self, rho, gamma, B = 1000):
#         qevals = []
#         noisy_query_answers = self.question.groupby_query(self.dataset, rho)
#         for i in range(B):
#             for query in noisy_query_answers:
#                 noisy_query_answers[query]['res']['query_answer']['val'] = noisy_query_answers[query]['res']['query_answer']['generator']()
#             qeval = self.question.evaluation_by_query_answers(noisy_query_answers)
#             qevals.append(qeval)
#         ci = (np.quantile(qevals, (1-gamma)/2), np.quantile(qevals, (1+gamma)/2))
#         self.ground_truth_ci = ci
#         return ci
        
    def phase_3_submit_explanation_request(self):
        t_start = time.time()
        
        predicates = self.predicates
        N = len(predicates)
        
        self.influence_function = InfluenceFunction(self.dataset, self.question)
        
        self.predicates_with_influences_and_scores = {
            predicate: self.influence_function(predicate)
            for predicate in predicates
        }
            
        self.predicates_with_influences = {
            predicate: combined['influence'] 
            for predicate, combined in self.predicates_with_influences_and_scores.items()
        }
        self.predicates_with_scores = {
            predicate: combined['score'] 
            for predicate, combined in self.predicates_with_influences_and_scores.items()
        }
        
        self.sorted_predicates = np.array(sorted(
            self.predicates_with_influences.keys(),
            key = self.predicates_with_influences.get,
            reverse=True
        ))
            
        logger.debug(f'{N} predicates and their influences & scores have been loaded.')  
        description_of_scores = pd.DataFrame(
            self.predicates_with_influences_and_scores.values()
        ).describe()
        logger.debug(f'\n{description_of_scores}')
        
        t_end = time.time()
        self.t_phase_3_preprocessing = t_end - t_start
        
    
    def phase_3_prepare_explanation(self, k, rho, split_factor = 0.9, topk_only = False, random_seed_topk = None, random_seed_influci = None, random_seed_rankci = None):
        if k == -1:
            k = len(self.predicates)
            
        predicates = self.predicates
        assert k <= len(predicates), f'You have larger k ({k}) than the number of predicates {len(predicates)}.'
        
        N = len(predicates)
        # Split the budget ... need to explore the optimal split ...
#         w_topk = 1/2*(np.log(N)**2)
#         w_influence_ci = 1/2
#         w_rank_ci = 3 * np.log2(N)
#         w = w_topk + w_influence_ci + w_rank_ci

        if type(rho) is dict:
            rho_topk = rho['rho_topk']
            rho_influence_ci = rho['rho_influ']
            rho_rank_ci = rho['rho_rank']
            rho = rho_topk + rho_influence_ci + rho_rank_ci
        else:
            w_topk = 0.05 # 4
            w_influence_ci = 0.05 # 2
            w_rank_ci = 1.9 # 14
            w = w_topk + w_influence_ci + w_rank_ci

            rho_topk = rho * (w_topk / w)
            rho_influence_ci = rho * (w_influence_ci / w)
            rho_rank_ci = rho * (w_rank_ci / w)
        
        
        self.rho_topk = rho_topk
        self.rho_influence_ci = rho_influence_ci
        self.rho_rank_ci = rho_rank_ci
        
        logger.debug(f'total rho_expl is {rho}')
        logger.debug(f'rho_topk is {rho_topk}')
        logger.debug(f'rho_ci is {rho_influence_ci}')
        logger.debug(f'rho_rank is {rho_rank_ci}')
        
        score_sensitivity = self.influence_function.score_sensitivity()
        
        
        if random_seed_topk is not None:
            np.random.seed(random_seed_topk)
        # Find the noisy top-k predicates
        t_start = time.time()
        logger.info('computing top k')
        topk_explanation_predicates = self.private_topk_explanation_predicates(
            self.predicates_with_scores, 
            k, 
            rho_topk, 
            score_sensitivity
        )
        logger.debug(topk_explanation_predicates)
        t_end = time.time()
        self.t_phase_3_topk = self.t_phase_3_preprocessing + t_end - t_start
        
        if topk_only:
            self.topk_explanation_predicates = topk_explanation_predicates
            self.topk_influence_ci = []
            self.topk_rank_ci = []
            self.t_phase_3_influci = 0
            self.t_phase_3_rankci = 0
            return
        
        if random_seed_influci is not None:
            np.random.seed(random_seed_influci)
        # Find the CI of predicate influence
        t_start = time.time()
        logger.info('computing influence ci')
        topk_influence_ci = []
        rho_per_predicate_influence_ci = rho_influence_ci / k
        for explanation_predicate in tqdm(topk_explanation_predicates):
            ci = self.private_ci_of_influence(
                explanation_predicate,
                self.influence_function,
                rho_per_predicate_influence_ci, 
                self.gamma
            )
            topk_influence_ci.append(ci)
        logger.debug(topk_influence_ci)
        t_end = time.time()
        self.t_phase_3_influci = t_end - t_start
            
        if random_seed_rankci is not None:
            np.random.seed(random_seed_rankci)
        # Find the rank ci of predicate
        t_start = time.time()
        logger.info('computing rank ci')
        topk_rank_ci = []
        rho_per_predicate_rank_ci = rho_rank_ci / k
        for explanation_predicate in tqdm(topk_explanation_predicates):
            ci = self.private_ci_of_rank(
                explanation_predicate, 
                self.predicates_with_scores, 
                rho_per_predicate_rank_ci, 
                score_sensitivity, 
                self.gamma,
                split_factor
            )
            topk_rank_ci.append(ci)
        logger.debug(topk_rank_ci)
        t_end = time.time()
        self.t_phase_3_rankci = t_end - t_start
            
        self.topk_explanation_predicates = topk_explanation_predicates
        self.topk_influence_ci = topk_influence_ci
        self.topk_rank_ci = topk_rank_ci
            
    def relative_influence(self, influence):
        qtype = self.groupby_query.agg
        noisy_question_point = self.question.evaluation_by_query_answers(self.query_answers)
        noisy_group_sizes = [record['res']['basic_query_answers'][1]['val'] for query, record in self.query_answers.items() if self.question.weights[query] != 0]
        
        if qtype in ['CNT', 'SUM']:
            relative_influence = influence / np.abs(noisy_question_point)
        else:
            relative_influence = influence / np.abs(noisy_question_point) / (np.abs(min(noisy_group_sizes)))
        
        return relative_influence
    
    def phase_3_true_top_k(self, k):
        scores = self.predicates_with_scores
        influences_and_scores = self.predicates_with_influences_and_scores
        true_topk = heapq.nlargest(k, scores.keys(), key=scores.get)
        
        positive_influences = len([x for x in self.predicates_with_influences_and_scores.values() if x['influence'] / self.question_point > 0.01])
        print('Positive Influences: ', positive_influences)
        
        result = pd.DataFrame()
        result['topk'] = true_topk
        result['rel-influence'] = [f"{self.relative_influence(influences_and_scores[p]['score'])* 100:.2f}%" for p in true_topk]
        # result['rel-influence'] = [influences_and_scores[p]['influence'] for p in true_topk]
        # result['rel-influence'] = [self.relative_influence(influences_and_scores[p]['influence']) for p in true_topk]
        return result
        
            
    def phase_3_show_explanation_table(self, withTruth = False):
        topk_explanation_predicates = self.topk_explanation_predicates
        topk_influence_ci = self.topk_influence_ci
        topk_rank_ci = self.topk_rank_ci
        sorted_predicates = sorted(self.predicates_with_scores.keys(), key=self.predicates_with_scores.get, reverse=True)
        
        # Construct the explanation table
        gammastr = f'{self.gamma*100:.0f}'
        percentageGammaStr = f'{self.gamma**2*100:.0f}'
        explanation_table = pd.DataFrame({
            'predicates': topk_explanation_predicates,
            f'Inf {gammastr}-CI L': [x[0] for x in topk_influence_ci],
            f'Inf {gammastr}-CI R': [x[1] for x in topk_influence_ci],
#             f'Rel Inf {percentageGammaStr}-CI L': [f'{x[0] / self.question_ci[1]*100:.0f}%' for x in topk_influence_ci],
#             f'Rel Inf {percentageGammaStr}-CI R': [f'{x[1] / self.question_ci[0]*100:.0f}%' for x in topk_influence_ci],
            f'Rel Inf {percentageGammaStr}-CI L': [f'{self.relative_influence(x[0])*100:.2f}%' for x in topk_influence_ci],
            f'Rel Inf {percentageGammaStr}-CI R': [f'{self.relative_influence(x[1])*100:.2f}%' for x in topk_influence_ci],
            f'Rnk {gammastr}-CI L': [x[0] for x in topk_rank_ci], 
            f'Rnk {gammastr}-CI R': [x[1] for x in topk_rank_ci], 
            f'True Rnk': [sorted_predicates.index(predicate)+1 for predicate in topk_explanation_predicates],
            f'True Rel Inf': [
                f"{self.relative_influence(self.predicates_with_scores[predicate])* 100:.2f}%"  # score is the true influence
                for predicate in topk_explanation_predicates]
        })
        explanation_table = explanation_table.sort_values(
            by=[
                f'Inf {gammastr}-CI R',
                f'Rnk {gammastr}-CI R',
            ],
            ascending = [False, True]
        ).reset_index(drop=True)
        
        if withTruth:
            explanation_table_1 = explanation_table[['predicates', f'Rel Inf {percentageGammaStr}-CI L', f'Rel Inf {percentageGammaStr}-CI R', f'Rnk {gammastr}-CI L', f'Rnk {gammastr}-CI R', 'True Rnk', 'True Rel Inf']]
            explanation_table_2 = explanation_table[['predicates', f'Inf {gammastr}-CI L', f'Inf {gammastr}-CI R', f'Rnk {gammastr}-CI L', f'Rnk {gammastr}-CI R', 'True Rnk', 'True Rel Inf']]
        else:
            explanation_table_1 = explanation_table[['predicates', f'Rel Inf {percentageGammaStr}-CI L', f'Rel Inf {percentageGammaStr}-CI R', f'Rnk {gammastr}-CI L', f'Rnk {gammastr}-CI R']]
            explanation_table_2 = explanation_table[['predicates', f'Inf {gammastr}-CI L', f'Inf {gammastr}-CI R', f'Rnk {gammastr}-CI L', f'Rnk {gammastr}-CI R']]
            
        
        return explanation_table_1, explanation_table_2
        
    def store_important_intermediates(self, foutp):
        relative_influ_ci = [[self.relative_influence(x) for x in ci] for ci in self.topk_influence_ci]
        to_store = {
            'QuestionCI': self.question_ci,
            'QuestionPoint': self.question_point,
            'GroundQuestionPoint': self.question.evaluation(self.dataset),
#             'GroundQuestionCI': self.phase_2_ground_truth_ci(self.query_rho, self.gamma),
            'Question': self.question,
            'Query': self.groupby_query,
            'QueryAnswers': self.query_answers,
            'GroundQueryAnswers': self.raw_query_answers,
            'Topk': self.topk_explanation_predicates,
            'InfluCI': self.topk_influence_ci,
            'RelInfluCI': relative_influ_ci,
            'RankCI': self.topk_rank_ci,
            'InfluScores': self.predicates_with_influences_and_scores,
            't_phase_1': self.t_phase_1,
            't_phase_2': self.t_phase_2,
            't_phase_3_preprocessing': self.t_phase_3_preprocessing,
            't_phase_3_topk': self.t_phase_3_topk,
            't_phase_3_influci': self.t_phase_3_influci,
            't_phase_3_rankci': self.t_phase_3_rankci,
            't_phase_3': self.t_phase_3_topk + self.t_phase_3_influci + self.t_phase_3_rankci,   
        }
        pickle.dump(to_store, foutp)