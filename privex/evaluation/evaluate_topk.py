import pandas as pd

class EvaluateTopk():
    def __init__(self, fun_topk, k, sorted_candidates, candidate_score_mapping, repetitions):
        self.fun_topk = fun_topk
        self.k = k
        self.sorted_candidates = sorted_candidates
        self.candidate_score_mapping = candidate_score_mapping
        self.repetitions = repetitions
        
    def evaluation(self):
        k = self.k
        true_topk_candidates = set(self.sorted_candidates[:k])
        true_kth_candidate = self.sorted_candidates[k-1]
        true_kth_score = self.candidate_score_mapping[true_kth_candidate]
        
        res = []
        for rep in range(self.repetitions):
            noisy_topk_candidates = set(self.fun_topk())
            noisy_kth_score = min(
                self.candidate_score_mapping[candidate]
                for candidate in noisy_topk_candidates
            )
            kth_score_gap = true_kth_score - noisy_kth_score
            precision_at_k = len(true_topk_candidates & noisy_topk_candidates) / self.k
            res.append({
                'kth_gap': kth_score_gap,
                'precision_at_k': precision_at_k
            })
        self.evaluation_records = pd.DataFrame(res)
    
    def text_report(self):
        report = self.evaluation_records.describe()
        return report