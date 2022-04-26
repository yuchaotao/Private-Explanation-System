from privex.evaluation.evaluate_ci import EvaluateCI
from privex.evaluation.evaluate_topk import EvaluateTopk

def evaluate_question_ci(es, groupby_query, question, dataset, rho, repetitions = 100):
    #1 Evaluate Question CI
    def fun_ci():
        es.phase_1_submit_query(groupby_query, rho)
        es.phase_2_submit_question(question)
        ci = es.phase_2_prepare_question_ci()
        return ci
    question_ci_evaluation = EvaluateCI(
        fun_ci = fun_ci,
        target_statistic = question.evaluation(dataset),
        repetitions = repetitions
    )
    question_ci_evaluation.evaluation()
    #print(question_ci_evaluation.text_report())
    return question_ci_evaluation
    
def evaluate_topk(es, k, rho, repetitions = 100):
    #2 Evaluate Topk
    score_sensitivity = es.influence_function.score_sensitivity()
    def fun_topk():
        topk_explanation_predicates = es.private_topk_explanation_predicates(
            es.predicates_with_scores, 
            k, 
            rho, 
            score_sensitivity
        )
        return topk_explanation_predicates
    topk_evaluation = EvaluateTopk(
        fun_topk = fun_topk,
        k = k,
        sorted_candidates = es.sorted_predicates,
        candidate_score_mapping = es.predicates_with_influences,
        repetitions = repetitions
    )
    topk_evaluation.evaluation()
    #print(topk_evaluation.text_report())
    return topk_evaluation
    
def evaluate_influence_ci(es, explanation_predicate, rho, repetitions = 100):
    #3 Evaluate influence ci
    def fun_ci():
        ci = es.private_ci_of_influence(
            explanation_predicate,
            es.influence_function,
            rho, 
            es.gamma
        )
        return ci
    influence_ci_evaluation = EvaluateCI(
        fun_ci = fun_ci,
        target_statistic = es.influence_function(
            explanation_predicate
        )['influence'],
        repetitions = repetitions
    )
    influence_ci_evaluation.evaluation()
    #print(influence_ci_evaluation.text_report())
    return influence_ci_evaluation
    
def evaluate_rank_ci(es, explanation_predicate, rho, repetitions = 100):
    #4 Evaluate rank ci
    score_sensitivity = es.influence_function.score_sensitivity()
    target_statistic = {
        predicate: i+1
        for i, predicate in enumerate(
            es.sorted_predicates
        )
    }[explanation_predicate]
    def fun_ci():
        ci = es.private_ci_of_rank(
            explanation_predicate, 
            es.predicates_with_scores, 
            rho, 
            score_sensitivity, 
            es.gamma
        )
        return ci
    rank_ci_evaluation = EvaluateCI(
        fun_ci = fun_ci,
        target_statistic = target_statistic,
        repetitions = repetitions
    )
    rank_ci_evaluation.evaluation()
    #print(rank_ci_evaluation.text_report())
    return rank_ci_evaluation