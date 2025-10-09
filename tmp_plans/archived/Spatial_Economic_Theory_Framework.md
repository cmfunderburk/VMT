# Spatial Economic Theory Framework for VMT EconSim

## Executive Summary

This document establishes the **theoretical foundation** for how a spatial, discrete-time
microeconomic simulation *should* behave. Unlike traditional microeconomics (which abstracts away
space and time), we need explicit models that incorporate:

1. **Spatial constraints** - Distance as a fundamental economic cost
2. **Temporal dynamics** - Sequential decision-making over discrete time steps
3. **Information limits** - Local perception rather than perfect information
4. **Discrete choices** - Grid-based movement and integer inventory units

This framework serves as the **normative specification** against which implementation is validated,
complementing the descriptive validation in `Opus_econ_model_review.md`.

______________________________________________________________________

## Part I: Theoretical Foundations

### 1.1 The Spatial Economic Decision Problem

#### Classical Problem (Textbook)

```
max U(x, y)
s.t. p_x * x + p_y * y ≤ M
     x, y ≥ 0
```

#### Our Spatial Problem (What We Need)

```
At each time step t, agent i at location (x_i, y_i) chooses action a_t from:
  A_t = {move_north, move_south, move_east, move_west, 
         collect_resource, deposit_inventory, withdraw_inventory,
         propose_trade(j), idle}

To maximize expected discounted utility:
  V_t = E[ Σ_{τ=t}^∞ δ^(τ-t) * U(bundle_{τ}) ]

Subject to:
  - Perception constraint: Can only observe entities within radius R
  - Movement constraint: 1 Manhattan step per time period
  - Spatial transaction costs: TC(distance) = k * distance
  - Inventory constraints: carrying ≤ C_max, home storage unlimited
  - Information constraint: Local knowledge only (no global state)
```

**Key Insight**: This is a **spatial dynamic programming problem** where agents maximize lifetime
utility through a sequence of spatially-constrained choices.

### 1.2 Distance as Economic Cost

#### Why Distance Matters Economically

In traditional economics, transaction costs are explicit (e.g., shipping fees). In our spatial
model, distance represents:

1. **Opportunity Cost of Time**: Moving to distant resource means foregone collection from nearby
   resources
2. **Delayed Gratification**: Resources collected later are worth less (implicit discounting)
3. **Information Cost**: Distant resources may not remain available
4. **Risk Premium**: Longer paths increase uncertainty

#### Formal Distance Discount Function

**Current Implementation**: `value = MU * exp(-k * distance)`

**Economic Interpretation**: This assumes that the disutility of distance grows exponentially, which
implies:

- Each additional unit of distance reduces value by a constant percentage
- Agents have **constant relative risk aversion** over distance
- Equivalent to time-discounting with δ = exp(-k)

**Alternative Models to Consider**:

1. **Linear Transaction Cost**: `value = MU - k * distance`

   - Simple subtraction of travel cost
   - Can result in negative values (infeasible choices)
   - Good for: Close-range decisions with small costs

2. **Hyperbolic Discounting**: `value = MU / (1 + k * distance)`

   - Models present bias (near > far disproportionately)
   - Common in behavioral economics
   - Good for: Modeling impatient agents

3. **Power Function**: `value = MU * distance^(-k)`

   - Flexible curvature parameter
   - Models range-dependent sensitivity
   - Good for: Variable transportation technologies

**Recommendation**: Document why exponential was chosen and under what conditions it represents
"rational" spatial behavior.

### 1.3 The Spatial Budget Constraint

#### Problem: No Explicit Prices

In classical consumer theory, the budget constraint is:

```
p_x * x + p_y * y ≤ M
```

In our simulation:

- No money (M)
- No explicit prices (p_x, p_y)
- Resources freely available at locations

#### Solution: Implicit Price via Distance

Define the **implicit price** of a good as the expected cost of acquiring one unit:

```
π_i(r) = TC(d_i,r) + OC(t_collect)

where:
  TC(d) = transportation cost = k * distance
  OC(t) = opportunity cost = value of next-best action
  d_i,r = distance from agent i to resource r
```

This gives us a **spatial budget constraint**:

```
Σ_r π_i(r) * q_r ≤ T_max * v_max

where:
  T_max = total time budget (simulation length)
  v_max = maximum value producible per time step
  q_r = quantity of resource r collected
```

**Key Prediction**: Agents with limited time should behave as if facing budget constraint with
prices proportional to distance.

### 1.4 Utility Maximization in Discrete Space

#### Challenges with Discrete Grids

1. **No Continuous Derivatives**: Can't use calculus to find MRS
2. **Integer Constraints**: Can't collect fractional units
3. **Path Dependence**: Order of collection matters
4. **Local Optima**: Grid structure creates multiple equilibria

#### Discrete Optimization Framework

**Greedy Myopic Strategy** (Current Implementation):

```
At each step, choose action a* that maximizes:
  a* = argmax_a { EU(a) }
  
where EU(a) = expected utility gain from action a
```

**Properties**:

- Computationally tractable (O(n) per agent)
- Guarantees local improvement
- Does NOT guarantee global optimum
- Matches satisficing behavior (Herbert Simon)

**Dynamic Programming Strategy** (Theoretical Ideal):

```
V_t(s_t) = max_a { U(s_t, a) + δ * V_{t+1}(s_{t+1}) }

where:
  s_t = state at time t (location, inventory, world state)
  V_t = value function at time t
```

**Properties**:

- Guarantees global optimum
- Computationally intractable (curse of dimensionality)
- Requires perfect foresight (unrealistic)

**Recommendation**: Explicitly document that agents use bounded rationality (greedy myopic), not
perfect foresight. This is economically defensible as "satisficing" behavior.

______________________________________________________________________

## Part II: Utility Function Specifications

### 2.1 Cobb-Douglas in Spatial Context

#### Canonical Form

```
U(x, y) = (x + ε)^α * (y + ε)^β
where α + β = 1, ε = 0.01 (bootstrap)
```

#### Marginal Utility

```
MU_x = α * (x + ε)^(α-1) * (y + ε)^β
MU_y = β * (x + ε)^α * (y + ε)^(β-1)
```

#### Marginal Rate of Substitution

```
MRS = MU_x / MU_y = (α/β) * [(y + ε)/(x + ε)]
```

#### Spatial Predictions

**Scenario: Two resources at different distances**

Given:

- Resource A at distance d_A
- Resource B at distance d_B
- Current inventory: (x, y)

**Predicted Choice**:

```
Collect A if: MU_x * exp(-k*d_A) > MU_y * exp(-k*d_B)

Rearranging: (α/β) * [(y+ε)/(x+ε)] > exp(k*(d_A - d_B))
```

This gives the **indifference distance differential**:

```
Δd* = (1/k) * ln[(α/β) * (y+ε)/(x+ε)]
```

**Economic Interpretation**: Agent will travel extra distance Δd\* to get preferred good before
switching to other good.

#### Equilibrium Properties

**No Trade**: Agents collect resources in ratio α:β regardless of distances (given infinite time)

**With Trade**: Agents specialize based on comparative advantage in distance, then trade to achieve
α:β consumption ratio.

**Testable Prediction**: Final inventory ratios should converge to α:β ± ε_margin, where ε_margin
accounts for discrete choices and finite time.

### 2.2 Perfect Substitutes in Spatial Context

#### Canonical Form

```
U(x, y) = α*x + β*y
```

#### Marginal Utility

```
MU_x = α (constant)
MU_y = β (constant)
```

#### Marginal Rate of Substitution

```
MRS = α/β (constant)
```

#### Spatial Predictions

**Key Property**: Agents care only about weighted sum α*x + β*y, not individual quantities.

**Predicted Behavior**:

```
If α > β: Agent prefers good x
If β > α: Agent prefers good y

Spatial decision:
Collect A if: α * exp(-k*d_A) > β * exp(-k*d_B)

Critical distance differential:
Δd* = (1/k) * ln(α/β)
```

**Economic Interpretation**: Agent will travel up to Δd\* extra to get preferred good. Beyond that,
switches to other good.

**Extreme Case (α >> β)**: Agent effectively ignores good y unless it's dramatically closer.

#### Equilibrium Properties

**No Trade**: Agent collects only the "cheapest" good (accounting for distance)

**With Trade**: No trade occurs unless agents have different preference parameters (α_i/β_i ≠
α_j/β_j) or face different spatial constraints.

**Testable Prediction**: Inventory should be heavily skewed toward one good, with ratio determined
by relative distances and preferences.

### 2.3 Perfect Complements (Leontief) in Spatial Context

#### Canonical Form

```
U(x, y) = min(α*x, β*y)
```

#### Marginal Utility

```
MU_x = α if α*x < β*y, else 0
MU_y = β if β*y < α*x, else 0
```

#### Marginal Rate of Substitution

```
MRS = undefined (kinked indifference curves)
```

#### Spatial Predictions

**Key Property**: Utility increases only along the ray x/y = β/α

**Predicted Behavior**:

```
Current inventory: (x, y)
Current ratio: r = (α*x) / (β*y)

If r < 1: Need more x → prioritize good A
If r > 1: Need more y → prioritize good B
If r ≈ 1: Indifferent (collect either to maintain balance)

Spatial decision incorporating distance:
Collect A if: [need_A] * exp(-k*d_A) > [need_B] * exp(-k*d_B)

where:
  need_A = max(0, β*y/α - x)  # units needed to reach balance
  need_B = max(0, α*x/β - y)
```

#### Equilibrium Properties

**No Trade**: Final inventory should satisfy α*x ≈ β*y (balanced proportions)

**With Trade**: Agents trade to achieve exact balance β\*y/α

**Testable Prediction**:

- Inventory ratio should converge to β/α with small oscillations
- Agents should alternate collection between goods
- Excess of one good should approach zero

______________________________________________________________________

## Part III: Multi-Agent Spatial Economics

### 3.1 Bilateral Trade in Spatial Context

#### Classical Trade Theory

**Edgeworth Box**: Two agents, fixed endowments, trade to Pareto frontier where MRS_A = MRS_B.

#### Spatial Modifications

**Key Differences**:

1. **Endogenous Endowments**: Agents collect resources, not fixed endowments
2. **Distance Matters**: Trading partners must be nearby (perception radius)
3. **Sequential Trades**: Not simultaneous market clearing
4. **Incomplete Information**: Agents don't know all potential partners

#### Formal Trade Model

**Trade Feasibility Constraint**:

```
Can trade with agent j if:
  distance(i, j) ≤ R_perception
  carrying_i(good_a) ≥ 1
  carrying_j(good_b) ≥ 1
```

**Trade Acceptance Condition**:

```
Agent i accepts trade of good_a for good_b if:
  U_i(bundle_i - 1*good_a + 1*good_b) > U_i(bundle_i) + ε_min

where ε_min = minimum utility gain threshold
```

**Trade Equilibrium**:

```
Trade occurs until one of:
  1. No mutually beneficial trades exist
  2. Agents are spatially separated
  3. Carrying inventories depleted
```

#### Spatial Trade Dynamics

**Phase 1: Collection**

- Agents accumulate resources independently
- Spatial patterns emerge based on utility functions

**Phase 2: Trade Negotiation**

- Agents who meet evaluate bilateral exchanges
- Multiple rounds of sequential trades

**Phase 3: Post-Trade Collection**

- Agents continue collecting with new preferences
- May seek specific goods for future trades

#### Predicted Trade Patterns

**Cobb-Douglas × Cobb-Douglas**:

```
If α_i ≠ α_j:
  Agent with higher α_x trades y for x
  Agent with higher α_y trades x for y
  Convergence: Each agent reaches their preferred ratio
```

**Perfect Substitutes × Perfect Substitutes**:

```
If α_i/β_i ≠ α_j/β_j:
  Agent with higher α/β wants more x, trades y
  Limited trade (each already specialized)
```

**Perfect Complements × Perfect Complements**:

```
If α_i/β_i ≠ α_j/β_j:
  High potential for trade (complementary imbalances)
  Both agents maintain fixed ratios but different levels
```

**Mixed Types**:

```
Cobb-Douglas × Perfect Substitutes:
  CD agent trades to balance, PS agent trades for specialization
  
Perfect Complements × Perfect Substitutes:
  PC agent trades to maintain ratio, PS agent takes advantage
  
Cobb-Douglas × Perfect Complements:
  Both seek balance, but different ratios
```

### 3.2 Spatial Competition and Congestion

#### Resource Competition Model

**Problem**: Multiple agents targeting same resource

**Current Resolution**: First-come, first-served (FCFS)

**Economic Implications**:

1. **No price mechanism**: Resources don't become "expensive" when scarce
2. **Positional advantage**: Proximity becomes critical asset
3. **Strategic timing**: Agents may rush to claim resources

**Alternative Models**:

1. **Auction Mechanism**: Agents "bid" with time/distance

   ```
   Winner = agent with highest MU * exp(-k * distance)
   ```

2. **Congestion Pricing**: Resource value decreases with nearby agents

   ```
   value = MU * exp(-k * distance) / (1 + n_nearby)
   ```

3. **Territorial Claims**: Agents establish "home ranges"

   ```
   penalty = p_trespass if collecting in other's territory
   ```

**Recommendation**: Document FCFS assumption and its economic interpretation (resources are
non-rivalrous until collected).

### 3.3 Spatial Externalities

#### Positive Externalities

**Information Spillovers**:

- Agents observing others' movements learn resource locations
- Clustering around productive areas

**Trading Network Effects**:

- More agents nearby → more potential trades
- Benefits to population density

#### Negative Externalities

**Resource Depletion**:

- Agents collecting same resource reduce availability
- Tragedy of the commons

**Congestion**:

- Movement conflicts (if implemented)
- Reduced efficiency in crowded areas

#### Modeling Externalities

**Social Welfare Function**:

```
W = Σ_i U_i(bundle_i) - Σ_ij C_ij(distance_ij)

where:
  C_ij = interaction costs between agents i and j
```

**Optimal Spatial Configuration**:

- Balances individual utility maximization with social costs
- May differ from Nash equilibrium

______________________________________________________________________

## Part IV: Temporal Dynamics and Convergence

### 4.1 Time Horizon and Discounting

#### Finite vs Infinite Horizon

**Finite Horizon (T steps)**:

- Agents optimize over known time limit
- End-game effects (may hoard or dump inventory)
- Backward induction possible

**Infinite Horizon** (Current):

- Agents optimize myopically each step
- Steady-state behavior emerges
- More realistic for continuous systems

#### Discount Factor

**Implicit Discounting through Distance**:

```
δ_spatial = exp(-k * d)
```

**Temporal Discounting** (if implemented):

```
δ_time = exp(-ρ * t)
```

**Combined Discounting**:

```
Value of future resource = MU * exp(-k*d - ρ*t)
```

### 4.2 Convergence Properties

#### What Should Converge?

1. **Individual Inventory Ratios**

   - Cobb-Douglas: → α:β
   - Perfect Substitutes: → All of preferred good
   - Perfect Complements: → α:β (balanced)

2. **Spatial Distributions**

   - Agents cluster near high-value resources
   - Density proportional to resource productivity

3. **Trade Frequency**

   - Should decrease as agents reach equilibrium bundles
   - May stabilize at low level (ongoing fine-tuning)

4. **Aggregate Welfare**

   - Total utility should increase monotonically
   - Rate of increase should slow (diminishing returns)

#### Convergence Rate

**Expected Convergence Time**:

```
T_converge ≈ (D_avg / v_move) * n_goods * f_adjustment

where:
  D_avg = average distance to resources
  v_move = movement speed (1 cell/step)
  n_goods = number of good types
  f_adjustment = adjustment factor for learning
```

**Factors Slowing Convergence**:

- High distance discount (k → ∞): Agents myopic
- Large world size: Long travel times
- High resource scarcity: Competition slows acquisition
- Infrequent trade opportunities: Isolated agents

### 4.3 Steady-State Characterization

#### Definition

A steady state is reached when:

```
For all agents i and times t > T*:
  |bundle_i(t+1) - bundle_i(t)| < ε_threshold
  |U_i(t+1) - U_i(t)| < ε_utility
```

#### Predicted Steady States

**Cobb-Douglas Agents**:

- Inventory oscillates around α:β ratio
- Small deviations due to discrete collection
- Periodic trades to rebalance

**Perfect Substitutes Agents**:

- Inventory heavily skewed to preferred good
- Occasional collection of other good if drastically closer
- Minimal trading

**Perfect Complements Agents**:

- Inventory maintains strict α:β ratio
- Active trading to eliminate surpluses
- Alternating collection pattern

#### Steady-State Metrics

**Stability Indicators**:

1. **Coefficient of Variation**: σ(bundle) / μ(bundle) over time
2. **Trade Frequency**: trades per agent per 100 steps
3. **Movement Entropy**: H = -Σ p(direction) * log(p(direction))
4. **Utility Growth Rate**: dU/dt should → 0

______________________________________________________________________

## Part V: Validation Test Design

### 5.1 Analytical Benchmarks

#### Test 1: Equidistant Resource Choice

**Setup**:

- Agent at (5, 5)
- Resource A at (5, 3), Resource B at (5, 7)
- Equal distance = 2

**Prediction**:

- Cobb-Douglas (α=0.7, β=0.3): Collect A:B ≈ 7:3
- Perfect Substitutes (α=0.7, β=0.3): Collect 100% A
- Perfect Complements (α=0.7, β=0.3): Collect A:B = 7:3 exactly

**Success Criterion**: Ratio within 10% of prediction after 100 steps

#### Test 2: Distance Tipping Point

**Setup**:

- Agent at (5, 5), starts with bundle (10, 10)
- Resource A at (5, 3), distance = 2
- Resource B at (5, y), distance = d (variable)

**Prediction**: Find critical distance d\* where agent switches preference

For Cobb-Douglas (α=0.5, β=0.5, k=0.15):

```
d* = d_A + (1/k) * ln(MU_x / MU_y)
   = 2 + (1/0.15) * ln(1)  [if x=y]
   = 2

Agent indifferent at equal distance, switches at d* > 2
```

**Success Criterion**: Measured switch point within ±1 cell of prediction

#### Test 3: Trade Equilibrium

**Setup**:

- Agent A: Cobb-Douglas (α=0.8), bundle (20, 5)
- Agent B: Cobb-Douglas (α=0.2), bundle (5, 20)
- Adjacent positions

**Prediction**:

```
MRS_A = (0.8/0.2) * (5/20) = 1.0
MRS_B = (0.2/0.8) * (20/5) = 1.0

Already at equilibrium! No trade should occur.
```

**Alternative Setup** (Disequilibrium):

- Agent A: bundle (30, 5)
- Agent B: bundle (5, 30)

```
MRS_A = (0.8/0.2) * (5/30) = 0.67 < 1
MRS_B = (0.2/0.8) * (30/5) = 1.5 > 1

Trade occurs: A gives x for y until MRS ≈ 1
```

**Success Criterion**: Post-trade MRS differ by < 10%

### 5.2 Comparative Statics

#### Varying Distance Discount (k)

**Test**: Run same scenario with k ∈ {0.05, 0.15, 0.30}

**Predictions**:

- Low k (0.05): Agents willing to travel far, broad spatial exploration
- Medium k (0.15): Balanced local vs distant resource collection
- High k (0.30): Agents myopic, collect only nearby resources

**Metrics**:

- Average distance traveled per step
- Resource diversity in inventory
- Final utility level

#### Varying Perception Radius (R)

**Test**: Run with R ∈ {4, 8, 16}

**Predictions**:

- Small R: Limited awareness, local optimization, fewer trades
- Large R: Better resource selection, more trade opportunities
- Utility should increase monotonically with R

#### Varying Agent Density

**Test**: Run with N_agents ∈ {10, 50, 100}

**Predictions**:

- Low density: No competition, optimal collection
- Medium density: Some competition, active trading
- High density: Congestion, resource scarcity effects

### 5.3 Statistical Validation (R-07)

#### Objective

Prove that different utility functions produce **measurably distinct** spatial patterns.

#### Spatial Pattern Metrics

1. **Movement Entropy**

   ```
   H = -Σ_dir p(direction) * log(p(direction))

   Prediction:
   - Perfect Substitutes: Low entropy (directional movement)
   - Cobb-Douglas: Medium entropy (balanced exploration)
   - Perfect Complements: Low entropy (alternating pattern)
   ```

2. **Inventory Diversity (Shannon Index)**

   ```
   D = -Σ_good (n_good / N_total) * log(n_good / N_total)

   Prediction:
   - Perfect Substitutes: Low diversity (single good)
   - Cobb-Douglas: High diversity (balanced)
   - Perfect Complements: High diversity (balanced)
   ```

3. **Spatial Clustering (Ripley's K)**

   ```
   K(r) = (A / N²) * Σ_i Σ_j I(d_ij < r)

   Prediction:
   - Perfect Substitutes: High clustering (same resource)
   - Cobb-Douglas: Medium clustering (diverse resources)
   - Perfect Complements: Medium clustering (balanced needs)
   ```

4. **Trade Network Density**

   ```
   ρ = (# actual trades) / (# possible trades)

   Prediction:
   - Perfect Substitutes: Low density (no mutual benefit)
   - Cobb-Douglas: Medium density (moderate rebalancing)
   - Perfect Complements: High density (frequent adjustments)
   ```

#### Statistical Test

**Hypothesis**:

```
H0: Spatial patterns independent of utility function
H1: Spatial patterns differ by utility function
```

**Method**: ANOVA on each metric across utility types

**Success Criterion**: p < 0.05 for at least 3 of 4 metrics

______________________________________________________________________

## Part VI: Implementation Roadmap

### Phase 1: Document Current Spatial Economic Model (Week 1-2)

**Deliverable**: `SPATIAL_ECONOMIC_MODEL.md`

**Contents**:

1. Formal specification of agent decision problem
2. Distance discount economic interpretation
3. Spatial budget constraint derivation
4. Bounded rationality justification
5. Steady-state predictions for each utility type

**Validation**: Document matches implementation in `unified_decision.py`

### Phase 2: Analytical Benchmarks (Week 3-4)

**Deliverable**: Test suite `tests/validation/test_analytical_benchmarks.py`

**Tests**:

- Equidistant resource choice (Test 1)
- Distance tipping point (Test 2)
- Trade equilibrium (Test 3)
- Inventory ratio convergence
- Utility monotonicity

**Success**: All tests pass with < 10% error margin

### Phase 3: Comparative Statics (Week 5-6)

**Deliverable**: Analysis notebook `notebooks/comparative_statics.ipynb`

**Experiments**:

- Vary distance discount k
- Vary perception radius R
- Vary agent density
- Vary resource distribution

**Success**: Results match theoretical predictions qualitatively

### Phase 4: Statistical Validation (Week 7-8)

**Deliverable**: `STATISTICAL_VALIDATION_REPORT.md`

**Analysis**:

- Compute all 4 spatial pattern metrics
- Run ANOVA tests
- Generate visualizations
- Document effect sizes

**Success**: R-07 validated (p < 0.05)

### Phase 5: Documentation and Refinement (Week 9-10)

**Deliverable**: Complete theoretical foundation package

**Documents**:

1. `SPATIAL_ECONOMIC_THEORY.md` (this document)
2. `VALIDATION_RESULTS.md` (summary of all tests)
3. `EDUCATOR_GUIDE.md` (non-technical explanations)
4. `RESEARCH_METHODOLOGY.md` (for academic publication)

**Success**: Ready for external review and educational deployment

______________________________________________________________________

## Part VII: Open Questions for Resolution

### 7.1 Distance Discount Function

**Question**: Is exponential discounting the "right" model for spatial costs?

**Investigation Needed**:

1. Compare exp(-k\*d) vs linear vs hyperbolic
2. Estimate k from human travel behavior studies
3. Test which produces most "realistic" agent patterns

**Decision Criteria**:

- Economic interpretability
- Educational clarity
- Empirical calibration potential

### 7.2 Epsilon Bootstrap Effect

**Question**: How does ε = 0.01 affect behavior, especially at low inventories?

**Investigation Needed**:

1. Analyze MU at bundle (0, 0) vs (1, 0) vs (10, 0)
2. Document when ε dominates decision-making
3. Test alternative bootstrap values

**Decision Criteria**:

- Prevents division by zero (mathematical)
- Models "subsistence" preferences (economic)
- Doesn't distort high-inventory behavior

### 7.3 Trade Acceptance Threshold

**Question**: What should ε_min be for MIN_TRADE_UTILITY_GAIN?

**Current Value**: 0.001

**Investigation Needed**:

1. Economic interpretation (transaction costs?)
2. Effect on trade frequency
3. Sensitivity to utility function scale

**Decision Criteria**:

- Prevents insignificant trades (computational)
- Models decision costs (economic)
- Allows beneficial trades (welfare)

### 7.4 Bounded Rationality vs Optimization

**Question**: Should agents use greedy myopic or dynamic programming?

**Current**: Greedy myopic (look-ahead = 1 step)

**Investigation Needed**:

1. Computational cost of DP with look-ahead = 5, 10
2. Behavioral realism of perfect foresight
3. Educational value of bounded rationality

**Decision Criteria**:

- Computational tractability
- Behavioral plausibility
- Educational message about human decision-making

### 7.5 Resource Regeneration

**Question**: Should resources regenerate, and if so, how?

**Current**: No regeneration (finite resources)

**Investigation Needed**:

1. Economic implications of renewable resources
2. Optimal harvesting strategies
3. Sustainability concepts for education

**Decision Criteria**:

- Educational goals (sustainability vs scarcity)
- Simulation complexity
- Long-run equilibrium properties

______________________________________________________________________

## Part VIII: Success Criteria and Validation Checklist

### Theoretical Completeness

- [ ] Formal agent decision problem documented
- [ ] Distance discount function economically justified
- [ ] Spatial budget constraint derived
- [ ] Bounded rationality assumption defended
- [ ] All three utility functions specified with spatial predictions
- [ ] Multi-agent equilibrium conditions stated
- [ ] Convergence properties characterized

### Analytical Validation

- [ ] Test 1: Equidistant choice passes (< 10% error)
- [ ] Test 2: Distance tipping point identified (< 1 cell error)
- [ ] Test 3: Trade equilibrium verified (< 10% MRS difference)
- [ ] Inventory ratios converge to predictions
- [ ] Utility increases monotonically
- [ ] Steady states reached within expected time

### Comparative Statics

- [ ] Distance discount variation produces predicted patterns
- [ ] Perception radius variation shows monotonic utility gain
- [ ] Agent density variation reveals competition effects
- [ ] Results qualitatively match economic theory

### Statistical Validation (R-07)

- [ ] Movement entropy differs by utility type (p < 0.05)
- [ ] Inventory diversity differs by utility type (p < 0.05)
- [ ] Spatial clustering differs by utility type (p < 0.05)
- [ ] Trade network density differs by utility type (p < 0.05)
- [ ] Effect sizes are large (Cohen's d > 0.8)

### Documentation Quality

- [ ] All mathematical notation defined
- [ ] Economic interpretations provided for each equation
- [ ] Assumptions explicitly stated
- [ ] Limitations acknowledged
- [ ] Testable predictions enumerated
- [ ] Validation methodology described

### Educational Readiness

- [ ] Non-technical summary available
- [ ] Visual aids prepared (diagrams, plots)
- [ ] Example scenarios documented
- [ ] Connection to textbook economics explained
- [ ] Novel contributions highlighted

______________________________________________________________________

## Part IX: Connection to Educational Mission

### How This Framework Supports Teaching

#### 1. Concrete Spatial Intuition

Students see:

- **Distance = Cost**: Agents prefer nearby resources (observable)
- **Trade-offs**: Balancing preference vs convenience (visual)
- **Equilibrium**: Agents converge to stable patterns (measurable)

#### 2. Preference Revelation

Students predict:

- "Cobb-Douglas agent will balance both goods"
- "Perfect Substitutes agent will specialize"
- "Perfect Complements agent will maintain ratio"

Then observe and verify.

#### 3. Market Dynamics

Students explore:

- **No Trade**: Individual optimization
- **Bilateral Trade**: Pairwise improvements
- **Market Equilibrium**: No further gains from trade

#### 4. Comparative Statics

Students experiment:

- "What if resources farther apart?" → See behavior change
- "What if agent more patient?" → See wider exploration
- "What if more agents?" → See competition emerge

### Success Metric R-07 Validation

**Goal**: Solo developer (you) and students can identify utility function from spatial behavior
alone.

**Method**:

1. Run 3 scenarios (unknown utility types)
2. Observe spatial patterns
3. Classify based on:
   - Movement patterns (entropy)
   - Inventory composition (diversity)
   - Trading behavior (frequency)
   - Spatial distribution (clustering)

**Success**: > 90% accuracy in blind classification

**This validates**: Different preferences → Observably different behaviors → Effective teaching tool

______________________________________________________________________

## Part X: Next Steps and Prioritization

### Critical Path (Must Complete First)

1. **Document Distance Discount Interpretation** (4 hours)

   - Write economic justification for exp(-k\*d)
   - Compare to alternatives
   - Choose and defend

2. **Specify Spatial Budget Constraint** (6 hours)

   - Derive implicit prices
   - Formulate constraint
   - Connect to classical theory

3. **Write Analytical Predictions** (8 hours)

   - For each utility function
   - For each test scenario
   - Quantitative thresholds

### High Value (Do Next)

4. **Implement Test 1** (Equidistant Choice) (6 hours)

   - Create scenario
   - Run simulation
   - Compare to prediction
   - Document results

5. **Resolve Epsilon Question** (4 hours)

   - Analyze low-inventory behavior
   - Test alternative values
   - Document interpretation

6. **Bounded Rationality Defense** (4 hours)

   - Justify myopic optimization
   - Connect to behavioral economics
   - Explain educational value

### Medium Priority (Fill Gaps)

7. **Trade Model Specification** (8 hours)

   - Formalize bilateral exchange
   - Predict equilibrium patterns
   - Test with each utility pair

8. **Convergence Analysis** (6 hours)

   - Measure convergence rates
   - Characterize steady states
   - Validate predictions

9. **Comparative Statics Suite** (12 hours)

   - Vary k, R, density
   - Document patterns
   - Compare to theory

### Lower Priority (Comprehensive Coverage)

10. **Statistical Validation** (16 hours)

    - Compute spatial metrics
    - Run ANOVA tests
    - Validate R-07

11. **Educator Materials** (12 hours)

    - Non-technical summaries
    - Visual aids
    - Teaching scenarios

12. **Research Paper Draft** (20 hours)

    - Academic formatting
    - Literature review
    - Novel contributions

______________________________________________________________________

## Conclusion

This document provides a **normative framework** for spatial microeconomic simulation. Unlike the
validation guide (which tests current implementation), this establishes **what should be true** from
economic first principles.

**Key Deliverable**: A formal economic model that:

1. Extends classical microeconomics to spatial, discrete-time settings
2. Makes testable predictions for each utility function
3. Provides analytical benchmarks for validation
4. Justifies design decisions on economic grounds
5. Supports educational mission with clear predictions

**Next Action**: Start with the critical path—document distance discount interpretation and spatial
budget constraint. These are foundational for all other validation work.

Once complete, this framework + validation guide + implementation will form a **complete economic
theory of spatial agent-based simulation**, ready for academic review and educational deployment.
