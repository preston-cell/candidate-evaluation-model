"""Modern Streamlit web interface for candidate evaluator with background processing."""

import streamlit as st
import tempfile
import os
import json
import time
from pathlib import Path
from datetime import datetime
import pandas as pd

from candidate_evaluator.core.evaluator import CandidateEvaluator
from candidate_evaluator.core.models import (
    EvaluationResult,
    CandidateProfile,
    CriterionScore,
    EvaluationCriterion,
    Evidence,
    HolisticEvaluationResult
)
from candidate_evaluator.utils.config import load_config, get_default_config
from candidate_evaluator.exporters import (
    JSONExporter,
    MarkdownExporter,
    HTMLExporter,
    CSVExporter
)
from candidate_evaluator.job_manager import JobManager
from candidate_evaluator.background_worker import JobStatus

# No custom CSS - using Streamlit defaults for reliability
CUSTOM_CSS = ""


def load_result_from_json(json_path: Path) -> EvaluationResult:
    """Load an EvaluationResult from a JSON file."""
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    candidate = CandidateProfile(
        candidate_id=data['candidate']['candidate_id'],
        name=data['candidate'].get('name'),
        materials=data['candidate'].get('materials', []),
        evaluation_date=datetime.fromisoformat(data['candidate']['evaluation_date'])
    )

    scores = []
    for score_data in data.get('scores', []):
        evidence_list = [
            Evidence(
                quote=ev['quote'],
                source=ev['source'],
                context=ev['context']
            )
            for ev in score_data.get('evidence', [])
        ]

        scores.append(CriterionScore(
            criterion=EvaluationCriterion(score_data['criterion']),
            score=score_data['score'],
            reasoning=score_data['reasoning'],
            evidence=evidence_list,
            confidence=score_data.get('confidence', 'medium'),
            notes=score_data.get('notes')
        ))

    return EvaluationResult(
        candidate=candidate,
        scores=scores,
        overall_score=data['overall_score'],
        overall_assessment=data['overall_assessment'],
        strengths=data.get('strengths', []),
        areas_for_development=data.get('areas_for_development', []),
        recommendation=data['recommendation'],
        metadata=data.get('metadata', {})
    )


def load_holistic_result_from_json(json_path: Path) -> HolisticEvaluationResult:
    """Load a HolisticEvaluationResult from a JSON file."""
    from candidate_evaluator.core.models import (
        InnovationPotential, ProgramFit, NotableQuality
    )

    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    candidate = CandidateProfile(
        candidate_id=data['candidate']['candidate_id'],
        name=data['candidate'].get('name'),
        materials=data['candidate'].get('materials', []),
        evaluation_date=datetime.fromisoformat(data['candidate']['evaluation_date'])
    )

    innovation_data = data.get('innovation_potential', {})
    innovation_potential = InnovationPotential(
        level=innovation_data.get('level', 'medium'),
        reasoning=innovation_data.get('reasoning', ''),
        key_evidence=innovation_data.get('key_evidence', [])
    )

    fit_data = data.get('program_fit', {})
    program_fit = ProgramFit(
        level=fit_data.get('level', 'moderate'),
        strengths_for_program=fit_data.get('strengths_for_program', []),
        concerns=fit_data.get('concerns', [])
    )

    notable_qualities = []
    for q in data.get('notable_qualities', []):
        if isinstance(q, dict):
            notable_qualities.append(NotableQuality(
                quality=q.get('quality', ''),
                evidence=q.get('evidence', ''),
                significance=q.get('significance', '')
            ))

    return HolisticEvaluationResult(
        candidate=candidate,
        overall_assessment=data.get('overall_assessment', ''),
        innovation_potential=innovation_potential,
        program_fit=program_fit,
        notable_qualities=notable_qualities,
        red_flags=data.get('red_flags', []),
        questions_for_interview=data.get('questions_for_interview', []),
        overall_score=float(data.get('overall_score', 5.0)),
        recommendation=data.get('recommendation', ''),
        interview_decision=data.get('interview_decision', False),
        metadata=data.get('metadata', {})
    )


def load_all_results_from_disk(results_dir: Path) -> list:
    """Load all evaluation results from JSON files in the results directory."""
    results = []
    if not results_dir.exists():
        return results

    for json_file in results_dir.glob("*_evaluation.json"):
        # Skip holistic evaluations
        if "_holistic_evaluation.json" in str(json_file):
            continue
        try:
            result = load_result_from_json(json_file)
            results.append(result)
        except Exception:
            pass

    return results


def load_all_holistic_results_from_disk(results_dir: Path) -> list:
    """Load all holistic evaluation results from JSON files in the results directory."""
    results = []
    if not results_dir.exists():
        return results

    for json_file in results_dir.glob("*_holistic_evaluation.json"):
        try:
            result = load_holistic_result_from_json(json_file)
            results.append(result)
        except Exception:
            pass

    return results


# Page config
st.set_page_config(
    page_title="Candidate Evaluator",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom CSS
# Using Streamlit default theme


def init_session_state():
    """Initialize session state variables"""
    if 'evaluator' not in st.session_state:
        st.session_state.evaluator = None
    if 'config' not in st.session_state:
        st.session_state.config = None
    if 'evaluation_results' not in st.session_state:
        st.session_state.evaluation_results = []
    if 'job_manager' not in st.session_state:
        st.session_state.job_manager = JobManager()


def load_configuration():
    """Load configuration"""
    if st.session_state.config is None:
        try:
            config = load_config()
        except Exception:
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
        st.markdown("## Candidate Evaluator")
        st.markdown("---")

        page_options = ["Dashboard", "New Evaluation", "Batch Jobs", "Results", "Analysis", "Research", "Settings"]

        page = st.radio(
            "Navigation",
            page_options,
            label_visibility="collapsed"
        )

        st.markdown("---")

        # Quick stats
        job_manager = st.session_state.job_manager
        active_jobs = len(job_manager.get_active_jobs())

        if active_jobs > 0:
            st.markdown(f"**Active Jobs:** {active_jobs}")
            st.caption("Go to Batch Jobs to view")

        st.markdown("---")
        st.caption("AI-powered candidate evaluation. Evaluate candidates against 11 research-backed criteria.")

    # Load config
    config = load_configuration()
    if config is None:
        st.stop()

    # Route pages
    if page == "Dashboard":
        dashboard_page()
    elif page == "New Evaluation":
        new_evaluation_page()
    elif page == "Batch Jobs":
        batch_jobs_page()
    elif page == "Results":
        results_page()
    elif page == "Analysis":
        analysis_page()
    elif page == "Research":
        research_page()
    elif page == "Settings":
        settings_page()


def dashboard_page():
    """Dashboard overview page."""
    st.title("Dashboard")

    output_dir = Path("./results")
    all_results = load_all_results_from_disk(output_dir)
    job_manager = st.session_state.job_manager

    # Stats row
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Evaluations", len(all_results))

    with col2:
        active_jobs = len(job_manager.get_active_jobs())
        st.metric("Active Jobs", active_jobs)

    with col3:
        if all_results:
            avg_score = sum(r.overall_score for r in all_results) / len(all_results)
            st.metric("Avg Score", f"{avg_score:.1f}/10")
        else:
            st.metric("Avg Score", "N/A")

    with col4:
        recent_jobs = job_manager.list_jobs(limit=10)
        completed = len([j for j in recent_jobs if j.get("status") == JobStatus.COMPLETED])
        st.metric("Recent Completed", completed)

    st.markdown("---")

    # Two column layout
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("Recent Evaluations")

        if all_results:
            recent = sorted(all_results, key=lambda r: r.candidate.evaluation_date, reverse=True)[:5]

            for result in recent:
                with st.container():
                    rcol1, rcol2, rcol3 = st.columns([3, 1, 1])
                    with rcol1:
                        st.markdown(f"**{result.candidate.candidate_id}**")
                        st.caption(result.candidate.evaluation_date.strftime("%Y-%m-%d %H:%M"))
                    with rcol2:
                        st.markdown(f"**{result.overall_score:.1f}**/10")
                    with rcol3:
                        st.caption(result.recommendation)
                    st.markdown("---")
        else:
            st.info("No evaluations yet. Select 'New Evaluation' from the sidebar to get started.")

    with col2:
        st.subheader("Active Jobs")

        active_jobs = job_manager.get_active_jobs()

        if active_jobs:
            for job in active_jobs[:3]:
                progress = job.get("progress", {})
                completed = progress.get("completed", 0)
                total = progress.get("total", 1)
                pct = (completed / total * 100) if total > 0 else 0

                st.markdown(f"**{job.get('job_name', job['job_id'][:20])}**")
                st.progress(pct / 100)
                st.caption(f"{completed}/{total} candidates")
                st.markdown("---")
        else:
            st.info("No active jobs")

        st.subheader("Quick Actions")
        st.caption("Use sidebar to navigate to New Evaluation")


def new_evaluation_page():
    """New evaluation page - single or batch."""
    st.title("New Evaluation")

    tab1, tab2 = st.tabs(["Single Candidate", "Batch Upload"])

    with tab1:
        single_evaluation_form()

    with tab2:
        batch_evaluation_form()


def single_evaluation_form():
    """Single candidate evaluation form."""
    st.markdown("### Evaluate a Single Candidate")

    # Evaluation mode toggle
    st.markdown("#### Evaluation Mode")
    eval_mode = st.radio(
        "Select evaluation approach",
        ["Criteria-Based (11 criteria)", "Holistic (program fit)"],
        horizontal=True,
        help="Criteria-Based uses 11 predefined criteria. Holistic evaluates overall program fit without specific criteria."
    )
    is_holistic = eval_mode == "Holistic (program fit)"

    if is_holistic:
        st.info("Holistic mode evaluates candidates based on overall program fit, innovation potential, and notable qualities without using predefined criteria.")

    col1, col2 = st.columns([2, 1])

    with col1:
        candidate_id = st.text_input(
            "Candidate ID",
            placeholder="e.g., CAND001",
            help="Unique identifier for the candidate"
        )

        candidate_name = st.text_input(
            "Name (optional)",
            placeholder="e.g., John Doe"
        )

        uploaded_files = st.file_uploader(
            "Upload Application Materials",
            type=['pdf', 'docx', 'txt', 'md'],
            accept_multiple_files=True,
            help="Upload resume, cover letter, writing samples, etc."
        )

    with col2:
        st.markdown("#### Supported Formats")
        st.markdown("""
        - PDF documents
        - Word documents (.docx)
        - Plain text (.txt)
        - Markdown (.md)
        """)

        st.markdown("#### Tips")
        st.markdown("""
        - Include all relevant materials
        - PDFs with interview responses work best
        - More context = better evaluation
        """)

    if st.button("Evaluate Candidate", disabled=not (candidate_id and uploaded_files)):
        with st.spinner("Evaluating candidate... This may take a minute."):
            try:
                temp_dir = tempfile.mkdtemp()
                material_paths = []

                for uploaded_file in uploaded_files:
                    temp_path = os.path.join(temp_dir, uploaded_file.name)
                    with open(temp_path, 'wb') as f:
                        f.write(uploaded_file.getbuffer())
                    material_paths.append(temp_path)

                evaluator = st.session_state.evaluator
                output_dir = Path("./results")
                output_dir.mkdir(exist_ok=True)

                if is_holistic:
                    result = evaluator.evaluate_candidate_holistic(
                        candidate_id=candidate_id,
                        material_paths=material_paths,
                        candidate_name=candidate_name or None
                    )
                    # Save holistic result
                    json_path = output_dir / f"{candidate_id}_holistic_evaluation.json"
                    with open(json_path, 'w', encoding='utf-8') as f:
                        json.dump(result.model_dump(), f, indent=2, default=str)
                    st.success("Holistic evaluation completed!")
                    display_holistic_evaluation_result(result)
                else:
                    result = evaluator.evaluate_candidate(
                        candidate_id=candidate_id,
                        material_paths=material_paths,
                        candidate_name=candidate_name or None
                    )
                    # Save criteria-based result
                    json_path = output_dir / f"{candidate_id}_evaluation.json"
                    JSONExporter.export_evaluation(result, json_path)
                    st.session_state.evaluation_results.append(result)
                    st.success("Evaluation completed!")
                    display_evaluation_result(result)

            except Exception as e:
                st.error(f"Error during evaluation: {e}")


def batch_evaluation_form():
    """Batch evaluation form with background processing."""
    st.markdown("### Batch Evaluation")
    st.markdown("Upload multiple PDF files to evaluate in the background. You can navigate away and the evaluation will continue running.")

    # Evaluation mode toggle
    st.markdown("#### Evaluation Mode")
    batch_eval_mode = st.radio(
        "Select evaluation approach",
        ["Criteria-Based (11 criteria)", "Holistic (program fit)"],
        horizontal=True,
        help="Criteria-Based uses 11 predefined criteria. Holistic evaluates overall program fit without specific criteria.",
        key="batch_eval_mode"
    )
    batch_is_holistic = batch_eval_mode == "Holistic (program fit)"

    if batch_is_holistic:
        st.info("Holistic mode will evaluate candidates based on overall program fit and provide binary interview recommendations.")

    uploaded_files = st.file_uploader(
        "Upload Candidate PDFs",
        type=['pdf'],
        accept_multiple_files=True,
        help="Upload multiple PDFs, one per candidate. Filename becomes the candidate ID.",
        key="batch_uploader"
    )

    if uploaded_files:
        st.markdown(f"**{len(uploaded_files)} files selected**")

        with st.expander("View files"):
            for f in uploaded_files:
                st.text(f"- {f.name}")

        col1, col2 = st.columns(2)

        with col1:
            job_name = st.text_input(
                "Job Name (optional)",
                placeholder="e.g., Spring 2026 Applicants",
                help="Give this batch a friendly name"
            )

        with col2:
            output_dir = st.text_input(
                "Output Directory",
                value="./results",
                help="Where to save evaluation results"
            )

        if st.button("Start Batch Evaluation", use_container_width=True):
            # Save files to temp location
            temp_dir = tempfile.mkdtemp()
            candidate_files = {}

            for uploaded_file in uploaded_files:
                temp_path = Path(temp_dir) / uploaded_file.name
                with open(temp_path, 'wb') as f:
                    f.write(uploaded_file.getbuffer())

                candidate_id = temp_path.stem
                candidate_files[candidate_id] = str(temp_path)

            # Get API key from config
            config = st.session_state.config
            job_config = {
                "api_key": config.api.anthropic_api_key,
                "max_tokens": config.api.max_tokens,
                "evaluation_mode": "holistic" if batch_is_holistic else "criteria"
            }

            # Submit job
            job_manager = st.session_state.job_manager
            mode_suffix = " (Holistic)" if batch_is_holistic else ""
            job_id = job_manager.submit_job(
                candidate_files=candidate_files,
                output_dir=output_dir,
                config=job_config,
                job_name=(job_name or f"Batch {datetime.now().strftime('%Y%m%d_%H%M')}") + mode_suffix
            )

            st.success(f"Job submitted! ID: `{job_id}`")
            st.info("You can navigate away - the evaluation will continue in the background.")

            # Redirect to jobs page
            time.sleep(1)
            st.rerun()


def batch_jobs_page():
    """View and manage batch jobs."""
    st.title("Batch Jobs")

    job_manager = st.session_state.job_manager

    # Auto-refresh toggle
    col1, col2 = st.columns([3, 1])
    with col2:
        auto_refresh = st.checkbox("Auto-refresh", value=True)

    if auto_refresh:
        time.sleep(0.1)  # Small delay to prevent too rapid refreshing

    # Tabs for job status
    tab1, tab2, tab3 = st.tabs(["Active", "Completed", "All Jobs"])

    with tab1:
        active_jobs = job_manager.get_active_jobs()

        if active_jobs:
            for job in active_jobs:
                render_job_card(job, job_manager)

            if auto_refresh:
                time.sleep(2)
                st.rerun()
        else:
            st.info("No active jobs. Start a new batch evaluation to see it here.")

    with tab2:
        all_jobs = job_manager.list_jobs(limit=50)
        completed_jobs = [j for j in all_jobs if j.get("status") == JobStatus.COMPLETED]

        if completed_jobs:
            for job in completed_jobs[:20]:
                render_job_card(job, job_manager, show_actions=False)
        else:
            st.info("No completed jobs yet.")

    with tab3:
        all_jobs = job_manager.list_jobs(limit=50)

        if all_jobs:
            # Summary table
            job_data = []
            for job in all_jobs:
                progress = job.get("progress", {})
                job_data.append({
                    "Job ID": job["job_id"][:20] + "...",
                    "Name": job.get("job_name", "-")[:30],
                    "Status": job.get("status", "unknown"),
                    "Progress": f"{progress.get('completed', 0)}/{progress.get('total', 0)}",
                    "Created": job.get("created_at", "")[:19]
                })

            st.dataframe(pd.DataFrame(job_data), hide_index=True, use_container_width=True)

            # Cleanup old jobs
            st.markdown("---")
            if st.button("Cleanup Old Jobs (> 7 days)"):
                job_manager.cleanup_old_jobs(days=7)
                st.success("Old jobs cleaned up!")
                st.rerun()
        else:
            st.info("No jobs yet.")


def render_job_card(job, job_manager, show_actions=True):
    """Render a job card with progress and actions."""
    job_id = job["job_id"]
    status = job.get("status", "unknown")
    progress = job.get("progress", {})
    completed = progress.get("completed", 0)
    failed = progress.get("failed", 0)
    total = progress.get("total", 1)
    current = progress.get("current_candidate")

    pct = (completed / total * 100) if total > 0 else 0

    with st.container():
        col1, col2, col3 = st.columns([3, 1, 1])

        with col1:
            st.markdown(f"**{job.get('job_name', job_id[:25])}**")
            st.caption(f"ID: {job_id[:30]}...")

        with col2:
            st.markdown(f"**{status.upper()}**")

        with col3:
            st.markdown(f"**{completed}/{total}**")
            if failed > 0:
                st.caption(f"{failed} failed")

        # Progress bar
        if status in [JobStatus.RUNNING, JobStatus.PENDING]:
            st.progress(pct / 100)
            if current:
                st.caption(f"Currently evaluating: {current}")

        # Actions
        if show_actions and status in [JobStatus.RUNNING, JobStatus.PENDING]:
            if st.button("Cancel", key=f"cancel_{job_id}"):
                job_manager.cancel_job(job_id)
                st.rerun()

        # Results for completed jobs
        if status == JobStatus.COMPLETED:
            with st.expander("View Results Summary"):
                # Try to get results from job data first
                results = job.get("results", [])
                result_data = []

                if results:
                    for r in results:
                        if r.get("status") == "success":
                            result_data.append({
                                "Candidate": r.get("candidate_id", ""),
                                "Score": f"{r.get('overall_score', 0):.1f}/10",
                                "Recommendation": r.get("recommendation", "") or ""
                            })

                # If no results in job data, try loading from disk
                if not result_data:
                    output_dir = Path(job.get("output_dir", "./results"))
                    if output_dir.exists():
                        disk_results = load_all_results_from_disk(output_dir)
                        # Filter to candidates in this job
                        job_candidates = set(job.get("candidate_files", {}).keys())
                        for r in disk_results:
                            if not job_candidates or r.candidate.candidate_id in job_candidates:
                                result_data.append({
                                    "Candidate": r.candidate.candidate_id,
                                    "Score": f"{r.overall_score:.1f}/10",
                                    "Recommendation": r.recommendation or ""
                                })

                if result_data:
                    st.dataframe(pd.DataFrame(result_data), hide_index=True)
                else:
                    st.write("No results available for this job.")

        # Errors for failed jobs
        if status == JobStatus.FAILED or failed > 0:
            errors = job.get("errors", [])
            if errors:
                with st.expander(f"View Errors ({len(errors)}) - Click to retry"):
                    for err in errors:
                        st.error(f"**{err.get('candidate_id')}**: {err.get('error')}")

                    st.markdown("---")

                    # Retry failed candidates
                    failed_ids = [err.get('candidate_id') for err in errors if err.get('candidate_id')]
                    if failed_ids and st.button(f"Retry {len(failed_ids)} Failed Candidates", key=f"retry_{job_id}"):
                        # Get original candidate files from job
                        candidate_files = job.get("candidate_files", {})
                        retry_files = {cid: path for cid, path in candidate_files.items() if cid in failed_ids}

                        if retry_files:
                            # Submit new job for failed candidates
                            config = st.session_state.config
                            job_config = {
                                "api_key": config.api.anthropic_api_key,
                                "max_tokens": config.api.max_tokens
                            }

                            new_job_id = job_manager.submit_job(
                                candidate_files=retry_files,
                                output_dir=job.get("output_dir", "./results"),
                                config=job_config,
                                job_name=f"Retry: {job.get('job_name', 'Failed candidates')}"
                            )
                            st.success(f"Retry job submitted: {new_job_id}")
                            st.rerun()
                        else:
                            st.warning("Could not find original files for failed candidates")

        st.markdown("---")


def results_page():
    """View all evaluation results."""
    st.title("Evaluation Results")

    output_dir = Path("./results")

    # Load BOTH types of results
    criteria_results = load_all_results_from_disk(output_dir)
    holistic_results = load_all_holistic_results_from_disk(output_dir)

    total = len(criteria_results) + len(holistic_results)

    if total == 0:
        st.info("No evaluation results yet. Run some evaluations first!")
        return

    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Criteria-Based", len(criteria_results))
    with col2:
        st.metric("Holistic", len(holistic_results))
    with col3:
        st.metric("Total", total)
    with col4:
        if st.button("Refresh", use_container_width=True):
            st.rerun()

    st.markdown("---")

    # Tab view for different evaluation types
    tab1, tab2 = st.tabs([
        f"Criteria-Based ({len(criteria_results)})",
        f"Holistic ({len(holistic_results)})"
    ])

    with tab1:
        if not criteria_results:
            st.info("No criteria-based evaluations yet.")
        else:
            # Export buttons for criteria-based
            exp_col1, exp_col2 = st.columns(2)
            with exp_col1:
                if st.button("Export Criteria (CSV)", use_container_width=True, key="export_csv"):
                    csv_path = output_dir / "criteria_results.csv"
                    CSVExporter.export_batch(criteria_results, csv_path)
                    with open(csv_path, 'rb') as f:
                        st.download_button(
                            "Download CSV",
                            data=f,
                            file_name=f"criteria_evaluations_{datetime.now().strftime('%Y%m%d')}.csv",
                            mime="text/csv",
                            key="dl_csv"
                        )
            with exp_col2:
                if st.button("Export Criteria (JSON)", use_container_width=True, key="export_json"):
                    json_path = output_dir / "criteria_results.json"
                    JSONExporter.export_batch(criteria_results, json_path)
                    with open(json_path, 'rb') as f:
                        st.download_button(
                            "Download JSON",
                            data=f,
                            file_name=f"criteria_evaluations_{datetime.now().strftime('%Y%m%d')}.json",
                            mime="application/json",
                            key="dl_json"
                        )

            # Results table
            st.subheader("Criteria-Based Results")
            summary_data = []
            for rank, result in enumerate(sorted(criteria_results, key=lambda r: r.overall_score, reverse=True), 1):
                summary_data.append({
                    'Rank': rank,
                    'Candidate ID': result.candidate.candidate_id,
                    'Name': result.candidate.name or '-',
                    'Score': f"{result.overall_score:.1f}/10",
                    'Date': result.candidate.evaluation_date.strftime("%Y-%m-%d"),
                    'Recommendation': result.recommendation
                })
            st.dataframe(pd.DataFrame(summary_data), hide_index=True, use_container_width=True)

            # Individual candidate view
            st.subheader("Candidate Details")
            candidate_options = {
                f"{r.candidate.candidate_id} ({r.overall_score:.1f})": r
                for r in sorted(criteria_results, key=lambda r: r.overall_score, reverse=True)
            }
            selected = st.selectbox("Select candidate", list(candidate_options.keys()), key="criteria_select")
            if selected:
                result = candidate_options[selected]
                display_evaluation_result(result)

    with tab2:
        if not holistic_results:
            st.info("No holistic evaluations yet. Run evaluations in Holistic mode to see results here.")
        else:
            # Results table for holistic
            st.subheader("Holistic Results")
            holistic_summary = []
            for rank, result in enumerate(sorted(holistic_results, key=lambda r: r.overall_score, reverse=True), 1):
                holistic_summary.append({
                    'Rank': rank,
                    'Candidate ID': result.candidate.candidate_id,
                    'Name': result.candidate.name or '-',
                    'Score': f"{result.overall_score:.1f}/10",
                    'Interview': 'Yes' if result.interview_decision else 'No',
                    'Innovation': result.innovation_potential.level.capitalize(),
                    'Program Fit': result.program_fit.level.capitalize(),
                    'Date': result.candidate.evaluation_date.strftime("%Y-%m-%d")
                })
            st.dataframe(pd.DataFrame(holistic_summary), hide_index=True, use_container_width=True)

            # Individual holistic candidate view
            st.subheader("Candidate Details")
            holistic_options = {
                f"{r.candidate.candidate_id} ({r.overall_score:.1f})": r
                for r in sorted(holistic_results, key=lambda r: r.overall_score, reverse=True)
            }
            selected_holistic = st.selectbox("Select candidate", list(holistic_options.keys()), key="holistic_select")
            if selected_holistic:
                result = holistic_options[selected_holistic]
                display_holistic_evaluation_result(result)


def display_evaluation_result(result):
    """Display a single evaluation result."""
    # Warn if evaluation is incomplete
    if len(result.scores) < 11:
        st.warning(f"Incomplete evaluation: only {len(result.scores)}/11 criteria scored. "
                   f"This is likely due to output truncation (max_tokens too low). "
                   f"Re-run this candidate for a complete evaluation.")

    # Score summary
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Overall Score", f"{result.overall_score:.1f}/10")
    with col2:
        st.metric("Criteria", f"{len(result.scores)}/11")
    with col3:
        high_conf = sum(1 for s in result.scores if s.confidence == 'high')
        st.metric("High Confidence", f"{high_conf}/{len(result.scores)}")
    with col4:
        st.metric("Date", result.candidate.evaluation_date.strftime("%Y-%m-%d"))

    st.markdown(f"**Recommendation:** {result.recommendation}")

    # Strengths and areas
    col1, col2 = st.columns(2)

    with col1:
        if result.strengths:
            st.markdown("#### Strengths")
            for s in result.strengths:
                st.markdown(f"- {s}")

    with col2:
        if result.areas_for_development:
            st.markdown("#### Areas for Development")
            for a in result.areas_for_development:
                st.markdown(f"- {a}")

    # Score breakdown
    st.markdown("#### Scores by Criterion")

    score_data = pd.DataFrame([
        {
            'Criterion': score.criterion.display_name,
            'Score': score.score,
            'Confidence': score.confidence.capitalize()
        }
        for score in sorted(result.scores, key=lambda s: s.score, reverse=True)
    ])

    st.dataframe(score_data, hide_index=True, use_container_width=True)

    # Bar chart
    chart_data = pd.DataFrame([
        {'Criterion': s.criterion.value.replace('_', ' ').title(), 'Score': s.score}
        for s in result.scores
    ])
    st.bar_chart(chart_data.set_index('Criterion'))

    # Detailed evidence
    with st.expander("View Detailed Evidence"):
        for score in result.scores:
            st.markdown(f"**{score.criterion.display_name}** - {score.score}/10 ({score.confidence})")
            st.markdown(score.reasoning)

            if score.evidence:
                for ev in score.evidence:
                    st.markdown(f"> *{ev.source}:* {ev.quote}")

            st.markdown("---")


def display_holistic_evaluation_result(result: HolisticEvaluationResult):
    """Display a holistic evaluation result (supports both old and enhanced formats)."""
    # Score summary with interview decision and confidence
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Overall Score", f"{result.overall_score:.1f}/10")
    with col2:
        interview_text = "Yes" if result.interview_decision else "No"
        st.metric("Interview Recommendation", interview_text)
    with col3:
        innovation_conf = getattr(result.innovation_potential, 'confidence', 'medium')
        st.metric("Innovation Potential", f"{result.innovation_potential.level.capitalize()} ({innovation_conf})")
    with col4:
        fit_conf = getattr(result.program_fit, 'confidence', 'medium')
        st.metric("Program Fit", f"{result.program_fit.level.capitalize()} ({fit_conf})")

    st.markdown(f"**Recommendation:** {result.recommendation}")

    # Score justification if present (enhanced format)
    if hasattr(result, 'score_justification') and result.score_justification:
        with st.expander("Score Justification"):
            st.markdown(result.score_justification)

    # Interview decision reasoning if present (enhanced format)
    if hasattr(result, 'interview_decision_reasoning') and result.interview_decision_reasoning:
        with st.expander("Interview Decision Reasoning"):
            st.markdown(result.interview_decision_reasoning)

    # Overall Assessment
    st.markdown("#### Overall Assessment")
    st.markdown(result.overall_assessment)

    # Innovation and Program Fit details
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Innovation Potential")
        st.markdown(f"**Level:** {result.innovation_potential.level.capitalize()} (Confidence: {getattr(result.innovation_potential, 'confidence', 'medium')})")
        st.markdown(result.innovation_potential.reasoning)

        # Display structured evidence if present (enhanced format)
        if hasattr(result.innovation_potential, 'evidence') and result.innovation_potential.evidence:
            st.markdown("**Evidence:**")
            for ev in result.innovation_potential.evidence:
                if hasattr(ev, 'quote'):
                    source_text = f" *({ev.source})*" if ev.source else ""
                    st.markdown(f"> \"{ev.quote}\"{source_text}")
                    if ev.context:
                        st.caption(f"Context: {ev.context}")
        # Fallback to legacy key_evidence
        elif result.innovation_potential.key_evidence:
            st.markdown("**Key Evidence:**")
            for ev in result.innovation_potential.key_evidence:
                st.markdown(f"> {ev}")

    with col2:
        st.markdown("#### Program Fit")
        st.markdown(f"**Level:** {result.program_fit.level.capitalize()} (Confidence: {getattr(result.program_fit, 'confidence', 'medium')})")

        # Detailed analysis if present (enhanced format)
        if hasattr(result.program_fit, 'detailed_analysis') and result.program_fit.detailed_analysis:
            st.markdown(result.program_fit.detailed_analysis)

        if result.program_fit.strengths_for_program:
            st.markdown("**Strengths:**")
            for s in result.program_fit.strengths_for_program:
                st.markdown(f"- {s}")
        if result.program_fit.concerns:
            st.markdown("**Concerns:**")
            for c in result.program_fit.concerns:
                st.markdown(f"- {c}")

        # Display structured evidence if present (enhanced format)
        if hasattr(result.program_fit, 'evidence') and result.program_fit.evidence:
            with st.expander("Supporting Evidence"):
                for ev in result.program_fit.evidence:
                    if hasattr(ev, 'quote'):
                        source_text = f" *({ev.source})*" if ev.source else ""
                        st.markdown(f"> \"{ev.quote}\"{source_text}")
                        if ev.context:
                            st.caption(f"Context: {ev.context}")

    # Notable Qualities
    if result.notable_qualities:
        st.markdown("#### Notable Qualities")
        for q in result.notable_qualities:
            confidence = getattr(q, 'confidence', 'medium')
            with st.expander(f"{q.quality} (Confidence: {confidence})"):
                # Handle both string evidence and list of structured evidence
                if isinstance(q.evidence, list):
                    st.markdown("**Evidence:**")
                    for ev in q.evidence:
                        if hasattr(ev, 'quote'):
                            source_text = f" *({ev.source})*" if ev.source else ""
                            st.markdown(f"> \"{ev.quote}\"{source_text}")
                            if ev.context:
                                st.caption(ev.context)
                        else:
                            st.markdown(f"> {ev}")
                else:
                    st.markdown(f"**Evidence:** {q.evidence}")
                st.markdown(f"**Significance:** {q.significance}")

    # Red Flags (supports both string and structured formats)
    if result.red_flags:
        st.markdown("#### Red Flags")
        for flag in result.red_flags:
            if hasattr(flag, 'flag'):
                # Enhanced format with severity
                severity_colors = {'high': 'error', 'medium': 'warning', 'low': 'info'}
                severity = getattr(flag, 'severity', 'medium')
                if severity == 'high':
                    st.error(f"**{flag.flag}**")
                elif severity == 'low':
                    st.info(f"{flag.flag}")
                else:
                    st.warning(f"{flag.flag}")
                if flag.evidence:
                    st.caption(f"Evidence: {flag.evidence}")
            else:
                # Legacy string format
                st.warning(flag)

    # Interview Questions (supports both string and structured formats)
    if result.questions_for_interview:
        st.markdown("#### Suggested Interview Questions")
        for i, q in enumerate(result.questions_for_interview, 1):
            if hasattr(q, 'question'):
                # Enhanced format with category and purpose
                category = getattr(q, 'category', 'General')
                st.markdown(f"**{i}. [{category}]** {q.question}")
                if q.purpose:
                    st.caption(f"Purpose: {q.purpose}")
            else:
                # Legacy string format
                st.markdown(f"{i}. {q}")


def analysis_page():
    """Analysis dashboard."""
    st.title("Analysis Dashboard")

    output_dir = Path("./results")
    all_results = load_all_results_from_disk(output_dir)

    # Also load holistic results
    holistic_results = load_all_holistic_results_from_disk(output_dir)

    total_results = len(all_results) + len(holistic_results)

    if total_results == 0:
        st.warning("No evaluation results found. Run some evaluations first!")
        return

    st.markdown(f"**Analyzing {len(all_results)} criteria-based + {len(holistic_results)} holistic evaluations**")

    tab1, tab2, tab3, tab4 = st.tabs(["Distribution Analysis", "AI vs Expert", "Decision Comparison", "Recommendations"])

    with tab1:
        if all_results:
            distribution_analysis(all_results)
        else:
            st.info("No criteria-based evaluations to analyze. Run criteria-based evaluations first.")

    with tab2:
        if all_results:
            expert_comparison_analysis(all_results, output_dir)
        else:
            st.info("Expert comparison requires criteria-based evaluations.")

    with tab3:
        decision_comparison_analysis(all_results, holistic_results, output_dir)

    with tab4:
        if all_results:
            recommendation_analysis(all_results)
        else:
            st.info("Recommendations analysis requires criteria-based evaluations.")


def distribution_analysis(all_results):
    """Score distribution analysis."""
    st.subheader("Score Distribution Analysis")

    from candidate_evaluator.core.distribution_analyzer import DistributionAnalyzer

    analyzer = DistributionAnalyzer(all_results)

    # Overall stats
    col1, col2, col3, col4 = st.columns(4)

    overall_scores = [r.overall_score for r in all_results]

    with col1:
        st.metric("Mean Score", f"{sum(overall_scores)/len(overall_scores):.2f}")
    with col2:
        st.metric("Median Score", f"{sorted(overall_scores)[len(overall_scores)//2]:.2f}")
    with col3:
        st.metric("Min Score", f"{min(overall_scores):.2f}")
    with col4:
        st.metric("Max Score", f"{max(overall_scores):.2f}")

    st.markdown("---")

    # Percentile analysis
    percentile = st.slider("Percentile Split", 25, 75, 50)

    if st.button("Analyze"):
        top_group, bottom_group = analyzer.segment_by_percentile(percentile)
        comparison = analyzer.compare_groups(top_group, bottom_group)

        col1, col2 = st.columns(2)

        with col1:
            st.markdown(f"### Top {100-percentile}% ({len(top_group)} candidates)")
            if top_group:
                top_analysis = analyzer.analyze_group(top_group)
                st.metric("Mean Score", f"{top_analysis.mean_overall_score:.2f}")

        with col2:
            st.markdown(f"### Bottom {percentile}% ({len(bottom_group)} candidates)")
            if bottom_group:
                bottom_analysis = analyzer.analyze_group(bottom_group)
                st.metric("Mean Score", f"{bottom_analysis.mean_overall_score:.2f}")

        st.markdown("### Most Discriminating Criteria")
        for i, crit in enumerate(comparison.get('most_discriminating_criteria', []), 1):
            name = crit['criterion'].replace('_', ' ').title()
            st.markdown(f"**{i}. {name}**: {crit['difference']:.1f} point gap")

        st.markdown("### Insights")
        for insight in comparison.get('insights', []):
            st.info(insight)


def expert_comparison_analysis(all_results, output_dir):
    """AI vs Expert comparison."""
    st.subheader("AI vs Expert Comparison")

    st.info("Upload expert ratings to compare with AI evaluations.")

    expert_file = st.file_uploader(
        "Upload Expert Ratings",
        type=['xlsx', 'xls', 'csv'],
        help="Excel or CSV with expert ratings"
    )

    if expert_file:
        try:
            from candidate_evaluator.core.expert_comparison import ExpertComparisonAnalyzer

            temp_dir = tempfile.mkdtemp()
            temp_path = Path(temp_dir) / expert_file.name
            with open(temp_path, 'wb') as f:
                f.write(expert_file.getbuffer())

            analyzer = ExpertComparisonAnalyzer()

            with st.spinner("Loading expert ratings..."):
                expert_ratings = analyzer.load_expert_ratings_from_excel(temp_path)

            st.success(f"Loaded {len(expert_ratings)} expert ratings")

            analyzer.set_ai_results(all_results)

            threshold = st.slider("Interview Threshold", 1.0, 10.0, 6.0)

            if st.button("Run Comparison"):
                metrics = analyzer.compare(interview_threshold=threshold)

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Matched", f"{metrics.matched_candidates}/{metrics.total_candidates}")
                with col2:
                    st.metric("MAE", f"{metrics.overall_mae:.2f}")
                with col3:
                    st.metric("Correlation", f"{metrics.overall_correlation:.2f}")

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Sensitivity", f"{metrics.sensitivity*100:.1f}%" if metrics.sensitivity else "N/A")
                with col2:
                    st.metric("Specificity", f"{metrics.specificity*100:.1f}%" if metrics.specificity else "N/A")
                with col3:
                    st.metric("Cohen's Kappa", f"{metrics.cohens_kappa:.2f}" if metrics.cohens_kappa else "N/A")

                if metrics.ai_bias:
                    st.warning(f"Detected bias: {metrics.ai_bias}")

        except Exception as e:
            st.error(f"Error: {e}")


def decision_comparison_analysis(criteria_results, holistic_results, output_dir):
    """Compare AI predictions against actual interview/admission decisions."""
    st.subheader("Decision Comparison")
    st.markdown("Compare AI evaluation predictions against actual interview and admission decisions.")

    # Instructions
    with st.expander("How to use", expanded=False):
        st.markdown("""
        **Upload a CSV or Excel file with columns:**
        - `candidate_id`: Must match the candidate IDs from evaluations
        - `interviewed`: Yes/No or True/False - whether the candidate was interviewed
        - `admitted` (optional): Yes/No or True/False - whether the candidate was admitted

        **The tool will calculate:**
        - Sensitivity (true positive rate)
        - Specificity (true negative rate)
        - Cohen's Kappa (agreement statistic)
        - Confusion matrix
        """)

    # File upload
    uploaded_file = st.file_uploader(
        "Upload decisions file",
        type=['csv', 'xlsx'],
        help="CSV or Excel with candidate_id, interviewed, admitted columns"
    )

    if uploaded_file is None:
        st.info("Upload a decisions file to compare AI predictions against actual outcomes.")
        return

    # Load decisions
    try:
        if uploaded_file.name.endswith('.xlsx'):
            decisions_df = pd.read_excel(uploaded_file)
        else:
            decisions_df = pd.read_csv(uploaded_file)
    except Exception as e:
        st.error(f"Error reading file: {e}")
        return

    # Normalize column names
    decisions_df.columns = decisions_df.columns.str.lower().str.strip()

    if 'candidate_id' not in decisions_df.columns:
        st.error("File must have a 'candidate_id' column")
        return

    if 'interviewed' not in decisions_df.columns:
        st.error("File must have an 'interviewed' column")
        return

    # Normalize boolean columns
    def normalize_bool(val):
        if pd.isna(val):
            return None
        if isinstance(val, bool):
            return val
        val_str = str(val).lower().strip()
        return val_str in ['yes', 'true', '1', 'y']

    decisions_df['interviewed'] = decisions_df['interviewed'].apply(normalize_bool)
    if 'admitted' in decisions_df.columns:
        decisions_df['admitted'] = decisions_df['admitted'].apply(normalize_bool)

    st.success(f"Loaded {len(decisions_df)} decision records")

    # Select data source for comparison
    st.markdown("### Select Evaluation Data")
    data_source = st.radio(
        "Compare against:",
        ["Criteria-Based Evaluations", "Holistic Evaluations", "Both"],
        horizontal=True
    )

    # Score threshold for criteria-based
    threshold = st.slider(
        "Score threshold for positive AI prediction",
        min_value=1.0, max_value=10.0, value=6.0, step=0.5,
        help="Candidates scoring at or above this threshold are predicted as 'interview'"
    )

    if st.button("Run Comparison"):
        results_to_compare = []

        if data_source in ["Criteria-Based Evaluations", "Both"]:
            for result in criteria_results:
                results_to_compare.append({
                    'candidate_id': result.candidate.candidate_id,
                    'overall_score': result.overall_score,
                    'ai_prediction': result.overall_score >= threshold,
                    'source': 'criteria'
                })

        if data_source in ["Holistic Evaluations", "Both"]:
            for result in holistic_results:
                results_to_compare.append({
                    'candidate_id': result.candidate.candidate_id,
                    'overall_score': result.overall_score,
                    'ai_prediction': result.interview_decision,
                    'source': 'holistic'
                })

        if not results_to_compare:
            st.warning("No evaluation results found for selected data source.")
            return

        ai_df = pd.DataFrame(results_to_compare)

        # Merge with decisions
        merged = ai_df.merge(decisions_df, on='candidate_id', how='inner')

        if len(merged) == 0:
            st.error("No matching candidates found between evaluations and decisions file. Check that candidate IDs match.")
            return

        st.markdown(f"**Matched {len(merged)} candidates**")

        # Calculate metrics for interview decisions
        st.markdown("### Interview Decision Comparison")

        actual_interviewed = merged['interviewed'].values
        ai_predicted = merged['ai_prediction'].values

        # Remove any None values
        valid_mask = [a is not None for a in actual_interviewed]
        actual_interviewed = [actual_interviewed[i] for i in range(len(valid_mask)) if valid_mask[i]]
        ai_predicted = [ai_predicted[i] for i in range(len(valid_mask)) if valid_mask[i]]

        if len(actual_interviewed) == 0:
            st.warning("No valid interview decisions to compare.")
            return

        # Calculate confusion matrix
        tp = sum(1 for a, p in zip(actual_interviewed, ai_predicted) if a and p)
        tn = sum(1 for a, p in zip(actual_interviewed, ai_predicted) if not a and not p)
        fp = sum(1 for a, p in zip(actual_interviewed, ai_predicted) if not a and p)
        fn = sum(1 for a, p in zip(actual_interviewed, ai_predicted) if a and not p)

        # Display confusion matrix
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### Confusion Matrix")
            cm_df = pd.DataFrame(
                [[tp, fn], [fp, tn]],
                columns=['AI: Yes', 'AI: No'],
                index=['Actual: Yes', 'Actual: No']
            )
            st.dataframe(cm_df, use_container_width=True)

        with col2:
            st.markdown("#### Key Metrics")

            # Sensitivity (recall)
            sensitivity = tp / (tp + fn) if (tp + fn) > 0 else 0
            st.metric(
                "Sensitivity (True Positive Rate)",
                f"{sensitivity:.1%}",
                help=f"AI identified {sensitivity:.1%} of candidates who were actually interviewed"
            )

            # Specificity
            specificity = tn / (tn + fp) if (tn + fp) > 0 else 0
            st.metric(
                "Specificity (True Negative Rate)",
                f"{specificity:.1%}",
                help=f"AI correctly rejected {specificity:.1%} of candidates not interviewed"
            )

            # Accuracy
            accuracy = (tp + tn) / len(actual_interviewed) if len(actual_interviewed) > 0 else 0
            st.metric("Overall Accuracy", f"{accuracy:.1%}")

            # Cohen's Kappa
            p_o = (tp + tn) / len(actual_interviewed) if len(actual_interviewed) > 0 else 0
            p_yes = ((tp + fn) / len(actual_interviewed)) * ((tp + fp) / len(actual_interviewed))
            p_no = ((fp + tn) / len(actual_interviewed)) * ((fn + tn) / len(actual_interviewed))
            p_e = p_yes + p_no
            kappa = (p_o - p_e) / (1 - p_e) if (1 - p_e) != 0 else 0

            kappa_interpretation = "Poor" if kappa < 0.2 else "Fair" if kappa < 0.4 else "Moderate" if kappa < 0.6 else "Good" if kappa < 0.8 else "Excellent"
            st.metric(
                "Cohen's Kappa",
                f"{kappa:.3f} ({kappa_interpretation})",
                help="Measures agreement beyond chance"
            )

        # High disagreement candidates
        st.markdown("### Disagreement Analysis")

        disagreements = merged[merged['ai_prediction'] != merged['interviewed']]

        if len(disagreements) > 0:
            st.markdown(f"**{len(disagreements)} candidates where AI and human disagree:**")

            false_positives = disagreements[disagreements['ai_prediction'] & ~disagreements['interviewed']]
            false_negatives = disagreements[~disagreements['ai_prediction'] & disagreements['interviewed']]

            col1, col2 = st.columns(2)

            with col1:
                st.markdown(f"**False Positives ({len(false_positives)})** - AI recommended, not interviewed:")
                for _, row in false_positives.head(10).iterrows():
                    st.text(f"- {row['candidate_id']}: AI score {row['overall_score']:.1f}")

            with col2:
                st.markdown(f"**False Negatives ({len(false_negatives)})** - Not recommended, was interviewed:")
                for _, row in false_negatives.head(10).iterrows():
                    st.text(f"- {row['candidate_id']}: AI score {row['overall_score']:.1f}")
        else:
            st.success("Perfect agreement between AI and human decisions!")

        # Bias detection
        st.markdown("### Bias Analysis")
        ai_positive_rate = sum(ai_predicted) / len(ai_predicted) if len(ai_predicted) > 0 else 0
        human_positive_rate = sum(actual_interviewed) / len(actual_interviewed) if len(actual_interviewed) > 0 else 0

        if ai_positive_rate > human_positive_rate + 0.1:
            st.warning(f"AI may be too lenient: AI recommends {ai_positive_rate:.1%} vs human {human_positive_rate:.1%}")
        elif ai_positive_rate < human_positive_rate - 0.1:
            st.warning(f"AI may be too strict: AI recommends {ai_positive_rate:.1%} vs human {human_positive_rate:.1%}")
        else:
            st.success(f"AI and human positive rates are similar: AI {ai_positive_rate:.1%}, Human {human_positive_rate:.1%}")


def recommendation_analysis(all_results):
    """Recommendation breakdown analysis."""
    st.subheader("Recommendation Analysis")

    # Group by recommendation
    recommendations = {}
    for result in all_results:
        rec = result.recommendation if result.recommendation else "Unknown"
        if rec not in recommendations:
            recommendations[rec] = []
        recommendations[rec].append(result)

    st.markdown(f"**{len(recommendations)} unique recommendation types**")

    for rec_type, candidates in sorted(recommendations.items(), key=lambda x: -len(x[1])):
        with st.expander(f"{rec_type} ({len(candidates)} candidates)"):
            if candidates:
                avg = sum(c.overall_score for c in candidates) / len(candidates)
                st.metric("Average Score", f"{avg:.2f}")

                # Show candidate list
                for c in sorted(candidates, key=lambda x: -x.overall_score)[:5]:
                    st.text(f"- {c.candidate.candidate_id}: {c.overall_score:.1f}/10")


def research_page():
    """Research dashboard for comparing evaluation methods."""
    st.title("Research Dashboard")
    st.markdown("Compare evaluation methods and analyze AI performance for research purposes.")

    output_dir = Path("./results")
    criteria_results = load_all_results_from_disk(output_dir)
    holistic_results = load_all_holistic_results_from_disk(output_dir)

    # Summary stats
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Criteria-Based Evaluations", len(criteria_results))
    with col2:
        st.metric("Holistic Evaluations", len(holistic_results))
    with col3:
        # Find candidates with both types
        criteria_ids = {r.candidate.candidate_id for r in criteria_results}
        holistic_ids = {r.candidate.candidate_id for r in holistic_results}
        both_ids = criteria_ids & holistic_ids
        st.metric("Candidates with Both", len(both_ids))

    if len(criteria_results) == 0 and len(holistic_results) == 0:
        st.warning("No evaluation results found. Run some evaluations first!")
        return

    tab1, tab2, tab3 = st.tabs(["Method Comparison", "Side-by-Side View", "Export Report"])

    with tab1:
        research_method_comparison(criteria_results, holistic_results)

    with tab2:
        research_side_by_side(criteria_results, holistic_results)

    with tab3:
        research_export_report(criteria_results, holistic_results, output_dir)


def research_method_comparison(criteria_results, holistic_results):
    """Compare criteria-based vs holistic evaluation methods."""
    st.subheader("Evaluation Method Comparison")

    # Find candidates evaluated with both methods
    criteria_by_id = {r.candidate.candidate_id: r for r in criteria_results}
    holistic_by_id = {r.candidate.candidate_id: r for r in holistic_results}
    both_ids = set(criteria_by_id.keys()) & set(holistic_by_id.keys())

    if len(both_ids) == 0:
        st.info("No candidates have been evaluated with both methods. Run evaluations with both Criteria-Based and Holistic modes on the same candidates to see comparisons.")

        # Show individual method stats if available
        if criteria_results:
            st.markdown("### Criteria-Based Results")
            scores = [r.overall_score for r in criteria_results]
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Mean Score", f"{sum(scores)/len(scores):.2f}")
            with col2:
                st.metric("Min Score", f"{min(scores):.2f}")
            with col3:
                st.metric("Max Score", f"{max(scores):.2f}")

        if holistic_results:
            st.markdown("### Holistic Results")
            scores = [r.overall_score for r in holistic_results]
            interview_yes = sum(1 for r in holistic_results if r.interview_decision)
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Mean Score", f"{sum(scores)/len(scores):.2f}")
            with col2:
                st.metric("Min Score", f"{min(scores):.2f}")
            with col3:
                st.metric("Max Score", f"{max(scores):.2f}")
            with col4:
                st.metric("Interview Yes", f"{interview_yes}/{len(holistic_results)}")

        return

    st.markdown(f"**{len(both_ids)} candidates evaluated with both methods**")

    # Build comparison data
    comparison_data = []
    for cid in both_ids:
        cr = criteria_by_id[cid]
        hr = holistic_by_id[cid]
        comparison_data.append({
            'candidate_id': cid,
            'criteria_score': cr.overall_score,
            'holistic_score': hr.overall_score,
            'criteria_rec': cr.recommendation,
            'holistic_rec': hr.recommendation,
            'holistic_interview': hr.interview_decision,
            'score_diff': cr.overall_score - hr.overall_score
        })

    df = pd.DataFrame(comparison_data)

    # Agreement metrics
    st.markdown("### Agreement Analysis")

    col1, col2 = st.columns(2)

    with col1:
        # Score correlation
        if len(df) > 1:
            correlation = df['criteria_score'].corr(df['holistic_score'])
            st.metric("Score Correlation", f"{correlation:.3f}")
        else:
            st.metric("Score Correlation", "N/A (need more data)")

        # Mean absolute difference
        mad = df['score_diff'].abs().mean()
        st.metric("Mean Absolute Difference", f"{mad:.2f} points")

    with col2:
        # Scores higher/lower/same
        higher = sum(1 for d in df['score_diff'] if d > 0.5)
        lower = sum(1 for d in df['score_diff'] if d < -0.5)
        similar = len(df) - higher - lower

        st.markdown("**Score Comparison:**")
        st.markdown(f"- Criteria higher: {higher} ({higher/len(df)*100:.1f}%)")
        st.markdown(f"- Holistic higher: {lower} ({lower/len(df)*100:.1f}%)")
        st.markdown(f"- Similar (within 0.5): {similar} ({similar/len(df)*100:.1f}%)")

    # Scatter plot comparison
    st.markdown("### Score Comparison Chart")
    chart_df = df[['criteria_score', 'holistic_score']].copy()
    chart_df.columns = ['Criteria-Based', 'Holistic']
    st.scatter_chart(chart_df)

    # Detailed comparison table
    st.markdown("### Detailed Comparison")
    display_df = df[['candidate_id', 'criteria_score', 'holistic_score', 'score_diff', 'holistic_interview']].copy()
    display_df.columns = ['Candidate', 'Criteria Score', 'Holistic Score', 'Difference', 'Interview Rec']
    display_df = display_df.sort_values('Difference', key=abs, ascending=False)
    st.dataframe(display_df, hide_index=True, use_container_width=True)


def research_side_by_side(criteria_results, holistic_results):
    """Side-by-side view of individual candidate evaluations."""
    st.subheader("Side-by-Side Candidate View")

    # Get all unique candidate IDs
    criteria_by_id = {r.candidate.candidate_id: r for r in criteria_results}
    holistic_by_id = {r.candidate.candidate_id: r for r in holistic_results}
    all_ids = sorted(set(criteria_by_id.keys()) | set(holistic_by_id.keys()))

    if not all_ids:
        st.info("No candidates to display.")
        return

    selected_id = st.selectbox("Select Candidate", all_ids)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Criteria-Based Evaluation")
        if selected_id in criteria_by_id:
            cr = criteria_by_id[selected_id]
            st.metric("Overall Score", f"{cr.overall_score:.1f}/10")
            st.markdown(f"**Recommendation:** {cr.recommendation}")

            if cr.strengths:
                st.markdown("**Strengths:**")
                for s in cr.strengths[:3]:
                    st.markdown(f"- {s}")

            if cr.areas_for_development:
                st.markdown("**Areas for Development:**")
                for a in cr.areas_for_development[:3]:
                    st.markdown(f"- {a}")

            with st.expander("Score Breakdown"):
                for score in sorted(cr.scores, key=lambda x: -x.score):
                    st.markdown(f"- {score.criterion.value.replace('_', ' ').title()}: {score.score}/10")
        else:
            st.info("No criteria-based evaluation for this candidate.")

    with col2:
        st.markdown("### Holistic Evaluation")
        if selected_id in holistic_by_id:
            hr = holistic_by_id[selected_id]
            st.metric("Overall Score", f"{hr.overall_score:.1f}/10")
            interview_text = "Yes" if hr.interview_decision else "No"
            st.metric("Interview Decision", interview_text)
            st.markdown(f"**Recommendation:** {hr.recommendation}")
            st.markdown(f"**Innovation Potential:** {hr.innovation_potential.level.capitalize()}")
            st.markdown(f"**Program Fit:** {hr.program_fit.level.capitalize()}")

            if hr.notable_qualities:
                st.markdown("**Notable Qualities:**")
                for q in hr.notable_qualities[:3]:
                    st.markdown(f"- {q.quality}")

            if hr.red_flags:
                st.markdown("**Red Flags:**")
                for flag in hr.red_flags[:3]:
                    st.warning(flag)

            with st.expander("Full Assessment"):
                st.markdown(hr.overall_assessment)
        else:
            st.info("No holistic evaluation for this candidate.")


def research_export_report(criteria_results, holistic_results, output_dir):
    """Export research comparison report."""
    st.subheader("Export Research Report")

    # Build report data
    criteria_by_id = {r.candidate.candidate_id: r for r in criteria_results}
    holistic_by_id = {r.candidate.candidate_id: r for r in holistic_results}
    both_ids = set(criteria_by_id.keys()) & set(holistic_by_id.keys())

    st.markdown("Generate a markdown report summarizing evaluation comparisons.")

    col1, col2 = st.columns(2)
    with col1:
        include_criteria = st.checkbox("Include criteria-based results", value=True)
    with col2:
        include_holistic = st.checkbox("Include holistic results", value=True)

    if st.button("Generate Report"):
        report_lines = [
            "# Candidate Evaluation Research Report",
            f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "\n## Summary Statistics",
            f"\n- Total criteria-based evaluations: {len(criteria_results)}",
            f"- Total holistic evaluations: {len(holistic_results)}",
            f"- Candidates with both evaluations: {len(both_ids)}",
        ]

        if criteria_results and include_criteria:
            scores = [r.overall_score for r in criteria_results]
            report_lines.extend([
                "\n## Criteria-Based Evaluation Summary",
                f"\n- Mean score: {sum(scores)/len(scores):.2f}",
                f"- Score range: {min(scores):.2f} - {max(scores):.2f}",
            ])

        if holistic_results and include_holistic:
            scores = [r.overall_score for r in holistic_results]
            interview_yes = sum(1 for r in holistic_results if r.interview_decision)
            report_lines.extend([
                "\n## Holistic Evaluation Summary",
                f"\n- Mean score: {sum(scores)/len(scores):.2f}",
                f"- Score range: {min(scores):.2f} - {max(scores):.2f}",
                f"- Interview recommendations: {interview_yes}/{len(holistic_results)} ({interview_yes/len(holistic_results)*100:.1f}%)",
            ])

        if both_ids:
            report_lines.extend([
                "\n## Method Comparison (candidates with both evaluations)",
            ])
            for cid in sorted(both_ids):
                cr = criteria_by_id[cid]
                hr = holistic_by_id[cid]
                diff = cr.overall_score - hr.overall_score
                report_lines.append(f"\n### {cid}")
                report_lines.append(f"- Criteria score: {cr.overall_score:.1f}")
                report_lines.append(f"- Holistic score: {hr.overall_score:.1f}")
                report_lines.append(f"- Difference: {diff:+.1f}")
                report_lines.append(f"- Interview decision (holistic): {'Yes' if hr.interview_decision else 'No'}")

        report_content = "\n".join(report_lines)

        # Save report
        report_path = output_dir / f"research_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)

        st.success(f"Report saved to: {report_path}")

        # Show preview
        st.markdown("### Report Preview")
        st.markdown(report_content)

        # Download button
        st.download_button(
            label="Download Report",
            data=report_content,
            file_name=f"research_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
            mime="text/markdown"
        )


def settings_page():
    """Settings page."""
    st.title("Settings")

    config = st.session_state.config

    st.subheader("API Configuration")

    col1, col2 = st.columns(2)

    with col1:
        st.text_input("Model", value=config.api.model, disabled=True)
        st.number_input("Max Tokens", value=config.api.max_tokens, disabled=True)

    with col2:
        st.slider("Temperature", 0.0, 1.0, float(config.api.temperature), disabled=True)

    st.info("Edit config.yaml to modify settings, then restart the application.")

    st.subheader("Criteria Weights")

    weights = config.criteria.weights
    criteria = ['critical_thinking', 'coachability', 'curiosity', 'creativity',
                'collaboration', 'follow_through', 'problem_solving_motivation',
                'evidence_based', 'detail_orientation', 'communication', 'expertise_enabler']

    weight_data = []
    for c in criteria:
        weight_data.append({
            'Criterion': c.replace('_', ' ').title(),
            'Weight': getattr(weights, c, 10)
        })

    st.dataframe(pd.DataFrame(weight_data), hide_index=True, use_container_width=True)

    st.markdown("---")

    st.subheader("Job Management")

    job_manager = st.session_state.job_manager

    col1, col2 = st.columns(2)

    with col1:
        st.text(f"Jobs directory: {job_manager.jobs_dir}")
        st.text(f"Logs directory: {job_manager.logs_dir}")

    with col2:
        if st.button("Cleanup Old Jobs"):
            job_manager.cleanup_old_jobs(days=7)
            st.success("Cleaned up jobs older than 7 days")


if __name__ == "__main__":
    main()
