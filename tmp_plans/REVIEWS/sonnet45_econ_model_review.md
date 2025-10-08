# Economic Model Review: Simulation vs Theory Gap Analysis

**Date:** October 7, 2025\
**Author:** Claude 3.5 Sonnet (via copilot-instructions.md context)\
**Purpose:** Comprehensive guide for explicit economic model documentation and validation

______________________________________________________________________

## Executive Summary

Your EconSim platform implements three foundational utility functions (Cobb-Douglas, Perfect
Substitutes, Perfect Complements) within a **spatial, discrete-time, resource-constrained
environment**. The implementation is economically sound but operates in a **hybrid theoretical
space** between classical microeconomic theory and computational spatial economics.

**Key Gap:** Your simulation lacks **explicit economic models** that bridge the gap between:

1. Classical utility theory (timeless, frictionless, continuous choice sets)
2. Your spatial implementation (movement costs, discrete resources, time-dependent decisions)

**This document provides:** A structured framework to write down the economic models **as they
actually exist in your simulation**, enabling rigorous validation against theoretical predictions.

______________________________________________________________________

## Part 1: What You've Built (Current Implementation)

### 1.1 Core Economic Primitives

| Component             | Implementation                                                      | Economic Interpretation                               |
| --------------------- | ------------------------------------------------------------------- | ----------------------------------------------------- |
| **Utility Functions** | 3 types (Cobb-Douglas, Perfect Substitutes, Leontief)               | Agent preferences over consumption bundles            |
| **Budget Constraint** | **Implicit** - Time/distance costs                                  | Movement requires time; collecting requires proximity |
| **Prices**            | **Emergent** - No fixed prices                                      | Trade ratios determined by bilateral negotiation      |
| **Choice Set**        | **Discrete & Bounded** - Visible resources within perception radius | Spatial constraints + information limitations         |
| **Endowments**        | Dual inventory (carrying + home)                                    | Initial wealth + accumulated resources                |
| **Market Structure**  | Bilateral bargaining (1-for-1 trades)                               | Decentralized exchange, no auctioneer                 |

### 1.2 Agent Decision Process (As Implemented)

**Code location:** `src/econsim/simulation/agent/unified_decision.py:make_agent_decision()`

```
Step 1: OBSERVE ENVIRONMENT
  - Scan perception_radius (Manhattan distance ≤ 8)
  - Identify nearby resources and agents
  
Step 2: EVALUATE OPTIONS
  - Calculate marginal utility for each resource
  - Apply distance discount: MU_discounted = MU * exp(-0.15 * distance)
  - Identify potential trading partners
  
Step 3: CHOOSE ACTION (Deterministic utility maximization)
  - If inventory full & at home: deposit goods
  - If inventory full & away: return home
  - Else: choose highest discounted marginal utility target
  - Special case: seek trading partner if bilateral exchange enabled
  
Step 4: EXECUTE (Two-phase system)
  - Phase 1: Collect all decisions (seeing same world state)
  - Phase 2: Execute special actions (trades, resource collection)
```

**Key Economic Behaviors:**

- **Cobb-Douglas agents** (`alpha=0.5, beta=0.5`): Balance both goods proportionally
- **Perfect Substitutes agents** (`alpha=1.0, beta=1.0`): Focus on closer/cheaper good
- **Leontief agents** (`alpha=1.0, beta=1.0`): Collect fixed proportions, reject unbalanced trades

### 1.3 What Makes This Different from Textbook Models

| Textbook Economics                      | Your Simulation                                 | Implications                                     |
| --------------------------------------- | ----------------------------------------------- | ------------------------------------------------ |
| **Continuous choice sets** (any bundle) | **Discrete choices** (grid locations)           | Agents optimize over finite options              |
| **Instantaneous transactions**          | **Movement takes time**                         | Distance = implicit cost                         |
| **Perfect information**                 | **Bounded perception** (radius = 8)             | Agents may miss better opportunities             |
| **Walrasian auctioneer** sets prices    | **Bilateral negotiation**                       | No market-clearing mechanism                     |
| **No storage costs**                    | **Inventory capacity** (100k units)             | Currently unlimited, but constraint point exists |
| **Utility over consumption**            | **Utility over total wealth** (carrying + home) | Correct economic interpretation                  |

______________________________________________________________________

## Part 2: What's Missing (The Model-Reality Gap)

### 2.1 Absence of Explicit Economic Constraints

Your simulation has **implicit constraints** but lacks **explicit mathematical formulations**:

**Example: The "Budget Constraint" in Your Simulation**

In classical consumer theory:

```
p_x * x + p_y * y ≤ M  (where M = income, p_x, p_y = prices)
```

In your simulation:

```
time_spent + distance_traveled ≤ T  (where T = simulation steps)
opportunity_cost(good_A) = distance_to_A + distance_to_home + time_to_collect
```

**Problem:** This constraint is never explicitly written down, making validation difficult.

**Solution:** Define a **spatial budget constraint model** (see Section 3.2).

### 2.2 Absence of Price Theory

Your simulation has **no fixed prices**, but agents implicitly value goods through:

1. **Marginal utility** (from utility functions)
2. **Distance discounting** (`exp(-0.15 * distance)`)
3. **Trade ratios** (emergent from bilateral negotiation)

**Example:** If a Cobb-Douglas agent (`alpha=0.8`) trades 1 good1 for 1 good2, the **implicit
exchange rate** is 1:1, but the agent's **marginal rate of substitution** might be different.

**Problem:** Cannot validate market efficiency or equilibrium concepts without explicit price
theory.

**Solution:** Define **implicit price functions** based on spatial costs (see Section 3.3).

### 2.3 Trade Mechanism Differs from Standard Theory

**Your implementation:**
(`src/econsim/simulation/agent/unified_decision.py:find_beneficial_bilateral_trade`)

- Strictly 1-for-1 trades
- Both agents must gain utility (Pareto improvement)
- Minimum utility gain threshold (`MIN_TRADE_UTILITY_GAIN = 1e-5`)
- Lower ID executes trade (deterministic conflict resolution)

**Standard economic theory:** Agents trade until marginal rates of substitution are equalized:

```
MRS_A = MRS_B = price_ratio
```

**Your simulation:** Trades until no mutually beneficial 1-for-1 swaps remain (may not reach
theoretical equilibrium).

**Implication:** Your simulation will reach a **different equilibrium** than textbook Walrasian
equilibrium.

______________________________________________________________________

## Part 3: How to Bridge the Gap (Validation Framework)

### 3.1 Define Your Actual Economic Model

To validate your simulation, you need to **explicitly write down the economic model you've actually
implemented**, not the textbook version.

**Template for Each Utility Function:**

```markdown
## Economic Model: Cobb-Douglas Agent in Spatial Grid

### 3.1.1 Preferences
- Utility function: U(x, y) = (x + ε)^α * (y + ε)^β
- Parameters: α = 0.5, β = 0.5 (balanced preferences)
- ε = 0.01 (bootstrap for zero quantities)

### 3.1.2 Constraints
- **Spatial constraint**: Agent at (x_agent, y_agent), resources at {(x_i, y_i)}
- **Perception constraint**: Can only observe resources within distance ≤ 8
- **Time constraint**: Each action takes 1 simulation step
- **Inventory constraint**: Carrying capacity = 100,000 units (effectively unlimited)
- **Movement constraint**: Can move 1 Manhattan distance unit per step

### 3.1.3 Decision Problem (Foraging Mode)
At each step t, agent chooses resource i to maximize:
```

max_i { MU(good_i) * exp(-0.15 * distance_i) }

where: MU(good_i) = U(current_bundle + good_i) - U(current_bundle) distance_i = |x_i - x_agent| +
|y_i - y_agent| current_bundle = carrying_inventory + home_inventory

```

### 3.1.4 Predicted Behavior
- Agent should collect both goods in proportion to α:β
- As one good accumulates, marginal utility decreases → switch to other good
- Distance discount means agent prefers nearby resources (even if lower MU)
- Equilibrium: Balanced collection of both goods weighted by distance costs

### 3.1.5 Validation Tests
1. **Two-resource equidistant choice**: Place good1 and good2 at equal distances → agent should choose based on α, β and current inventory
2. **Distance sensitivity**: Place preferred good far away, less-preferred good close → agent may choose closer good
3. **Diminishing returns**: Place cluster of one good type → agent should eventually switch to collecting the other good
```

### 3.2 Formalize the Spatial Budget Constraint

**Your simulation's implicit budget constraint:**

```
Total_Cost(x, y) = Σ (distance_to_resource_i + collection_time_i + distance_to_home)
                   ≤ T_total (total simulation time)
```

**Opportunity cost interpretation:**

- Collecting 1 unit of good A has opportunity cost = time not spent collecting good B
- Distance to resource = "price" in time units
- Home as storage location = "investment" vs "liquidity" tradeoff

**Validation approach:**

1. Track total time spent per good type
2. Calculate "time price" = total_time / total_collected
3. Compare to theoretical optimal time allocation: `time_A/time_B = (α/β) * (MU_B/MU_A)`

### 3.3 Define Implicit Prices from Spatial Costs

**Proposed implicit price function:**

```
p_i(distance) = λ * distance * exp(-DISTANCE_DISCOUNT_FACTOR * distance)

where λ = opportunity cost of one step (inverse of agent's time value)
```

**For bilateral trade:**

```
Implicit exchange rate = MU_A / MU_B  (agent's marginal rate of substitution)

Trade occurs if:
  MU_A / MU_B (agent) < MU_B / MU_A (partner)
  → Both agents gain from 1-for-1 swap
```

**Validation:** After trading equilibrium, check if all agents have similar MRS (up to trade
granularity).

### 3.4 Validation Scenario Templates

Create controlled experiments that isolate specific theoretical predictions:

#### Scenario Template 1: Pure Preference Revelation

**Setup:**

- Single agent, Cobb-Douglas (α = 0.7, β = 0.3)
- Two resources at **equal distance** (e.g., both 5 steps away)
- No other agents (no competition)

**Theoretical Prediction:**

```
Agent should choose good1 (higher α) until:
  MU(good1) * 0.7 < MU(good2) * 0.3
  
For Cobb-Douglas: MU(x) ∝ α / (x + ε)
  
→ Agent should maintain ratio: (x + ε) / (y + ε) ≈ α / β = 7/3
```

**Validation Check:**

1. Run simulation for 100 steps
2. Record final bundle (x, y)
3. Calculate ratio: x / y
4. Compare to theoretical 7/3 ≈ 2.33
5. **Success:** ratio within 10% of prediction
6. **Failure:** Investigate if distance discounting, deposits, or other mechanisms cause deviation

#### Scenario Template 2: Distance vs Preference Tradeoff

**Setup:**

- Single agent, Cobb-Douglas (α = 0.8, β = 0.2) - strong preference for good1
- good1 resource at distance 10
- good2 resource at distance 2

**Theoretical Prediction:**

```
Agent chooses good1 if:
  MU(good1) * exp(-0.15 * 10) > MU(good2) * exp(-0.15 * 2)
  
At equilibrium (zero inventory):
  (0.8 / ε) * exp(-1.5) > (0.2 / ε) * exp(-0.3)
  0.8 * 0.223 > 0.2 * 0.741
  0.178 > 0.148  → TRUE, chooses good1 initially
  
As agent collects good1:
  MU(good1) decreases → eventually switches to good2
```

**Validation Check:**

1. Record agent's choice sequence
2. Calculate theoretical "switching point" (when MU ratios flip)
3. Compare observed vs predicted switching point
4. **Success:** Agent switches within ±5 steps of prediction

#### Scenario Template 3: Trade Equilibrium

**Setup:**

- Two agents at same location
- Agent A: Cobb-Douglas (α = 0.8), endowment (10, 2)
- Agent B: Cobb-Douglas (α = 0.2), endowment (2, 10)

**Theoretical Prediction:**

```
Agent A: MRS_A = (α / x) / (β / y) = (0.8 / 10) / (0.2 / 2) = 0.8
Agent B: MRS_B = (0.2 / 2) / (0.8 / 10) = 1.25

Since MRS_A < 1 < MRS_B:
  A values good2 more (willing to give >1 good1 for 1 good2)
  B values good1 more (willing to give >1 good2 for 1 good1)
  
→ Trade is mutually beneficial
  
With 1-for-1 constraint:
  A gives 1 good1, receives 1 good2 → new endowment (9, 3)
  B gives 1 good2, receives 1 good1 → new endowment (3, 9)
  
Continue until MRS equalized or 1-for-1 no longer beneficial
```

**Validation Check:**

1. Run simulation with trade enabled
2. Record all executed trades
3. Calculate MRS for both agents at each step
4. Check if trading stops when MRS are approximately equal (within 10%)
5. **Success:** Final MRS difference < theoretical 1-for-1 constraint bound
6. **Failure:** If trades stop prematurely, check MIN_TRADE_UTILITY_GAIN threshold

______________________________________________________________________

## Part 4: Specific Model Deviations to Document

### 4.1 Distance Discounting Economic Interpretation

**Your implementation:**
`apply_distance_discount(utility_gain, distance) = utility_gain * exp(-0.15 * distance)`

**What this means economically:**

- Exponential discounting with rate = 0.15 per Manhattan distance unit
- At distance 5: value reduced to 47% of original
- At distance 10: value reduced to 22% of original

**Theoretical justification:**

- Models **hyperbolic discounting** of future rewards (further = later)
- Could also represent **uncertainty** about resource availability
- Or **opportunity cost** of time spent traveling

**Questions to answer:**

1. Why exponential vs linear discounting?
2. Why rate = 0.15? (empirically chosen? theoretically derived?)
3. How does this compare to real-world spatial economic models?

**Validation approach:**

- Test with different discount rates (0.05, 0.15, 0.30)
- Observe agent behavior changes
- Document which rate produces most "realistic" spatial patterns

### 4.2 Epsilon Bootstrap (`EPSILON_UTILITY = 0.01`)

**Purpose:** Prevents log(0) and division by zero in utility calculations

**Economic interpretation:**

- Agents derive small utility from zero consumption (survival minimum?)
- Affects marginal utility at low quantities

**Example impact on Cobb-Douglas:**

```
U(0, 0) = (0.01)^0.5 * (0.01)^0.5 = 0.01  (not zero!)
U(1, 0) = (1.01)^0.5 * (0.01)^0.5 = 0.1005  (10x higher)
U(0, 1) = (0.01)^0.5 * (1.01)^0.5 = 0.1005  (symmetric)
```

**Problem:** Epsilon affects preference revelation at low quantities.

**Validation needed:**

1. Does epsilon = 0.01 distort behavior significantly?
2. Test with epsilon = 0.001, 0.1 to assess sensitivity
3. Document acceptable epsilon range for educational accuracy

### 4.3 Carrying Capacity (100,000 units)

**Current status:** "Effectively unlimited"

**Economic interpretation:**

- Agents face **no storage constraint** in practice
- Home inventory = unlimited storage
- Carrying inventory = portable wealth

**Future consideration:**

- If capacity becomes binding (e.g., reduced to 50 units):
  - Creates **inventory management tradeoff**
  - Agents must choose: collect more or trade current inventory
  - Changes optimal foraging strategy

**Validation scenario (if capacity reduced):**

- Agent with capacity = 10 units
- Cluster of resources (20+ units available)
- Predicted: Agent collects to capacity, returns home, repeat
- Check if this creates **"hub-and-spoke"** spatial patterns

### 4.4 Perception Radius (Manhattan Distance ≤ 8)

**Current:** Agents can only see resources within 8 Manhattan distance units

**Economic interpretation:**

- **Bounded rationality** - incomplete information
- **Search costs** - agents don't know all opportunities

**Implications:**

1. Agents may miss better resources outside perception radius
2. Creates **spatial heterogeneity** in agent knowledge
3. Prevents global optimization (only local optimization)

**Validation:**

- Compare agent behavior with perception_radius = 8 vs 100 (near-perfect info)
- Measure efficiency loss from bounded perception
- Document how this affects equilibrium outcomes

### 4.5 Trade Minimum Utility Gain (`MIN_TRADE_UTILITY_GAIN = 1e-5`)

**Purpose:** Prevents numerical instability from tiny utility improvements

**Economic interpretation:**

- **Transaction costs** - trades must provide sufficient benefit
- Below threshold → not worth negotiating

**Problem:** This creates a **"no-trade zone"** even when theoretical MRS differ slightly.

**Example:**

```
Agent A: MU(good1) = 1.00001, MU(good2) = 1.00000
Agent B: MU(good1) = 1.00000, MU(good2) = 1.00001

Theoretical: Trade is beneficial (MRS differ)
Your simulation: No trade (gains below threshold)
```

**Validation:**

- Test with threshold = 0, 1e-5, 1e-3
- Observe if trades reach "closer to equilibrium" with lower threshold
- Document tradeoff: numerical stability vs equilibrium accuracy

______________________________________________________________________

## Part 5: Recommended Documentation Structure

To support your validation efforts, create the following documents in `tmp_plans/CRITICAL/`:

### 5.1 `ECONOMIC_MODEL_COBB_DOUGLAS.md`

```markdown
# Formal Model: Cobb-Douglas Agent

## 1. Utility Function Specification
[Mathematical definition with parameters]

## 2. Decision Problem
[Optimization problem with constraints]

## 3. Theoretical Predictions
[Analytical solutions for simple scenarios]

## 4. Implementation Notes
[Code pointers, parameter values, edge cases]

## 5. Validation Scenarios
[Specific tests with predicted outcomes]

## 6. Known Deviations
[Where simulation differs from theory and why]
```

### 5.2 `ECONOMIC_MODEL_PERFECT_SUBSTITUTES.md`

[Same structure as above]

### 5.3 `ECONOMIC_MODEL_PERFECT_COMPLEMENTS.md`

[Same structure as above]

### 5.4 `ECONOMIC_MODEL_SPATIAL_CONSTRAINTS.md`

```markdown
# Formal Model: Spatial Budget Constraint

## 1. Distance Cost Function
[Mathematical formulation of distance discounting]

## 2. Time Budget Constraint
[Total time allocation across activities]

## 3. Opportunity Cost Calculation
[How to compute implicit prices]

## 4. Validation Tests
[Scenarios to test spatial cost model]
```

### 5.5 `ECONOMIC_MODEL_BILATERAL_TRADE.md`

```markdown
# Formal Model: Bilateral Exchange Mechanism

## 1. Trade Matching Algorithm
[How agents find partners]

## 2. Trade Feasibility Conditions
[When 1-for-1 trades are mutually beneficial]

## 3. Equilibrium Concept
[What "equilibrium" means in your simulation vs Walrasian]

## 4. Validation Tests
[Trade scenarios with predicted outcomes]
```

### 5.6 `VALIDATION_TEST_SUITE.md`

```markdown
# Economic Model Validation Test Suite

## Purpose
[Link to educational goals from initial_planning.md]

## Test Categories
1. Preference Revelation Tests
2. Distance Sensitivity Tests
3. Trade Equilibrium Tests
4. Multi-agent Competition Tests

## Each Test Entry:
- **Scenario Description**
- **Theoretical Prediction** (with math)
- **Implementation** (code/config)
- **Success Criteria** (quantitative)
- **Current Status** (pass/fail/not run)
```

______________________________________________________________________

## Part 6: Validation Workflow (Practical Steps)

### Step 1: Start Simple (Single Agent, No Trade)

**Week 1 Goal:** Validate pure foraging behavior for each utility function

1. Create `tests/validation/test_cobb_douglas_foraging.py`
2. Implement Scenario Template 1 (equal distance choice)
3. Run simulation, record agent path and inventory
4. Calculate theoretical prediction (show math in comments)
5. Assert observed behavior within 10% of prediction
6. Document any deviations in `ECONOMIC_MODEL_COBB_DOUGLAS.md`

**Success criteria:**

- All 3 utility functions pass distance-preference tradeoff tests
- Can predict agent behavior from utility function alone with >90% accuracy

### Step 2: Add Distance Complexity

**Week 2 Goal:** Validate spatial cost model

1. Create scenarios with varying distance configurations
2. Test boundary cases:
   - Very close resources (distance = 1)
   - Very far resources (distance = 20+)
   - Multiple resources at different distances
3. Measure actual vs predicted "switching points"
4. Calibrate `DISTANCE_DISCOUNT_FACTOR` if needed

**Success criteria:**

- Can predict when agent switches between resources
- Distance discount model validated across 10+ scenarios

### Step 3: Add Trading (Two Agents)

**Week 3 Goal:** Validate bilateral trade mechanism

1. Create pairwise trade scenarios (Scenario Template 3)
2. Test with complementary preferences:
   - Both Cobb-Douglas with different α
   - Cobb-Douglas vs Perfect Substitutes
   - All combinations of 3 utility functions
3. Calculate theoretical final allocations
4. Measure convergence to predicted equilibrium

**Success criteria:**

- Trade equilibrium reached within 20 steps
- Final allocation within 1 unit of theoretical prediction
- MRS equalization up to 1-for-1 constraint

### Step 4: Multi-Agent Competition

**Week 4 Goal:** Validate emergent behaviors with >2 agents

1. Create scenarios with 3-10 agents
2. Test resource competition:
   - Multiple agents targeting same resource
   - Spatial clustering vs dispersion
   - Emergence of "territories"
3. Document emergent patterns

**Success criteria:**

- No deadlocks or indefinite idling
- Resource allocation roughly proportional to preferences
- System reaches stable state (or predictable cycles)

### Step 5: Educational Validation

**Week 5 Goal:** Verify visual behaviors match utility functions (Success Metric R-07)

1. Run `make visualtest` for each utility function
2. Record spatial patterns (screenshots + metrics)
3. Blind test: Can you identify utility function from behavior alone?
4. Statistical test: Measure spatial autocorrelation, movement entropy, inventory distributions
5. Verify patterns are **measurably distinct** (R-07 requirement)

**Success criteria:**

- 90%+ accuracy identifying utility function from behavior (R-07)
- Statistical significance test: p < 0.05 for behavioral differences
- Students can predict behavior from utility function description

______________________________________________________________________

## Part 7: Connection to Your Educational Mission

### From `initial_planning.md`:

**Success Metric R-07:**

> "Solo developer can correctly identify preference type from agent spatial behavior in blind tests
> with 90%+ accuracy, and visual behaviors are measurably distinct using spatial pattern metrics"

**To achieve this, you need:**

1. **Explicit models** (this document provides framework)
2. **Quantitative predictions** (validation scenarios above)
3. **Statistical metrics** for "measurably distinct" (next step)

### Proposed Spatial Pattern Metrics:

| Metric                    | Measures                            | Cobb-Douglas | Perfect Substitutes     | Perfect Complements       |
| ------------------------- | ----------------------------------- | ------------ | ----------------------- | ------------------------- |
| **Resource Mix Ratio**    | `collected_good1 / collected_good2` | ≈ α / β      | Extreme (>>1 or \<<1)   | Fixed by α, β             |
| **Movement Entropy**      | Randomness of direction changes     | Medium       | Low (beeline to target) | Medium-High (alternating) |
| **Home Return Frequency** | Deposits per 100 steps              | Low          | Very Low                | Medium                    |
| **Trade Acceptance Rate** | Trades executed / proposed          | High         | Low                     | Very High (if imbalanced) |
| **Spatial Clustering**    | Time spent in same grid area        | Low          | High                    | Low                       |

**Validation test:**

```python
def test_measurably_distinct_behaviors():
    """R-07: Visual behaviors are measurably distinct."""
    # Run 100 steps for each utility function
    results_cd = run_scenario(utility="cobb_douglas")
    results_ps = run_scenario(utility="perfect_substitutes")
    results_pc = run_scenario(utility="perfect_complements")
    
    # Calculate metrics
    metrics_cd = calculate_spatial_metrics(results_cd)
    metrics_ps = calculate_spatial_metrics(results_ps)
    metrics_pc = calculate_spatial_metrics(results_pc)
    
    # Statistical test: Are distributions significantly different?
    p_value = kruskal_wallis_test([metrics_cd, metrics_ps, metrics_pc])
    
    assert p_value < 0.05, "Behaviors not measurably distinct (R-07 failed)"
```

______________________________________________________________________

## Part 8: Known Issues & Future Model Extensions

### 8.1 Current Model Limitations

1. **No explicit price mechanism** → Cannot teach price theory directly
2. **1-for-1 trade constraint** → Restricts market efficiency
3. **No production** → Pure exchange economy
4. **No time preferences** → All decisions are myopic (no planning ahead)
5. **Deterministic decisions** → No bounded rationality, exploration, or mistakes

### 8.2 Educational Gaps to Address

From `initial_planning.md` **Risk R-03**: "Economic algorithms contain theoretical errors"

**Mitigation:** "Theoretical validation test suite, economics expert code review, mathematical
cross-reference system"

**This document provides:** Framework for "mathematical cross-reference system"

**Still needed:**

- Expert review of economic model specifications (economics PhD?)
- Literature citations for spatial economic models (nearest neighbor: economic geography, spatial
  search theory)
- Comparison to published simulation models (NetLogo economics models, MASON frameworks)

### 8.3 Future Model Extensions (Post-MVP)

**From initial_planning.md Phase 3-4:**

1. **Market equilibrium** (Week 17-22)

   - Requires: Explicit prices, market-clearing mechanism
   - Model: Walrasian tatonnement or double auction

2. **Game theory** (Week 23+)

   - Requires: Strategic interaction, payoff matrices
   - Model: Nash equilibrium in spatial games

3. **Information economics** (Week 23+)

   - Requires: Asymmetric information, signaling
   - Model: Adverse selection, moral hazard in trades

**For each extension:**

- Write explicit model **before implementation**
- Derive theoretical predictions
- Create validation scenarios
- Measure simulation vs theory gap

______________________________________________________________________

## Part 9: Immediate Action Items

### This Week (High Priority):

1. **Choose one utility function** (recommend Cobb-Douglas - most intuitive)
2. **Write formal model document** using Section 5.1 template
3. **Implement Scenario Template 1** (equal distance choice)
4. **Run validation test** and document results
5. **Identify one deviation** between theory and simulation

**Estimated time:** 4-6 hours (iterative, not all at once)

### Next Week (Medium Priority):

1. Complete formal models for other two utility functions
2. Implement Scenario Templates 2 & 3
3. Create `VALIDATION_TEST_SUITE.md` tracking document
4. Run full validation suite (10+ scenarios)

**Estimated time:** 8-10 hours

### Future (Low Priority, but critical for education):

1. Define spatial pattern metrics (Section 7)
2. Implement statistical tests for R-07 (measurably distinct)
3. Conduct blind identification tests (solo developer → students)
4. Revise economic models based on validation findings

**Estimated time:** 12-15 hours

______________________________________________________________________

## Part 10: Example Validation Document (Template)

Here's a complete example to get you started:

### `ECONOMIC_MODEL_COBB_DOUGLAS_VALIDATION.md`

```markdown
# Economic Model: Cobb-Douglas Agent (Validation Results)

## 1. Theoretical Model

### Preferences
- Utility function: U(x, y) = (x + 0.01)^0.5 * (y + 0.01)^0.5
- Interpretation: Agent values both goods equally, diminishing marginal utility

### Marginal Utilities
- MU_x = ∂U/∂x = 0.5 * (x + 0.01)^(-0.5) * (y + 0.01)^0.5
- MU_y = ∂U/∂y = 0.5 * (x + 0.01)^0.5 * (y + 0.01)^(-0.5)

### Marginal Rate of Substitution
- MRS = MU_x / MU_y = (y + 0.01) / (x + 0.01)
- At (x, y) = (0, 0): MRS = 1.0 (equal preference)
- At (x, y) = (10, 5): MRS = 5.01 / 10.01 ≈ 0.5 (prefers y now)

## 2. Validation Scenario 1: Equal Distance Choice

### Setup
- Grid: 10x10
- Agent: (5, 5), Cobb-Douglas (α=0.5, β=0.5)
- Resource A (good1): (5, 7) - distance 2
- Resource B (good2): (5, 3) - distance 2
- Initial inventory: (0, 0)

### Theoretical Prediction
```

MU_x(0, 0) = 0.5 * (0.01)^(-0.5) * (0.01)^0.5 = 0.5 * 10 * 0.1 = 0.5 MU_y(0, 0) = 0.5 * (0.01)^0.5
\* (0.01)^(-0.5) = 0.5 * 0.1 * 10 = 0.5

Distance discount: exp(-0.15 * 2) = exp(-0.3) ≈ 0.741

Discounted MU_x = 0.5 * 0.741 = 0.370 Discounted MU_y = 0.5 * 0.741 = 0.370

Prediction: Agent is indifferent - should choose deterministically (e.g., lowest resource ID)

````

### Simulation Results
```python
# Run via: pytest tests/validation/test_cobb_douglas_equal_distance.py -v

Observed behavior:
  Step 1: Agent moves to (5, 6) (toward Resource A)
  Step 2: Agent moves to (5, 7), collects good1
  Step 3: Agent moves to (5, 6)
  Step 4: Agent moves to (5, 5)
  Step 5: Agent moves to (5, 4) (toward Resource B)
  Step 6: Agent moves to (5, 3), collects good2
  
Final inventory: (1, 1)
Ratio: 1.0 (matches α/β = 1.0)
````

### Analysis

✅ **PASS** - Agent collected both goods equally (theory matched) ✅ **PASS** - Deterministic choice
(picked resource A first due to ID tiebreak)

### Notes

- Epsilon (0.01) did not distort behavior at zero inventory
- Distance discount worked as expected (equal discounting → equal choice)

## 3. Validation Scenario 2: Distance-Preference Tradeoff

### Setup

- Grid: 10x10
- Agent: (5, 5), Cobb-Douglas (α=0.5, β=0.5)
- Resource A (good1): (5, 10) - distance 5
- Resource B (good2): (5, 3) - distance 2
- Initial inventory: (0, 0)

### Theoretical Prediction

```
At (0, 0):
  MU_x = 0.5, MU_y = 0.5

Distance discount:
  Discounted MU_x = 0.5 * exp(-0.15 * 5) = 0.5 * 0.472 = 0.236
  Discounted MU_y = 0.5 * exp(-0.15 * 2) = 0.5 * 0.741 = 0.370

Prediction: Agent chooses Resource B (closer, same MU)

After collecting good2 (inventory = 0, 1):
  MU_x(0, 1) = 0.5 * (0.01)^(-0.5) * (1.01)^0.5 ≈ 5.03
  MU_y(0, 1) = 0.5 * (0.01)^0.5 * (1.01)^(-0.5) ≈ 0.050
  
  Discounted MU_x = 5.03 * 0.472 = 2.374
  Discounted MU_y = 0.050 * 0.741 = 0.037
  
Prediction: Now agent should switch to Resource A (MU_x much higher)
```

### Simulation Results

```python
Observed behavior:
  Steps 1-3: Agent moves to Resource B, collects good2
  Steps 4-8: Agent moves to Resource A, collects good1
  Steps 9-11: Agent moves to Resource B, collects good2
  Steps 12-16: Agent moves to Resource A, collects good1
  
Final inventory (after 100 steps): (9, 11)
Ratio: 9/11 = 0.82 (close to predicted 1.0, with noise from distance costs)
```

### Analysis

✅ **PASS** - Agent alternates collection based on marginal utility ✅ **PASS** - Distance discount
correctly influences initial choice ⚠️ **PARTIAL** - Final ratio slightly skewed toward good2
(closer resource)

### Notes

- Distance asymmetry creates slight preference for closer good
- This is **economically correct** - distance = implicit price difference
- Theoretical model should account for this in equilibrium prediction

## 4. Validation Scenario 3: Switching Point

### Setup

- Agent: Cobb-Douglas (α=0.5, β=0.5)
- Resources A (good1) clustered at distance 2-3 (10 units total)
- Resource B (good2) single unit at distance 2

### Theoretical Prediction

```
Agent should collect good1 until:
  MU_x / MU_y ≈ 1.0 (equal preferences)
  
With distance discount canceling out (both ≈ distance 2):
  (y + 0.01) / (x + 0.01) ≈ 1.0
  → x ≈ y (equal quantities)
  
Predicted switch point: After collecting 1 good1, should collect 1 good2
```

### Simulation Results

```python
Observed behavior:
  Collected 2 good1 before switching to good2
  
Analysis: Slight delay due to resource clustering
  - After 1st good1, next good1 very close (distance 1)
  - Discounted MU favored immediate collection over distant good2
```

### Analysis

✅ **PASS** - Switching behavior observed ⚠️ **DEVIATION** - Switched later than theoretical
prediction due to spatial clustering

### Notes

- **Important finding**: Theoretical model assumes all resources equidistant
- Reality: Resource distribution affects collection sequence
- **Model refinement needed**: Account for "next-nearest resource" in predictions

## 5. Summary & Recommendations

### What Works

- Core utility maximization logic is sound
- Distance discounting behaves as expected
- Agent demonstrates correct preference patterns

### Deviations from Theory

1. **Spatial clustering effects** - Agent behavior influenced by resource distribution
2. **Sequential collection** - Theoretical model assumes simultaneous choice, simulation is
   sequential

### Recommendations

1. **Update theoretical model** to include "nearest available resource" constraint
2. **Add spatial pattern metrics** to validation suite
3. **Test with 100+ random resource configurations** for robustness

### Next Steps

1. Validate Perfect Substitutes utility function
2. Validate Perfect Complements utility function
3. Create cross-utility-function comparison tests

```

---

## Conclusion

You have a **solid foundation** with three economically sound utility functions, but you're operating in a **spatial, discrete-time economic model** that differs from textbook microeconomics.

**The path forward:**

1. **Document what you've actually built** (not what textbooks describe)
2. **Write explicit models** for each component (use templates above)
3. **Create validation scenarios** with quantitative predictions
4. **Measure simulation vs theory gaps** and document deviations
5. **Refine models** based on findings (iterate!)

**This is your foundation for achieving Success Metric R-07** and building an educationally robust platform.

**Time investment:** ~30-40 hours over 4-6 weeks to fully validate all models.

**Payoff:** Rigorous economic foundation for teaching, publishable educational tool, confidence in simulation accuracy.

---

## References & Further Reading

### Economic Theory
- **Mas-Colell, Whinston, Green (1995)** - *Microeconomic Theory* - Chapters 1-3 (Consumer Theory)
- **Varian (2014)** - *Intermediate Microeconomics* - Chapters 4-8 (Utility, Choice, Demand)

### Spatial Economics
- **Fujita & Thisse (2002)** - *Economics of Agglomeration* - Spatial cost models
- **Krugman (1991)** - "Increasing Returns and Economic Geography" - Distance-dependent trade

### Agent-Based Modeling
- **Tesfatsion & Judd (2006)** - *Handbook of Computational Economics, Vol. 2*
- **Epstein & Axtell (1996)** - *Growing Artificial Societies* - Sugarscape model (similar to your simulation)

### Educational Simulations
- **Holt (2007)** - *Markets, Games, and Strategic Behavior* - Experimental economics pedagogy
- **NetLogo Economics Models** - https://ccl.northwestern.edu/netlogo/models/community/

---

**Document Status:** Draft v1.0  
**Next Review:** After first validation scenario implemented  
**Owner:** cmfunderburk (solo developer)  
**AI Assistant:** Claude 3.5 Sonnet (October 2025)
```
