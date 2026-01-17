"""
Deep Research - Automated Research Assistant System
"""

from .orchestrator import DeepResearch
from .manager import DeepResearchManager
from .config import Config
from .synthesizer import SynthesizeData
from .system_status import SystemStatus

__version__ = "0.1.0"
__all__ = ["DeepResearch", "DeepResearchManager", "Config", "SynthesizeData", "SystemStatus"]
