# Qualtrics Util Refactoring Plan

## Current State Analysis

**File:** `qualtrics_util.py` (1,892 lines, 33 methods)

**Issues:**
- Single monolithic class with mixed responsibilities
- No separation of concerns (API, business logic, CLI)
- Hard to test individual components
- Difficult to maintain and extend
- No proper error handling layer
- Configuration mixed with business logic

**Strengths:**
- Functional code that works
- Clear command interface
- Comprehensive feature set

## Refactoring Goals

1. **Modularity**: Separate concerns into focused modules
2. **Testability**: Enable unit testing of individual components
3. **Maintainability**: Make code easier to understand and modify
4. **Extensibility**: Make it easier to add new features
5. **Documentation**: Add comprehensive docstrings and type hints

## Proposed Structure

```
qualtrics_util/
├── src/
│   └── qualtrics_util/
│       ├── __init__.py              # Package initialization
│       ├── __main__.py              # CLI entry point
│       ├── cli.py                   # Argument parsing & CLI logic
│       ├── config.py                # Configuration management
│       ├── api/
│       │   ├── __init__.py
│       │   ├── base.py              # Base API client with auth
│       │   ├── contacts.py          # Contact list operations
│       │   ├── distributions.py     # Distribution operations
│       │   ├── surveys.py           # Survey operations
│       │   └── messages.py          # Message library operations
│       ├── services/
│       │   ├── __init__.py
│       │   ├── scheduler.py         # SMS/Email scheduling logic
│       │   └── exporter.py          # Survey data export
│       ├── models/
│       │   ├── __init__.py
│       │   └── embedded_data.py    # Embedded data helpers
│       └── utils/
│           ├── __init__.py
│           ├── datetime_utils.py    # Time/date/timezone helpers
│           └── validators.py        # Input validation
├── tests/
│   ├── __init__.py
│   ├── test_config.py
│   ├── test_api/
│   │   ├── test_contacts.py
│   │   ├── test_distributions.py
│   │   └── test_surveys.py
│   ├── test_services/
│   │   ├── test_scheduler.py
│   │   └── test_exporter.py
│   └── integration/
│       └── test_cli.py
├── config/
│   └── *.yaml                       # Move all config files here
├── .github/
│   └── workflows/
│       └── build.yml                # Keep existing CI/CD
├── setup.py                         # Package setup
├── pyproject.toml                   # Modern Python packaging
├── requirements.txt
└── README.md
```

## Phase-by-Phase Refactoring Plan

### Phase 1: Foundation & Configuration ✅
**Goal:** Create new structure without breaking existing functionality

**Tasks:**
1. Create new directory structure
2. Extract configuration management
3. Set up package structure
4. Create basic modules (empty shells)
5. Keep original file working

**Deliverable:** Structure exists, original code still works

---

### Phase 2: API Layer Extraction 🔄
**Goal:** Extract and modularize API interactions

**Tasks:**
1. Create `api/base.py` - Authentication and base API client
2. Create `api/contacts.py` - Contact list operations
3. Create `api/distributions.py` - Distribution operations
4. Create `api/surveys.py` - Survey operations
5. Create `api/messages.py` - Message library operations
6. Add error handling and logging

**Deliverable:** API layer fully extracted with tests

---

### Phase 3: Service Layer Extraction
**Goal:** Extract business logic from the monolithic class

**Tasks:**
1. Create `services/scheduler.py` - SMS/Email scheduling
2. Create `services/exporter.py` - Survey data export
3. Extract `models/embedded_data.py` - Embedded data helpers
4. Create `utils/datetime_utils.py` - Time/timezone utilities
5. Create `utils/validators.py` - Input validation

**Deliverable:** Business logic separated into focused services

---

### Phase 4: CLI & Integration
**Goal:** Refactor CLI and integrate all components

**Tasks:**
1. Create `cli.py` - Argument parsing and routing
2. Create `__main__.py` - Entry point
3. Wire everything together
4. Update imports and dependencies
5. Ensure backward compatibility

**Deliverable:** Fully refactored CLI with new structure

---

### Phase 5: Testing & Documentation
**Goal:** Add comprehensive tests and documentation

**Tasks:**
1. Write unit tests for all modules
2. Add integration tests
3. Write/update docstrings (Google-style)
4. Add type hints throughout
5. Update README with new structure
6. Create developer documentation

**Deliverable:** Well-tested, documented codebase

---

### Phase 6: Cleanup & Migration
**Goal:** Remove old code and finalize

**Tasks:**
1. Archive old `qualtrics_util.py`
2. Update all references
3. Update CI/CD for new structure
4. Create migration guide
5. Final testing and validation

**Deliverable:** Production-ready refactored codebase

---

## Detailed Task Breakdown

### Phase 1: Foundation (Current)

#### Task 1.1: Create Directory Structure
- [ ] Create `src/qualtrics_util/` directory
- [ ] Create subdirectories: `api/`, `services/`, `models/`, `utils/`
- [ ] Create `tests/` directory with matching structure
- [ ] Add `__init__.py` files

#### Task 1.2: Extract Configuration
- [ ] Create `config.py` for config loading
- [ ] Move config files to `config/` directory
- [ ] Add configuration validation
- [ ] Add environment variable handling

#### Task 1.3: Setup Package
- [ ] Create `__init__.py` with version info
- [ ] Create basic module files (stubs)
- [ ] Update imports in original file (temporary)
- [ ] Test that nothing breaks

**Time Estimate:** 1-2 hours

---

### Phase 2: API Layer

#### Task 2.1: Base API Client
- [ ] Extract authentication logic
- [ ] Create base API client class
- [ ] Add error handling
- [ ] Add request/response logging
- [ ] Write tests

#### Task 2.2: Contacts API
- [ ] Extract contact list operations
- [ ] Create ContactsAPI class
- [ ] Add methods: get, update, create
- [ ] Add embedded data handling
- [ ] Write tests

#### Task 2.3: Distributions API
- [ ] Extract distribution operations
- [ ] Create DistributionsAPI class
- [ ] Support both SMS and Email
- [ ] Add delete operations
- [ ] Write tests

#### Task 2.4: Surveys API
- [ ] Extract survey operations
- [ ] Create SurveysAPI class
- [ ] Add export functionality
- [ ] Write tests

**Time Estimate:** 4-6 hours

---

### Phase 3: Service Layer

#### Task 3.1: Scheduler Service
- [ ] Extract scheduling logic
- [ ] Create SchedulerService class
- [ ] Support time slots and ranges
- [ ] Handle timezone conversion
- [ ] Write tests

#### Task 3.2: Exporter Service
- [ ] Extract export logic
- [ ] Create ExporterService class
- [ ] Support multiple formats
- [ ] Add progress tracking
- [ ] Write tests

**Time Estimate:** 3-4 hours

---

### Phase 4: CLI & Integration

#### Task 4.1: CLI Module
- [ ] Create `cli.py` with argument parsing
- [ ] Route commands to appropriate services
- [ ] Add help text and usage
- [ ] Handle command errors

#### Task 4.2: Integration
- [ ] Wire all modules together
- [ ] Update `__main__.py`
- [ ] Test all CLI commands
- [ ] Ensure backward compatibility

**Time Estimate:** 2-3 hours

---

### Phase 5: Testing & Documentation

#### Task 5.1: Unit Tests
- [ ] Test API modules
- [ ] Test service modules
- [ ] Test utility functions
- [ ] Aim for 80%+ coverage

#### Task 5.2: Documentation
- [ ] Add docstrings to all functions
- [ ] Add type hints
- [ ] Update README
- [ ] Create API documentation

**Time Estimate:** 4-6 hours

---

### Phase 6: Cleanup

#### Task 6.1: Migration
- [ ] Archive old file
- [ ] Update all references
- [ ] Update CI/CD
- [ ] Create migration guide

**Time Estimate:** 1-2 hours

---

## Testing Strategy

### Unit Tests
- Test each module in isolation
- Mock external dependencies (API calls)
- Test edge cases and error conditions

### Integration Tests
- Test complete workflows
- Test CLI commands end-to-end
- Test configuration loading

### Test Coverage Goal
- Minimum 80% code coverage
- 100% coverage for critical paths

## Implementation Guidelines

### Code Quality Standards
- Follow PEP 8 style guide
- Use type hints (PEP 484)
- Write comprehensive docstrings (Google style)
- Keep functions under 30 lines
- Maximum cyclomatic complexity of 10

### Commit Strategy
- Commit after each completed task
- Use conventional commit messages
- Create feature branches for each phase
- Merge to main after testing

### Documentation Standards
- Google-style docstrings
- Include examples in docstrings
- Update README for each phase
- Maintain CHANGELOG

## Risk Mitigation

### Breaking Changes
- **Strategy:** Keep original file working throughout refactor
- **Backup:** Git version control for all changes
- **Testing:** Test after each phase

### API Changes
- **Strategy:** Maintain backward compatible API
- **Approach:** Add new API while keeping old one

### Testing Gaps
- **Strategy:** Add tests incrementally
- **Approach:** Test-driven development where possible

## Success Criteria

- [ ] All original functionality preserved
- [ ] Code is modular and testable
- [ ] 80%+ test coverage
- [ ] Documentation complete
- [ ] CI/CD working
- [ ] No performance degradation
- [ ] Backward compatibility maintained

## Timeline Estimate

- **Phase 1:** 1-2 hours
- **Phase 2:** 4-6 hours
- **Phase 3:** 3-4 hours
- **Phase 4:** 2-3 hours
- **Phase 5:** 4-6 hours
- **Phase 6:** 1-2 hours

**Total:** 15-23 hours

## Next Steps

1. Review and approve this plan
2. Create Phase 1 feature branch
3. Begin Phase 1 implementation
4. Review and iterate

---

**Questions for Discussion:**
1. Should we maintain backward compatibility with the old structure?
2. What testing framework should we use? (pytest recommended)
3. Should we add type checking? (mypy recommended)
4. What's the priority: speed or thoroughness?

