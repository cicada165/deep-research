# Secret Masking Utility

This document describes the secret masking utility that prevents accidental API key leaks in logs and terminal output.

## Overview

The `utils.secret_masker` module provides automatic masking of sensitive information (API keys, tokens, etc.) to prevent accidental exposure during research demos, logging, or debugging.

## Usage

### Basic Usage

```python
from utils.secret_masker import mask_secrets

# Mask a string containing an API key
api_key = "sk-1234567890abcdefghijklmnopqrstuvwxyz"
masked = mask_secrets(api_key)
# Result: "sk-***MASKED***"
```

### Masking Dictionaries

```python
from utils.secret_masker import mask_secrets

config_dict = {
    "openai_api_key": "sk-test123",
    "other_data": "safe information"
}

masked_dict = mask_secrets(config_dict)
# Result: {
#     "openai_api_key": "sk-t***MASKED***",
#     "other_data": "safe information"
# }
```

### Safe Print Function

```python
from utils.secret_masker import safe_print

api_key = "sk-1234567890abcdefghijklmnopqrstuvwxyz"
safe_print("API Key:", api_key)
# Output: API Key: sk-***MASKED***
```

### Safe Logging

```python
from utils.secret_masker import safe_log

safe_log("Using API key: sk-1234567890abcdefghijklmnopqrstuvwxyz", "INFO")
# Output: [INFO] Using API key: sk-***MASKED***
```

## Supported Patterns

The secret masker automatically detects and masks:

- **OpenAI API keys**: `sk-...` (32+ characters)
- **Anthropic API keys**: `sk-ant-...` (32+ characters)
- **Tavily API keys**: `tvly-...` (20+ characters)
- **Bearer tokens**: `Bearer ...` (20+ characters)
- **Authorization headers**: `Authorization: ...`
- **Generic API keys**: Alphanumeric strings 20+ characters

## Integration

The secret masker is integrated into:

- `test_script.py` - Test output masking
- `deep_research/system_status.py` - Status report masking
- `utils/__init__.py` - Available as utility import

## Best Practices

1. **Always use `mask_secrets()`** when printing or logging configuration objects
2. **Use `safe_print()`** instead of `print()` for output that might contain secrets
3. **Never log raw API keys** - always mask them first
4. **Check error messages** - ensure exceptions don't expose API keys

## Example: Masking Config Objects

```python
from deep_research import Config
from utils.secret_masker import mask_secrets

config = Config()
# Mask the entire config object
masked_config = mask_secrets(config)
print(f"Config: {masked_config}")
```

## Custom Patterns

You can add custom patterns:

```python
from utils.secret_masker import SecretMasker

custom_masker = SecretMasker(custom_patterns=[
    (r'my-custom-key-\d+', 'my-custom-key-***MASKED***')
])

masked = custom_masker.mask_string("my-custom-key-12345")
```

## GitHub Actions Integration

The CI/CD workflow automatically checks for potential secret leaks:

```yaml
- name: Check for potential secret leaks
  run: |
    if grep -r "sk-[a-zA-Z0-9]\{32,\}" --include="*.py" . | grep -v "MASKED"; then
      echo "⚠️  Warning: Potential hardcoded API keys found"
      exit 1
    fi
```

## Security Notes

- Secret masking is a **prevention tool**, not a security solution
- Never commit API keys to version control
- Use environment variables or secrets management for production
- The masker helps prevent **accidental** leaks, not intentional exposure
