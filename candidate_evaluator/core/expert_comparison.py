"""Expert comparison module for comparing AI evaluations with human/expert ratings."""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Union
from datetime import datetime

from candidate_evaluator.core.models import (
    EvaluationResult,
    ExpertRating,
    ExpertComparisonMetrics,
    EvaluationCriterion
)


class ExpertComparisonAnalyzer:
    """Analyze agreement between AI evaluations and expert ratings."""

    # Mapping of common column name variations to standard criterion names
    CRITERION_ALIASES = {
        'creativity': ['creativity', 'creative', 'demonstrated creativity',
                       'demonstrated creativity in solution development'],
        'problem_solving_motivation': ['problem_solving', 'problem solving',
                                        'motivation to solve problems', 'problem-solving'],
        'detail_orientation': ['detail_orientation', 'detail orientation',
                               'works toward increasing specificity', 'specificity'],
        'critical_thinking': ['critical_thinking', 'critical thinking',
                              'logical analysis', 'critical thinking / logical analysis'],
        'coachability': ['coachability', 'receptive to feedback',
                         'coachability – receptive to feedback'],
        'curiosity': ['curiosity'],
        'collaboration': ['collaboration', 'collaborates',
                          'collaborates with others effectively'],
        'follow_through': ['follow_through', 'follow through',
                           'demonstrated follow through'],
        'evidence_based': ['evidence_based', 'evidence based',
                           'understands the value of evidence'],
        'communication': ['communication', 'effective communicator'],
        'expertise_enabler': ['expertise_enabler', 'expertise',
                              'uses own expertise as an enabler']
    }

    def __init__(self):
        self.ai_results: List[EvaluationResult] = []
        self.expert_ratings: List[ExpertRating] = []

    def load_expert_ratings_from_excel(
        self,
        file_path: Union[str, Path],
        candidate_id_col: str = 'candidate_id',
        score_columns: Optional[Dict[str, str]] = None,
        interview_col: Optional[str] = None,
        rater_col: Optional[str] = None
    ) -> List[ExpertRating]:
        """
        Load expert ratings from Excel file.

        Args:
            file_path: Path to Excel file
            candidate_id_col: Column name containing candidate IDs
            score_columns: Dict mapping criterion names to column names
            interview_col: Column name for interview decision (yes/no/true/false)
            rater_col: Column name for rater identifier

        Returns:
            List of ExpertRating objects
        """
        file_path = Path(file_path)

        if file_path.suffix in ['.xlsx', '.xls']:
            df = pd.read_excel(file_path)
        elif file_path.suffix == '.csv':
            df = pd.read_csv(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_path.suffix}")

        ratings = []

        # Auto-detect candidate ID column if not specified
        if candidate_id_col not in df.columns:
            candidate_id_col = self._find_column(df, ['candidate_id', 'candidate', 'name', 'applicant', 'id'])

        # Auto-detect score columns if not specified
        if score_columns is None:
            score_columns = self._auto_detect_score_columns(df)

        for _, row in df.iterrows():
            candidate_id = str(row.get(candidate_id_col, '')).strip()
            if not candidate_id or candidate_id == 'nan':
                continue

            scores = {}
            comments = {}

            for criterion, col_name in score_columns.items():
                if col_name in df.columns:
                    value = row.get(col_name)
                    if pd.notna(value):
                        try:
                            scores[criterion] = float(value)
                        except (ValueError, TypeError):
                            pass

                # Look for corresponding comment column
                comment_col = f"Comments on {col_name}"
                if comment_col in df.columns:
                    comment = row.get(comment_col)
                    if pd.notna(comment):
                        comments[criterion] = str(comment)

            # Interview decision
            interview_decision = None
            if interview_col and interview_col in df.columns:
                decision = row.get(interview_col)
                if pd.notna(decision):
                    decision_str = str(decision).lower().strip()
                    interview_decision = decision_str in ['yes', 'true', '1', 'recommend', 'interview']

            # Rater ID
            rater_id = None
            if rater_col and rater_col in df.columns:
                rater_id = str(row.get(rater_col))

            # Calculate overall score from individual scores
            overall_score = None
            if scores:
                overall_score = sum(scores.values()) / len(scores)

            rating = ExpertRating(
                candidate_id=candidate_id,
                rater_id=rater_id,
                scores=scores,
                overall_score=overall_score,
                interview_decision=interview_decision,
                comments=comments,
                rating_date=datetime.now()
            )
            ratings.append(rating)

        self.expert_ratings = ratings
        return ratings

    def load_expert_ratings_from_csv(
        self,
        file_path: Union[str, Path],
        **kwargs
    ) -> List[ExpertRating]:
        """Load expert ratings from CSV file. Same parameters as Excel loader."""
        return self.load_expert_ratings_from_excel(file_path, **kwargs)

    def set_ai_results(self, results: List[EvaluationResult]):
        """Set AI evaluation results for comparison."""
        self.ai_results = results

    def _find_column(self, df: pd.DataFrame, candidates: List[str]) -> str:
        """Find a column by checking against multiple possible names."""
        df_cols_lower = {col.lower().strip(): col for col in df.columns}
        for candidate in candidates:
            if candidate.lower() in df_cols_lower:
                return df_cols_lower[candidate.lower()]
        raise ValueError(f"Could not find column matching any of: {candidates}")

    def _auto_detect_score_columns(self, df: pd.DataFrame) -> Dict[str, str]:
        """Auto-detect score columns by matching criterion aliases."""
        score_columns = {}
        df_cols_lower = {col.lower().strip(): col for col in df.columns}

        for criterion, aliases in self.CRITERION_ALIASES.items():
            for alias in aliases:
                if alias.lower() in df_cols_lower:
                    score_columns[criterion] = df_cols_lower[alias.lower()]
                    break

        return score_columns

    def _match_candidates(self) -> List[Tuple[EvaluationResult, ExpertRating]]:
        """Match AI results with expert ratings by candidate ID."""
        # Create lookup by candidate ID (normalized)
        expert_lookup = {}
        for rating in self.expert_ratings:
            # Normalize candidate ID for matching
            normalized_id = self._normalize_candidate_id(rating.candidate_id)
            expert_lookup[normalized_id] = rating

        matches = []
        for ai_result in self.ai_results:
            normalized_id = self._normalize_candidate_id(ai_result.candidate.candidate_id)
            if normalized_id in expert_lookup:
                matches.append((ai_result, expert_lookup[normalized_id]))

        return matches

    def _normalize_candidate_id(self, candidate_id: str) -> str:
        """Normalize candidate ID for matching (handles different naming conventions)."""
        # Remove common suffixes
        normalized = candidate_id.lower().strip()
        for suffix in ['_app_redacted', '_redacted', '_app', '_evaluation']:
            normalized = normalized.replace(suffix, '')
        # Replace underscores with spaces for name-based matching
        normalized = normalized.replace('_', ' ')
        return normalized

    def compare(
        self,
        ai_results: Optional[List[EvaluationResult]] = None,
        expert_ratings: Optional[List[ExpertRating]] = None,
        interview_threshold: float = 6.0
    ) -> ExpertComparisonMetrics:
        """
        Compare AI evaluations with expert ratings.

        Args:
            ai_results: List of AI evaluation results (uses self.ai_results if not provided)
            expert_ratings: List of expert ratings (uses self.expert_ratings if not provided)
            interview_threshold: Score threshold for recommending interview

        Returns:
            ExpertComparisonMetrics with agreement statistics
        """
        if ai_results:
            self.ai_results = ai_results
        if expert_ratings:
            self.expert_ratings = expert_ratings

        if not self.ai_results or not self.expert_ratings:
            raise ValueError("Both AI results and expert ratings must be provided")

        matches = self._match_candidates()

        if not matches:
            raise ValueError("No matching candidates found between AI and expert ratings")

        # Extract scores for comparison
        ai_overall_scores = []
        expert_overall_scores = []
        ai_criterion_scores: Dict[str, List[float]] = {}
        expert_criterion_scores: Dict[str, List[float]] = {}
        ai_recommendations = []
        expert_recommendations = []
        high_disagreement = []

        for ai_result, expert_rating in matches:
            # Overall scores
            ai_overall_scores.append(ai_result.overall_score)
            expert_overall = expert_rating.overall_score or (
                sum(expert_rating.scores.values()) / len(expert_rating.scores)
                if expert_rating.scores else None
            )
            if expert_overall:
                expert_overall_scores.append(expert_overall)

            # Per-criterion scores
            for score in ai_result.scores:
                criterion = score.criterion.value
                if criterion not in ai_criterion_scores:
                    ai_criterion_scores[criterion] = []
                    expert_criterion_scores[criterion] = []

                ai_criterion_scores[criterion].append(score.score)

                # Find matching expert score
                expert_score = expert_rating.scores.get(criterion)
                if expert_score is not None:
                    expert_criterion_scores[criterion].append(expert_score)
                else:
                    # Try to find by alias
                    for alias in self.CRITERION_ALIASES.get(criterion, []):
                        if alias in expert_rating.scores:
                            expert_criterion_scores[criterion].append(expert_rating.scores[alias])
                            break

            # Interview recommendations
            ai_recommends = ai_result.overall_score >= interview_threshold
            ai_recommendations.append(ai_recommends)

            if expert_rating.interview_decision is not None:
                expert_recommendations.append(expert_rating.interview_decision)
            elif expert_overall:
                expert_recommendations.append(expert_overall >= interview_threshold)

            # Check for high disagreement
            if expert_overall:
                diff = abs(ai_result.overall_score - expert_overall)
                if diff >= 2.0:  # More than 2 points difference
                    high_disagreement.append(ai_result.candidate.candidate_id)

        # Calculate metrics
        overall_mae = self._calculate_mae(ai_overall_scores, expert_overall_scores)
        overall_correlation = self._calculate_correlation(ai_overall_scores, expert_overall_scores)

        criterion_mae = {}
        criterion_correlation = {}
        for criterion in ai_criterion_scores:
            if criterion in expert_criterion_scores:
                ai_scores = ai_criterion_scores[criterion]
                expert_scores = expert_criterion_scores[criterion]
                if len(ai_scores) == len(expert_scores) and len(ai_scores) > 0:
                    criterion_mae[criterion] = self._calculate_mae(ai_scores, expert_scores)
                    criterion_correlation[criterion] = self._calculate_correlation(ai_scores, expert_scores)

        # Classification metrics
        sensitivity = None
        specificity = None
        cohens_kappa = None

        if len(ai_recommendations) == len(expert_recommendations) and len(ai_recommendations) > 0:
            sensitivity, specificity = self._calculate_sensitivity_specificity(
                ai_recommendations, expert_recommendations
            )
            cohens_kappa = self._calculate_cohens_kappa(
                ai_recommendations, expert_recommendations
            )

        # Detect bias
        ai_bias = None
        if ai_overall_scores and expert_overall_scores:
            ai_mean = np.mean(ai_overall_scores)
            expert_mean = np.mean(expert_overall_scores[:len(ai_overall_scores)])
            diff = ai_mean - expert_mean
            if diff > 0.5:
                ai_bias = f"AI scores higher on average (+{diff:.2f})"
            elif diff < -0.5:
                ai_bias = f"AI scores lower on average ({diff:.2f})"

        return ExpertComparisonMetrics(
            total_candidates=len(self.ai_results),
            matched_candidates=len(matches),
            criterion_mae=criterion_mae,
            criterion_correlation=criterion_correlation,
            overall_mae=overall_mae,
            overall_correlation=overall_correlation,
            sensitivity=sensitivity,
            specificity=specificity,
            cohens_kappa=cohens_kappa,
            high_disagreement_candidates=high_disagreement,
            ai_bias=ai_bias
        )

    def _calculate_mae(self, predicted: List[float], actual: List[float]) -> float:
        """Calculate Mean Absolute Error."""
        if not predicted or not actual:
            return 0.0
        min_len = min(len(predicted), len(actual))
        return float(np.mean(np.abs(np.array(predicted[:min_len]) - np.array(actual[:min_len]))))

    def _calculate_correlation(self, x: List[float], y: List[float]) -> float:
        """Calculate Pearson correlation coefficient."""
        if len(x) < 2 or len(y) < 2:
            return 0.0
        min_len = min(len(x), len(y))
        try:
            corr = np.corrcoef(x[:min_len], y[:min_len])[0, 1]
            return float(corr) if not np.isnan(corr) else 0.0
        except:
            return 0.0

    def _calculate_sensitivity_specificity(
        self,
        predicted: List[bool],
        actual: List[bool]
    ) -> Tuple[float, float]:
        """Calculate sensitivity (true positive rate) and specificity (true negative rate)."""
        tp = sum(1 for p, a in zip(predicted, actual) if p and a)
        tn = sum(1 for p, a in zip(predicted, actual) if not p and not a)
        fp = sum(1 for p, a in zip(predicted, actual) if p and not a)
        fn = sum(1 for p, a in zip(predicted, actual) if not p and a)

        sensitivity = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        specificity = tn / (tn + fp) if (tn + fp) > 0 else 0.0

        return sensitivity, specificity

    def _calculate_cohens_kappa(
        self,
        predicted: List[bool],
        actual: List[bool]
    ) -> float:
        """Calculate Cohen's Kappa for inter-rater agreement."""
        n = len(predicted)
        if n == 0:
            return 0.0

        # Observed agreement
        agree = sum(1 for p, a in zip(predicted, actual) if p == a)
        p_o = agree / n

        # Expected agreement by chance
        p_yes_pred = sum(predicted) / n
        p_yes_actual = sum(actual) / n
        p_e = (p_yes_pred * p_yes_actual) + ((1 - p_yes_pred) * (1 - p_yes_actual))

        if p_e == 1:
            return 1.0

        kappa = (p_o - p_e) / (1 - p_e)
        return float(kappa)

    def get_disagreement_details(
        self,
        candidate_ids: Optional[List[str]] = None
    ) -> List[Dict]:
        """
        Get detailed comparison for specific candidates (or high-disagreement candidates).

        Returns list of dicts with AI and expert scores side by side.
        """
        if candidate_ids is None:
            # Get from last comparison
            matches = self._match_candidates()
            details = []
            for ai_result, expert_rating in matches:
                ai_overall = ai_result.overall_score
                expert_overall = expert_rating.overall_score or (
                    sum(expert_rating.scores.values()) / len(expert_rating.scores)
                    if expert_rating.scores else 0
                )
                diff = abs(ai_overall - expert_overall)
                if diff >= 1.5:  # Significant disagreement
                    details.append(self._build_comparison_detail(ai_result, expert_rating))
            return details
        else:
            matches = self._match_candidates()
            match_dict = {
                self._normalize_candidate_id(ai.candidate.candidate_id): (ai, expert)
                for ai, expert in matches
            }
            details = []
            for cid in candidate_ids:
                normalized = self._normalize_candidate_id(cid)
                if normalized in match_dict:
                    ai_result, expert_rating = match_dict[normalized]
                    details.append(self._build_comparison_detail(ai_result, expert_rating))
            return details

    def _build_comparison_detail(
        self,
        ai_result: EvaluationResult,
        expert_rating: ExpertRating
    ) -> Dict:
        """Build detailed comparison dict for a single candidate."""
        expert_overall = expert_rating.overall_score or (
            sum(expert_rating.scores.values()) / len(expert_rating.scores)
            if expert_rating.scores else 0
        )

        criterion_comparison = {}
        for score in ai_result.scores:
            criterion = score.criterion.value
            ai_score = score.score
            expert_score = expert_rating.scores.get(criterion)

            criterion_comparison[criterion] = {
                'ai_score': ai_score,
                'expert_score': expert_score,
                'difference': (ai_score - expert_score) if expert_score else None,
                'expert_comment': expert_rating.comments.get(criterion)
            }

        return {
            'candidate_id': ai_result.candidate.candidate_id,
            'ai_overall': ai_result.overall_score,
            'expert_overall': expert_overall,
            'overall_difference': ai_result.overall_score - expert_overall,
            'ai_recommendation': ai_result.recommendation,
            'expert_interview': expert_rating.interview_decision,
            'criterion_comparison': criterion_comparison
        }

    def export_comparison_report(
        self,
        metrics: ExpertComparisonMetrics,
        output_path: Union[str, Path]
    ) -> str:
        """Export comparison metrics to a markdown report."""
        output_path = Path(output_path)

        report = f"""# AI vs Expert Comparison Report

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}

## Summary

- **Total Candidates Evaluated by AI**: {metrics.total_candidates}
- **Candidates with Expert Ratings**: {metrics.matched_candidates}
- **Match Rate**: {metrics.matched_candidates / metrics.total_candidates * 100:.1f}%

## Overall Agreement

| Metric | Value |
|--------|-------|
| Mean Absolute Error | {metrics.overall_mae:.2f} |
| Correlation | {metrics.overall_correlation:.2f} |

## Classification Performance (Interview Recommendations)

| Metric | Value | Interpretation |
|--------|-------|----------------|
| Sensitivity | {metrics.sensitivity*100:.1f}% | % of expert-recommended candidates AI also recommended |
| Specificity | {metrics.specificity*100:.1f}% | % of expert-rejected candidates AI also rejected |
| Cohen's Kappa | {metrics.cohens_kappa:.2f} | Inter-rater agreement (>0.6 = substantial) |

## Per-Criterion Agreement

| Criterion | MAE | Correlation |
|-----------|-----|-------------|
"""
        for criterion in metrics.criterion_mae:
            mae = metrics.criterion_mae.get(criterion, 'N/A')
            corr = metrics.criterion_correlation.get(criterion, 'N/A')
            mae_str = f"{mae:.2f}" if isinstance(mae, float) else mae
            corr_str = f"{corr:.2f}" if isinstance(corr, float) else corr
            report += f"| {criterion.replace('_', ' ').title()} | {mae_str} | {corr_str} |\n"

        if metrics.ai_bias:
            report += f"\n## Detected Bias\n\n{metrics.ai_bias}\n"

        if metrics.high_disagreement_candidates:
            report += f"\n## High Disagreement Candidates\n\n"
            report += "Candidates where AI and expert scores differ by 2+ points:\n\n"
            for cid in metrics.high_disagreement_candidates[:10]:
                report += f"- {cid}\n"

        with open(output_path, 'w') as f:
            f.write(report)

        return str(output_path)
