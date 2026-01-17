"""
Reusable UI components for Streamlit app
"""

import streamlit as st
from typing import Optional
from deep_research import SynthesizeData
from utils.session_manager import ResearchSession


def render_research_form():
    """Render research topic input form"""
    st.header("🔍 New Research")
    
    topic = st.text_area(
        "Research Topic",
        placeholder="Enter your research topic or question...",
        height=100,
        help="Describe what you want to research. Be specific for better results."
    )
    
    col1, col2 = st.columns([1, 4])
    with col1:
        start_button = st.button("Start Research", type="primary", use_container_width=True)
    with col2:
        quick_research = st.checkbox("Quick Research (fewer queries, faster)", value=False)
    
    return topic, start_button, quick_research


def render_progress_indicator(status: dict):
    """Render research progress indicator"""
    if not status.get("is_running"):
        return
    
    st.progress(status.get("progress", 0.0))
    
    current_step = status.get("current_step")
    status_message = status.get("status_message")
    
    if current_step:
        step_labels = {
            "planning": "📋 Planning",
            "execution": "🔎 Executing Searches",
            "fact_checking": "🔍 Fact-Checking",
            "synthesis": "📝 Synthesizing",
            "completed": "✅ Complete",
            "error": "❌ Error"
        }
        step_label = step_labels.get(current_step, current_step)
        st.info(f"{step_label}: {status_message or ''}")


def render_research_report(session: ResearchSession):
    """Render formatted research report with chat messages"""
    if not session.formatted_report and not session.synthesize_data:
        st.warning("No report available for this research session.")
        return
    
    # Display short summary in a chat message
    if session.synthesize_data and session.synthesize_data.short_summary:
        with st.chat_message("assistant"):
            st.markdown("### Executive Summary")
            st.markdown(session.synthesize_data.short_summary)
    
    # Display full report
    st.markdown("---")
    st.markdown("### Full Report")
    
    if session.formatted_report:
        st.markdown(session.formatted_report)
    elif session.synthesize_data and session.synthesize_data.markdown_report:
        st.markdown(session.synthesize_data.markdown_report)
    
    # Display follow-up questions
    if session.synthesize_data and session.synthesize_data.follow_up_questions:
        st.markdown("---")
        st.markdown("### Follow-up Questions")
        for i, question in enumerate(session.synthesize_data.follow_up_questions, 1):
            st.markdown(f"{i}. {question}")


def render_citations(synthesize_data: Optional[SynthesizeData]):
    """Render citations and bibliography in expander"""
    if not synthesize_data:
        return
    
    # Extract citations from markdown report if available
    with st.expander("📚 Citations & Sources", expanded=False):
        st.markdown("### Sources")
        
        # Note: The current implementation doesn't extract structured citations
        # This is a placeholder that can be enhanced when citation tracking is added
        if synthesize_data.markdown_report:
            # Try to find URLs in the markdown
            import re
            urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', 
                            synthesize_data.markdown_report)
            
            if urls:
                for i, url in enumerate(set(urls), 1):
                    st.markdown(f"[{i}] {url}")
            else:
                st.info("Citations will be displayed here when available. The research system is working on extracting source citations.")
        else:
            st.info("No citations available for this research session.")


def render_research_history():
    """Render research history list"""
    history = st.session_state.get("research_history", [])
    
    if not history:
        st.info("No research history yet. Start a new research to see results here.")
        return
    
    st.header("📜 Research History")
    
    for session in history:
        with st.expander(
            f"{session.topic[:60]}... | {session.created_at.strftime('%Y-%m-%d %H:%M')} | {session.status.upper()}",
            expanded=False
        ):
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Status:** {session.status}")
                st.write(f"**Created:** {session.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
                if session.completed_at:
                    st.write(f"**Completed:** {session.completed_at.strftime('%Y-%m-%d %H:%M:%S')}")
                if session.execution_time:
                    st.write(f"**Duration:** {session.execution_time:.1f} seconds")
            
            with col2:
                if session.status == "completed":
                    st.success("✅ Completed")
                elif session.status == "error":
                    st.error("❌ Error")
                elif session.status == "running":
                    st.warning("⏳ Running")
                
                if st.button("View Report", key=f"view_{session.id}"):
                    st.session_state["ui_state"]["selected_research_id"] = session.id
                    st.session_state["ui_state"]["active_tab"] = "history"
                    st.rerun()
            
            if session.error:
                st.error(f"Error: {session.error}")
                if st.checkbox("Show technical details", key=f"details_{session.id}"):
                    st.code(session.error_traceback or "")
