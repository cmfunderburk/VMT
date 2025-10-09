# EconSim Educational Scenarios + Behavior Split: Big Picture Plan

**Project Name**: Educational Scenarios Foundation (VMT EconSim)  
**Project Type**: Desktop GUI feature + Simulation behavior refactor  
**Development Philosophy**: Visual-first demonstrations of core microeconomics; deterministic, modular, test-driven

---

## Core Understanding

### 1. Problem & Success Definition

**Problem**: Create a cohesive, classroom-ready set of interactive economic scenarios, surfaced via a dedicated launcher tab, that cleanly demonstrate single-agent utility, bilateral exchange, and forage-and-exchange dynamics. Align the internal agent logic with this pedagogy by splitting decision logic into composable behavior modules.

**Mission**: Deliver three crisp, parameterized educational scenarios with immediate visual feedback and theory-accurate outcomes, while refactoring the agent decision engine to explicit behavior modules that are easy to reason about, test, and extend.

**Success Metrics**:

- **R-01**: Users can launch the three scenarios from an "Educational Scenarios" tab; each loads in < 1s and runs at 30+ FPS on dev machine
- **R-02**: In Choice & Utility, parameter changes (α, β, k) update predictions and agent actions within 100ms
- **R-03**: In Bilateral Exchange (pure endowment), sequential 1-for-1 exchanges converge within 5% of theoretical contract curve in ≥90% seeded runs
- **R-04**: In Forage-and-Exchange, both agents experience Pareto-improving trades after specialization ≥80% of runs with complementary preferences
- **R-05**: All scenarios deterministic under fixed seed; behavior replicated across 10 runs identically
- **R-06**: Behavior-split refactor preserves existing unit/integration tests or provides targeted updates with unchanged public semantics
- **R-07**: Educator can explain outcomes using on-screen inventories, utilities, and arrows that match analytical predictions

### 2. Key User Scenarios

- **S-01 Choice & Utility (5x5 grid)**
  - One agent; inventory + utility shown in GUI; dropdown selects utility form (Cobb-Douglas, Perfect Substitutes, Leontief); sliders for α, β, ε, distance discount k
  - Resources spawn randomly; agent chooses via distance-discounted marginal utility
  - Learning outcome: identify switching points and how preferences map to spatial behavior

- **S-02 Bilateral Exchange (Pure Endowment, 5x5)**
  - Two agents; no resources on grid; initial endowments differ; utilities and inventories visible
  - Sequential 1-for-1 trades when mutually beneficial (Pareto improvements)
  - Learning outcome: observe path of exchanges approaching the contract curve; welfare gains from trade

- **S-03 Forage-and-Exchange (5x5)**
  - Two or three agents; resources spawn; agents forage based on distance-discounted MU, then exchange
  - Learning outcome: specialization by proximity, then gains from trade; narrow self-interest foraging vs overall utility with exchange

---

## Assumptions & Validations

- **A-01**: Behavior-split (Forage, BilateralExchange, Dual) improves testability and conceptual clarity over monolithic `unified_decision`
  - Validation: unit tests on behavior modules; integration parity tests vs current unified flow

- **A-02**: New tab can reuse existing launcher patterns (tabs/manager, cards) with a scenario registry
  - Validation: headless instantiation in tests + Qt smoke tests

- **A-03**: 1-for-1 trade protocol is sufficient for MVP pedagogy, variable ratios deferred
  - Validation: analytical expectations in Phase 2.2 tests; upgrade path documented

- **A-04**: Distance discount suffices for spatial cost pedagogy for now; explicit travel costs optional later
  - Validation: correctness tests focus on relative decisions, not absolute travel accounting

---

## Phase 2: Design Contracts

### 3. Domain Model (extensions)

- **Behavior Modules** (`econsim.simulation.agent.behaviors`)
  - `base.py`: `Behavior` protocol with `decide(agent, context) -> AgentAction`
  - `forage.py`: distance-discounted resource targeting and collect/deposit flow
  - `bilateral_exchange.py`: partner search, Pareto check, pair/trade/unpair
  - `dual.py`: composition policy for forage + trade precedence and inventory bootstrap

- **Coordinator**
  - Keep `unified_decision.make_agent_decision()` as the single entrypoint; delegate to selected `Behavior` strategy based on `SimulationFeatures`

- **Scenario Descriptors**
  - Pure data for GUI cards: grid size, agent count, utility presets, endowments/spawn rules

### 4. Core Interfaces (intent)

- `Behavior.decide(agent, ctx) -> AgentAction`
  - Inputs: agent, nearby resources/agents, features, rng, step
  - Output: `AgentAction` (existing structure preserved)

- `ScenarioSpec`
  - Fields: `id`, `label`, `grid`, `agents`, `utilities`, `endowments`, `spawns`, `ui_controls`
  - Consumed by `EducationalScenariosTab`

- `EducationalScenariosTab`
  - Renders `ScenarioSpec` cards; Launch → constructs config → executor

### 5. Error Handling Strategy (educational)

- Transform edge cases into teachable moments (e.g., no beneficial trade → show MU ratios and why)
- Deterministic tiebreaking with clear on-screen rationale strings from `AgentAction.reason`

### 6. Testing Strategy Outline

- **T-01 Scenario Acceptance**: Each scenario launches, runs, and produces expected visual state markers (inventories/utilities increasing where predicted)
- **T-02 Economic Correctness**: Analytical validations for switching points (S-01), Pareto improvements and near-contract allocations (S-02), specialization + trade (S-03)
- **T-03 Determinism**: Fixed seeds reproduce paths; sorted tie rules verified
- **T-04 Refactor Parity**: Behavior-split decisions match legacy unified outcomes in controlled seeds

### 7. Integration & Dependencies

- No new external dependencies required; reuse PyQt6 + Pygame embedding and existing executor
- Scenario overlays (e.g., contract curve) implemented in existing render layers incrementally

---

## Phase 3: Implementation Readiness

### 8. Directory Structure & File Plan

```
src/econsim/simulation/agent/behaviors/
  base.py                    # Behavior protocol/interface
  forage.py                  # S-01 core logic
  bilateral_exchange.py      # S-02 core logic
  dual.py                    # S-03 composition policy

src/econsim/simulation/agent/
  unified_decision.py        # Delegate to behaviors; preserves entrypoint

src/econsim/gui/launcher/tabs/
  educational_tab.py         # New tab UI

src/econsim/gui/launcher/
  registry.py                # Extend with ScenarioSpec registry (or new module)
```

### 9. Tooling & Quality

- Maintain existing lint/type/test gates; add new unit tests for behaviors + scenario acceptance tests
- Visual smoke tests for Qt components under offscreen platform

---

## Phase 4: Implementation Roadmap (MVP focus)

### Milestone 1: Behavior Skeletons + Delegation (Week 1)

- Extract `forage`, `bilateral_exchange`, `dual` logic from `unified_decision` into `behaviors/`
- Keep public function `make_agent_decision()` stable; feature flags select behavior
- Add unit tests for each behavior module; update/refactor existing tests to use new paths

### Milestone 2: Educational Scenarios Tab (Week 2)

- Add `EducationalScenariosTab` mirroring gallery patterns; render three scenario cards
- Define `ScenarioSpec` data and simple registry; wire Launch → executor configs
- Headless and smoke tests for tab instantiation and basic interactions

### Milestone 3: Choice & Utility (S-01) (Week 3)

- Implement parameter sliders (α, β, ε, k) and utility selector; live predictions vs actual actions
- Show inventories, utility value, and directional arrows to predicted target
- Acceptance + analytical tests for switching points and sensitivity sweeps

### Milestone 4: Bilateral Exchange (S-02) (Week 4)

- Pure endowment setup; 1-for-1 exchange; contract-curve overlay (discrete approximation)
- Tests: Pareto improvement per trade; convergence within tolerance; no-trade at equilibrium

### Milestone 5: Forage-and-Exchange (S-03) (Week 5)

- Forage specialization by proximity; withdraw/deposit policy; partner search; exchange execution
- Tests: specialization metrics; trades occur; total utility increases until no beneficial trades

---

## Architecture Decisions

### D-01: Split Behaviors vs Monolith

- Decision: Create `behaviors/` with explicit `forage`, `bilateral_exchange`, `dual` modules; `unified_decision` delegates
- Rationale: Pedagogical alignment, test isolation, easier extension
- Consequences: Small refactor cost; preserve entrypoint to minimize churn

### D-02: MVP Trade Protocol = 1-for-1

- Decision: Keep 1-for-1 discrete exchanges; variable ratios deferred
- Rationale: Simplicity for classroom clarity; analytical validation straightforward
- Revisit: After S-02 validation; see variable-ratio design document

### D-03: Distance Discount as Spatial Cost Model

- Decision: Continue using distance discount in decision utility; no explicit travel cost ledger
- Rationale: Matches current code; clear intuition for students
- Revisit: If instructors request separate cost accounting or market travel analyses

### D-04: UI Surfacing via Dedicated Tab

- Decision: Add `EducationalScenariosTab` rather than overloading Test Gallery
- Rationale: Clear educator-facing entry; keeps experiments/tests separate
- Consequences: One additional tab to maintain; reuses existing widget patterns

---

## Scenario Details (Teaching Outcomes)

### S-01 Choice & Utility

- Demonstrate: (1) switching by distance-discounted MU, (2) switching points as k varies, (3) collection proportions match α, β tendencies

### S-02 Bilateral Exchange (Pure Endowment)

- Demonstrate: (1) trade only if both benefit, (2) sequential trades approach contract curve, (3) trade improves welfare

### S-03 Forage-and-Exchange

- Demonstrate: (1) forage via distance-discounted MU, (2) exchange shaped by preference parameters, (3) narrow forage U-max may be suboptimal when exchange available

---

## Success Checklist (Incremental)

1. [ ] Behaviors extracted with parity tests vs current unified logic
2. [ ] Delegation via `make_agent_decision()` selects correct behavior per features
3. [ ] EducationalScenariosTab renders three scenarios with launch wiring
4. [ ] S-01 sliders + predictions update live; tests green for switching points
5. [ ] S-02 contract-curve overlay; Pareto + convergence tests pass
6. [ ] S-03 specialization + trade metrics validate learning outcomes
7. [ ] Determinism tests pass across all scenarios

---

## Open Questions

1. Should we surface ε and k in S-01 by default, or hide behind an "Advanced" toggle?
2. For S-02 overlays, what’s the preferred discrete approximation for the contract curve in a 5x5 setting?
3. In S-03, do we allow 3-agent variant at MVP, or focus strictly on 2 agents first for clarity?
4. Where should scenario run exports live (CSV, JSON) for classroom artifacts?

---

## Next Actions (This Week)

1. Create `behaviors/` skeletons and delegate from `unified_decision`
2. Draft `EducationalScenariosTab` with static cards and no-op launch
3. Define `ScenarioSpec` structures for S-01/02/03; stub registry
4. Add parity tests ensuring refactor doesn’t change existing behavior under fixed seeds

