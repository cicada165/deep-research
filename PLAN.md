# Architecture: Recursive Fact-Checking (Implemented)
**Status**: ✅ Implemented
**Date**: 2024-02-09


## ARCHITECT Analysis

### Current Retrieval Logic

The system follows a three-agent architecture:

1. **PlannerAgent** (`planner.py`): Generates 10 search queries based on the research topic
2. **ExecuteAgent** (`executor.py`): 
   - Performs web searches for each query (supports Qwen, Tavily, DuckDuckGo)
   - Summarizes search results into 2-3 paragraph summaries (<500 words)
   - Returns a dictionary mapping queries to summaries
3. **SynthesizeAgent** (`synthesizer.py`): 
   - Consolidates all search summaries
   - Generates a comprehensive markdown report (2000+ words)
   - Creates a short summary and follow-up questions

**Current Flow:**
```
Topic → Planner → [Query1, Query2, ...] → Executor → [Summary1, Summary2, ...] → Synthesizer → Final Report
```

### Problem Statement

The current system has no fact-checking mechanism:
- Facts are retrieved from single sources without verification
- No cross-referencing between sources
- No confidence scoring for claims
- No recursive verification of disputed facts

### Proposed Solution: Recursive Fact-Checking

Add a **FactCheckerAgent** that operates between Execution and Synthesis:

1. **Fact Extraction**: After Executor retrieves summaries, extract key factual claims
2. **Initial Verification**: For each claim, search for verification/contradiction
3. **Recursive Verification**: If a fact is disputed or has low confidence:
   - Generate targeted verification queries
   - Perform additional searches
   - Cross-reference multiple sources
   - Update confidence scores
4. **Fact Annotation**: Annotate facts with confidence levels and source counts
5. **Enhanced Synthesis**: Pass fact-checked data to Synthesizer with confidence metadata

**Enhanced Flow:**
```
Topic → Planner → [Query1, Query2, ...] 
  → Executor → [Summary1, Summary2, ...] 
  → FactChecker → [VerifiedSummary1, VerifiedSummary2, ...] (with confidence scores)
  → Synthesizer → Final Report (with fact-check annotations)
```

## Implementation Plan

### Phase 1: Create FactCheckerAgent

**File**: `deep_research/fact_checker.py`

**Components:**
1. `FactClaim` (Pydantic model): Represents a factual claim with:
   - `claim_text`: The factual statement
   - `confidence`: Float (0.0-1.0)
   - `source_count`: Number of sources confirming
   - `contradiction_count`: Number of sources contradicting
   - `verification_queries`: List of queries used to verify
   - `sources`: List of source URLs/identifiers

2. `FactCheckerAgent` class:
   - `extract_facts(summaries: Dict[str, str]) -> List[FactClaim]`: Extract factual claims from summaries
   - `verify_fact(claim: FactClaim) -> FactClaim`: Verify a single fact by searching
   - `recursive_verify(claim: FactClaim, max_depth: int = 2) -> FactClaim`: Recursively verify disputed facts
   - `fact_check_summaries(summaries: Dict[str, str]) -> Dict[str, str]`: Main entry point that:
     - Extracts facts from all summaries
     - Verifies each fact
     - Recursively verifies low-confidence facts
     - Returns enhanced summaries with fact-check annotations

**Configuration:**
- Add to `config.py`:
  - `fact_checker_enabled: bool = True`
  - `fact_checker_model: str = "gpt-4-turbo-preview"` (high-capability for fact extraction)
  - `fact_checker_max_depth: int = 2` (recursion depth)
  - `fact_checker_confidence_threshold: float = 0.6` (below this, trigger recursive verification)
  - `fact_checker_max_verification_queries: int = 3` (max queries per fact)

### Phase 2: Integrate with Orchestrator

**Modify**: `deep_research/orchestrator.py`

Add fact-checking step between execution and synthesis:
```python
# Step 2: Execution
search_results = self.executor.execute_search_queries(queries)

# Step 2.5: Fact-Checking (NEW)
if self.config.fact_checker_enabled:
    print("🔍 Step 2.5: Fact-checking and verification...")
    from .fact_checker import FactCheckerAgent
    fact_checker = FactCheckerAgent(self.config)
    verified_results = fact_checker.fact_check_summaries(search_results)
    search_results = verified_results  # Use verified results for synthesis
    print(f"   Verified facts with confidence scores\n")

# Step 3: Synthesis
synthesize_data = self.synthesizer.synthesize_report(topic, search_results)
```

### Phase 3: Enhance Synthesizer

**Modify**: `deep_research/synthesizer.py`

Update synthesis prompt to:
- Include confidence scores in the report
- Mark low-confidence facts with disclaimers
- Add a "Fact Verification" section to the report
- Use confidence metadata when available

### Phase 4: Update Manager

**Modify**: `deep_research/manager.py`

Ensure `DeepResearchManager` uses the fact-checking flow through `DeepResearch` orchestrator.

## Design Decisions

1. **Recursive Depth**: Limit to 2 levels to prevent infinite loops and control costs
2. **Confidence Threshold**: 0.6 - facts below this trigger recursive verification
3. **Fact Extraction**: Use LLM to extract factual claims (statements that can be verified)
4. **Verification Strategy**: 
   - For each fact, generate 2-3 targeted verification queries
   - Search and count confirmations vs contradictions
   - Calculate confidence: `confirmations / (confirmations + contradictions + 1)`
5. **Integration Point**: Between Executor and Synthesizer to maintain clean separation
6. **Backward Compatibility**: Make fact-checking optional via config flag

## Testing Strategy

1. Unit tests for `FactCheckerAgent`:
   - Test fact extraction
   - Test confidence calculation
   - Test recursive verification logic
2. Integration tests:
   - Test full flow with fact-checking enabled/disabled
   - Verify fact annotations appear in final report
3. Manual testing:
   - Run on a topic with known facts
   - Verify confidence scores are reasonable
   - Check that disputed facts trigger recursive verification

## Files to Create/Modify

**New Files:**
- `deep_research/fact_checker.py` - FactCheckerAgent implementation

**Modified Files:**
- `deep_research/config.py` - Add fact-checker configuration
- `deep_research/orchestrator.py` - Integrate fact-checking step
- `deep_research/synthesizer.py` - Enhance to use confidence metadata
- `deep_research/__init__.py` - Export FactCheckerAgent if needed

**Test Files:**
- `test_fact_checker.py` - Unit tests for fact-checker
