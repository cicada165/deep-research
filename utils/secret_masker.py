"""
Secret masking utility to prevent API key leaks in logs and terminal output
"""

import re
from typing import Optional, Union, List, Dict, Any


class SecretMasker:
    """
    Utility class to mask sensitive information (API keys, tokens, etc.) in strings
    """
    
    # Common API key patterns
    API_KEY_PATTERNS = [
        # OpenAI: sk-... (starts with sk-)
        (r'sk-[a-zA-Z0-9]{32,}', 'sk-***MASKED***'),
        # Anthropic: sk-ant-... (starts with sk-ant-)
        (r'sk-ant-[a-zA-Z0-9-]{32,}', 'sk-ant-***MASKED***'),
        # Generic API keys (alphanumeric, 20+ chars)
        (r'[a-zA-Z0-9]{20,}', lambda m: m.group(0)[:4] + '***MASKED***' if len(m.group(0)) >= 20 else m.group(0)),
        # Tavily API keys (tvly-...)
        (r'tvly-[a-zA-Z0-9]{20,}', 'tvly-***MASKED***'),
        # Bearer tokens
        (r'Bearer\s+[a-zA-Z0-9_-]{20,}', 'Bearer ***MASKED***'),
        # Authorization headers
        (r'Authorization:\s*[^\s]+', 'Authorization: ***MASKED***'),
    ]
    
    # Known API key prefixes to mask
    KNOWN_PREFIXES = [
        'sk-',
        'sk-ant-',
        'tvly-',
        'Bearer ',
    ]
    
    def __init__(self, custom_patterns: Optional[List[tuple]] = None):
        """
        Initialize SecretMasker
        
        Args:
            custom_patterns: Optional list of (pattern, replacement) tuples
        """
        self.patterns = self.API_KEY_PATTERNS.copy()
        if custom_patterns:
            self.patterns.extend(custom_patterns)
    
    def mask_string(self, text: str, mask_char: str = '*', show_first: int = 4, show_last: int = 0) -> str:
        """
        Mask sensitive information in a string
        
        Args:
            text: Input string that may contain secrets
            mask_char: Character to use for masking
            show_first: Number of characters to show at the start (default: 4)
            show_last: Number of characters to show at the end (default: 0)
            
        Returns:
            String with secrets masked
        """
        if not text or not isinstance(text, str):
            return text
        
        masked_text = text
        
        # Apply each pattern
        for pattern, replacement in self.patterns:
            if callable(replacement):
                # Replacement is a function
                masked_text = re.sub(pattern, replacement, masked_text)
            else:
                # Replacement is a string
                masked_text = re.sub(pattern, replacement, masked_text, flags=re.IGNORECASE)
        
        return masked_text
    
    def mask_dict(self, data: Dict[str, Any], keys_to_mask: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Mask sensitive values in a dictionary
        
        Args:
            data: Dictionary that may contain secrets
            keys_to_mask: List of keys to always mask (default: common API key keys)
            
        Returns:
            Dictionary with secrets masked
        """
        if keys_to_mask is None:
            keys_to_mask = [
                'api_key', 'apikey', 'api-key',
                'openai_api_key', 'anthropic_api_key', 'qwen_api_key',
                'tavily_api_key', 'deepseek_api_key',
                'token', 'access_token', 'secret', 'password',
                'authorization', 'auth',
            ]
        
        masked_data = {}
        for key, value in data.items():
            # Check if key should be masked
            key_lower = key.lower()
            should_mask = any(mask_key in key_lower for mask_key in keys_to_mask)
            
            if should_mask and isinstance(value, str) and value:
                masked_data[key] = self.mask_string(value)
            elif isinstance(value, dict):
                masked_data[key] = self.mask_dict(value, keys_to_mask)
            elif isinstance(value, list):
                masked_data[key] = [self.mask_dict(item, keys_to_mask) if isinstance(item, dict) 
                                   else self.mask_string(item) if isinstance(item, str) else item 
                                   for item in value]
            else:
                masked_data[key] = value
        
        return masked_data
    
    def mask_config(self, config: Any) -> Any:
        """
        Mask API keys in a Config object
        
        Args:
            config: Config object or dict with API keys
            
        Returns:
            Config object or dict with masked API keys
        """
        if hasattr(config, '__dict__'):
            # It's an object, convert to dict
            config_dict = {k: v for k, v in config.__dict__.items() if not k.startswith('_')}
            masked_dict = self.mask_dict(config_dict)
            # Create a new object with masked values (if possible)
            if hasattr(config, '__class__'):
                masked_config = type(config)(**masked_dict)
                return masked_config
            return masked_dict
        elif isinstance(config, dict):
            return self.mask_dict(config)
        else:
            return config


# Global instance for convenience
_default_masker = SecretMasker()


def mask_secrets(text: Union[str, Dict, Any], **kwargs) -> Union[str, Dict, Any]:
    """
    Convenience function to mask secrets in text or objects
    
    Args:
        text: String, dict, or object containing potential secrets
        **kwargs: Additional arguments passed to mask_string or mask_dict
        
    Returns:
        Masked version of input
    """
    if isinstance(text, str):
        return _default_masker.mask_string(text, **kwargs)
    elif isinstance(text, dict):
        return _default_masker.mask_dict(text, **kwargs)
    else:
        return _default_masker.mask_config(text)


def safe_print(*args, **kwargs):
    """
    Print function that automatically masks secrets
    
    Usage:
        safe_print("API key:", api_key)  # Will mask the API key
    """
    import sys
    
    # Mask all string arguments
    masked_args = [mask_secrets(arg) if isinstance(arg, str) else arg for arg in args]
    
    # Print using original print function
    print(*masked_args, **kwargs)


def safe_log(message: str, level: str = "INFO"):
    """
    Safe logging function that masks secrets
    
    Args:
        message: Log message
        level: Log level (INFO, WARNING, ERROR, etc.)
    """
    masked_message = mask_secrets(message)
    print(f"[{level}] {masked_message}")
