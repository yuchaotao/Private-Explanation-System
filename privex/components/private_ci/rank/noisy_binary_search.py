import numpy as np

def noisy_binary_search(predicate, predicates_with_scores, rho, score_sensitivity, gamma, split_factor = 0.9):
    sorted_scores = np.array(sorted(
        predicates_with_scores.values(),
        reverse=True
    ))
    rank_bound_scores = predicates_with_scores[predicate] - sorted_scores
    ci = (
        find_lower_bound(predicate, rank_bound_scores, 
                         gamma, rho * (1-split_factor), score_sensitivity),
        find_upper_bound(predicate, rank_bound_scores, 
                         gamma, rho * split_factor, score_sensitivity)
    )
    return ci
    
def rank_bound_score(self, predicate, t):
    '''
    It corresponds to I(p) - I(top(t)) in the paper.
    '''
    return self.predicates_with_scores[predicate] - self.sorted_impacts[t-1]

def find_upper_bound(predicate, rank_bound_scores, gamma, rho, score_sensitivity):
    '''
    It is a noisy binary search.
    This procedure satisfies rho-zCDP
    '''
    psize = len(rank_bound_scores)
    N = np.ceil(np.log2(psize)).astype(int)
    sigma = 2.0 * score_sensitivity / np.sqrt(2*(rho/N))
#     print(2, score_sensitivity, 2, rho, N)
    xi = sigma * np.sqrt(2 * np.log(N / (1-(gamma+1)/2)))

    low, high = 1, psize
    while high > low:
        t = np.ceil((low+high)/2).astype(int)
        S = rank_bound_scores[t-1]
        S_hat = S + np.random.normal(scale=sigma)
#         print(predicate, score_sensitivity, sigma, gamma, N, xi, t, S, S_hat)
        if S_hat > xi:
            high = max(t-1, 1)
        else:
            low = min(t+1, psize)
    return high
    
def find_lower_bound(predicate, rank_bound_scores, gamma, rho, score_sensitivity):
    '''
    It is a noisy binary search.
    '''
    psize = len(rank_bound_scores)
    N = np.ceil(np.log2(psize)).astype(int)
    sigma = 2.0 * score_sensitivity / np.sqrt(2*(rho/N))
    xi = sigma * np.sqrt(2 * np.log(N / (1-gamma)))

    low, high = 1, psize
    while high > low:
        t = np.floor((low+high)/2).astype(int)  # here exists change
        S = rank_bound_scores[t-1]
        S_hat = S + np.random.normal(scale=sigma)
        if S_hat < -xi:  # here exists change
            low = min(t+1, psize)  # here exists change
        else:
            high = max(t-1, 1)  # here exists change
    return high