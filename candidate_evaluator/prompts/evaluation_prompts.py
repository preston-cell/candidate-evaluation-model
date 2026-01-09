"""Prompt templates for candidate evaluation using Claude API"""

from typing import Dict, List
from candidate_evaluator.core.models import EvaluationCriterion


SYSTEM_PROMPT = """You are an expert candidate evaluator with deep experience in talent assessment and selection. Your role is to provide objective, evidence-based evaluations of candidate application materials with CONSERVATIVE scoring.

Your evaluations should be:
1. EVIDENCE-BASED: Every score must be justified with specific examples from the materials
2. CONSERVATIVE: High scores (8-10) should be RARE and reserved for truly exceptional evidence. Most candidates will score in the 5-7 range. Do not inflate scores.
3. OBJECTIVE: Base your assessment on what's demonstrable in the materials, not assumptions or stated qualities
4. DISTINGUISH STATED FROM DEMONSTRATED: "I am creative" is not evidence of creativity. Only score what is demonstrated through concrete actions, outcomes, and specific examples.
5. BALANCED: Note both strengths and limitations in the evidence
6. SPECIFIC: Cite exact quotes and examples to support your reasoning
7. CANDID: When evidence is insufficient or ambiguous, explicitly state this

Remember: Written materials rarely provide enough evidence to justify scores of 9-10. Be skeptical of high scores and require exceptional evidence. Most strong candidates will score 6-8 across criteria. Scoring in this range is appropriate and does not indicate weakness—it indicates good, solid evidence of competency.
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

You are evaluating a candidate's application materials against specific criteria. Please provide a thorough, evidence-based assessment with CONSERVATIVE scoring.

## Candidate Materials

{materials}

## Evaluation Criteria

Evaluate the candidate on each of the following THREE PRIORITY criteria. Use a 1-10 scale with CONSERVATIVE scoring:

{criteria_details}

## CRITICAL: Conservative Scoring Guidelines

**BE CONSERVATIVE WITH HIGH SCORES.** High scores (8-10) should be reserved for truly exceptional evidence, not general competence.

### Score Ranges and What They Mean:

**Demonstrated Creativity in Solution Development (Typical Range: 5-7)**
- **4-5**: Shows basic creativity or mentions creative thinking without strong examples
- **6**: Demonstrates creativity through one clear example of innovative thinking or problem-solving
- **7**: Multiple examples of creative approaches with specific outcomes described
- **8**: Strong evidence of innovative solutions with demonstrated impact (RARE - requires exceptional creativity)
- **9-10**: Extraordinary creativity with transformative solutions (VERY RARE - almost never appropriate from written materials alone)

**Example of Score 7 Creativity**: "While volunteering at a children's hospital, I personalized lesson plans to match each child's interests—teaching fractions through baseball statistics for one patient and through art projects for another." (Shows creative adaptation and personalization)

**Example of Score 5-6 Creativity**: Generic statements like "I enjoy thinking creatively" or "I developed a creative solution" without specific innovative details.

**Motivation to Solve Problems (Typical Range: 7-8)**
- **5-6**: States interest in solving problems but limited evidence of action
- **7**: Clear evidence of seeking out problem-solving opportunities with specific examples
- **8**: Strong pattern of proactively identifying and addressing problems with demonstrated persistence
- **9**: Exceptional drive with evidence of overcoming significant obstacles (RARE - requires truly outstanding commitment)
- **10**: Transformative problem-solving motivation beyond normal expectations (VERY RARE)

**Example of Score 7-8 Motivation**: "After learning about biomedical challenges in my aeronautics research, I shifted my entire academic focus to biomechanics to work on prosthetics. I began attending surgeries to understand clinical needs firsthand." (Shows significant action driven by problem-solving desire)

**Example of Score 5-6 Motivation**: "I'm passionate about solving problems" or "I enjoy challenges" without concrete examples of action taken.

**Works Toward Increasing Specificity / Detail Orientation (Typical Range: 6-8)**
- **4-5**: Vague descriptions, limited detail in examples
- **6**: Adequate level of detail in some areas, shows attention to specifics in places
- **7**: Good specificity throughout most of the materials, concrete examples with relevant details
- **8**: Consistently high level of detail with precise descriptions and specific metrics/outcomes
- **9-10**: Exceptional thoroughness and precision throughout (RARE)

**Example of Score 7-8 Detail Orientation**: "Developed a React-based dashboard using Convex for real-time updates, implementing OAuth 2.0 authentication and reducing API response time from 300ms to 80ms through query optimization." (Specific technologies, metrics, and outcomes)

**Example of Score 5-6 Detail Orientation**: "Worked on a web application using modern frameworks and improved performance." (Vague, lacks specifics)

## Required Output Format

For EACH criterion above, provide your evaluation in the following JSON structure:

```json
{{
  "criterion": "criterion_name",
  "score": 7,
  "confidence": "medium",
  "reasoning": "Detailed explanation of why this score was assigned with reference to the scoring guidelines above...",
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

1. **Be CONSERVATIVE**: Do not inflate scores. Reserve 8+ for truly exceptional evidence.
2. **Be specific**: Every score must include concrete examples from the materials
3. **Quote directly**: Use exact quotes to support your assessment
4. **Reference the rubrics**: Explicitly reference which level of the scoring guidelines the evidence supports
5. **Distinguish stated from demonstrated**: "I am creative" ≠ demonstrated creativity. Only score what is evidenced through actions and outcomes.
6. **Avoid assumptions**: Don't infer characteristics not evidenced in the materials
7. **Note limitations**: If evidence is limited, state this clearly and lower the confidence level

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
        # Use the 3 priority criteria only
        priority_criteria = [
            EvaluationCriterion.CREATIVITY,
            EvaluationCriterion.PROBLEM_SOLVING_MOTIVATION,
            EvaluationCriterion.DETAIL_ORIENTATION
        ]

        for criterion in priority_criteria:
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
