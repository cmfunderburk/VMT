# Debug Recording System - Architecture Document

**Status:** Final (Updated with Patch V1) | **Date:** October 7, 2025\
**Version:** 1.1 (Dual Recording Support)\
**Implementation Phase:** Debug Recording (Immediate) + Playback Recording (Future)\
**Related Documents:**

- [Patch V1: Full Playback Support](DEBUG_RECORDING_ARCHITECTURE_PATCH_V1.md) (Future
  Implementation)

______________________________________________________________________

## Table of Contents

1. [Overview](#1-overview)
2. [Core Principles](#2-core-principles)
3. [System Architecture](#3-system-architecture)
4. [Component Design](#4-component-design)
5. [Data Schema](#5-data-schema)
6. [Recording Workflow](#6-recording-workflow)
7. [Query & Analysis](#7-query--analysis)
8. [Performance Considerations](#8-performance-considerations)
9. [Extension Points](#9-extension-points)

______________________________________________________________________

## 1. Overview

### Purpose

The Debug Recording System provides a **post-run analysis framework** for VMT EconSim simulations.
It captures the complete decision-making process of agents, enabling developers to understand
**why** agents behaved as they did, not just **what** they did.

### Key Design Goals

1. **Zero Simulation Pollution:** Recording logic never invades simulation code
2. **Economic Focus:** Capture utility calculations, trade evaluations, movement decisions
3. **Query Performance:** SQLite-based storage enables rapid analysis of 100k+ step simulations
4. **Minimal Overhead:** Default recording level targets \<15% performance impact
5. **Educational Value:** Support visual analysis through web-based explorer
6. **Full Playback Support:** Frame-by-frame state capture for visual replay equivalent to live
   simulation

### Dual Recording System (Phased Implementation)

This system is designed to support **two independent recording modes** that can be enabled
separately or together:

1. **Debug Recording (`.vmtrec`)** - SQLite database for querying agent decisions, trades, and
   economic reasoning ✅ **IMMEDIATE PRIORITY**

   - Purpose: Post-run analysis, trade network queries, utility progression plots
   - Overhead: \<15% at default ECONOMIC level
   - Use cases: Debugging decision logic, freeze detection, performance analysis
   - **Status:** To be implemented first

2. **Playback Recording (`.vmtplay`)** - MessagePack binary stream for visual replay 🔜 **FUTURE
   ENHANCEMENT**

   - Purpose: Frame-by-frame visual playback equivalent to `realtime_pygame_v2.py`
   - Overhead: \<25% (independent of debug recording)
   - Use cases: Educational videos, spatial pattern analysis, visual debugging
   - **Status:** Planned for future implementation (see Patch V1)

**Key Innovation:** Both modes use the same observer infrastructure but write to different outputs,
allowing users to choose the recording type that fits their needs.

**Implementation Strategy:** The debug recording system is designed with the dual-output
architecture in mind, ensuring that adding playback recording later will require minimal changes to
the core observer pattern.

### What This Replaces

This system replaces the removed `delta_recorder`, which was designed for visual playback but lacked
economic reasoning capture. The new architecture provides:

- **Debug logs** (immediate) for understanding *why* agents made decisions
- **Playback streams** (future) for visualizing *what* agents did over time
- Both outputs designed to use the pure observer pattern (zero simulation code changes)

**Note:** The initial implementation focuses on debug recording (`.vmtrec`) for post-run analysis.
Playback recording (`.vmtplay`) will be added later using the same observer infrastructure.

______________________________________________________________________

## 2. Core Principles

### Three-Layer Architecture

The system has three distinct layers:

```
┌─────────────────────────────────────────────────────────┐
│ Layer 1: User Commands (What users type)               │
│ • make visualtest, make perf, make test-unit           │
│ • GUI Launcher → Select scenario → Run                 │
│ • pytest tests/                                         │
└─────────────────────────────────────────────────────────┘
                          ↓ invokes
┌─────────────────────────────────────────────────────────┐
│ Layer 2: Infrastructure (Where wrapping happens)       │
│ • visual_test_simple.py                                │
│ • tests/conftest.py (pytest fixtures)                  │
│ • tests/performance/run_benchmark.py                   │
│ • gui/launcher/scenario_runner.py                      │
│                                                         │
│ These files contain:                                   │
│   coordinator = auto_enable_recording(coordinator)     │
│   finalize_recording(coordinator)                      │
└─────────────────────────────────────────────────────────┘
                          ↓ creates & wraps
┌─────────────────────────────────────────────────────────┐
│ Layer 3: Simulation Core (Completely unmodified)       │
│ • SimulationCoordinator                                │
│ • UnifiedStepExecutor                                  │
│ • Agent, make_agent_decision()                         │
│ • All economic logic                                   │
└─────────────────────────────────────────────────────────┘
```

**Key Insight:** The observer wrapping happens in **Layer 2 (Infrastructure)**, not Layer 1 (User
Commands) or Layer 3 (Simulation Core). This means:

- Users never see or write recording code
- Simulation core remains pristine
- Only infrastructure glue code needs 2-line modifications

### Default-On Philosophy

**The debug recording system is enabled by default** in all standard workflows. This design choice
reflects the system's purpose: to make debugging **easier**, not harder.

**Key Points:**

- ✅ **Automatic in infrastructure code:** Two-line addition to existing test/launcher code
- ✅ **Low overhead:** \<15% performance impact at default level justifies always-on behavior
- ✅ **Configurable:** Can be disabled via `ECONSIM_DEBUG_RECORDING=0` if needed
- ✅ **Zero end-user burden:** Users just run `make visualtest` - recording happens automatically
- ✅ **Educational:** Students/developers get recordings automatically for analysis

**Rationale:** If recording is opt-in, developers won't enable it until they encounter a problem—but
by then, they've lost the data needed to diagnose it. Always-on recording ensures we **always have
the data** when we need it.

### Actual User Workflow (What Users Experience)

**Users never write recording code.** They interact with the system through standard commands:

```bash
# User runs make command (recording happens automatically)
$ make visualtest
Starting visual test with seed 11111...
Debug recording enabled: sim_runs/251007_14-23-45-HDL-11111.vmtrec
Running simulation...
[... visual test output ...]
Recording saved: sim_runs/251007_14-23-45-HDL-11111.vmtrec (1.2 MB)

# User can analyze the recording later
$ vmt-explorer sim_runs/251007_14-23-45-HDL-11111.vmtrec
Opening VMT Recording Explorer at http://localhost:5000...

# User can disable recording if needed
$ ECONSIM_DEBUG_RECORDING=0 make visualtest
Starting visual test with seed 11111...
Debug recording disabled.
Running simulation...
```

**Where wrapping happens:**

- `visual_test_simple.py` - Modified with 2 lines: `auto_enable_recording()` and
  `finalize_recording()`
- `tests/conftest.py` - pytest fixture wraps coordinators automatically
- `tests/performance/run_benchmark.py` - Wraps coordinators before benchmarking
- `gui/launcher/scenario_runner.py` - Wraps coordinators when launching scenarios

**What stays unchanged:**

- `SimulationCoordinator` class - zero modifications
- `UnifiedStepExecutor` class - zero modifications
- Agent decision logic - zero modifications
- Test logic itself - only fixture setup changes

### The Pure Observer Pattern

**Definition:** The recorder is an **external module** that observes the simulation through a
one-way dependency.

```
┌─────────────────────────────────────┐
│     Simulation Core                 │
│  (coordinator, executor, agent)     │
│                                     │
│  ✅ Zero recorder imports           │
│  ✅ No recording parameters         │
│  ✅ No recording conditionals       │
│  ✅ Clean economic logic            │
└──────────────┬──────────────────────┘
               │ Observes (read-only)
               ▼
┌─────────────────────────────────────┐
│     Recording Module                │
│  (recorder, observer, query)        │
│                                     │
│  ✅ Imports simulation modules      │
│  ✅ Reads internal state            │
│  ✅ Wraps methods externally        │
│  ❌ Never modifies simulation       │
└─────────────────────────────────────┘
```

### Active Observation Rights

The recorder has **permission to**:

- Import any simulation module (`coordinator`, `executor`, `agent`, etc.)
- Read any attribute, including private members (e.g., `executor._agents`)
- Wrap any method to capture inputs/outputs (via decorator pattern)
- Access runtime state during callbacks

The recorder **must not**:

- Modify simulation source code
- Add parameters to simulation functions
- Change simulation logic or control flow
- Create circular dependencies

### Consultation Requirement

If the recorder needs a simulation code change (e.g., adding a callback hook), the implementer
**must consult** the project maintainer to evaluate if the change is essential or if an external
wrapping technique can be used instead.

### Compatibility Guarantees

The `SimulationObserver` provides **complete transparency** to ensure existing code works without
modification.

**Guaranteed Compatible Patterns:**

```python
# Pattern 1: isinstance checks
if isinstance(coordinator, SimulationCoordinator):
    # ✅ Works - observer inherits from SimulationCoordinator
    process_coordinator(coordinator)

# Pattern 2: Attribute access
utility = coordinator.executor.agents[0].utility
# ✅ Works - delegates to wrapped coordinator via __getattr__

# Pattern 3: Method calls
coordinator.step(rng)
# ✅ Works - wrapped method includes recording hooks

# Pattern 4: Duck typing
def run_simulation(coordinator):
    for _ in range(100):
        coordinator.step(rng)
# ✅ Works - observer quacks like a coordinator

# Pattern 5: Type hints
def analyze(coord: SimulationCoordinator) -> dict:
    return {"agents": len(coord.agents)}
# ✅ Works - observer is a SimulationCoordinator subclass
```

**Required Coordinator API:**

For `auto_enable_recording()` to generate meaningful filenames, the coordinator should expose:

- `coordinator.config.seed` (int) - Simulation seed for reproducibility
- `coordinator.config.scenario_name` (str) - Scenario identifier (e.g., "HDL", "BUT")

If these are not available, the system falls back to timestamp-only filenames.

**Not Guaranteed (But Rare):**

- Direct `type()` checks: `type(observer) == SimulationCoordinator` will be `False` (use
  `isinstance()` instead)
- Accessing observer's `__class__.__name__` for logic: Will be `"SimulationObserver"` not
  `"SimulationCoordinator"`

______________________________________________________________________

## 3. System Architecture

### Module Structure

```
src/econsim/simulation/debug/
├── __init__.py                 # Public API exports (auto_enable_recording, etc.)
├── recorder.py                 # DebugRecorder (SQLite writer for .vmtrec) ✅ IMMEDIATE
├── observer.py                 # SimulationObserver (wraps coordinator) ✅ IMMEDIATE
├── auto_enable.py              # auto_enable_recording() function ✅ IMMEDIATE
├── schema.py                   # Data structures (DecisionRecord, TradeRecord, etc.) ✅ IMMEDIATE
├── query.py                    # SimulationRecording (query interface for .vmtrec) ✅ IMMEDIATE
├── analysis.py                 # Automated analysis (freeze detection, etc.) ✅ IMMEDIATE
├── playback_recorder.py        # PlaybackRecorder (MessagePack writer for .vmtplay) 🔜 FUTURE
├── playback_reader.py          # PlaybackReader (reads .vmtplay files) 🔜 FUTURE
└── playback_schema.py          # Playback data structures (PlaybackFrame, etc.) 🔜 FUTURE
```

**Implementation Priority:** Core debug recording components (marked ✅) will be implemented first.
Playback recording components (marked 🔜) are planned for future implementation and documented here
to ensure the initial design accommodates them.

### Test Runner Integration Points

The recording system must be integrated into existing test infrastructure:

**1. Unit/Integration Tests (`tests/`):**

```python
# In conftest.py or test fixtures
@pytest.fixture
def coordinator_with_recording(coordinator):
    """Automatically wrap coordinators in tests."""
    from econsim.simulation.debug import auto_enable_recording
    return auto_enable_recording(coordinator)
```

**2. Performance Tests (`tests/performance/`):**

```python
# Performance tests may disable recording to measure baseline
@pytest.mark.parametrize("recording_enabled", [False, True])
def test_performance(recording_enabled):
    with override_env("ECONSIM_DEBUG_RECORDING", str(int(recording_enabled))):
        coordinator = auto_enable_recording(coordinator)
        # ... run test
```

**3. Visual Test (`visual_test_simple.py`):**

```python
# Automatically record visual test runs
from econsim.simulation.debug import auto_enable_recording

coordinator = SimulationCoordinator(grid, agents, config)
coordinator = auto_enable_recording(coordinator)  # Single line addition

# Rest of visual test unchanged
```

**4. GUI Launcher (`src/econsim/gui/launcher/`):**

```python
# Launcher automatically records all scenario runs
def run_scenario(scenario_config):
    coordinator = create_coordinator(scenario_config)
    coordinator = auto_enable_recording(coordinator)
    
    # UI communicates recording status to user
    if isinstance(coordinator, SimulationObserver):
        show_recording_indicator(coordinator.recording_filepath)
```

### Component Interaction Diagram (Dual Recording Mode)

```
┌─────────────────────────────────────────────────────────────┐
│  User Entry Points (Recording ENABLED by default)          │
│  • make visualtest (debug recording)                        │
│  • make perf (debug recording)                              │
│  • make test-unit (debug recording)                         │
│  • GUI Launcher (debug recording)                           │
│  [Playback recording to be added in future implementation]  │
└──────────────────────┬──────────────────────────────────────┘
                       │ Invokes
                       ▼
┌──────────────────────────────────────────────────────────────┐
│  Infrastructure Layer (Wrapping Happens Here)               │
│  • visual_test_simple.py                                    │
│  • tests/conftest.py (pytest fixtures)                      │
│  • tests/performance/run_benchmark.py                       │
│  • gui/launcher/scenario_runner.py                          │
└──────────────────────┬──────────────────────────────────────┘
                       │ Creates coordinator, then calls:
                       │ coordinator = auto_enable_recording(coordinator)
                       ▼
┌──────────────────────┐        ┌──────────────────────────────┐
│ SimulationCoordinator│◀───────│  SimulationObserver          │
│  (unmodified)        │ Wraps  │  (designed for extensibility)│
└──────┬───────────────┘        └──────┬───────────────────────┘
       │                               │
       │ coordinator.step()            │ Observes & Records
       ▼                               │
┌──────────────────────┐               ▼
│ UnifiedStepExecutor  │        ┌──────────┐  ┌────────────┐
│  (unmodified)        │        │  Debug   │  │  Playback  │
└──────────────────────┘        │ Recorder │  │  Recorder  │
                                │ ✅ NOW   │  │ 🔜 FUTURE  │
                                └────┬─────┘  └─────┬──────┘
                                     │              │
                                     ▼              ▼
                            ┌─────────────┐  ┌──────────────┐
                            │ .vmtrec     │  │ .vmtplay     │
                            │ (SQLite)    │  │ (MessagePack)│
                            │ Decisions   │  │ Full Frames  │
                            │ Trades      │  │ Per Step     │
                            └─────────────┘  └──────────────┘
                                   ✅              🔜
                            (immediate impl.)  (future impl.)

Environment Variables (Current Implementation):
  ECONSIM_DEBUG_RECORDING=1       # Default: ON (can set to 0 to disable)
  ECONSIM_DEBUG_RECORDING_LEVEL=ECONOMIC  # Default level
  
Environment Variables (Future Addition):
  ECONSIM_PLAYBACK_RECORDING=1    # To be added later
  ECONSIM_PLAYBACK_COMPRESSION=1  # To be added later
```

### Data Flow

**Recording Phase (Automatic):**

01. User runs `make visualtest`, `make perf`, GUI launcher, or pytest

02. Infrastructure layer (e.g., `visual_test_simple.py`, `conftest.py`) creates
    `SimulationCoordinator`

03. Infrastructure calls `coordinator = auto_enable_recording(coordinator)`

04. `auto_enable_recording()` checks environment variables:

    - `ECONSIM_DEBUG_RECORDING` (default: 1 for debug logs)

05. If debug enabled, creates `DebugRecorder` with filename like `251007_14-23-45-HDL-11111.vmtrec`

06. Wraps coordinator with `SimulationObserver` (extensible for future playback recorder)

07. Infrastructure runs simulation loop (unchanged from before)

08. Observer intercepts `coordinator.step()` calls and captures data to debug recorder

09. At simulation end, infrastructure calls `finalize_recording(coordinator)` to close files

10. File locations printed to console:

    ```
    Debug recording enabled: sim_runs/251007_14-23-45-HDL-11111.vmtrec
    ...
    Recording saved: sim_runs/251007_14-23-45-HDL-11111.vmtrec (1.2 MB)
    ```

**Analysis Phase (Debug Logs) - Current Implementation:**

1. User loads `.vmtrec` file with `SimulationRecording.load()`
2. Query interface provides methods: `decisions_at_step()`, `agent_history()`, etc.
3. Web explorer visualizes data with timeline scrubbing and agent inspection

**Playback Phase (Visual Replay) - Future Implementation:**

1. User runs `vmt-playback sim_runs/251007_14-23-45-HDL-11111.vmtplay` (to be implemented)
2. `PlaybackViewer` GUI opens with pygame rendering (to be implemented)
3. Timeline scrubber allows instant jump to any step (to be implemented)
4. Play/pause/step controls with speed adjustment (to be implemented)
5. If `.vmtrec` file exists, clicking agents shows decision details (to be implemented)

**Environment Variables (Current Implementation):**

```bash
# Debug recording (SQLite decision logs) - IMPLEMENTED NOW
ECONSIM_DEBUG_RECORDING=1              # Enable (default: 1)
ECONSIM_DEBUG_RECORDING_LEVEL=ECONOMIC # Detail level (default)
ECONSIM_DEBUG_RECORDING_DIR=./sim_runs # Output directory
```

**Environment Variables (Future Addition):**

```bash
# Playback recording (MessagePack frame stream) - TO BE ADDED LATER
ECONSIM_PLAYBACK_RECORDING=1           # Enable (future default: 0 in tests, 1 in GUI)
ECONSIM_PLAYBACK_RECORDING_DIR=./sim_runs
ECONSIM_PLAYBACK_COMPRESSION=1         # Use zlib compression (future default: 1)
```

______________________________________________________________________

## 4. Component Design

### 4.1 DebugRecorder

**Responsibility:** Write simulation data to SQLite database.

**Key Methods:**

```python
class DebugRecorder:
    def __init__(self, filepath: str, level: RecordingLevel):
        """Initialize recorder with output path and detail level."""
        
    def record_metadata(self, config: dict):
        """Store simulation configuration (seed, grid size, etc.)."""
        
    def record_snapshot(self, step: int, agents: List[Agent], resources: List[Resource]):
        """Store complete world state at a given step."""
        
    def record_decision(self, step: int, decision: DecisionRecord):
        """Store an agent's decision details."""
        
    def record_trade(self, step: int, trade: TradeRecord):
        """Store bilateral trade execution."""
        
    def close(self):
        """Finalize database and close connection."""
```

**Implementation Notes:**

- Uses parameterized queries to prevent SQL injection
- Batches writes for performance (e.g., all decisions per step in one transaction)
- Creates indexes on `(step, agent_id)` for fast queries
- Validates recording level to skip unnecessary data capture

### 4.2 SimulationObserver

**Responsibility:** Wrap `SimulationCoordinator` to capture data without modifying simulation code.

**Design Pattern: Transparent Proxy**

The `SimulationObserver` acts as a **transparent proxy** to the underlying `SimulationCoordinator`.
This ensures complete compatibility with existing code that uses `isinstance()` checks or accesses
coordinator attributes.

**Compatibility Guarantees:**

- ✅ All `SimulationCoordinator` methods are accessible (via `__getattr__` delegation)
- ✅ All `SimulationCoordinator` attributes are accessible (via `__getattr__` delegation)
- ✅ `isinstance(observer, SimulationCoordinator)` returns `True` (via inheritance)
- ✅ Original coordinator accessible via `.coordinator` property
- ✅ Recording-specific methods clearly namespaced (prefixed with `recording_`)

**Key Methods:**

```python
class SimulationObserver(SimulationCoordinator):
    """
    Transparent proxy wrapper for SimulationCoordinator that records simulation data.
    
    Supports dual recording modes (debug + playback) simultaneously.
    Inherits from SimulationCoordinator to satisfy isinstance() checks while
    delegating all coordinator behavior to the wrapped instance.
    """
    
    def __init__(self, 
                 coordinator: SimulationCoordinator, 
                 debug_recorder: Optional[DebugRecorder] = None,
                 playback_recorder: Optional[PlaybackRecorder] = None):  # Future parameter
        """Wrap coordinator with recording capability (designed for dual recorders).
        
        Note: playback_recorder parameter is for future expansion. Current implementation
        only uses debug_recorder.
        """
        # Do NOT call super().__init__() - we delegate to wrapped coordinator
        self._coordinator = coordinator
        self._debug_recorder = debug_recorder
        self._playback_recorder = playback_recorder  # Reserved for future use
        self._step_counter = 0
        self._wrap_step_method()
    
    def __getattr__(self, name: str):
        """Delegate all attribute access to wrapped coordinator."""
        return getattr(self._coordinator, name)
    
    def __setattr__(self, name: str, value):
        """Route coordinator attributes to wrapped instance, observer attrs to self."""
        if name in ('_coordinator', '_debug_recorder', '_playback_recorder', 
                    '_step_counter', '_original_step'):
            # Observer-specific attributes stay on the wrapper
            object.__setattr__(self, name, value)
        else:
            # Everything else goes to wrapped coordinator
            setattr(self._coordinator, name, value)
    
    @property
    def coordinator(self) -> SimulationCoordinator:
        """Access to wrapped coordinator (for type checking/debugging)."""
        return self._coordinator
    
    @property
    def recording_filepath(self) -> Optional[str]:
        """Path to the debug recording file being written."""
        return self._debug_recorder.filepath if self._debug_recorder else None
    
    @property
    def playback_filepath(self) -> Optional[str]:
        """Path to the playback recording file being written."""
        return self._playback_recorder.filepath if self._playback_recorder else None
    
    @property
    def recording_enabled(self) -> bool:
        """Check if any recording is active."""
        return self._debug_recorder is not None or self._playback_recorder is not None
    
    def _wrap_step_method(self):
        """Install wrapper on coordinator.step() to capture data."""
        self._original_step = self._coordinator.step
        
        def wrapped_step(rng):
            self._on_step_start(self._step_counter)
            result = self._original_step(rng)  # Original logic unchanged
            self._on_step_end(self._step_counter)
            self._step_counter += 1
            return result
        
        # Replace step method on wrapped coordinator
        self._coordinator.step = wrapped_step
    
    def _on_step_start(self, step: int):
        """Capture pre-step snapshot (if configured for this recording level)."""
        if self._debug_recorder and step % self._debug_recorder.snapshot_frequency == 0:
            agents = self._coordinator.executor.agents
            resources = self._coordinator.grid.resources
            self._debug_recorder.record_snapshot(step, agents, resources)
    
    def _on_step_end(self, step: int):
        """Capture data for recorders if enabled."""
        
        # Debug recording (sparse, decision-focused) - CURRENT IMPLEMENTATION
        if self._debug_recorder:
            for agent in self._coordinator.executor.agents:
                decision = self._extract_decision_record(agent, step)
                self._debug_recorder.record_decision(step, decision)
            
            # Capture trades executed this step
            trades = self._coordinator.executor.get_trades_this_step()
            for trade in trades:
                self._debug_recorder.record_trade(step, trade)
        
        # Playback recording (complete state, every step) - FUTURE IMPLEMENTATION
        if self._playback_recorder:
            snapshot = self._capture_full_world_state(step)
            self._playback_recorder.record_frame(step, snapshot)
    
    def _extract_decision_record(self, agent: Agent, step: int) -> DecisionRecord:
        """Build DecisionRecord from agent state."""
        # Implementation captures agent's current state, last decision, etc.
        pass
    
    def _capture_full_world_state(self, step: int) -> PlaybackFrame:
        """Capture complete world state for visual playback (FUTURE IMPLEMENTATION)."""
        agents = [
            PlaybackAgentState(
                id=agent.id,
                x=agent.x,
                y=agent.y,
                carrying_inventory=agent.carrying_inventory.copy(),
                home_inventory=agent.home_inventory.copy(),
                home_x=agent.home_x,
                home_y=agent.home_y,
                partner_id=agent.partner_id if hasattr(agent, 'partner_id') else None,
                utility=agent.utility,
                utility_function_type=agent.utility_function.__class__.__name__
            )
            for agent in self._coordinator.executor.agents
        ]
        
        resources = [
            PlaybackResourceState(
                x=res.x,
                y=res.y,
                resource_type=res.resource_type,
                remaining_quantity=res.remaining_quantity
            )
            for res in self._coordinator.grid.resources
        ]
        
        return PlaybackFrame(step=step, agents=agents, resources=resources)
    
    def recording_close(self):
        """Explicitly close both recordings (also called by finalize_recording)."""
        if self._debug_recorder:
            self._debug_recorder.close()
            self._debug_recorder = None
        if self._playback_recorder:
            self._playback_recorder.close()
            self._playback_recorder = None
```

**Why This Works:**

1. **Inherits from SimulationCoordinator:** `isinstance(observer, SimulationCoordinator)` returns
   `True`
2. **`__getattr__` delegation:** Any method/attribute not on observer forwards to wrapped
   coordinator
3. **`__setattr__` routing:** Coordinator attributes go to wrapped instance, observer-specific stay
   on wrapper
4. **No `super().__init__` call:** Avoids initializing a second coordinator instance
5. **Recording methods namespaced:** All recording-specific methods prefixed with `recording_`

**Implementation Considerations:**

1. **Inheritance vs Composition:** Observer inherits from `SimulationCoordinator` for `isinstance()`
   compatibility but doesn't call `super().__init__()`. This avoids creating a second coordinator
   instance while maintaining type compatibility.

2. **Attribute Routing:** The `__setattr__` override ensures coordinator-related attributes go to
   the wrapped instance while observer-specific attributes (`_recorder`, `_step_counter`) stay on
   the wrapper.

3. **Method Wrapping Scope:** Only `coordinator.step()` is wrapped. All other methods naturally
   delegate through `__getattr__`, maintaining their original behavior.

4. **Performance:** The `__getattr__` delegation adds minimal overhead (~1 nanosecond per attribute
   access) compared to recording operations (microseconds to milliseconds).

5. **Type Checking:** For maximum compatibility, use `hasattr(coordinator, 'recording_enabled')` to
   check for recording capability rather than `isinstance(coordinator, SimulationObserver)`.

### Method Wrapping Strategy (Hot Path Avoidance)

**Wrapped Methods:**

- ✅ `coordinator.step(rng)` - Single wrap point, not a hot path (1,000 calls in 1,000-step
  simulation)

**NOT Wrapped (Hot Paths - Thousands to Millions of Calls):**

- ❌ `make_agent_decision()` - Called 100,000+ times per simulation (hot path)
- ❌ `evaluate_trade()` - Called 2,000,000+ times per simulation (very hot path)
- ❌ `executor.execute_step()` - Internal implementation detail
- ❌ `agent.calculate_utility()` - Called millions of times during option evaluation

**Data Capture Strategy:**

- **Before step**: Optionally capture world snapshot (every N steps for time-travel capability)
- **After step**: Read decision results from agent state or executor's completed actions
- **Never during step**: No wrapping of decision logic, utility calculations, or trade evaluation

**Example: Post-Execution Read Pattern**

```python
def _on_step_end(self, step: int):
    """Capture decisions AFTER execution completes (not during)."""
    # All decisions have been made and executed by this point
    # We only READ the results from agent state
    
    for agent in self._coordinator.executor.agents:
        # Read agent's last decision from its state (no logic, pure reading)
        decision_record = DecisionRecord(
            agent_id=agent.id,
            decision_type=agent.last_action,  # Already computed and stored
            position=agent.position,
            utility_before=agent.utility_history[-2] if len(agent.utility_history) > 1 else 0,
            utility_after=agent.utility_history[-1],
            # ... all fields are READ-ONLY from existing state
        )
        self._recorder.record_decision(step, decision_record)
```

**Why This Matters:**

```python
# ❌ DANGEROUS (Hot Path Wrap): 100,000 function calls per simulation
for agent in agents:  # 100 agents per step
    decision = wrapped_make_agent_decision(agent, ...)  # Wrap adds overhead to hot path

# ✅ SAFE (Single Wrap): 1,000 function calls per simulation  
coordinator.step(rng)  # Single wrap, reads results afterward
```

### Determinism Guarantees

The recording system **must not affect simulation behavior**. These guarantees are enforced:

1. **No RNG Consumption**: Recording code never calls `rng.random()` or any RNG methods that consume
   state
2. **No State Mutation**: Recording code only reads simulation state, never writes to it
3. **No Control Flow Changes**: Recording code never alters which agents act or what decisions they
   make
4. **Exception Isolation**: Recording exceptions are caught and logged but never suppress simulation
   exceptions
5. **Read-Only Access**: Recording accesses simulation state using read-only getters (no setters)

**Verification:**

```python
# Same seed must produce identical results with recording ON or OFF
def test_determinism_with_recording():
    # Run 1: Recording enabled
    seed = 12345
    coordinator1 = SimulationCoordinator(grid, agents, config, seed=seed)
    coordinator1 = auto_enable_recording(coordinator1)
    for _ in range(1000):
        coordinator1.step(rng1)
    
    # Run 2: Recording disabled
    coordinator2 = SimulationCoordinator(grid, agents, config, seed=seed)
    for _ in range(1000):
        coordinator2.step(rng2)
    
    # Must be identical
    assert agents1_final_state == agents2_final_state
    assert trades1 == trades2
```

### 4.3 Automatic Enabling (auto_enable_recording)

**Responsibility:** Transparently wrap coordinators in test/launcher processes.

**Key Function:**

```python
def auto_enable_recording(
    coordinator: SimulationCoordinator,
    enable_debug: Optional[bool] = None,
    enable_playback: Optional[bool] = None  # Reserved for future use
) -> SimulationCoordinator:
    """
    Automatically wrap coordinator with observer if recording is enabled.
    
    Args:
        coordinator: Unwrapped coordinator
        enable_debug: Override for ECONSIM_DEBUG_RECORDING env var
        enable_playback: Override for ECONSIM_PLAYBACK_RECORDING env var (future parameter)
    
    Returns:
        Original coordinator (if debug disabled) or SimulationObserver (if debug enabled).
        The returned observer is a transparent proxy that satisfies isinstance() checks.
    
    Current Implementation:
        Only debug recording is implemented. Playback recording is reserved for future expansion.
    
    Configuration:
        Debug Recording (Current):
            - ECONSIM_DEBUG_RECORDING=1 (default: 1)
            - ECONSIM_DEBUG_RECORDING_LEVEL=ECONOMIC (default)
            - ECONSIM_DEBUG_RECORDING_DIR=./sim_runs (default)
        
        Playback Recording (NEW in V1.1):
            - ECONSIM_PLAYBACK_RECORDING=1 (default: 0 in tests, 1 in GUI)
            - ECONSIM_PLAYBACK_RECORDING_DIR=./sim_runs (default)
            - ECONSIM_PLAYBACK_COMPRESSION=1 (default: 1)
    
    Compatibility:
        The returned SimulationObserver inherits from SimulationCoordinator and
        delegates all coordinator methods/attributes, ensuring transparent behavior.
    """
    from econsim.simulation.features import SimulationFeatures
    
    features = SimulationFeatures.from_environment()
    
    # Read environment or use overrides
    debug_enabled = enable_debug if enable_debug is not None else features.debug_recording_enabled
    # Note: playback_enabled reserved for future implementation
    playback_enabled = False  # Hardcoded to False for current implementation
    
    # If debug not enabled, return unwrapped
    if not debug_enabled:
        return coordinator
    
    # Avoid double-wrapping
    if isinstance(coordinator, SimulationObserver):
        return coordinator  # Already wrapped
    
    # Create debug recorder (current implementation)
    debug_recorder = None
    
    if debug_enabled:
        debug_path = generate_recording_filename(coordinator, suffix=".vmtrec")
        filepath = Path(features.debug_recording_dir) / debug_path
        filepath.parent.mkdir(parents=True, exist_ok=True)
        debug_recorder = DebugRecorder(str(filepath), level=features.debug_recording_level)
        print(f"Debug recording enabled: {filepath}")
    
    # Note: Playback recorder creation will be added in future implementation
    # The observer interface supports it, but it's not yet implemented
    
    # Wrap coordinator with debug recorder (playback_recorder=None for now)
    observer = SimulationObserver(coordinator, debug_recorder, playback_recorder=None)
    
    return observer  # Return wrapped coordinator (satisfies isinstance checks)

def finalize_recording(coordinator: SimulationCoordinator):
    """
    Close debug recorder if coordinator is wrapped with observer.
    
    Safe to call on both wrapped and unwrapped coordinators.
    Prints file sizes and locations when closing.
    
    Note: In future implementation, this will also close playback recorder.
    """
    if isinstance(coordinator, SimulationObserver):
        # Close debug recorder (playback recorder support to be added later)
        coordinator.recording_close()
        
        # Report debug recording file size
        if coordinator.recording_filepath and Path(coordinator.recording_filepath).exists():
            debug_path = coordinator.recording_filepath
            size_mb = Path(debug_path).stat().st_size / (1024 * 1024)
            print(f"Recording saved: {debug_path} ({size_mb:.1f} MB)")
        
        # Report playback recording file size
        if coordinator.playback_filepath and Path(coordinator.playback_filepath).exists():
            playback_path = coordinator.playback_filepath
            size_mb = Path(playback_path).stat().st_size / (1024 * 1024)
            print(f"Recording saved: {playback_path} ({size_mb:.1f} MB)")
```

**Transparent Proxy Demonstration:**

```python
# Observer is fully compatible with existing code
coordinator = SimulationCoordinator(grid, agents, config)
observer = auto_enable_recording(coordinator)

# ✅ isinstance checks work
assert isinstance(observer, SimulationCoordinator)  # True!

# ✅ All coordinator attributes accessible
print(observer.executor)  # Delegates to wrapped coordinator
print(observer.agents)    # Delegates to wrapped coordinator

# ✅ Methods work unchanged
observer.step(rng)  # Calls wrapped step with recording

# ✅ Recording-specific methods namespaced
print(observer.recording_filepath)  # Recording-specific property
observer.recording_close()          # Recording-specific method

# ✅ Can access wrapped coordinator if needed (rare)
original_coordinator = observer.coordinator
```

**Method Wrapping Technique:**

```python
def _wrap_step_method(self):
    """Install wrapper on coordinator.step() without modifying coordinator class."""
    self._original_step = self._coordinator.step
    
    def wrapped_step(rng):
        self._on_step_start(self._step_counter)
        result = self._original_step(rng)  # Original logic unchanged
        self._on_step_end(self._step_counter)
        self._step_counter += 1
        return result
    
    # Replace step method on wrapped coordinator instance (not class)
    self._coordinator.step = wrapped_step
```

**Access to Internal State (Active Observation):**

```python
# Observer can read any coordinator/executor state
agents = self._coordinator.executor.agents
resources = self._coordinator.grid.resources
config = self._coordinator.config

# Observer can inspect decision details after execution
for agent in self._coordinator.executor.agents:
    decision = extract_last_decision(agent)
    self._recorder.record_decision(step, decision)
```

### 4.4 Data Structures

**DecisionRecord:** Captures agent's decision-making process.

```python
@dataclass
class DecisionRecord:
    step: int
    agent_id: int
    
    # Current state
    position: Tuple[int, int]
    carrying_inventory: Dict[str, int]
    home_inventory: Dict[str, int]
    current_utility: float
    
    # Decision details
    decision_type: str  # "move", "collect", "trade", "pair", "unpair", "idle"
    target_position: Optional[Tuple[int, int]]
    target_resource: Optional[str]
    trade_partner_id: Optional[int]
    trade_goods: Optional[Tuple[str, str]]  # (give, receive)
    
    # Economic reasoning
    expected_utility: float
    utility_gain: float
    alternatives_considered: int  # For recording level >= 3
```

**TradeRecord:** Captures bilateral trade execution.

```python
@dataclass
class TradeRecord:
    step: int
    agent1_id: int
    agent2_id: int
    good_from_agent1: str
    good_from_agent2: str
    agent1_utility_before: float
    agent1_utility_after: float
    agent2_utility_before: float
    agent2_utility_after: float
```

**WorldSnapshot:** Periodic full state capture.

```python
@dataclass
class WorldSnapshot:
    step: int
    agents: List[AgentState]  # Full agent state
    resources: List[ResourceState]  # Resource positions and quantities
    timestamp: datetime
```

**Playback Data Structures (FUTURE IMPLEMENTATION - V1.1 Planned):**

```python
@dataclass
class PlaybackFrame:
    """Complete world state for a single step (visual playback).
    
    Note: This is a planned structure for future playback recording implementation.
    """
    step: int
    agents: List[PlaybackAgentState]
    resources: List[PlaybackResourceState]

@dataclass
class PlaybackAgentState:
    """Agent state for visual rendering.
    
    Note: This is a planned structure for future playback recording implementation.
    """
    id: int
    x: int
    y: int
    carrying_inventory: Dict[str, int]
    home_inventory: Dict[str, int]
    home_x: int
    home_y: int
    partner_id: Optional[int]
    utility: float  # For overlay display
    utility_function_type: str  # For sprite selection (if needed)

@dataclass
class PlaybackResourceState:
    """Resource state for visual rendering.
    
    Note: This is a planned structure for future playback recording implementation.
    """
    x: int
    y: int
    resource_type: str
    remaining_quantity: int
```

### 4.5 SimulationRecording (Query Interface)

**Responsibility:** Provide efficient access to recorded data.

**Key Methods:**

```python
class SimulationRecording:
    @staticmethod
    def load(filepath: str) -> 'SimulationRecording':
        """Load a .vmtrec file for analysis."""
        
    def get_metadata(self) -> dict:
        """Get simulation configuration."""
        
    def decisions_at_step(self, step: int) -> List[DecisionRecord]:
        """Get all agent decisions for a specific step."""
        
    def agent_history(self, agent_id: int) -> List[DecisionRecord]:
        """Get complete decision history for one agent."""
        
    def trades_at_step(self, step: int) -> List[TradeRecord]:
        """Get all trades executed at a specific step."""
        
    def snapshot_at_step(self, step: int) -> Optional[WorldSnapshot]:
        """Get nearest snapshot to requested step."""
        
    def agent_utility_series(self, agent_id: int) -> List[Tuple[int, float]]:
        """Get [(step, utility)] time series for plotting."""
```

### 4.6 PlaybackRecorder & PlaybackReader (FUTURE IMPLEMENTATION - V1.1 Planned)

**Note:** These components are planned for future implementation. They are documented here to ensure
the current debug recording architecture accommodates them.

**PlaybackRecorder Responsibility:** Write complete world state frames to MessagePack binary file
(to be implemented).

**Planned Key Methods:**

```python
class PlaybackRecorder:
    """Records complete world state for visual playback.
    
    FUTURE IMPLEMENTATION: This class will be implemented after debug recording.
    """
    
    def __init__(self, filepath: str, compression: bool = True):
        """Initialize playback recorder with MessagePack output."""
        self.filepath = filepath
        self.compression = compression  # zlib compression
        self.file = open(filepath, 'wb')
        self.frame_offsets = []  # For frame index
        
    def record_metadata(self, config: dict):
        """Store simulation configuration in header."""
        
    def record_frame(self, step: int, frame: PlaybackFrame):
        """Write a single frame to file."""
        # Serialize with MessagePack
        # Optionally compress with zlib
        # Track byte offset for frame index
        
    def close(self):
        """Finalize recording with frame index."""
        # Write frame index at end of file
        # Update header with index location
```

**PlaybackReader Responsibility:** Read playback files for visual replay (to be implemented).

**Planned Key Methods:**

```python
class PlaybackReader:
    """Read playback files for visual replay.
    
    FUTURE IMPLEMENTATION: This class will be implemented after debug recording.
    """
    
    def __init__(self, filepath: str):
        """Load playback file and frame index."""
        self.filepath = filepath
        self.file = open(filepath, 'rb')
        self._load_header()
        self._load_frame_index()
    
    def get_frame(self, step: int) -> PlaybackFrame:
        """Read a specific frame by step number (instant seeking)."""
        # Seek to frame offset using frame index
        # Read and decompress if needed
        # Deserialize with MessagePack
        
    def __len__(self):
        """Total number of frames."""
        return len(self.frame_index)
    
    def close(self):
        """Close file handle."""
```

**Planned File Format (.vmtplay):**

- **Header:** Metadata (seed, grid size, total steps, frame index offset)
- **Frames:** Variable-length MessagePack-serialized PlaybackFrame objects
- **Frame Index:** Array of byte offsets for instant seeking
- **Compression:** Optional zlib compression on frame data

**Expected Performance:** Fast sequential read for playback, instant seeking via frame index, ~60%
size reduction with compression.

**Implementation Timeline:** This will be implemented in a future phase after the debug recording
system is complete and tested.

### 4.7 Automated Analysis

**Responsibility:** Detect common patterns and anomalies.

**Example: Freeze Detection**

```python
def analyze_freeze(recording: SimulationRecording, 
                   start_step: int, 
                   end_step: int) -> FreezeAnalysis:
    """
    Analyze a suspected freeze period to identify causes.
    
    Checks:
    1. Agent movement patterns (are agents stuck?)
    2. Trade activity (has trading stopped?)
    3. Decision diversity (are agents repeating same decisions?)
    4. Utility progression (is anyone improving?)
    
    Returns a report with:
    - Affected agents
    - Common decision patterns
    - Potential deadlock causes
    """
```

______________________________________________________________________

## 5. Data Schema

### SQLite Database Schema

**metadata table:**

```sql
CREATE TABLE metadata (
    key TEXT PRIMARY KEY,
    value TEXT
);
-- Stores: seed, grid_width, grid_height, num_agents, recording_level, etc.
```

**snapshots table:**

```sql
CREATE TABLE snapshots (
    step INTEGER PRIMARY KEY,
    data BLOB,  -- MessagePack-serialized WorldSnapshot
    timestamp TEXT
);
-- Snapshot frequency depends on recording level
```

**decisions table:**

```sql
CREATE TABLE decisions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    step INTEGER NOT NULL,
    agent_id INTEGER NOT NULL,
    position_x INTEGER,
    position_y INTEGER,
    carrying_inventory TEXT,  -- JSON dict
    home_inventory TEXT,      -- JSON dict
    current_utility REAL,
    decision_type TEXT,
    target_x INTEGER,
    target_y INTEGER,
    target_resource TEXT,
    trade_partner_id INTEGER,
    trade_give TEXT,
    trade_receive TEXT,
    expected_utility REAL,
    utility_gain REAL,
    alternatives_considered INTEGER
);
CREATE INDEX idx_decisions_step_agent ON decisions(step, agent_id);
CREATE INDEX idx_decisions_agent ON decisions(agent_id);
```

**trades table:**

```sql
CREATE TABLE trades (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    step INTEGER NOT NULL,
    agent1_id INTEGER NOT NULL,
    agent2_id INTEGER NOT NULL,
    good_from_agent1 TEXT,
    good_from_agent2 TEXT,
    agent1_utility_before REAL,
    agent1_utility_after REAL,
    agent2_utility_before REAL,
    agent2_utility_after REAL
);
CREATE INDEX idx_trades_step ON trades(step);
```

### File Formats

**Debug Recording (`.vmtrec`):**

- **Extension:** `.vmtrec` (VMT Recording)
- **Format:** SQLite 3 database
- **Portability:** Platform-independent, can be analyzed on any system with SQLite
- **Size:** Approx. 1-5 MB per 1000 steps at ECONOMIC level (depends on agent count)
- **Use case:** Querying agent decisions, trade history, utility progression

**Playback Recording (`.vmtplay`) - FUTURE IMPLEMENTATION (V1.1 Planned):**

- **Extension:** `.vmtplay` (VMT Playback)
- **Format:** MessagePack binary stream with frame index (planned)
- **Structure:**
  - Header (metadata: seed, grid size, total steps, frame index offset)
  - Frames (variable-length MessagePack-serialized PlaybackFrame objects)
  - Frame Index (byte offsets for instant seeking)
- **Compression:** Optional zlib compression (planned default: enabled, ~60% size reduction)
- **Size:** Estimated approx. 7-20 MB per 1000 steps (compressed) for 100 agents
- **Use case:** Frame-by-frame visual playback with instant seeking
- **Status:** To be implemented after debug recording is complete

______________________________________________________________________

## 6. Recording Workflow

### Integration Points

The recording system is integrated into **infrastructure code** that users invoke via `make`
commands or the GUI launcher. Users never directly call recording functions.

**1. Visual Test (`visual_test_simple.py`)**

```python
from econsim.simulation.coordinator import SimulationCoordinator
from econsim.simulation.debug import auto_enable_recording, finalize_recording

# Standard simulation setup
coordinator = SimulationCoordinator(grid, agents, config)

# ADD THIS LINE: Enable recording (respects env vars, default ON)
coordinator = auto_enable_recording(coordinator)

# Run simulation (unchanged)
for step in range(1000):
    coordinator.step(rng)
    pygame_render_step(coordinator)  # Visual rendering

# ADD THIS LINE: Finalize recording
finalize_recording(coordinator)
```

**2. Pytest Integration (`tests/conftest.py`)**

```python
from econsim.simulation.debug import auto_enable_recording, finalize_recording

@pytest.fixture
def coordinator(grid, agents, config):
    """Fixture that automatically enables recording for all tests."""
    coord = SimulationCoordinator(grid, agents, config)
    coord = auto_enable_recording(coord)  # Recording ON by default
    yield coord
    finalize_recording(coord)  # Cleanup after test
```

**3. Performance Benchmarks (`tests/performance/run_benchmark.py`)**

```python
from econsim.simulation.debug import auto_enable_recording, finalize_recording

def run_benchmark(scenario_config):
    coordinator = create_coordinator(scenario_config)
    
    # Recording is ENABLED by default (overhead is measured)
    # To measure baseline without recording: ECONSIM_DEBUG_RECORDING=0 make perf
    coordinator = auto_enable_recording(coordinator)
    
    start_time = time.time()
    for step in range(1000):
        coordinator.step(rng)
    elapsed = time.time() - start_time
    
    finalize_recording(coordinator)
    return elapsed
```

**4. GUI Launcher (`gui/launcher/scenario_runner.py`)**

```python
from econsim.simulation.debug import auto_enable_recording, finalize_recording, SimulationObserver

def run_scenario(scenario_config, ui_callback):
    coordinator = create_coordinator(scenario_config)
    coordinator = auto_enable_recording(coordinator)
    
    # Show recording status in UI (check for recording capability)
    if hasattr(coordinator, 'recording_enabled') and coordinator.recording_enabled:
        ui_callback.show_recording_indicator(coordinator.recording_filepath)
    
    for step in range(scenario_config.num_steps):
        coordinator.step(rng)  # Works whether wrapped or not
        ui_callback.update_visualization(step)
    
    finalize_recording(coordinator)  # Safe to call on wrapped or unwrapped
    
    # Show where recording was saved
    if hasattr(coordinator, 'recording_filepath'):
        ui_callback.show_message(f"Recording saved: {coordinator.recording_filepath}")
```

**5. Configuration Control (Environment Variables)**

```bash
# Default behavior: Recording ENABLED
make visualtest        # Records to sim_runs/251007_14-23-45-HDL-11111.vmtrec
make perf              # Records all 7 scenarios with overhead measurement
make test-unit         # Records test runs for debugging

# Disable recording (e.g., for fastest possible runs)
ECONSIM_DEBUG_RECORDING=0 make visualtest

# Change recording level
ECONSIM_DEBUG_RECORDING_LEVEL=FULL_DEBUG make visualtest

# Change output directory
ECONSIM_DEBUG_RECORDING_DIR=./my_recordings make visualtest
```

**2. Observer Hooks (Automatic) - Hot Path Avoidance**

The observer captures data using a **post-execution read pattern** to avoid hot path overhead:

**Single Wrap Point:**

- **`coordinator.step()`** → Wrap adds recording hooks before/after (1,000 calls per simulation)

**Read After Execution (No Wrapping):**

- **`executor.agents`** → Read agent state after `step()` completes (read-only access)
- **`executor.get_trades_this_step()`** → Read completed trades (if method exists)
- **Agent attributes** → Read `agent.last_action`, `agent.utility`, `agent.position` after decisions
  made

**Why This Strategy:**

```python
# The entire step executes normally (unwrapped hot paths)
coordinator.step(rng)  # ← Only this is wrapped (1x per step)
    ├─ executor.execute_step()  # ← NOT wrapped (internal)
    │   ├─ make_agent_decision() × 100  # ← NOT wrapped (hot path)
    │   ├─ evaluate_trade() × 2000      # ← NOT wrapped (very hot path)
    │   └─ agent.calculate_utility() × 10000  # ← NOT wrapped (hottest path)
    └─ [Step completes]

# NOW we read the results (post-execution)
for agent in executor.agents:  # Read state, don't intercept decisions
    record_decision(agent.last_action, agent.utility, ...)
```

**Data Sources (All Read-Only):**

- Agent state: `agent.position`, `agent.carrying_inventory`, `agent.utility`
- Executor state: `executor.trades_this_step` (if tracked)
- Grid state: `grid.resources` (for snapshots)
- No method wrapping of decision logic or utility calculations

**3. Recording Level Logic (Hot Path Impact)**

```python
# Level 1 - SUMMARY: Only aggregate metrics (NO hot path wrapping)
if level >= RecordingLevel.SUMMARY:
    # Read aggregates after step completes
    recorder.record_summary_stats(step, agent_count, trade_count, avg_utility)

# Level 2 - ECONOMIC: Individual decisions + trades (DEFAULT, NO hot path wrapping)
if level >= RecordingLevel.ECONOMIC:
    # Read individual agent state after step completes
    for agent in executor.agents:
        decision_record = extract_from_agent_state(agent)
        recorder.record_decision(step, decision_record)
    recorder.record_trade(step, trade_record)

# Level 3 - FULL_DEBUG: All evaluated options (NO hot path wrapping)
if level >= RecordingLevel.FULL_DEBUG:
    # Read from executor's option cache (if available) after step completes
    # Or reconstruct from agent state
    recorder.record_evaluated_options(step, agent_id, all_options)

# Level 4 - TRACE: Function call traces (⚠️ WRAPS HOT PATHS - USE SPARINGLY)
if level >= RecordingLevel.TRACE:
    # ⚠️ WARNING: This level DOES wrap make_agent_decision() and other hot paths
    # Expect ~100% overhead due to function call interception
    # Only use for deep debugging of specific issues
    recorder.record_function_call(step, function_name, args, result)
```

**Hot Path Wrapping by Level:**

| Level      | Wraps `coordinator.step()` | Wraps `make_agent_decision()` | Wraps `evaluate_trade()` |
| ---------- | -------------------------- | ----------------------------- | ------------------------ |
| SUMMARY    | ✅ Yes                     | ❌ No                         | ❌ No                    |
| ECONOMIC   | ✅ Yes                     | ❌ No                         | ❌ No                    |
| FULL_DEBUG | ✅ Yes                     | ❌ No                         | ❌ No                    |
| TRACE      | ✅ Yes                     | ⚠️ Yes (slow!)                | ⚠️ Yes (very slow!)      |

### Capturing Decision Data Without Hot Path Wrapping

**Challenge:** We want to record *what* each agent decided and *why*, but we can't wrap
`make_agent_decision()` without massive overhead.

**Solution:** Agents should store their last decision in their state, which we read afterward.

**Required Agent State (Implementation Consideration):**

```python
class Agent:
    # Existing state
    position: Tuple[int, int]
    carrying_inventory: Dict[str, int]
    utility_history: List[float]
    
    # NEW: Store last decision for recording
    last_decision: Optional[AgentDecision] = None
    
    def set_last_decision(self, decision: AgentDecision):
        """Store decision for later recording (called by executor)."""
        self.last_decision = decision
```

**Executor Integration (Implementation Consideration):**

```python
class UnifiedStepExecutor:
    def execute_step(self, rng):
        decisions = []
        
        # Phase 1: Collect decisions
        for agent in self.agents:
            decision = make_agent_decision(agent, ...)  # Hot path, NOT wrapped
            
            # Store decision on agent for recording to read later
            agent.set_last_decision(decision)
            
            decisions.append((agent, decision))
        
        # Phase 2: Execute actions
        for agent, decision in decisions:
            self._execute_action(agent, decision)
```

**Observer Reads After Execution:**

```python
def _on_step_end(self, step: int):
    """Read decisions from agent state (post-execution)."""
    for agent in self._coordinator.executor.agents:
        if agent.last_decision:
            record = DecisionRecord(
                step=step,
                agent_id=agent.id,
                decision_type=agent.last_decision.action_type,
                target_position=agent.last_decision.target_position,
                expected_utility=agent.last_decision.expected_utility,
                # ... all from stored decision object
            )
            self._recorder.record_decision(step, record)
```

**Key Points:**

- ✅ No wrapping of `make_agent_decision()` (hot path stays fast)
- ✅ Minimal state addition to Agent class (one `last_decision` field)
- ✅ Recording reads completed decisions, never intercepts decision-making
- ✅ Determinism preserved (storing decision doesn't affect RNG or logic)

### Snapshot Strategy

**Periodic Snapshots:** Full world state captured at intervals.

```python
# Economic level: Snapshot every 100 steps
if step % 100 == 0:
    recorder.record_snapshot(step, agents, resources)

# Full Debug level: Snapshot every 50 steps
if step % 50 == 0:
    recorder.record_snapshot(step, agents, resources)
```

**Purpose:** Enable fast time-travel in explorer without replaying from step 0.

______________________________________________________________________

## 7. Query & Analysis

### Common Query Patterns

**Pattern 1: Agent Investigation**

```python
recording = SimulationRecording.load("my_run.vmtrec")

# Get complete history for agent 42
history = recording.agent_history(agent_id=42)

# Find when agent stopped trading
last_trade_step = max(
    d.step for d in history if d.decision_type == "trade"
)

# Analyze utility progression
utility_series = recording.agent_utility_series(agent_id=42)
```

**Pattern 2: Step Analysis**

```python
# What happened at step 500?
decisions = recording.decisions_at_step(500)
trades = recording.trades_at_step(500)

# How many agents were idle?
idle_count = sum(1 for d in decisions if d.decision_type == "idle")
```

**Pattern 3: Trade Network**

```python
# Build trade network for steps 400-600
trade_graph = defaultdict(list)
for step in range(400, 601):
    for trade in recording.trades_at_step(step):
        trade_graph[trade.agent1_id].append(trade.agent2_id)
        trade_graph[trade.agent2_id].append(trade.agent1_id)
```

### Web-Based Explorer

**Technology Stack:**

- Backend: Flask or FastAPI (lightweight Python web framework)
- Frontend: HTML5 Canvas for 2D view, Chart.js for plots
- Database: Direct SQLite queries from backend

**Key Features:**

1. **Timeline Scrubber:** Navigate to any step
2. **2D Visualization:** Show agent positions, resources (like visual_test_simple.py)
3. **Agent Inspector Panel:** Click agent → see decision details, inventory, utility
4. **Chart View:** Plot utility, trade frequency, movement over time
5. **Query Console:** Run custom SQL queries on recording

**Launch Command:**

```bash
vmt-explorer my_run.vmtrec
# Opens browser at http://localhost:5000
```

______________________________________________________________________

## 8. Performance Considerations

### Overhead Targets

**Debug Recording (Current Implementation):**

| Recording Level | Target Overhead | Achieved By                  |
| --------------- | --------------- | ---------------------------- |
| SUMMARY         | < 5%            | Aggregate metrics only       |
| ECONOMIC        | < 15%           | Batched writes, minimal data |
| FULL_DEBUG      | < 30%           | Selective option recording   |
| TRACE           | ~100%           | Function call interception   |

**Playback Recording (Future Implementation - Estimated):**

| Feature                      | Est. Overhead | Notes                    |
| ---------------------------- | ------------- | ------------------------ |
| Uncompressed                 | ~20%          | Full frame serialization |
| Compressed (planned default) | ~25%          | zlib compression adds 5% |

**Dual Recording (Future - When Playback Implemented):**

| Configuration         | Est. Combined Overhead | File Sizes (1000 steps, 100 agents)         |
| --------------------- | ---------------------- | ------------------------------------------- |
| ECONOMIC + Playback   | < 35%                  | .vmtrec: 1-5 MB, .vmtplay: 7-20 MB (est.)   |
| FULL_DEBUG + Playback | < 50%                  | .vmtrec: 10-20 MB, .vmtplay: 7-20 MB (est.) |

**Key Design:** Playback recording overhead will be independent of debug recording level, allowing
flexible combinations based on use case once implemented.

### Optimization Techniques

**1. Batched Writes**

```python
# Collect all decisions for a step
decision_batch = []
for agent in agents:
    decision_batch.append(create_decision_record(agent))

# Write all at once
recorder.record_decisions_batch(step, decision_batch)
```

**2. Lazy Serialization**

```python
# Don't serialize inventory if not needed
if level < RecordingLevel.FULL_DEBUG:
    decision.alternatives_considered = 0  # Skip this field
```

**3. Conditional Capturing**

```python
# Only wrap methods when recording is enabled
if recorder is not None:
    self._wrap_make_agent_decision()
```

**4. Database Indexes**

```sql
-- Critical for fast queries
CREATE INDEX idx_decisions_step_agent ON decisions(step, agent_id);
CREATE INDEX idx_decisions_agent ON decisions(agent_id);
```

### Benchmarking Strategy

**Test Scenario:** High Density Local (100 agents, 1000 steps)

```python
# Baseline (no recording)
baseline_time = run_simulation(recording=False)

# Economic level recording
economic_time = run_simulation(recording=True, level=RecordingLevel.ECONOMIC)

overhead_pct = ((economic_time - baseline_time) / baseline_time) * 100
assert overhead_pct < 15.0, f"Overhead {overhead_pct}% exceeds target"
```

### Determinism Verification

**Recording must not affect simulation behavior.** Verify with seed-based reproduction:

```bash
# Run same simulation twice with recording enabled
ECONSIM_DEBUG_RECORDING=1 python visual_test_simple.py --seed 12345 --output run1.vmtrec
ECONSIM_DEBUG_RECORDING=1 python visual_test_simple.py --seed 12345 --output run2.vmtrec

# Recordings should be identical (same decisions, trades, outcomes)
python -m econsim.tools.compare_recordings run1.vmtrec run2.vmtrec
# Expected: "Recordings are identical"

# Run with recording OFF, then ON - final state must match
ECONSIM_DEBUG_RECORDING=0 python tests/integration/test_determinism.py --seed 12345
ECONSIM_DEBUG_RECORDING=1 python tests/integration/test_determinism.py --seed 12345
# Expected: Both runs produce identical agent positions, utilities, inventories
```

**Automated Determinism Test:**

```python
def test_recording_preserves_determinism():
    """Verify recording doesn't change simulation behavior."""
    seed = 12345
    
    # Run without recording
    agents1, trades1 = run_simulation_without_recording(seed)
    
    # Run with recording
    agents2, trades2 = run_simulation_with_recording(seed)
    
    # Must be byte-for-byte identical
    assert agents1 == agents2, "Agent states diverged with recording!"
    assert trades1 == trades2, "Trade outcomes diverged with recording!"
    assert len(trades1) == len(trades2), "Trade counts differ!"
```

**Performance Breakdown by Recording Level:**

| Level      | Overhead | Hot Path Impact | Snapshot Freq | Est. Size (1000 steps, 100 agents) |
| ---------- | -------- | --------------- | ------------- | ---------------------------------- |
| SUMMARY    | \<5%     | None            | Never         | 50 KB (aggregates only)            |
| ECONOMIC   | \<15%    | None            | Every 100     | 1-5 MB (decisions + trades)        |
| FULL_DEBUG | \<30%    | None            | Every 50      | 10-20 MB (all options)             |
| TRACE      | ~100%    | Yes (wraps hot) | Every 10      | 100+ MB (function traces)          |

**Note:** TRACE level is the **only** level that wraps hot paths and should be used sparingly for
deep debugging of specific issues.

______________________________________________________________________

## 9. Extension Points

### Future Enhancements

**1. Streaming Recording** For very long simulations, write data in chunks and support append mode.

```python
recorder = DebugRecorder("long_run.vmtrec", mode="append")
```

**2. Remote Recording** Stream data to a remote server for distributed simulation analysis.

```python
recorder = RemoteDebugRecorder("http://analysis-server:8080/upload")
```

**3. Custom Metrics** Allow users to register custom metric extractors.

```python
recorder.register_metric("gini_coefficient", calculate_gini)
```

**4. Replay System** Use recordings to deterministically replay simulations (requires state
restoration).

```python
simulator = SimulationReplay.from_recording("my_run.vmtrec")
simulator.step_to(500)  # Restore state at step 500
```

**5. Diff Viewer** Compare two recordings to identify behavioral changes after code modifications.

```python
diff = RecordingComparator.compare("before.vmtrec", "after.vmtrec")
diff.show_agent_differences(agent_id=42)
```

### Extensibility Guidelines

**Adding New Data Types:**

1. Define dataclass in `schema.py`
2. Add table schema in `recorder.py`
3. Add recording method: `recorder.record_X()`
4. Add query method: `recording.get_X()`
5. Update recording level logic if needed

**Example: Recording Partnership Events**

```python
# 1. Define structure
@dataclass
class PartnershipRecord:
    step: int
    agent1_id: int
    agent2_id: int
    action: str  # "pair" or "unpair"

# 2. Add table
CREATE TABLE partnerships (
    step INTEGER,
    agent1_id INTEGER,
    agent2_id INTEGER,
    action TEXT
);

# 3. Recorder method
def record_partnership(self, step: int, record: PartnershipRecord):
    self._db.execute("INSERT INTO partnerships VALUES (?, ?, ?, ?)", ...)

# 4. Query method
def partnerships_at_step(self, step: int) -> List[PartnershipRecord]:
    return self._db.query("SELECT * FROM partnerships WHERE step = ?", step)
```

### Visual Playback Viewer (FUTURE IMPLEMENTATION - V1.1 Planned)

**Note:** This component will be implemented after the debug recording system is complete.

**PlaybackViewer** will provide frame-by-frame visual replay of recorded simulations:

**Planned Key Features:**

- **pygame-based rendering:** Same sprite rendering as `realtime_pygame_v2.py`
- **Timeline controls:** Play/pause/step-forward/step-backward
- **Speed adjustment:** 0.1x to 10x playback speed
- **Instant seeking:** Jump to any step via frame index (no replay from step 0)
- **Decision inspector integration:** Click agent → show decision details from `.vmtrec` file
- **Educational use:** Create reference runs for teaching economic concepts

**Planned Launch Commands:**

```bash
# Playback only (to be implemented)
vmt-playback sim_runs/251007_14-23-45-HDL-11111.vmtplay

# Playback with decision inspection (to be implemented)
vmt-playback sim_runs/251007_14-23-45-HDL-11111.vmtplay \
             --debug sim_runs/251007_14-23-45-HDL-11111.vmtrec

# Or use make target for latest recording (to be implemented)
make playback
```

**Planned Keyboard Controls:**

- `SPACE` - Play/Pause
- `RIGHT ARROW` - Step forward
- `LEFT ARROW` - Step backward
- `UP ARROW` - Increase speed (2x multiplier)
- `DOWN ARROW` - Decrease speed (0.5x divisor)
- `Mouse Click` - Inspect agent (if debug file loaded)

**Implementation Priority:** Low priority until debug recording system is complete and validated.

______________________________________________________________________

## Summary

The Debug Recording System (V1.1) is designed as a **phased dual-output recording solution** for
analyzing VMT EconSim simulations. By adhering to the **pure observer pattern**, the system
maintains complete separation from simulation logic. The architecture is designed to support both
economic reasoning capture and visual playback, though initial implementation focuses on debug
recording.

**Implementation Status:**

- ✅ **Debug Recording (Immediate)** - SQLite-based decision logs (`.vmtrec`) - **TO BE IMPLEMENTED
  FIRST**
- 🔜 **Playback Recording (Future)** - MessagePack frame stream (`.vmtplay`) - **PLANNED FOR LATER**

**Current Implementation (Immediate Priority):**

- ✅ **Debug logs (`.vmtrec`)** - Post-run analysis of agent decisions
- ✅ **Automatic by default** - No manual setup required in test runs
- ✅ **Zero simulation code modification** - Pure observer pattern
- ✅ **Transparent proxy design** - Full compatibility with existing code (`isinstance()` works)
- ✅ **Purpose-built for economic debugging** - Captures decision-making rationale
- ✅ **Query performance via SQLite indexes** - Fast analysis of 100k+ step simulations
- ✅ **\<15% overhead at ECONOMIC level** - Acceptable for always-on use
- ✅ **Extensible architecture** - Designed to add playback recording later

**Future Implementation (After Debug Recording Complete):**

- 🔜 **Playback stream (`.vmtplay`)** - Frame-by-frame visual replay
- 🔜 **Timeline controls** - Play/pause/seek for educational demos
- 🔜 **Visual playback viewer** - pygame-based rendering with decision inspection
- 🔜 **Independent overhead** - Est. \<25% for playback, \<35% combined
- 🔜 **Dual-output capability** - Enable debug, playback, or both via env vars

**Architectural Advantages:**

- **Default-on ensures data availability:** Recordings are always available when debugging is needed
- **Test runner integration:** Seamless wrapping in pytest fixtures and launcher processes
- **Configuration-driven:** Easy to disable or adjust recording modes via environment variables
- **Educational alignment:** Students automatically get recordings to analyze and replay simulations
- **Hot path avoidance:** Only wraps `coordinator.step()`, not decision logic (preserves
  performance)
- **Determinism guaranteed:** Recording never consumes RNG state or modifies simulation behavior
- **Transparent proxy:** Full compatibility with existing code (isinstance checks work)

**Performance & Correctness (Current Implementation):**

- ✅ \<15% overhead for debug recording at ECONOMIC level (default) - **TO BE VALIDATED**
- ✅ Zero hot path wrapping at ECONOMIC/FULL_DEBUG levels - **BY DESIGN**
- ✅ Determinism guaranteed: same seed = identical results with recording ON or OFF - **TO BE
  TESTED**
- ✅ Post-execution read pattern ensures no interference with simulation logic - **BY DESIGN**

**Performance & Correctness (Future Implementation):**

- 🔜 Est. \<25% overhead for playback recording (compressed)
- 🔜 Est. \<35% overhead for dual recording (both enabled)
- 🔜 Independent recording modes allow flexible overhead trade-offs

**Use Case Matrix (Current Implementation):**

| Context           | Debug | Playback | Rationale                                 |
| ----------------- | ----- | -------- | ----------------------------------------- |
| Unit Tests        | ✅    | 🔜       | Debug logs for analysis (playback future) |
| Visual Tests      | ✅    | 🔜       | Debug logs now, playback later            |
| GUI Launcher      | ✅    | 🔜       | Debug logs now, playback later            |
| Performance Tests | ✅    | 🔜       | Measure debug overhead (playback future)  |
| Production Runs   | ❌    | ❌       | Maximum speed, no recording               |

**Use Case Matrix (Future - After Playback Implemented):**

| Context           | Debug | Playback | Rationale                               |
| ----------------- | ----- | -------- | --------------------------------------- |
| Unit Tests        | ✅    | ❌       | Only need decision logs for debugging   |
| Visual Tests      | ✅    | ✅       | Benefit from both analysis and replay   |
| GUI Launcher      | ✅    | ✅       | Educational context needs visual replay |
| Performance Tests | ✅    | ❌       | Measure debug recording overhead        |
| Production Runs   | ❌    | ❌       | Maximum speed, no recording             |

**Implementation Roadmap:**

**Phase 1: Debug Recording (IMMEDIATE PRIORITY - Weeks 1-4)**

1. Implement `DebugRecorder` class (SQLite writer)
2. Implement `SimulationObserver` (single-recorder mode)
3. Implement `auto_enable_recording()` function (debug-only)
4. Implement `SimulationRecording` query interface
5. Add unit tests and integration tests
6. Validate \<15% overhead target
7. Test determinism guarantees

**Phase 2: Debug Analysis Tools (Weeks 5-6)**

1. Implement automated freeze detection
2. Create web-based recording explorer
3. Add query utilities and visualization

**Phase 3: Playback Recording (FUTURE - After Phase 1 & 2 Complete)**

1. Implement `PlaybackRecorder` class (MessagePack writer)
2. Implement `PlaybackReader` class
3. Update `SimulationObserver` to support dual recorders
4. Update `auto_enable_recording()` for playback flag
5. Implement `PlaybackViewer` GUI
6. Add playback-specific tests

**Next Steps:**

- See [Implementation Plan](DEBUG_RECORDING_SYSTEM_IMPLEMENTATION_PLAN.md) for detailed Phase 1
  development schedule
- See [Patch V1](DEBUG_RECORDING_ARCHITECTURE_PATCH_V1.md) for detailed Phase 3 (playback) system
  design
- **Current Focus:** Implement Phase 1 (debug recording) completely before starting Phase 3
  (playback)
