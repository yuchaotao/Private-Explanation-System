import pandas as pd

class EvaluateCI():
    def __init__(self, fun_ci, target_statistic, repetitions):
        self.fun_ci = fun_ci
        self.target_statistic = target_statistic
        self.repetitions = repetitions
        
        self.evaluation_records = None
        
    def evaluation(self):
        res = []
        for rep in range(self.repetitions):
            ci = self.fun_ci()
            ci_width = ci[1] - ci[0]
            ci_coverage = int(ci[0] <= self.target_statistic <= ci[1])
            res.append({
                'ci_l': ci[0],
                'ci_u': ci[1],
                'ci_width': ci_width,
                'ci_coverage': ci_coverage
            })
        self.evaluation_records = pd.DataFrame(res)
    
    def text_report(self):
        report = self.evaluation_records.describe()
        return report
        