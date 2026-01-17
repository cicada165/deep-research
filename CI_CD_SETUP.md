# CI/CD and Environment Setup

This document describes the automated environment setup and CI/CD pipeline for the Deep Research project.

## Environment Setup

### Requirements File

The `requirements.txt` file contains all dependencies organized by category:

- **Core LLM Dependencies**: OpenAI, Anthropic
- **LangChain Dependencies**: LangChain and related packages
- **Web Search**: DuckDuckGo, BeautifulSoup, requests, httpx
- **Data Validation**: Pydantic, pydantic-settings
- **Streamlit Frontend**: Streamlit
- **Utilities**: tqdm, markdown

### Installation

```bash
pip install -r requirements.txt
```

## GitHub Actions CI/CD

### Workflow: `streamlit-tests.yml`

Location: `.github/workflows/streamlit-tests.yml`

**Triggers:**
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop` branches

**Test Matrix:**
- Python versions: 3.9, 3.10, 3.11
- Runs on: Ubuntu Latest

**Test Steps:**

1. **Checkout code** - Clones the repository
2. **Set up Python** - Installs specified Python version with pip caching
3. **Install dependencies** - Installs all packages from `requirements.txt`
4. **Verify imports** - Tests that all modules can be imported
5. **Run syntax checks** - Validates Python syntax for all files
6. **Test secret masking** - Verifies secret masking utility works
7. **Test configuration validation** - Tests config building and validation
8. **Test session manager** - Validates session management
9. **Check for secret leaks** - Scans for potential hardcoded API keys
10. **Lint check** - Basic linting validation

### Smoke Tests

The workflow runs "smoke tests" that verify:

- ✅ All imports work correctly
- ✅ Python files compile without syntax errors
- ✅ Secret masking functions correctly
- ✅ Configuration validation works
- ✅ Session management is functional
- ✅ No obvious hardcoded secrets in code

### Running Tests Locally

You can run the same tests locally:

```bash
# Install dependencies
pip install -r requirements.txt

# Test imports
python -c "from deep_research import DeepResearch, Config; from utils.secret_masker import mask_secrets; print('✅ Imports work')"

# Test syntax
python -m py_compile app.py utils/*.py deep_research/*.py

# Test secret masking
python -c "from utils.secret_masker import mask_secrets; assert 'MASKED' in mask_secrets('sk-test1234567890'); print('✅ Masking works')"
```

## Secret Masking

See [SECRET_MASKING.md](SECRET_MASKING.md) for detailed documentation on the secret masking utility.

### Quick Usage

```python
from utils.secret_masker import mask_secrets, safe_print

# Mask API keys in strings
api_key = "sk-1234567890abcdefghijklmnopqrstuvwxyz"
masked = mask_secrets(api_key)  # "sk-***MASKED***"

# Safe printing
safe_print("API Key:", api_key)  # Automatically masks secrets
```

## Workflow Status

The workflow will show:
- ✅ Green checkmark if all tests pass
- ❌ Red X if any test fails
- ⚠️ Yellow warning for non-critical issues

## Continuous Integration Benefits

1. **Early Error Detection** - Catches import errors, syntax issues before deployment
2. **Multi-Version Testing** - Ensures compatibility across Python versions
3. **Secret Leak Prevention** - Automatically scans for hardcoded API keys
4. **Import Validation** - Verifies all dependencies are correctly specified
5. **Configuration Testing** - Validates config building and validation logic

## Troubleshooting

### Workflow Fails on Import

- Check that all dependencies are in `requirements.txt`
- Verify Python version compatibility
- Check for circular imports

### Secret Leak Detection Fails

- Review the grep pattern in the workflow
- Ensure test files use `MASKED` in their test strings
- Check that actual API keys aren't hardcoded

### Syntax Check Fails

- Run `python -m py_compile <file>` locally to see the exact error
- Check for Python version-specific syntax issues

## Next Steps

1. **Add more comprehensive tests** - Unit tests, integration tests
2. **Add code coverage** - Track test coverage
3. **Add deployment automation** - Auto-deploy on successful tests
4. **Add performance tests** - Benchmark research execution time
