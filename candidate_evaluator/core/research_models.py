"""Data models for research-style analysis and reports"""

from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

from candidate_evaluator.core.models import EvaluationResult, EvaluationCriterion
from candidate_evaluator.core.pattern_analyzer import PatternFindings, LinguisticMarker


class CriterionMarkerAnalysis(BaseModel):
    """Analysis of markers for a specific criterion"""
    criterion: EvaluationCriterion
    score: int
    total_markers_found: int
    unique_markers: int
    marker_density: float  # Markers per 1000 words
    top_phrases: List[Dict[str, Any]]
    confidence_assessment: str
    supporting_evidence_strength: str  # 'strong', 'moderate', 'weak'


class InnovationPotentialAssessment(BaseModel):
    """Assessment of innovation program potential"""
    overall_innovation_score: float
    innovation_indicators_count: int
    key_innovation_markers: List[str]
    creativity_indicators: List[str]
    curiosity_indicators: List[str]
    problem_solving_indicators: List[str]
    analytical_thinking_indicators: List[str]
    innovation_potential_level: str  # 'high', 'medium', 'low'
    recommendation: str


class MethodologyDescription(BaseModel):
    """Description of evaluation methodology"""
    approach: str
    ai_model_used: str
    evaluation_framework: str
    criteria_definitions: Dict[str, str]
    scoring_methodology: str
    evidence_extraction_method: str
    linguistic_analysis_method: str
    limitations: List[str]


class KeyFindings(BaseModel):
    """Key findings from the analysis"""
    primary_findings: List[str]
    marker_correlations: List[Dict[str, Any]]
    patterns_identified: List[str]
    innovation_indicators: List[str]
    notable_observations: List[str]


class ResearchEvaluationReport(BaseModel):
    """Complete research-style evaluation report"""
    # Metadata
    report_id: str
    candidate_id: str
    candidate_name: Optional[str]
    report_date: datetime = Field(default_factory=datetime.now)

    # Research sections
    executive_summary: str
    research_intention: str
    methodology: MethodologyDescription

    # Findings
    key_findings: KeyFindings
    criterion_analyses: List[CriterionMarkerAnalysis]
    innovation_assessment: InnovationPotentialAssessment

    # Data
    linguistic_patterns: Dict[str, Any]
    statistical_summary: Dict[str, Any]

    # Conclusions
    discussion: str
    conclusions: List[str]
    recommendations: List[str]

    # Appendices
    detailed_evidence: List[Dict[str, Any]]
    score_breakdown: Dict[str, Any]

    # Original evaluation
    evaluation_result: EvaluationResult


class ComparativeResearchReport(BaseModel):
    """Comparative research report across multiple candidates"""
    report_id: str
    report_date: datetime = Field(default_factory=datetime.now)
    candidates_analyzed: int

    # Research sections
    research_objective: str
    methodology: MethodologyDescription

    # Comparative findings
    marker_prevalence_analysis: Dict[str, Any]
    innovation_marker_distribution: Dict[str, Any]
    criterion_performance_patterns: List[Dict[str, Any]]
    linguistic_pattern_comparison: Dict[str, Any]

    # Insights
    key_insights: List[str]
    candidate_segmentation: Dict[str, List[str]]
    success_predictors: List[Dict[str, Any]]

    # Conclusions
    conclusions: List[str]
    recommendations: List[str]

    # Individual reports
    individual_reports: List[ResearchEvaluationReport]


class MarkerCorrelation(BaseModel):
    """Correlation between markers and outcomes"""
    marker_phrase: str
    associated_criterion: EvaluationCriterion
    frequency: int
    correlation_with_high_scores: float
    statistical_significance: str
    example_contexts: List[str]
