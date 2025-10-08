# VMT EconSim AI Coding Agent Instructions

Deterministic educational microeconomics simulation with spatial NxN grid, utility-maximizing agents, bilateral trade, and PyQt6 visualization. Core focus: **economic theory correctness**, **visual clarity**, and **deterministic reproducibility**.

## ⚠️ DEVELOPMENT PAUSE - Economic Model Validation (October 2025)

**ALL CODING IS ON PAUSE** while validating the economic modeling framework.

**Current Focus**: Documenting explicit mathematical models bridging classical microeconomic theory → spatial, discrete-time implementation. Multiple expert reviews have identified gaps between textbook theory and our spatial grid reality.

**Key Documents**:
- `tmp_plans/FINAL/Opus_econ_model_review.md` - Validation guide for current implementation
- `tmp_plans/FINAL/Spatial_Economic_Theory_Framework.md` - Normative theoretical foundation
- `tmp_plans/REVIEWS/` - Expert reviews (Claude Opus, Gemini, GPT-5, Sonnet)

**When to Resume Coding**: After economic framework validation complete and formal models documented. Exception: Critical bug fixes only.

## Project Philosophy

**Educational Mission**: Teach microeconomic theory through spatial visualization. Agent movements must reflect utility-maximizing behavior—students should predict behavior from utility functions alone.

**Economic Correctness First**: All decisions implement sound economic theory (utility maximization, Pareto improvements, deterministic tiebreaks). Visual behavior derives from correct economic logic, not ad-hoc movement rules.

## Architecture: Two-Phase Execution Model

The simulation uses a **two-phase execution pattern** to maintain determinism:

### Phase 1: Decision Collection (Deterministic)
All agents make decisions seeing **identical world state**. No global state changes occur during decision-making.

```python
# src/econsim/simulation/executor.py:UnifiedStepExecutor._execute_unified_decisions
for agent in self.agents:
    action = make_agent_decision(agent, grid, agents, features, rng)
    decisions.append((agent, action))
```

### Phase 2: Action Execution (Coordinated)
Execute all special actions (`collect`, `trade`, `pair`, `unpair`) with proper coordination. Agent modes and targets updated atomically.

**Key Distinction**:
- **Agent methods** (`deposit_to_home()`, `withdraw_from_home()`): Single-entity operations, called during Phase 1
- **Special actions**: Multi-entity operations requiring coordination, executed in Phase 2

## Critical Architecture Components

### Decision System (`src/econsim/simulation/agent/unified_decision.py`)
- **Entry point**: `make_agent_decision()` at line 1130
- **Decision modes**: `decide_forage_only()`, `decide_bilateral_exchange_only()`, `decide_dual_mode()`, `decide_idle()`
- **Distance discounting**: `value = MU * exp(-0.15 * distance)`
- **Economic correctness**: Total bundle utility = `carrying_inventory` + `home_inventory`

### Utility Functions (`src/econsim/simulation/agent/utility_functions.py`)
Factory-based with three implementations (all economically sound):
- **Cobb-Douglas**: `U = (x + 0.01)^α * (y + 0.01)^β` - Diminishing returns, balanced consumption
- **Perfect Substitutes**: `U = αx + βy` - Linear preferences, focus on "cheaper" good
- **Perfect Complements (Leontief)**: `U = min(αx, βy)` - Fixed proportions

**Critical**: `epsilon=0.01` prevents divide-by-zero in marginal utility calculations. Don't change without theoretical validation.

### Spatial Optimization (`src/econsim/simulation/world/spatial.py`)
- **AgentSpatialGrid**: O(n) rebuild, O(agents_in_radius) queries with deterministic ordering
- **Perception radius**: Default 8 Manhattan units, configurable per scenario
- **Determinism**: Dict preserves insertion order; agents sorted by ID for tiebreaks

### Feature Flags (`src/econsim/simulation/features.py`)
Environment-driven behavior configuration (read once at startup):
- `ECONSIM_FORAGE_ENABLED=0`: Disable resource collection (default: enabled)
- `ECONSIM_TRADE_DRAFT=1`: Enable trading intent enumeration
- `ECONSIM_TRADE_EXEC=1`: Enable trading intent execution
- `ECONSIM_DEBUG_TARGET_ARROWS=1`: Enhanced target arrow debugging in GUI

**Pattern**: Feature flags cached in `SimulationCoordinator._cached_feature_flags` to avoid environment lookups per step.

## Development Workflow (When Coding Resumes)

### 1. Setup Environment
```bash
make venv                    # Create vmt-dev/ virtual environment
source vmt-dev/bin/activate  # Python 3.11+ required
make install                 # Editable install with dev dependencies
```

### 2. Visual Validation (Primary Development Tool)
```bash
make visualtest              # Launch High Density Local at 20 FPS
                            # Agent movements MUST reflect utility functions
```

**Critical**: Visual behavior is ground truth. If agents don't behave as economic theory predicts, fix the economic logic, not the visuals.

### 3. Test & Validate Changes
```bash
make test-unit               # 210+ tests must pass
make perf                    # No regression vs baseline (7 scenarios, 1000 steps)
```

### 4. Determinism Verification
Same seed = **identical results** across runs. Verify with:
- `tests/integration/test_determinism_trades.py` (integration test)
- Agent decisions sorted by `agent.id` for deterministic tiebreaks
- No unordered sets or random branching in decision logic

### 5. Performance Baselines
Before major refactors:
```bash
make baseline-capture        # Capture performance + determinism hashes
                            # Saves to baselines/ directory
```

## Common Patterns & Conventions

### Deterministic Agent Selection
```python
# CORRECT: Sort by agent.id for reproducible tiebreaks
nearby_agents.sort(key=lambda a: a.id)

# WRONG: Unordered iteration breaks determinism
for agent in set(agents):  # ❌ Non-deterministic
```

### Distance-Discounted Utility
```python
# Standard pattern across all utility functions
marginal_utility = self.utility_function.marginal_utility(bundle, "good1")
discounted_value = marginal_utility * math.exp(-0.15 * distance)
```

### Agent Inventory Operations
```python
# Single-entity operations (callable in Phase 1)
agent.deposit_to_home("good1", amount=5)
agent.withdraw_from_home("good2", amount=3)

# Multi-entity operations (must be special action in Phase 2)
return AgentAction(action_type="collect", target_x=rx, target_y=ry)
return AgentAction(action_type="trade", partner=other_agent)
```

### Adding New Utility Functions
1. Subclass `UtilityFunction` in `utility_functions.py`
2. Implement `value()` and `marginal_utility()` with economic correctness
3. Add to `create_utility_function()` factory
4. Create validation tests with analytical predictions (see `tmp_plans/FINAL/Opus_econ_model_review.md`)

## Documentation & Planning

- **Big picture**: `initial_planning.md` (educational mission, success metrics, risk radar)
- **Strategic plans**: `tmp_plans/CRITICAL/` (DebugRecorder design, refactor status)
- **Economic reviews**: `tmp_plans/REVIEWS/` (theory validation, expert audits)
- **Project status**: `README.md` (current phase, working features, next steps)

## Key Files Reference

| Component | File | Critical Lines |
|-----------|------|----------------|
| Decision Engine | `src/econsim/simulation/agent/unified_decision.py` | Line 1130: `make_agent_decision()` |
| Two-Phase Executor | `src/econsim/simulation/executor.py` | Line 34: `UnifiedStepExecutor` |
| Utility Functions | `src/econsim/simulation/agent/utility_functions.py` | Lines 95, 148, 191 (CD, PS, PC) |
| Agent Class | `src/econsim/simulation/agent/core.py` | Line 27: `Agent` |
| Spatial Index | `src/econsim/simulation/world/spatial.py` | Line 21: `AgentSpatialGrid` |
| Feature Flags | `src/econsim/simulation/features.py` | Line 31: `SimulationFeatures` |
| Visual Test | `visual_test_simple.py` | Auto-launch High Density Local |
| Coordinator | `src/econsim/simulation/coordinator.py` | Step orchestration |

## When NOT to Change

- **Distance discount constant** (`-0.15`): Tuned for educational scenarios; changing affects all predictions
- **Epsilon in utility functions** (`0.01`): Prevents divide-by-zero in MU calculations
- **Deterministic tiebreaks**: Always sort by `agent.id` before selection
- **Two-phase execution order**: Phase 1 decisions must not see Phase 2 state changes