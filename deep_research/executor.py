"""
Execute Agent - Performs web searches and summarizes content
Uses cost-effective models for faster and cheaper execution
"""

from typing import List, Dict, Optional
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
import time

# Try to import create_agent, fallback to None if not available
try:
    from langchain.agents import create_agent
    HAS_CREATE_AGENT = True
except ImportError:
    try:
        from langchain_core.agents import create_agent
        HAS_CREATE_AGENT = True
    except ImportError:
        HAS_CREATE_AGENT = False
        print("⚠️  create_agent not available, will use direct LLM calls")

from .config import Config


class SearchResult:
    """Individual search result with content and metadata"""
    def __init__(self, title: str = "", url: str = "", snippet: str = "", content: Optional[str] = None, summary: Optional[str] = None, domain: Optional[str] = None, retrieved_at: Optional[str] = None):
        self.title = title
        self.url = url
        self.snippet = snippet
        self.content = content
        self.summary = summary
        self.domain = domain or (self._extract_domain(url) if url else None)
        self.retrieved_at = retrieved_at
        self.reliability_score = self._calculate_reliability_score()
    
    def _extract_domain(self, url: str) -> Optional[str]:
        """Extract domain from URL"""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            return parsed.netloc
        except:
            return None
    
    def _calculate_reliability_score(self) -> float:
        """Calculate initial reliability score based on domain and content"""
        score = 0.5  # Base score
        
        # Known reliable domains get higher scores
        reliable_domains = [
            'edu', 'gov', 'org', 'wikipedia.org', 'nature.com', 
            'science.org', 'pubmed.ncbi.nlm.nih.gov', 'arxiv.org'
        ]
        
        if self.domain:
            domain_lower = self.domain.lower()
            for reliable in reliable_domains:
                if reliable in domain_lower:
                    score = 0.8
                    break
        
        # Boost score if we have substantial content
        if self.content and len(self.content) > 500:
            score += 0.1
        if self.summary and len(self.summary) > 200:
            score += 0.1
        
        return min(score, 1.0)


class ExecuteAgent:
    """
    Execute Agent that performs web searches and summarizes content.
    
    The role of the Execute Agent is to receive a search keyword, call a web search tool,
    and then generate a concise summary (2-3 paragraphs, <500 words) based on the search results,
    without comments, only retaining the information itself.
    """
    
    def __init__(self, config: Config):
        self.config = config
        self.search_method = config.executor_search_method.lower()
        self.llm = None
        self.agent = None
        self._initialize_search_method()
        
    def _initialize_search_method(self):
        """Initialize the search method based on configuration"""
        if self.search_method == "qwen":
            self._initialize_qwen_search()
        elif self.search_method == "tavily":
            self._initialize_tavily_search()
        else:
            # Fallback to DuckDuckGo
            self._initialize_duckduckgo_search()
    
    def _initialize_qwen_search(self):
        """Initialize Qwen API with built-in search capability"""
        try:
            from langchain_community.chat_models import ChatTongyi
            
            if not self.config.qwen_api_key:
                print("⚠️  Qwen API key not found, falling back to DuckDuckGo search")
                self._initialize_duckduckgo_search()
                return
            
            self.llm = ChatTongyi(
                model='qwen-max',
                api_key=self.config.qwen_api_key,
                base_url='https://dashscope.aliyuncs.com/compatible-mode/v1',
                model_kwargs={
                    "enable_search": True,  # Enable internet search
                }
            )
            
            # Create agent with execute prompt if available
            if HAS_CREATE_AGENT:
                execute_prompt = """You are a professional research assistant. Given a search keyword, 
you need to perform a web search for that keyword and generate a concise summary of the search results.

The summary should contain 2-3 paragraphs, be controlled within 500 words, and cover the core points.
The expression should be concise and refined, without needing to use complete sentences or strictly 
adhere to grammatical norms.

This summary will be used by others for integration into a report, so it is essential to extract 
core information and remove irrelevant content. Apart from the summary itself, no additional 
comments should be added."""
                
                self.agent = create_agent(
                    model=self.llm,
                    system_prompt=execute_prompt
                )
            else:
                # Store prompt for direct LLM calls
                self.execute_prompt = """You are a professional research assistant. Given a search keyword, 
you need to perform a web search for that keyword and generate a concise summary of the search results.

The summary should contain 2-3 paragraphs, be controlled within 500 words, and cover the core points.
The expression should be concise and refined, without needing to use complete sentences or strictly 
adhere to grammatical norms.

This summary will be used by others for integration into a report, so it is essential to extract 
core information and remove irrelevant content. Apart from the summary itself, no additional 
comments should be added."""
            print("✅ Initialized Qwen search with built-in internet search")
            
        except ImportError:
            print("⚠️  langchain_community not available, falling back to DuckDuckGo search")
            self._initialize_duckduckgo_search()
        except Exception as e:
            print(f"⚠️  Error initializing Qwen search: {e}, falling back to DuckDuckGo")
            self._initialize_duckduckgo_search()
    
    def _initialize_tavily_search(self):
        """Initialize Tavily search tool"""
        try:
            from langchain_community.tools.tavily_search import TavilySearchResults
            
            if not self.config.tavily_api_key:
                print("⚠️  Tavily API key not found, falling back to DuckDuckGo search")
                self._initialize_duckduckgo_search()
                return
            
            tavily_tool = TavilySearchResults(
                api_key=self.config.tavily_api_key,
                max_results=5
            )
            
            # Initialize LLM for summarization
            self.llm = self._initialize_summarization_llm()
            self.tavily_tool = tavily_tool
            
            execute_prompt = """You are a professional research assistant. Given a search keyword, 
you need to perform a web search for that keyword and generate a concise summary of the search results.

The summary should contain 2-3 paragraphs, be controlled within 500 words, and cover the core points.
The expression should be concise and refined, without needing to use complete sentences or strictly 
adhere to grammatical norms.

This summary will be used by others for integration into a report, so it is essential to extract 
core information and remove irrelevant content. Apart from the summary itself, no additional 
comments should be added."""
            
            if HAS_CREATE_AGENT:
                self.agent = create_agent(
                    model=self.llm,
                    system_prompt=execute_prompt,
                    tools=[tavily_tool]
                )
            else:
                self.execute_prompt = execute_prompt
                self.tavily_tool = tavily_tool
            print("✅ Initialized Tavily search")
            
        except ImportError:
            print("⚠️  Tavily tools not available, falling back to DuckDuckGo search")
            self._initialize_duckduckgo_search()
        except Exception as e:
            print(f"⚠️  Error initializing Tavily search: {e}, falling back to DuckDuckGo")
            self._initialize_duckduckgo_search()
    
    def _initialize_duckduckgo_search(self):
        """Initialize DuckDuckGo search as fallback"""
        try:
            from duckduckgo_search import DDGS
            import requests
            from bs4 import BeautifulSoup
            
            # Suppress "duckduckgo_search has been renamed to ddgs" warning
            import warnings
            with warnings.catch_warnings():
                warnings.filterwarnings("ignore", category=RuntimeWarning, message=".*duckduckgo_search.*renamed.*")
                self.ddgs = DDGS()
            self.requests = requests
            self.BeautifulSoup = BeautifulSoup
            self.llm = self._initialize_summarization_llm()
            self.search_method = "duckduckgo"
            print("✅ Initialized DuckDuckGo search")
            
        except ImportError:
            raise ImportError("duckduckgo-search package is required. Install with: pip install duckduckgo-search")
    
    def _initialize_summarization_llm(self):
        """Initialize LLM for summarization (used with DuckDuckGo or Tavily)"""
        if not self.config.openai_api_key and not self.config.anthropic_api_key:
            raise ValueError("At least one API key (OpenAI or Anthropic) must be configured for summarization")
        
        if self.config.executor_model.startswith("claude"):
            if not self.config.anthropic_api_key:
                raise ValueError("Anthropic API key required for Claude models")
            from langchain_anthropic import ChatAnthropic
            return ChatAnthropic(
                model=self.config.executor_model,
                temperature=self.config.executor_temperature,
                api_key=self.config.anthropic_api_key
            )
        else:
            if not self.config.openai_api_key:
                raise ValueError("OpenAI API key required for OpenAI models")
            from langchain_openai import ChatOpenAI
            return ChatOpenAI(
                model=self.config.executor_model,
                temperature=self.config.executor_temperature,
                api_key=self.config.openai_api_key
            )
    
    def execute_search(self, query: str) -> str:
        """
        Execute a search and return a concise summary
        
        Args:
            query: Search keyword
            
        Returns:
            Summary string (2-3 paragraphs, <500 words)
        """
        if self.search_method == "qwen" and self.agent:
            return self._execute_qwen_search(query)
        elif self.search_method == "tavily" and self.agent:
            return self._execute_tavily_search(query)
        else:
            return self._execute_duckduckgo_search(query)
    
    def _execute_qwen_search(self, query: str) -> str:
        """Execute search using Qwen with built-in search"""
        try:
            if self.agent:
                # Use agent if available
                response = self.agent.invoke({
                    "messages": [{"role": "user", "content": query}]
                })
                
                # Extract summary from response
                if isinstance(response, dict):
                    # Get the last AI message
                    messages = response.get("messages", [])
                    for msg in reversed(messages):
                        if hasattr(msg, 'content'):
                            return msg.content.strip()
                        elif isinstance(msg, dict) and 'content' in msg:
                            return msg['content'].strip()
                
                # Fallback
                return str(response)
            else:
                # Direct LLM call (Qwen has built-in search enabled)
                prompt_template = ChatPromptTemplate.from_messages([
                    ("system", self.execute_prompt),
                    ("human", "Search keyword: {query}"),
                ])
                
                prompt = prompt_template.format_messages(query=query)
                response = self.llm.invoke(prompt)
                return response.content.strip()
            
        except Exception as e:
            print(f"Error in Qwen search: {e}")
            return f"Search failed for query: {query}"
    
    def _execute_tavily_search(self, query: str) -> str:
        """Execute search using Tavily"""
        try:
            response = self.agent.invoke({
                "messages": [{"role": "user", "content": query}]
            })
            
            # Extract summary from response
            if isinstance(response, dict):
                messages = response.get("messages", [])
                for msg in reversed(messages):
                    if hasattr(msg, 'content'):
                        return msg.content.strip()
                    elif isinstance(msg, dict) and 'content' in msg:
                        return msg['content'].strip()
            
            return str(response)
            
        except Exception as e:
            print(f"Error in Tavily search: {e}")
            return f"Search failed for query: {query}"
    
    def _execute_duckduckgo_search(self, query: str) -> str:
        """Execute search using DuckDuckGo and summarize"""
        try:
            # Perform search
            results = list(self.ddgs.text(query, max_results=5))
            
            if not results or len(results) == 0:
                return f"No search results found for: {query}. Please try a different search query."
            
            # Collect search content
            search_content = []
            for result in results:
                title = result.get('title', '')
                snippet = result.get('body', '')
                url = result.get('href', '')
                if title or snippet:  # Only add if there's actual content
                    search_content.append(f"Title: {title}\nURL: {url}\nContent: {snippet}\n")
            
            if not search_content:
                return f"No meaningful search results found for: {query}. The search returned empty content."
            
            combined_content = "\n".join(search_content)
            
            # Summarize using the execute prompt
            execute_prompt = """You are a professional research assistant. Given search results, 
generate a concise summary.

The summary should contain 2-3 paragraphs, be controlled within 500 words, and cover the core points.
The expression should be concise and refined, without needing to use complete sentences or strictly 
adhere to grammatical norms.

This summary will be used by others for integration into a report, so it is essential to extract 
core information and remove irrelevant content. Apart from the summary itself, no additional 
comments should be added."""
            
            prompt_template = ChatPromptTemplate.from_messages([
                ("system", execute_prompt),
                ("human", """Search Query: {query}

Search Results:
{content}

Generate a concise summary based on the search results."""),
            ])
            
            prompt = prompt_template.format_messages(
                query=query,
                content=combined_content[:3000]  # Limit content length
            )
            
            response = self.llm.invoke(prompt)
            summary = response.content.strip() if hasattr(response, 'content') else str(response).strip()
            
            # If summary is too short or seems like an error, return the raw content
            if not summary or len(summary) < 100 or "no results" in summary.lower() or "failed" in summary.lower():
                # Return a formatted version of the raw search results instead
                return f"Search results for '{query}':\n\n{combined_content[:800]}"
            
            return summary
            
        except Exception as e:
            print(f"⚠️  Error in DuckDuckGo search for '{query}': {e}")
            return f"Search encountered an error for query: {query}. Error: {str(e)}"
    
    def execute_search_queries(self, queries: List[str]) -> Dict[str, str]:
        """
        Execute multiple search queries and return summaries
        
        Args:
            queries: List of search query strings
            
        Returns:
            Dictionary mapping queries to their summaries
        """
        all_results = {}
        
        for i, query in enumerate(queries, 1):
            print(f"  [{i}/{len(queries)}] Searching: {query}")
            
            try:
                summary = self.execute_search(query)
                all_results[query] = summary
                
                # Small delay to be respectful
                time.sleep(0.5)
            except Exception as e:
                print(f"    ⚠️  Error: {e}")
                all_results[query] = f"Error: {str(e)}"
        
        return all_results
