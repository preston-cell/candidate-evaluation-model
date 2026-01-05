"""Pattern analysis and linguistic marker extraction"""

import re
from typing import List, Dict, Set, Tuple
from collections import Counter, defaultdict
from dataclasses import dataclass

from candidate_evaluator.core.models import EvaluationCriterion


@dataclass
class LinguisticMarker:
    """A linguistic marker found in candidate materials"""
    phrase: str
    context: str
    source: str
    associated_criteria: List[EvaluationCriterion]
    marker_type: str  # 'keyword', 'phrase_pattern', 'syntactic_pattern'
    confidence: float


@dataclass
class PatternFindings:
    """Findings from pattern analysis"""
    criterion: EvaluationCriterion
    positive_markers: List[LinguisticMarker]
    negative_markers: List[LinguisticMarker]
    phrase_frequency: Dict[str, int]
    pattern_summary: str


class LinguisticPatternAnalyzer:
    """Analyzes text for linguistic markers indicating various criteria"""

    # Keywords and phrases associated with each criterion
    CRITERION_MARKERS = {
        EvaluationCriterion.CRITICAL_THINKING: {
            'positive_keywords': [
                'analyze', 'analyzed', 'analysis', 'evaluate', 'assessed',
                'systematic', 'logic', 'logical', 'reasoning', 'rationale',
                'root cause', 'investigated', 'examined', 'compared',
                'weighed', 'considered', 'concluded', 'inferred',
                'synthesized', 'integrated', 'derived', 'determined'
            ],
            'positive_phrases': [
                r'root cause analysis',
                r'systematic approach',
                r'analyzed.*data',
                r'evaluated.*options',
                r'logical.*conclusion',
                r'critical.*thinking',
                r'reasoned.*approach',
                r'evidence.*suggests',
                r'based on.*analysis'
            ]
        },
        EvaluationCriterion.COACHABILITY: {
            'positive_keywords': [
                'feedback', 'learned', 'improved', 'adapted', 'incorporated',
                'mentorship', 'guidance', 'advice', 'suggestion', 'receptive',
                'open', 'flexible', 'adjusted', 'refined', 'iterated',
                'coaching', 'development', 'growth mindset'
            ],
            'positive_phrases': [
                r'received.*feedback',
                r'incorporated.*feedback',
                r'learned.*from',
                r'improved.*based on',
                r'adapted.*approach',
                r'mentored by',
                r'guidance from',
                r'open to.*feedback',
                r'receptive to.*suggestions',
                r'growth.*mindset'
            ]
        },
        EvaluationCriterion.CURIOSITY: {
            'positive_keywords': [
                'curious', 'explored', 'investigated', 'researched',
                'discovered', 'learned', 'studied', 'questioned',
                'wondered', 'inquired', 'probed', 'examined',
                'delved', 'dug deeper', 'fascinated', 'interested'
            ],
            'positive_phrases': [
                r'wanted to.*understand',
                r'curious.*about',
                r'explored.*options',
                r'researched.*alternatives',
                r'sought.*understanding',
                r'asked.*questions',
                r'investigated.*further',
                r'learned.*about',
                r'discovered.*that',
                r'deep dive'
            ]
        },
        EvaluationCriterion.CREATIVITY: {
            'positive_keywords': [
                'innovative', 'creative', 'novel', 'unique', 'original',
                'invented', 'designed', 'developed', 'pioneered',
                'unconventional', 'breakthrough', 'revolutionary',
                'reimagined', 'transformed', 'ingenious'
            ],
            'positive_phrases': [
                r'creative.*solution',
                r'innovative.*approach',
                r'novel.*method',
                r'unique.*way',
                r'out.*of.*the.*box',
                r'first.*to',
                r'pioneered.*approach',
                r'developed.*new',
                r'invented.*method',
                r'unconventional.*solution'
            ]
        },
        EvaluationCriterion.COLLABORATION: {
            'positive_keywords': [
                'collaborated', 'team', 'partnered', 'coordinated',
                'cooperated', 'worked with', 'cross-functional',
                'stakeholder', 'together', 'jointly', 'collective',
                'consensus', 'facilitated', 'aligned'
            ],
            'positive_phrases': [
                r'worked.*with.*team',
                r'collaborated.*with',
                r'cross-functional.*team',
                r'partnered.*with',
                r'facilitated.*discussion',
                r'stakeholder.*engagement',
                r'incorporated.*feedback.*from',
                r'coordinated.*with',
                r'team.*effort',
                r'collective.*decision'
            ]
        },
        EvaluationCriterion.FOLLOW_THROUGH: {
            'positive_keywords': [
                'completed', 'delivered', 'finished', 'achieved',
                'accomplished', 'executed', 'implemented', 'fulfilled',
                'finalized', 'concluded', 'maintained', 'sustained',
                'consistent', 'thorough', 'comprehensive'
            ],
            'positive_phrases': [
                r'completed.*project',
                r'delivered.*on.*time',
                r'followed.*through',
                r'saw.*through.*completion',
                r'achieved.*goals',
                r'maintained.*throughout',
                r'start.*to.*finish',
                r'executed.*plan',
                r'fulfilled.*commitments',
                r'comprehensive.*implementation'
            ]
        },
        EvaluationCriterion.PROBLEM_SOLVING_MOTIVATION: {
            'positive_keywords': [
                'challenge', 'problem', 'solve', 'solution', 'overcome',
                'tackle', 'address', 'resolve', 'fix', 'troubleshoot',
                'motivated', 'driven', 'passionate', 'eager'
            ],
            'positive_phrases': [
                r'solved.*problem',
                r'motivated.*to.*solve',
                r'tackled.*challenge',
                r'driven.*to.*find',
                r'passionate.*about.*solving',
                r'overcame.*obstacle',
                r'addressed.*issue',
                r'resolved.*problem',
                r'eager.*to.*solve',
                r'enjoyed.*solving'
            ]
        },
        EvaluationCriterion.EVIDENCE_BASED: {
            'positive_keywords': [
                'data', 'evidence', 'metrics', 'measured', 'quantified',
                'tracked', 'analyzed', 'statistics', 'results', 'validated',
                'tested', 'verified', 'proof', 'demonstrated', 'findings'
            ],
            'positive_phrases': [
                r'data.*driven',
                r'evidence.*based',
                r'measured.*impact',
                r'tracked.*metrics',
                r'analyzed.*data',
                r'based.*on.*data',
                r'validated.*through',
                r'tested.*hypothesis',
                r'quantified.*results',
                r'metrics.*showed'
            ]
        },
        EvaluationCriterion.DETAIL_ORIENTATION: {
            'positive_keywords': [
                'detailed', 'thorough', 'meticulous', 'precise',
                'accurate', 'specific', 'comprehensive', 'exhaustive',
                'granular', 'careful', 'rigorous', 'methodical'
            ],
            'positive_phrases': [
                r'attention.*to.*detail',
                r'detailed.*analysis',
                r'thorough.*review',
                r'meticulous.*approach',
                r'precise.*implementation',
                r'comprehensive.*documentation',
                r'carefully.*considered',
                r'methodical.*process',
                r'granular.*level',
                r'rigorous.*testing'
            ]
        },
        EvaluationCriterion.COMMUNICATION: {
            'positive_keywords': [
                'communicated', 'presented', 'articulated', 'explained',
                'documented', 'wrote', 'shared', 'conveyed', 'clarified',
                'discussed', 'facilitated', 'transparent', 'clear'
            ],
            'positive_phrases': [
                r'clearly.*communicated',
                r'effectively.*presented',
                r'articulated.*vision',
                r'explained.*complex',
                r'documented.*process',
                r'shared.*findings',
                r'facilitated.*discussion',
                r'transparent.*communication',
                r'conveyed.*information',
                r'clear.*explanation'
            ]
        },
        EvaluationCriterion.EXPERTISE_ENABLER: {
            'positive_keywords': [
                'expertise', 'knowledge', 'enabled', 'facilitated',
                'leveraged', 'applied', 'pragmatic', 'practical',
                'balanced', 'adapted', 'flexible', 'integrated'
            ],
            'positive_phrases': [
                r'leveraged.*expertise',
                r'applied.*knowledge',
                r'enabled.*team',
                r'expertise.*in.*\w+',
                r'used.*background.*to',
                r'knowledge.*helped',
                r'technical.*expertise.*enabled',
                r'pragmatic.*approach',
                r'balanced.*technical',
                r'adapted.*expertise'
            ]
        }
    }

    def __init__(self):
        """Initialize the pattern analyzer"""
        self.extracted_markers: Dict[EvaluationCriterion, List[LinguisticMarker]] = defaultdict(list)

    def analyze_text(self, text: str, source: str = "document") -> Dict[EvaluationCriterion, PatternFindings]:
        """
        Analyze text to extract linguistic markers for each criterion.

        Args:
            text: Text to analyze
            source: Source identifier (e.g., filename)

        Returns:
            Dictionary mapping criteria to their pattern findings
        """
        text_lower = text.lower()
        findings = {}

        for criterion in EvaluationCriterion:
            positive_markers = []
            phrase_counts = Counter()

            markers = self.CRITERION_MARKERS.get(criterion, {})

            # Extract keyword markers
            for keyword in markers.get('positive_keywords', []):
                # Find instances of this keyword
                pattern = r'\b' + re.escape(keyword) + r'\b'
                matches = re.finditer(pattern, text_lower, re.IGNORECASE)

                for match in matches:
                    start = max(0, match.start() - 100)
                    end = min(len(text), match.end() + 100)
                    context = text[start:end].strip()

                    marker = LinguisticMarker(
                        phrase=keyword,
                        context=context,
                        source=source,
                        associated_criteria=[criterion],
                        marker_type='keyword',
                        confidence=0.7
                    )
                    positive_markers.append(marker)
                    phrase_counts[keyword] += 1

            # Extract phrase pattern markers
            for phrase_pattern in markers.get('positive_phrases', []):
                matches = re.finditer(phrase_pattern, text_lower, re.IGNORECASE)

                for match in matches:
                    matched_text = match.group(0)
                    start = max(0, match.start() - 100)
                    end = min(len(text), match.end() + 100)
                    context = text[start:end].strip()

                    marker = LinguisticMarker(
                        phrase=matched_text,
                        context=context,
                        source=source,
                        associated_criteria=[criterion],
                        marker_type='phrase_pattern',
                        confidence=0.85
                    )
                    positive_markers.append(marker)
                    phrase_counts[matched_text] += 1

            # Generate summary
            top_phrases = phrase_counts.most_common(5)
            summary = self._generate_pattern_summary(criterion, positive_markers, top_phrases)

            findings[criterion] = PatternFindings(
                criterion=criterion,
                positive_markers=positive_markers,
                negative_markers=[],  # Could add negative indicators
                phrase_frequency=dict(phrase_counts),
                pattern_summary=summary
            )

        return findings

    def _generate_pattern_summary(
        self,
        criterion: EvaluationCriterion,
        markers: List[LinguisticMarker],
        top_phrases: List[Tuple[str, int]]
    ) -> str:
        """Generate a summary of patterns found"""
        if not markers:
            return f"No strong linguistic markers found for {criterion.display_name}."

        summary_parts = [
            f"Found {len(markers)} linguistic markers for {criterion.display_name}."
        ]

        if top_phrases:
            phrases_str = ", ".join([f"'{phrase}' ({count}x)" for phrase, count in top_phrases[:3]])
            summary_parts.append(f"Most frequent indicators: {phrases_str}.")

        # Analyze marker types
        keyword_count = sum(1 for m in markers if m.marker_type == 'keyword')
        pattern_count = sum(1 for m in markers if m.marker_type == 'phrase_pattern')

        summary_parts.append(
            f"Includes {keyword_count} keyword matches and {pattern_count} phrase patterns."
        )

        return " ".join(summary_parts)

    def analyze_multiple_files(
        self,
        file_contents: List[Dict[str, str]]
    ) -> Dict[EvaluationCriterion, PatternFindings]:
        """
        Analyze multiple files and aggregate findings.

        Args:
            file_contents: List of dicts with 'content' and 'metadata'

        Returns:
            Aggregated pattern findings across all files
        """
        all_findings = defaultdict(lambda: {
            'markers': [],
            'phrase_counts': Counter()
        })

        # Analyze each file
        for file_data in file_contents:
            content = file_data['content']
            source = file_data['metadata']['filename']

            file_findings = self.analyze_text(content, source)

            for criterion, findings in file_findings.items():
                all_findings[criterion]['markers'].extend(findings.positive_markers)
                all_findings[criterion]['phrase_counts'].update(findings.phrase_frequency)

        # Aggregate into final findings
        aggregated_findings = {}

        for criterion, data in all_findings.items():
            top_phrases = data['phrase_counts'].most_common(5)
            summary = self._generate_pattern_summary(
                criterion,
                data['markers'],
                top_phrases
            )

            aggregated_findings[criterion] = PatternFindings(
                criterion=criterion,
                positive_markers=data['markers'],
                negative_markers=[],
                phrase_frequency=dict(data['phrase_counts']),
                pattern_summary=summary
            )

        return aggregated_findings

    def get_innovation_indicators(
        self,
        findings: Dict[EvaluationCriterion, PatternFindings]
    ) -> Dict[str, any]:
        """
        Extract specific indicators of innovation program potential.

        Args:
            findings: Pattern findings from analysis

        Returns:
            Dictionary of innovation indicators
        """
        innovation_criteria = [
            EvaluationCriterion.CREATIVITY,
            EvaluationCriterion.CURIOSITY,
            EvaluationCriterion.PROBLEM_SOLVING_MOTIVATION,
            EvaluationCriterion.CRITICAL_THINKING
        ]

        total_markers = sum(
            len(findings[c].positive_markers)
            for c in innovation_criteria
            if c in findings
        )

        # Extract top innovation phrases
        innovation_phrases = Counter()
        for criterion in innovation_criteria:
            if criterion in findings:
                innovation_phrases.update(findings[criterion].phrase_frequency)

        return {
            'total_innovation_markers': total_markers,
            'top_innovation_phrases': innovation_phrases.most_common(10),
            'innovation_criteria_coverage': len([
                c for c in innovation_criteria
                if c in findings and len(findings[c].positive_markers) > 0
            ]),
            'innovation_potential_score': min(10, total_markers / 5)  # Rough score
        }
