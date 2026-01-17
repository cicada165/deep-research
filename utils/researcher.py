"""
Backend integration wrapper for DeepResearch with async execution
"""

import threading
import time
from datetime import datetime
from typing import Optional, Callable
from deep_research import DeepResearch, Config
from utils.session_manager import ResearchSession, generate_research_id


class ResearchRunner:
    """Thread-safe wrapper for DeepResearch"""
    
    def __init__(self, config: Config):
        """Initialize with config"""
        self.config = config
        self.researcher = DeepResearch(config)
        self._cancelled = False
        self._thread: Optional[threading.Thread] = None
    
    def run_research(
        self, 
        topic: str, 
        progress_callback: Optional[Callable] = None
    ) -> ResearchSession:
        """Run research with progress updates"""
        session = ResearchSession(
            id=generate_research_id(),
            topic=topic,
            created_at=datetime.now(),
            status="running"
        )
        
        start_time = time.time()
        
        try:
            # Step 1: Planning
            if progress_callback:
                progress_callback("planning", 0.15, "Planning research strategy...")
            session.current_step = "planning"
            session.status_message = "Planning research strategy..."
            
            plan = self.researcher.planner.create_research_plan(topic)
            queries = [item.query for item in plan.searches]
            
            # Step 2: Execution
            if progress_callback:
                progress_callback("execution", 0.40, f"Executing {len(queries)} searches...")
            session.current_step = "execution"
            session.status_message = f"Executing {len(queries)} searches..."
            
            search_results = self.researcher.executor.execute_search_queries(queries)
            
            # Step 2.5: Fact-Checking
            if self.config.fact_checker_enabled:
                if progress_callback:
                    progress_callback("fact_checking", 0.70, "Fact-checking and verification...")
                session.current_step = "fact_checking"
                session.status_message = "Fact-checking and verification..."
                
                from deep_research.fact_checker import FactCheckerAgent
                fact_checker = FactCheckerAgent(self.config)
                search_results = fact_checker.fact_check_summaries(search_results)
            
            # Step 3: Synthesis
            if progress_callback:
                progress_callback("synthesis", 0.85, "Synthesizing final report...")
            session.current_step = "synthesis"
            session.status_message = "Synthesizing final report..."
            
            synthesize_data = self.researcher.synthesizer.synthesize_report(
                topic, search_results
            )
            formatted_report = self.researcher.synthesizer.format_report(
                synthesize_data, topic
            )
            
            if progress_callback:
                progress_callback("completed", 1.0, "Research complete!")
            
            # Update session
            session.status = "completed"
            session.completed_at = datetime.now()
            session.synthesize_data = synthesize_data
            session.formatted_report = formatted_report
            session.current_step = "completed"
            session.status_message = "Research complete!"
            session.progress = 1.0
            session.execution_time = time.time() - start_time
            session.config_snapshot = {
                "planner_model": self.config.planner_model,
                "executor_model": self.config.executor_model,
                "synthesizer_model": self.config.synthesizer_model,
                "fact_checker_enabled": self.config.fact_checker_enabled,
            }
            
            return session
            
        except Exception as e:
            import traceback
            session.status = "error"
            session.error = str(e)
            session.error_traceback = traceback.format_exc()
            session.completed_at = datetime.now()
            session.execution_time = time.time() - start_time
            
            if progress_callback:
                progress_callback("error", 0.0, f"Error: {str(e)}")
            
            return session
    
    def cancel_research(self):
        """Cancel ongoing research"""
        self._cancelled = True
