"""Streamlit web interface for candidate evaluator"""

import streamlit as st
import tempfile
import os
from pathlib import Path
from datetime import datetime
import pandas as pd

from candidate_evaluator.core.evaluator import CandidateEvaluator
from candidate_evaluator.utils.config import load_config, get_default_config
from candidate_evaluator.exporters import (
    JSONExporter,
    MarkdownExporter,
    HTMLExporter,
    CSVExporter
)


# Page config
st.set_page_config(
    page_title="Candidate Evaluator",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)


def init_session_state():
    """Initialize session state variables"""
    if 'evaluator' not in st.session_state:
        st.session_state.evaluator = None
    if 'config' not in st.session_state:
        st.session_state.config = None
    if 'evaluation_results' not in st.session_state:
        st.session_state.evaluation_results = []


def load_configuration():
    """Load configuration"""
    if st.session_state.config is None:
        try:
            config = load_config()
        except:
            try:
                config = get_default_config()
            except Exception as e:
                st.error(f"Error loading configuration: {e}")
                st.info("Please set ANTHROPIC_API_KEY environment variable or create config.yaml")
                return None

        st.session_state.config = config
        st.session_state.evaluator = CandidateEvaluator(config)

    return st.session_state.config


def main():
    """Main application"""
    init_session_state()

    # Sidebar
    with st.sidebar:
        st.title("📊 Candidate Evaluator")
        st.markdown("---")

        page = st.radio(
            "Navigation",
            ["Single Evaluation", "Batch Evaluation", "View Results", "Settings"]
        )

        st.markdown("---")
        st.markdown("### About")
        st.markdown(
            "AI-powered candidate evaluation using Claude API. "
            "Evaluate candidates against 11 specific criteria with evidence-based scoring."
        )

    # Load config
    config = load_configuration()
    if config is None:
        st.stop()

    # Pages
    if page == "Single Evaluation":
        single_evaluation_page()
    elif page == "Batch Evaluation":
        batch_evaluation_page()
    elif page == "View Results":
        view_results_page()
    elif page == "Settings":
        settings_page()


def single_evaluation_page():
    """Single candidate evaluation page"""
    st.title("Single Candidate Evaluation")

    col1, col2 = st.columns([2, 1])

    with col1:
        candidate_id = st.text_input(
            "Candidate ID *",
            placeholder="e.g., CAND001",
            help="Unique identifier for the candidate"
        )

        candidate_name = st.text_input(
            "Candidate Name (optional)",
            placeholder="e.g., John Doe"
        )

    with col2:
        st.info(
            "**Supported Formats**\n\n"
            "• PDF (.pdf)\n"
            "• Word (.docx)\n"
            "• Text (.txt)\n"
            "• Markdown (.md)"
        )

    st.markdown("### Upload Application Materials")

    uploaded_files = st.file_uploader(
        "Upload one or more files",
        type=['pdf', 'docx', 'txt', 'md'],
        accept_multiple_files=True,
        help="Upload resume, cover letter, writing samples, etc."
    )

    # Export options
    st.markdown("### Export Options")
    export_formats = st.multiselect(
        "Output formats",
        ['JSON', 'Markdown', 'HTML', 'CSV'],
        default=['Markdown', 'HTML']
    )

    if st.button("Evaluate Candidate", type="primary", disabled=not (candidate_id and uploaded_files)):
        with st.spinner("Evaluating candidate... This may take a minute."):
            try:
                # Save uploaded files to temp directory
                temp_dir = tempfile.mkdtemp()
                material_paths = []

                for uploaded_file in uploaded_files:
                    temp_path = os.path.join(temp_dir, uploaded_file.name)
                    with open(temp_path, 'wb') as f:
                        f.write(uploaded_file.getbuffer())
                    material_paths.append(temp_path)

                # Evaluate
                evaluator = st.session_state.evaluator
                result = evaluator.evaluate_candidate(
                    candidate_id=candidate_id,
                    material_paths=material_paths,
                    candidate_name=candidate_name or None
                )

                # Store result
                st.session_state.evaluation_results.append(result)

                # Display results
                st.success("✅ Evaluation completed!")

                # Overall score
                st.markdown("### Overall Assessment")
                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric("Overall Score", f"{result.overall_score:.2f}/10")

                with col2:
                    st.metric("Criteria Evaluated", len(result.scores))

                with col3:
                    avg_confidence = sum(
                        1 if s.confidence == 'high' else 0.5 if s.confidence == 'medium' else 0.25
                        for s in result.scores
                    ) / len(result.scores)
                    confidence_label = "High" if avg_confidence > 0.7 else "Medium" if avg_confidence > 0.4 else "Low"
                    st.metric("Avg Confidence", confidence_label)

                st.markdown(f"**Recommendation:** {result.recommendation}")
                st.markdown(result.overall_assessment)

                # Strengths and areas
                col1, col2 = st.columns(2)

                with col1:
                    if result.strengths:
                        st.markdown("#### 💪 Key Strengths")
                        for strength in result.strengths:
                            st.markdown(f"- {strength}")

                with col2:
                    if result.areas_for_development:
                        st.markdown("#### 📈 Areas for Development")
                        for area in result.areas_for_development:
                            st.markdown(f"- {area}")

                # Detailed scores
                st.markdown("### Detailed Scores by Criterion")

                # Create DataFrame for scores
                score_data = []
                for score in sorted(result.scores, key=lambda s: s.score, reverse=True):
                    score_data.append({
                        'Criterion': score.criterion.display_name,
                        'Score': score.score,
                        'Confidence': score.confidence.capitalize(),
                        'Reasoning': score.reasoning[:100] + '...' if len(score.reasoning) > 100 else score.reasoning
                    })

                df = pd.DataFrame(score_data)

                # Display as styled dataframe
                st.dataframe(
                    df,
                    use_container_width=True,
                    hide_index=True
                )

                # Detailed evidence (expandable)
                with st.expander("View Detailed Evidence"):
                    for score in result.scores:
                        st.markdown(f"#### {score.criterion.display_name}")
                        st.markdown(f"**Score:** {score.score}/10 ({score.confidence} confidence)")
                        st.markdown(f"**Reasoning:** {score.reasoning}")

                        if score.evidence:
                            st.markdown("**Evidence:**")
                            for i, ev in enumerate(score.evidence, 1):
                                st.markdown(f"{i}. *From {ev.source}:*")
                                st.markdown(f"> {ev.quote}")
                                st.markdown(f"   {ev.context}")

                        if score.notes:
                            st.info(f"**Notes:** {score.notes}")

                        st.markdown("---")

                # Export results
                st.markdown("### Export Results")

                output_dir = Path("./results")
                output_dir.mkdir(exist_ok=True)

                export_files = []

                if 'JSON' in export_formats:
                    json_path = output_dir / f"{candidate_id}_evaluation.json"
                    JSONExporter.export_evaluation(result, json_path)
                    export_files.append(('JSON', json_path))

                if 'Markdown' in export_formats:
                    md_path = output_dir / f"{candidate_id}_evaluation.md"
                    MarkdownExporter.export_evaluation(result, md_path)
                    export_files.append(('Markdown', md_path))

                if 'HTML' in export_formats:
                    html_path = output_dir / f"{candidate_id}_evaluation.html"
                    HTMLExporter.export_evaluation(result, html_path)
                    export_files.append(('HTML', html_path))

                if 'CSV' in export_formats:
                    csv_path = output_dir / f"{candidate_id}_evaluation.csv"
                    CSVExporter.export_evaluation(result, csv_path)
                    export_files.append(('CSV', csv_path))

                for format_name, file_path in export_files:
                    with open(file_path, 'rb') as f:
                        st.download_button(
                            label=f"Download {format_name}",
                            data=f,
                            file_name=file_path.name,
                            mime='application/octet-stream'
                        )

            except Exception as e:
                st.error(f"Error during evaluation: {e}")
                import traceback
                st.exception(e)


def batch_evaluation_page():
    """Batch evaluation page"""
    st.title("Batch Candidate Evaluation")

    st.markdown(
        "Upload a CSV file with candidate information and materials. "
        "The CSV should have columns: `candidate_id`, `name` (optional), `material_paths` (semicolon-separated)"
    )

    st.markdown("### Example CSV Format")
    st.code(
        "candidate_id,name,material_paths\n"
        "CAND001,John Doe,materials/john_resume.pdf;materials/john_cover.txt\n"
        "CAND002,Jane Smith,materials/jane_resume.pdf;materials/jane_cover.txt",
        language="csv"
    )

    csv_file = st.file_uploader(
        "Upload Candidates CSV",
        type=['csv'],
        help="CSV file with candidate information"
    )

    generate_comparison = st.checkbox("Generate comparison report", value=True)

    if csv_file and st.button("Evaluate All Candidates", type="primary"):
        st.info("Batch evaluation can take several minutes depending on the number of candidates.")

        try:
            # Load CSV
            import csv
            import io

            content = csv_file.read().decode('utf-8')
            reader = csv.DictReader(io.StringIO(content))

            candidates = []
            for row in reader:
                material_paths = row['material_paths'].split(';')
                material_paths = [p.strip() for p in material_paths]

                candidates.append({
                    'candidate_id': row['candidate_id'],
                    'candidate_name': row.get('name'),
                    'material_paths': material_paths
                })

            st.write(f"Found {len(candidates)} candidates")

            # Progress tracking
            progress_bar = st.progress(0)
            status_text = st.empty()

            evaluator = st.session_state.evaluator
            results = []

            for i, candidate in enumerate(candidates):
                status_text.text(f"Evaluating {i+1}/{len(candidates)}: {candidate['candidate_id']}")
                progress_bar.progress((i + 1) / len(candidates))

                try:
                    result = evaluator.evaluate_candidate(
                        candidate_id=candidate['candidate_id'],
                        material_paths=candidate['material_paths'],
                        candidate_name=candidate.get('candidate_name')
                    )
                    results.append(result)
                except Exception as e:
                    st.warning(f"Failed to evaluate {candidate['candidate_id']}: {e}")

            status_text.text("Evaluation complete!")

            if results:
                st.success(f"✅ Successfully evaluated {len(results)}/{len(candidates)} candidates")

                # Display summary
                st.markdown("### Results Summary")

                summary_data = []
                for result in sorted(results, key=lambda r: r.overall_score, reverse=True):
                    summary_data.append({
                        'Candidate ID': result.candidate.candidate_id,
                        'Name': result.candidate.name or '-',
                        'Overall Score': f"{result.overall_score:.2f}",
                        'Recommendation': result.recommendation
                    })

                st.dataframe(pd.DataFrame(summary_data), use_container_width=True, hide_index=True)

                # Store results
                st.session_state.evaluation_results.extend(results)

                # Export
                output_dir = Path("./results")
                output_dir.mkdir(exist_ok=True)

                csv_path = output_dir / "batch_results.csv"
                CSVExporter.export_batch(results, csv_path)

                with open(csv_path, 'rb') as f:
                    st.download_button(
                        "Download Batch Results (CSV)",
                        data=f,
                        file_name="batch_results.csv",
                        mime="text/csv"
                    )

                if generate_comparison and len(results) > 1:
                    with st.spinner("Generating comparison report..."):
                        comparison = evaluator.compare_candidates(results)

                        md_path = output_dir / "comparison.md"
                        MarkdownExporter.export_comparison(comparison, md_path)

                        with open(md_path, 'rb') as f:
                            st.download_button(
                                "Download Comparison Report (Markdown)",
                                data=f,
                                file_name="comparison.md",
                                mime="text/markdown"
                            )

            else:
                st.error("No candidates were successfully evaluated")

        except Exception as e:
            st.error(f"Error during batch evaluation: {e}")
            st.exception(e)


def view_results_page():
    """View previous results page"""
    st.title("View Evaluation Results")

    if not st.session_state.evaluation_results:
        st.info("No evaluation results yet. Evaluate some candidates first!")
        return

    st.markdown(f"**Total Evaluations:** {len(st.session_state.evaluation_results)}")

    # Select candidate
    candidate_options = {
        f"{r.candidate.candidate_id} - {r.candidate.name or 'Unnamed'} ({r.overall_score:.2f})": r
        for r in st.session_state.evaluation_results
    }

    selected = st.selectbox("Select candidate to view", list(candidate_options.keys()))

    if selected:
        result = candidate_options[selected]

        # Display summary
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Overall Score", f"{result.overall_score:.2f}/10")
        with col2:
            st.metric("Materials", len(result.candidate.materials))
        with col3:
            st.metric("Evaluation Date", result.candidate.evaluation_date.strftime("%Y-%m-%d"))

        st.markdown(f"**Recommendation:** {result.recommendation}")

        # Scores chart
        st.markdown("### Scores by Criterion")

        chart_data = pd.DataFrame([
            {'Criterion': score.criterion.value.replace('_', ' ').title(), 'Score': score.score}
            for score in result.scores
        ])

        st.bar_chart(chart_data.set_index('Criterion'))

        # Detailed view
        with st.expander("View Full Report"):
            st.markdown(result.overall_assessment)

            for score in result.scores:
                st.markdown(f"#### {score.criterion.display_name}")
                st.markdown(f"**Score:** {score.score}/10")
                st.markdown(score.reasoning)

                if score.evidence:
                    for ev in score.evidence:
                        st.markdown(f"> *{ev.source}:* {ev.quote}")


def settings_page():
    """Settings page"""
    st.title("Settings")

    config = st.session_state.config

    st.markdown("### API Configuration")
    st.text_input("Model", value=config.api.model, disabled=True)
    st.slider("Temperature", 0.0, 1.0, float(config.api.temperature), disabled=True)
    st.number_input("Max Tokens", value=config.api.max_tokens, disabled=True)

    st.info("To modify settings, edit the config.yaml file and restart the application.")

    st.markdown("### Criteria Weights")

    weights = config.criteria.weights
    for criterion in ['critical_thinking', 'coachability', 'curiosity', 'creativity',
                      'collaboration', 'follow_through', 'problem_solving_motivation',
                      'evidence_based', 'detail_orientation', 'communication',
                      'expertise_enabler']:
        weight = getattr(weights, criterion, 10)
        st.slider(
            criterion.replace('_', ' ').title(),
            1, 10, weight,
            disabled=True,
            help=f"Current weight: {weight}"
        )


if __name__ == "__main__":
    main()
