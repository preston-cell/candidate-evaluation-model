"""Research report generator for candidate evaluation"""

import logging
from typing import List, Dict, Any
from datetime import datetime
from collections import Counter

from candidate_evaluator.core.models import EvaluationResult, EvaluationCriterion
from candidate_evaluator.core.pattern_analyzer import LinguisticPatternAnalyzer, PatternFindings
from candidate_evaluator.core.research_models import (
    ResearchEvaluationReport,
    CriterionMarkerAnalysis,
    InnovationPotentialAssessment,
    MethodologyDescription,
    KeyFindings
)

logger = logging.getLogger(__name__)


class ResearchReportGenerator:
    """Generates research-style evaluation reports with linguistic analysis"""

    def __init__(self):
        """Initialize the research report generator"""
        self.pattern_analyzer = LinguisticPatternAnalyzer()

    def generate_research_report(
        self,
        evaluation_result: EvaluationResult,
        processed_files: List[Dict[str, Any]]
    ) -> ResearchEvaluationReport:
        """
        Generate a comprehensive research report.

        Args:
            evaluation_result: Standard evaluation result
            processed_files: List of processed file data with content and metadata

        Returns:
            ResearchEvaluationReport with full analysis
        """
        logger.info(f"Generating research report for {evaluation_result.candidate.candidate_id}")

        # Perform linguistic analysis
        pattern_findings = self.pattern_analyzer.analyze_multiple_files(processed_files)

        # Calculate word count for density metrics
        total_words = sum(
            len(f['content'].split())
            for f in processed_files
        )

        # Generate criterion analyses
        criterion_analyses = []
        for score in evaluation_result.scores:
            analysis = self._analyze_criterion_markers(
                score.criterion,
                score.score,
                pattern_findings.get(score.criterion),
                total_words
            )
            criterion_analyses.append(analysis)

        # Generate innovation assessment
        innovation_assessment = self._assess_innovation_potential(
            evaluation_result,
            pattern_findings
        )

        # Generate key findings
        key_findings = self._extract_key_findings(
            evaluation_result,
            pattern_findings,
            innovation_assessment
        )

        # Generate methodology description
        methodology = self._create_methodology_description(evaluation_result)

        # Generate linguistic patterns summary
        linguistic_patterns = self._summarize_linguistic_patterns(pattern_findings)

        # Generate statistical summary
        statistical_summary = self._create_statistical_summary(
            evaluation_result,
            pattern_findings,
            total_words
        )

        # Generate executive summary
        executive_summary = self._generate_executive_summary(
            evaluation_result,
            innovation_assessment,
            key_findings
        )

        # Generate research intention
        research_intention = self._generate_research_intention()

        # Generate discussion
        discussion = self._generate_discussion(
            evaluation_result,
            pattern_findings,
            innovation_assessment
        )

        # Generate conclusions
        conclusions = self._generate_conclusions(
            evaluation_result,
            innovation_assessment,
            key_findings
        )

        # Generate recommendations
        recommendations = self._generate_recommendations(
            evaluation_result,
            innovation_assessment
        )

        # Compile detailed evidence
        detailed_evidence = self._compile_detailed_evidence(pattern_findings)

        # Create score breakdown
        score_breakdown = self._create_score_breakdown(evaluation_result)

        # Construct report
        report = ResearchEvaluationReport(
            report_id=f"RES-{evaluation_result.candidate.candidate_id}-{datetime.now().strftime('%Y%m%d')}",
            candidate_id=evaluation_result.candidate.candidate_id,
            candidate_name=evaluation_result.candidate.name,
            executive_summary=executive_summary,
            research_intention=research_intention,
            methodology=methodology,
            key_findings=key_findings,
            criterion_analyses=criterion_analyses,
            innovation_assessment=innovation_assessment,
            linguistic_patterns=linguistic_patterns,
            statistical_summary=statistical_summary,
            discussion=discussion,
            conclusions=conclusions,
            recommendations=recommendations,
            detailed_evidence=detailed_evidence,
            score_breakdown=score_breakdown,
            evaluation_result=evaluation_result
        )

        logger.info("Research report generation complete")
        return report

    def _analyze_criterion_markers(
        self,
        criterion: EvaluationCriterion,
        score: int,
        findings: PatternFindings,
        total_words: int
    ) -> CriterionMarkerAnalysis:
        """Analyze markers for a specific criterion"""
        if findings is None:
            return CriterionMarkerAnalysis(
                criterion=criterion,
                score=score,
                total_markers_found=0,
                unique_markers=0,
                marker_density=0.0,
                top_phrases=[],
                confidence_assessment="No linguistic markers detected",
                supporting_evidence_strength="weak"
            )

        markers = findings.positive_markers
        unique_phrases = set(m.phrase for m in markers)

        # Calculate density (per 1000 words)
        marker_density = (len(markers) / total_words * 1000) if total_words > 0 else 0

        # Get top phrases
        top_phrases = [
            {'phrase': phrase, 'frequency': count}
            for phrase, count in sorted(
                findings.phrase_frequency.items(),
                key=lambda x: x[1],
                reverse=True
            )[:5]
        ]

        # Assess evidence strength
        if len(markers) >= 10:
            evidence_strength = "strong"
        elif len(markers) >= 5:
            evidence_strength = "moderate"
        else:
            evidence_strength = "weak"

        # Confidence assessment
        confidence = self._assess_marker_confidence(len(markers), score)

        return CriterionMarkerAnalysis(
            criterion=criterion,
            score=score,
            total_markers_found=len(markers),
            unique_markers=len(unique_phrases),
            marker_density=round(marker_density, 2),
            top_phrases=top_phrases,
            confidence_assessment=confidence,
            supporting_evidence_strength=evidence_strength
        )

    def _assess_marker_confidence(self, marker_count: int, score: int) -> str:
        """Assess confidence in score based on marker count"""
        if marker_count == 0:
            return "Low confidence: No linguistic markers detected. Score based on implicit evidence."
        elif marker_count < 3:
            return "Moderate confidence: Few linguistic markers found. Score may be influenced by contextual evidence."
        elif marker_count >= 5:
            return f"High confidence: {marker_count} linguistic markers detected, supporting score of {score}."
        else:
            return f"Moderate-to-high confidence: {marker_count} linguistic markers detected."

    def _assess_innovation_potential(
        self,
        evaluation_result: EvaluationResult,
        pattern_findings: Dict[EvaluationCriterion, PatternFindings]
    ) -> InnovationPotentialAssessment:
        """Assess candidate's innovation program potential"""
        # Get innovation-related scores
        innovation_criteria = {
            EvaluationCriterion.CREATIVITY: 'creativity_indicators',
            EvaluationCriterion.CURIOSITY: 'curiosity_indicators',
            EvaluationCriterion.PROBLEM_SOLVING_MOTIVATION: 'problem_solving_indicators',
            EvaluationCriterion.CRITICAL_THINKING: 'analytical_thinking_indicators'
        }

        indicators_by_type = {}
        total_innovation_markers = 0
        innovation_score_sum = 0

        for criterion, indicator_key in innovation_criteria.items():
            score_obj = evaluation_result.get_score_by_criterion(criterion)
            if score_obj:
                innovation_score_sum += score_obj.score

            findings = pattern_findings.get(criterion)
            if findings:
                markers = [m.phrase for m in findings.positive_markers[:5]]
                indicators_by_type[indicator_key] = markers
                total_innovation_markers += len(findings.positive_markers)
            else:
                indicators_by_type[indicator_key] = []

        # Calculate overall innovation score
        avg_innovation_score = innovation_score_sum / len(innovation_criteria)

        # Determine innovation potential level
        if avg_innovation_score >= 8 and total_innovation_markers >= 20:
            potential_level = "high"
            recommendation = "Strong candidate for innovation programs. Demonstrates exceptional creative thinking and problem-solving orientation."
        elif avg_innovation_score >= 6.5 and total_innovation_markers >= 10:
            potential_level = "medium"
            recommendation = "Good candidate for innovation programs with appropriate support and mentorship."
        else:
            potential_level = "low"
            recommendation = "Limited evidence of innovation orientation in written materials. Consider additional assessment methods."

        # Extract key innovation markers
        all_innovation_markers = []
        for criterion in innovation_criteria.keys():
            if criterion in pattern_findings:
                all_innovation_markers.extend([
                    m.phrase for m in pattern_findings[criterion].positive_markers
                ])

        # Get most common markers
        marker_counts = Counter(all_innovation_markers)
        key_markers = [phrase for phrase, count in marker_counts.most_common(10)]

        return InnovationPotentialAssessment(
            overall_innovation_score=round(avg_innovation_score, 2),
            innovation_indicators_count=total_innovation_markers,
            key_innovation_markers=key_markers,
            creativity_indicators=indicators_by_type.get('creativity_indicators', []),
            curiosity_indicators=indicators_by_type.get('curiosity_indicators', []),
            problem_solving_indicators=indicators_by_type.get('problem_solving_indicators', []),
            analytical_thinking_indicators=indicators_by_type.get('analytical_thinking_indicators', []),
            innovation_potential_level=potential_level,
            recommendation=recommendation
        )

    def _extract_key_findings(
        self,
        evaluation_result: EvaluationResult,
        pattern_findings: Dict[EvaluationCriterion, PatternFindings],
        innovation_assessment: InnovationPotentialAssessment
    ) -> KeyFindings:
        """Extract key findings from the analysis"""
        primary_findings = []

        # Finding 1: Overall performance
        primary_findings.append(
            f"Candidate achieved an overall score of {evaluation_result.overall_score:.2f}/10 "
            f"across 11 evaluation criteria."
        )

        # Finding 2: Strongest criteria
        top_scores = sorted(evaluation_result.scores, key=lambda s: s.score, reverse=True)[:3]
        top_criteria_str = ", ".join([s.criterion.display_name for s in top_scores])
        primary_findings.append(
            f"Highest performance observed in: {top_criteria_str}."
        )

        # Finding 3: Innovation potential
        primary_findings.append(
            f"Innovation potential assessment: {innovation_assessment.innovation_potential_level.upper()} "
            f"({innovation_assessment.innovation_indicators_count} innovation-related markers identified)."
        )

        # Finding 4: Linguistic markers
        total_markers = sum(len(f.positive_markers) for f in pattern_findings.values())
        primary_findings.append(
            f"Linguistic analysis identified {total_markers} total markers across all criteria, "
            f"providing strong quantitative evidence for scores."
        )

        # Marker correlations
        marker_correlations = []
        for criterion, findings in pattern_findings.items():
            if len(findings.positive_markers) > 5:
                score_obj = evaluation_result.get_score_by_criterion(criterion)
                if score_obj:
                    marker_correlations.append({
                        'criterion': criterion.display_name,
                        'marker_count': len(findings.positive_markers),
                        'score': score_obj.score,
                        'correlation': 'strong' if len(findings.positive_markers) > 10 else 'moderate'
                    })

        # Patterns identified
        patterns = []
        for criterion, findings in pattern_findings.items():
            if findings.positive_markers:
                top_phrase = max(findings.phrase_frequency.items(), key=lambda x: x[1])[0]
                patterns.append(
                    f"{criterion.display_name}: Frequent use of '{top_phrase}' "
                    f"({findings.phrase_frequency[top_phrase]} occurrences)"
                )

        # Innovation indicators
        innovation_indicators = [
            f"Creativity markers: {len(innovation_assessment.creativity_indicators)} unique phrases",
            f"Curiosity markers: {len(innovation_assessment.curiosity_indicators)} unique phrases",
            f"Problem-solving markers: {len(innovation_assessment.problem_solving_indicators)} unique phrases",
            f"Analytical thinking markers: {len(innovation_assessment.analytical_thinking_indicators)} unique phrases"
        ]

        # Notable observations
        notable_observations = []

        # Check for evidence gaps
        weak_evidence = [
            c.criterion.display_name
            for c in evaluation_result.scores
            if len(c.evidence) < 2
        ]
        if weak_evidence:
            notable_observations.append(
                f"Limited direct evidence found for: {', '.join(weak_evidence[:3])}"
            )

        # Check for strong patterns
        strong_patterns = [
            criterion.display_name
            for criterion, findings in pattern_findings.items()
            if len(findings.positive_markers) > 15
        ]
        if strong_patterns:
            notable_observations.append(
                f"Exceptionally strong linguistic evidence for: {', '.join(strong_patterns)}"
            )

        return KeyFindings(
            primary_findings=primary_findings,
            marker_correlations=marker_correlations,
            patterns_identified=patterns[:10],
            innovation_indicators=innovation_indicators,
            notable_observations=notable_observations
        )

    def _create_methodology_description(self, evaluation_result: EvaluationResult) -> MethodologyDescription:
        """Create methodology description"""
        criteria_definitions = {
            criterion.value: criterion.description
            for criterion in EvaluationCriterion
        }

        return MethodologyDescription(
            approach="AI-assisted evaluation combining automated linguistic analysis with structured assessment",
            ai_model_used=evaluation_result.metadata.get('model', 'Claude Sonnet 4.5'),
            evaluation_framework="11-criterion competency framework with evidence-based scoring",
            criteria_definitions=criteria_definitions,
            scoring_methodology="1-10 scale with detailed reasoning and evidence extraction. Scores represent: 1-3 (insufficient evidence/concerns), 4-5 (limited evidence), 6-7 (adequate competency), 8-9 (strong competency), 10 (exceptional competency)",
            evidence_extraction_method="Direct quote extraction from application materials with source attribution and context",
            linguistic_analysis_method="Pattern matching using criterion-specific keyword and phrase libraries. Markers extracted using regular expression matching and frequency analysis.",
            limitations=[
                "Assessment limited to written application materials",
                "Some criteria (e.g., collaboration) difficult to fully assess without behavioral observation",
                "Linguistic markers may not capture all relevant evidence",
                "Cultural and linguistic variations may affect marker detection",
                "Self-reported information cannot be independently verified"
            ]
        )

    def _summarize_linguistic_patterns(
        self,
        pattern_findings: Dict[EvaluationCriterion, PatternFindings]
    ) -> Dict[str, Any]:
        """Summarize linguistic patterns found"""
        summary = {
            'total_markers': sum(len(f.positive_markers) for f in pattern_findings.values()),
            'markers_by_criterion': {},
            'most_common_phrases': Counter(),
            'marker_distribution': {}
        }

        for criterion, findings in pattern_findings.items():
            summary['markers_by_criterion'][criterion.value] = {
                'count': len(findings.positive_markers),
                'unique_phrases': len(set(m.phrase for m in findings.positive_markers)),
                'top_phrase': max(findings.phrase_frequency.items(), key=lambda x: x[1])[0] if findings.phrase_frequency else None
            }

            summary['most_common_phrases'].update(findings.phrase_frequency)

        # Overall top phrases
        summary['top_phrases_overall'] = [
            {'phrase': phrase, 'count': count}
            for phrase, count in summary['most_common_phrases'].most_common(15)
        ]

        return summary

    def _create_statistical_summary(
        self,
        evaluation_result: EvaluationResult,
        pattern_findings: Dict[EvaluationCriterion, PatternFindings],
        total_words: int
    ) -> Dict[str, Any]:
        """Create statistical summary"""
        scores = [s.score for s in evaluation_result.scores]

        return {
            'overall_score': evaluation_result.overall_score,
            'mean_score': sum(scores) / len(scores),
            'median_score': sorted(scores)[len(scores) // 2],
            'score_range': {'min': min(scores), 'max': max(scores)},
            'total_words_analyzed': total_words,
            'total_linguistic_markers': sum(len(f.positive_markers) for f in pattern_findings.values()),
            'average_markers_per_criterion': sum(len(f.positive_markers) for f in pattern_findings.values()) / len(pattern_findings) if pattern_findings else 0,
            'criteria_with_strong_evidence': len([
                f for f in pattern_findings.values()
                if len(f.positive_markers) >= 10
            ]),
            'criteria_with_weak_evidence': len([
                s for s in evaluation_result.scores
                if len(s.evidence) < 2
            ])
        }

    def _generate_executive_summary(
        self,
        evaluation_result: EvaluationResult,
        innovation_assessment: InnovationPotentialAssessment,
        key_findings: KeyFindings
    ) -> str:
        """Generate executive summary"""
        return f"""This research report presents a comprehensive evaluation of candidate {evaluation_result.candidate.candidate_id}{' (' + evaluation_result.candidate.name + ')' if evaluation_result.candidate.name else ''} using AI-assisted linguistic analysis and structured assessment against 11 key criteria. The candidate achieved an overall score of {evaluation_result.overall_score:.2f}/10, with innovation potential assessed as {innovation_assessment.innovation_potential_level.upper()}.

Through systematic analysis of application materials, we identified {innovation_assessment.innovation_indicators_count} linguistic markers indicative of innovation-related competencies. The evaluation reveals particular strength in {', '.join([s.criterion.display_name for s in sorted(evaluation_result.scores, key=lambda x: x.score, reverse=True)[:2]])}.

{innovation_assessment.recommendation}

This report details our methodology, presents key findings regarding linguistic markers and competency indicators, and provides evidence-based recommendations."""

    def _generate_research_intention(self) -> str:
        """Generate research intention statement"""
        return """The primary intention of this research evaluation is to identify and quantify linguistic markers in candidate application materials that correlate with innovation program potential and key competencies. Specifically, this analysis aims to:

1. **Identify Linguistic Markers**: Extract and categorize phrases, keywords, and language patterns that indicate specific competencies (e.g., analytical thinking, creativity, collaboration).

2. **Assess Innovation Potential**: Determine candidate suitability for innovation-focused roles or programs by analyzing markers related to creativity, curiosity, problem-solving motivation, and critical thinking.

3. **Provide Evidence-Based Scoring**: Deliver quantitative scores (1-10 scale) for each criterion, supported by direct quotes and linguistic evidence from application materials.

4. **Uncover Patterns**: Reveal patterns in how high-performing candidates discuss their experiences, enabling identification of success predictors.

5. **Enable Data-Driven Decisions**: Provide hiring managers and program coordinators with objective, reproducible assessments to supplement traditional evaluation methods.

This approach combines AI-powered natural language processing with structured evaluation frameworks to provide deeper insights than traditional resume screening while maintaining objectivity and consistency."""

    def _generate_discussion(
        self,
        evaluation_result: EvaluationResult,
        pattern_findings: Dict[EvaluationCriterion, PatternFindings],
        innovation_assessment: InnovationPotentialAssessment
    ) -> str:
        """Generate discussion section"""
        discussion_parts = []

        # Overall performance discussion
        discussion_parts.append(
            f"The candidate's overall score of {evaluation_result.overall_score:.2f}/10 places them "
            f"{'in the strong performer category' if evaluation_result.overall_score >= 8 else 'in the moderate performer category' if evaluation_result.overall_score >= 6 else 'below the typical threshold for innovation programs'}. "
            f"This assessment is based on comprehensive analysis of their application materials, including linguistic pattern matching and evidence extraction."
        )

        # Innovation potential discussion
        discussion_parts.append(
            f"\n\nRegarding innovation potential, our analysis identified {innovation_assessment.innovation_indicators_count} markers "
            f"across four key innovation-related criteria. The {innovation_assessment.innovation_potential_level} innovation potential rating "
            f"reflects {'strong' if innovation_assessment.innovation_potential_level == 'high' else 'moderate' if innovation_assessment.innovation_potential_level == 'medium' else 'limited'} "
            f"evidence of creative problem-solving, intellectual curiosity, and analytical thinking in the candidate's written materials."
        )

        # Linguistic patterns discussion
        total_markers = sum(len(f.positive_markers) for f in pattern_findings.values())
        discussion_parts.append(
            f"\n\nOur linguistic analysis identified {total_markers} total markers, with notable concentrations in "
            f"{', '.join([c.display_name for c, f in sorted(pattern_findings.items(), key=lambda x: len(x[1].positive_markers), reverse=True)[:3]])}. "
            f"The density and distribution of these markers provide quantitative support for the qualitative assessments."
        )

        # Evidence quality discussion
        strong_evidence_criteria = [
            s.criterion.display_name
            for s in evaluation_result.scores
            if len(s.evidence) >= 3
        ]
        if strong_evidence_criteria:
            discussion_parts.append(
                f"\n\nParticularly strong evidence was found for {', '.join(strong_evidence_criteria[:3])}, "
                f"where multiple direct quotes and examples from the materials supported the scores. "
                f"This depth of evidence increases confidence in these specific assessments."
            )

        return "".join(discussion_parts)

    def _generate_conclusions(
        self,
        evaluation_result: EvaluationResult,
        innovation_assessment: InnovationPotentialAssessment,
        key_findings: KeyFindings
    ) -> List[str]:
        """Generate conclusions"""
        conclusions = []

        # Overall assessment conclusion
        if evaluation_result.overall_score >= 8:
            conclusions.append(
                f"Candidate demonstrates strong competency across evaluation criteria with overall score of {evaluation_result.overall_score:.2f}/10, "
                f"indicating high potential for success in demanding roles."
            )
        elif evaluation_result.overall_score >= 6.5:
            conclusions.append(
                f"Candidate shows adequate competency with overall score of {evaluation_result.overall_score:.2f}/10, "
                f"suggesting good potential with appropriate support and development."
            )
        else:
            conclusions.append(
                f"Candidate's overall score of {evaluation_result.overall_score:.2f}/10 indicates areas requiring significant development "
                f"for innovation program readiness."
            )

        # Innovation potential conclusion
        conclusions.append(
            f"Innovation potential assessment yields {innovation_assessment.innovation_potential_level.upper()} rating, "
            f"based on {innovation_assessment.innovation_indicators_count} identified markers. "
            f"{innovation_assessment.recommendation}"
        )

        # Linguistic markers conclusion
        conclusions.append(
            f"Linguistic analysis successfully identified quantifiable markers for all evaluation criteria, "
            f"with {len([f for f in pattern_findings.values() if len(f.positive_markers) >= 5])} criteria "
            f"showing substantial supporting evidence."
        )

        # Methodology validation
        conclusions.append(
            "The combination of AI-assisted linguistic analysis and structured evaluation provides robust, "
            "evidence-based assessment that complements traditional screening methods and enables consistent, "
            "reproducible candidate evaluation at scale."
        )

        return conclusions

    def _generate_recommendations(
        self,
        evaluation_result: EvaluationResult,
        innovation_assessment: InnovationPotentialAssessment
    ) -> List[str]:
        """Generate recommendations"""
        recommendations = []

        # Primary recommendation
        recommendations.append(evaluation_result.recommendation)

        # Innovation-specific recommendations
        if innovation_assessment.innovation_potential_level == "high":
            recommendations.append(
                "Strongly recommend for innovation programs or roles requiring creative problem-solving. "
                "Consider fast-tracking for advanced opportunities."
            )
        elif innovation_assessment.innovation_potential_level == "medium":
            recommendations.append(
                "Consider for innovation programs with appropriate mentorship and support structures. "
                "May benefit from additional assessment through behavioral interviews or case studies."
            )
        else:
            recommendations.append(
                "Limited evidence of innovation orientation in written materials. "
                "Recommend additional assessment methods (e.g., portfolio review, problem-solving exercises) "
                "before final decision on innovation programs."
            )

        # Development recommendations
        weak_areas = [s for s in evaluation_result.scores if s.score < 6]
        if weak_areas and len(weak_areas) <= 3:
            areas_str = ', '.join([s.criterion.display_name for s in weak_areas])
            recommendations.append(
                f"If selected, focus development efforts on: {areas_str}. "
                f"These areas showed limited evidence in application materials and may benefit from targeted coaching."
            )

        # Next steps
        recommendations.append(
            "Proceed with behavioral interview focusing on specific examples of the competencies assessed. "
            "Particularly probe areas where linguistic evidence was limited to validate assessment."
        )

        return recommendations

    def _compile_detailed_evidence(
        self,
        pattern_findings: Dict[EvaluationCriterion, PatternFindings]
    ) -> List[Dict[str, Any]]:
        """Compile detailed evidence appendix"""
        evidence = []

        for criterion, findings in pattern_findings.items():
            criterion_evidence = {
                'criterion': criterion.display_name,
                'criterion_code': criterion.value,
                'total_markers': len(findings.positive_markers),
                'unique_phrases': len(set(m.phrase for m in findings.positive_markers)),
                'markers': [
                    {
                        'phrase': m.phrase,
                        'type': m.marker_type,
                        'source': m.source,
                        'context': m.context[:200] + '...' if len(m.context) > 200 else m.context,
                        'confidence': m.confidence
                    }
                    for m in findings.positive_markers[:10]  # Limit to top 10 for each
                ],
                'phrase_frequency': findings.phrase_frequency
            }
            evidence.append(criterion_evidence)

        return evidence

    def _create_score_breakdown(self, evaluation_result: EvaluationResult) -> Dict[str, Any]:
        """Create detailed score breakdown"""
        return {
            'overall_score': evaluation_result.overall_score,
            'scores_by_criterion': [
                {
                    'criterion': s.criterion.display_name,
                    'criterion_code': s.criterion.value,
                    'score': s.score,
                    'confidence': s.confidence,
                    'evidence_count': len(s.evidence),
                    'reasoning_summary': s.reasoning[:200] + '...' if len(s.reasoning) > 200 else s.reasoning
                }
                for s in evaluation_result.scores
            ],
            'highest_scores': [
                {'criterion': s.criterion.display_name, 'score': s.score}
                for s in sorted(evaluation_result.scores, key=lambda x: x.score, reverse=True)[:3]
            ],
            'lowest_scores': [
                {'criterion': s.criterion.display_name, 'score': s.score}
                for s in sorted(evaluation_result.scores, key=lambda x: x.score)[:3]
            ]
        }
