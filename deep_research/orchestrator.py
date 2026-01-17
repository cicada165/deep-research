"""
Main Orchestrator - Coordinates all three agents
"""

from typing import Optional, TYPE_CHECKING
from .config import Config
from .planner import PlannerAgent
from .executor import ExecuteAgent
from .synthesizer import SynthesizeAgent

if TYPE_CHECKING:
    from .synthesizer import SynthesizeData


class DeepResearch:
    """Main class that orchestrates the Deep Research system"""
    
    def __init__(self, config: Optional[Config] = None):
        """
        Initialize the Deep Research system
        
        Args:
            config: Optional Config object. If None, uses default config.
        """
        self.config = config or Config()
        
        # Initialize all agents
        self.planner = PlannerAgent(self.config)
        self.executor = ExecuteAgent(self.config)
        self.synthesizer = SynthesizeAgent(self.config)
    
    def research(self, topic: str, save_to_file: Optional[str] = None) -> str:
        """
        Conduct comprehensive research on a topic
        
        Args:
            topic: The research topic
            save_to_file: Optional file path to save the report
            
        Returns:
            The final research report
        """
        print(f"🔍 Starting research on: {topic}\n")
        
        # Step 1: Planning - Generate research plan and queries
        print("📋 Step 1: Planning research strategy...")
        plan = self.planner.create_research_plan(topic)
        print(f"   Generated {len(plan.searches)} search queries")
        
        # Display first few queries with reasons
        for i, search_item in enumerate(plan.searches[:3], 1):
            print(f"   {i}. {search_item.query} - {search_item.reason[:60]}...")
        if len(plan.searches) > 3:
            print(f"   ... and {len(plan.searches) - 3} more queries\n")
        else:
            print()
        
        queries = [item.query for item in plan.searches]
        
        # Step 2: Execution - Perform searches and summarize
        print("🔎 Step 2: Executing searches and summarizing content...")
        search_results = self.executor.execute_search_queries(queries)
        
        print(f"   Completed {len(search_results)} search queries\n")
        
        # Step 2.5: Fact-Checking (if enabled)
        if self.config.fact_checker_enabled:
            print("🔍 Step 2.5: Fact-checking and verification...")
            from .fact_checker import FactCheckerAgent
            fact_checker = FactCheckerAgent(self.config)
            search_results = fact_checker.fact_check_summaries(search_results)
            print(f"   Verified facts with confidence scores\n")
        
        # Step 3: Synthesis - Generate final report
        print("📝 Step 3: Synthesizing final report...")
        synthesize_data = self.synthesizer.synthesize_report(topic, search_results)
        formatted_report = self.synthesizer.format_report(synthesize_data, topic)
        
        # Display summary
        word_count = len(synthesize_data.markdown_report.split())
        print(f"   Generated report: {word_count} words")
        print(f"   Follow-up questions: {len(synthesize_data.follow_up_questions)}\n")
        
        print("✅ Research complete!\n")
        
        # Save to file if requested
        if save_to_file:
            with open(save_to_file, 'w', encoding='utf-8') as f:
                f.write(formatted_report)
            print(f"📄 Report saved to: {save_to_file}\n")
        
        return formatted_report
    
    def quick_research(self, topic: str, num_queries: int = 5) -> str:
        """
        Conduct a quicker research with fewer queries
        
        Args:
            topic: The research topic
            num_queries: Number of search queries to use
            
        Returns:
            The final research report
        """
        print(f"⚡ Quick research on: {topic}\n")
        
        # Get queries from planner
        all_queries = self.planner.get_search_queries(topic)
        queries = all_queries[:num_queries]
        
        print(f"📋 Using {len(queries)} search queries\n")
        
        # Execute searches
        print("🔎 Executing searches...")
        search_results = self.executor.execute_search_queries(queries)
        
        # Fact-Checking (if enabled)
        if self.config.fact_checker_enabled:
            print("🔍 Fact-checking and verification...")
            from .fact_checker import FactCheckerAgent
            fact_checker = FactCheckerAgent(self.config)
            search_results = fact_checker.fact_check_summaries(search_results)
        
        # Synthesize report
        print("📝 Synthesizing report...")
        synthesize_data = self.synthesizer.synthesize_report(topic, search_results)
        formatted_report = self.synthesizer.format_report(synthesize_data, topic)
        
        print("✅ Quick research complete!\n")
        
        return formatted_report
    
    def research_structured(self, topic: str):
        """
        Conduct research and return structured data instead of formatted string
        
        Args:
            topic: The research topic
            
        Returns:
            SynthesizeData with short_summary, markdown_report, and follow_up_questions
        """
        print(f"🔍 Starting research on: {topic}\n")
        
        # Step 1: Planning
        print("📋 Step 1: Planning research strategy...")
        plan = self.planner.create_research_plan(topic)
        queries = [item.query for item in plan.searches]
        print(f"   Generated {len(queries)} search queries\n")
        
        # Step 2: Execution
        print("🔎 Step 2: Executing searches...")
        search_results = self.executor.execute_search_queries(queries)
        print(f"   Completed {len(search_results)} search queries\n")
        
        # Step 2.5: Fact-Checking (if enabled)
        if self.config.fact_checker_enabled:
            print("🔍 Step 2.5: Fact-checking and verification...")
            from .fact_checker import FactCheckerAgent
            fact_checker = FactCheckerAgent(self.config)
            search_results = fact_checker.fact_check_summaries(search_results)
            print(f"   Verified facts with confidence scores\n")
        
        # Step 3: Synthesis
        print("📝 Step 3: Synthesizing final report...")
        synthesize_data = self.synthesizer.synthesize_report(topic, search_results)
        
        print("✅ Research complete!\n")
        
        return synthesize_data
