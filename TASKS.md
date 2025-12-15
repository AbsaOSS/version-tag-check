# Implementation Tasks: Version Qualifier Support

This document breaks down the implementation of version qualifier support as specified in [`docs/qualifier-spec.md`](docs/qualifier-spec.md) into detailed, actionable tasks.

**Related Issues:**
- [#5 – Add support for qualifiers and their validation](https://github.com/AbsaOSS/version-tag-check/issues/5)
- [#38 – Spike: Integrate new version qualifier validation spec into repo documentation and workflow](https://github.com/AbsaOSS/version-tag-check/issues/38)

**Specification Reference:** [`docs/qualifier-spec.md`](docs/qualifier-spec.md)

---

## Task Breakdown

### Phase 1: Core Version Model Enhancement

#### Task 1.1: Extend Version Class to Support Qualifiers
**Priority:** High  
**Estimated Effort:** 2-3 hours  
**Spec Reference:** Section 2.2, 3

**Description:**
Enhance the `Version` class in `version_tag_check/version.py` to parse and store qualifier information.

**Requirements:**
- Update `VERSION_REGEX` to capture optional qualifier: `^v(\d+)\.(\d+)\.(\d+)(?:-([A-Z0-9]+))?$`
  - Note: The qualifier pattern `[A-Z0-9]+` is intentionally permissive to allow parsing of any potential qualifier. Strict validation of allowed qualifier formats will be implemented in Task 1.2.
- Add private `__qualifier` attribute to store parsed qualifier
- Add public `qualifier` property to access the qualifier
- Update `__parse()` method to extract and validate qualifier format
- Ensure backward compatibility with existing version strings without qualifiers

**Acceptance Criteria:**
- `Version("v1.0.0")` parses successfully with `qualifier = None`
- `Version("v1.0.0-SNAPSHOT")` parses successfully with `qualifier = "SNAPSHOT"`
- `Version("v1.0.0-RC1")` parses successfully with `qualifier = "RC1"`
- `Version("v1.0.0-HF10")` parses successfully with `qualifier = "HF10"`
- `Version("v1.0.0-invalid")` parses but validation handled in Task 1.2
- `__str__()` method includes qualifier when present: `"v1.0.0-SNAPSHOT"`

**Testing:**
- Add tests in `tests/test_version.py` for parsing versions with qualifiers
- Test edge cases: empty qualifier after hyphen, multiple hyphens, etc.

---

#### Task 1.2: Implement Qualifier Validation
**Priority:** High  
**Estimated Effort:** 2-3 hours  
**Spec Reference:** Section 3, 5.1, 5.2

**Description:**
Create a validator to check if a qualifier matches the allowed patterns.

**Requirements:**
- Create `QualifierValidator` class or add validation methods to `Version` class
- Implement regex patterns for each allowed qualifier:
  - `SNAPSHOT`: exactly `SNAPSHOT`
  - `ALPHA`: exactly `ALPHA`
  - `BETA`: exactly `BETA`
  - `RC([1-9][0-9]?)`: `RC` followed by 1-2 digits (RC1 to RC99)
  - `RELEASE`: exactly `RELEASE`
  - `HF([1-9][0-9]?)`: `HF` followed by 1-2 digits (HF1 to HF99)
- Add method to validate qualifier against allowed patterns
- Generate clear error messages for invalid qualifiers

**Acceptance Criteria:**
- `SNAPSHOT`, `ALPHA`, `BETA`, `RELEASE` validate successfully
- `RC1`, `RC2`, `RC99` validate successfully
- `HF1`, `HF2`, `HF99` validate successfully
- `snapshot`, `alpha`, `rc1`, `hf1` (lowercase) are rejected
- `RC`, `RC0`, `RC001`, `HF`, `HF0`, `HF001` are rejected
- `RC1-SNAPSHOT`, `BETA1`, `UNKNOWN` are rejected
- Error messages clearly indicate what's wrong with the qualifier

**Testing:**
- Add comprehensive tests in `tests/test_version.py`
- Test all valid qualifier patterns
- Test all invalid qualifier patterns
- Test case sensitivity
- Test boundary conditions (RC99, HF99, RC100, HF100)

---

### Phase 2: Version Comparison with Qualifiers

#### Task 2.1: Implement Qualifier Precedence Logic
**Priority:** High  
**Estimated Effort:** 3-4 hours  
**Spec Reference:** Section 4.2, 4.3

**Description:**
Implement the precedence rules for comparing versions with the same numeric base but different qualifiers.

**Requirements:**
- Create qualifier precedence mapping or enum:
  1. `SNAPSHOT` (lowest)
  2. `ALPHA`
  3. `BETA`
  4. `RC1` < `RC2` < ... < `RC99`
  5. `RELEASE`
  6. No qualifier (highest for that numeric base)
- Implement special handling for `HF` qualifiers:
  - `v1.0.0` < `v1.0.0-HF1` < `v1.0.0-HF2` < ... < `v1.0.0-HF99`
  - HF qualifiers come **after** the bare version
- Add helper method to extract numeric suffix from RC and HF qualifiers

**Acceptance Criteria:**
- For same numeric version:
  - `v1.0.0-SNAPSHOT` < `v1.0.0-ALPHA` < `v1.0.0-BETA`
  - `v1.0.0-BETA` < `v1.0.0-RC1` < `v1.0.0-RC2`
  - `v1.0.0-RC99` < `v1.0.0-RELEASE` < `v1.0.0`
  - `v1.0.0` < `v1.0.0-HF1` < `v1.0.0-HF2`
  - `v1.0.0-RC1` < `v1.0.0-RC10` (numeric comparison, not string)
  - `v1.0.0-HF1` < `v1.0.0-HF10` (numeric comparison, not string)

**Testing:**
- Add extensive comparison tests in `tests/test_version.py`
- Test all qualifier precedence rules from spec section 4.2
- Test hotfix precedence rules from spec section 4.3
- Test that numeric version still takes precedence (Task 2.2)

---

#### Task 2.2: Update Version Comparison Methods
**Priority:** High  
**Estimated Effort:** 2-3 hours  
**Spec Reference:** Section 4.1, 4.2, 4.3

**Description:**
Update `__eq__`, `__lt__`, `__gt__` methods in `Version` class to incorporate qualifier comparison.

**Requirements:**
- Maintain numeric precedence first (Major, Minor, Patch)
- Only compare qualifiers when numeric components are equal
- Use qualifier precedence logic from Task 2.1
- Ensure comparison methods handle:
  - Both versions with qualifiers
  - One version with qualifier, one without
  - Both versions without qualifiers (existing behavior)

**Acceptance Criteria:**
- Numeric version comparison still works: `v2.0.0-SNAPSHOT` > `v1.9.9-RELEASE`
- Qualifier comparison for same numeric: `v1.0.0-ALPHA` < `v1.0.0-BETA`
- Mixed comparison: `v1.0.0` > `v1.0.0-RELEASE` > `v1.0.0-RC1`
- Hotfix comparison: `v1.0.0` < `v1.0.0-HF1` < `v1.0.0-HF2`
- All existing tests continue to pass
- Invalid versions still return `False` for comparisons

**Testing:**
- Update existing tests in `tests/test_version.py` if needed
- Add new comparison tests covering all combinations from spec
- Test edge cases: comparing invalid versions with valid ones

---

### Phase 3: Version Validation Logic

#### Task 3.1: Update NewVersionValidator for Qualifier Support
**Priority:** High  
**Estimated Effort:** 3-4 hours  
**Spec Reference:** Section 5, 6

**Description:**
Enhance `NewVersionValidator` class in `version_tag_check/version_validator.py` to handle versions with qualifiers.

**Requirements:**
- Update `is_valid_increment()` to consider qualifier precedence
- Allow transitions within same numeric version using qualifier progression
  - Example: `v1.0.0-ALPHA` → `v1.0.0-BETA` → `v1.0.0-RC1` → `v1.0.0`
- Allow patch increment with qualifier reset
  - Example: `v1.0.0` → `v1.0.1-SNAPSHOT` → `v1.0.1`
- Support hotfix progression after release
  - Example: `v1.0.0` → `v1.0.0-HF1` → `v1.0.0-HF2`
- Prevent backwards transitions
  - Reject: `v1.0.0-RC2` → `v1.0.0-RC1`
  - Reject: `v1.0.0` → `v1.0.0-RELEASE`

**Acceptance Criteria:**
- Valid sequences from spec section 6.1 all pass validation
- Invalid sequences from spec section 6.2 all fail validation with clear errors
- Pre-release progression validates correctly
- Cross-version transitions validate correctly
- Hotfix sequences validate correctly
- Error messages clearly indicate why a sequence is invalid

**Testing:**
- Add comprehensive tests in `tests/test_version_validator.py`
- Test valid sequences from spec examples
- Test invalid sequences from spec examples
- Test edge cases and boundary conditions

---

#### Task 3.2: Update VersionTagCheckAction Integration
**Priority:** High  
**Estimated Effort:** 2 hours  
**Spec Reference:** Section 5, 9

**Description:**
Update `VersionTagCheckAction` in `version_tag_check/version_tag_check_action.py` to integrate qualifier validation.

**Requirements:**
- Ensure tag format check includes qualifier validation
- Update error messages to distinguish between:
  - Invalid format (structure issues)
  - Invalid qualifier (disallowed or malformed qualifier)
- Update logging to include qualifier information
- Maintain backward compatibility with existing behavior

**Acceptance Criteria:**
- Action correctly validates version format with qualifiers
- Action rejects tags with invalid qualifiers with clear messages
- Action distinguishes between format errors and qualifier errors
- Logging includes qualifier information when present
- All existing integration tests pass

**Testing:**
- Update tests in `tests/test_version_tag_check_action.py`
- Add tests for qualifier validation integration
- Test error message clarity for different failure modes

---

### Phase 4: Testing and Quality Assurance

#### Task 4.1: Comprehensive Unit Test Suite
**Priority:** High  
**Estimated Effort:** 3-4 hours  
**Spec Reference:** All sections

**Description:**
Create comprehensive unit tests covering all spec requirements.

**Requirements:**
- Test all valid qualifier formats from spec section 3
- Test all invalid qualifier formats from spec section 5.2
- Test all precedence rules from spec section 4
- Test all sequence validation rules from spec section 6
- Maintain overall project coverage at ≥80%
- Ensure tests check exact error messages where specified

**Test Categories:**
1. **Parsing tests** (Section 2, 3)
   - Valid formats with each qualifier type
   - Invalid formats
   - Edge cases (boundary numbers, case sensitivity)

2. **Validation tests** (Section 5)
   - Each allowed qualifier pattern
   - Each disallowed pattern
   - Malformed qualifiers

3. **Comparison tests** (Section 4)
   - Numeric precedence
   - Qualifier precedence for same numeric
   - Hotfix precedence
   - Mixed comparisons

4. **Sequence tests** (Section 6)
   - Valid pre-release progressions
   - Valid cross-version transitions
   - Valid hotfix sequences
   - Invalid backwards transitions
   - Invalid qualifier in sequence

**Acceptance Criteria:**
- All tests pass
- Code coverage ≥80% for new/modified code
- Tests follow existing patterns in `tests/test_version.py`
- Tests are readable and well-documented
- Edge cases and boundary conditions covered

---

#### Task 4.2: Integration Testing
**Priority:** Medium  
**Estimated Effort:** 2-3 hours  
**Spec Reference:** Section 9

**Description:**
Create integration tests to verify end-to-end behavior of the action with qualifiers.

**Requirements:**
- Test complete workflow from tag input to validation output
- Mock GitHub repository responses with qualified tags
- Test realistic version tag sequences
- Verify error messages are user-friendly

**Test Scenarios:**
- Create tag with valid qualifier → should pass
- Create tag with invalid qualifier → should fail with clear message
- Create tag that's valid progression → should pass
- Create tag that's invalid progression → should fail with clear message
- Mix of qualified and non-qualified tags in history

**Acceptance Criteria:**
- Integration tests cover main user workflows
- Tests use realistic version sequences
- Error messages are clear and actionable
- Tests pass consistently

---

#### Task 4.3: Code Quality and Linting
**Priority:** High  
**Estimated Effort:** 1-2 hours  
**Spec Reference:** Development practices

**Description:**
Ensure all new code meets project quality standards.

**Requirements:**
- Run Black formatter on all modified files
- Run Pylint and maintain score ≥9.5
- Run mypy and fix any type errors
- Add type hints to all new public functions and classes
- Add docstrings to all new public functions and classes

**Acceptance Criteria:**
- Black formatting applied: `black $(git ls-files '*.py')`
- Pylint score ≥9.5: `pylint --ignore=tests $(git ls-files '*.py')`
- Mypy passes: `mypy .`
- All public APIs have type hints
- All public APIs have docstrings following project conventions
- No new linting warnings introduced

---

### Phase 5: Documentation and Examples

#### Task 5.1: Update README.md
**Priority:** High  
**Estimated Effort:** 1-2 hours  
**Spec Reference:** Section 9

**Description:**
Update README.md to document the new qualifier support feature.

**Requirements:**
- Update "Supported Version Tags Formats" section
  - Move planned formats to actual supported formats
  - Document all six qualifier types
- Update "Support Version Weight Comparison" section
  - Document qualifier precedence rules
  - Show example comparisons with qualifiers
- Add examples section showing common version progressions
- Update usage examples if needed

**Changes:**
```markdown
### Supported Version Tags Formats
- `v1.0.0` - Standard semantic version
- `v1.0.0-SNAPSHOT` - Snapshot pre-release
- `v1.0.0-ALPHA` - Alpha pre-release
- `v1.0.0-BETA` - Beta pre-release
- `v1.0.0-RC1` to `v1.0.0-RC99` - Release candidates
- `v1.0.0-RELEASE` - Release qualifier
- `v1.0.0-HF1` to `v1.0.0-HF99` - Hotfixes

### Version Weight Comparison With Qualifiers
For the same numeric version (e.g., `v1.0.0`):
- `v1.0.0-SNAPSHOT` < `v1.0.0-ALPHA` < `v1.0.0-BETA`
- `v1.0.0-BETA` < `v1.0.0-RC1` < `v1.0.0-RC2` < ... < `v1.0.0-RC99`
- `v1.0.0-RC99` < `v1.0.0-RELEASE` < `v1.0.0`
- `v1.0.0` < `v1.0.0-HF1` < `v1.0.0-HF2` < ... < `v1.0.0-HF99`

Numeric versions always take precedence:
- `v2.0.0-SNAPSHOT` > `v1.9.9-RELEASE`
```

**Acceptance Criteria:**
- README clearly documents all supported qualifier formats
- README shows qualifier precedence rules
- Examples are clear and helpful
- Links to `docs/qualifier-spec.md` are present (already exists in the Documentation section)
- Documentation is consistent with the specification

---

#### Task 5.2: Add Usage Examples
**Priority:** Medium  
**Estimated Effort:** 1 hour  
**Spec Reference:** Section 6.1

**Description:**
Add examples document or section showing common version tag progressions.

**Requirements:**
- Create examples showing typical version progressions
- Include pre-release cycles
- Include hotfix scenarios
- Include cross-version transitions

**Example Progressions:**
1. **Standard release cycle:**
   - `v1.0.0-SNAPSHOT` → `v1.0.0-ALPHA` → `v1.0.0-BETA` → `v1.0.0-RC1` → `v1.0.0-RC2` → `v1.0.0-RELEASE` → `v1.0.0`

2. **Patch with hotfixes:**
   - `v1.0.0` → `v1.0.1-RC1` → `v1.0.1` → `v1.0.1-HF1` → `v1.0.1-HF2`

3. **Minor version bump:**
   - `v1.0.0` → `v1.1.0-SNAPSHOT` → `v1.1.0-RC1` → `v1.1.0`

**Acceptance Criteria:**
- Examples cover common scenarios from spec section 6.1
- Examples are practical and realistic
- Examples demonstrate both valid and invalid progressions
- Documentation is clear and easy to follow

---

#### Task 5.3: Update DEVELOPER.md
**Priority:** Low  
**Estimated Effort:** 30 minutes  
**Spec Reference:** Development practices

**Description:**
Update DEVELOPER.md if any development practices changed due to qualifier support.

**Requirements:**
- Review if any new testing approaches are needed
- Update if any new development patterns were introduced
- Ensure developer guide reflects current practices

**Acceptance Criteria:**
- DEVELOPER.md is up-to-date
- New contributors can understand how to work with qualifier code
- Testing guidance covers qualifier validation

---

### Phase 6: GitHub Actions Integration

#### Task 6.1: Update action.yml
**Priority:** Medium  
**Estimated Effort:** 30 minutes  
**Spec Reference:** Section 9

**Description:**
Review and update `action.yml` if any changes are needed for qualifier support.

**Requirements:**
- Review action inputs - no changes expected
- Review action description - may need update to mention qualifier support
- Ensure composite action definition is accurate

**Acceptance Criteria:**
- `action.yml` accurately describes action capabilities
- Input/output definitions are correct
- Action description mentions qualifier support if appropriate

---

#### Task 6.2: Update Workflow Files
**Priority:** Low  
**Estimated Effort:** 1 hour  
**Spec Reference:** Section 9

**Description:**
Review and update GitHub workflow files in `.github/workflows/` if needed.

**Requirements:**
- Check if any workflows use version tags
- Update examples in workflows if needed
- Ensure CI/CD workflows test qualifier functionality

**Acceptance Criteria:**
- Workflows accurately demonstrate action usage
- CI/CD tests cover qualifier scenarios
- No breaking changes to existing workflows

---

## Implementation Order

**Recommended sequence:**

1. **Phase 1:** Core Version Model (Tasks 1.1, 1.2)
   - Foundation for all other work
   - Can be tested independently

2. **Phase 2:** Comparison Logic (Tasks 2.1, 2.2)
   - Builds on Phase 1
   - Required for validation logic

3. **Phase 3:** Validation Logic (Tasks 3.1, 3.2)
   - Integrates Phases 1 and 2
   - Core business logic

4. **Phase 4:** Testing (Tasks 4.1, 4.2, 4.3)
   - Continuous throughout development
   - Final comprehensive pass after Phase 3

5. **Phase 5:** Documentation (Tasks 5.1, 5.2, 5.3)
   - After implementation is complete
   - Reflects actual implementation

6. **Phase 6:** Integration (Tasks 6.1, 6.2)
   - Final cleanup and polish
   - After documentation is done

---

## Non-Goals (from Spec Section 7)

These are explicitly **out of scope** and should NOT be implemented:

- ❌ Combined qualifiers (e.g., `v1.0.0-RC1-SNAPSHOT`)
- ❌ Arbitrary/custom qualifiers beyond the six defined types
- ❌ Pre-release or build metadata (e.g., `v1.0.0-RC1+build.123`)
- ❌ Multi-part numeric qualifiers (e.g., `RC1.1`, `HF1.2`)
- ❌ Changes to core semantic versioning behavior for non-qualified versions

---

## Future Configuration Options (from Spec Section 8)

These are potential future enhancements, not part of initial implementation:

- Configurable allowed qualifiers (enable/disable specific ones)
- Case-sensitivity settings
- Strict vs lenient sequence rules
- Hotfix semantics configuration
- Custom precedence override

These could be tracked as separate issues for future releases.

---

## Success Criteria

The implementation is complete when:

- ✅ All tasks in Phases 1-6 are completed
- ✅ All tests pass with ≥80% code coverage
- ✅ Code quality checks pass (Black, Pylint ≥9.5, mypy)
- ✅ Documentation is updated and accurate
- ✅ Specification requirements are fully implemented
- ✅ Action successfully validates tags with qualifiers
- ✅ Error messages are clear and helpful
- ✅ No regressions in existing functionality
- ✅ Code review completed and feedback addressed

---

## Maintenance Notes

- Keep this document updated as tasks are completed
- Link related PRs to specific tasks
- Update task estimates based on actual time taken
- Note any blockers or dependencies discovered during implementation
- Track any deviations from the spec and document reasons
