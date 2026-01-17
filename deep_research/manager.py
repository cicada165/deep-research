"""
DeepResearchManager - High-level manager for the Deep Research system
Provides a clean interface for orchestrating research workflows
"""

import os
from typing import List, Optional, Tuple
from .config import Config
from .planner import PlannerAgent, WebSearchPlan
from .executor import ExecuteAgent
from .synthesizer import SynthesizeAgent, SynthesizeData


class DeepResearchManager:
    """
    Manager class for the Deep Research system.
    
    This class orchestrates the entire research process:
    1. Generate search plan based on user query
    2. Perform web searches based on the plan
    3. Generate markdown report from search results
    4. Save report to file
    """
    
    def __init__(self, config: Optional[Config] = None):
        """
        Initialize the Deep Research Manager
        
        Args:
            config: Optional Config object. If None, uses default config.
        """
        self.config = config or Config()
        
        # Initialize all agents
        self.planner = PlannerAgent(self.config)
        self.executor = ExecuteAgent(self.config)
        self.synthesizer = SynthesizeAgent(self.config)
        
        print("Initialization complete, welcome to use.\nPlease confirm that relevant models can be called successfully before use.\n")
    
    def run(self, query: str, save_to_file: bool = True) -> None:
        """
        Core entry function that orchestrates the entire research process
        
        Args:
            query: User research query string
            save_to_file: Whether to save the report as a Markdown file
        """
        print("Starting research...\n")
        
        # Step 1: Generate search plan based on user query
        print("Step 1: Generating search plan...")
        search_plan = self.plan_searches(query)
        
        # Step 2: Perform web searches based on the generated plan
        print("\nStep 2: Performing web searches...")
        search_results = self.perform_searches(search_plan)
        
        # Step 3: Generate markdown report based on search content
        print("\nStep 3: Generating report...")
        markdown_content, follow_up_questions = self.write_report(query, search_results)
        
        # Display results
        print("\n\n=====REPORT=====\n\n")
        print(markdown_content)
        
        print("\n\n=====FOLLOW UP QUESTIONS=====\n\n")
        follow_up_questions_text = "\n".join(f"{i+1}. {q}" for i, q in enumerate(follow_up_questions))
        print(follow_up_questions_text)
        
        # Save as Markdown file
        if save_to_file:
            self.save_report_as_md(query, markdown_content)
    
    def plan_searches(self, query: str) -> WebSearchPlan:
        """
        Generate a search plan based on user query
        
        Args:
            query: User query string
            
        Returns:
            WebSearchPlan containing search tasks
        """
        print("Planning searches...")
        plan = self.planner.create_research_plan(query)
        print(f"Generated {len(plan.searches)} search queries")
        return plan
    
    def perform_searches(self, search_plan: WebSearchPlan) -> List[str]:
        """
        Execute web searches based on the search plan
        
        Args:
            search_plan: WebSearchPlan containing search tasks
            
        Returns:
            List of search result strings
        """
        tasks = [item.query for item in search_plan.searches]
        results = []
        num_completed = 0
        failed_searches = []
        
        for task in tasks:
            print(f"Searching: {task}")
            try:
                search_content = self.executor.execute_search(task)
                
                if search_content and not search_content.startswith("No search results") and not search_content.startswith("Search failed"):
                    results.append(search_content)
                else:
                    failed_searches.append(task)
                    print(f"  ⚠️  No results for: {task}")
            
            except Exception as e:
                failed_searches.append(task)
                print(f"  ❌ Error searching '{task}': {e}")
            
            num_completed += 1
            print(f"Searching... {num_completed}/{len(tasks)} completed")
        
        if failed_searches:
            print(f"\n⚠️  Warning: {len(failed_searches)} searches failed or returned no results")
            print(f"   Successful searches: {len(results)}/{len(tasks)}")
        
        if not results:
            print("\n❌ Error: No search results obtained. Please check:")
            print("   1. API keys are configured correctly")
            print("   2. Search method is working (run: python check_system.py)")
            print("   3. Network connectivity")
            raise ValueError("No search results obtained. Cannot generate report.")
        
        return results
    
    def write_report(self, query: str, search_results: List[str]) -> Tuple[str, List[str]]:
        """
        Generate a research report from search results
        
        Args:
            query: Original user query
            search_results: List of search result strings
            
        Returns:
            Tuple of (markdown_content, follow_up_questions)
        """
        print("Thinking about report...")
        
        # Combine search results into a single string
        combined_results = "\n\n".join([
            f"### Search Result {i+1}\n\n{result}"
            for i, result in enumerate(search_results)
        ])
        
        # Create search results dictionary for synthesizer
        search_results_dict = {
            f"Query {i+1}": result
            for i, result in enumerate(search_results)
        }
        
        # Generate report
        synthesize_data = self.synthesizer.synthesize_report(query, search_results_dict)
        
        # Process Markdown content: remove code block markers
        markdown_content = synthesize_data.markdown_report.strip()
        if markdown_content.startswith("```"):
            # Remove markdown code block markers
            lines = markdown_content.split("\n")
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines[-1].strip() == "```":
                lines = lines[:-1]
            markdown_content = "\n".join(lines).strip()
        
        # Remove "markdown" keyword if present
        markdown_content = markdown_content.replace("```markdown", "").replace("```", "").strip()
        
        return markdown_content, synthesize_data.follow_up_questions
    
    def save_report_as_md(self, query: str, markdown_content: str) -> None:
        """
        Save the generated report as a Markdown file
        
        Args:
            query: User query string (used for filename)
            markdown_content: Markdown content to save
        """
        # Use user's query as filename
        sanitized_query = query.replace(" ", "_").replace(":", "").replace("?", "")
        
        # Create filename
        file_name = f"Research_Report_{sanitized_query}.md"
        
        # Get file path
        file_path = os.path.join(os.getcwd(), file_name)
        
        # Write file
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(markdown_content)
        
        print(f"\nReport saved as: {file_name}")
        print(f"File path: {file_path}")
