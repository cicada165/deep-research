"""
Test script for DeepResearchManager
"""

from deep_research import DeepResearchManager

def main():
    """Test the DeepResearchManager"""
    print("=" * 60)
    print("Testing DeepResearchManager")
    print("=" * 60)
    
    # Initialize manager
    try:
        manager = DeepResearchManager()
    except Exception as e:
        print(f"❌ Error initializing: {e}")
        print("\nMake sure you have API keys configured in .env file")
        return
    
    # Test query
    test_query = "AI applications in education"
    
    print(f"\n🔍 Test Query: {test_query}\n")
    
    try:
        # Run the full research process
        manager.run(test_query, save_to_file=True)
        
        print("\n✅ DeepResearchManager test complete!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
