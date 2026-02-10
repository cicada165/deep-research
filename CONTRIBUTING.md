# Contributing to Deep Research

Thank you for your interest in contributing to Deep Research! This document explains our multi-agent workflow protocol and how to contribute effectively.

## 🤖 Multi-Agent Workflow Protocol

Deep Research uses a specialized multi-agent workflow to ensure quality, maintainability, and clear separation of concerns. Understanding this workflow is essential for contributing.

### The Command Chain

Our workflow follows a strict command chain with specialized roles:

```
ORCHESTRATOR → ARCHITECT → CODER → REVIEWER → DEBUGGER
```

### Agent Roles

#### 1. **ORCHESTRATOR** (Project Manager)
- **Always the entry point** for new features or tasks
- Breaks down research goals into actionable tasks in `TODO.md`
- Delegates to appropriate agents
- Does NOT write code

**Responsibilities:**
- Create and maintain `TODO.md`
- Break down complex tasks into phases
- Assign tasks to appropriate agents
- Track progress and coordinate workflow

**When to use:** Starting any new feature, bug fix, or improvement

#### 2. **ARCHITECT** (System Designer)
- Defines data flow and system structure
- Creates technical specifications
- Designs APIs and integration points
- Updates documentation

**Responsibilities:**
- Design system architecture
- Define data models and interfaces
- Create technical specifications (SPECS.md)
- Plan integration points
- Update README.md and documentation

**When to use:** Before implementing new features, when designing APIs, when planning major changes

#### 3. **CODER** (Implementation)
- Writes Python code
- Implements features according to specifications
- Follows code style guidelines
- Writes unit tests

**Responsibilities:**
- Implement features from specifications
- Write clean, documented code
- Follow existing code patterns
- Write tests for new code
- Update code comments and docstrings

**When to use:** After architecture is defined, when implementing features

#### 4. **REVIEWER** (Quality Assurance)
- Audits code for quality and correctness
- Verifies implementation matches specifications
- Checks for security issues
- Validates test coverage

**Responsibilities:**
- Review code for bugs and issues
- Verify code matches specifications
- Check security and best practices
- Validate test coverage
- Create audit reports

**When to use:** After code is written, before merging

#### 5. **DEBUGGER** (Problem Solver)
- **Only active when issues arise**
- Fixes bugs found by Reviewer
- Resolves terminal command failures
- Troubleshoots runtime errors

**Responsibilities:**
- Fix bugs and errors
- Resolve test failures
- Debug runtime issues
- Apply hotfixes when needed

**When to use:** Only when bugs are found or tests fail

### Workflow Example

Here's how a new feature flows through the system:

```
1. ORCHESTRATOR: "Add citation export feature"
   → Creates task in TODO.md
   → Delegates to @Architect

2. ARCHITECT: Designs citation export system
   → Creates SPECS.md with technical design
   → Defines data models and APIs
   → Updates TODO.md: "Ready for @Coder"

3. CODER: Implements citation export
   → Writes code according to SPECS.md
   → Adds tests
   → Updates TODO.md: "Ready for @Reviewer"

4. REVIEWER: Audits implementation
   → Reviews code quality
   → Tests functionality
   → Creates audit report
   → Updates TODO.md: "✅ Approved" or "⚠️ Issues found"

5. If issues found → DEBUGGER fixes them
   → Resolves bugs
   → Updates TODO.md: "✅ Fixed"
```

## 📋 Contribution Workflow

### Step 1: Check TODO.md

**Always start by reading `TODO.md`** to understand:
- Current project status
- Active tasks
- Which agent should handle your contribution

### Step 2: Identify Your Role

Based on what you want to contribute:

- **New Feature Idea** → Start as ORCHESTRATOR
- **Architecture/Design** → Work as ARCHITECT
- **Code Implementation** → Work as CODER
- **Code Review** → Work as REVIEWER
- **Bug Fix** → Work as DEBUGGER

### Step 3: Follow the Protocol

1. **If you're ORCHESTRATOR:**
   - Add task to `TODO.md`
   - Break it into phases
   - Delegate to appropriate agent: "@[Agent Name], your turn to [Task]"

2. **If you're ARCHITECT:**
   - Read existing SPECS.md and architecture docs
   - Design your feature
   - Create/update SPECS.md
   - Update TODO.md: "Ready for @Coder"

3. **If you're CODER:**
   - Read SPECS.md for your feature
   - Implement according to specifications
   - Write tests
   - Update TODO.md: "Ready for @Reviewer"

4. **If you're REVIEWER:**
   - Review code against specifications
   - Test functionality
   - Create audit report
   - Update TODO.md with findings

5. **If you're DEBUGGER:**
   - Fix identified issues
   - Verify fixes work
   - Update TODO.md: "✅ Fixed"

### Step 4: Update TODO.md

**Always update `TODO.md`** to reflect:
- Task status (pending, in_progress, completed)
- Which agent is currently working
- Any blockers or issues

## 🎯 How to Contribute

### Reporting Bugs

1. Check if the bug is already in `TODO.md`
2. If not, add it under "Current Tasks" or "Bug Reports"
3. Tag as `@Debugger` if it's a critical bug
4. Include:
   - Description of the bug
   - Steps to reproduce
   - Expected vs actual behavior
   - Error messages (if any)

### Proposing New Features

1. **Start as ORCHESTRATOR:**
   - Add feature to `TODO.md`
   - Break down into phases
   - Delegate to @Architect

2. **ARCHITECT designs it:**
   - Creates technical specifications
   - Updates SPECS.md
   - Defines integration points

3. **CODER implements it:**
   - Follows SPECS.md
   - Writes code and tests
   - Updates TODO.md

4. **REVIEWER validates it:**
   - Reviews code
   - Tests functionality
   - Approves or requests changes

### Improving Documentation

1. Read existing documentation
2. Identify gaps or outdated information
3. Update relevant files:
   - `README.md` for user-facing docs
   - `SPECS.md` for technical specs
   - Code docstrings for API docs
4. Update TODO.md: "Documentation updated"

### Code Style

Follow these guidelines:

- **Python Style**: Follow PEP 8
- **Type Hints**: Use type hints for function parameters and returns
- **Docstrings**: Use Google-style docstrings
- **Imports**: Group imports (stdlib, third-party, local)
- **Naming**: Use descriptive names, follow existing conventions

Example:

```python
from typing import Optional, Dict, List
from deep_research.config import Config

def process_research_topic(
    topic: str,
    config: Optional[Config] = None
) -> Dict[str, str]:
    """
    Process a research topic and return search results.
    
    Args:
        topic: The research topic to process
        config: Optional configuration object
        
    Returns:
        Dictionary mapping queries to summaries
    """
    # Implementation
    pass
```

## 🧪 Testing Requirements

### Before Submitting

1. **Run existing tests:**
   ```bash
   python test_system.py
   python test_planner.py
   python test_executor.py
   python test_synthesizer.py
   ```

2. **Write tests for new features:**
   - Unit tests for individual functions
   - Integration tests for workflows
   - Test edge cases and error handling

3. **Ensure all tests pass:**
   - No test failures
   - No linter errors
   - Code coverage maintained

### Test Structure

```python
# test_new_feature.py
import unittest
from deep_research.new_feature import NewFeature

class TestNewFeature(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures"""
        pass
    
    def test_basic_functionality(self):
        """Test basic feature functionality"""
        pass
    
    def test_edge_cases(self):
        """Test edge cases"""
        pass
```

## 📝 Commit Messages

Use clear, descriptive commit messages:

**Good:**
```
Add recursive fact-checking depth tracking

- Implement depth counter in FactCheckerAgent
- Track verification history at each depth
- Update confidence calculation with depth bonus
```

**Bad:**
```
fix stuff
```

## 🔒 Security Guidelines

### Never Commit

- API keys or secrets
- `.env` files
- `.env.github` files
- `.streamlit/secrets.toml` (if it contains keys)
- Hardcoded credentials

### Always

- Use environment variables for secrets
- Check `.gitignore` includes sensitive files
- Use placeholder values in examples
- Document security considerations in code

## 🚀 Pull Request Process

1. **Fork the repository**

2. **Create a feature branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes:**
   - Follow the multi-agent workflow
   - Update TODO.md
   - Write tests
   - Update documentation

4. **Test your changes:**
   ```bash
   python test_system.py
   # Run relevant tests
   ```

5. **Update TODO.md:**
   - Mark your task as completed
   - Note any issues or follow-ups

6. **Commit and push:**
   ```bash
   git commit -m "Descriptive commit message"
   git push origin feature/your-feature-name
   ```

7. **Create Pull Request:**
   - Reference TODO.md task
   - Describe changes
   - Link to SPECS.md if applicable
   - Note which agent role you're fulfilling

## 📚 Understanding the Codebase

### Key Files

- **`TODO.md`**: Current tasks and status
- **`SPECS.md`**: Technical specifications
- **`README.md`**: User documentation
- **`.cursorrules`**: Multi-agent workflow protocol

### Key Directories

- **`deep_research/`**: Core package
  - `orchestrator.py`: Main coordination
  - `planner.py`: Planning agent
  - `executor.py`: Execution agent
  - `fact_checker.py`: Fact-checking agent
  - `synthesizer.py`: Synthesis agent

- **`utils/`**: Frontend utilities
  - `researcher.py`: Research runner wrapper
  - `session_manager.py`: Session state management
  - `config_builder.py`: Config building

- **`app.py`**: Streamlit web interface

## 🎓 Learning Resources

### For New Contributors

1. **Read these files first:**
   - `README.md` - Understand the project
   - `TODO.md` - See current status
   - `SPECS.md` - Understand architecture
   - `.cursorrules` - Understand workflow

2. **Run the examples:**
   ```bash
   python example.py
   streamlit run app.py
   ```

3. **Study existing code:**
   - Start with `orchestrator.py` to understand flow
   - Look at agent implementations
   - Review test files

4. **Start small:**
   - Fix a small bug
   - Improve documentation
   - Add a test case

## ❓ Questions?

- Check `TODO.md` for current tasks
- Review existing issues and PRs
- Ask in discussions or issues
- Read the code comments and docstrings

## 🙏 Thank You!

Your contributions make Deep Research better for everyone. Whether you're fixing bugs, adding features, improving docs, or reviewing code, your work is appreciated!

Remember: **Always refer to TODO.md and follow the multi-agent workflow protocol.**

---

**Happy Contributing! 🚀**
