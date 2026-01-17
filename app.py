"""
Streamlit Frontend for Deep Research System
"""

import streamlit as st
import threading
import time
from utils.session_manager import initialize_session_state, add_research_to_history, get_research_by_id
from utils.config_builder import build_config_from_session, validate_config
from utils.researcher import ResearchRunner
from utils.ui_components import (
    render_research_form,
    render_progress_indicator,
    render_research_report,
    render_citations,
    render_research_history
)


def load_api_keys_from_secrets():
    """Load API keys from st.secrets, fallback to session state"""
    keys = {}
    
    # Try to load from secrets first
    if hasattr(st, "secrets") and "api_keys" in st.secrets:
        secrets = st.secrets["api_keys"]
        keys = {
            "openai_api_key": secrets.get("openai_api_key"),
            "anthropic_api_key": secrets.get("anthropic_api_key"),
            "qwen_api_key": secrets.get("qwen_api_key"),
            "tavily_api_key": secrets.get("tavily_api_key"),
            "deepseek_api_key": secrets.get("deepseek_api_key"),
        }
    
    # Fallback to session state (from sidebar input)
    session_keys = st.session_state.get("api_keys", {})
    for key_name in ["openai_api_key", "anthropic_api_key", "qwen_api_key", "tavily_api_key", "deepseek_api_key"]:
        if keys.get(key_name) is None and key_name in session_keys:
            keys[key_name] = session_keys[key_name]
    
    return keys


def render_sidebar():
    """Render sidebar with settings and API keys"""
    st.sidebar.header("⚙️ Configuration")
    
    # API Keys Section
    st.sidebar.subheader("🔑 API Keys")
    
    # Check if secrets are available
    has_secrets = hasattr(st, "secrets") and "api_keys" in st.secrets
    
    if has_secrets:
        st.sidebar.success("✅ Using API keys from secrets")
        st.sidebar.caption("Keys loaded from .streamlit/secrets.toml")
    else:
        st.sidebar.info("💡 Tip: Use Streamlit secrets for production")
    
    # API Key Input Fields
    with st.sidebar.expander("API Keys", expanded=not has_secrets):
        api_keys = {}
        
        api_keys["openai_api_key"] = st.text_input(
            "OpenAI API Key",
            value=st.session_state.get("api_keys", {}).get("openai_api_key", ""),
            type="password",
            help="Required for OpenAI models (GPT-4, GPT-3.5)",
            key="sidebar_openai_key"
        )
        
        api_keys["anthropic_api_key"] = st.text_input(
            "Anthropic API Key",
            value=st.session_state.get("api_keys", {}).get("anthropic_api_key", ""),
            type="password",
            help="Required for Claude models",
            key="sidebar_anthropic_key"
        )
        
        api_keys["qwen_api_key"] = st.text_input(
            "Qwen API Key",
            value=st.session_state.get("api_keys", {}).get("qwen_api_key", ""),
            type="password",
            help="Optional: For Qwen search method",
            key="sidebar_qwen_key"
        )
        
        api_keys["tavily_api_key"] = st.text_input(
            "Tavily API Key",
            value=st.session_state.get("api_keys", {}).get("tavily_api_key", ""),
            type="password",
            help="Optional: For Tavily search method",
            key="sidebar_tavily_key"
        )
        
        api_keys["deepseek_api_key"] = st.text_input(
            "DeepSeek API Key",
            value=st.session_state.get("api_keys", {}).get("deepseek_api_key", ""),
            type="password",
            help="Optional: For DeepSeek models",
            key="sidebar_deepseek_key"
        )
        
        # Store in session state
        st.session_state["api_keys"] = api_keys
    
    # Model Configuration
    st.sidebar.subheader("🤖 Model Configuration")
    with st.sidebar.expander("Models", expanded=False):
        model_config = st.session_state.get("model_config", {})
        
        model_config["planner_model"] = st.selectbox(
            "Planner Model",
            ["gpt-4-turbo-preview", "gpt-4", "gpt-3.5-turbo", "claude-3-5-sonnet-20241022"],
            index=0 if model_config.get("planner_model") == "gpt-4-turbo-preview" else 2,
            key="sidebar_planner_model"
        )
        
        model_config["executor_model"] = st.selectbox(
            "Executor Model",
            ["gpt-3.5-turbo", "gpt-4-turbo-preview", "gpt-4", "claude-3-5-sonnet-20241022"],
            index=0 if model_config.get("executor_model") == "gpt-3.5-turbo" else 0,
            key="sidebar_executor_model"
        )
        
        model_config["synthesizer_model"] = st.selectbox(
            "Synthesizer Model",
            ["gpt-4-turbo-preview", "gpt-4", "gpt-3.5-turbo", "claude-3-5-sonnet-20241022"],
            index=0 if model_config.get("synthesizer_model") == "gpt-4-turbo-preview" else 0,
            key="sidebar_synthesizer_model"
        )
        
        model_config["fact_checker_model"] = st.selectbox(
            "Fact Checker Model",
            ["gpt-4-turbo-preview", "gpt-4", "gpt-3.5-turbo", "claude-3-5-sonnet-20241022"],
            index=0 if model_config.get("fact_checker_model") == "gpt-4-turbo-preview" else 0,
            key="sidebar_fact_checker_model"
        )
        
        model_config["executor_search_method"] = st.selectbox(
            "Search Method",
            ["qwen", "tavily", "duckduckgo"],
            index=0 if model_config.get("executor_search_method") == "qwen" else 2,
            key="sidebar_search_method"
        )
        
        st.session_state["model_config"] = model_config
    
    # Research Parameters
    st.sidebar.subheader("🔍 Research Settings")
    with st.sidebar.expander("Parameters", expanded=False):
        research_params = st.session_state.get("research_params", {})
        
        research_params["fact_checker_enabled"] = st.checkbox(
            "Enable Fact-Checking",
            value=research_params.get("fact_checker_enabled", True),
            key="sidebar_fact_checker_enabled"
        )
        
        if research_params["fact_checker_enabled"]:
            research_params["fact_checker_max_depth"] = st.slider(
                "Fact Checker Max Depth",
                min_value=1,
                max_value=3,
                value=research_params.get("fact_checker_max_depth", 2),
                key="sidebar_fact_checker_depth"
            )
            
            research_params["fact_checker_confidence_threshold"] = st.slider(
                "Confidence Threshold",
                min_value=0.0,
                max_value=1.0,
                value=research_params.get("fact_checker_confidence_threshold", 0.6),
                step=0.1,
                key="sidebar_confidence_threshold"
            )
        
        research_params["planner_temperature"] = st.slider(
            "Planner Temperature",
            min_value=0.0,
            max_value=1.0,
            value=research_params.get("planner_temperature", 0.7),
            step=0.1,
            key="sidebar_planner_temp"
        )
        
        research_params["executor_temperature"] = st.slider(
            "Executor Temperature",
            min_value=0.0,
            max_value=1.0,
            value=research_params.get("executor_temperature", 0.3),
            step=0.1,
            key="sidebar_executor_temp"
        )
        
        research_params["synthesizer_temperature"] = st.slider(
            "Synthesizer Temperature",
            min_value=0.0,
            max_value=1.0,
            value=research_params.get("synthesizer_temperature", 0.7),
            step=0.1,
            key="sidebar_synthesizer_temp"
        )
        
        st.session_state["research_params"] = research_params


def run_research_in_thread(topic: str, quick_research: bool = False):
    """Run research in a separate thread to avoid blocking UI"""
    def research_thread():
        try:
            # Build config from session state
            config = build_config_from_session()
            
            # Validate config
            is_valid, errors = validate_config(config)
            if not is_valid:
                # Use a thread-safe way to update session state
                # Note: Direct session state updates from threads may not always work
                # The UI will poll for updates via the refresh button
                with st.session_state._lock if hasattr(st.session_state, '_lock') else threading.Lock():
                    st.session_state["research_status"] = {
                        "is_running": False,
                        "current_step": "error",
                        "progress": 0.0,
                        "status_message": "; ".join(errors),
                        "error": "; ".join(errors),
                    }
                return
            
            # Create research runner
            runner = ResearchRunner(config)
            
            # Progress callback - updates session state
            def progress_callback(step: str, progress: float, message: str):
                # Thread-safe update (Streamlit handles this, but be cautious)
                try:
                    st.session_state["research_status"] = {
                        "is_running": True,
                        "current_step": step,
                        "progress": progress,
                        "status_message": message,
                        "error": None,
                    }
                except Exception:
                    # If session state update fails from thread, that's OK
                    # User can refresh manually
                    pass
            
            # Run research
            session = runner.run_research(topic, progress_callback=progress_callback)
            
            # Update session state (final update)
            try:
                st.session_state["research_status"] = {
                    "is_running": False,
                    "current_step": session.status,
                    "progress": 1.0 if session.status == "completed" else 0.0,
                    "status_message": session.status_message or "Research complete",
                    "error": session.error,
                }
                
                # Add to history
                add_research_to_history(session)
                st.session_state["current_research"] = session
            except Exception:
                # If update fails, store in a way that can be retrieved
                pass
            
        except Exception as e:
            import traceback
            try:
                st.session_state["research_status"] = {
                    "is_running": False,
                    "current_step": "error",
                    "progress": 0.0,
                    "status_message": f"Error: {str(e)}",
                    "error": str(e),
                }
            except Exception:
                pass
    
    # Start thread
    thread = threading.Thread(target=research_thread, daemon=True)
    thread.start()
    # Ensure research_status exists before accessing nested key
    if "research_status" not in st.session_state:
        st.session_state["research_status"] = {}
    st.session_state["research_status"]["is_running"] = True


def render_main_content():
    """Render main content area based on active tab"""
    ui_state = st.session_state.get("ui_state", {})
    active_tab = ui_state.get("active_tab", "new_research")
    
    # Tab selection
    tabs = st.tabs(["🔍 New Research", "📜 History", "ℹ️ About"])
    
    # New Research Tab
    with tabs[0]:
        # Check if research is running
        research_status = st.session_state.get("research_status", {})
        
        if research_status.get("is_running"):
            st.info("⏳ Research in progress...")
            render_progress_indicator(research_status)
            st.button("Refresh Status", on_click=st.rerun)
        else:
            # Render research form
            topic, start_button, quick_research = render_research_form()
            
            if start_button:
                if not topic or not topic.strip():
                    st.error("Please enter a research topic")
                else:
                    # Start research
                    run_research_in_thread(topic.strip(), quick_research)
                    st.rerun()
            
            # Show current research if available
            current_research = st.session_state.get("current_research")
            if current_research and current_research.status == "completed":
                st.markdown("---")
                st.markdown("### Latest Research Results")
                render_research_report(current_research)
                render_citations(current_research.synthesize_data)
                
                # Export buttons
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("📥 Download Markdown"):
                        st.download_button(
                            label="Download Report",
                            data=current_research.formatted_report or current_research.synthesize_data.markdown_report if current_research.synthesize_data else "",
                            file_name=f"research_{current_research.id}.md",
                            mime="text/markdown"
                        )
    
    # History Tab
    with tabs[1]:
        # Check if a specific research is selected
        selected_id = ui_state.get("selected_research_id")
        if selected_id:
            session = get_research_by_id(selected_id)
            if session:
                st.button("← Back to History", on_click=lambda: st.session_state.update({"ui_state": {"selected_research_id": None, "active_tab": "history"}}))
                st.markdown(f"### Research: {session.topic}")
                render_research_report(session)
                render_citations(session.synthesize_data)
            else:
                st.warning("Research session not found")
                if "ui_state" not in st.session_state:
                    st.session_state["ui_state"] = {}
                st.session_state["ui_state"]["selected_research_id"] = None
        else:
            render_research_history()
    
    # About Tab
    with tabs[2]:
        st.header("About Deep Research")
        st.markdown("""
        Deep Research is an automated research assistant system that uses a multi-agent architecture 
        to conduct comprehensive research and generate detailed reports.
        
        ### Features
        - **Intelligent Planning**: Generates research strategies and search queries
        - **Web Search**: Performs searches across multiple sources
        - **Fact-Checking**: Verifies factual claims with recursive verification
        - **Report Synthesis**: Generates comprehensive, well-structured reports
        
        ### How It Works
        1. **Planning**: Analyzes your topic and generates search queries
        2. **Execution**: Performs web searches and summarizes content
        3. **Fact-Checking**: Verifies facts with confidence scores
        4. **Synthesis**: Consolidates results into a final report
        
        ### Configuration
        Configure API keys, models, and research parameters in the sidebar.
        """)


def main():
    """Main Streamlit application"""
    st.set_page_config(
        page_title="Deep Research",
        page_icon="🔍",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("🔍 Deep Research")
    st.caption("Automated research assistant with fact-checking")
    
    # Initialize session state
    initialize_session_state()
    
    # Render sidebar
    render_sidebar()
    
    # Render main content
    render_main_content()
    
    # Note: Auto-refresh is handled by the research thread updating session state
    # and user clicking "Refresh Status" button, or by Streamlit's natural rerun on interaction


if __name__ == "__main__":
    main()
