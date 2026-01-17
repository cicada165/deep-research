"""
Fact Checker Agent - Verifies factual claims with recursive verification
"""

from typing import Dict, List, Optional, Set
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from datetime import datetime
from .config import Config
from .executor import ExecuteAgent


class VerificationSource(BaseModel):
    """Represents a source used for verification"""
    query: str
    url: Optional[str] = None
    title: Optional[str] = None
    domain: Optional[str] = None
    summary: Optional[str] = None
    reliability_score: float = 0.5
    verification_result: str = "neutral"  # "confirm", "contradict", "neutral"
    depth: int = 0
    verified_at: str = ""


class FactClaim(BaseModel):
    """Represents a factual claim with verification metadata"""
    claim_text: str
    confidence: float = 0.5  # 0.0-1.0
    source_count: int = 0
    contradiction_count: int = 0
    verification_queries: List[str] = []
    sources: List[str] = []  # Legacy field for backward compatibility
    verification_sources: List[VerificationSource] = []  # Enhanced source tracking
    verification_depth: int = 0  # Maximum depth reached
    verification_history: List[Dict] = []  # Track verification attempts at each depth


class FactCheckerAgent:
    """
    Fact Checker Agent that verifies factual claims from search summaries.
    
    The agent:
    1. Extracts factual claims from summaries
    2. Verifies each claim by searching for confirmation/contradiction
    3. Recursively verifies disputed or low-confidence facts
    4. Returns enhanced summaries with confidence annotations
    """
    
    def __init__(self, config: Config):
        self.config = config
        self.executor = ExecuteAgent(config)  # Reuse executor for verification searches
        
        # Initialize LLM for fact extraction and analysis
        if config.openai_api_key:
            self.llm = ChatOpenAI(
                model=config.fact_checker_model,
                temperature=config.fact_checker_temperature,
                api_key=config.openai_api_key
            )
        elif config.anthropic_api_key:
            self.llm = ChatAnthropic(
                model=config.fact_checker_model if "claude" in config.fact_checker_model.lower() else "claude-3-5-sonnet-20241022",
                temperature=config.fact_checker_temperature,
                api_key=config.anthropic_api_key
            )
        else:
            raise ValueError("No API key available for fact checker. Please set OPENAI_API_KEY or ANTHROPIC_API_KEY")
    
    def extract_facts(self, summaries: Dict[str, str]) -> List[FactClaim]:
        """
        Extract factual claims from search summaries with improved extraction
        
        Args:
            summaries: Dictionary mapping queries to summaries
            
        Returns:
            List of FactClaim objects
        """
        # Combine all summaries
        combined_text = "\n\n".join([f"Query: {q}\nSummary: {s}" for q, s in summaries.items()])
        
        # Use LLM to extract factual claims with improved prompt
        extraction_prompt = """You are a fact extraction assistant. Extract factual claims from the following research summaries.

A factual claim is a specific, verifiable statement. Good examples:
- "The population of Tokyo is 14 million" (specific number, verifiable)
- "The study was published in Nature in 2023" (specific publication, date)
- "Machine learning models achieved 95% accuracy in the benchmark" (specific metric)
- "The research involved 1,200 participants from 5 countries" (specific numbers)

Avoid extracting:
- Vague statements: "AI is transforming education" (too general)
- Opinions: "This is the best approach" (subjective)
- Predictions: "This will revolutionize the field" (future-oriented)
- Broad trends without specifics

For each factual claim, extract:
1. The specific factual statement (be precise)
2. The context (which query/summary it came from)

Return a JSON list of claims, each with:
- claim_text: The factual statement (be specific and precise)
- context: Brief context about where it came from

Focus on extracting 5-10 of the most important, verifiable facts from the summaries.

Research Summaries:
{summaries}

Return only a JSON list, no additional text."""

        prompt_template = ChatPromptTemplate.from_messages([
            ("system", "You are a precise fact extraction assistant. Extract specific, verifiable facts. Return only valid JSON."),
            ("human", extraction_prompt),
        ])
        
        try:
            prompt = prompt_template.format_messages(summaries=combined_text[:8000])  # Limit length
            response = self.llm.invoke(prompt)
            response_text = response.content.strip() if hasattr(response, 'content') else str(response).strip()
            
            # Try to parse JSON response
            import json
            # Remove markdown code blocks if present
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            claims_data = json.loads(response_text)
            
            # Convert to FactClaim objects
            facts = []
            for claim_data in claims_data:
                if isinstance(claim_data, dict) and "claim_text" in claim_data:
                    facts.append(FactClaim(
                        claim_text=claim_data["claim_text"],
                        confidence=0.5,  # Initial confidence
                        sources=[claim_data.get("context", "")],
                        verification_sources=[],
                        verification_history=[]
                    ))
            
            return facts
            
        except Exception as e:
            print(f"⚠️  Error extracting facts: {e}")
            # Fallback: return empty list
            return []
    
    def verify_fact(self, claim: FactClaim, depth: int = 0, previous_results: Optional[List[VerificationSource]] = None) -> FactClaim:
        """
        Verify a single fact by searching for confirmation/contradiction with enhanced source tracking
        
        Args:
            claim: The FactClaim to verify
            depth: Current recursion depth
            previous_results: Results from previous verification rounds (for cross-referencing)
            
        Returns:
            Updated FactClaim with confidence scores and source metadata
        """
        if depth >= self.config.fact_checker_max_depth:
            return claim
        
        # Generate verification queries (more targeted at deeper levels)
        if depth > 0 and previous_results:
            # Use previous results to generate more targeted queries
            previous_summaries = "\n".join([f"- {r.summary[:200]}" for r in previous_results if r.summary][:3])
            verification_prompt = """Generate 2-3 highly specific search queries to verify this factual claim, considering previous verification attempts.

Claim: {claim}

Previous verification results:
{previous_results}

Generate queries that would:
- Find authoritative sources (academic, government, reputable news)
- Verify specific numbers, dates, or statistics mentioned
- Cross-reference with multiple independent sources
- Focus on finding definitive evidence

Return a JSON list of query strings, no additional text."""
            prompt_template = ChatPromptTemplate.from_messages([
                ("system", "You are a fact verification assistant. Generate targeted verification queries. Return only valid JSON."),
                ("human", verification_prompt),
            ])
            prompt = prompt_template.format_messages(
                claim=claim.claim_text,
                previous_results=previous_summaries
            )
        else:
            verification_prompt = """Generate 2-3 specific search queries to verify this factual claim.

Claim: {claim}

Generate queries that would help verify if this claim is true or false.
Focus on queries that would find:
- Confirmation of the claim from authoritative sources
- Contradiction of the claim
- Specific data or evidence

Return a JSON list of query strings, no additional text."""
            prompt_template = ChatPromptTemplate.from_messages([
                ("system", "You are a fact verification assistant. Return only valid JSON."),
                ("human", verification_prompt),
            ])
            prompt = prompt_template.format_messages(claim=claim.claim_text)
        
        try:
            response = self.llm.invoke(prompt)
            response_text = response.content.strip() if hasattr(response, 'content') else str(response).strip()
            
            # Parse JSON
            import json
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            queries = json.loads(response_text)
            if not isinstance(queries, list):
                queries = [queries] if queries else []
            
            # Limit number of queries
            queries = queries[:self.config.fact_checker_max_verification_queries]
            if depth == 0:
                claim.verification_queries = queries
            
            # Perform verification searches with source tracking
            confirmations = 0
            contradictions = 0
            verification_sources_at_depth = []
            
            for query in queries:
                try:
                    summary = self.executor.execute_search(query)
                    
                    # Analyze if summary confirms or contradicts
                    analysis_prompt = """Analyze if the following search result confirms or contradicts the factual claim.

Claim: {claim}

Search Result:
{result}

Respond with ONLY one word: "confirm", "contradict", or "neutral"."""

                    analysis_template = ChatPromptTemplate.from_messages([
                        ("human", analysis_prompt),
                    ])
                    
                    analysis_prompt_msg = analysis_template.format_messages(
                        claim=claim.claim_text,
                        result=summary[:1000]
                    )
                    
                    analysis_response = self.llm.invoke(analysis_prompt_msg)
                    analysis = analysis_response.content.strip().lower() if hasattr(analysis_response, 'content') else str(analysis_response).strip().lower()
                    
                    result_type = "neutral"
                    if "confirm" in analysis:
                        confirmations += 1
                        result_type = "confirm"
                    elif "contradict" in analysis:
                        contradictions += 1
                        result_type = "contradict"
                    
                    # Create verification source with metadata
                    verification_source = VerificationSource(
                        query=query,
                        summary=summary,
                        verification_result=result_type,
                        depth=depth,
                        verified_at=datetime.now().isoformat(),
                        reliability_score=0.6  # Default, could be enhanced with domain analysis
                    )
                    verification_sources_at_depth.append(verification_source)
                    claim.verification_sources.append(verification_source)
                    
                    # Legacy field for backward compatibility
                    claim.sources.append(f"Query: {query} (depth {depth}, {result_type})")
                    
                except Exception as e:
                    print(f"⚠️  Error verifying fact with query '{query}': {e}")
                    continue
            
            # Enhanced confidence calculation
            total = confirmations + contradictions
            if total > 0:
                # Base confidence from confirmations
                base_confidence = confirmations / (total + 1)
                
                # Boost confidence based on source diversity and depth
                source_diversity_bonus = min(len(verification_sources_at_depth) * 0.05, 0.1)
                depth_bonus = depth * 0.02  # Slight boost for deeper verification
                
                # Weight by source reliability (if available)
                reliability_weight = sum(s.reliability_score for s in verification_sources_at_depth) / len(verification_sources_at_depth) if verification_sources_at_depth else 0.5
                reliability_bonus = (reliability_weight - 0.5) * 0.1
                
                claim.confidence = min(base_confidence + source_diversity_bonus + depth_bonus + reliability_bonus, 1.0)
            else:
                claim.confidence = 0.3  # Low confidence if no verification found
            
            # Update counts (accumulate across depths)
            claim.source_count += confirmations
            claim.contradiction_count += contradictions
            claim.verification_depth = max(claim.verification_depth, depth)
            
            # Record verification history
            claim.verification_history.append({
                "depth": depth,
                "confirmations": confirmations,
                "contradictions": contradictions,
                "confidence": claim.confidence,
                "sources_count": len(verification_sources_at_depth)
            })
            
            return claim
            
        except Exception as e:
            print(f"⚠️  Error verifying fact: {e}")
            claim.confidence = 0.3  # Low confidence on error
            return claim
    
    def recursive_verify(self, claim: FactClaim, max_depth: int = None, current_depth: int = 0, visited_claims: Optional[Set[str]] = None) -> FactClaim:
        """
        Recursively verify a fact if confidence is below threshold with true multi-level recursion
        
        Args:
            claim: The FactClaim to verify
            max_depth: Maximum recursion depth (uses config if None)
            current_depth: Current recursion depth (internal use)
            visited_claims: Set of claim texts already verified to prevent loops (internal use)
            
        Returns:
            Updated FactClaim with improved confidence
        """
        if max_depth is None:
            max_depth = self.config.fact_checker_max_depth
        
        if visited_claims is None:
            visited_claims = set()
        
        # Prevent infinite loops by tracking visited claims
        claim_key = claim.claim_text.lower().strip()[:100]  # Normalize for comparison
        if claim_key in visited_claims and current_depth > 0:
            return claim
        visited_claims.add(claim_key)
        
        # Perform verification at current depth
        previous_results = [s for s in claim.verification_sources if s.depth < current_depth]
        claim = self.verify_fact(claim, depth=current_depth, previous_results=previous_results)
        
        # Recursively verify if confidence is still below threshold and we haven't reached max depth
        if (claim.confidence < self.config.fact_checker_confidence_threshold and 
            current_depth < max_depth - 1):
            # Recursive call with incremented depth
            claim = self.recursive_verify(
                claim, 
                max_depth=max_depth, 
                current_depth=current_depth + 1,
                visited_claims=visited_claims
            )
        
        return claim
    
    def fact_check_summaries(self, summaries: Dict[str, str]) -> Dict[str, str]:
        """
        Main entry point: fact-check all summaries and return enhanced versions
        
        Args:
            summaries: Dictionary mapping queries to summaries
            
        Returns:
            Enhanced summaries with fact-check annotations
        """
        if not self.config.fact_checker_enabled:
            return summaries
        
        print("   Extracting factual claims...")
        facts = self.extract_facts(summaries)
        print(f"   Found {len(facts)} factual claims to verify")
        
        if not facts:
            return summaries
        
        # Verify each fact
        verified_facts = []
        for i, fact in enumerate(facts, 1):
            print(f"   [{i}/{len(facts)}] Verifying: {fact.claim_text[:60]}...")
            verified_fact = self.recursive_verify(fact)
            verified_facts.append(verified_fact)
        
        # Enhance summaries with confidence annotations
        enhanced_summaries = {}
        for query, summary in summaries.items():
            # Find facts related to this summary
            relevant_facts = [f for f in verified_facts if query in str(f.sources)]
            
            # Add confidence annotations
            if relevant_facts:
                low_confidence_facts = [f for f in relevant_facts if f.confidence < self.config.fact_checker_confidence_threshold]
                
                if low_confidence_facts:
                    annotation = f"\n\n[Fact-checking note: Some claims in this summary have low confidence scores (<{self.config.fact_checker_confidence_threshold}). Please verify independently.]"
                    enhanced_summaries[query] = summary + annotation
                else:
                    enhanced_summaries[query] = summary
            else:
                enhanced_summaries[query] = summary
        
        # Print summary
        high_conf = sum(1 for f in verified_facts if f.confidence >= self.config.fact_checker_confidence_threshold)
        print(f"   Verified {len(verified_facts)} facts: {high_conf} high-confidence, {len(verified_facts) - high_conf} low-confidence")
        
        return enhanced_summaries
