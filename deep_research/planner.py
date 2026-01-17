"""
Planner Agent - Generates research keywords and search strategies
Uses high-capability models for strong reasoning and logical organization
"""

from typing import List, Dict
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field

from .config import Config


class WebSearchItem(BaseModel):
    """Web search item (single search instruction)"""
    query: str = Field(..., description="Keywords for web search, write only one keyword or short phrase")
    reason: str = Field(..., description="Explanation of the necessity of this search item for answering the original question")


class WebSearchPlan(BaseModel):
    """Web search plan (contains multiple search instructions)"""
    searches: List[WebSearchItem] = Field(..., description="List of web searches to be performed to accurately answer the original question")


class PlannerAgent:
    """Planner Agent that generates research keywords and search strategies"""
    
    def __init__(self, config: Config):
        self.config = config
        self.llm = self._initialize_llm()
        self.parser = PydanticOutputParser(pydantic_object=WebSearchPlan)
        
    def _initialize_llm(self):
        """Initialize the LLM for planning (high-capability model)"""
        # Check for DeepSeek (OpenAI-compatible API)
        if self.config.planner_model.startswith("deepseek") or (self.config.deepseek_api_key and "deepseek" in self.config.planner_model.lower()):
            if not self.config.deepseek_api_key:
                raise ValueError("DeepSeek API key required for DeepSeek models")
            return ChatOpenAI(
                model=self.config.planner_model if self.config.planner_model.startswith("deepseek") else "deepseek-chat",
                temperature=self.config.planner_temperature,
                api_key=self.config.deepseek_api_key,
                base_url=self.config.deepseek_base_url
            )
        # Check for Claude
        elif self.config.planner_model.startswith("claude"):
            if not self.config.anthropic_api_key:
                raise ValueError("Anthropic API key required for Claude models")
            return ChatAnthropic(
                model=self.config.planner_model,
                temperature=self.config.planner_temperature,
                api_key=self.config.anthropic_api_key
            )
        # Default to OpenAI
        else:
            if not self.config.openai_api_key:
                raise ValueError("OpenAI API key required for OpenAI models")
            return ChatOpenAI(
                model=self.config.planner_model,
                temperature=self.config.planner_temperature,
                api_key=self.config.openai_api_key
            )
    
    def create_research_plan(self, research_topic: str) -> WebSearchPlan:
        """
        Generate a comprehensive research plan with search queries
        
        Args:
            research_topic: The topic to research
            
        Returns:
            WebSearchPlan with search items
        """
        planning_system_prompt = """You are a professional research assistant. Based on user queries, 
you need to complete the following core tasks to ensure precise and efficient searches:

1. Design 10 unique web search keywords. Keywords must align with the core needs of the query, 
   balancing precision and coverage. Each keyword should be focused and specific.

2. For each keyword, individually explain the search reason, detailing how the keyword helps 
   answer the user's query. Reasons must be specific, actionable, and not vague.

Ensure all keywords are non-redundant and collectively provide comprehensive coverage of the topic."""
        
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", planning_system_prompt),
            ("human", """User Query: {topic}

{format_instructions}

Generate a web search plan with 10 unique search keywords and their reasons."""),
        ])
        
        prompt = prompt_template.format_messages(
            topic=research_topic,
            format_instructions=self.parser.get_format_instructions()
        )
        
        response = self.llm.invoke(prompt)
        
        # Parse the response
        plan = self.parser.parse(response.content)
        
        return plan
    
    def get_search_queries(self, research_topic: str) -> List[str]:
        """
        Get a list of search queries from the research plan
        
        Args:
            research_topic: The topic to research
            
        Returns:
            List of search query strings
        """
        plan = self.create_research_plan(research_topic)
        return [item.query for item in plan.searches]
    
    def get_search_plan_with_reasons(self, research_topic: str) -> WebSearchPlan:
        """
        Get the full search plan with queries and reasons
        
        Args:
            research_topic: The topic to research
            
        Returns:
            WebSearchPlan with all search items including reasons
        """
        return self.create_research_plan(research_topic)
