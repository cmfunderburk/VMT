# Economic Model Implementation Plan

**Created**: October 8, 2025  
**Status**: Planning Phase  
**Purpose**: Bridge textbook microeconomic theory → spatial grid implementation

---

## Overview

This plan structures the development of mathematically rigorous economic models for the VMT EconSim platform, progressing from foundational single-agent utility maximization through bilateral exchange to market mechanisms. Each phase requires explicit mathematical specification, theoretical predictions, and validation tests.

**Core Principle**: Document the relationship between classical economic theory and spatial discrete-time implementation BEFORE coding.

---

## Phase 1: Single-Agent Utility Demonstration (Foundation)

**Goal**: Establish spatial-utility relationship through interactive single-agent scenarios where parameter changes produce predictable behavioral changes.

**Status**: 🔴 Not Started

### 1.1 Mathematical Model Specification

**Document**: `tmp_plans/MODELS/single_agent_utility_spatial.md`

**Required Content**:
```markdown
## Agent Decision Problem (Spatial Context)

At each timestep t, agent at position (x_a, y_a) observes:
- Resource A at positions {(x_i^A, y_i^A)} within perception radius R
- Resource B at positions {(x_j^B, y_j^B)} within perception radius R
- Current bundle: (q_1^carry + q_1^home, q_2^carry + q_2^home)

Agent chooses action a* to maximize expected utility gain:
  a* = argmax_a { ΔU(a) · exp(-k · d(a)) }

where:
- ΔU(a) = U(bundle + Δq(a)) - U(bundle)
- d(a) = Manhattan distance to target
- k = distance discount constant (currently 0.15)
- Δq(a) = expected good change from action a

## Utility Functions

### Cobb-Douglas: U(q_1, q_2) = (q_1 + ε)^α · (q_2 + ε)^β
- α + β = 1 (normalized)
- ε = 0.01 (prevents divide-by-zero)
- MU_1 = α · U / (q_1 + ε)
- MU_2 = β · U / (q_2 + ε)

### Perfect Substitutes: U(q_1, q_2) = α·q_1 + β·q_2
- Linear indifference curves
- MU_1 = α (constant)
- MU_2 = β (constant)

### Perfect Complements: U(q_1, q_2) = min(α·q_1, β·q_2)
- Right-angle indifference curves
- MU computation requires checking which good is binding
```

**Deliverables**:
- [ ] Complete mathematical specification document
- [ ] Analytical predictions for each utility type
- [ ] Distance-preference tradeoff calculations
- [ ] Parameter sensitivity analysis

### 1.2 Interactive Parameter Manipulation GUI

**Feature**: Real-time utility parameter adjustment with immediate visual feedback

**Implementation Requirements**:
- Slider controls for α, β (preference parameters)
- Slider for distance discount k
- Slider for ε (epsilon) with warning about divide-by-zero
- Visual display of:
  - Current indifference curves
  - Distance-discounted values for visible resources
  - Predicted next action
  - Actual chosen action (validation)
  
**Success Criteria**:
- [ ] Parameter changes update within 100ms
- [ ] Agent behavior matches analytical predictions in 95%+ of test cases
- [ ] Visual prediction arrows match actual agent choices
- [ ] Students can predict behavior changes before parameter adjustment

**Code Locations**:
- GUI controls: `src/econsim/gui/widgets/parameter_controls.py` (new)
- Real-time utility display: `src/econsim/gui/widgets/utility_display.py` (new)
- Integrate with: `src/econsim/gui/embedded/realtime_pygame_v2.py`

### 1.3 Validation Scenarios

**Scenario 1.1**: Equal Distance Choice (Pure Preference)
```python
# Setup:
# - Agent at (10, 10) with bundle (5, 5)
# - Resource A at (10, 15) - distance 5
# - Resource B at (15, 10) - distance 5
# - Cobb-Douglas with α=0.7, β=0.3

# Analytical Prediction:
# MU_A = 0.7 * U / 5.01 ≈ higher
# MU_B = 0.3 * U / 5.01 ≈ lower
# Distance equal → choose based on MU → choose A

# Success: Agent chooses Resource A
```

**Scenario 1.2**: Distance-Preference Tradeoff
```python
# Setup:
# - Agent at (10, 10) with bundle (10, 10)
# - Resource A at (10, 12) - distance 2
# - Resource B at (10, 20) - distance 10
# - Cobb-Douglas with α=0.5, β=0.5

# Vary distance_B from 2 to 20, predict switching point
# At balanced bundle, MU_A = MU_B
# Switching point: exp(-0.15*d_B) = exp(-0.15*2)
# d_B ≈ 2 (no preference when equal)

# Success: Switching occurs at predicted distance
```

**Scenario 1.3**: Parameter Sensitivity
```python
# Setup: Fixed resource layout
# Sweep α from 0.1 to 0.9 (β = 1 - α)
# Record agent choices at each parameter value

# Prediction: 
# - Low α → prefer good 2 (higher β)
# - High α → prefer good 1
# - α=0.5 → distance-based choice

# Success: Behavioral transition matches prediction
```

**Implementation**:
- [ ] Create test scenarios in `tests/validation/test_single_agent_utility.py`
- [ ] Automated validation against analytical solutions
- [ ] Visual test mode for educational demonstration
- [ ] Export results for documentation

---

## Phase 2: Bilateral Exchange with Foraging

**Goal**: Model and validate 2-agent forage-and-trade system where agents collect resources then exchange to mutual benefit.

**Status**: 🔴 Not Started

**Critical**: This is the foundation for all multi-agent economics. Get this right before proceeding.

### 2.1 Two-Agent Forage-and-Exchange Model

**Document**: `tmp_plans/MODELS/bilateral_forage_exchange.md`

**Scenario Setup**:
```markdown
## Agents:
- Agent 1: Cobb-Douglas U_1(q_1, q_2) = (q_1 + ε)^0.7 · (q_2 + ε)^0.3
- Agent 2: Cobb-Douglas U_2(q_1, q_2) = (q_1 + ε)^0.3 · (q_2 + ε)^0.7

Initial bundles: (0, 0) for both
Homes: Agent 1 at (5, 5), Agent 2 at (15, 15)

## Resources:
- Good 1 (Resource A) clustered near Agent 1's home
- Good 2 (Resource B) clustered near Agent 2's home

## Economic Predictions:

### Foraging Phase:
Agent 1 collects primarily Good 1 (lower travel cost, but not preferred)
Agent 2 collects primarily Good 2 (lower travel cost, but not preferred)

After foraging:
- Agent 1 bundle: (~10, ~2) - specialization due to proximity
- Agent 2 bundle: (~2, ~10) - specialization due to proximity

### Exchange Phase:
Gains from trade exist because:
- Agent 1: MU_1 / MU_2 = (0.7/10.01) / (0.3/2.01) ≈ 0.47 (values good 2 highly)
- Agent 2: MU_1 / MU_2 = (0.3/2.01) / (0.7/10.01) ≈ 2.13 (values good 1 highly)

1-for-1 exchange (Agent 1 gives Good 1, receives Good 2):
- Agent 1: ΔU_1 = U(9, 3) - U(10, 2) > 0 ✓
- Agent 2: ΔU_2 = U(3, 9) - U(2, 10) > 0 ✓

Both benefit (Pareto improvement) → trade occurs

### Spatial Dynamics:
Agents must:
1. Forage efficiently (minimize distance costs)
2. Store goods at home (inventory management)
3. Find trading partner (perception radius constraint)
4. Move to trading location (travel cost)
5. Execute exchange (1-for-1 currently)

Trade occurs when: ΔU_1 + ΔU_2 > 2 * travel_cost_utility
```

**Theoretical Questions to Answer**:
- [ ] What is the equilibrium bundle for each agent?
- [ ] How many trades occur before equilibrium?
- [ ] Does spatial separation prevent mutually beneficial trades?
- [ ] What happens if perception radius < distance between homes?
- [ ] How do distance costs affect comparative advantage?

**Implementation Requirements**:
- [ ] Explicit trade decision logic with Pareto improvement check
- [ ] Distance-adjusted trade valuation (current: ignores travel cost)
- [ ] Trade coordination in Phase 2 execution
- [ ] Multiple-trade convergence to equilibrium

**Validation Tests**:
```python
# tests/validation/test_bilateral_forage_exchange.py

def test_complementary_preferences_lead_to_trade():
    """Agent 1 prefers A, Agent 2 prefers B → specialization + exchange"""
    # Expected: At least 1 trade, both agents better off

def test_trade_increases_total_utility():
    """Sum of utilities increases after each trade"""
    # Expected: U_1(t+1) + U_2(t+1) > U_1(t) + U_2(t)

def test_equilibrium_convergence():
    """Agents reach point where no more beneficial trades exist"""
    # Expected: MU ratios converge within tolerance

def test_spatial_barrier_prevents_trade():
    """Large distance between homes prevents economically beneficial trade"""
    # Expected: No trades when homes > perception radius * 2
```

### 2.2 Bilateral Exchange WITHOUT Foraging (Pure Endowment Economy)

**Document**: `tmp_plans/MODELS/bilateral_pure_exchange.md`

**Scenario Setup**:
```markdown
## Edgeworth Box in Spatial Grid

Agents start with fixed endowments (no foraging):
- Agent 1: (20, 5) at position (10, 10)
- Agent 2: (5, 20) at position (12, 12)

Total economy: (25, 25) - fixed total

## Classical Edgeworth Box Predictions:

Contract curve (Pareto optimal allocations):
For Cobb-Douglas (α_1, β_1) and (α_2, β_2):
  MU_1^1 / MU_2^1 = MU_1^2 / MU_2^2

With α_1=0.7, β_1=0.3, α_2=0.3, β_2=0.7:
  (0.7/q_1^1) / (0.3/q_2^1) = (0.3/q_1^2) / (0.7/q_2^2)

Solving: optimal allocation around (17.5, 12.5) for Agent 1

## Spatial Implementation Differences:

1. **Discrete exchanges**: Can only trade in integer units
2. **Travel costs**: Agents must move to common location
3. **Sequential trades**: 1-for-1 exchanges, not continuous
4. **Perception constraint**: Must be within radius to negotiate

## Key Question: 
Does sequential 1-for-1 exchange converge to contract curve?
```

**Theoretical Analysis Required**:
- [ ] Prove/disprove: 1-for-1 exchanges reach Pareto frontier
- [ ] Calculate: Number of trades needed for convergence
- [ ] Model: Effect of discrete vs continuous exchange
- [ ] Analyze: Path dependency in trade sequences

**Implementation**:
- [ ] Disable foraging (feature flag: `ECONSIM_FORAGE_ENABLED=0`)
- [ ] Initialize agents with endowments in `Agent.__init__()`
- [ ] Pure exchange scenario in launcher
- [ ] Visualization of contract curve overlay

**Validation**:
```python
def test_pure_exchange_reaches_pareto_optimum():
    """Sequential 1-for-1 trades should reach contract curve (or close)"""
    # Success: Final allocation within 5% of theoretical optimum

def test_no_trade_at_equilibrium():
    """At Pareto optimum, no further beneficial trades exist"""
    # Success: No trades executed after equilibrium reached

def test_initial_allocation_affects_path_not_destination():
    """Different starting endowments reach same contract curve"""
    # Success: Multiple paths converge to similar final state
```

### 2.3 Extending Beyond 1-for-1 Exchange

**Goal**: Enable variable exchange ratios (e.g., 2-for-3 trades) based on marginal utility ratios.

**Document**: `tmp_plans/MODELS/variable_ratio_exchange.md`

**Economic Theory**:
```markdown
## Optimal Exchange Ratio

For Agent 1 offering Good 1, Agent 2 offering Good 2:

Agent 1 willing to give up to: x_1 units of Good 1
for at least: x_2 units of Good 2

where: MU_1^1 · x_1 = MU_2^1 · x_2
solving: x_2 / x_1 = MU_1^1 / MU_2^1 (Agent 1's MRS)

Similarly, Agent 2's MRS: x_2 / x_1 = MU_1^2 / MU_2^2

## Bargaining Solution

Trade ratio must satisfy both agents' constraints:
  MU_1^2 / MU_2^2 ≤ (Δq_2 / Δq_1) ≤ MU_1^1 / MU_2^1

Any ratio in this range creates Pareto improvement.

## Implementation Challenges:

1. **Discrete units**: Cannot trade fractional goods
2. **Rounding**: May create asymmetric benefits
3. **Bargaining protocol**: How to determine specific ratio?
4. **Computational complexity**: Searching over ratio space

## Proposed Solution:

Start with simple heuristic:
- Ratio = geometric mean of MU ratios
- Round to nearest integer ratio
- Verify Pareto improvement before executing
```

**Implementation Phases**:
- [ ] **Phase 2.3a**: Design variable ratio data structures
- [ ] **Phase 2.3b**: Implement MU-based ratio calculation
- [ ] **Phase 2.3c**: Add integer rounding with Pareto verification
- [ ] **Phase 2.3d**: Validation against optimal exchange theory

**Success Criteria**:
- Variable ratios reach equilibrium faster than 1-for-1
- Final allocations closer to theoretical contract curve
- No rejected trades that would benefit both parties

---

## Phase 3: Market Exchange Mechanisms

**Goal**: Transition from bilateral negotiation to market-clearing mechanisms (Walrasian auctioneer, double auction, etc.)

**Status**: 🔴 Blocked until Phase 2 complete

**Prerequisite**: Phase 2 must be fully validated. Market mechanisms build on bilateral exchange foundations.

### 3.1 Walrasian Auctioneer (Theoretical Benchmark)

**Document**: `tmp_plans/MODELS/walrasian_market.md`

**Overview**: Centralized price mechanism that finds market-clearing prices.

**Theory**:
```markdown
## Market Clearing Condition

For N agents with utility functions U_i(q_1^i, q_2^i):

At prices (p_1, p_2), each agent maximizes utility subject to budget:
  max U_i(q_1^i, q_2^i)
  s.t. p_1·q_1^i + p_2·q_2^i ≤ p_1·e_1^i + p_2·e_2^i

where e^i is initial endowment.

Market clears when:
  Σ_i q_1^i = Σ_i e_1^i  (total demand = total supply for Good 1)
  Σ_i q_2^i = Σ_i e_2^i  (total demand = total supply for Good 2)

## Computational Implementation:

1. Auctioneer announces prices (p_1, p_2)
2. Each agent submits demand (q_1^i, q_2^i) based on utility max
3. Auctioneer adjusts prices based on excess demand
4. Iterate until market clears (ε-convergence)

## Spatial Adaptation:

- Agents must move to "market location" to participate
- Distance costs affect willingness to trade
- Price adjustments visible in real-time GUI
```

**Implementation Details**: (Defer until Phase 2 complete)

### 3.2 Decentralized Market (Double Auction)

**Document**: `tmp_plans/MODELS/double_auction_spatial.md`

**Overview**: Order book system where agents post bids/asks, market clears through matching.

**Defer**: Document structure only, full details after Phase 2.

### 3.3 Spatial Market Centers

**Document**: `tmp_plans/MODELS/spatial_market_centers.md`

**Overview**: Multiple trading locations with transportation costs affecting price arbitrage.

**Defer**: Document structure only, full details after Phase 2.

---

## Implementation Priorities

### Immediate Actions (This Week)

1. **Document Single-Agent Utility Model** (Phase 1.1)
   - Create `tmp_plans/MODELS/single_agent_utility_spatial.md`
   - Complete mathematical specifications
   - Generate analytical predictions for test scenarios

2. **Document Bilateral Forage-Exchange Model** (Phase 2.1)
   - Create `tmp_plans/MODELS/bilateral_forage_exchange.md`
   - Specify 2-agent scenario with exact parameters
   - Calculate theoretical equilibrium

3. **Document Pure Exchange Model** (Phase 2.2)
   - Create `tmp_plans/MODELS/bilateral_pure_exchange.md`
   - Relate to Edgeworth box theory
   - Analyze discrete vs continuous exchange

### Next Sprint (After Documentation)

4. **Implement Phase 1 Validation Tests**
   - Create `tests/validation/test_single_agent_utility.py`
   - Automated comparison: predicted vs actual behavior
   - Visual test scenarios for demonstration

5. **Design Phase 1 Interactive GUI**
   - Sketch parameter control interface
   - Plan real-time utility visualization
   - Integration with existing launcher

### Future Sprints (Sequentially)

6. **Implement Phase 2.1**: Forage-and-exchange validation
7. **Implement Phase 2.2**: Pure exchange scenarios
8. **Implement Phase 2.3**: Variable ratio exchange
9. **Design Phase 3**: Market mechanisms (documentation only initially)

---

## Success Metrics

### Phase 1 Success:
- [ ] Single-agent behavior matches analytical predictions in 95%+ of test cases
- [ ] Parameter changes produce immediate, predictable behavioral changes
- [ ] Students can correctly predict agent choices after 5-minute tutorial

### Phase 2 Success:
- [ ] Two-agent trades converge to theoretical equilibrium
- [ ] Pareto improvements detected correctly 100% of time
- [ ] Spatial costs properly incorporated into trade decisions
- [ ] Variable ratio exchanges reach equilibrium faster than 1-for-1

### Phase 3 Success (Future):
- [ ] Market-clearing prices converge to theoretical predictions
- [ ] Decentralized mechanisms achieve efficient allocations
- [ ] Spatial market structure demonstrations work correctly

---

## Open Questions (Requiring Expert Review)

1. **Discrete Exchange Convergence**: Does sequential 1-for-1 exchange provably reach the contract curve? Or only approach it asymptotically?

2. **Spatial Cost Integration**: Should travel costs enter utility function directly, or remain as distance-discounting in decision logic?

3. **Perception Radius Economics**: How does limited information (perception radius) affect market efficiency? Need formal model.

4. **Integer Rounding in Variable Ratios**: What's the impact of rounding exchange ratios on equilibrium convergence?

5. **Multi-Agent Convergence**: Beyond 2 agents, what are convergence guarantees for bilateral sequential exchange?

---

## Documentation Structure

```
tmp_plans/MODELS/
├── single_agent_utility_spatial.md          # Phase 1.1
├── bilateral_forage_exchange.md             # Phase 2.1
├── bilateral_pure_exchange.md               # Phase 2.2
├── variable_ratio_exchange.md               # Phase 2.3
├── walrasian_market.md                      # Phase 3.1 (future)
├── double_auction_spatial.md                # Phase 3.2 (future)
└── spatial_market_centers.md                # Phase 3.3 (future)

tests/validation/
├── test_single_agent_utility.py             # Phase 1 tests
├── test_bilateral_forage_exchange.py        # Phase 2.1 tests
├── test_bilateral_pure_exchange.py          # Phase 2.2 tests
└── test_variable_ratio_exchange.py          # Phase 2.3 tests
```

---

## Next Steps

1. **Review this plan** - Validate progression and priorities
2. **Create Phase 1.1 document** - Start with single-agent utility model
3. **Mathematical validation** - Verify all analytical predictions
4. **Begin Phase 1 implementation** - After documentation complete

**Critical**: Do NOT proceed to implementation until mathematical models are fully documented and peer-reviewed.
