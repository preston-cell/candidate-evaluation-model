"""CSV export functionality"""

import csv
from pathlib import Path
from typing import Union, List
import pandas as pd

from candidate_evaluator.core.models import EvaluationResult, ComparisonResult


class CSVExporter:
    """Export evaluation results to CSV format"""

    @staticmethod
    def export_evaluation(
        result: EvaluationResult,
        output_path: Union[str, Path]
    ) -> str:
        """
        Export evaluation result to CSV file.

        Args:
            result: EvaluationResult object
            output_path: Path to output file

        Returns:
            Path to exported file
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Prepare rows
        rows = []

        # Add candidate info row
        rows.append({
            'Type': 'Candidate Info',
            'Field': 'Candidate ID',
            'Value': result.candidate.candidate_id,
            'Score': '',
            'Confidence': ''
        })

        if result.candidate.name:
            rows.append({
                'Type': 'Candidate Info',
                'Field': 'Name',
                'Value': result.candidate.name,
                'Score': '',
                'Confidence': ''
            })

        rows.append({
            'Type': 'Overall',
            'Field': 'Overall Score',
            'Value': '',
            'Score': f'{result.overall_score:.2f}',
            'Confidence': ''
        })

        rows.append({
            'Type': 'Overall',
            'Field': 'Recommendation',
            'Value': result.recommendation,
            'Score': '',
            'Confidence': ''
        })

        # Add criterion scores
        for score in result.scores:
            rows.append({
                'Type': 'Criterion',
                'Field': score.criterion.display_name,
                'Value': score.reasoning[:100] + '...' if len(score.reasoning) > 100 else score.reasoning,
                'Score': str(score.score),
                'Confidence': score.confidence
            })

        # Write to CSV
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            fieldnames = ['Type', 'Field', 'Value', 'Score', 'Confidence']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

        return str(output_path)

    @staticmethod
    def export_batch(
        results: List[EvaluationResult],
        output_path: Union[str, Path],
        use_pandas: bool = True
    ) -> str:
        """
        Export multiple evaluation results to CSV file.

        Args:
            results: List of EvaluationResult objects
            output_path: Path to output file
            use_pandas: Whether to use pandas for export (creates better formatted output)

        Returns:
            Path to exported file
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        if use_pandas:
            # Create DataFrame
            data = []

            for result in results:
                row = {
                    'candidate_id': result.candidate.candidate_id,
                    'candidate_name': result.candidate.name or '',
                    'overall_score': result.overall_score,
                    'recommendation': result.recommendation,
                    'evaluation_date': result.candidate.evaluation_date.strftime('%Y-%m-%d %H:%M')
                }

                # Add scores for each criterion
                for score in result.scores:
                    criterion_key = score.criterion.value
                    row[f'{criterion_key}_score'] = score.score
                    row[f'{criterion_key}_confidence'] = score.confidence

                data.append(row)

            df = pd.DataFrame(data)

            # Reorder columns
            fixed_cols = ['candidate_id', 'candidate_name', 'overall_score', 'recommendation', 'evaluation_date']
            score_cols = [col for col in df.columns if col not in fixed_cols]
            df = df[fixed_cols + sorted(score_cols)]

            # Export to CSV
            df.to_csv(output_path, index=False)

        else:
            # Manual CSV export
            rows = []
            header = ['candidate_id', 'candidate_name', 'overall_score', 'recommendation']

            # Get all criteria from first result
            if results:
                for score in results[0].scores:
                    header.append(f'{score.criterion.value}_score')
                    header.append(f'{score.criterion.value}_confidence')

            for result in results:
                row = [
                    result.candidate.candidate_id,
                    result.candidate.name or '',
                    f'{result.overall_score:.2f}',
                    result.recommendation
                ]

                for score in result.scores:
                    row.append(str(score.score))
                    row.append(score.confidence)

                rows.append(row)

            with open(output_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(header)
                writer.writerows(rows)

        return str(output_path)

    @staticmethod
    def export_comparison_matrix(
        result: ComparisonResult,
        output_path: Union[str, Path]
    ) -> str:
        """
        Export comparison as a matrix CSV.

        Args:
            result: ComparisonResult object
            output_path: Path to output file

        Returns:
            Path to exported file
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Create comparison matrix
        data = []

        for eval_result in result.candidates:
            row = {
                'Rank': result.ranking.index(eval_result.candidate.candidate_id) + 1 if eval_result.candidate.candidate_id in result.ranking else 'N/A',
                'Candidate ID': eval_result.candidate.candidate_id,
                'Name': eval_result.candidate.name or '',
                'Overall Score': f'{eval_result.overall_score:.2f}',
                'Recommendation': eval_result.recommendation
            }

            # Add scores for each criterion
            for score in eval_result.scores:
                row[score.criterion.display_name] = score.score

            data.append(row)

        # Use pandas if available
        try:
            df = pd.DataFrame(data)
            df = df.sort_values('Rank')
            df.to_csv(output_path, index=False)
        except:
            # Fallback to manual CSV
            if data:
                with open(output_path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=data[0].keys())
                    writer.writeheader()
                    writer.writerows(data)

        return str(output_path)
