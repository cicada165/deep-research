"""
System Status Checker - Diagnostic tool for Deep Research system
"""

from typing import Dict, List
from .config import Config


class SystemStatus:
    """Check system configuration and agent readiness"""
    
    def __init__(self, config: Config = None):
        self.config = config or Config()
    
    def check_all(self) -> Dict[str, any]:
        """Check all system components"""
        status = {
            "api_keys": self.check_api_keys(),
            "search_method": self.check_search_method(),
            "models": self.check_models(),
            "agents": self.check_agents()
        }
        return status
    
    def check_api_keys(self) -> Dict[str, bool]:
        """Check which API keys are configured"""
        return {
            "openai": bool(self.config.openai_api_key),
            "anthropic": bool(self.config.anthropic_api_key),
            "qwen": bool(self.config.qwen_api_key),
            "tavily": bool(self.config.tavily_api_key),
            "deepseek": bool(self.config.deepseek_api_key)
        }
    
    def check_search_method(self) -> Dict[str, any]:
        """Check search method configuration"""
        method = self.config.executor_search_method.lower()
        status = {
            "configured_method": method,
            "qwen_available": bool(self.config.qwen_api_key),
            "tavily_available": bool(self.config.tavily_api_key),
            "duckduckgo_available": True,  # Always available
            "active_method": None,
            "status": "unknown"
        }
        
        if method == "qwen":
            if self.config.qwen_api_key:
                status["active_method"] = "qwen"
                status["status"] = "ready"
            else:
                status["active_method"] = "duckduckgo"
                status["status"] = "fallback (qwen key missing)"
        elif method == "tavily":
            if self.config.tavily_api_key:
                status["active_method"] = "tavily"
                status["status"] = "ready"
            else:
                status["active_method"] = "duckduckgo"
                status["status"] = "fallback (tavily key missing)"
        else:
            status["active_method"] = "duckduckgo"
            status["status"] = "ready"
        
        return status
    
    def check_models(self) -> Dict[str, str]:
        """Check model configuration"""
        return {
            "planner": self.config.planner_model,
            "executor": self.config.executor_model,
            "synthesizer": self.config.synthesizer_model
        }
    
    def check_agents(self) -> Dict[str, bool]:
        """Check if agents can be initialized"""
        results = {}
        try:
            from .planner import PlannerAgent
            planner = PlannerAgent(self.config)
            results["planner"] = True
        except Exception as e:
            results["planner"] = False
            results["planner_error"] = str(e)
        
        try:
            from .executor import ExecuteAgent
            executor = ExecuteAgent(self.config)
            results["executor"] = True
            results["executor_search_method"] = executor.search_method
        except Exception as e:
            results["executor"] = False
            results["executor_error"] = str(e)
        
        try:
            from .synthesizer import SynthesizeAgent
            synthesizer = SynthesizeAgent(self.config)
            results["synthesizer"] = True
        except Exception as e:
            results["synthesizer"] = False
            results["synthesizer_error"] = str(e)
        
        return results
    
    def print_status(self):
        """Print formatted status report"""
        status = self.check_all()
        
        print("=" * 60)
        print("Deep Research System Status")
        print("=" * 60)
        
        print("\n📋 API Keys:")
        api_keys = status["api_keys"]
        for key, available in api_keys.items():
            status_icon = "✅" if available else "❌"
            print(f"  {status_icon} {key.upper()}: {'Configured' if available else 'Not configured'}")
        
        print("\n🔍 Search Method:")
        search = status["search_method"]
        print(f"  Configured: {search['configured_method']}")
        print(f"  Active: {search['active_method']}")
        print(f"  Status: {search['status']}")
        
        print("\n🤖 Models:")
        models = status["models"]
        for agent, model in models.items():
            print(f"  {agent.capitalize()}: {model}")
        
        print("\n⚙️  Agents:")
        agents = status["agents"]
        for agent in ["planner", "executor", "synthesizer"]:
            if agent in agents:
                status_icon = "✅" if agents[agent] else "❌"
                print(f"  {status_icon} {agent.capitalize()}: {'Ready' if agents[agent] else 'Error'}")
                if not agents[agent] and f"{agent}_error" in agents:
                    print(f"    Error: {agents[agent + '_error']}")
        
        if "executor_search_method" in agents:
            print(f"    Executor using: {agents['executor_search_method']}")
        
        print("\n" + "=" * 60)
        
        # Recommendations
        print("\n💡 Recommendations:")
        recommendations = []
        
        if not api_keys["openai"] and not api_keys["anthropic"]:
            recommendations.append("Configure at least one LLM API key (OPENAI_API_KEY or ANTHROPIC_API_KEY)")
        
        if search["configured_method"] == "qwen" and not api_keys["qwen"]:
            recommendations.append("Configure QWEN_API_KEY for Qwen search, or set EXECUTOR_SEARCH_METHOD=duckduckgo")
        
        if search["configured_method"] == "tavily" and not api_keys["tavily"]:
            recommendations.append("Configure TAVILY_API_KEY for Tavily search, or set EXECUTOR_SEARCH_METHOD=duckduckgo")
        
        if not recommendations:
            print("  ✅ System is properly configured!")
        else:
            for rec in recommendations:
                print(f"  ⚠️  {rec}")
        
        print()
