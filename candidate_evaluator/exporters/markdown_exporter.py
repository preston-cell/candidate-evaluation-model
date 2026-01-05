"""Markdown export functionality"""

from pathlib import Path
from typing import Union, List
from datetime import datetime

from candidate_evaluator.core.models import EvaluationResult, ComparisonResult, CriterionScore


class MarkdownExporter:
    """Export evaluation results to Markdown format"""

    @staticmethod
    def export_evaluation(
        result: EvaluationResult,
        output_path: Union[str, Path],
        include_evidence: bool = True
    ) -> str:
        """
        Export evaluation result to Markdown file.

        Args:
            result: EvaluationResult object
            output_path: Path to output file
            include_evidence: Whether to include detailed evidence

        Returns:
            Path to exported file
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Build markdown content
        lines = []

        # Header
        lines.append(f"# Candidate Evaluation Report")
        lines.append("")
        lines.append(f"**Candidate ID**: {result.candidate.candidate_id}")
        if result.candidate.name:
            lines.append(f"**Name**: {result.candidate.name}")
        lines.append(f"**Evaluation Date**: {result.candidate.evaluation_date.strftime('%Y-%m-%d %H:%M')}")
        lines.append(f"**Materials Evaluated**: {', '.join(result.candidate.materials)}")
        lines.append("")

        # Overall Score Section
        lines.append("## Overall Assessment")
        lines.append("")
        lines.append(f"**Overall Score**: {result.overall_score:.2f}/10")
        lines.append(f"**Recommendation**: {result.recommendation}")
        lines.append("")
        lines.append(result.overall_assessment)
        lines.append("")

        # Strengths
        if result.strengths:
            lines.append("### Key Strengths")
            lines.append("")
            for strength in result.strengths:
                lines.append(f"- {strength}")
            lines.append("")

        # Areas for Development
        if result.areas_for_development:
            lines.append("### Areas for Development")
            lines.append("")
            for area in result.areas_for_development:
                lines.append(f"- {area}")
            lines.append("")

        # Detailed Scores
        lines.append("## Detailed Evaluation by Criterion")
        lines.append("")

        # Sort scores by score value (highest first)
        sorted_scores = sorted(result.scores, key=lambda s: s.score, reverse=True)

        for score in sorted_scores:
            lines.extend(MarkdownExporter._format_criterion_score(score, include_evidence))

        # Metadata
        if result.metadata:
            lines.append("---")
            lines.append("")
            lines.append("## Evaluation Metadata")
            lines.append("")
            for key, value in result.metadata.items():
                lines.append(f"- **{key}**: {value}")

        # Write to file
        content = "\n".join(lines)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)

        return str(output_path)

    @staticmethod
    def _format_criterion_score(score: CriterionScore, include_evidence: bool) -> List[str]:
        """Format a criterion score as markdown lines"""
        lines = []

        # Score bar visualization
        filled = '█' * score.score
        empty = '░' * (10 - score.score)
        score_bar = f"{filled}{empty}"

        lines.append(f"### {score.criterion.display_name}")
        lines.append("")
        lines.append(f"**Score**: {score.score}/10 `{score_bar}` (Confidence: {score.confidence})")
        lines.append("")
        lines.append(f"**Reasoning**: {score.reasoning}")
        lines.append("")

        if score.notes:
            lines.append(f"**Notes**: {score.notes}")
            lines.append("")

        if include_evidence and score.evidence:
            lines.append("**Evidence**:")
            lines.append("")
            for i, ev in enumerate(score.evidence, 1):
                lines.append(f"{i}. *From {ev.source}*:")
                lines.append(f"   > {ev.quote}")
                lines.append(f"   ")
                lines.append(f"   {ev.context}")
                lines.append("")

        return lines

    @staticmethod
    def export_comparison(
        result: ComparisonResult,
        output_path: Union[str, Path]
    ) -> str:
        """
        Export comparison result to Markdown file.

        Args:
            result: ComparisonResult object
            output_path: Path to output file

        Returns:
            Path to exported file
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        lines = []

        # Header
        lines.append("# Candidate Comparison Report")
        lines.append("")
        lines.append(f"**Comparison Date**: {result.comparison_date.strftime('%Y-%m-%d %H:%M')}")
        lines.append(f"**Candidates Compared**: {len(result.candidates)}")
        lines.append("")

        # Ranking
        lines.append("## Ranking")
        lines.append("")
        for i, candidate_id in enumerate(result.ranking, 1):
            # Find the candidate
            candidate_result = next(
                (c for c in result.candidates if c.candidate.candidate_id == candidate_id),
                None
            )
            if candidate_result:
                name = candidate_result.candidate.name or candidate_id
                score = candidate_result.overall_score
                lines.append(f"{i}. **{name}** (ID: {candidate_id}) - Score: {score:.2f}/10")

        lines.append("")

        # Comparison Matrix
        if result.comparison_matrix:
            lines.append("## Comparison by Criterion")
            lines.append("")

            for criterion, details in result.comparison_matrix.items():
                if isinstance(details, dict):
                    lines.append(f"### {criterion.replace('_', ' ').title()}")
                    lines.append("")
                    lines.append(f"**Best**: {details.get('best', 'N/A')}")
                    lines.append("")
                    lines.append(details.get('analysis', ''))
                    lines.append("")

        # Insights
        if result.insights:
            lines.append("## Key Insights")
            lines.append("")
            for insight in result.insights:
                lines.append(f"- {insight}")
            lines.append("")

        # Individual Summaries
        lines.append("## Individual Candidate Summaries")
        lines.append("")

        for candidate_result in result.candidates:
            candidate_id = candidate_result.candidate.candidate_id
            name = candidate_result.candidate.name or candidate_id

            lines.append(f"### {name}")
            lines.append("")
            lines.append(f"**Overall Score**: {candidate_result.overall_score:.2f}/10")
            lines.append(f"**Recommendation**: {candidate_result.recommendation}")
            lines.append("")

            if candidate_result.strengths:
                lines.append("**Strengths**:")
                for strength in candidate_result.strengths:
                    lines.append(f"- {strength}")
                lines.append("")

            if candidate_result.areas_for_development:
                lines.append("**Areas for Development**:")
                for area in candidate_result.areas_for_development:
                    lines.append(f"- {area}")
                lines.append("")

        # Write to file
        content = "\n".join(lines)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)

        return str(output_path)

    @staticmethod
    def export_batch_summary(
        results: List[EvaluationResult],
        output_path: Union[str, Path]
    ) -> str:
        """
        Export batch evaluation summary to Markdown.

        Args:
            results: List of EvaluationResult objects
            output_path: Path to output file

        Returns:
            Path to exported file
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        lines = []

        lines.append("# Batch Evaluation Summary")
        lines.append("")
        lines.append(f"**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        lines.append(f"**Total Candidates**: {len(results)}")
        lines.append("")

        # Sort by score
        sorted_results = sorted(results, key=lambda r: r.overall_score, reverse=True)

        # Summary table
        lines.append("## Candidate Rankings")
        lines.append("")
        lines.append("| Rank | Candidate | Overall Score | Recommendation |")
        lines.append("|------|-----------|---------------|----------------|")

        for i, result in enumerate(sorted_results, 1):
            name = result.candidate.name or result.candidate.candidate_id
            score = f"{result.overall_score:.2f}"
            rec = result.recommendation
            lines.append(f"| {i} | {name} | {score} | {rec} |")

        lines.append("")

        # Write to file
        content = "\n".join(lines)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)

        return str(output_path)
