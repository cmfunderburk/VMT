# Educational Scenarios Refactor - Project Structure Plan

**Status**: Planning Phase (October 2025)  
**Purpose**: Separate economic models for educational clarity and theoretical validation  
**Related**: `a.md`, `Spatial_Economic_Theory_Framework.md`, `Opus_econ_model_review.md`

---

## Executive Summary

This refactor reorganizes the codebase to support **distinct, theoretically-validated economic models** that can be composed for educational scenarios. The goal is to:

1. **Isolate economic behaviors** (forage, bilateral exchange, market exchange) into separate, testable modules
2. **Create educational scenarios** that demonstrate one economic concept at a time
3. **Enable composition** of behaviors (e.g., forage + bilateral exchange) with clear theoretical models
4. **Improve GUI** to display utility, inventory, and decision-making rationale in real-time

### Key Principle
**Each behavior module implements ONE economic model with explicit mathematical foundation.** No ad-hoc mixing of behaviors without documented theory.

---

## Part I: Target Folder Structure

```
src/econsim/
├── __init__.py
├── main.py
│
├── agent/                          # Agent decision-making logic
│   ├── __init__.py
│   ├── core.py                     # Agent class (inventory, state)
│   ├── utility_functions.py       # Utility function implementations
│   │
│   ├── behaviors/                  # Economic behavior modules
│   │   ├── __init__.py
│   │   ├── base.py                 # Base behavior interface
│   │   ├── forage.py               # Single-agent utility maximization
│   │   ├── bilateral_exchange.py  # Two-agent pure exchange
│   │   ├── composite.py            # Logic for combining behaviors
│   │   │
│   │   └── market/                 # Future: Market-based exchange
│   │       ├── __init__.py
│   │       ├── centralized_market.py
│   │       └── decentralized_search.py
│   │
│   └── legacy/                     # Temporary: old unified_decision.py
│       ├── __init__.py
│       ├── unified_decision.py
│       └── modes.py
│
├── world/                          # Spatial environment
│   ├── __init__.py
│   ├── grid.py                     # Core grid implementation
│   ├── coordinates.py              # Manhattan distance, etc.
│   ├── spatial.py                  # AgentSpatialGrid indexing
│   ├── resources.py                # Resource spawning/respawn logic
│   ├── respawn.py                  # (keep or merge with resources.py)
│   │
│   └── helpers/                    # World utilities
│       ├── __init__.py
│       ├── pathfinding.py          # A* or Manhattan pathfinding
│       └── visibility.py           # Perception radius calculations
│
├── simulation/                     # Simulation orchestration
│   ├── __init__.py
│   ├── coordinator.py              # High-level step coordination
│   ├── executor.py                 # Two-phase execution
│   ├── features.py                 # Feature flags
│   ├── config.py                   # Simulation configuration
│   └── constants.py                # Global constants
│
├── gui/                            # PyQt6 visualization
│   ├── __init__.py
│   ├── launcher/                   # Main launcher window
│   │   ├── __init__.py
│   │   ├── main_window.py
│   │   └── tabs/
│   │       ├── __init__.py
│   │       ├── test_gallery.py     # Existing test gallery
│   │       └── educational_scenarios.py  # NEW: Educational tab
│   │
│   ├── embedded/                   # Simulation view
│   │   ├── __init__.py
│   │   ├── simulation_widget.py
│   │   └── overlays/
│   │       ├── __init__.py
│   │       ├── agent_info_overlay.py      # NEW: Detailed agent info
│   │       ├── utility_graph_overlay.py   # NEW: Live utility graph
│   │       └── decision_rationale.py      # NEW: Why agent chose action
│   │
│   └── widgets/                    # Reusable widgets
│       ├── __init__.py
│       ├── parameter_controls.py   # NEW: Sliders for utility params
│       └── scenario_selector.py    # NEW: Dropdown for scenarios
│
└── logging/                        # Debug and analysis tools
    ├── __init__.py
    ├── debug_recorder.py           # DebugRecorder (from CRITICAL/)
    ├── step_logger.py              # Per-step event logging
    └── economic_analytics.py       # NEW: Welfare analysis, efficiency metrics
```

---

## Part II: Behavior Module Design

### 2.1 Base Behavior Interface (`behaviors/base.py`)

```python
from abc import ABC, abstractmethod
from typing import Optional, Tuple
from ..core import Agent
from ...world.grid import Grid

class AgentBehavior(ABC):
    """
    Base class for all agent behaviors.
    Each behavior implements ONE economic model.
    """
    
    @abstractmethod
    def decide(
        self, 
        agent: Agent, 
        grid: Grid, 
        nearby_agents: list[Agent],
        rng: np.random.Generator
    ) -> AgentAction:
        """
        Make a decision for this agent given current state.
        
        Returns:
            AgentAction with action_type and optional parameters
        """
        pass
    
    @abstractmethod
    def get_theoretical_model(self) -> str:
        """
        Return a string describing the economic model implemented.
        Used for documentation and validation.
        """
        pass
    
    @abstractmethod
    def validate_assumptions(self, agent: Agent, grid: Grid) -> list[str]:
        """
        Check if the economic model's assumptions hold.
        Returns list of violated assumptions (empty if all valid).
        
        Example: "Agent must have non-zero inventory for bilateral exchange"
        """
        pass
```

### 2.2 Forage Behavior (`behaviors/forage.py`)

**Economic Model**: Single-agent utility maximization with distance-discounted values

```python
class ForageBehavior(AgentBehavior):
    """
    Implements single-agent utility maximization through resource collection.
    
    Theoretical Model:
    -----------------
    At each step, agent chooses action a to maximize:
        V(a) = E[U(bundle_t+1) | a]
    
    Where bundle_t+1 = current_bundle + collected_resource
    
    Distance Discounting:
        value(resource_r, distance_d) = MU(resource_r) * exp(-k * d)
    
    Decision Rule:
        1. Evaluate all visible resources by distance-discounted MU
        2. If best resource value > 0, move toward/collect it
        3. Else, deposit excess inventory at home or idle
    
    Assumptions:
        - Agent acts myopically (no multi-step planning)
        - Resources are stationary and observable
        - No strategic interaction with other agents
    """
    
    def __init__(self, distance_discount: float = 0.15):
        self.distance_discount = distance_discount
    
    def decide(self, agent, grid, nearby_agents, rng):
        # Find all visible resources
        visible_resources = grid.get_resources_in_radius(
            agent.x, agent.y, agent.perception_radius
        )
        
        # Evaluate each by distance-discounted MU
        best_resource, best_value = None, -float('inf')
        for resource in visible_resources:
            distance = manhattan_distance((agent.x, agent.y), (resource.x, resource.y))
            mu = agent.utility_function.marginal_utility(agent.total_bundle, resource.type)
            value = mu * math.exp(-self.distance_discount * distance)
            
            if value > best_value:
                best_value = value
                best_resource = resource
        
        # Decision logic
        if best_resource and best_value > 0:
            if agent.is_at(best_resource.x, best_resource.y):
                return AgentAction("collect", target_x=best_resource.x, target_y=best_resource.y)
            else:
                return AgentAction("move", direction=toward(best_resource))
        
        # Fallback: deposit at home if carrying excess
        if agent.has_carrying_inventory() and agent.is_at_home():
            return AgentAction("deposit")
        
        return AgentAction("idle")
    
    def get_theoretical_model(self) -> str:
        return """
        Single-agent utility maximization with exponential distance discounting.
        See: tmp_plans/MODELS/1_single_agent_utility_spatial.md
        """
    
    def validate_assumptions(self, agent, grid) -> list[str]:
        violations = []
        if agent.perception_radius <= 0:
            violations.append("Agent must have positive perception radius")
        return violations
```

### 2.3 Bilateral Exchange Behavior (`behaviors/bilateral_exchange.py`)

**Economic Model**: Pure exchange between two agents (Edgeworth box)

```python
class BilateralExchangeBehavior(AgentBehavior):
    """
    Implements bilateral exchange between two agents.
    
    Theoretical Model:
    -----------------
    Two agents i and j with endowments (e_i, e_j) and utility functions (U_i, U_j).
    
    Feasible Allocations:
        x_i + x_j = e_i + e_j  (resource balance)
    
    Pareto Improvement:
        Trade (e_i → x_i, e_j → x_j) occurs iff:
            U_i(x_i) > U_i(e_i) AND U_j(x_j) > U_j(e_j)
    
    Allocation Rule (Simplified):
        - Find goods where MU_i/MU_j differs from MU_j/MU_i
        - Exchange to equalize marginal rates of substitution (MRS_i = MRS_j)
        - In discrete case, exchange fixed unit amounts
    
    Assumptions:
        - Agents are co-located (no distance cost)
        - Perfect information about partner's utility
        - Enforceable contracts (no reneging)
        - No transaction costs
    """
    
    def __init__(self, trade_unit: int = 1):
        self.trade_unit = trade_unit
    
    def decide(self, agent, grid, nearby_agents, rng):
        # Only consider agents at same location
        colocated = [a for a in nearby_agents if a.is_at(agent.x, agent.y)]
        
        if not colocated:
            return AgentAction("idle")
        
        # Find best trading partner
        best_partner, best_gain = None, 0.0
        for partner in colocated:
            gain = self._evaluate_trade_opportunity(agent, partner)
            if gain > best_gain:
                best_gain = gain
                best_partner = partner
        
        if best_partner:
            return AgentAction("trade", partner=best_partner)
        
        return AgentAction("idle")
    
    def _evaluate_trade_opportunity(self, agent, partner):
        """
        Calculate mutual gains from trade.
        Returns sum of utility improvements if both benefit, else 0.
        """
        # Try all possible single-unit exchanges
        goods = agent.total_bundle.keys()
        best_joint_gain = 0.0
        
        for give_good in goods:
            for receive_good in goods:
                if give_good == receive_good:
                    continue
                
                # Check feasibility
                if agent.total_bundle[give_good] < self.trade_unit:
                    continue
                if partner.total_bundle[receive_good] < self.trade_unit:
                    continue
                
                # Calculate utility changes
                agent_new_bundle = agent.total_bundle.copy()
                agent_new_bundle[give_good] -= self.trade_unit
                agent_new_bundle[receive_good] += self.trade_unit
                
                partner_new_bundle = partner.total_bundle.copy()
                partner_new_bundle[receive_good] -= self.trade_unit
                partner_new_bundle[give_good] += self.trade_unit
                
                agent_gain = (
                    agent.utility_function.value(agent_new_bundle) -
                    agent.utility_function.value(agent.total_bundle)
                )
                partner_gain = (
                    partner.utility_function.value(partner_new_bundle) -
                    partner.utility_function.value(partner.total_bundle)
                )
                
                # Only trade if both benefit (Pareto improvement)
                if agent_gain > 0 and partner_gain > 0:
                    joint_gain = agent_gain + partner_gain
                    if joint_gain > best_joint_gain:
                        best_joint_gain = joint_gain
        
        return best_joint_gain
    
    def get_theoretical_model(self) -> str:
        return """
        Bilateral pure exchange (Edgeworth box) with Pareto improvement criterion.
        See: tmp_plans/MODELS/2_bilateral_pure_exchange.md
        """
    
    def validate_assumptions(self, agent, grid) -> list[str]:
        violations = []
        if agent.total_bundle_value() == 0:
            violations.append("Agent must have non-zero endowment for exchange")
        return violations
```

### 2.4 Composite Behavior (`behaviors/composite.py`)

**Purpose**: Combine forage and bilateral exchange with documented logic

```python
class CompositeBehavior(AgentBehavior):
    """
    Combines multiple behaviors with priority logic.
    
    Theoretical Model:
    -----------------
    Agent chooses between forage and exchange by comparing expected utility gains:
        action = argmax_a { V_forage, V_exchange }
    
    Where:
        V_forage = max_{r in resources} MU(r) * exp(-k * distance(r))
        V_exchange = max_{j in partners} E[ΔU | trade with j]
    
    Note: This is an APPROXIMATION. Optimal behavior may require multi-period
    planning (e.g., forage now to enable better trade later). Document deviations
    from true optimality.
    
    Assumptions:
        - Agents evaluate behaviors independently (no joint optimization)
        - No look-ahead beyond current step
        - Distance cost to reach partner is ignored (exchange is local)
    """
    
    def __init__(self, forage_behavior: ForageBehavior, exchange_behavior: BilateralExchangeBehavior):
        self.forage = forage_behavior
        self.exchange = exchange_behavior
    
    def decide(self, agent, grid, nearby_agents, rng):
        # Evaluate both behaviors
        forage_action = self.forage.decide(agent, grid, nearby_agents, rng)
        exchange_action = self.exchange.decide(agent, grid, nearby_agents, rng)
        
        # Estimate value of each action
        forage_value = self._estimate_action_value(agent, forage_action, grid)
        exchange_value = self._estimate_action_value(agent, exchange_action, grid)
        
        # Choose better option
        if exchange_value > forage_value:
            return exchange_action
        else:
            return forage_action
    
    def _estimate_action_value(self, agent, action, grid):
        """
        Estimate expected utility gain from action.
        Used for comparing different behavior options.
        """
        # Implementation details...
        pass
    
    def get_theoretical_model(self) -> str:
        return """
        Composite forage + bilateral exchange with greedy action selection.
        See: tmp_plans/MODELS/3_bilateral_forage_exchange.md
        Note: May not be globally optimal (no multi-step planning).
        """
    
    def validate_assumptions(self, agent, grid) -> list[str]:
        violations = []
        violations.extend(self.forage.validate_assumptions(agent, grid))
        violations.extend(self.exchange.validate_assumptions(agent, grid))
        return violations
```

---

## Part III: World Module Enhancements

### 3.1 Resource Management (`world/resources.py`)

Currently scattered across `grid.py` and `respawn.py`. Consolidate into:

```python
class ResourceManager:
    """
    Handles resource spawning, respawning, and availability tracking.
    """
    
    def __init__(self, grid: Grid, respawn_config: RespawnConfig):
        self.grid = grid
        self.respawn_config = respawn_config
        self.resources: dict[tuple[int, int], Resource] = {}
        self.respawn_timers: dict[tuple[int, int], int] = {}
    
    def spawn_initial_resources(self, resource_density: float, rng):
        """Place initial resources on grid according to density."""
        pass
    
    def collect_resource(self, x: int, y: int) -> Optional[Resource]:
        """Remove resource at location, start respawn timer."""
        pass
    
    def step_respawn(self):
        """Decrement respawn timers, spawn new resources when ready."""
        pass
    
    def get_resources_in_radius(self, cx: int, cy: int, radius: int) -> list[Resource]:
        """Return all resources within Manhattan distance radius."""
        pass
```

### 3.2 World Helpers (`world/helpers/`)

#### `pathfinding.py`
```python
def find_path(grid, start, goal) -> list[tuple[int, int]]:
    """A* pathfinding on Manhattan grid."""
    pass

def next_step_toward(current, target) -> Direction:
    """Return optimal direction for single-step movement toward target."""
    pass
```

#### `visibility.py`
```python
def get_visible_agents(grid, agent, perception_radius) -> list[Agent]:
    """Return all agents within perception radius."""
    pass

def get_visible_resources(resource_manager, agent, perception_radius) -> list[Resource]:
    """Return all resources within perception radius."""
    pass
```

---

## Part IV: Educational Scenarios GUI

### 4.1 New Launcher Tab (`gui/launcher/tabs/educational_scenarios.py`)

```python
class EducationalScenariosTab(QWidget):
    """
    Interactive educational scenarios demonstrating economic concepts.
    
    Scenarios:
        1. Choice and Utility (single agent, forage only)
        2. Bilateral Exchange (two agents, pure exchange)
        3. Forage and Exchange (three agents, composite behavior)
    """
    
    def __init__(self):
        super().__init__()
        self.scenario_selector = ScenarioSelector()
        self.parameter_controls = ParameterControls()
        self.simulation_view = SimulationWidget()
        self.info_panels = EducationalInfoPanels()
        
        self._setup_ui()
        self._connect_signals()
    
    def load_scenario(self, scenario_name: str):
        """Load scenario configuration and behavior modules."""
        if scenario_name == "Choice and Utility":
            self._load_single_agent_forage()
        elif scenario_name == "Bilateral Exchange":
            self._load_bilateral_exchange()
        elif scenario_name == "Forage and Exchange":
            self._load_composite_behavior()
```

### 4.2 Educational Overlays (`gui/embedded/overlays/`)

#### `agent_info_overlay.py`
```python
class AgentInfoOverlay(QWidget):
    """
    Displays detailed agent state:
    - Current inventory (carrying + home)
    - Current utility value
    - Marginal utilities for each good
    - Current action and decision rationale
    """
    
    def update_agent_info(self, agent: Agent):
        self.inventory_display.setText(self._format_inventory(agent))
        self.utility_display.setText(f"U = {agent.current_utility():.2f}")
        self.marginal_utilities.setText(self._format_marginal_utilities(agent))
        self.action_rationale.setText(self._explain_current_action(agent))
```

#### `utility_graph_overlay.py`
```python
class UtilityGraphOverlay(QWidget):
    """
    Real-time graph of agent utility over time.
    Shows how decisions affect welfare.
    """
    
    def __init__(self):
        self.utility_history: dict[int, list[float]] = {}  # agent_id -> utilities
        self.matplotlib_widget = MatplotlibWidget()
    
    def update_step(self, agents: list[Agent], step: int):
        for agent in agents:
            self.utility_history[agent.id].append(agent.current_utility())
        self._redraw_graph()
```

#### `decision_rationale.py`
```python
class DecisionRationaleOverlay(QWidget):
    """
    Explains WHY agent chose current action in economic terms.
    
    Examples:
    - "Moving north toward wood: MU_wood=0.43, discounted value=0.38"
    - "Trading with Agent 2: Expected ΔU=+0.15 (Pareto improvement)"
    - "Idle: No resources within perception radius"
    """
    
    def update_rationale(self, agent: Agent, decision_context: dict):
        explanation = self._generate_explanation(agent, decision_context)
        self.text_display.setText(explanation)
```

### 4.3 Parameter Controls (`gui/widgets/parameter_controls.py`)

```python
class ParameterControls(QWidget):
    """
    Interactive controls for adjusting economic parameters.
    
    Controls:
    - Utility function type (Cobb-Douglas, Perfect Substitutes, etc.)
    - Preference parameters (alpha, beta)
    - Distance discount rate
    - Perception radius
    - Resource spawn density
    """
    
    parameters_changed = pyqtSignal(dict)
    
    def __init__(self):
        super().__init__()
        self.utility_function_dropdown = QComboBox()
        self.alpha_slider = QSlider()
        self.beta_slider = QSlider()
        # ... more controls
    
    def get_current_parameters(self) -> dict:
        return {
            "utility_function": self.utility_function_dropdown.currentText(),
            "alpha": self.alpha_slider.value() / 100.0,
            "beta": self.beta_slider.value() / 100.0,
            # ...
        }
```

---

## Part V: Implementation Phases

### Phase 1: Core Behavior Modules (Week 1-2)
**Goal**: Extract behaviors from `unified_decision.py` into separate modules

1. Create `agent/behaviors/base.py` with `AgentBehavior` interface
2. Implement `ForageBehavior` with existing forage logic
3. Implement `BilateralExchangeBehavior` with existing trade logic
4. Write unit tests for each behavior in isolation
5. Move old code to `agent/legacy/`

**Success Criteria**:
- Each behavior module passes unit tests
- Theoretical models documented in docstrings
- No cross-dependencies between forage and exchange

### Phase 2: World Module Refactor (Week 2-3)
**Goal**: Clean up resource and spatial management

1. Create `world/resources.py` with `ResourceManager`
2. Consolidate respawn logic from `respawn.py`
3. Create `world/helpers/pathfinding.py` and `visibility.py`
4. Update `Grid` to use new resource manager
5. Write integration tests for world module

**Success Criteria**:
- Resource spawning/collection works identically to before
- Spatial queries return deterministic results
- World module tests pass

### Phase 3: Educational GUI (Week 3-4)
**Goal**: Build interactive educational scenarios

1. Create `gui/launcher/tabs/educational_scenarios.py`
2. Implement scenario configurations (1-3 agents, grid sizes)
3. Build `AgentInfoOverlay`, `UtilityGraphOverlay`, `DecisionRationaleOverlay`
4. Add `ParameterControls` for real-time adjustments
5. Connect parameter changes to simulation reloads

**Success Criteria**:
- All three scenarios (Choice, Exchange, Composite) launch and run
- Agent info displays update in real-time
- Parameter changes trigger simulation reset with new config

### Phase 4: Composite Behavior Logic (Week 4-5)
**Goal**: Implement and validate combined forage + exchange

1. Create `CompositeBehavior` in `behaviors/composite.py`
2. Document theoretical assumptions and limitations
3. Write model validation tests (see `Opus_econ_model_review.md`)
4. Compare composite behavior to separate behaviors
5. Document expected vs. optimal behavior discrepancies

**Success Criteria**:
- Composite behavior produces rational decisions
- Assumptions documented with formal model references
- Known limitations explained (e.g., no multi-step planning)

### Phase 5: Logging and Analytics (Week 5-6)
**Goal**: Add economic analysis tools

1. Implement `logging/economic_analytics.py`
2. Track welfare metrics (sum of utilities, Pareto efficiency)
3. Log trade events with before/after utility values
4. Generate summary statistics for educational scenarios
5. Integrate with existing `DebugRecorder`

**Success Criteria**:
- Can measure total welfare change over time
- Can verify all trades are Pareto improvements
- Summary stats help validate economic correctness

---

## Part VI: Migration Strategy

### Handling Legacy Code
During refactor, old `unified_decision.py` will remain in `agent/legacy/`:

```python
# agent/legacy/__init__.py
"""
Legacy unified decision module.
TO BE DEPRECATED after behavior modules validated.
"""

# Existing scenarios continue using legacy code until migration complete
```

### Gradual Transition
1. **New scenarios** use behavior modules from day 1
2. **Existing scenarios** continue with `unified_decision.py`
3. **After validation**, migrate existing scenarios one-by-one
4. **Delete legacy** only after all tests pass with new behaviors

### Test Parity Verification
```bash
# Run tests with both old and new implementations
make test-legacy   # Uses unified_decision.py
make test-new      # Uses behavior modules
diff legacy_results.json new_results.json  # Must match
```

---

## Part VII: Open Questions & Design Decisions

### 7.1 Composite Behavior Logic
**Question**: How should agent choose between forage and exchange?

**Options**:
1. **Greedy**: Evaluate both, pick higher expected utility gain (current proposal)
2. **Priority**: Always try exchange first, fallback to forage (simpler, less optimal)
3. **Probabilistic**: Sample action proportional to expected gains (stochastic)
4. **Optimal**: Solve multi-step DP (theoretically correct, computationally hard)

**Recommendation**: Start with **Greedy**, document limitations, consider optimal as future work.

### 7.2 Distance Cost in Bilateral Exchange
**Question**: Should exchange have distance cost (agents must co-locate)?

**Current**: No distance cost (agents exchange when co-located)
**Alternative**: Add "travel to partner" cost in utility evaluation

**Recommendation**: Keep distance-free for educational clarity. Document assumption.

### 7.3 GUI Update Frequency
**Question**: How often to update overlays (every step vs. on-demand)?

**Options**:
1. **Every step**: Shows continuous evolution (may be slow)
2. **On-demand**: User clicks agent to see details (faster, less automatic)
3. **Configurable**: Let user choose update rate

**Recommendation**: Start with **every step** for selected agents (e.g., 1-3 agents in educational scenarios).

### 7.4 Parameter Validation
**Question**: How to prevent users from setting impossible parameters (e.g., alpha=0, beta=0)?

**Options**:
1. **Hard constraints**: Sliders have min/max values
2. **Soft warnings**: Allow but show warning message
3. **Economic validation**: Check if preferences satisfy basic axioms

**Recommendation**: **Hard constraints** with tooltips explaining valid ranges.

---

## Part VIII: Success Metrics

### Economic Correctness
- [ ] All behaviors implement documented theoretical models
- [ ] Forage decisions maximize distance-discounted MU
- [ ] Bilateral trades are Pareto improvements
- [ ] Composite behavior is rational (even if not optimal)

### Code Quality
- [ ] Each behavior module has >90% test coverage
- [ ] No circular dependencies between modules
- [ ] All public methods have docstrings with economic context
- [ ] Legacy code isolated and scheduled for removal

### Educational Value
- [ ] Users can see utility values and marginal utilities in real-time
- [ ] Decision rationales display in plain English
- [ ] Parameter changes produce predictable behavior changes
- [ ] Each scenario clearly demonstrates ONE economic concept

### Performance
- [ ] No regression vs. baseline (see `make perf`)
- [ ] GUI updates at ≥20 FPS for educational scenarios (≤3 agents)
- [ ] Determinism maintained (same seed = identical results)

---

## Part IX: Risk Assessment

### High Risk
1. **Breaking existing scenarios**: Refactor may introduce bugs in working code
   - **Mitigation**: Keep legacy code, gradual migration, test parity
2. **Composite behavior complexity**: Combining forage + exchange is theoretically hard
   - **Mitigation**: Start with simple greedy logic, document limitations

### Medium Risk
1. **GUI performance**: Real-time overlays may slow down simulation
   - **Mitigation**: Update only visible agents, use efficient rendering
2. **Parameter explosion**: Too many controls may confuse users
   - **Mitigation**: Hide advanced parameters, provide presets

### Low Risk
1. **World module refactor**: Resource management is well-understood
   - **Mitigation**: Good test coverage, straightforward consolidation

---

## Part X: Next Steps

### Immediate Actions (After Economic Model Validation)
1. **Review this plan** with economic theory experts
2. **Finalize theoretical models** in `tmp_plans/MODELS/` directory
3. **Write failing tests** for each behavior module (test-driven development)
4. **Create skeleton files** with docstrings and interfaces

### Before Starting Implementation
- [ ] Economic framework validated (see `Spatial_Economic_Theory_Framework.md`)
- [ ] Formal models documented for all three behaviors
- [ ] This plan reviewed and approved
- [ ] Test structure agreed upon

### When Ready to Code
```bash
# Create skeleton structure
mkdir -p src/econsim/agent/behaviors
mkdir -p src/econsim/agent/legacy
mkdir -p src/econsim/world/helpers
mkdir -p src/econsim/gui/embedded/overlays
mkdir -p src/econsim/logging

# Start with behavior interfaces
touch src/econsim/agent/behaviors/base.py
touch src/econsim/agent/behaviors/forage.py
touch src/econsim/agent/behaviors/bilateral_exchange.py
touch src/econsim/agent/behaviors/composite.py

# Write tests FIRST
touch tests/unit/test_forage_behavior.py
touch tests/unit/test_bilateral_exchange_behavior.py
touch tests/integration/test_composite_behavior.py
```

---

## Appendix A: File Migration Map

| Current File | New Location | Notes |
|--------------|--------------|-------|
| `agent/unified_decision.py` | `agent/legacy/unified_decision.py` | Keep until migration complete |
| `agent/modes.py` | `agent/legacy/modes.py` | Replaced by behavior system |
| `agent/core.py` | `agent/core.py` | Keep, minimal changes |
| `agent/utility_functions.py` | `agent/utility_functions.py` | Keep, no changes |
| `world/grid.py` | `world/grid.py` | Keep, use ResourceManager |
| `world/respawn.py` | Merge into `world/resources.py` | Consolidate resource logic |
| `world/spatial.py` | `world/spatial.py` | Keep, no changes |
| `world/coordinates.py` | `world/coordinates.py` | Keep, no changes |

## Appendix B: Dependency Graph

```
agent/behaviors/forage.py
  ├─> agent/core.py (Agent class)
  ├─> agent/utility_functions.py (utility calculations)
  ├─> world/grid.py (resource queries)
  └─> world/coordinates.py (distance calculations)

agent/behaviors/bilateral_exchange.py
  ├─> agent/core.py
  ├─> agent/utility_functions.py
  └─> world/coordinates.py (for co-location check)

agent/behaviors/composite.py
  ├─> behaviors/forage.py
  ├─> behaviors/bilateral_exchange.py
  └─> agent/core.py

gui/launcher/tabs/educational_scenarios.py
  ├─> agent/behaviors/* (all behaviors)
  ├─> gui/widgets/parameter_controls.py
  ├─> gui/embedded/simulation_widget.py
  └─> simulation/coordinator.py

simulation/coordinator.py
  ├─> agent/behaviors/base.py (behavior interface)
  ├─> simulation/executor.py
  └─> world/grid.py
```

---

**Document Status**: Draft  
**Last Updated**: October 9, 2025  
**Next Review**: After economic model validation complete
