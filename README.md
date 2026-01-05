# Candidate Evaluator

> AI-powered candidate assessment tool using Claude API for evidence-based evaluation against specific criteria

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

## 📋 Overview

Candidate Evaluator is a production-ready tool that leverages Anthropic's Claude AI to evaluate candidate application materials against 11 specific criteria with evidence-based scoring. It provides structured, objective assessments with detailed reasoning and supporting quotes from the materials.

### Key Features

✅ **Evidence-Based Evaluation** - Every score includes specific quotes and examples from materials
✅ **Research-Style Analysis** - Generate detailed research reports with linguistic marker identification
✅ **Innovation Potential Assessment** - Identify markers indicating innovation program potential
✅ **Linguistic Pattern Analysis** - Extract and analyze key phrases that correlate with competencies
✅ **11 Evaluation Criteria** - Comprehensive assessment framework
✅ **Multiple File Formats** - Supports PDF, DOCX, TXT, and Markdown
✅ **Batch Processing** - Evaluate multiple candidates efficiently
✅ **Comparison Mode** - Compare candidates side-by-side
✅ **Multiple Export Formats** - JSON, Markdown, HTML, CSV, and Research Papers
✅ **CLI & Web Interface** - Command-line tool and optional Streamlit web UI
✅ **Customizable Criteria** - Configure weights and add custom criteria
✅ **Production Ready** - Comprehensive error handling, logging, and testing

## 🎯 Evaluation Criteria

Each candidate is scored 1-10 on the following criteria:

1. **Critical Thinking / Logical Analysis** - Ability to analyze information objectively and draw logical conclusions
2. **Coachability** - Receptiveness to feedback and willingness to learn
3. **Curiosity** - Drive to explore and seek deeper understanding
4. **Demonstrated Creativity** - Ability to develop innovative solutions
5. **Collaboration** - Working effectively with others and incorporating diverse inputs
6. **Follow Through** - Consistency in completing tasks and projects
7. **Problem-Solving Motivation** - Intrinsic drive to tackle challenges
8. **Evidence-Based Thinking** - Reliance on data and evidence over assumptions
9. **Detail Orientation** - Attention to specifics and thoroughness
10. **Effective Communication** - Clarity and precision in expression
11. **Expertise as Enabler** - Leveraging knowledge to enable solutions rather than limit possibilities

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/candidate-evaluation-model.git
cd candidate-evaluation-model

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install the package
pip install -e .
```

### Configuration

1. **Set up your API key** (choose one method):

   ```bash
   # Option 1: Environment variable
   export ANTHROPIC_API_KEY="your-api-key-here"

   # Option 2: Create config file
   candidate-eval init
   # Edit config.yaml and add your API key
   ```

2. **Customize settings** (optional):
   - Edit `config.yaml` to adjust criteria weights, output formats, etc.

### Basic Usage

**Evaluate a single candidate:**

```bash
candidate-eval evaluate resume.pdf cover_letter.txt \
  --candidate-id CAND001 \
  --name "Jane Doe" \
  --format markdown html
```

**Generate research report with linguistic analysis:**

```bash
candidate-eval evaluate resume.pdf cover_letter.txt \
  --candidate-id CAND001 \
  --research
```

This generates a comprehensive research paper that includes:
- Linguistic marker analysis
- Innovation potential assessment
- Pattern identification
- Statistical summaries
- Evidence correlations
- Detailed findings and methodology

**Batch evaluation:**

```bash
# Create a CSV file with candidate information
# Format: candidate_id,name,material_paths (semicolon-separated)
candidate-eval batch candidates.csv --compare --format json markdown csv
```

**Launch web interface:**

```bash
streamlit run candidate_evaluator/web_app.py
```

## 📖 Documentation

### CLI Commands

#### `evaluate` - Evaluate Single Candidate

```bash
candidate-eval evaluate [MATERIALS...] \
  --candidate-id ID \
  --name "Candidate Name" \
  --output-dir ./results \
  --format json markdown html csv
```

**Arguments:**
- `MATERIALS`: One or more paths to candidate materials (PDF, DOCX, TXT, MD)

**Options:**
- `--candidate-id, -id`: Unique candidate identifier (required)
- `--name, -n`: Candidate name (optional)
- `--output-dir, -o`: Output directory (default: ./results)
- `--format, -f`: Output format(s) - can specify multiple

#### `batch` - Batch Evaluation

```bash
candidate-eval batch CANDIDATES_FILE \
  --output-dir ./results \
  --format json markdown csv \
  --compare
```

**Arguments:**
- `CANDIDATES_FILE`: CSV file with candidate information

**CSV Format:**
```csv
candidate_id,name,material_paths
CAND001,John Doe,materials/john_resume.pdf;materials/john_cover.txt
CAND002,Jane Smith,materials/jane_resume.pdf;materials/jane_cover.txt
```

**Options:**
- `--output-dir, -o`: Output directory
- `--format, -f`: Output format(s)
- `--compare`: Generate comparison report

#### `init` - Initialize Configuration

```bash
candidate-eval init
```

Creates `config.yaml` and `.env` template files in the current directory.

### Python API

```python
from candidate_evaluator import CandidateEvaluator
from candidate_evaluator.utils.config import load_config

# Load configuration
config = load_config()

# Create evaluator
evaluator = CandidateEvaluator(config)

# Evaluate a candidate
result = evaluator.evaluate_candidate(
    candidate_id="CAND001",
    material_paths=["resume.pdf", "cover_letter.txt"],
    candidate_name="Jane Doe"
)

# Access results
print(f"Overall Score: {result.overall_score:.2f}")
print(f"Recommendation: {result.recommendation}")

# Export results
from candidate_evaluator.exporters import MarkdownExporter

MarkdownExporter.export_evaluation(
    result,
    output_path="results/evaluation.md"
)
```

### Output Formats

#### JSON
Structured data format, ideal for integration with other tools:
```json
{
  "candidate": {
    "candidate_id": "CAND001",
    "name": "Jane Doe",
    "overall_score": 8.5
  },
  "scores": [...]
}
```

#### Markdown
Human-readable format with visual score bars and organized sections.

#### HTML
Styled web page with interactive elements, ready to view in browser.

#### CSV
Tabular format for analysis in spreadsheets or data tools.

## 🎨 Web Interface

The optional Streamlit web interface provides:

- **Single Evaluation** - Upload files and evaluate candidates through a web form
- **Batch Evaluation** - Upload CSV and process multiple candidates
- **View Results** - Browse and compare previous evaluations
- **Settings** - Configure criteria weights and preferences

Launch with:
```bash
streamlit run candidate_evaluator/web_app.py
```

## 📂 Project Structure

```
candidate-evaluation-model/
├── candidate_evaluator/          # Main package
│   ├── core/                      # Core evaluation logic
│   │   ├── evaluator.py          # Main evaluator class
│   │   └── models.py             # Data models
│   ├── prompts/                   # Prompt templates
│   │   └── evaluation_prompts.py
│   ├── utils/                     # Utilities
│   │   ├── config.py             # Configuration management
│   │   ├── logger.py             # Logging setup
│   │   └── file_processor.py    # File processing
│   ├── exporters/                 # Export functionality
│   │   ├── json_exporter.py
│   │   ├── markdown_exporter.py
│   │   ├── html_exporter.py
│   │   └── csv_exporter.py
│   ├── cli.py                     # CLI interface
│   └── web_app.py                # Streamlit web app
├── tests/                         # Test suite
├── examples/                      # Example materials
│   ├── sample_materials/
│   └── sample_batch.csv
├── config_templates/              # Configuration templates
├── docs/                          # Documentation
├── requirements.txt              # Dependencies
├── setup.py                      # Package setup
└── README.md                     # This file
```

## ⚙️ Configuration

### config.yaml

```yaml
api:
  anthropic_api_key: "your-key-here"
  model: "claude-sonnet-4-5-20250929"
  max_tokens: 4096
  temperature: 0.3

criteria:
  weights:
    critical_thinking: 10
    coachability: 10
    curiosity: 10
    # ... other criteria

output:
  output_dir: "./results"
  default_formats: ["json", "markdown"]
  include_evidence: true
  include_quotes: true

processing:
  max_file_size_mb: 10
  supported_formats: ["pdf", "docx", "txt", "md"]
  batch_size: 5

logging:
  level: "INFO"
  log_file: "./candidate_evaluator.log"
  console_logging: true
```

### Environment Variables

```bash
ANTHROPIC_API_KEY=your-api-key-here
MODEL=claude-sonnet-4-5-20250929
OUTPUT_DIR=./results
LOG_LEVEL=INFO
```

## 🧪 Testing

Run tests with pytest:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=candidate_evaluator --cov-report=html

# Run specific test file
pytest tests/test_file_processor.py
```

## 🤝 Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Run tests and ensure they pass
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

### Development Setup

```bash
# Install development dependencies
pip install -r requirements.txt
pip install -e ".[dev]"

# Run linting
flake8 candidate_evaluator/
black candidate_evaluator/

# Run type checking
mypy candidate_evaluator/
```

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [Anthropic's Claude API](https://www.anthropic.com/)
- Uses [Click](https://click.palletsprojects.com/) for CLI
- UI powered by [Streamlit](https://streamlit.io/)
- File processing with [PyPDF2](https://pypdf2.readthedocs.io/) and [python-docx](https://python-docx.readthedocs.io/)

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/candidate-evaluation-model/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/candidate-evaluation-model/discussions)
- **Email**: your.email@example.com

## 🗺️ Roadmap

- [ ] Support for additional file formats (ODT, RTF)
- [ ] Integration with ATS systems
- [ ] Custom criteria builder UI
- [ ] Automated interview question generation
- [ ] Multi-language support
- [ ] API server mode
- [ ] Enhanced comparison analytics
- [ ] Export to additional formats (PowerPoint, Google Docs)

## 🔬 Research Reports & Linguistic Analysis

The tool's research report feature provides an academic-style analysis that goes beyond simple scoring. When you use the `--research` flag, the system performs deep linguistic analysis to identify patterns and markers that correlate with each evaluation criterion.

### What's Included in Research Reports

**1. Research Intention & Methodology**
- Clear statement of research objectives
- Detailed methodology description
- Evaluation framework explanation
- Limitations and considerations

**2. Linguistic Marker Analysis**
- Automatic extraction of criterion-specific keywords and phrases
- Pattern matching across all materials
- Frequency analysis of key indicators
- Marker density metrics (per 1,000 words)

**3. Innovation Potential Assessment**
- Specific assessment of innovation program suitability
- Identification of creativity markers (e.g., "innovative approach", "novel solution")
- Curiosity indicators (e.g., "explored alternatives", "researched options")
- Problem-solving markers (e.g., "tackled challenge", "solved problem")
- Analytical thinking patterns (e.g., "analyzed data", "systematic approach")

**4. Key Findings**
- Primary findings across all criteria
- Marker-score correlations showing which phrases correlate with high scores
- Identified patterns in language use
- Notable observations and insights

**5. Statistical Summary**
- Total linguistic markers identified
- Distribution across criteria
- Evidence strength assessment
- Confidence levels for each score

**6. Detailed Evidence Appendices**
- Complete list of markers found for each criterion
- Context for each marker with source attribution
- Phrase frequency tables
- Sample evidence with direct quotes

### Example Research Report Sections

```markdown
## Innovation Potential Assessment

**Innovation Score**: 8.5/10 - HIGH Potential

**Innovation Markers Identified**: 47 total
- Creativity indicators: 12 unique phrases
  - "innovative solution", "creative approach", "novel method"
- Curiosity indicators: 15 unique phrases
  - "explored alternatives", "researched options", "investigated further"
- Problem-solving indicators: 11 unique phrases
  - "solved complex problem", "overcame obstacle", "tackled challenge"

**Recommendation**: Strong candidate for innovation programs.
Demonstrates exceptional creative thinking and problem-solving orientation.

## Linguistic Pattern Analysis

### Critical Thinking Markers
- **Total markers found**: 23
- **Unique phrases**: 15
- **Marker density**: 3.2 per 1,000 words
- **Evidence strength**: Strong

**Most Frequent Phrases**:
1. "analyzed data" (5 occurrences)
2. "systematic approach" (3 occurrences)
3. "evaluated options" (3 occurrences)
4. "root cause analysis" (2 occurrences)
5. "logical conclusion" (2 occurrences)
```

### Use Cases for Research Reports

- **Academic Research**: Study language patterns in successful candidates
- **Program Selection**: Identify candidates for specialized innovation programs
- **Hiring Optimization**: Understand what markers correlate with high performance
- **Process Improvement**: Identify gaps in how candidates present their experiences
- **Training Development**: See what competencies candidates struggle to demonstrate

## 📊 Example Output

```markdown
# Candidate Evaluation Report

**Candidate ID**: CAND001
**Name**: Jane Doe
**Overall Score**: 8.5/10
**Recommendation**: Strong fit - Highly recommended for next stage

## Key Strengths
- Exceptional evidence-based thinking and data-driven approach
- Strong collaboration skills with proven cross-team experience
- High coachability with growth mindset

## Detailed Scores
- Critical Thinking: 9/10
- Collaboration: 9/10
- Evidence-Based: 9/10
- Communication: 8/10
...
```

---

**Made with ❤️ by the Candidate Evaluator Team**
