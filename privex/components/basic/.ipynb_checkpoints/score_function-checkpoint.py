from privex.components.basic.influence_function import InfluenceFunction

class ScoreFunction(InfluenceFunction):
    def __init__(self, dataset, question):
        super().__init__(dataset, question)
        
    def __call__(self, predicate):
        influence = super().__call__(predicate)
        
        agg = self.question.groupby_query.agg
        if agg in ['CNT', 'SUM']:
            score = influence
        elif agg in ['AVG']:
            df_groups = self.question.groupby_query.get_df_groups(
                self.dataset
            )
            gsizes = [df_group.size for df_group in df_groups.values()]
            score = influence * (max(gsizes) + 1)
        return score
    
    def sensitivity(self):
        agg = self.question.groupby_query.agg
        attr_agg = self.question.groupby_query.attr_agg
        attr_sum_sens = self.dataset.get_sens(attr_agg, 'SUM')
        sens_dict = {
            'CNT': 6,
            'SUM': 6 * attr_sum_sens,
            'AVG': 16 * attr_sum_sens
        }
        return sens_dict[agg]