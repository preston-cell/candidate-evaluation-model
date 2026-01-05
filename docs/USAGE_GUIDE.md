# Usage Guide

Detailed guide for using the Candidate Evaluator tool.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Evaluating Candidates](#evaluating-candidates)
3. [Understanding Results](#understanding-results)
4. [Batch Processing](#batch-processing)
5. [Comparison Reports](#comparison-reports)
6. [Best Practices](#best-practices)
7. [Troubleshooting](#troubleshooting)

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Anthropic API key ([Get one here](https://console.anthropic.com/))
- Candidate application materials (PDF, DOCX, TXT, or MD format)

### Installation

```bash
pip install -e .
```

### Initial Configuration

1. Set your API key:
   ```bash
   export ANTHROPIC_API_KEY="your-key-here"
   ```

2. (Optional) Create custom configuration:
   ```bash
   candidate-eval init
   ```

## Evaluating Candidates

### Single Candidate Evaluation

The most common use case is evaluating a single candidate:

```bash
candidate-eval evaluate resume.pdf cover_letter.txt \
  --candidate-id CAND001 \
  --name "Jane Doe"
```

This will:
1. Process all provided files
2. Extract text content
3. Send to Claude for evaluation
4. Generate scores for all 11 criteria
5. Export results to `./results/` directory

### Specifying Output Formats

Choose which formats to export:

```bash
candidate-eval evaluate resume.pdf \
  --candidate-id CAND001 \
  --format json markdown html csv
```

Available formats:
- **json**: Structured data for programmatic use
- **markdown**: Human-readable text report
- **html**: Styled web page
- **csv**: Spreadsheet-compatible tabular data

### Custom Output Directory

```bash
candidate-eval evaluate resume.pdf \
  --candidate-id CAND001 \
  --output-dir /path/to/custom/directory
```

## Understanding Results

### Score Interpretation

Scores range from 1-10:

- **1-3**: Insufficient evidence or significant concerns
- **4-5**: Limited evidence or mixed signals
- **6-7**: Adequate evidence of competency
- **8-9**: Strong evidence of competency
- **10**: Exceptional evidence of competency

### Confidence Levels

Each score includes a confidence level:

- **High**: Strong, clear evidence from materials
- **Medium**: Some evidence, but could be stronger
- **Low**: Limited evidence available; score is best estimate

### Evidence and Quotes

Every score includes:
- Direct quotes from the materials
- Source file for each quote
- Context explaining relevance

Example:
```markdown
**Evidence**:
1. From resume.pdf:
   > "Led development of microservices architecture serving 10M+ users"

   Demonstrates ability to handle complex technical challenges at scale
```

### Overall Assessment

The overall score is a weighted average of all criteria scores. Default weight is 10 for all criteria, but this can be customized in `config.yaml`.

## Batch Processing

### Preparing the CSV File

Create a CSV file with candidate information:

```csv
candidate_id,name,material_paths
CAND001,John Doe,materials/john_resume.pdf;materials/john_cover.txt
CAND002,Jane Smith,materials/jane_resume.pdf;materials/jane_cover.txt
CAND003,Bob Johnson,materials/bob_resume.pdf
```

**Important**:
- `material_paths` should be semicolon-separated
- Paths can be relative or absolute
- `name` column is optional

### Running Batch Evaluation

```bash
candidate-eval batch candidates.csv --format json markdown csv
```

This will:
1. Process each candidate sequentially
2. Generate individual reports for each
3. Create a batch summary
4. Export to specified formats

### Batch Summary Files

The batch command creates:
- Individual evaluation files for each candidate
- `batch_results.csv` - Summary table
- `batch_summary.md` - Ranked summary report

## Comparison Reports

When evaluating multiple candidates, generate a comparison report:

```bash
candidate-eval batch candidates.csv --compare
```

This creates additional files:
- `comparison.json` - Structured comparison data
- `comparison.md` - Side-by-side comparison report
- `comparison_matrix.csv` - Comparison table

### Comparison Features

The comparison report includes:
- Ranked list of candidates
- Best performer for each criterion
- Relative strengths and weaknesses
- Recommendations for each candidate

## Best Practices

### Preparing Materials

For best results:

1. **Include diverse materials**: Resume, cover letter, writing samples, project descriptions
2. **Ensure quality**: Clear, readable text in supported formats
3. **Completeness**: More context helps evaluation accuracy
4. **Relevance**: Include materials that demonstrate the criteria

### Interpreting Results

1. **Consider confidence levels**: Low confidence scores may need additional assessment
2. **Read the reasoning**: Don't just look at numbers
3. **Review evidence**: Check if quotes support the scores
4. **Note limitations**: Some criteria are harder to assess from written materials alone

### When to Use Each Format

- **JSON**: For integration with other tools, data analysis
- **Markdown**: For reading, sharing with non-technical stakeholders
- **HTML**: For presentation, email sharing
- **CSV**: For spreadsheet analysis, batch comparisons

## Troubleshooting

### Common Issues

**Issue**: `ANTHROPIC_API_KEY not found`
```bash
# Solution: Set environment variable
export ANTHROPIC_API_KEY="your-key-here"
```

**Issue**: `Unsupported file format`
```bash
# Solution: Convert to supported format (PDF, DOCX, TXT, MD)
# Or use online converters
```

**Issue**: `File too large`
```bash
# Solution: Increase max file size in config.yaml
processing:
  max_file_size_mb: 20
```

**Issue**: API timeout or rate limits
```bash
# Solution: Reduce batch size in config.yaml
processing:
  batch_size: 3
```

### Getting Help

If you encounter issues:

1. Check the log file: `candidate_evaluator.log`
2. Run with verbose logging: `candidate-eval --verbose evaluate ...`
3. Review error messages carefully
4. Check [GitHub Issues](https://github.com/yourusername/candidate-evaluation-model/issues)

## Advanced Usage

### Custom Criteria

You can evaluate against custom criteria by modifying the prompts in `candidate_evaluator/prompts/evaluation_prompts.py`.

### Programmatic Use

```python
from candidate_evaluator import CandidateEvaluator
from candidate_evaluator.utils.config import load_config

config = load_config()
evaluator = CandidateEvaluator(config)

result = evaluator.evaluate_candidate(
    candidate_id="CAND001",
    material_paths=["resume.pdf"],
    candidate_name="Jane Doe"
)

# Access scores
for score in result.scores:
    print(f"{score.criterion.display_name}: {score.score}/10")
```

### Adjusting Weights

Edit `config.yaml` to prioritize certain criteria:

```yaml
criteria:
  weights:
    critical_thinking: 15  # Higher weight
    collaboration: 10
    curiosity: 5  # Lower weight
```

## Tips for Best Results

1. **Provide context**: More material = better assessment
2. **Quality over quantity**: Well-written materials are more valuable
3. **Diversity**: Include different types of documents (technical, narrative, etc.)
4. **Review evidence**: Always check the quotes that support scores
5. **Use confidence levels**: Pay attention to low-confidence scores
6. **Supplement with interviews**: Written materials can't capture everything

## Next Steps

- Try evaluating sample materials: `examples/sample_materials/`
- Customize criteria weights in `config.yaml`
- Set up batch evaluation for your candidate pool
- Explore the web interface: `streamlit run candidate_evaluator/web_app.py`
