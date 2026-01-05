# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
