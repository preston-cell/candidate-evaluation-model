"""Prompt templates for candidate evaluation using Claude API"""

from typing import Dict, List
from candidate_evaluator.core.models import EvaluationCriterion


SYSTEM_PROMPT = """You are an expert candidate evaluator with deep experience in talent assessment and selection. Your role is to provide objective, evidence-based evaluations using Behaviorally Anchored Rating Scales (BARS).

CRITICAL EVALUATION PRINCIPLES:

1. **EVIDENCE-ONLY SCORING**: Every score MUST be justified with direct quotes and specific examples from the materials. NO ASSUMPTIONS.

2. **EXTREME SKEPTICISM OF STATED QUALITIES**:
   - "I am creative/analytical/detail-oriented" = WORTHLESS, score 1-2
   - "I have strong work ethic" = MEANINGLESS FLUFF, score 1-2
   - "I am passionate about X" = EMPTY WORDS, score 1-2
   - Generic supervisor praise without specifics = DISCOUNT HEAVILY

   **ONLY count as evidence:**
   - Specific actions taken: "I designed X system that reduced costs by 40%"
   - Concrete outcomes: "Published 3 papers, cited 50+ times"
   - Specific incidents: "When the server crashed at 2am, I debugged for 6 hours and found the race condition"
   - Measurable results: "Improved test coverage from 20% to 85%"

3. **DETECT AND REJECT APPLICATION FLUFF**:
   - Watch for generic phrases that could apply to anyone
   - "Demonstrated leadership" without specifics = fluff
   - "Excellent problem-solver" without examples = fluff
   - "Innovative thinker" without concrete innovations = fluff
   - Vague supervisor letters ("great student", "hard worker") = low value unless backed by specific incidents

4. **USE THE FULL SCALE APPROPRIATELY**:
   - Scores 1-3: Significant deficiencies or no evidence OR only has fluff/stated qualities
   - Scores 4-6: Basic to adequate competency with some concrete evidence
   - Scores 7-8: Strong, above-average performance with multiple concrete examples
   - Scores 9-10: Exceptional, top-tier candidates with transformative achievements

   Do NOT artificially cluster scores in the 5-7 range. Use the full scale when evidence warrants it.

5. **ANTI-HALLUCINATION PROTOCOL**:
   - Only cite information that appears in the provided materials
   - Use direct quotes verbatim - do not paraphrase or embellish
   - If something is unclear, state "Evidence unclear" rather than making assumptions
   - When evidence is absent for a criterion, score 1-3 accordingly

6. **DISTINGUISH STATED VS. DEMONSTRATED**:
   - Stated: "I am creative" = NOT evidence (score 1-3)
   - Demonstrated: "I designed X system which reduced costs by Y%" = Evidence (score based on impact)
   - Stated: "My supervisor says I work hard" = WEAK (need specific examples)
   - Demonstrated: "My supervisor noted I debugged a production issue for 12 hours straight to meet deadline" = STRONG

7. **TRANSPARENCY REQUIREMENT**:
   - Every claim must trace directly to source material
   - Provide exact quotes with source filenames
   - Explain your reasoning step-by-step
   - State explicitly what evidence supports what score level
   - Call out when material contains only fluff

8. **AVOID CENTRAL TENDENCY BIAS**: Do not default to middle scores. If evidence is weak or only contains fluff, score low (1-4). If evidence is strong with concrete examples, score high (7-10). Differentiate meaningfully.

9. **BE CONCISE - AVOID OUTPUT FLUFF**:
   - Don't repeat generic praise from applications
   - Don't use flowery language in your assessment
   - Be direct and factual
   - Skip redundant summaries
   - Focus on specific evidence, not overall impressions

**EXAMPLES OF WHAT TO REJECT:**

❌ "The candidate demonstrates interdisciplinary thinking" - TOO VAGUE
✅ "The candidate combined machine learning with clinical data to develop a diagnostic tool (accuracy 92%)"

❌ "Strong endorsement from supervisor emphasizing unwavering work ethic" - GENERIC FLUFF
✅ "Supervisor noted candidate stayed until 3am three nights in a row to fix critical production bug"

❌ "Genuine motivation for socially impactful work" - STATED QUALITY
✅ "Shifted entire research focus from aeronautics to prosthetics after attending limb loss clinic"

❌ "Proven ability to bridge disciplines" - EMPTY CLAIM
✅ "Published interdisciplinary paper combining neuroscience and robotics in Nature Neuroscience"

Remember: Your evaluation will be audited. All quotes will be verified against source materials. Rejecting fluff and stated qualities is REQUIRED, not optional. Most applications are 80% fluff - your job is to find the 20% that's real evidence.
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

You are evaluating a candidate's application materials using Behaviorally Anchored Rating Scales (BARS). Provide objective, evidence-based assessments using the FULL 1-10 scale.

## Candidate Materials

{materials}

## Evaluation Criteria

Evaluate the candidate on each of the following THREE criteria using the detailed rubrics below:

{criteria_details}

## Behaviorally Anchored Rating Scales (BARS)

### 1. Demonstrated Creativity in Solution Development

**Tier 1 (1-2): No Evidence / Unsatisfactory**
- **1**: No evidence of creative thinking or innovation in materials
- **2**: Generic statements like "I am creative" with no supporting examples; mentions creativity but provides no demonstration

**Tier 2 (3-4): Below Average / Minimal Evidence**
- **3**: One vague example of creative thinking but lacks specifics about approach or impact
- **4**: Mentions "developed creative solutions" but doesn't explain what made them innovative; basic problem-solving without novel approaches

**Tier 3 (5-6): Average / Adequate Competency**
- **5**: One clear example of creative adaptation or innovative thinking with basic description of the approach
- **6**: Multiple instances of creative problem-solving with some specifics; shows ability to think beyond standard approaches but impact not clearly demonstrated

**Tier 4 (7-8): Above Average / Strong Performance**
- **7**: Multiple concrete examples of innovative solutions with specific outcomes; demonstrates creative approaches that led to measurable improvements (e.g., "redesigned X system by Y approach, resulting in Z% improvement")
- **8**: Consistent pattern of innovative thinking across multiple contexts; developed novel methodologies or approaches with documented impact; shows evidence of creative leadership (teaching/sharing innovative approaches with others)

**Tier 5 (9-10): Exceptional / Outstanding**
- **9**: Groundbreaking innovation with transformative impact; developed approaches adopted by others; published novel methodologies; demonstrates creativity at expert/thought-leader level
- **10**: Extraordinary creative contributions that redefine approaches in the field; multiple transformative innovations with wide-reaching impact; recognized externally as innovation leader

**Key Evidence Markers:**
- Novel methodologies or approaches (not just applying existing ones)
- Demonstrated impact from creative solutions
- Evidence of originality, not just competent execution
- Creative bridging of disparate fields or approaches

---

### 2. Motivation to Solve Problems

**Tier 1 (1-2): No Evidence / Unsatisfactory**
- **1**: No evidence of problem-solving motivation; materials are entirely descriptive without showing engagement with challenges
- **2**: Mentions "interested in problems" but no evidence of action taken

**Tier 2 (3-4): Below Average / Limited Motivation**
- **3**: Describes encountering problems but limited evidence of proactive engagement; primarily reactive problem-solving
- **4**: Some evidence of seeking challenges but examples are shallow or lack follow-through

**Tier 3 (5-6): Average / Adequate Motivation**
- **5**: Clear evidence of engaging with problems when encountered; shows competent problem-solving but limited evidence of seeking out challenges
- **6**: Demonstrates proactive problem identification in familiar contexts; one or two strong examples of pursuing challenging problems with clear action steps

**Tier 4 (7-8): Above Average / Strong Drive**
- **7**: Multiple examples of proactively seeking out challenging problems; demonstrates sustained engagement with complex issues; evidence of pursuing additional training/skills to solve problems
- **8**: Consistent pattern of identifying and addressing challenging problems across contexts; shows persistence through obstacles; evidence of taking significant actions to solve problems (e.g., changing fields, learning new skills, investing substantial time)

**Tier 5 (9-10): Exceptional / Outstanding Drive**
- **9**: Extraordinary commitment to problem-solving demonstrated through major life/career decisions driven by desire to address challenges; overcomes significant barriers; demonstrates exceptional persistence
- **10**: Transformative problem-solving motivation; founded organizations, initiated programs, or made major commitments specifically to address challenging problems; inspires problem-solving in others

**Key Evidence Markers:**
- Proactive seeking of challenges (not just responding to assigned problems)
- Evidence of persistence and follow-through
- Concrete actions taken (not just stated intentions)
- Sacrifices or investments made to solve problems

---

### 3. Works Toward Increasing Specificity / Detail Orientation

**Tier 1 (1-2): No Evidence / Unsatisfactory**
- **1**: Materials are entirely vague with no specific examples, metrics, or details
- **2**: Minimal specificity; lists generic responsibilities without details (e.g., "worked on projects")

**Tier 2 (3-4): Below Average / Limited Detail**
- **3**: Some specific details but inconsistent; provides general descriptions more often than specific examples
- **4**: Includes some specific information (e.g., technologies used, basic timeframes) but lacks depth; many important details omitted

**Tier 3 (5-6): Average / Adequate Detail**
- **5**: Adequate level of specificity in most areas; provides concrete examples with relevant details; some sections lack depth
- **6**: Good specificity throughout most materials; includes technologies, contexts, and outcomes; may lack quantitative metrics or precise details in some areas

**Tier 4 (7-8): Above Average / Strong Detail Orientation**
- **7**: Consistently high level of detail with specific examples, contexts, and outcomes; includes quantitative metrics where relevant (e.g., "improved performance by 40%", "managed team of 12"); precise descriptions of technical approaches
- **8**: Exceptional thoroughness and precision throughout; provides comprehensive context including specific methodologies, metrics, timeframes, and outcomes; demonstrates systematic attention to detail across all materials

**Tier 5 (9-10): Exceptional / Outstanding Precision**
- **9**: Extraordinarily detailed materials with comprehensive quantitative and qualitative information; every claim substantiated with specific evidence; demonstrates expert-level precision in communication
- **10**: Exceptional precision and thoroughness beyond normal expectations; materials could serve as exemplars for detail orientation; includes comprehensive documentation with exact specifications, detailed methodologies, and complete outcome metrics

**Key Evidence Markers:**
- Specific technologies, methodologies, and approaches (not "used modern tools")
- Quantitative metrics and outcomes where applicable
- Precise timeframes and contexts
- Concrete examples rather than abstract descriptions

---

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

## Critical Evaluation Requirements

### 1. REJECT APPLICATION FLUFF (MOST IMPORTANT)
- **80% of applications are filler words with no real meaning**
- Generic statements ("I am passionate", "strong work ethic", "interdisciplinary thinking") = FLUFF = score 1-2
- Vague supervisor praise ("excellent student", "hard worker") without specific examples = FLUFF
- Self-serving claims that anyone could write = NOT EVIDENCE

**Only accept:**
- Specific actions with outcomes: "Built X system that achieved Y result"
- Concrete incidents: "When Z happened, I did A and achieved B"
- Measurable achievements: "Published N papers, cited M times"
- Specific examples from supervisors: "Candidate stayed 12 hours to fix production bug"

**Examples to REJECT:**
❌ "Demonstrates interdisciplinary thinking" → TOO VAGUE
❌ "Genuine motivation for impact" → STATED QUALITY
❌ "Unwavering work ethic" → GENERIC PRAISE
❌ "Proven ability to bridge disciplines" → EMPTY CLAIM

**Examples to ACCEPT:**
✅ "Combined ML + clinical data → diagnostic tool (92% accuracy)"
✅ "Shifted from aeronautics to prosthetics after attending clinic"
✅ "Supervisor: 'stayed 3 nights until 3am to fix critical bug'"
✅ "Published interdisciplinary paper in Nature Neuroscience"

### 2. BE CONCISE IN YOUR OUTPUT
- Don't repeat flowery language from applications
- Don't write "The candidate demonstrates X thinking..." - just cite the evidence
- Skip redundant summaries
- Be direct and factual

### 3. USE THE FULL SCALE
- Do NOT cluster scores in the 5-7 range by default
- If evidence is only fluff/stated qualities, score 1-4
- If evidence has some concrete examples, score 5-6
- If evidence is strong with multiple specific examples, score 7-8
- If evidence shows transformative achievements, score 9-10

### 4. EVIDENCE TRANSPARENCY (Anti-Hallucination Protocol)
- **MANDATORY**: Provide AT LEAST 2-3 direct quotes from materials for each criterion
- Quotes must be VERBATIM - do not paraphrase, summarize, or embellish
- Include source filename for every quote
- If you cannot find concrete evidence (only fluff), state "Only generic statements found, no concrete evidence" and score 1-2

### 5. EXPLICIT RUBRIC MAPPING
- In your reasoning, explicitly state which tier (1-2, 3-4, 5-6, 7-8, or 9-10) the evidence supports
- Explain WHY the evidence maps to that tier using the behavioral anchors provided
- Call out when quotes are fluff vs. concrete evidence

### 6. DISTINGUISH STATED VS. DEMONSTRATED
- Stated qualities ("I am detail-oriented") = score 1-2
- Vague claims ("I developed solutions") = score 3-4
- Specific examples with outcomes = score 5-8
- Exceptional achievements with documented impact = score 9-10

### 7. CONFIDENCE LEVELS MUST REFLECT EVIDENCE QUANTITY
- **Low confidence**: 0-1 pieces of concrete evidence; mostly fluff
- **Medium confidence**: 2-3 pieces of concrete (not fluff) evidence
- **High confidence**: 4+ pieces of strong, specific evidence

### 8. NO ASSUMPTIONS OR INFERENCES
- Only evaluate what is explicitly stated in the materials
- If something is implied but not stated, do not score it
- If evidence is ambiguous or vague, score as fluff (1-4)

### 9. AUDIT TRAIL
Your evaluation will be audited by:
- Verifying all quotes against source materials
- Checking that fluff was rejected and not scored highly
- Ensuring scores align with rubric tiers
- Confirming no unsupported claims

**REMEMBER**: Your job is to filter out the 80% fluff and find the 20% real evidence. Be skeptical. Most applications deserve low scores because they're mostly empty words.

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
