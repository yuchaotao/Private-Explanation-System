from privex.framework.meta_explanation_session import MetaExplanationSession
from privex.core.baseline.private_ci_of_influence import PrivateCIofInfluence
from privex.core.baseline.private_ci_of_question import PrivateCIofQuestion
from privex.core.baseline.private_ci_of_rank import PrivateCIofRank
from privex.core.baseline.private_topk_explanation_predicates import PrivateTopkExplanationPredicates

class ExplanationSession(MetaExplanationSession):
    private_ci_of_influence = PrivateCIofInfluence()
    private_ci_of_question = PrivateCIofQuestion()
    private_ci_of_rank = PrivateCIofRank()
    private_topk_explanation_predicates = PrivateTopkExplanationPredicates()