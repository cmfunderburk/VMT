# VMT EconSim Platform

**Deterministic educational microeconomics simulation** with spatial NxN grid, utility-maximizing
agents, bilateral trade, and PyQt6 visualization. Built for teaching economic theory through
concrete spatial interactions.

## Current Status

**Architecture:** Factory-based, unified decision engine, O(n) spatial indexing

### Working Features

- ✅ Unified decision engine (`make_agent_decision`)
- ✅ Agent dual inventory system (carrying + home)
- ✅ Two-phase execution model (collect → execute)
- ✅ Factory-based utility functions (Cobb-Douglas, Perfect Substitutes, Leontief)
- ✅ Deterministic simulation (seed-based reproducibility)
- ✅ O(n) spatial proximity queries (`AgentSpatialGrid`)
- ✅ PyQt6 launcher with 7 educational scenarios

## Quick Start

```bash
# Setup canonical environment
make venv && source vmt-dev/bin/activate

# Fast visual validation (High Density Local scenario)
make visualtest

# Full test suite
make test-unit

# Performance baselines
make perf

# Interactive scenario browser
make launcher
```

## Architecture Overview

```text
SimulationFeatures → AgentSpatialGrid → Agent perception
    ↓
Utility evaluation (distance-discounted)
    ↓
make_agent_decision → Two-phase execution
    ↓
(1) Collect all decisions
(2) Execute special actions deterministically
```

**Key Files:**

- `src/econsim/simulation/agent/unified_decision.py` - Decision entrypoint
- `src/econsim/simulation/agent/core.py` - Agent class
- `src/econsim/simulation/agent/utility_functions.py` - Factory pattern
- `src/econsim/simulation/executor.py` - V2 two-phase execution
- `src/econsim/simulation/world/spatial.py` - O(n) spatial indexing

**Determinism requirements:**

- Fixed seed propagation
- Deterministic tiebreaks (sort by `agent.id`)
- No random branching or unordered sets

**Economic correctness:**

- Utility maximization with distance discounting
- Dual inventory: `carrying_inventory` + `home_inventory`
- Single-agent ops: `deposit_to_home()`, `withdraw_from_home()`
- Multi-entity ops: `special_action` in execution phase

## Next Steps (Logical Implementation Order)

### 1. Complete Comprehensive Economic Theory Documentation (High Priority)

### 2. **Implement DebugRecorder System** (Medium Priority)

**Goal:** Replace removed delta recorder with decision-focused recording

**Status:** Design complete (see `tmp_plans/CRITICAL/`)\
**Architecture:** SQLite-based with 4 recording levels\
**Use case:** Debug agent decision reasoning (e.g., "Why idle during steps 400-600?")

**Tasks:**

- Implement SQLite schema (snapshots + decisions + trades + events)
- Build recording levels (Summary, Economic, Full Debug, Trace)
- Create query API for freeze/deadlock analysis
- Add CLI tool for .vmtrec file inspection

**Reference:** `tmp_plans/CRITICAL/DEBUG_RECORDING_QUICK_REFERENCE.md`

### 3. **Enhance Educational Scenarios** (Medium Priority)

**Goal:** Expand from 7 to 15+ scenarios covering microeconomic theory

**Current scenarios:** High Density Local, Competition, Density Grid, etc.\
**Needed:** Game theory (Prisoner's Dilemma), market equilibrium, spatial externalities

**Tasks:**

- Design 8 new educational scenarios
- Validate against economic theory predictions
- Add scenario-specific statistical dashboards
- Export capabilities for classroom use

## Development Principles

1. **Economic theory first** - correctness over convenience
2. **Visual clarity** - behaviors must reflect utility functions
3. **Determinism** - reproducible results with same seed
4. **Factory patterns** - extensibility through composition
5. **Ask before removing** - verify safety of legacy code deletion

## Documentation

- **Planning:** `initial_planning.md` (big-picture strategy)
- **Instructions:** `.github/copilot-instructions.md` (AI context)
- **Critical plans:** `tmp_plans/CRITICAL/` (DebugRecorder, refactor status)
- **Performance:** `baselines/` (regression guard metrics)

## License

Apache 2.0 - See LICENSE file
