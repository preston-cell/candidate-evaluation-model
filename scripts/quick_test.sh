#!/bin/bash
# Quick test script for Candidate Evaluator

set -e

echo "🧪 Running Quick Test of Candidate Evaluator"
echo "============================================="

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo "⚠️  Warning: No virtual environment detected"
    echo "   Consider activating venv: source venv/bin/activate"
    echo ""
fi

# Check if API key is set
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "❌ Error: ANTHROPIC_API_KEY not set"
    echo "   Please set your API key: export ANTHROPIC_API_KEY='your-key'"
    exit 1
fi

echo "✅ API key found"
echo ""

# Run example evaluation
echo "📊 Testing single candidate evaluation..."
echo ""

python -m candidate_evaluator.cli evaluate \
    examples/sample_materials/sample_resume.txt \
    examples/sample_materials/sample_cover_letter.txt \
    --candidate-id TEST001 \
    --name "Jane Doe" \
    --format json markdown \
    --output-dir ./test_results

echo ""
echo "✅ Evaluation complete!"
echo ""
echo "📁 Results saved to: ./test_results/"
echo ""
echo "View results:"
echo "  JSON: cat test_results/TEST001_evaluation.json"
echo "  Markdown: cat test_results/TEST001_evaluation.md"
echo ""
echo "🎉 Quick test successful!"
