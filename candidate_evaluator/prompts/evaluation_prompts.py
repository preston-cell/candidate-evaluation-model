"""Prompt templates for candidate evaluation using Claude API"""

from typing import Dict, List
from candidate_evaluator.core.models import EvaluationCriterion


SYSTEM_PROMPT = """You are an expert candidate evaluator with deep experience in talent assessment and selection. Your role is to provide objective, evidence-based evaluations of candidate application materials.

Your evaluations should be:
1. EVIDENCE-BASED: Every score must be justified with specific examples from the materials
2. OBJECTIVE: Base your assessment on what's demonstrable in the materials, not assumptions
3. BALANCED: Note both strengths and limitations in the evidence
4. SPECIFIC: Cite exact quotes and examples to support your reasoning
5. CANDID: When evidence is insufficient or ambiguous, explicitly state this

Remember: Some criteria may be difficult to assess from written materials alone. In such cases, note the limitation and base your score on available evidence while flagging the need for additional assessment methods (e.g., interviews, references).
"""


def _get_criterion_details() -> Dict[str, Dict[str, str]]:
    """Get detailed descriptions for each criterion"""
    details = {}
    for criterion in EvaluationCriterion:
        details[criterion.value] = {
            'name': criterion.display_name,
            'description': criterion.description,
        }
    return details


EVALUATION_PROMPT_TEMPLATE = """# Candidate Evaluation Task

You are evaluating a candidate's application materials against specific criteria. Please provide a thorough, evidence-based assessment.

## Candidate Materials

{materials}

## Evaluation Criteria

Evaluate the candidate on each of the following criteria using a 1-10 scale:
- **1-3**: Insufficient evidence or evidence suggests significant concerns
- **4-5**: Limited evidence or mixed signals
- **6-7**: Adequate evidence of competency
- **8-9**: Strong evidence of competency
- **10**: Exceptional evidence of competency

{criteria_details}

## Required Output Format

For EACH criterion above, provide your evaluation in the following JSON structure:

```json
{{
  "criterion": "criterion_name",
  "score": 7,
  "confidence": "medium",
  "reasoning": "Detailed explanation of why this score was assigned...",
  "evidence": [
    {{
      "quote": "Exact quote from materials",
      "source": "filename.pdf",
      "context": "Why this quote is relevant to the criterion"
    }}
  ],
  "notes": "Any caveats, limitations, or additional observations"
}}
```

**CRITICAL**: The `confidence` field MUST be EXACTLY one of these three lowercase values:
- `"low"` - Limited evidence available
- `"medium"` - Adequate evidence available
- `"high"` - Strong, abundant evidence available

Do NOT use other values like "medium-high", "moderate", "moderate-high", etc. Only use "low", "medium", or "high".

Then provide an overall assessment:

```json
{{
  "overall_score": 7.2,
  "overall_assessment": "High-level summary of the candidate...",
  "strengths": [
    "Key strength 1",
    "Key strength 2"
  ],
  "areas_for_development": [
    "Area 1 where evidence was limited or scores were lower",
    "Area 2"
  ],
  "recommendation": "Overall recommendation (e.g., 'Strong fit', 'Potential fit with development', 'Not recommended', etc.)"
}}
```

## Important Guidelines

1. **Be specific**: Every score must include concrete examples from the materials
2. **Quote directly**: Use exact quotes to support your assessment
3. **Note limitations**: If evidence is limited for a criterion, explicitly state this and explain what additional information would be helpful
4. **Consider context**: Some criteria (like collaboration) may be harder to assess from solo-authored documents
5. **Avoid assumptions**: Don't infer characteristics not evidenced in the materials
6. **Be constructive**: Frame observations professionally and constructively

Please provide your complete evaluation now, following the JSON format specified above.
"""


COMPARISON_PROMPT_TEMPLATE = """# Candidate Comparison Task

You are comparing multiple candidates who have been evaluated using the same criteria. Provide a structured comparison that helps decision-makers understand relative strengths and weaknesses.

## Candidates to Compare

{candidates_data}

## Analysis Required

1. **Ranking**: Rank candidates from strongest to weakest overall fit
2. **Comparative Strengths**: For each candidate, identify what makes them stand out compared to others
3. **Trade-offs**: Identify key trade-offs in the selection (e.g., "Candidate A shows stronger technical skills while Candidate B demonstrates superior communication")
4. **Criteria Comparison**: For each criterion, identify who performs best and why
5. **Recommendations**: Provide specific recommendations for next steps with each candidate

## Output Format

Provide your analysis in the following JSON structure:

```json
{{
  "ranking": ["candidate_id_1", "candidate_id_2", "candidate_id_3"],
  "ranking_rationale": "Explanation of the ranking...",
  "comparison_matrix": {{
    "critical_thinking": {{
      "best": "candidate_id",
      "analysis": "Why this candidate excels in this area..."
    }},
    // ... for each criterion
  }},
  "candidate_insights": {{
    "candidate_id_1": {{
      "comparative_strengths": ["Strength 1", "Strength 2"],
      "comparative_weaknesses": ["Weakness 1"],
      "best_fit_for": "Type of role or situation where this candidate would excel"
    }},
    // ... for each candidate
  }},
  "recommendations": {{
    "candidate_id_1": "Specific next steps for this candidate",
    // ... for each candidate
  }},
  "key_insights": [
    "Notable insight 1 from the comparison",
    "Notable insight 2"
  ]
}}
```

Please provide your complete comparison analysis now.
"""


def get_evaluation_prompt(materials_text: str, custom_criteria: List[str] = None) -> str:
    """
    Generate evaluation prompt with materials and criteria.

    Args:
        materials_text: Combined text of all candidate materials
        custom_criteria: Optional list of custom criteria to evaluate

    Returns:
        Formatted prompt string
    """
    # Get criterion details
    criteria_details_text = []

    if custom_criteria:
        # Use custom criteria if provided
        for i, criterion_text in enumerate(custom_criteria, 1):
            criteria_details_text.append(f"{i}. {criterion_text}")
    else:
        # Use default criteria
        for criterion in EvaluationCriterion:
            criteria_details_text.append(
                f"### {criterion.value}\n"
                f"**{criterion.display_name}**\n"
                f"{criterion.description}\n"
            )

    criteria_section = "\n\n".join(criteria_details_text)

    return EVALUATION_PROMPT_TEMPLATE.format(
        materials=materials_text,
        criteria_details=criteria_section
    )


def get_comparison_prompt(candidates_evaluations: List[Dict]) -> str:
    """
    Generate comparison prompt for multiple candidates.

    Args:
        candidates_evaluations: List of candidate evaluation summaries

    Returns:
        Formatted prompt string
    """
    candidates_text = []

    for eval_data in candidates_evaluations:
        candidate_section = f"""
## Candidate: {eval_data['candidate_id']}
- **Overall Score**: {eval_data['overall_score']:.2f}
- **Recommendation**: {eval_data['recommendation']}

### Scores by Criterion
{_format_scores(eval_data['scores'])}

### Overall Assessment
{eval_data['overall_assessment']}

### Strengths
{_format_list(eval_data['strengths'])}

### Areas for Development
{_format_list(eval_data['areas_for_development'])}
"""
        candidates_text.append(candidate_section)

    return COMPARISON_PROMPT_TEMPLATE.format(
        candidates_data="\n".join(candidates_text)
    )


def _format_scores(scores: Dict[str, int]) -> str:
    """Format scores dictionary as text"""
    lines = []
    for criterion, score in scores.items():
        criterion_obj = EvaluationCriterion(criterion)
        lines.append(f"- {criterion_obj.display_name}: {score}/10")
    return "\n".join(lines)


def _format_list(items: List[str]) -> str:
    """Format list as bulleted text"""
    if not items:
        return "- None specified"
    return "\n".join(f"- {item}" for item in items)
