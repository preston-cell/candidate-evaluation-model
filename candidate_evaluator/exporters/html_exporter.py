"""HTML export functionality"""

from pathlib import Path
from typing import Union, List
from datetime import datetime

from candidate_evaluator.core.models import EvaluationResult, ComparisonResult


class HTMLExporter:
    """Export evaluation results to HTML format"""

    HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            line-height: 1.6;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            background-color: white;
            border-radius: 8px;
            padding: 30px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        h1 {{ color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }}
        h2 {{ color: #34495e; margin-top: 30px; }}
        h3 {{ color: #7f8c8d; }}
        .meta-info {{
            background-color: #ecf0f1;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
        }}
        .meta-info p {{ margin: 5px 0; }}
        .score-badge {{
            display: inline-block;
            padding: 5px 15px;
            border-radius: 20px;
            font-weight: bold;
            font-size: 1.2em;
        }}
        .score-high {{ background-color: #2ecc71; color: white; }}
        .score-medium {{ background-color: #f39c12; color: white; }}
        .score-low {{ background-color: #e74c3c; color: white; }}
        .criterion {{
            border-left: 4px solid #3498db;
            padding-left: 20px;
            margin: 25px 0;
        }}
        .score-bar {{
            width: 100%;
            height: 30px;
            background-color: #ecf0f1;
            border-radius: 15px;
            overflow: hidden;
            margin: 10px 0;
        }}
        .score-bar-fill {{
            height: 100%;
            background: linear-gradient(90deg, #e74c3c 0%, #f39c12 50%, #2ecc71 100%);
            transition: width 0.3s ease;
        }}
        .evidence {{
            background-color: #f8f9fa;
            border-left: 3px solid #95a5a6;
            padding: 10px 15px;
            margin: 10px 0;
        }}
        .evidence-quote {{
            font-style: italic;
            color: #555;
            margin: 5px 0;
        }}
        .strengths, .areas {{
            background-color: #e8f8f5;
            padding: 15px;
            border-radius: 5px;
            margin: 15px 0;
        }}
        .areas {{
            background-color: #fef5e7;
        }}
        ul {{ padding-left: 20px; }}
        .recommendation {{
            background-color: #d6eaf8;
            padding: 15px;
            border-radius: 5px;
            font-size: 1.1em;
            margin: 20px 0;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background-color: #3498db;
            color: white;
        }}
        tr:hover {{ background-color: #f5f5f5; }}
        .confidence {{
            padding: 2px 8px;
            border-radius: 3px;
            font-size: 0.85em;
        }}
        .confidence-high {{ background-color: #2ecc71; color: white; }}
        .confidence-medium {{ background-color: #f39c12; color: white; }}
        .confidence-low {{ background-color: #e74c3c; color: white; }}
    </style>
</head>
<body>
    <div class="container">
        {content}
    </div>
</body>
</html>
"""

    @staticmethod
    def export_evaluation(
        result: EvaluationResult,
        output_path: Union[str, Path],
        include_evidence: bool = True
    ) -> str:
        """
        Export evaluation result to HTML file.

        Args:
            result: EvaluationResult object
            output_path: Path to output file
            include_evidence: Whether to include detailed evidence

        Returns:
            Path to exported file
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Build HTML content
        content_parts = []

        # Header
        content_parts.append(f"<h1>Candidate Evaluation Report</h1>")

        # Meta info
        content_parts.append('<div class="meta-info">')
        content_parts.append(f"<p><strong>Candidate ID:</strong> {result.candidate.candidate_id}</p>")
        if result.candidate.name:
            content_parts.append(f"<p><strong>Name:</strong> {result.candidate.name}</p>")
        content_parts.append(f"<p><strong>Evaluation Date:</strong> {result.candidate.evaluation_date.strftime('%Y-%m-%d %H:%M')}</p>")
        content_parts.append(f"<p><strong>Materials:</strong> {', '.join(result.candidate.materials)}</p>")
        content_parts.append('</div>')

        # Overall score
        score_class = HTMLExporter._get_score_class(result.overall_score)
        content_parts.append(f'<h2>Overall Assessment</h2>')
        content_parts.append(f'<p>Overall Score: <span class="score-badge {score_class}">{result.overall_score:.2f}/10</span></p>')

        content_parts.append(f'<div class="recommendation"><strong>Recommendation:</strong> {result.recommendation}</div>')
        content_parts.append(f'<p>{result.overall_assessment}</p>')

        # Strengths
        if result.strengths:
            content_parts.append('<div class="strengths">')
            content_parts.append('<h3>Key Strengths</h3>')
            content_parts.append('<ul>')
            for strength in result.strengths:
                content_parts.append(f'<li>{strength}</li>')
            content_parts.append('</ul>')
            content_parts.append('</div>')

        # Areas for development
        if result.areas_for_development:
            content_parts.append('<div class="areas">')
            content_parts.append('<h3>Areas for Development</h3>')
            content_parts.append('<ul>')
            for area in result.areas_for_development:
                content_parts.append(f'<li>{area}</li>')
            content_parts.append('</ul>')
            content_parts.append('</div>')

        # Detailed scores
        content_parts.append('<h2>Detailed Evaluation by Criterion</h2>')

        sorted_scores = sorted(result.scores, key=lambda s: s.score, reverse=True)

        for score in sorted_scores:
            content_parts.append('<div class="criterion">')
            content_parts.append(f'<h3>{score.criterion.display_name}</h3>')

            # Score bar
            score_percentage = (score.score / 10) * 100
            content_parts.append(f'<div class="score-bar">')
            content_parts.append(f'<div class="score-bar-fill" style="width: {score_percentage}%"></div>')
            content_parts.append('</div>')

            confidence_class = f'confidence-{score.confidence}'
            content_parts.append(f'<p><strong>Score:</strong> {score.score}/10 ')
            content_parts.append(f'<span class="confidence {confidence_class}">Confidence: {score.confidence}</span></p>')

            content_parts.append(f'<p><strong>Reasoning:</strong> {score.reasoning}</p>')

            if score.notes:
                content_parts.append(f'<p><strong>Notes:</strong> {score.notes}</p>')

            if include_evidence and score.evidence:
                content_parts.append('<p><strong>Evidence:</strong></p>')
                for ev in score.evidence:
                    content_parts.append('<div class="evidence">')
                    content_parts.append(f'<p><em>From {ev.source}:</em></p>')
                    content_parts.append(f'<p class="evidence-quote">"{ev.quote}"</p>')
                    content_parts.append(f'<p>{ev.context}</p>')
                    content_parts.append('</div>')

            content_parts.append('</div>')

        content = '\n'.join(content_parts)

        # Wrap in template
        html = HTMLExporter.HTML_TEMPLATE.format(
            title=f"Evaluation: {result.candidate.candidate_id}",
            content=content
        )

        # Write to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)

        return str(output_path)

    @staticmethod
    def _get_score_class(score: float) -> str:
        """Get CSS class based on score"""
        if score >= 8:
            return 'score-high'
        elif score >= 6:
            return 'score-medium'
        else:
            return 'score-low'

    @staticmethod
    def export_comparison(
        result: ComparisonResult,
        output_path: Union[str, Path]
    ) -> str:
        """
        Export comparison result to HTML file.

        Args:
            result: ComparisonResult object
            output_path: Path to output file

        Returns:
            Path to exported file
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        content_parts = []

        content_parts.append('<h1>Candidate Comparison Report</h1>')
        content_parts.append('<div class="meta-info">')
        content_parts.append(f'<p><strong>Comparison Date:</strong> {result.comparison_date.strftime("%Y-%m-%d %H:%M")}</p>')
        content_parts.append(f'<p><strong>Candidates Compared:</strong> {len(result.candidates)}</p>')
        content_parts.append('</div>')

        # Ranking table
        content_parts.append('<h2>Ranking</h2>')
        content_parts.append('<table>')
        content_parts.append('<tr><th>Rank</th><th>Candidate</th><th>Overall Score</th><th>Recommendation</th></tr>')

        for i, candidate_id in enumerate(result.ranking, 1):
            candidate_result = next(
                (c for c in result.candidates if c.candidate.candidate_id == candidate_id),
                None
            )
            if candidate_result:
                name = candidate_result.candidate.name or candidate_id
                score = candidate_result.overall_score
                score_class = HTMLExporter._get_score_class(score)
                rec = candidate_result.recommendation

                content_parts.append(
                    f'<tr>'
                    f'<td>{i}</td>'
                    f'<td>{name}</td>'
                    f'<td><span class="score-badge {score_class}">{score:.2f}</span></td>'
                    f'<td>{rec}</td>'
                    f'</tr>'
                )

        content_parts.append('</table>')

        # Insights
        if result.insights:
            content_parts.append('<h2>Key Insights</h2>')
            content_parts.append('<ul>')
            for insight in result.insights:
                content_parts.append(f'<li>{insight}</li>')
            content_parts.append('</ul>')

        content = '\n'.join(content_parts)

        html = HTMLExporter.HTML_TEMPLATE.format(
            title="Candidate Comparison",
            content=content
        )

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)

        return str(output_path)
