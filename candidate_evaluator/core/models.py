"""Data models for candidate evaluation"""

from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, validator
from enum import Enum


class EvaluationCriterion(str, Enum):
    """Evaluation criteria enum"""
    CRITICAL_THINKING = "critical_thinking"
    COACHABILITY = "coachability"
    CURIOSITY = "curiosity"
    CREATIVITY = "creativity"
    COLLABORATION = "collaboration"
    FOLLOW_THROUGH = "follow_through"
    PROBLEM_SOLVING_MOTIVATION = "problem_solving_motivation"
    EVIDENCE_BASED = "evidence_based"
    DETAIL_ORIENTATION = "detail_orientation"
    COMMUNICATION = "communication"
    EXPERTISE_ENABLER = "expertise_enabler"

    @property
    def display_name(self) -> str:
        """Get human-readable name for criterion"""
        names = {
            "critical_thinking": "Critical Thinking / Logical Analysis",
            "coachability": "Coachability – Receptive to Feedback",
            "curiosity": "Curiosity",
            "creativity": "Demonstrated Creativity in Solution Development",
            "collaboration": "Collaborates with Others Effectively; Incorporates Inputs from Others",
            "follow_through": "Demonstrated Follow Through",
            "problem_solving_motivation": "Motivation to Solve Problems",
            "evidence_based": "Understands the Value of Evidence to Challenge Assumptions",
            "detail_orientation": "Works Toward Increasing Specificity / Detail Orientation",
            "communication": "Effective Communicator",
            "expertise_enabler": "Uses Own Expertise as an Enabler Rather Than a Limitation"
        }
        return names.get(self.value, self.value)

    @property
    def description(self) -> str:
        """Get description of what this criterion measures"""
        descriptions = {
            "critical_thinking": "Ability to analyze information objectively, identify patterns, and draw logical conclusions",
            "coachability": "Openness to feedback, willingness to learn, and ability to implement suggestions",
            "curiosity": "Drive to explore, ask questions, and seek deeper understanding",
            "creativity": "Ability to develop innovative solutions and think outside conventional approaches",
            "collaboration": "Capacity to work effectively with others and integrate diverse perspectives",
            "follow_through": "Consistency in completing tasks and following projects to completion",
            "problem_solving_motivation": "Intrinsic drive to tackle challenges and find solutions",
            "evidence_based": "Reliance on data and evidence rather than assumptions in decision-making",
            "detail_orientation": "Attention to specifics and commitment to thoroughness and accuracy",
            "communication": "Clarity, precision, and effectiveness in written and verbal expression",
            "expertise_enabler": "Leveraging subject matter knowledge to enable solutions rather than limit possibilities"
        }
        return descriptions.get(self.value, "")


class Evidence(BaseModel):
    """Evidence supporting a score"""
    quote: str = Field(description="Direct quote from materials")
    source: str = Field(description="Source document (e.g., 'resume.pdf', 'cover_letter.txt')")
    context: str = Field(description="Additional context about why this evidence is relevant")


class CriterionScore(BaseModel):
    """Score for a single evaluation criterion"""
    criterion: EvaluationCriterion
    score: int = Field(ge=1, le=10, description="Score from 1-10")
    reasoning: str = Field(description="Detailed reasoning for the score")
    evidence: List[Evidence] = Field(default_factory=list, description="Supporting evidence")
    confidence: str = Field(
        default="medium",
        description="Confidence level: low, medium, high"
    )
    notes: Optional[str] = Field(
        default=None,
        description="Additional notes, caveats, or areas where evidence was limited"
    )

    @validator('confidence')
    def validate_confidence(cls, v):
        if v.lower() not in ['low', 'medium', 'high']:
            raise ValueError('Confidence must be low, medium, or high')
        return v.lower()


class CandidateProfile(BaseModel):
    """Profile of a candidate being evaluated"""
    candidate_id: str = Field(description="Unique identifier for the candidate")
    name: Optional[str] = Field(default=None, description="Candidate name if provided")
    materials: List[str] = Field(description="List of material file paths evaluated")
    evaluation_date: datetime = Field(default_factory=datetime.now)


class EvaluationResult(BaseModel):
    """Complete evaluation result for a candidate"""
    candidate: CandidateProfile
    scores: List[CriterionScore]
    overall_score: float = Field(
        description="Weighted average of all criterion scores"
    )
    overall_assessment: str = Field(
        description="High-level summary assessment of the candidate"
    )
    strengths: List[str] = Field(
        default_factory=list,
        description="Key strengths identified"
    )
    areas_for_development: List[str] = Field(
        default_factory=list,
        description="Areas where evidence was limited or scores were lower"
    )
    recommendation: str = Field(
        description="Overall recommendation (e.g., 'Strong fit', 'Potential fit with development', etc.)"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata (model used, processing time, etc.)"
    )

    def get_score_by_criterion(self, criterion: EvaluationCriterion) -> Optional[CriterionScore]:
        """Get score for a specific criterion"""
        for score in self.scores:
            if score.criterion == criterion:
                return score
        return None

    def to_summary_dict(self) -> Dict[str, Any]:
        """Convert to summary dictionary for quick reference"""
        return {
            "candidate_id": self.candidate.candidate_id,
            "candidate_name": self.candidate.name,
            "overall_score": self.overall_score,
            "evaluation_date": self.candidate.evaluation_date.isoformat(),
            "recommendation": self.recommendation,
            "overall_assessment": self.overall_assessment,
            "strengths": self.strengths,
            "areas_for_development": self.areas_for_development,
            "scores": {
                score.criterion.value: score.score
                for score in self.scores
            }
        }


class ComparisonResult(BaseModel):
    """Comparison of multiple candidates"""
    candidates: List[EvaluationResult]
    comparison_date: datetime = Field(default_factory=datetime.now)
    ranking: List[str] = Field(
        description="Candidate IDs in ranked order (best to worst)"
    )
    comparison_matrix: Dict[str, Dict[str, Any]] = Field(
        description="Matrix comparing candidates across criteria"
    )
    insights: List[str] = Field(
        default_factory=list,
        description="Key insights from the comparison"
    )
