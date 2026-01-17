"""
Session state management utilities
"""

import streamlit as st
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List
from deep_research import SynthesizeData


@dataclass
class ResearchSession:
    """Represents a single research session"""
    id: str
    topic: str
    created_at: datetime
    completed_at: Optional[datetime] = None
    status: str = "pending"  # "pending", "running", "completed", "error"
    
    # Research Results
    synthesize_data: Optional[SynthesizeData] = None
    formatted_report: Optional[str] = None
    
    # Progress Tracking
    current_step: Optional[str] = None
    progress: float = 0.0
    status_message: Optional[str] = None
    
    # Error Handling
    error: Optional[str] = None
    error_traceback: Optional[str] = None
    
    # Metadata
    config_snapshot: Optional[dict] = None
    execution_time: Optional[float] = None


def initialize_session_state():
    """Initialize all session state variables with defaults"""
    defaults = {
        "api_keys": {
            "openai_api_key": None,
            "anthropic_api_key": None,
            "qwen_api_key": None,
            "tavily_api_key": None,
            "deepseek_api_key": None,
        },
        "model_config": {
            "planner_model": "gpt-4-turbo-preview",
            "executor_model": "gpt-3.5-turbo",
            "synthesizer_model": "gpt-4-turbo-preview",
            "fact_checker_model": "gpt-4-turbo-preview",
            "executor_search_method": "qwen",
        },
        "research_params": {
            "planner_temperature": 0.7,
            "executor_temperature": 0.3,
            "synthesizer_temperature": 0.7,
            "fact_checker_enabled": True,
            "fact_checker_max_depth": 2,
            "fact_checker_confidence_threshold": 0.6,
        },
        "research_history": [],
        "current_research": None,
        "ui_state": {
            "sidebar_expanded": True,
            "selected_research_id": None,
            "active_tab": "new_research",
        },
        "research_status": {
            "is_running": False,
            "current_step": None,
            "progress": 0.0,
            "status_message": None,
            "error": None,
        },
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def add_research_to_history(session: ResearchSession):
    """Add research session to history"""
    if "research_history" not in st.session_state:
        st.session_state["research_history"] = []
    
    # Add to history (keep last 20 sessions)
    st.session_state["research_history"].insert(0, session)
    if len(st.session_state["research_history"]) > 20:
        st.session_state["research_history"] = st.session_state["research_history"][:20]


def get_research_by_id(research_id: str) -> Optional[ResearchSession]:
    """Retrieve research session by ID"""
    if "research_history" not in st.session_state:
        return None
    
    for session in st.session_state["research_history"]:
        if session.id == research_id:
            return session
    
    return None


def clear_research_history():
    """Clear all research history"""
    st.session_state["research_history"] = []


def generate_research_id() -> str:
    """Generate a unique ID for a research session"""
    return datetime.now().strftime("%Y%m%d_%H%M%S_%f")
