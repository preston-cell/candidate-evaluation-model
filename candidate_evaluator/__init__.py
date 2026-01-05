"""
Candidate Evaluator - AI-powered candidate assessment tool
"""

__version__ = "1.0.0"
__author__ = "Your Name"
__license__ = "MIT"

from candidate_evaluator.core.evaluator import CandidateEvaluator
from candidate_evaluator.core.models import EvaluationResult, CriterionScore
from candidate_evaluator.core.research_models import ResearchEvaluationReport

__all__ = ["CandidateEvaluator", "EvaluationResult", "CriterionScore", "ResearchEvaluationReport"]
