"""
Configuration builder from session state
"""

import streamlit as st
from deep_research import Config


def load_api_keys_from_secrets() -> dict:
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


def build_config_from_session() -> Config:
    """Build Config object from session state"""
    api_keys = load_api_keys_from_secrets()
    
    # Create config with API keys
    config_dict = {
        "openai_api_key": api_keys.get("openai_api_key"),
        "anthropic_api_key": api_keys.get("anthropic_api_key"),
        "qwen_api_key": api_keys.get("qwen_api_key"),
        "tavily_api_key": api_keys.get("tavily_api_key"),
        "deepseek_api_key": api_keys.get("deepseek_api_key"),
    }
    
    # Add model configuration
    model_config = st.session_state.get("model_config", {})
    config_dict.update({
        "planner_model": model_config.get("planner_model", "gpt-4-turbo-preview"),
        "executor_model": model_config.get("executor_model", "gpt-3.5-turbo"),
        "synthesizer_model": model_config.get("synthesizer_model", "gpt-4-turbo-preview"),
        "fact_checker_model": model_config.get("fact_checker_model", "gpt-4-turbo-preview"),
        "executor_search_method": model_config.get("executor_search_method", "qwen"),
    })
    
    # Add research parameters
    research_params = st.session_state.get("research_params", {})
    config_dict.update({
        "planner_temperature": research_params.get("planner_temperature", 0.7),
        "executor_temperature": research_params.get("executor_temperature", 0.3),
        "synthesizer_temperature": research_params.get("synthesizer_temperature", 0.7),
        "fact_checker_enabled": research_params.get("fact_checker_enabled", True),
        "fact_checker_max_depth": research_params.get("fact_checker_max_depth", 2),
        "fact_checker_confidence_threshold": research_params.get("fact_checker_confidence_threshold", 0.6),
    })
    
    return Config(**config_dict)


def validate_config(config: Config) -> tuple[bool, list[str]]:
    """Validate configuration and return (is_valid, errors)"""
    errors = []
    
    # Check for at least one API key
    if not config.openai_api_key and not config.anthropic_api_key:
        errors.append("At least one API key (OpenAI or Anthropic) is required")
    
    return len(errors) == 0, errors
