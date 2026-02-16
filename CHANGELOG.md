# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2026-02-03

### Added

#### Admit Pattern Analysis Feature
- **New "Admit Patterns" tab** in the web interface for analyzing what distinguishes admitted from rejected candidates
- **Pattern discovery system** that:
  - Accepts batch upload of candidate application PDFs
  - Uses CSV mapping file to specify admit/reject labels for each candidate
  - Evaluates all candidates (using holistic or criteria-based mode)
  - Analyzes patterns distinguishing admitted from rejected candidates
  - Identifies predictive factors, common strengths/weaknesses, and surprising cases

#### New Components
- `AdmitPatternAnalyzer` class in `pattern_analyzer.py` for running pattern analysis
- `AdmitPatternAnalysisResult`, `AdmitPatternCategory`, `AdmitPatternEvidence` models
- `ADMIT_PATTERN_ANALYSIS_PROMPT` template for Claude-powered pattern discovery
- `get_admit_pattern_analysis_prompt()` function for generating analysis prompts
- Sample admit mapping CSV template in `examples/sample_admit_mapping.csv`

#### CSV Format for Admit Mapping
```csv
filename,admit_status
candidate_001_application.pdf,yes
candidate_002_application.pdf,no
```

### Technical Details
- Supports both holistic and criteria-based evaluation modes for candidate processing
- Calculates basic statistics without API calls for quick preview
- Full Claude-powered analysis for detailed pattern discovery
- Saves analysis results to JSON for later reference
- Handles large batches by processing candidates sequentially

## [1.0.0] - 2024-01-05

### Added

#### Core Features
- **Evidence-based evaluation system** using Claude API (Sonnet 4.5)
- **11 evaluation criteria** with customizable weights
- **Multi-format file processing**: PDF, DOCX, TXT, Markdown support
- **Batch processing** for evaluating multiple candidates
- **Comparison mode** for side-by-side candidate analysis

#### Interfaces
- **CLI tool** with comprehensive commands:
  - `evaluate` - Single candidate evaluation
  - `batch` - Batch processing from CSV
  - `init` - Configuration initialization
- **Streamlit web interface** with:
  - Single evaluation page
  - Batch evaluation page
  - Results viewer
  - Settings panel

#### Export Formats
- **JSON exporter** for structured data
- **Markdown exporter** for human-readable reports
- **HTML exporter** with styled templates
- **CSV exporter** for data analysis

#### Configuration
- YAML-based configuration system
- Environment variable support
- Customizable criteria weights
- Flexible output settings

#### Developer Tools
- Comprehensive test suite
- Type hints throughout
- Detailed logging system
- Error handling and validation

#### Documentation
- Complete README with quick start
- Detailed usage guide
- Contributing guidelines
- Example materials and templates

### Technical Details

- Python 3.8+ support
- Pydantic models for data validation
- Click for CLI framework
- Rich for terminal formatting
- Comprehensive error handling
- Production-ready logging

### Notes

Initial release providing a complete, production-ready candidate evaluation system with CLI and web interfaces, multiple export formats, and comprehensive documentation.
