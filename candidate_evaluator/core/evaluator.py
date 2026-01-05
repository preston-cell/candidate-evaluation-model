"""Core candidate evaluation engine using Claude API"""

import json
import logging
import time
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path

from anthropic import Anthropic

from candidate_evaluator.core.models import (
    EvaluationResult,
    CriterionScore,
    CandidateProfile,
    Evidence,
    EvaluationCriterion,
    ComparisonResult
)
from candidate_evaluator.utils.config import Config
from candidate_evaluator.utils.file_processor import FileProcessor
from candidate_evaluator.prompts.evaluation_prompts import (
    SYSTEM_PROMPT,
    get_evaluation_prompt,
    get_comparison_prompt
)

logger = logging.getLogger(__name__)


class CandidateEvaluator:
    """Main class for evaluating candidates using Claude API"""

    def __init__(self, config: Config):
        """
        Initialize the evaluator.

        Args:
            config: Configuration object
        """
        self.config = config
        self.client = Anthropic(api_key=config.api.anthropic_api_key)
        self.file_processor = FileProcessor(
            max_file_size_mb=config.processing.max_file_size_mb
        )

    def evaluate_candidate(
        self,
        candidate_id: str,
        material_paths: List[str],
        candidate_name: Optional[str] = None,
        custom_criteria: Optional[List[str]] = None
    ) -> EvaluationResult:
        """
        Evaluate a candidate based on their application materials.

        Args:
            candidate_id: Unique identifier for the candidate
            material_paths: List of paths to candidate materials
            candidate_name: Optional name of the candidate
            custom_criteria: Optional custom evaluation criteria

        Returns:
            EvaluationResult object

        Raises:
            ValueError: If materials cannot be processed or evaluation fails
        """
        logger.info(f"Starting evaluation for candidate: {candidate_id}")
        start_time = time.time()

        # Process files
        logger.info(f"Processing {len(material_paths)} files...")
        processed_files = self.file_processor.process_multiple_files(material_paths)
        combined_materials = self.file_processor.combine_materials(processed_files)

        logger.info(f"Total materials length: {len(combined_materials)} characters")

        # Generate evaluation prompt
        prompt = get_evaluation_prompt(combined_materials, custom_criteria)

        # Call Claude API
        logger.info("Calling Claude API for evaluation...")
        response = self._call_claude_api(prompt)

        # Parse response
        logger.info("Parsing evaluation response...")
        evaluation_data = self._parse_evaluation_response(response)

        # Calculate overall score
        weights = self.config.criteria.weights
        weighted_sum = 0
        total_weight = 0

        scores = []
        for score_data in evaluation_data['criterion_scores']:
            criterion = EvaluationCriterion(score_data['criterion'])
            weight = getattr(weights, criterion.value, 10)

            weighted_sum += score_data['score'] * weight
            total_weight += weight

            # Create evidence objects
            evidence_list = [
                Evidence(**ev) for ev in score_data.get('evidence', [])
            ]

            scores.append(CriterionScore(
                criterion=criterion,
                score=score_data['score'],
                reasoning=score_data['reasoning'],
                evidence=evidence_list,
                confidence=score_data.get('confidence', 'medium'),
                notes=score_data.get('notes')
            ))

        overall_score = weighted_sum / total_weight if total_weight > 0 else 0

        # Create candidate profile
        candidate = CandidateProfile(
            candidate_id=candidate_id,
            name=candidate_name,
            materials=[str(Path(p).name) for p in material_paths],
            evaluation_date=datetime.now()
        )

        # Calculate processing time
        processing_time = time.time() - start_time

        # Create evaluation result
        result = EvaluationResult(
            candidate=candidate,
            scores=scores,
            overall_score=overall_score,
            overall_assessment=evaluation_data.get('overall_assessment', ''),
            strengths=evaluation_data.get('strengths', []),
            areas_for_development=evaluation_data.get('areas_for_development', []),
            recommendation=evaluation_data.get('recommendation', ''),
            metadata={
                'model': self.config.api.model,
                'processing_time_seconds': processing_time,
                'materials_character_count': len(combined_materials),
                'timestamp': datetime.now().isoformat()
            }
        )

        logger.info(f"Evaluation completed in {processing_time:.2f} seconds")
        logger.info(f"Overall score: {overall_score:.2f}")

        return result

    def evaluate_batch(
        self,
        candidates: List[Dict[str, Any]],
        batch_size: Optional[int] = None
    ) -> List[EvaluationResult]:
        """
        Evaluate multiple candidates in batch.

        Args:
            candidates: List of candidate dictionaries with keys:
                - candidate_id: str
                - material_paths: List[str]
                - candidate_name: Optional[str]
            batch_size: Optional batch size (defaults to config)

        Returns:
            List of EvaluationResult objects
        """
        if batch_size is None:
            batch_size = self.config.processing.batch_size

        logger.info(f"Starting batch evaluation of {len(candidates)} candidates")

        results = []
        for i, candidate_data in enumerate(candidates, 1):
            logger.info(f"Processing candidate {i}/{len(candidates)}: {candidate_data['candidate_id']}")

            try:
                result = self.evaluate_candidate(
                    candidate_id=candidate_data['candidate_id'],
                    material_paths=candidate_data['material_paths'],
                    candidate_name=candidate_data.get('candidate_name')
                )
                results.append(result)

            except Exception as e:
                logger.error(f"Failed to evaluate candidate {candidate_data['candidate_id']}: {e}")
                # Continue with other candidates
                continue

        logger.info(f"Batch evaluation completed: {len(results)}/{len(candidates)} successful")
        return results

    def compare_candidates(
        self,
        evaluation_results: List[EvaluationResult]
    ) -> ComparisonResult:
        """
        Compare multiple evaluated candidates.

        Args:
            evaluation_results: List of EvaluationResult objects

        Returns:
            ComparisonResult object
        """
        logger.info(f"Comparing {len(evaluation_results)} candidates")

        # Prepare candidate data for comparison
        candidates_data = [
            result.to_summary_dict() for result in evaluation_results
        ]

        # Generate comparison prompt
        prompt = get_comparison_prompt(candidates_data)

        # Call Claude API
        logger.info("Calling Claude API for comparison...")
        response = self._call_claude_api(prompt)

        # Parse comparison response
        logger.info("Parsing comparison response...")
        comparison_data = self._parse_comparison_response(response)

        # Create comparison matrix
        comparison_matrix = comparison_data.get('comparison_matrix', {})

        result = ComparisonResult(
            candidates=evaluation_results,
            ranking=comparison_data.get('ranking', []),
            comparison_matrix=comparison_matrix,
            insights=comparison_data.get('key_insights', [])
        )

        logger.info("Comparison completed")
        return result

    def _call_claude_api(self, prompt: str) -> str:
        """
        Call Claude API with the given prompt.

        Args:
            prompt: User prompt

        Returns:
            API response text

        Raises:
            Exception: If API call fails
        """
        try:
            message = self.client.messages.create(
                model=self.config.api.model,
                max_tokens=self.config.api.max_tokens,
                temperature=self.config.api.temperature,
                system=SYSTEM_PROMPT,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            # Extract text from response
            response_text = message.content[0].text
            return response_text

        except Exception as e:
            logger.error(f"Claude API call failed: {e}")
            raise

    def _parse_evaluation_response(self, response: str) -> Dict[str, Any]:
        """
        Parse Claude's evaluation response.

        Args:
            response: Raw response text from Claude

        Returns:
            Parsed evaluation data

        Raises:
            ValueError: If response cannot be parsed
        """
        try:
            # Extract JSON from response
            # Look for JSON code blocks
            json_blocks = []
            lines = response.split('\n')
            in_json_block = False
            current_block = []

            for line in lines:
                if line.strip().startswith('```json'):
                    in_json_block = True
                    current_block = []
                elif line.strip() == '```' and in_json_block:
                    in_json_block = False
                    if current_block:
                        json_blocks.append('\n'.join(current_block))
                elif in_json_block:
                    current_block.append(line)

            if not json_blocks:
                raise ValueError("No JSON blocks found in response")

            # Parse criterion scores from individual blocks
            criterion_scores = []
            overall_data = None

            for block in json_blocks:
                try:
                    data = json.loads(block)

                    # Check if this is a criterion score or overall assessment
                    if 'criterion' in data:
                        criterion_scores.append(data)
                    elif 'overall_score' in data:
                        overall_data = data

                except json.JSONDecodeError as e:
                    logger.warning(f"Failed to parse JSON block: {e}")
                    continue

            if not criterion_scores:
                raise ValueError("No criterion scores found in response")

            # Combine parsed data
            result = {
                'criterion_scores': criterion_scores,
                'overall_assessment': overall_data.get('overall_assessment', '') if overall_data else '',
                'strengths': overall_data.get('strengths', []) if overall_data else [],
                'areas_for_development': overall_data.get('areas_for_development', []) if overall_data else [],
                'recommendation': overall_data.get('recommendation', '') if overall_data else ''
            }

            return result

        except Exception as e:
            logger.error(f"Failed to parse evaluation response: {e}")
            logger.debug(f"Response was: {response}")
            raise ValueError(f"Failed to parse evaluation response: {e}")

    def _parse_comparison_response(self, response: str) -> Dict[str, Any]:
        """
        Parse Claude's comparison response.

        Args:
            response: Raw response text from Claude

        Returns:
            Parsed comparison data

        Raises:
            ValueError: If response cannot be parsed
        """
        try:
            # Extract JSON from response
            json_start = response.find('{')
            json_end = response.rfind('}') + 1

            if json_start == -1 or json_end == 0:
                raise ValueError("No JSON found in response")

            json_str = response[json_start:json_end]
            data = json.loads(json_str)

            return data

        except Exception as e:
            logger.error(f"Failed to parse comparison response: {e}")
            logger.debug(f"Response was: {response}")
            raise ValueError(f"Failed to parse comparison response: {e}")
