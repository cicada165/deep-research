"""
Simple test script to verify the system is set up correctly
"""

import sys
import os

def test_imports():
    """Test that all modules can be imported"""
    print("Testing imports...")
    try:
        from deep_research import DeepResearch, Config
        print("✅ All imports successful")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_config():
    """Test configuration loading"""
    print("\nTesting configuration...")
    try:
        from deep_research import Config
        config = Config()
        print(f"✅ Config loaded")
        print(f"   Planner model: {config.planner_model}")
        print(f"   Executor model: {config.executor_model}")
        print(f"   Synthesizer model: {config.synthesizer_model}")
        
        # Check API keys
        has_openai = bool(config.openai_api_key)
        has_anthropic = bool(config.anthropic_api_key)
        
        if has_openai or has_anthropic:
            print(f"✅ API keys configured (OpenAI: {has_openai}, Anthropic: {has_anthropic})")
        else:
            print("⚠️  No API keys found. Please set OPENAI_API_KEY or ANTHROPIC_API_KEY in .env file")
        
        return True
    except Exception as e:
        print(f"❌ Config error: {e}")
        return False

def test_agent_initialization():
    """Test that agents can be initialized"""
    print("\nTesting agent initialization...")
    try:
        from deep_research import DeepResearch, Config
        config = Config()
        
        # Check if we have at least one API key
        if not config.openai_api_key and not config.anthropic_api_key:
            print("⚠️  Skipping agent initialization test (no API keys)")
            return True
        
        researcher = DeepResearch(config)
        print("✅ All agents initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Agent initialization error: {e}")
        return False

def main():
    print("=" * 60)
    print("Deep Research System - Setup Test")
    print("=" * 60)
    
    results = []
    results.append(test_imports())
    results.append(test_config())
    results.append(test_agent_initialization())
    
    print("\n" + "=" * 60)
    if all(results):
        print("✅ All tests passed! System is ready to use.")
        print("\nNext steps:")
        print("1. Make sure your .env file has API keys configured")
        print("2. Run: python example.py")
    else:
        print("❌ Some tests failed. Please check the errors above.")
    print("=" * 60)

if __name__ == "__main__":
    main()
