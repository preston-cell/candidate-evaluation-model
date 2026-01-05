from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="candidate-evaluator",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="AI-powered candidate evaluation tool using Claude API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/candidate-evaluation-model",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "anthropic>=0.40.0",
        "python-dotenv>=1.0.0",
        "pydantic>=2.0.0",
        "pyyaml>=6.0",
        "PyPDF2>=3.0.0",
        "python-docx>=1.0.0",
        "markdown>=3.5.0",
        "click>=8.1.0",
        "rich>=13.0.0",
        "tabulate>=0.9.0",
        "pandas>=2.0.0",
    ],
    extras_require={
        "web": ["streamlit>=1.28.0", "flask>=3.0.0"],
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.5.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "candidate-eval=candidate_evaluator.cli:main",
        ],
    },
)
