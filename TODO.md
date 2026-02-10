# Project Tasks

## ✅ Completed
- [x] **Fact-Checker Agent** (@Coder)
  - Implemented `deep_research/fact_checker.py`
  - Integrated into `deep_research/orchestrator.py`
  - Added recursive verification logic
- [x] **Streamlit Frontend** (@Coder)
  - Implemented `app.py`
  - Added session state management (`utils/session_manager.py`)
  - Added config builder (`utils/config_builder.py`)
  - Added UI components (`utils/ui_components.py`)
- [x] **System Verification** (@Reviewer)
  - Verified `test_system.py` passes
  - Verified `test_script.py` passes
  - Fixed `duckduckgo_search` deprecation warning

## 🚧 In Progress
- [ ] **Documentation Updates** (@Architect)
  - [x] `README.md` (Up to date)
  - [ ] Update `PLAN.md` status
  - [ ] Update `SPECS.md` status

## 📋 Backlog / Future Improvements
- [ ] Add support for "DeepSeek" search method (currently just a placeholder in config)
- [ ] Implement persistent database for research history (currently in-memory)
- [ ] Add PDF export functionality (currently Markdown only)
