# Lint Pass Report - October 7, 2025

## Summary

**Total errors found:** 616 **Auto-fixed:** 485 (78.7%) **Remaining:** 131 (21.3%)

## Auto-Fixed Issues (485)

- Import sorting and organization (I001)
- Deprecated typing imports (UP035, UP006, UP045)
- Code formatting (black)
- Various simplifications

## Remaining Issues by Category

### Critical Issues (Require Manual Fix)

#### 1. Undefined Names (26 instances - F821)

Most critical - these are actual bugs or missing imports:

- `Qt` undefined in `src/econsim/main.py` (2 occurrences)
- Multiple Qt imports undefined in GUI files
- `SimulationFeatures` undefined in `phase_manager.py`
- `manual_tests_path`, `sys` undefined in `batch_runner_tab.py`
- `TestConfiguration` undefined in test fixtures (3 files)

#### 2. Star Import Issues (31 instances - F403/F405)

Should be replaced with explicit imports:

- `src/econsim/__init__.py` - 2 star imports
- `src/econsim/gui/__init__.py` - 4 star imports causing 25 F405 warnings

#### 3. Module Import Not at Top (6 instances - E402)

- `src/econsim/simulation/agent/unified_decision.py`
- Several tab files in launcher
- `tests/performance/baseline_capture.py`

### Medium Priority Issues

#### 4. Unused Variables (20 instances - F841)

Variables assigned but never used - code smell, not critical:

- Performance metrics in `framework/base_test.py`
- Test variables in various test files

#### 5. Unused Loop Control Variables (12 instances - B007)

Loop variables like `step_num`, `agent_id` not used in body:

- Should be renamed to `_step_num`, `_agent_id` etc.

#### 6. Unused Imports (19 instances - F401)

Clean up or add to `__all__`:

- Various test imports
- GUI component imports

### Low Priority Issues (Stylistic)

#### 7. Lambda Assignments (4 instances - E731)

Should be rewritten as `def` functions:

- `tests/performance/baseline_capture.py` (3)
- `src/econsim/gui/launcher/tabs/manager.py` (1)

#### 8. Exception Handling (3 instances - B904)

Missing `from` clause in exception handling:

- `src/econsim/gui/launcher/test_runner.py`

#### 9. Simplifications (7 instances)

- SIM108: Use ternary operators (3)
- SIM102: Combine if statements (2)
- SIM118: Use `key in dict` instead of `key in dict.keys()` (2)

#### 10. Other (3 instances)

- E722: Bare except (1)
- F811: Redefined function (1)
- UP007: Use X | Y for union types (1)

## Recommendations

### Immediate Action Required

1. Fix undefined names (F821) - these are actual bugs
2. Fix star imports (F403/F405) - use explicit imports
3. Fix module import locations (E402)

### Should Fix Soon

4. Remove unused variables and imports
5. Rename unused loop control variables

### Optional Improvements

6. Rewrite lambda assignments as functions
7. Add `from` clauses to exception handling
8. Apply simplification suggestions

## Notes

- Markdown linting has been added via `mdformat`
- Configuration: `.mdformat.toml` created
- Makefile updated with `make lint` and `make format` targets
- All auto-fixable issues have been resolved

## Next Steps

Run `make format` to apply automatic fixes, then manually address:

1. Critical F821 undefined name errors
2. Star import replacements (F403/F405)
3. Import location issues (E402)
