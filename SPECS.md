# Streamlit Frontend - Technical Specifications
**Status**: ✅ Implemented
**Last Updated**: 2024-02-09


---

## 1. Overview

This document defines the technical architecture for a Streamlit web application that provides a user-friendly interface for the Deep Research system. The app will enable users to configure API keys, run research queries, view results, and manage research history.

### Key Requirements
- Secure API key management
- Real-time research progress updates
- Research history and session management
- Rich markdown report display with citations
- Export functionality

---

## 2. Session State Architecture

### 2.1 Session State Structure

The application will use `st.session_state` to manage application state across reruns. The following structure is proposed:

```python
st.session_state = {
    # API Configuration
    "api_keys": {
        "openai_api_key": str | None,
        "anthropic_api_key": str | None,
        "qwen_api_key": str | None,
        "tavily_api_key": str | None,
        "deepseek_api_key": str | None,
    },
    
    # Model Configuration
    "model_config": {
        "planner_model": str,
        "executor_model": str,
        "synthesizer_model": str,
        "fact_checker_model": str,
        "executor_search_method": str,  # "qwen", "tavily", "duckduckgo"
    },
    
    # Research Parameters
    "research_params": {
        "planner_temperature": float,
        "executor_temperature": float,
        "synthesizer_temperature": float,
        "fact_checker_enabled": bool,
        "fact_checker_max_depth": int,
        "fact_checker_confidence_threshold": float,
    },
    
    # Research History (List of ResearchSession objects)
    "research_history": List[ResearchSession],
    
    # Current Research Session
    "current_research": ResearchSession | None,
    
    # UI State
    "ui_state": {
        "sidebar_expanded": bool,
        "selected_research_id": str | None,  # ID of research to display
        "active_tab": str,  # "new_research", "history", "settings"
    },
    
    # Research Execution State
    "research_status": {
        "is_running": bool,
        "current_step": str | None,  # "planning", "execution", "fact_checking", "synthesis"
        "progress": float,  # 0.0 to 1.0
        "status_message": str,
        "error": str | None,
    },
}
```

### 2.2 ResearchSession Data Model

```python
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from deep_research import SynthesizeData

@dataclass
class ResearchSession:
    """Represents a single research session"""
    id: str  # UUID or timestamp-based ID
    topic: str
    created_at: datetime
    completed_at: Optional[datetime]
    status: str  # "pending", "running", "completed", "error"
    
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
    config_snapshot: Optional[dict] = None  # Snapshot of config used
    execution_time: Optional[float] = None  # Seconds
```

### 2.3 Session State Initialization

```python
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
```

### 2.4 Session State Persistence Strategy

**In-Memory Only (Default)**:
- Session state persists only during the Streamlit session
- Data is lost on page refresh or session timeout
- Suitable for development and single-user scenarios

**Future Enhancement - Local Storage**:
- Use `streamlit-option-menu` or similar for persistent settings
- Consider browser localStorage via `streamlit-javascript` component
- For production: implement database backend (SQLite, PostgreSQL)

---

## 3. Security Architecture

### 3.1 API Key Management Strategy

**Primary Method: Streamlit Secrets (`st.secrets`)**

For production deployments, API keys should be stored in Streamlit's secrets management:

**File Structure**:
```
.streamlit/
└── secrets.toml  # Git-ignored, contains API keys
```

**secrets.toml Format**:
```toml
[api_keys]
openai_api_key = "sk-..."
anthropic_api_key = "sk-ant-..."
qwen_api_key = "sk-..."
tavily_api_key = "tvly-..."
deepseek_api_key = "sk-..."

[model_config]
planner_model = "gpt-4-turbo-preview"
executor_model = "gpt-3.5-turbo"
synthesizer_model = "gpt-4-turbo-preview"
fact_checker_model = "gpt-4-turbo-preview"
executor_search_method = "qwen"
```

**Fallback Method: Sidebar Input**

For development and user convenience, provide sidebar input fields as a fallback:

```python
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
    for key_name in keys.keys():
        session_key = f"api_key_{key_name}"
        if keys[key_name] is None and session_key in st.session_state:
            keys[key_name] = st.session_state[session_key]
    
    return keys
```

### 3.2 API Key Input UI (Sidebar)

```python
def render_api_key_inputs():
    """Render API key input fields in sidebar"""
    st.sidebar.header("🔑 API Keys")
    st.sidebar.caption("Enter API keys or use Streamlit secrets")
    
    # Check if secrets are available
    has_secrets = hasattr(st, "secrets") and "api_keys" in st.secrets
    
    if has_secrets:
        st.sidebar.success("✅ Using API keys from secrets")
        st.sidebar.caption("Keys loaded from .streamlit/secrets.toml")
    else:
        st.sidebar.info("💡 Tip: Use Streamlit secrets for production")
    
    # API Key Input Fields
    api_keys = {}
    
    with st.sidebar.expander("API Keys", expanded=not has_secrets):
        api_keys["openai_api_key"] = st.text_input(
            "OpenAI API Key",
            value=st.session_state.get("api_key_openai_api_key", ""),
            type="password",
            help="Required for OpenAI models (GPT-4, GPT-3.5)"
        )
        
        api_keys["anthropic_api_key"] = st.text_input(
            "Anthropic API Key",
            value=st.session_state.get("api_key_anthropic_api_key", ""),
            type="password",
            help="Required for Claude models"
        )
        
        api_keys["qwen_api_key"] = st.text_input(
            "Qwen API Key",
            value=st.session_state.get("api_key_qwen_api_key", ""),
            type="password",
            help="Optional: For Qwen search method"
        )
        
        api_keys["tavily_api_key"] = st.text_input(
            "Tavily API Key",
            value=st.session_state.get("api_key_tavily_api_key", ""),
            type="password",
            help="Optional: For Tavily search method"
        )
        
        api_keys["deepseek_api_key"] = st.text_input(
            "DeepSeek API Key",
            value=st.session_state.get("api_key_deepseek_api_key", ""),
            type="password",
            help="Optional: For DeepSeek models"
        )
    
    # Store in session state
    for key, value in api_keys.items():
        st.session_state[f"api_key_{key}"] = value
    
    return api_keys
```

### 3.3 Security Best Practices

1. **Never Log API Keys**: Ensure API keys are never printed or logged
2. **Mask in UI**: Use `type="password"` for all API key inputs
3. **Secrets Validation**: Validate that at least one required API key is present
4. **Session Isolation**: Each Streamlit session has isolated session state
5. **No Persistence**: Don't save API keys to files (except secrets.toml which is git-ignored)

---

## 4. File Structure & Modularity

### 4.1 Proposed Directory Structure

```
deep-research/
├── app.py                          # Main Streamlit application entry point
├── utils/
│   ├── __init__.py
│   ├── researcher.py               # Backend logic wrapper for DeepResearch
│   ├── session_manager.py          # Session state management utilities
│   ├── config_builder.py           # Build Config from session state
│   └── ui_components.py            # Reusable UI components
├── deep_research/                  # Existing backend package
│   ├── __init__.py
│   ├── config.py
│   ├── orchestrator.py
│   ├── planner.py
│   ├── executor.py
│   ├── synthesizer.py
│   └── fact_checker.py
├── .streamlit/
│   ├── config.toml                 # Streamlit app configuration
│   └── secrets.toml                 # API keys (git-ignored)
├── requirements.txt
├── README.md
└── SPECS.md                        # This file
```

### 4.2 Module Responsibilities

#### `app.py` - Main Application
**Responsibilities**:
- Streamlit app entry point
- Page layout and navigation
- Component orchestration
- User interaction handling

**Key Functions**:
```python
def main():
    """Main Streamlit application"""
    initialize_session_state()
    render_sidebar()
    render_main_content()

def render_sidebar():
    """Render sidebar with settings and API keys"""

def render_main_content():
    """Render main content area based on active tab"""
```

#### `utils/researcher.py` - Backend Integration
**Responsibilities**:
- Wrapper around `DeepResearch` orchestrator
- Thread-safe research execution
- Progress callback handling
- Error handling and recovery

**Key Classes/Functions**:
```python
class ResearchRunner:
    """Thread-safe wrapper for DeepResearch"""
    
    def __init__(self, config: Config):
        """Initialize with config"""
    
    def run_research(
        self, 
        topic: str, 
        progress_callback: Optional[Callable] = None
    ) -> ResearchSession:
        """Run research with progress updates"""
    
    def cancel_research(self):
        """Cancel ongoing research"""
```

#### `utils/session_manager.py` - State Management
**Responsibilities**:
- Session state initialization
- Research history management
- State persistence helpers

**Key Functions**:
```python
def initialize_session_state():
    """Initialize all session state variables"""

def add_research_to_history(session: ResearchSession):
    """Add research session to history"""

def get_research_by_id(research_id: str) -> Optional[ResearchSession]:
    """Retrieve research session by ID"""

def clear_research_history():
    """Clear all research history"""
```

#### `utils/config_builder.py` - Configuration Builder
**Responsibilities**:
- Build `Config` object from session state
- Validate configuration
- Handle API key loading

**Key Functions**:
```python
def build_config_from_session() -> Config:
    """Build Config object from session state"""
    
def validate_config(config: Config) -> tuple[bool, list[str]]:
    """Validate configuration and return (is_valid, errors)"""
```

#### `utils/ui_components.py` - UI Components
**Responsibilities**:
- Reusable Streamlit components
- Report display components
- Progress indicators
- Citation renderers

**Key Functions**:
```python
def render_research_form():
    """Render research topic input form"""

def render_progress_indicator(status: dict):
    """Render research progress indicator"""

def render_research_report(session: ResearchSession):
    """Render formatted research report"""

def render_citations(synthesize_data: SynthesizeData):
    """Render citations and bibliography"""
```

---

## 5. Data Flow Architecture

### 5.1 Research Execution Flow

```
User Input (Topic)
    ↓
[app.py] Validate Input
    ↓
[config_builder.py] Build Config from Session State
    ↓
[researcher.py] Create ResearchRunner
    ↓
[researcher.py] Run Research (Thread/Async)
    ↓
[orchestrator.py] DeepResearch.research()
    ├─→ Planning (Update progress: 25%)
    ├─→ Execution (Update progress: 50%)
    ├─→ Fact-Checking (Update progress: 75%)
    └─→ Synthesis (Update progress: 100%)
    ↓
[researcher.py] Create ResearchSession
    ↓
[session_manager.py] Add to History
    ↓
[app.py] Display Results
```

### 5.2 Progress Update Mechanism

```python
# In utils/researcher.py
def progress_callback(step: str, progress: float, message: str):
    """Callback function to update session state"""
    st.session_state["research_status"] = {
        "is_running": True,
        "current_step": step,
        "progress": progress,
        "status_message": message,
        "error": None,
    }
    # Trigger rerun to update UI
    st.rerun()
```

**Note**: Streamlit's threading model requires careful handling. Consider:
- Using `st.rerun()` judiciously to avoid infinite loops
- Using `threading.Event` for cancellation
- Using `queue.Queue` for progress updates if needed

### 5.3 Configuration Flow

```
Session State (API Keys, Models, Params)
    ↓
[config_builder.py] build_config_from_session()
    ↓
[researcher.py] Create Config Object
    ↓
[DeepResearch] Initialize with Config
    ↓
Research Execution
```

---

## 6. UI Component Specifications

### 6.1 Sidebar Layout

```
┌─────────────────────────┐
│ 🔑 API Keys             │
│ [Input Fields]          │
│                         │
│ ⚙️ Model Configuration   │
│ [Dropdowns]             │
│                         │
│ 🔍 Search Settings      │
│ [Method Selection]      │
│                         │
│ ✅ Fact-Checking        │
│ [Toggle + Settings]     │
│                         │
│ 🌡️ Temperature Settings  │
│ [Sliders]               │
└─────────────────────────┘
```

### 6.2 Main Content Layout

**Tab 1: New Research**
```
┌─────────────────────────────────────┐
│ Research Topic Input                │
│ [Text Area]                         │
│ [Start Research Button]             │
│                                     │
│ Progress Indicator                  │
│ [Progress Bar]                      │
│ [Status Message]                    │
│                                     │
│ Results (when complete)             │
│ [Report Display]                    │
└─────────────────────────────────────┘
```

**Tab 2: Research History**
```
┌─────────────────────────────────────┐
│ Research History                    │
│ ┌───────────────────────────────┐   │
│ │ Topic 1 | Date | [View]      │   │
│ │ Topic 2 | Date | [View]      │   │
│ └───────────────────────────────┘   │
│                                     │
│ Selected Research Report            │
│ [Full Report Display]               │
└─────────────────────────────────────┘
```

### 6.3 Report Display Components

**Report Structure**:
1. **Executive Summary** (Expandable)
2. **Full Report** (Markdown with syntax highlighting)
3. **Citations Section** (Expandable)
4. **Follow-up Questions** (List)
5. **Export Buttons** (Markdown, PDF)

**Citation Display**:
- In-text citations: `[1]`, `[2]`, etc.
- Bibliography: Expandable section with full source details
- Clickable source links

---

## 7. Integration Points

### 7.1 DeepResearch Orchestrator Integration

```python
# In utils/researcher.py
from deep_research import DeepResearch, Config

class ResearchRunner:
    def __init__(self, config: Config):
        self.config = config
        self.researcher = DeepResearch(config)
        self._cancelled = False
    
    def run_research(self, topic: str, progress_callback=None):
        """Run research with progress updates"""
        try:
            # Step 1: Planning
            if progress_callback:
                progress_callback("planning", 0.25, "Planning research strategy...")
            
            plan = self.researcher.planner.create_research_plan(topic)
            
            # Step 2: Execution
            if progress_callback:
                progress_callback("execution", 0.50, "Executing searches...")
            
            queries = [item.query for item in plan.searches]
            search_results = self.researcher.executor.execute_search_queries(queries)
            
            # Step 2.5: Fact-Checking
            if self.config.fact_checker_enabled:
                if progress_callback:
                    progress_callback("fact_checking", 0.75, "Fact-checking and verification...")
                
                from deep_research.fact_checker import FactCheckerAgent
                fact_checker = FactCheckerAgent(self.config)
                search_results = fact_checker.fact_check_summaries(search_results)
            
            # Step 3: Synthesis
            if progress_callback:
                progress_callback("synthesis", 0.90, "Synthesizing final report...")
            
            synthesize_data = self.researcher.synthesizer.synthesize_report(
                topic, search_results
            )
            formatted_report = self.researcher.synthesizer.format_report(
                synthesize_data, topic
            )
            
            if progress_callback:
                progress_callback("completed", 1.0, "Research complete!")
            
            return ResearchSession(
                id=generate_id(),
                topic=topic,
                created_at=datetime.now(),
                completed_at=datetime.now(),
                status="completed",
                synthesize_data=synthesize_data,
                formatted_report=formatted_report,
            )
            
        except Exception as e:
            return ResearchSession(
                id=generate_id(),
                topic=topic,
                created_at=datetime.now(),
                status="error",
                error=str(e),
            )
```

### 7.2 Configuration Integration

```python
# In utils/config_builder.py
from deep_research import Config

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
```

---

## 8. Error Handling

### 8.1 Error Categories

1. **Configuration Errors**: Missing API keys, invalid model names
2. **Execution Errors**: Network failures, API rate limits, timeouts
3. **Validation Errors**: Invalid topic input, empty queries

### 8.2 Error Display Strategy

```python
def display_error(error: str, traceback: Optional[str] = None):
    """Display error in UI"""
    st.error(f"❌ Error: {error}")
    
    if traceback and st.checkbox("Show technical details"):
        st.code(traceback, language="python")
```

### 8.3 Error Recovery

- **API Key Missing**: Show clear message with instructions
- **Network Error**: Allow retry with exponential backoff
- **Rate Limit**: Show wait time and retry option
- **Timeout**: Allow cancellation and restart

---

## 9. Performance Considerations

### 9.1 Streamlit Rerun Optimization

- Use `st.session_state` to prevent unnecessary reruns
- Cache expensive operations with `@st.cache_data`
- Use `st.empty()` containers for dynamic updates

### 9.2 Research Execution

- Run research in separate thread to prevent UI blocking
- Use progress callbacks for real-time updates
- Implement cancellation mechanism

### 9.3 Memory Management

- Limit research history size (e.g., last 10 sessions)
- Clear old sessions on new research start
- Use generators for large data processing

---

## 10. Testing Strategy

### 10.1 Unit Tests

- `utils/config_builder.py`: Test config building from session state
- `utils/session_manager.py`: Test session state management
- `utils/researcher.py`: Test research execution wrapper

### 10.2 Integration Tests

- End-to-end research flow
- Error handling scenarios
- Configuration validation

### 10.3 UI Tests

- Manual testing of all UI components
- Cross-browser compatibility
- Responsive design validation

---

## 11. Deployment Considerations

### 11.1 Streamlit Cloud Deployment

1. **Secrets Management**: Use Streamlit Cloud secrets
2. **Requirements**: Ensure `requirements.txt` includes `streamlit`
3. **App Configuration**: Set up `.streamlit/config.toml`

### 11.2 Local Development

1. **Run Command**: `streamlit run app.py`
2. **Port**: Default 8501
3. **Hot Reload**: Enabled by default

---

## 12. Implementation Checklist

### Phase 1: Core Infrastructure
- [ ] Create `utils/` directory structure
- [ ] Implement `utils/session_manager.py`
- [ ] Implement `utils/config_builder.py`
- [ ] Create `app.py` skeleton

### Phase 2: UI Components
- [ ] Implement sidebar with API key inputs
- [ ] Implement model configuration UI
- [ ] Create research input form
- [ ] Create progress indicator component

### Phase 3: Backend Integration
- [ ] Implement `utils/researcher.py`
- [ ] Integrate with `DeepResearch` orchestrator
- [ ] Implement progress callback mechanism
- [ ] Add error handling

### Phase 4: Results Display
- [ ] Implement report display component
- [ ] Add citation rendering
- [ ] Create export functionality
- [ ] Add research history view

### Phase 5: Polish & Testing
- [ ] Add input validation
- [ ] Improve error messages
- [ ] Add loading states
- [ ] Test end-to-end workflow

---

## 13. Dependencies

Add to `requirements.txt`:
```
streamlit>=1.28.0
streamlit-option-menu>=0.3.6  # Optional: For better UI components
```

---

## 14. Next Steps

**@Coder, your turn to implement the Streamlit frontend.**

Start with:
1. Create `utils/` directory and `__init__.py`
2. Implement `utils/session_manager.py` (Phase 1)
3. Implement `utils/config_builder.py` (Phase 1)
4. Create basic `app.py` structure (Phase 1)
5. Then proceed through remaining phases sequentially

Refer to this SPECS.md document throughout implementation for architectural guidance.

---

**Document Status**: ✅ Complete - Ready for Implementation  
**Last Updated**: Architecture Phase  
**Next Action**: @Coder to begin Phase 1 implementation
