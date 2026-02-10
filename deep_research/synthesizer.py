"""
Synthesize Agent - Consolidates search results and writes the final report
Uses high-capability models for strong reasoning and long-text generation
"""

from typing import List, Dict, Optional
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field

# Try to import create_agent and SummarizationMiddleware
try:
    from langchain.agents import create_agent
    HAS_CREATE_AGENT = True
except ImportError:
    try:
        from langchain_core.agents import create_agent
        HAS_CREATE_AGENT = True
    except ImportError:
        HAS_CREATE_AGENT = False

try:
    from langchain.agents.middleware import SummarizationMiddleware
    HAS_SUMMARIZATION_MIDDLEWARE = True
except ImportError:
    try:
        from langchain_core.agents.middleware import SummarizationMiddleware
        HAS_SUMMARIZATION_MIDDLEWARE = True
    except ImportError:
        HAS_SUMMARIZATION_MIDDLEWARE = False

from .config import Config


class SynthesizeData(BaseModel):
    """Structured output for the Synthesize Agent"""
    short_summary: str = Field(..., description="Brief summary of the research results, within 200 words")
    markdown_report: str = Field(..., description="Final comprehensive report in Markdown format")
    follow_up_questions: List[str] = Field(..., description="Suggested topics for further research")


class SynthesizeAgent:
    """
    Synthesize Agent that consolidates results and writes the final report.
    
    This is the outputter of the entire research system, responsible for integrating 
    all previously searched information into a complete, structured, and readable 
    long report. The overall task flow is to first write a search outline, then search 
    based on the outline, then compile the search results into a Markdown format report, 
    and simultaneously generate a brief summary and some follow-up questions for 
    further research.
    """
    
    def __init__(self, config: Config):
        self.config = config
        self.llm = self._initialize_llm()
        self.parser = PydanticOutputParser(pydantic_object=SynthesizeData)
        self.agent = None
        self._initialize_agent()
        
    def _initialize_llm(self):
        """Initialize the LLM for synthesis (high-capability model)"""
        if not self.config.openai_api_key and not self.config.anthropic_api_key:
            raise ValueError("At least one API key (OpenAI or Anthropic) must be configured")
        
        if self.config.synthesizer_model.startswith("claude"):
            if not self.config.anthropic_api_key:
                raise ValueError("Anthropic API key required for Claude models")
            return ChatAnthropic(
                model=self.config.synthesizer_model,
                temperature=self.config.synthesizer_temperature,
                api_key=self.config.anthropic_api_key
            )
        else:
            if not self.config.openai_api_key:
                raise ValueError("OpenAI API key required for OpenAI models")
            return ChatOpenAI(
                model=self.config.synthesizer_model,
                temperature=self.config.synthesizer_temperature,
                api_key=self.config.openai_api_key,
                base_url=self.config.openai_base_url
            )
    
    def _initialize_agent(self):
        """Initialize the synthesize agent with middleware if available"""
        synthesize_prompt = """You are a senior researcher, responsible for writing a coherent report for a research query.

You will receive the original query requirements and the preliminary research results completed by the research assistant.

Please first formulate a report outline, clarifying the structural framework and logical flow of the report. 
Then, write a complete report based on the outline, and use it as the final output.

The content should have structure and paragraphs. The lowest level of structure should not use "1." or "- " 
for bullet points; describe directly with text.

The final report must be in Markdown format, and the content should be detailed and in-depth. 
The word count should be no less than 2000 words."""
        
        summary_prompt = """You are a senior researcher, responsible for writing coherent reports for a research query.
Currently, there is a report, and you need to accurately extract key points from the existing report 
without excessive deletion."""
        
        if HAS_CREATE_AGENT:
            middleware = []
            if HAS_SUMMARIZATION_MIDDLEWARE:
                # Add SummarizationMiddleware when input tokens exceed 20000
                middleware.append(
                    SummarizationMiddleware(
                        model=self.llm,
                        trigger=("tokens", 20000),
                        summary_prompt=summary_prompt,
                    )
                )
            
            try:
                # Temporarily disable agent due to issues with empty responses
                # The direct LLM call with structured output works more reliably
                self.agent = None
                print("⚠️  Agent disabled, using direct LLM calls with structured output")
                # Uncomment below to enable agent (may have issues with empty responses):
                # self.agent = create_agent(
                #     model=self.llm,
                #     system_prompt=synthesize_prompt,
                #     middleware=middleware if middleware else None,
                #     response_format=SynthesizeData
                # )
                # print("✅ Synthesize Agent initialized with structured output")
            except Exception as e:
                print(f"⚠️  Could not create agent: {e}, will use direct LLM calls")
                self.agent = None
        else:
            self.agent = None
            self.synthesize_prompt = synthesize_prompt
            print("⚠️  create_agent not available, will use direct LLM calls")
    
    def synthesize_report(self, research_topic: str, search_results: Dict[str, str]) -> SynthesizeData:
        """
        Synthesize all search results into a comprehensive research report
        
        Args:
            research_topic: The original research topic
            search_results: Dictionary mapping queries to their summaries
            
        Returns:
            SynthesizeData with short_summary, markdown_report, and follow_up_questions
        """
        # Prepare content for synthesis
        content_sections = []
        content_sections.append(f"# Research Topic: {research_topic}\n\n")
        content_sections.append("## Search Results and Summaries\n\n")
        
        for query, summary in search_results.items():
            section = f"### Search Query: {query}\n\n"
            section += f"{summary}\n\n"
            content_sections.append(section)
        
        combined_content = "\n".join(content_sections)
        
        if self.agent:
            # Use agent if available
            try:
                response = self.agent.invoke({
                    "messages": [{"role": "user", "content": combined_content}]
                })
                
                # Extract structured response
                if isinstance(response, dict):
                    structured_response = response.get("structured_response")
                    if structured_response:
                        result = SynthesizeData(
                            short_summary=structured_response.short_summary if hasattr(structured_response, 'short_summary') else getattr(structured_response, 'short_summary', ''),
                            markdown_report=structured_response.markdown_report if hasattr(structured_response, 'markdown_report') else getattr(structured_response, 'markdown_report', ''),
                            follow_up_questions=structured_response.follow_up_questions if hasattr(structured_response, 'follow_up_questions') else getattr(structured_response, 'follow_up_questions', [])
                        )
                        if not result.markdown_report or len(result.markdown_report.strip()) == 0:
                            print("⚠️  Warning: Agent returned empty markdown_report, falling back to direct call")
                            return self._synthesize_direct(research_topic, combined_content)
                        return result
                    # Try to extract from messages
                    messages = response.get("messages", [])
                    for msg in reversed(messages):
                        if hasattr(msg, 'content'):
                            content = msg.content
                            # Try to parse as JSON or structured data
                            parsed = self._parse_response(content)
                            if not parsed.markdown_report or len(parsed.markdown_report.strip()) == 0:
                                print("⚠️  Warning: Parsed response is empty, falling back to direct call")
                                return self._synthesize_direct(research_topic, combined_content)
                            return parsed
                
                # Fallback: try to parse response directly
                parsed = self._parse_response(str(response))
                if not parsed.markdown_report or len(parsed.markdown_report.strip()) == 0:
                    print("⚠️  Warning: Parsed response is empty, falling back to direct call")
                    return self._synthesize_direct(research_topic, combined_content)
                return parsed
                
            except Exception as e:
                print(f"⚠️  Error using agent: {e}, falling back to direct LLM call")
                import traceback
                traceback.print_exc()
                return self._synthesize_direct(research_topic, combined_content)
        else:
            # Direct LLM call
            return self._synthesize_direct(research_topic, combined_content)
    
    def _synthesize_direct(self, research_topic: str, content: str) -> SynthesizeData:
        """Synthesize using direct LLM call with structured output"""
        synthesize_prompt = """You are a senior researcher, responsible for writing a coherent report for a research query.

You will receive the original query requirements and the preliminary research results completed by the research assistant.

Please first formulate a report outline, clarifying the structural framework and logical flow of the report. 
Then, write a complete report based on the outline, and use it as the final output.

The content should have structure and paragraphs. The lowest level of structure should not use "1." or "- " 
for bullet points; describe directly with text.

The final report must be in Markdown format, and the content should be detailed and in-depth. 
The word count should be no less than 2000 words.

You must provide:
1. A brief summary (within 200 words)
2. A comprehensive Markdown report (at least 2000 words)
3. A list of suggested follow-up research questions"""
        
        # Try to use with_structured_output if available (for newer OpenAI models)
        try:
            if hasattr(self.llm, 'with_structured_output'):
                # Use structured output method
                structured_llm = self.llm.with_structured_output(
                    SynthesizeData, 
                    method="json_schema" if "gpt-4o" in self.config.synthesizer_model.lower() or "gpt-4-turbo" in self.config.synthesizer_model.lower() else "function_calling"
                )
                
                user_prompt = f"""Research Topic: {research_topic}

Research Content:
{content}

Generate a comprehensive research report with a short summary, detailed markdown report, and follow-up questions."""
                
                response = structured_llm.invoke(user_prompt)
                # Response should already be a SynthesizeData object
                if isinstance(response, SynthesizeData):
                    if not response.markdown_report or len(response.markdown_report.strip()) == 0:
                        print("⚠️  Warning: Structured output returned empty markdown_report")
                    return response
                else:
                    # Convert dict to SynthesizeData
                    return SynthesizeData(**response) if isinstance(response, dict) else response
        except Exception as e:
            print(f"⚠️  Structured output not available or failed: {e}, falling back to manual parsing")
        
        # Fallback to manual parsing with PydanticOutputParser
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", synthesize_prompt),
            ("human", """Research Topic: {topic}

Research Content:
{content}

{format_instructions}

Generate a comprehensive research report with a short summary, detailed markdown report, and follow-up questions. Return the response in the exact JSON format specified above."""),
        ])
        
        prompt = prompt_template.format_messages(
            topic=research_topic,
            content=content,
            format_instructions=self.parser.get_format_instructions()
        )
        
        try:
            response = self.llm.invoke(prompt)
            response_content = response.content if hasattr(response, 'content') else str(response)
            
            # Debug: print response length
            if not response_content or len(response_content.strip()) == 0:
                print("⚠️  Warning: Empty response from LLM")
                return SynthesizeData(
                    short_summary="Unable to generate summary - empty response from model.",
                    markdown_report=f"# Research Report: {research_topic}\n\nUnable to generate report content. The model returned an empty response.",
                    follow_up_questions=[]
                )
            
            try:
                parsed = self.parser.parse(response_content)
                # Validate parsed content
                if not parsed.markdown_report or len(parsed.markdown_report.strip()) == 0:
                    print("⚠️  Warning: Parsed markdown_report is empty")
                    # Try to extract content from raw response
                    return self._extract_from_raw_response(response_content, research_topic)
                return parsed
            except Exception as parse_error:
                print(f"⚠️  Error parsing structured output: {parse_error}")
                print(f"   Response preview: {response_content[:200]}...")
                # Fallback: try to extract from raw response
                return self._extract_from_raw_response(response_content, research_topic)
                
        except Exception as e:
            print(f"❌ Error during synthesis: {e}")
            import traceback
            traceback.print_exc()
            # Fallback: return basic structure
            return SynthesizeData(
                short_summary="Summary generation failed.",
                markdown_report=f"# Research Report: {research_topic}\n\nError generating report: {str(e)}",
                follow_up_questions=[]
            )
    
    def _parse_response(self, content: str) -> SynthesizeData:
        """Try to parse response content into SynthesizeData"""
        try:
            return self.parser.parse(content)
        except:
            # If parsing fails, create a basic structure
            return self._extract_from_raw_response(content, "Research Topic")
    
    def _extract_from_raw_response(self, content: str, research_topic: str) -> SynthesizeData:
        """Extract content from raw LLM response when structured parsing fails"""
        # Try to find JSON in the response
        import json
        import re
        
        # Try to extract JSON block
        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        if json_match:
            try:
                json_data = json.loads(json_match.group())
                return SynthesizeData(
                    short_summary=json_data.get('short_summary', 'Summary not available.'),
                    markdown_report=json_data.get('markdown_report', content),
                    follow_up_questions=json_data.get('follow_up_questions', [])
                )
            except:
                pass
        
        # If no JSON found, use the entire content as the report
        # Try to extract summary from first paragraph
        lines = content.split('\n')
        summary = lines[0][:200] if lines else "Summary not available."
        
        return SynthesizeData(
            short_summary=summary,
            markdown_report=f"# Research Report: {research_topic}\n\n{content}",
            follow_up_questions=[]
        )
    
    def format_report(self, synthesize_data: SynthesizeData, research_topic: str) -> str:
        """
        Format the final report with all components
        
        Args:
            synthesize_data: The SynthesizeData object
            research_topic: The original research topic
            
        Returns:
            Formatted report string
        """
        # Clean markdown report (remove code block markers if present)
        clean_markdown = synthesize_data.markdown_report.strip()
        if clean_markdown.startswith("```"):
            # Remove markdown code block markers
            lines = clean_markdown.split("\n")
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines[-1].strip() == "```":
                lines = lines[:-1]
            clean_markdown = "\n".join(lines).strip()
        
        formatted = f"""# Research Report: {research_topic}

## Executive Summary

{synthesize_data.short_summary}

---

## Full Report

{clean_markdown}

---

## Follow-up Research Questions

"""
        for i, question in enumerate(synthesize_data.follow_up_questions, 1):
            formatted += f"{i}. {question}\n"
        
        formatted += "\n---\n\n*Report generated by Deep Research System*\n"
        
        return formatted
