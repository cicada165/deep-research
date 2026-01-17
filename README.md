# Deep Research

An intelligent, automated research assistant system that uses a multi-agent architecture to conduct comprehensive research, verify facts recursively, and generate detailed reports with citations.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🎯 Overview

Deep Research is an AI-powered research system that automates the entire research workflow:

1. **Intelligent Planning**: Generates strategic search queries based on your research topic
2. **Comprehensive Execution**: Performs parallel web searches and extracts relevant content
3. **Recursive Fact-Checking**: Verifies claims with multi-level verification for accuracy
4. **Report Synthesis**: Generates comprehensive, well-structured research reports with citations

The system uses a cost-optimized architecture that employs high-capability models (GPT-4, Claude) for reasoning tasks and cost-effective models (GPT-3.5) for simpler operations.

## ✨ Key Features

- **Multi-Agent Architecture**: Specialized agents for planning, execution, fact-checking, and synthesis
- **Recursive Fact Verification**: Multi-level verification system that cross-references sources and improves confidence scores
- **Multiple Search Methods**: Supports Qwen, Tavily, and DuckDuckGo search backends
- **Streamlit Web Interface**: User-friendly web UI for running research and viewing results
- **Configurable Models**: Choose different LLMs for different tasks to optimize cost and quality
- **Citation Tracking**: Automatic citation generation with source verification
- **Export Functionality**: Save reports as Markdown files

## 🏗️ Architecture

The system consists of four specialized agents working in coordination:

### 1. Planner Agent
- **Role**: Strategic research planning
- **Model**: High-capability (GPT-4, Claude)
- **Function**: Analyzes research topics and generates 10 strategic search queries with rationales

### 2. Execute Agent
- **Role**: Web search and content extraction
- **Model**: Cost-effective (GPT-3.5)
- **Function**: Performs parallel web searches, extracts content, and generates concise summaries

### 3. Fact Checker Agent (Optional)
- **Role**: Fact verification and validation
- **Model**: High-capability (GPT-4, Claude)
- **Function**: Extracts factual claims, verifies them against multiple sources, and recursively verifies disputed facts

### 4. Synthesize Agent
- **Role**: Report generation
- **Model**: High-capability (GPT-4, Claude)
- **Function**: Consolidates all information into a comprehensive, well-structured research report

## 🔄 How It Works

### Basic Research Flow

```
Research Topic
    ↓
[Planner Agent] → Generates 10 strategic search queries
    ↓
[Execute Agent] → Performs searches, extracts content, creates summaries
    ↓
[Fact Checker Agent] → Verifies facts, cross-references sources (if enabled)
    ↓
[Synthesize Agent] → Generates comprehensive report with citations
    ↓
Final Research Report
```

### Recursive Fact-Checking Logic

The fact-checking system uses a sophisticated recursive verification process:

#### Step 1: Fact Extraction
- Extracts specific, verifiable factual claims from search summaries
- Filters out vague statements, opinions, and predictions
- Creates `FactClaim` objects with initial metadata

#### Step 2: Initial Verification
- For each fact, generates targeted verification queries
- Searches for sources that confirm or contradict the claim
- Calculates initial confidence score based on:
  - Number of confirming sources
  - Number of contradicting sources
  - Source reliability scores

#### Step 3: Recursive Verification (Multi-Level)
- **Depth 0**: Initial verification from search summaries
- **Depth 1**: If confidence < threshold (default 0.6), generate more targeted queries
- **Depth 2**: If still low confidence, perform deeper verification with specialized queries
- **Max Depth**: Configurable (default: 2 levels)

#### Step 4: Confidence Calculation
The system calculates confidence using multiple factors:

```python
base_confidence = confirmations / (confirmations + contradictions + 1)

# Add bonuses:
source_diversity_bonus = min(0.1, unique_domains * 0.02)
depth_bonus = verification_depth * 0.02
reliability_weight = average_source_reliability

final_confidence = min(1.0, base_confidence + bonuses) * reliability_weight
```

#### Step 5: Cross-Referencing
- Tracks verification history at each depth
- Cross-references sources from different verification rounds
- Identifies consensus across multiple independent sources
- Updates confidence scores incrementally

#### Example Recursive Verification Flow

```
Fact: "The population of Tokyo is 14 million"

Depth 0 (Initial):
  - Query: "Tokyo population 2024"
  - Sources: 3 confirm, 0 contradict
  - Confidence: 0.75

Depth 1 (Recursive - if confidence < 0.6):
  - Query: "Tokyo metropolitan area population official statistics"
  - Sources: 2 confirm, 0 contradict
  - Confidence: 0.85 (improved)

Depth 2 (Recursive - if still < 0.6):
  - Query: "Tokyo population census data Japan government"
  - Sources: 1 confirm, 0 contradict
  - Confidence: 0.90 (further improved)
```

#### Benefits of Recursive Verification

1. **Accuracy**: Multiple verification rounds catch errors and inconsistencies
2. **Confidence Scoring**: Gradual improvement in confidence with each verification round
3. **Source Diversity**: Tracks sources from different domains and verification depths
4. **Dispute Resolution**: Automatically investigates disputed facts more deeply
5. **Transparency**: Maintains verification history for auditability

## 📦 Installation

### Prerequisites

- Python 3.8 or higher
- API keys for at least one LLM provider (OpenAI or Anthropic)

### Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/deep-research.git
cd deep-research
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Configure API Keys

Create a `.env` file in the project root:

```bash
# Required: At least one API key for LLMs
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here

# Optional: For specific search methods
QWEN_API_KEY=your_qwen_key_here          # For Qwen with built-in search
TAVILY_API_KEY=your_tavily_key_here       # For Tavily search
DEEPSEEK_API_KEY=your_deepseek_key_here   # For DeepSeek models
```

### Step 4: Verify Installation

```bash
python test_system.py
```

This will verify that all dependencies are installed and API keys are configured correctly.

## 🚀 Quick Start

### Option 1: Streamlit Web Interface (Recommended)

Launch the web interface:

```bash
streamlit run app.py
```

Then:
1. Open your browser to `http://localhost:8501`
2. Enter your API keys in the sidebar (or use Streamlit secrets)
3. Enter a research topic
4. Click "Start Research"
5. View results with citations and confidence scores

### Option 2: Python API

#### Basic Usage

```python
from deep_research import DeepResearchManager

# Initialize the manager
manager = DeepResearchManager()

# Run complete research process
manager.run("AI applications in education")
```

#### Advanced Usage

```python
from deep_research import DeepResearch, Config

# Create custom configuration
config = Config(
    planner_model="gpt-4-turbo-preview",
    executor_model="gpt-3.5-turbo",
    synthesizer_model="gpt-4-turbo-preview",
    fact_checker_enabled=True,
    fact_checker_max_depth=2,
    fact_checker_confidence_threshold=0.6
)

# Initialize researcher
researcher = DeepResearch(config)

# Conduct research
report = researcher.research(
    "What are the latest developments in quantum computing?",
    save_to_file="quantum_computing_report.md"
)

# Get structured data
structured_data = researcher.research_structured("Your topic")
print(structured_data.short_summary)
print(structured_data.markdown_report)
print(structured_data.follow_up_questions)
```

#### Quick Research (Fewer Queries)

```python
# Quick research with 5 queries (faster, less comprehensive)
quick_report = researcher.quick_research("Climate change solutions", num_queries=5)
```

## ⚙️ Configuration

### Environment Variables

All configuration can be set via environment variables in `.env`:

```bash
# Model Configuration
PLANNER_MODEL=gpt-4-turbo-preview
EXECUTOR_MODEL=gpt-3.5-turbo
SYNTHESIZER_MODEL=gpt-4-turbo-preview
FACT_CHECKER_MODEL=gpt-4-turbo-preview

# Search Configuration
EXECUTOR_SEARCH_METHOD=qwen  # Options: qwen, tavily, duckduckgo

# Temperature Settings
PLANNER_TEMPERATURE=0.7
EXECUTOR_TEMPERATURE=0.3
SYNTHESIZER_TEMPERATURE=0.7

# Fact-Checking Configuration
FACT_CHECKER_ENABLED=true
FACT_CHECKER_MAX_DEPTH=2
FACT_CHECKER_CONFIDENCE_THRESHOLD=0.6
FACT_CHECKER_MAX_VERIFICATION_QUERIES=3
```

### Programmatic Configuration

```python
from deep_research import Config, DeepResearch

config = Config(
    openai_api_key="your_key",
    planner_model="gpt-4-turbo-preview",
    executor_model="gpt-3.5-turbo",
    fact_checker_enabled=True,
    fact_checker_max_depth=2
)

researcher = DeepResearch(config)
```

## 📁 Project Structure

```
deep-research/
├── .streamlit/              # Streamlit configuration
│   ├── config.toml         # Streamlit app config
│   └── secrets.toml        # API keys (git-ignored)
├── deep_research/          # Main package
│   ├── __init__.py
│   ├── config.py           # Configuration management
│   ├── planner.py          # Planner Agent
│   ├── executor.py         # Execute Agent
│   ├── fact_checker.py     # Fact Checker Agent
│   ├── synthesizer.py      # Synthesize Agent
│   ├── orchestrator.py     # DeepResearch orchestrator
│   ├── manager.py          # High-level manager
│   └── system_status.py    # System status checker
├── utils/                  # Frontend utilities
│   ├── config_builder.py   # Config from session state
│   ├── researcher.py      # Research runner wrapper
│   ├── session_manager.py  # Session state management
│   └── ui_components.py    # UI components
├── app.py                  # Streamlit web application
├── example.py              # Example usage script
├── test_system.py          # System verification
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── CONTRIBUTING.md        # Contribution guidelines
└── TODO.md                # Project task tracker
```

## 🔍 Usage Examples

### Example 1: Basic Research

```python
from deep_research import DeepResearchManager

manager = DeepResearchManager()
manager.run("Impact of AI on healthcare")
```

### Example 2: Custom Configuration

```python
from deep_research import DeepResearch, Config

config = Config(
    planner_model="gpt-4-turbo-preview",
    executor_model="gpt-3.5-turbo",
    fact_checker_enabled=True,
    fact_checker_max_depth=3,  # Deeper verification
    fact_checker_confidence_threshold=0.7  # Higher threshold
)

researcher = DeepResearch(config)
report = researcher.research("Quantum computing breakthroughs 2024")
```

### Example 3: Structured Output

```python
from deep_research import DeepResearch

researcher = DeepResearch()
data = researcher.research_structured("Renewable energy trends")

# Access structured components
print("Summary:", data.short_summary)
print("\nFull Report:\n", data.markdown_report)
print("\nFollow-up Questions:")
for q in data.follow_up_questions:
    print(f"  - {q}")
```

## 🧪 Testing

Run the test suite:

```bash
# Test system setup
python test_system.py

# Test individual components
python test_planner.py
python test_executor.py
python test_synthesizer.py
python test_manager.py
```

## 📊 Model Selection Guide

### Cost Optimization Strategy

The system is designed to optimize costs while maintaining quality:

- **Planning & Synthesis**: Use high-capability models (GPT-4, Claude) for complex reasoning
- **Execution**: Use cost-effective models (GPT-3.5) for simpler summarization
- **Fact-Checking**: Use high-capability models for accurate verification

### Recommended Configurations

**Budget-Conscious**:
```python
Config(
    planner_model="gpt-3.5-turbo",
    executor_model="gpt-3.5-turbo",
    synthesizer_model="gpt-3.5-turbo",
    fact_checker_enabled=False  # Disable to save costs
)
```

**Balanced** (Recommended):
```python
Config(
    planner_model="gpt-4-turbo-preview",
    executor_model="gpt-3.5-turbo",
    synthesizer_model="gpt-4-turbo-preview",
    fact_checker_enabled=True
)
```

**Maximum Quality**:
```python
Config(
    planner_model="gpt-4-turbo-preview",
    executor_model="gpt-4-turbo-preview",
    synthesizer_model="gpt-4-turbo-preview",
    fact_checker_enabled=True,
    fact_checker_max_depth=3
)
```

## 🐛 Troubleshooting

### Common Issues

**Issue**: `ValueError: No API key available`
- **Solution**: Ensure at least one API key (OpenAI or Anthropic) is set in `.env`

**Issue**: `ImportError: No module named 'langchain'`
- **Solution**: Run `pip install -r requirements.txt`

**Issue**: Search results are empty
- **Solution**: Check your search method API key (Qwen/Tavily) or use DuckDuckGo (no key required)

**Issue**: Fact-checking is slow
- **Solution**: Reduce `fact_checker_max_depth` or disable fact-checking for faster results

**Issue**: Streamlit app crashes on startup
- **Solution**: Ensure all session state is initialized. Check `utils/session_manager.py`

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on:

- Our multi-agent workflow protocol
- How to propose new features
- Code style and standards
- Testing requirements

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Built with [LangChain](https://www.langchain.com/) for LLM integration
- Uses [Streamlit](https://streamlit.io/) for the web interface
- Search backends: Qwen, Tavily, DuckDuckGo

## 📧 Contact

For questions, issues, or suggestions, please open an issue on GitHub.

---

**Made with ❤️ for researchers and knowledge seekers**
