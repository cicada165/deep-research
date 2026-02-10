"""
Test script for the Planning Agent
"""

from deep_research import DeepResearch, Config

def test_planner():
    """Test the planning agent"""
    print("=" * 60)
    print("Testing Planning Agent")
    print("=" * 60)
    
    # Initialize
    try:
        researcher = DeepResearch()
        planner = researcher.planner
    except Exception as e:
        print(f"❌ Error initializing: {e}")
        print("\nMake sure you have API keys configured in .env file")
        return
    
    # Test topic
    topic = "AI applications in education"
    
    print(f"\n📋 Research Topic: {topic}\n")
    
    # Generate plan
    print("Generating research plan...")
    try:
        plan = planner.create_research_plan(topic)
        
        print(f"\n✅ Generated {len(plan.searches)} search queries:\n")
        
        # Display all search items
        for i, search_item in enumerate(plan.searches, 1):
            print(f"{i}. Query: {search_item.query}")
            print(f"   Reason: {search_item.reason}")
            print()
        
        # Test getting just queries
        print("\n" + "=" * 60)
        print("Extracting queries only:")
        print("=" * 60)
        queries = planner.get_search_queries(topic)
        for i, query in enumerate(queries, 1):
            print(f"{i}. {query}")
        
        print("\n✅ Planning Agent test complete!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_planner()
