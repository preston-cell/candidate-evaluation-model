"""Research paper exporter for detailed analytical reports"""

from pathlib import Path
from typing import Union
from datetime import datetime

from candidate_evaluator.core.research_models import ResearchEvaluationReport


class ResearchPaperExporter:
    """Export research evaluation reports as formatted papers"""

    @staticmethod
    def export_research_paper(
        report: ResearchEvaluationReport,
        output_path: Union[str, Path],
        format: str = 'markdown'
    ) -> str:
        """
        Export research report as formatted paper.

        Args:
            report: Research evaluation report
            output_path: Path to output file
            format: Output format ('markdown' or 'latex')

        Returns:
            Path to exported file
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        if format == 'markdown':
            content = ResearchPaperExporter._generate_markdown_paper(report)
        elif format == 'latex':
            content = ResearchPaperExporter._generate_latex_paper(report)
        else:
            raise ValueError(f"Unsupported format: {format}")

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)

        return str(output_path)

    @staticmethod
    def _generate_markdown_paper(report: ResearchEvaluationReport) -> str:
        """Generate markdown formatted research paper"""
        lines = []

        # Title and metadata
        lines.append("# Candidate Evaluation Research Report")
        lines.append("")
        lines.append(f"**Linguistic Marker Analysis and Innovation Potential Assessment**")
        lines.append("")
        lines.append("---")
        lines.append("")

        # Metadata
        lines.append("## Report Metadata")
        lines.append("")
        lines.append(f"- **Report ID**: {report.report_id}")
        lines.append(f"- **Candidate ID**: {report.candidate_id}")
        if report.candidate_name:
            lines.append(f"- **Candidate Name**: {report.candidate_name}")
        lines.append(f"- **Report Date**: {report.report_date.strftime('%B %d, %Y')}")
        lines.append(f"- **AI Model Used**: {report.methodology.ai_model_used}")
        lines.append("")
        lines.append("---")
        lines.append("")

        # Executive Summary
        lines.append("## Executive Summary")
        lines.append("")
        lines.append(report.executive_summary)
        lines.append("")
        lines.append("---")
        lines.append("")

        # Research Intention
        lines.append("## 1. Research Intention and Objectives")
        lines.append("")
        lines.append(report.research_intention)
        lines.append("")

        # Methodology
        lines.append("## 2. Methodology")
        lines.append("")
        lines.append(f"### 2.1 Evaluation Approach")
        lines.append("")
        lines.append(report.methodology.approach)
        lines.append("")

        lines.append(f"### 2.2 Assessment Framework")
        lines.append("")
        lines.append(report.methodology.evaluation_framework)
        lines.append("")

        lines.append(f"### 2.3 Scoring Methodology")
        lines.append("")
        lines.append(report.methodology.scoring_methodology)
        lines.append("")

        lines.append(f"### 2.4 Linguistic Analysis Method")
        lines.append("")
        lines.append(report.methodology.linguistic_analysis_method)
        lines.append("")

        lines.append(f"### 2.5 Evaluation Criteria")
        lines.append("")
        lines.append("The following 11 criteria were assessed:")
        lines.append("")
        for i, (criterion_code, description) in enumerate(report.methodology.criteria_definitions.items(), 1):
            criterion_name = criterion_code.replace('_', ' ').title()
            lines.append(f"{i}. **{criterion_name}**: {description}")
        lines.append("")

        lines.append(f"### 2.6 Limitations")
        lines.append("")
        for limitation in report.methodology.limitations:
            lines.append(f"- {limitation}")
        lines.append("")

        # Key Findings
        lines.append("## 3. Key Findings")
        lines.append("")

        lines.append("### 3.1 Primary Findings")
        lines.append("")
        for i, finding in enumerate(report.key_findings.primary_findings, 1):
            lines.append(f"{i}. {finding}")
        lines.append("")

        lines.append("### 3.2 Linguistic Marker Analysis")
        lines.append("")
        lines.append(f"**Total Markers Identified**: {report.linguistic_patterns['total_markers']}")
        lines.append("")
        lines.append("**Markers by Criterion**:")
        lines.append("")

        # Create table of markers by criterion
        lines.append("| Criterion | Total Markers | Unique Phrases | Most Common |")
        lines.append("|-----------|---------------|----------------|-------------|")

        for criterion_code, data in report.linguistic_patterns['markers_by_criterion'].items():
            criterion_name = criterion_code.replace('_', ' ').title()
            lines.append(
                f"| {criterion_name} | {data['count']} | {data['unique_phrases']} | "
                f"{data['top_phrase'] if data['top_phrase'] else 'N/A'} |"
            )
        lines.append("")

        lines.append("### 3.3 Most Frequent Phrases Overall")
        lines.append("")
        for i, phrase_data in enumerate(report.linguistic_patterns['top_phrases_overall'][:10], 1):
            lines.append(f"{i}. **\"{phrase_data['phrase']}\"** - {phrase_data['count']} occurrences")
        lines.append("")

        lines.append("### 3.4 Marker-Score Correlations")
        lines.append("")
        if report.key_findings.marker_correlations:
            lines.append("| Criterion | Markers Found | Score | Correlation |")
            lines.append("|-----------|---------------|-------|-------------|")
            for correlation in report.key_findings.marker_correlations[:10]:
                lines.append(
                    f"| {correlation['criterion']} | {correlation['marker_count']} | "
                    f"{correlation['score']}/10 | {correlation['correlation'].title()} |"
                )
            lines.append("")
        else:
            lines.append("*No significant correlations identified.*")
            lines.append("")

        lines.append("### 3.5 Innovation Indicators")
        lines.append("")
        for indicator in report.key_findings.innovation_indicators:
            lines.append(f"- {indicator}")
        lines.append("")

        if report.key_findings.notable_observations:
            lines.append("### 3.6 Notable Observations")
            lines.append("")
            for observation in report.key_findings.notable_observations:
                lines.append(f"- {observation}")
            lines.append("")

        # Innovation Potential Assessment
        lines.append("## 4. Innovation Potential Assessment")
        lines.append("")

        innov = report.innovation_assessment

        lines.append(f"### 4.1 Overall Innovation Score")
        lines.append("")
        lines.append(f"**{innov.overall_innovation_score:.2f}/10** - {innov.innovation_potential_level.upper()} Potential")
        lines.append("")

        lines.append(f"### 4.2 Innovation Indicators")
        lines.append("")
        lines.append(f"**Total Innovation Markers Identified**: {innov.innovation_indicators_count}")
        lines.append("")

        if innov.creativity_indicators:
            lines.append("**Creativity Indicators**:")
            for indicator in innov.creativity_indicators[:5]:
                lines.append(f"- {indicator}")
            lines.append("")

        if innov.curiosity_indicators:
            lines.append("**Curiosity Indicators**:")
            for indicator in innov.curiosity_indicators[:5]:
                lines.append(f"- {indicator}")
            lines.append("")

        if innov.problem_solving_indicators:
            lines.append("**Problem-Solving Indicators**:")
            for indicator in innov.problem_solving_indicators[:5]:
                lines.append(f"- {indicator}")
            lines.append("")

        if innov.analytical_thinking_indicators:
            lines.append("**Analytical Thinking Indicators**:")
            for indicator in innov.analytical_thinking_indicators[:5]:
                lines.append(f"- {indicator}")
            lines.append("")

        lines.append("### 4.3 Key Innovation Markers")
        lines.append("")
        for marker in innov.key_innovation_markers[:10]:
            lines.append(f"- \"{marker}\"")
        lines.append("")

        lines.append(f"### 4.4 Recommendation")
        lines.append("")
        lines.append(innov.recommendation)
        lines.append("")

        # Detailed Criterion Analysis
        lines.append("## 5. Detailed Criterion Analysis")
        lines.append("")

        for analysis in report.criterion_analyses:
            lines.append(f"### 5.{report.criterion_analyses.index(analysis) + 1} {analysis.criterion.display_name}")
            lines.append("")

            lines.append(f"**Score**: {analysis.score}/10")
            lines.append(f"**Confidence**: {analysis.confidence_assessment}")
            lines.append("")

            lines.append("**Linguistic Evidence**:")
            lines.append(f"- Total markers found: {analysis.total_markers_found}")
            lines.append(f"- Unique markers: {analysis.unique_markers}")
            lines.append(f"- Marker density: {analysis.marker_density} per 1,000 words")
            lines.append(f"- Evidence strength: {analysis.supporting_evidence_strength.title()}")
            lines.append("")

            if analysis.top_phrases:
                lines.append("**Most Frequent Phrases**:")
                for phrase_data in analysis.top_phrases[:5]:
                    lines.append(f"- \"{phrase_data['phrase']}\" ({phrase_data['frequency']}x)")
                lines.append("")

        # Statistical Summary
        lines.append("## 6. Statistical Summary")
        lines.append("")

        stats = report.statistical_summary
        lines.append(f"- **Overall Score**: {stats['overall_score']:.2f}/10")
        lines.append(f"- **Mean Score Across Criteria**: {stats['mean_score']:.2f}/10")
        lines.append(f"- **Median Score**: {stats['median_score']}/10")
        lines.append(f"- **Score Range**: {stats['score_range']['min']}-{stats['score_range']['max']}")
        lines.append(f"- **Total Words Analyzed**: {stats['total_words_analyzed']:,}")
        lines.append(f"- **Total Linguistic Markers**: {stats['total_linguistic_markers']}")
        lines.append(f"- **Average Markers per Criterion**: {stats['average_markers_per_criterion']:.1f}")
        lines.append(f"- **Criteria with Strong Evidence**: {stats['criteria_with_strong_evidence']}/11")
        lines.append(f"- **Criteria with Weak Evidence**: {stats['criteria_with_weak_evidence']}/11")
        lines.append("")

        # Discussion
        lines.append("## 7. Discussion")
        lines.append("")
        lines.append(report.discussion)
        lines.append("")

        # Conclusions
        lines.append("## 8. Conclusions")
        lines.append("")
        for i, conclusion in enumerate(report.conclusions, 1):
            lines.append(f"{i}. {conclusion}")
        lines.append("")

        # Recommendations
        lines.append("## 9. Recommendations")
        lines.append("")
        for i, recommendation in enumerate(report.recommendations, 1):
            lines.append(f"{i}. {recommendation}")
        lines.append("")

        # Score Breakdown Table
        lines.append("## 10. Appendix A: Complete Score Breakdown")
        lines.append("")

        lines.append("| Criterion | Score | Confidence | Evidence Items |")
        lines.append("|-----------|-------|------------|----------------|")

        for score_data in report.score_breakdown['scores_by_criterion']:
            lines.append(
                f"| {score_data['criterion']} | {score_data['score']}/10 | "
                f"{score_data['confidence'].title()} | {score_data['evidence_count']} |"
            )
        lines.append("")

        # Detailed Evidence
        lines.append("## 11. Appendix B: Detailed Linguistic Evidence")
        lines.append("")

        for evidence in report.detailed_evidence[:5]:  # Limit to first 5 criteria for brevity
            lines.append(f"### {evidence['criterion']}")
            lines.append("")
            lines.append(f"**Total Markers**: {evidence['total_markers']} | **Unique Phrases**: {evidence['unique_phrases']}")
            lines.append("")

            lines.append("**Sample Markers**:")
            for marker in evidence['markers'][:5]:
                lines.append(f"- **\"{marker['phrase']}\"** ({marker['type']})")
                lines.append(f"  - Source: {marker['source']}")
                lines.append(f"  - Context: \"{marker['context']}\"")
                lines.append("")

        # Footer
        lines.append("---")
        lines.append("")
        lines.append("*This report was generated using AI-assisted linguistic analysis and structured evaluation methods.*")
        lines.append(f"*Report generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}*")
        lines.append("")

        return "\n".join(lines)

    @staticmethod
    def _generate_latex_paper(report: ResearchEvaluationReport) -> str:
        """Generate LaTeX formatted research paper"""
        # Simplified LaTeX template
        latex = []

        latex.append(r"\documentclass[12pt,a4paper]{article}")
        latex.append(r"\usepackage{geometry}")
        latex.append(r"\geometry{margin=1in}")
        latex.append(r"\usepackage{graphicx}")
        latex.append(r"\usepackage{hyperref}")
        latex.append("")
        latex.append(r"\title{Candidate Evaluation Research Report \\ Linguistic Marker Analysis and Innovation Potential Assessment}")
        latex.append(f"\\author{{Candidate: {report.candidate_id}}}")
        latex.append(f"\\date{{{report.report_date.strftime('%B %d, %Y')}}}")
        latex.append("")
        latex.append(r"\begin{document}")
        latex.append(r"\maketitle")
        latex.append("")
        latex.append(r"\begin{abstract}")
        latex.append(report.executive_summary.replace('&', r'\&'))
        latex.append(r"\end{abstract}")
        latex.append("")
        latex.append(r"\tableofcontents")
        latex.append(r"\newpage")
        latex.append("")
        latex.append(r"\section{Research Intention}")
        latex.append(report.research_intention.replace('&', r'\&'))
        latex.append("")
        # Add more sections...
        latex.append(r"\end{document}")

        return "\n".join(latex)
