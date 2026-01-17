"""
Example usage of Deep Research system
"""

from deep_research import DeepResearch, DeepResearchManager

def example_manager():
    """Example using DeepResearchManager (simplest interface)"""
    print("=" * 60)
    print("Example 1: Using DeepResearchManager")
    print("=" * 60)
    
    # Initialize the manager
    manager = DeepResearchManager()
    
    # Run complete research process
    # This will: plan -> search -> synthesize -> display -> save
    manager.run("AI applications in education")

def example_direct():
    """Example using DeepResearch (more control)"""
    print("\n" + "=" * 60)
    print("Example 2: Using DeepResearch (More Control)")
    print("=" * 60)
    
    # Initialize the research system
    researcher = DeepResearch()
    
    # Conduct full research
    topic = "Latest developments in quantum computing in 2024"
    report = researcher.research(topic, save_to_file="report_quantum_computing.md")
    print(report[:500] + "...\n")  # Print first 500 chars

def example_structured():
    """Example getting structured data"""
    print("\n" + "=" * 60)
    print("Example 3: Getting Structured Data")
    print("=" * 60)
    
    researcher = DeepResearch()
    
    # Get structured data
    structured_data = researcher.research_structured("Impact of AI on healthcare")
    
    print("Short Summary:")
    print(structured_data.short_summary)
    print("\nFollow-up Questions:")
    for i, q in enumerate(structured_data.follow_up_questions, 1):
        print(f"{i}. {q}")

if __name__ == "__main__":
    # Uncomment the example you want to run
    # example_manager()      # Simplest interface
    # example_direct()       # More control
    example_structured()     # Get structured data
