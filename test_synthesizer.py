"""
Test script for the Synthesize Agent
"""

from deep_research import DeepResearch, Config

def test_synthesizer():
    """Test the synthesize agent with mock search results"""
    print("=" * 60)
    print("Testing Synthesize Agent")
    print("=" * 60)
    
    # Initialize
    try:
        researcher = DeepResearch()
        synthesizer = researcher.synthesizer
        print("✅ Synthesize Agent initialized\n")
    except Exception as e:
        print(f"❌ Error initializing: {e}")
        print("\nMake sure you have API keys configured in .env file")
        return
    
    # Mock search results
    research_topic = "AI applications in education"
    
    mock_search_results = {
        "AI Education Application Scenarios": "AI applications in education include intelligent teaching systems, personalized learning recommendations, and intelligent assessment. These applications analyze student learning behaviors to provide customized learning paths and content recommendations.",
        "AI-Assisted Teaching System Platforms": "AI-assisted teaching system platforms integrate technologies such as natural language processing and machine learning, enabling automatic generation of teaching content, assessment of student assignments, and real-time feedback. These platforms are transforming traditional teaching methods.",
        "Intelligent Educational Robot Applications": "Intelligent educational robots can play a role in classroom teaching, special education, and other fields. They can interact with students and provide personalized learning support, especially suitable for students who need additional attention."
    }
    
    print(f"📋 Research Topic: {research_topic}\n")
    print(f"📊 Mock Search Results: {len(mock_search_results)} summaries\n")
    
    try:
        # Synthesize report
        print("Generating comprehensive report...")
        synthesize_data = synthesizer.synthesize_report(research_topic, mock_search_results)
        
        print("\n" + "=" * 60)
        print("Short Summary:")
        print("=" * 60)
        print(synthesize_data.short_summary)
        
        print("\n" + "=" * 60)
        print("Markdown Report (first 500 chars):")
        print("=" * 60)
        print(synthesize_data.markdown_report[:500] + "...")
        
        print("\n" + "=" * 60)
        print("Follow-up Questions:")
        print("=" * 60)
        for i, question in enumerate(synthesize_data.follow_up_questions, 1):
            print(f"{i}. {question}")
        
        # Check report length
        word_count = len(synthesize_data.markdown_report.split())
        print(f"\n📊 Report Statistics:")
        print(f"   Word count: {word_count}")
        if word_count >= 2000:
            print("   ✅ Report meets minimum 2000 word requirement")
        else:
            print(f"   ⚠️  Report is {2000 - word_count} words short of 2000 word requirement")
        
        # Format and display
        print("\n" + "=" * 60)
        print("Formatted Report (first 800 chars):")
        print("=" * 60)
        formatted = synthesizer.format_report(synthesize_data, research_topic)
        print(formatted[:800] + "...")
        
        print("\n✅ Synthesize Agent test complete!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_synthesizer()
