# REVIEWER AUDIT REPORT: Streamlit Interface

**Date**: Current Review  
**Auditor**: Reviewer (PhD-level Research Auditor)  
**Scope**: Streamlit Frontend UI Audit

---

## EXECUTIVE SUMMARY

The Streamlit interface has been implemented with basic functionality, but **critical issues prevent proper source citation display** and **error handling is insufficient**. The UI does not correctly display source URLs because the backend does not preserve them through the summarization pipeline.

**Overall Status**: ❌ **REQUIRES FIXES**

---

## 1. HALLUCINATION CHECK: Source URL Display

### ❌ CRITICAL ISSUE: Source URLs Not Preserved

**Problem**: The UI attempts to extract URLs from the markdown report using regex (`utils/ui_components.py:96-98`), but this approach is fundamentally flawed:

1. **Backend Data Loss**: The `ExecuteAgent` collects URLs during search (`executor.py:298`) but **discards them during summarization**. The LLM summary prompt (`executor.py:345-354`) does not require preserving source URLs.

2. **No Structured Data**: The `SynthesizeData` model (`synthesizer.py:37-41`) has no field for source URLs or citations. The executor returns `Dict[str, str]` (query → summary) with no URL metadata.

3. **Unreliable Extraction**: The UI's regex extraction (`ui_components.py:97-98`) will miss URLs that:
   - Are embedded in markdown links `[text](url)` 
   - Are formatted differently
   - Were never included in the summary

**Evidence**:
```python
# utils/ui_components.py:96-98
urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', 
                synthesize_data.markdown_report)
```
This regex only finds bare URLs, not markdown-formatted links.

**Impact**: Users cannot verify claims because source URLs are not displayed, violating the core requirement that "every claim has a source URL."

---

## 2. UX EVALUATION: Error Handling

### ⚠️ INSUFFICIENT ERROR HANDLING

#### 2.1 Search API Failure Handling

**Issues Found**:

1. **Generic Error Messages**: When search fails, the executor returns generic strings like `"Search failed for query: {query}"` (`executor.py:297, 319, 383`), but these are not clearly communicated to users in the UI.

2. **Silent Failures**: In `app.py:208-281`, the research thread catches exceptions but updates session state in a way that may not trigger UI updates reliably. The comment on line 220 notes: "Direct session state updates from threads may not always work."

3. **No Partial Failure Handling**: If some searches succeed and others fail, the UI doesn't indicate which queries failed or why. The executor logs warnings (`executor.py:123-124`) but doesn't surface them to the UI.

4. **No Retry Mechanism**: Search failures immediately stop the process. No retry logic for transient network errors.

**Specific Problems**:

```python
# app.py:270-281
except Exception as e:
    import traceback
    try:
        st.session_state["research_status"] = {
            "is_running": False,
            "current_step": "error",
            "progress": 0.0,
            "status_message": f"Error: {str(e)}",
            "error": str(e),
        }
    except Exception:
        pass  # ⚠️ Silent failure - error may not be displayed
```

**Recommendation**: Add explicit error display components and handle partial search failures gracefully.

#### 2.2 Configuration Validation Errors

**Status**: ✅ **GOOD** - Configuration validation errors are caught and displayed (`app.py:216-228`), but they're only shown in the research status, not prominently in the sidebar.

#### 2.3 Network/API Key Errors

**Status**: ⚠️ **PARTIAL** - API key validation happens in `validate_config()`, but:
- Errors are generic ("API key required")
- No guidance on which specific key is missing
- No test connection button to verify keys before research starts

---

## 3. UI CLUTTER & CITATION DISPLAY

### ❌ CITATIONS HIDDEN BY DEFAULT

**Problem**: Citations are in a collapsed expander (`ui_components.py:89`):
```python
with st.expander("📚 Citations & Sources", expanded=False):
```

**Impact**: Users must actively expand to see sources, making it easy to miss missing citations.

### ⚠️ PLACEHOLDER MESSAGES

**Problem**: When no citations are found, the UI shows a vague message:
```python
# ui_components.py:104
st.info("Citations will be displayed here when available. The research system is working on extracting source citations.")
```

**Issue**: This message doesn't indicate that citations are **missing** (a critical problem), but rather suggests they're "coming soon."

### ⚠️ NO SOURCE METADATA

**Missing Information**:
- No source titles displayed
- No domain information
- No retrieval dates
- No reliability scores
- No indication of which claims each source supports

---

## 4. DETAILED FINDINGS

### 4.1 Backend Data Flow Issues

| Component | Issue | Severity |
|-----------|-------|----------|
| `ExecuteAgent.execute_search()` | Returns only summary string, loses URLs | 🔴 CRITICAL |
| `ExecuteAgent.execute_search_queries()` | Returns `Dict[str, str]` with no URL metadata | 🔴 CRITICAL |
| `SynthesizeData` model | No `sources` or `references` field | 🔴 CRITICAL |
| `Synthesizer.synthesize_report()` | Receives no source URLs, cannot include them | 🔴 CRITICAL |

### 4.2 UI Display Issues

| Component | Issue | Severity |
|-----------|-------|----------|
| `render_citations()` | Relies on unreliable regex extraction | 🔴 CRITICAL |
| `render_citations()` | Citations collapsed by default | 🟡 MEDIUM |
| `render_research_report()` | No in-text citations displayed | 🟡 MEDIUM |
| Error display | Errors may not be visible if session state update fails | 🟡 MEDIUM |

### 4.3 Error Handling Gaps

| Scenario | Current Handling | Required Handling |
|----------|------------------|-------------------|
| Search API timeout | Generic error message | Specific timeout error with retry option |
| Partial search failures | Logged but not shown | Display which queries failed |
| Invalid API keys | Validated but generic message | Show which key is invalid |
| Network errors | Caught but may not display | Prominent error banner |
| Empty search results | Returns error string | Clear "no results" message with suggestions |

---

## 5. REQUIRED FIXES

### 🔴 CRITICAL FIXES (Must Fix Before Approval)

#### Fix 1: Preserve Source URLs in Backend
**File**: `deep_research/executor.py`

**Required Changes**:
1. Modify `execute_search_queries()` to return structured data:
   ```python
   Dict[str, Dict[str, Any]]  # query → {summary: str, sources: List[Dict[url, title, domain]]}
   ```

2. Update `_execute_duckduckgo_search()` to preserve URLs:
   - Collect `SearchResult` objects with URLs
   - Include URLs in summary prompt: "Include source URLs in format: [1] Title (URL)"
   - Return both summary and source list

3. Update `_execute_qwen_search()` and `_execute_tavily_search()` similarly

**Assigned to**: @Coder

---

#### Fix 2: Add Source Data to SynthesizeData
**File**: `deep_research/synthesizer.py`

**Required Changes**:
1. Add `references` field to `SynthesizeData`:
   ```python
   references: List[Dict[str, str]] = Field(
       default_factory=list,
       description="List of source references with url, title, domain"
   )
   ```

2. Update `synthesize_report()` to:
   - Extract sources from search_results
   - Pass sources to LLM with instruction to include in-text citations
   - Populate `references` field in response

**Assigned to**: @Coder

---

#### Fix 3: Fix Citation Display in UI
**File**: `utils/ui_components.py`

**Required Changes**:
1. Update `render_citations()` to use structured data:
   ```python
   if synthesize_data.references:
       for i, ref in enumerate(synthesize_data.references, 1):
           st.markdown(f"[{i}] **{ref.get('title', 'Source')}**")
           st.markdown(f"    {ref.get('url', '')}")
           if ref.get('domain'):
               st.caption(f"Domain: {ref.get('domain')}")
   ```

2. Change expander to `expanded=True` by default

3. Show warning if no citations: `st.warning("⚠️ No source citations found. This report cannot be verified.")`

**Assigned to**: @Coder

---

### 🟡 MEDIUM PRIORITY FIXES

#### Fix 4: Improve Error Handling
**Files**: `app.py`, `utils/researcher.py`

**Required Changes**:
1. Add error display component in main UI (not just in status)
2. Show partial search failures with list of failed queries
3. Add "Test API Keys" button in sidebar
4. Add retry button for failed searches
5. Display network errors prominently

**Assigned to**: @Coder or @Debugger

---

#### Fix 5: Add In-Text Citations
**File**: `utils/ui_components.py`

**Required Changes**:
1. Parse markdown report for citation markers `[1]`, `[2]`, etc.
2. Display citations inline with tooltips or expandable details
3. Link citations to bibliography section

**Assigned to**: @Coder

---

#### Fix 6: Improve Citation Visibility
**File**: `utils/ui_components.py`

**Required Changes**:
1. Add citation count badge: "📚 5 Sources"
2. Show citation status: "✅ All claims cited" or "⚠️ Missing citations"
3. Make citations section more prominent (not just expander)

**Assigned to**: @Coder

---

## 6. TESTING REQUIREMENTS

Before approval, verify:

1. ✅ **Source URL Preservation Test**:
   - Run research query
   - Verify all source URLs are displayed in citations section
   - Verify URLs match the sources used in the report

2. ✅ **Error Handling Test**:
   - Disable network / invalid API key
   - Verify clear error message displayed
   - Verify error persists across page refreshes

3. ✅ **Partial Failure Test**:
   - Simulate some searches failing
   - Verify UI shows which queries failed
   - Verify report still generates with available results

4. ✅ **Citation Display Test**:
   - Verify citations are visible without expanding
   - Verify all claims in report have corresponding citations
   - Verify citation format is readable

---

## 7. RECOMMENDATION

**Status**: ❌ **REJECT - REQUIRES FIXES**

The Streamlit interface cannot be approved until:
1. Source URLs are preserved and displayed (Critical Fixes 1-3)
2. Error handling is improved (Medium Fix 4)
3. Citations are visible and properly formatted (Medium Fixes 5-6)

**Next Steps**:
1. @Coder: Implement Critical Fixes 1-3
2. @Coder or @Debugger: Implement Medium Priority Fixes 4-6
3. Resubmit for review after fixes

---

## 8. POSITIVE OBSERVATIONS

✅ **Good Practices Found**:
- Session state management is well-structured
- Progress indicators provide good UX
- Error tracking in `ResearchSession` is comprehensive
- Thread-safe research execution is properly implemented
- Configuration validation is in place

✅ **UI Structure**:
- Clean sidebar organization
- Good use of tabs for navigation
- Research history is well-implemented
- Export functionality is present

---

**End of Audit Report**
