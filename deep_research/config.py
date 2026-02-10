"""
Configuration management for Deep Research system
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

try:
    load_dotenv()
except Exception:
    pass

# Try loading from .env.github if available (fallback for permission issues)
try:
    load_dotenv(".env.github")
except Exception:
    pass


class Config(BaseSettings):
    """Configuration settings for Deep Research"""
    
    # API Keys
    openai_api_key: Optional[str] = os.getenv("OPENAI_API_KEY")
    openai_base_url: Optional[str] = os.getenv("OPENAI_BASE_URL")
    anthropic_api_key: Optional[str] = os.getenv("ANTHROPIC_API_KEY")
    deepseek_api_key: Optional[str] = os.getenv("DEEPSEEK_API_KEY")
    deepseek_base_url: str = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")
    qwen_api_key: Optional[str] = os.getenv("QWEN_API_KEY")
    tavily_api_key: Optional[str] = os.getenv("TAVILY_API_KEY")
    
    # Model Configuration
    # High-capability models for Planning and Synthesis
    planner_model: str = os.getenv("PLANNER_MODEL", "gpt-4-turbo-preview")
    synthesizer_model: str = os.getenv("SYNTHESIZER_MODEL", "gpt-4-turbo-preview")
    
    # Cost-effective models for Execution
    executor_model: str = os.getenv("EXECUTOR_MODEL", "gpt-3.5-turbo")
    executor_search_method: str = os.getenv("EXECUTOR_SEARCH_METHOD", "qwen")  # Options: qwen, tavily, duckduckgo
    
    # Temperature settings
    planner_temperature: float = float(os.getenv("PLANNER_TEMPERATURE", "0.7"))
    executor_temperature: float = float(os.getenv("EXECUTOR_TEMPERATURE", "0.3"))
    synthesizer_temperature: float = float(os.getenv("SYNTHESIZER_TEMPERATURE", "0.7"))
    
    # Search configuration
    max_search_results: int = int(os.getenv("MAX_SEARCH_RESULTS", "10"))
    max_summary_length: int = int(os.getenv("MAX_SUMMARY_LENGTH", "500"))
    
    # Fact-Checking configuration
    fact_checker_enabled: bool = os.getenv("FACT_CHECKER_ENABLED", "true").lower() == "true"
    fact_checker_model: str = os.getenv("FACT_CHECKER_MODEL", "gpt-4-turbo-preview")
    fact_checker_max_depth: int = int(os.getenv("FACT_CHECKER_MAX_DEPTH", "2"))
    fact_checker_confidence_threshold: float = float(os.getenv("FACT_CHECKER_CONFIDENCE_THRESHOLD", "0.6"))
    fact_checker_max_verification_queries: int = int(os.getenv("FACT_CHECKER_MAX_VERIFICATION_QUERIES", "3"))
    fact_checker_temperature: float = float(os.getenv("FACT_CHECKER_TEMPERATURE", "0.3"))
    
    class Config:
        env_file = ".env.github"
        extra = "ignore"
        case_sensitive = False
