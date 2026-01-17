"""
Test script for the Execute Agent
"""

from deep_research import DeepResearch, Config

def test_executor():
    """Test the execute agent"""
    print("=" * 60)
    print("Testing Execute Agent")
    print("=" * 60)
    
    # Initialize
    try:
        researcher = DeepResearch()
        executor = researcher.executor
        print(f"✅ Execute Agent initialized")
        print(f"   Search method: {executor.search_method}\n")
    except Exception as e:
        print(f"❌ Error initializing: {e}")
        print("\nMake sure you have API keys configured in .env file")
        return
    
    # Test search query
    test_query = "AI education policy and development trends"
    
    print(f"🔍 Testing search query: {test_query}\n")
    
    try:
        # Execute search
        summary = executor.execute_search(test_query)
        
        print("=" * 60)
        print("Search Summary:")
        print("=" * 60)
        print(summary)
        print("\n" + "=" * 60)
        
        # Check summary length
        word_count = len(summary.split())
        print(f"\nSummary length: {word_count} words")
        if word_count > 500:
            print("⚠️  Warning: Summary exceeds 500 words")
        else:
            print("✅ Summary within 500 word limit")
        
        print("\n✅ Execute Agent test complete!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

def test_multiple_queries():
    """Test executing multiple queries"""
    print("\n" + "=" * 60)
    print("Testing Multiple Queries")
    print("=" * 60)
    
    try:
        researcher = DeepResearch()
        executor = researcher.executor
        
        queries = [
            "AI applications in education",
            "Intelligent educational robots",
            "Personalized learning recommendation systems"
        ]
        
        print(f"Executing {len(queries)} queries...\n")
        results = executor.execute_search_queries(queries)
        
        print("\n" + "=" * 60)
        print("Results:")
        print("=" * 60)
        for query, summary in results.items():
            print(f"\nQuery: {query}")
            print(f"Summary: {summary[:200]}...")
        
        print("\n✅ Multiple queries test complete!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_executor()
    # Uncomment to test multiple queries
    # test_multiple_queries()
