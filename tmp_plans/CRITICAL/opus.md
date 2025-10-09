# Critical Review: Educational Scenarios Refactor Plan

## Executive Summary of Critical Issues

The refactor plan is well-structured but contains several **fundamental gaps** in mapping economic theory to spatial simulation:

1. **Missing spatial economics formalization** - No explicit model for how space affects economic decisions
2. **Incomplete composite behavior theory** - Handwaves the interaction between forage and exchange
3. **No convergence guarantees** - Bilateral exchange may oscillate without reaching equilibrium
4. **Perception radius economics** - Treats visibility as binary without economic interpretation
5. **Transaction sequencing problem** - No theory for who trades with whom when multiple partners available

---

## Part I: Critical Gaps in Economic-to-Spatial Mapping

### Gap 1: Spatial Discounting Theory Incomplete

**Issue**: The forage behavior uses `exp(-0.15 * distance)` without theoretical justification.

**Missing Elements**:
- Why exponential vs. linear or hyperbolic discounting?
- How does discount rate relate to agent's time preference?
- What happens when movement has opportunity cost (foregone collections)?

**Required Documentation**:
```python
class SpatialDiscountModel:
    """
    Theory needed:
    1. Derive discount function from first principles
       - Movement cost: c(d) = time_cost(d) + energy_cost(d)
       - Opportunity cost: foregone_utility_per_step * d
       - Risk/uncertainty: probability of resource disappearing
    
    2. Validate against empirical predictions
       - Switching points between equidistant resources
       - Reservation distance (max distance worth traveling)
    """
```

### Gap 2: Bilateral Exchange Spatial Assumptions

**Issue**: The plan assumes "agents are co-located (no distance cost)" but doesn't address:
- How agents find each other
- Why they would co-locate
- Opportunity cost of traveling to trade

**Missing Theory**:
```python
def spatial_exchange_model():
    """
    Need to formalize:
    1. Search model - how agents find partners
       - Random walk until encounter?
       - Directed movement toward known partners?
       - Market maker/meeting place?
    
    2. Trade-off between forage and travel-to-trade
       - V_forage(local) vs. V_travel_then_trade(distant_partner)
       
    3. Bilateral monopoly problem in space
       - With travel costs, partners have local market power
    """
```

### Gap 3: Composite Behavior Non-Optimality

**Issue**: The plan admits composite behavior is "greedy" and "may not be globally optimal" but doesn't quantify the efficiency loss.

**Critical Questions**:
1. How suboptimal is greedy vs. true dynamic programming?
2. Can agents get "stuck" in local optima?
3. What's the worst-case welfare loss?

**Required Analysis**:
```python
class CompositeEfficiencyAnalysis:
    """
    Measure efficiency loss from myopic decisions:
    
    1. Optimal benchmark (if computationally feasible):
       V* = max E[Σ_{t=0}^∞ δ^t U(c_t) | policy]
    
    2. Greedy policy value:
       V_greedy = E[Σ_{t=0}^∞ δ^t U(c_t) | greedy_policy]
    
    3. Efficiency ratio:
       efficiency = V_greedy / V*
       
    4. Document worst-case scenarios:
       - Agent forages when should position for trade
       - Agent trades suboptimally due to limited local partners
    """
```

---

## Part II: Implementation Inconsistencies

### Inconsistency 1: Perception Radius Economics

**Problem**: Perception radius is treated as exogenous parameter, not economic choice.

**Current Plan**:
```python
visible_resources = grid.get_resources_in_radius(
    agent.x, agent.y, agent.perception_radius  # Fixed parameter
)
```

**Economic Interpretation Needed**:
- Cost of information acquisition
- Limited attention as scarce resource
- Optimal search intensity

**Suggested Fix**:
```python
class PerceptionModel:
    """
    Endogenous perception based on:
    1. Marginal value of information
    2. Cognitive/attention cost
    3. Local resource density
    
    perception_radius = argmax_{r} E[V(information(r))] - cost(r)
    """
```

### Inconsistency 2: Trade Execution Atomicity

**Problem**: The plan doesn't address what happens when:
- Multiple agents want to trade with same partner
- Trade proposals conflict
- Partial trades are beneficial

**Current Assumption**: "Enforceable contracts (no reneging)"

**Reality in Simulation**: Need explicit protocol for:
```python
class TradeProtocol:
    """
    Resolve conflicts when multiple trade proposals:
    
    Option 1: First-come-first-served (by agent.id)
    Option 2: Auction (highest surplus wins)
    Option 3: Random matching
    Option 4: Stable matching algorithm
    
    Each has different economic implications!
    """
```

### Inconsistency 3: Resource Respawning Economics

**Problem**: Resources respawn deterministically, but agents don't account for future availability.

**Missing Elements**:
- Renewable resource extraction theory
- Optimal harvesting under regeneration
- Commons problem when multiple agents compete

**Required Model**:
```python
class RenewableResourceModel:
    """
    Agents should consider:
    1. Current collection value: MU(resource_now)
    2. Option value of waiting: E[MU(resource_future) | wait]
    3. Competition: P(other_agent_collects)
    
    Optimal policy solves:
    collect_if: MU_now > δ * E[MU_future] * P(available_future)
    """
```

---

## Part III: Testing and Validation Gaps

### Gap 1: No Equilibrium Tests

**Problem**: Plan lacks tests for economic equilibria.

**Required Tests**:
```python
def test_bilateral_exchange_equilibrium():
    """
    Verify:
    1. Exchange stops at contract curve (MRS_i = MRS_j)
    2. No further Pareto improvements possible
    3. Core allocations achieved (no coalition can do better)
    """

def test_spatial_foraging_equilibrium():
    """
    Verify:
    1. Marginal value equalized across resources (accounting for distance)
    2. No agent wants to deviate from current position
    3. Steady-state distribution matches theoretical prediction
    """
```

### Gap 2: No Welfare Metrics

**Problem**: "Success Metrics" section doesn't define welfare measurement.

**Required Metrics**:
```python
class WelfareMetrics:
    """
    Track:
    1. Utilitarian welfare: W = Σ_i U_i
    2. Pareto efficiency: No waste, all gains exploited
    3. Equity: Gini coefficient of utility distribution
    4. Stability: Convergence to steady-state
    
    Compare:
    - Actual vs. social optimum
    - With/without exchange
    - Different behavioral rules
    """
```

---

## Part IV: Step-by-Step Review Process

### Phase 1: Theoretical Foundation (Week 0 - Before Coding)

#### Step 1.1: Formalize Spatial Economics
```markdown
1. Document spatial utility model:
   U(x, y, t) = u(consumption) - c(movement) - s(search)
   
2. Derive optimal foraging policy:
   - Marginal value of movement
   - Reservation utility for resources
   
3. Prove/disprove convergence:
   - Does system reach steady state?
   - Is it unique?
```

#### Step 1.2: Formalize Exchange in Space
```markdown
1. Define bilateral exchange protocol:
   - Who can trade with whom?
   - How are terms determined?
   - What about multilateral trade?
   
2. Prove efficiency properties:
   - Are all trades Pareto improvements?
   - Do we reach core allocation?
   
3. Address spatial monopoly:
   - Local market power due to distance
   - Price discrimination possibilities
```

#### Step 1.3: Formalize Composite Behavior
```markdown
1. Define optimal benchmark:
   - Full dynamic programming solution
   - Computational complexity
   
2. Quantify greedy approximation:
   - Worst-case efficiency loss
   - Average-case performance
   
3. Identify failure modes:
   - When does greedy fail badly?
   - Can we detect and correct?
```

### Phase 2: Implementation Review (During Coding)

#### Step 2.1: Behavior Module Review
```python
# For each behavior module:
def review_behavior_implementation(module):
    """
    Check:
    1. Mathematical model matches documentation
    2. All parameters have economic interpretation
    3. Edge cases handled (zero inventory, etc.)
    4. Determinism preserved
    5. Assumptions validated before use
    """
```

#### Step 2.2: Integration Review
```python
def review_integration():
    """
    Verify:
    1. Behaviors compose without conflicts
    2. State updates are atomic
    3. No hidden dependencies
    4. Feature flags work correctly
    5. Legacy compatibility maintained
    """
```

### Phase 3: Validation Testing (After Implementation)

#### Step 3.1: Economic Correctness Tests
```bash
# Test suite for economic properties
pytest tests/economic/
├── test_utility_maximization.py
├── test_pareto_efficiency.py
├── test_equilibrium_convergence.py
├── test_welfare_theorems.py
└── test_spatial_economics.py
```

#### Step 3.2: Educational Effectiveness Tests
```markdown
1. User prediction accuracy:
   - Can students predict agent behavior from parameters?
   
2. Concept clarity:
   - Does each scenario teach exactly one concept?
   
3. Parameter sensitivity:
   - Do changes produce expected effects?
```

### Phase 4: Documentation Review

#### Step 4.1: Theory Documentation
```markdown
For each behavior:
1. Mathematical model (equations)
2. Assumptions (explicit list)
3. Limitations (known deviations)
4. Predictions (testable outcomes)
5. References (academic sources)
```

#### Step 4.2: Code Documentation
```markdown
For each module:
1. Docstrings link to theory docs
2. Parameter ranges justified
3. Implementation choices explained
4. Test coverage documented
5. Performance characteristics noted
```

---

## Part V: Prioritized Action Items

### Critical (Must Fix Before Implementation)

1. **Formalize spatial discount function**
   - Derive from first principles
   - Validate discount rate choice
   - Document in `tmp_plans/MODELS/spatial_discounting.md`

2. **Define exchange protocol precisely**
   - Who trades with whom, when
   - Conflict resolution mechanism
   - Document in `tmp_plans/MODELS/bilateral_exchange_protocol.md`

3. **Quantify composite behavior efficiency**
   - Benchmark against optimal
   - Identify worst cases
   - Document in `tmp_plans/MODELS/composite_behavior_analysis.md`

### Important (Fix During Implementation)

4. **Add equilibrium tests**
   - Test for convergence
   - Verify steady-state properties
   - Add to test suite

5. **Implement welfare metrics**
   - Track total utility
   - Measure efficiency
   - Add to analytics module

6. **Handle perception economically**
   - Model information cost
   - Allow endogenous radius
   - Document assumptions

### Nice-to-Have (Post-Launch)

7. **Dynamic resource model**
   - Renewable resource theory
   - Optimal harvesting
   - Commons problems

8. **Market mechanisms**
   - Centralized exchange
   - Price discovery
   - Market clearing

---

## Part VI: Risk Assessment Updates

### New High Risks Identified

1. **Theoretical Incoherence**
   - Mixing models without unified framework
   - **Mitigation**: Complete theory docs before coding

2. **Equilibrium Non-Existence**  
   - System may not converge
   - **Mitigation**: Prove convergence or document cycles

3. **Efficiency Loss Unbounded**
   - Greedy composite could be arbitrarily bad
   - **Mitigation**: Quantify and bound efficiency loss

#### Critical Review: Educational Scenarios Refactor Plan

## Executive Summary of Critical Issues

The refactor plan is well-structured but contains several **fundamental gaps** in mapping economic theory to spatial simulation:

1. **Missing spatial economics formalization** - No explicit model for how space affects economic decisions
2. **Incomplete composite behavior theory** - Handwaves the interaction between forage and exchange
3. **No convergence guarantees** - Bilateral exchange may oscillate without reaching equilibrium
4. **Perception radius economics** - Treats visibility as binary without economic interpretation
5. **Transaction sequencing problem** - No theory for who trades with whom when multiple partners available

---

## Part I: Critical Gaps in Economic-to-Spatial Mapping

### Gap 1: Spatial Discounting Theory Incomplete

**Issue**: The forage behavior uses `exp(-0.15 * distance)` without theoretical justification.

**Missing Elements**:
- Why exponential vs. linear or hyperbolic discounting?
- How does discount rate relate to agent's time preference?
- What happens when movement has opportunity cost (foregone collections)?

**Required Documentation**:
```python
class SpatialDiscountModel:
    """
    Theory needed:
    1. Derive discount function from first principles
       - Movement cost: c(d) = time_cost(d) + energy_cost(d)
       - Opportunity cost: foregone_utility_per_step * d
       - Risk/uncertainty: probability of resource disappearing
    
    2. Validate against empirical predictions
       - Switching points between equidistant resources
       - Reservation distance (max distance worth traveling)
    """
```

### Gap 2: Bilateral Exchange Spatial Assumptions

**Issue**: The plan assumes "agents are co-located (no distance cost)" but doesn't address:
- How agents find each other
- Why they would co-locate
- Opportunity cost of traveling to trade

**Missing Theory**:
```python
def spatial_exchange_model():
    """
    Need to formalize:
    1. Search model - how agents find partners
       - Random walk until encounter?
       - Directed movement toward known partners?
       - Market maker/meeting place?
    
    2. Trade-off between forage and travel-to-trade
       - V_forage(local) vs. V_travel_then_trade(distant_partner)
       
    3. Bilateral monopoly problem in space
       - With travel costs, partners have local market power
    """
```

### Gap 3: Composite Behavior Non-Optimality

**Issue**: The plan admits composite behavior is "greedy" and "may not be globally optimal" but doesn't quantify the efficiency loss.

**Critical Questions**:
1. How suboptimal is greedy vs. true dynamic programming?
2. Can agents get "stuck" in local optima?
3. What's the worst-case welfare loss?

**Required Analysis**:
```python
class CompositeEfficiencyAnalysis:
    """
    Measure efficiency loss from myopic decisions:
    
    1. Optimal benchmark (if computationally feasible):
       V* = max E[Σ_{t=0}^∞ δ^t U(c_t) | policy]
    
    2. Greedy policy value:
       V_greedy = E[Σ_{t=0}^∞ δ^t U(c_t) | greedy_policy]
    
    3. Efficiency ratio:
       efficiency = V_greedy / V*
       
    4. Document worst-case scenarios:
       - Agent forages when should position for trade
       - Agent trades suboptimally due to limited local partners
    """
```

---

## Part II: Implementation Inconsistencies

### Inconsistency 1: Perception Radius Economics

**Problem**: Perception radius is treated as exogenous parameter, not economic choice.

**Current Plan**:
```python
visible_resources = grid.get_resources_in_radius(
    agent.x, agent.y, agent.perception_radius  # Fixed parameter
)
```

**Economic Interpretation Needed**:
- Cost of information acquisition
- Limited attention as scarce resource
- Optimal search intensity

**Suggested Fix**:
```python
class PerceptionModel:
    """
    Endogenous perception based on:
    1. Marginal value of information
    2. Cognitive/attention cost
    3. Local resource density
    
    perception_radius = argmax_{r} E[V(information(r))] - cost(r)
    """
```

### Inconsistency 2: Trade Execution Atomicity

**Problem**: The plan doesn't address what happens when:
- Multiple agents want to trade with same partner
- Trade proposals conflict
- Partial trades are beneficial

**Current Assumption**: "Enforceable contracts (no reneging)"

**Reality in Simulation**: Need explicit protocol for:
```python
class TradeProtocol:
    """
    Resolve conflicts when multiple trade proposals:
    
    Option 1: First-come-first-served (by agent.id)
    Option 2: Auction (highest surplus wins)
    Option 3: Random matching
    Option 4: Stable matching algorithm
    
    Each has different economic implications!
    """
```

### Inconsistency 3: Resource Respawning Economics

**Problem**: Resources respawn deterministically, but agents don't account for future availability.

**Missing Elements**:
- Renewable resource extraction theory
- Optimal harvesting under regeneration
- Commons problem when multiple agents compete

**Required Model**:
```python
class RenewableResourceModel:
    """
    Agents should consider:
    1. Current collection value: MU(resource_now)
    2. Option value of waiting: E[MU(resource_future) | wait]
    3. Competition: P(other_agent_collects)
    
    Optimal policy solves:
    collect_if: MU_now > δ * E[MU_future] * P(available_future)
    """
```

---

## Part III: Testing and Validation Gaps

### Gap 1: No Equilibrium Tests

**Problem**: Plan lacks tests for economic equilibria.

**Required Tests**:
```python
def test_bilateral_exchange_equilibrium():
    """
    Verify:
    1. Exchange stops at contract curve (MRS_i = MRS_j)
    2. No further Pareto improvements possible
    3. Core allocations achieved (no coalition can do better)
    """

def test_spatial_foraging_equilibrium():
    """
    Verify:
    1. Marginal value equalized across resources (accounting for distance)
    2. No agent wants to deviate from current position
    3. Steady-state distribution matches theoretical prediction
    """
```

### Gap 2: No Welfare Metrics

**Problem**: "Success Metrics" section doesn't define welfare measurement.

**Required Metrics**:
```python
class WelfareMetrics:
    """
    Track:
    1. Utilitarian welfare: W = Σ_i U_i
    2. Pareto efficiency: No waste, all gains exploited
    3. Equity: Gini coefficient of utility distribution
    4. Stability: Convergence to steady-state
    
    Compare:
    - Actual vs. social optimum
    - With/without exchange
    - Different behavioral rules
    """
```

---

## Part IV: Step-by-Step Review Process

### Phase 1: Theoretical Foundation (Week 0 - Before Coding)

#### Step 1.1: Formalize Spatial Economics
```markdown
1. Document spatial utility model:
   U(x, y, t) = u(consumption) - c(movement) - s(search)
   
2. Derive optimal foraging policy:
   - Marginal value of movement
   - Reservation utility for resources
   
3. Prove/disprove convergence:
   - Does system reach steady state?
   - Is it unique?
```

#### Step 1.2: Formalize Exchange in Space
```markdown
1. Define bilateral exchange protocol:
   - Who can trade with whom?
   - How are terms determined?
   - What about multilateral trade?
   
2. Prove efficiency properties:
   - Are all trades Pareto improvements?
   - Do we reach core allocation?
   
3. Address spatial monopoly:
   - Local market power due to distance
   - Price discrimination possibilities
```

#### Step 1.3: Formalize Composite Behavior
```markdown
1. Define optimal benchmark:
   - Full dynamic programming solution
   - Computational complexity
   
2. Quantify greedy approximation:
   - Worst-case efficiency loss
   - Average-case performance
   
3. Identify failure modes:
   - When does greedy fail badly?
   - Can we detect and correct?
```

### Phase 2: Implementation Review (During Coding)

#### Step 2.1: Behavior Module Review
```python
# For each behavior module:
def review_behavior_implementation(module):
    """
    Check:
    1. Mathematical model matches documentation
    2. All parameters have economic interpretation
    3. Edge cases handled (zero inventory, etc.)
    4. Determinism preserved
    5. Assumptions validated before use
    """
```

#### Step 2.2: Integration Review
```python
def review_integration():
    """
    Verify:
    1. Behaviors compose without conflicts
    2. State updates are atomic
    3. No hidden dependencies
    4. Feature flags work correctly
    5. Legacy compatibility maintained
    """
```

### Phase 3: Validation Testing (After Implementation)

#### Step 3.1: Economic Correctness Tests
```bash
# Test suite for economic properties
pytest tests/economic/
├── test_utility_maximization.py
├── test_pareto_efficiency.py
├── test_equilibrium_convergence.py
├── test_welfare_theorems.py
└── test_spatial_economics.py
```

#### Step 3.2: Educational Effectiveness Tests
```markdown
1. User prediction accuracy:
   - Can students predict agent behavior from parameters?
   
2. Concept clarity:
   - Does each scenario teach exactly one concept?
   
3. Parameter sensitivity:
   - Do changes produce expected effects?
```

### Phase 4: Documentation Review

#### Step 4.1: Theory Documentation
```markdown
For each behavior:
1. Mathematical model (equations)
2. Assumptions (explicit list)
3. Limitations (known deviations)
4. Predictions (testable outcomes)
5. References (academic sources)
```

#### Step 4.2: Code Documentation
```markdown
For each module:
1. Docstrings link to theory docs
2. Parameter ranges justified
3. Implementation choices explained
4. Test coverage documented
5. Performance characteristics noted
```

---

## Part V: Prioritized Action Items

### Critical (Must Fix Before Implementation)

1. **Formalize spatial discount function**
   - Derive from first principles
   - Validate discount rate choice
   - Document in `tmp_plans/MODELS/spatial_discounting.md`

2. **Define exchange protocol precisely**
   - Who trades with whom, when
   - Conflict resolution mechanism
   - Document in `tmp_plans/MODELS/bilateral_exchange_protocol.md`

3. **Quantify composite behavior efficiency**
   - Benchmark against optimal
   - Identify worst cases
   - Document in `tmp_plans/MODELS/composite_behavior_analysis.md`

### Important (Fix During Implementation)

4. **Add equilibrium tests**
   - Test for convergence
   - Verify steady-state properties
   - Add to test suite

5. **Implement welfare metrics**
   - Track total utility
   - Measure efficiency
   - Add to analytics module

6. **Handle perception economically**
   - Model information cost
   - Allow endogenous radius
   - Document assumptions

### Nice-to-Have (Post-Launch)

7. **Dynamic resource model**
   - Renewable resource theory
   - Optimal harvesting
   - Commons problems

8. **Market mechanisms**
   - Centralized exchange
   - Price discovery
   - Market clearing

---

## Part VI: Risk Assessment Updates

### New High Risks Identified

1. **Theoretical Incoherence**
   - Mixing models without unified framework
   - **Mitigation**: Complete theory docs before coding

2. **Equilibrium Non-Existence**  
   - System may not converge
   - **Mitigation**: Prove convergence or document cycles

3. **Efficiency Loss Unbounded**
   - Greedy composite could be arbitrarily bad
   - **Mitigation**: Quantify and bound efficiency loss

### BROKE OFF HERE ###


# ...existing content...

### Recommendation: Systematic Review Process

Based on the gaps identified, here's the step-by-step process to systematically address each issue:

---

## Part VII: Systematic Resolution Process

### Week 0: Theoretical Foundation Sprint

#### Day 1-2: Spatial Economics Formalization
```markdown
Task: Create `tmp_plans/MODELS/spatial_economics_foundation.md`

1. Define spatial utility function:
   U(x, y, t) = u(consumption_bundle) - c(distance_traveled) - s(search_cost)

2. Derive distance discount from first principles:
   - Start with time cost: steps_to_target = manhattan_distance(current, target)
   - Opportunity cost per step: foregone_collections_per_step
   - Risk of resource depletion: P(resource_gone) = 1 - exp(-λ * distance)
   - Result: Justify exponential vs. other functional forms

3. Validate with testable predictions:
   - Switching distance between two resources of different values
   - Maximum profitable foraging distance
   - Effect of resource density on search pattern
```

#### Day 3-4: Exchange Protocol Specification
```markdown
Task: Create `tmp_plans/MODELS/exchange_protocol_specification.md`

1. Define matching mechanism:
   Option A: Simultaneous proposals with stable matching
   Option B: Sequential by agent.id (deterministic order)
   Option C: Random matching with acceptance/rejection
   
2. Specify negotiation protocol:
   - Bilateral monopoly: Nash bargaining solution
   - Take-it-or-leave-it offers
   - Iterative bargaining with convergence

3. Handle edge cases:
   - Multiple agents want same partner
   - Circular trade desires (A→B, B→C, C→A)
   - Partial trades when inventory discrete
```

#### Day 5: Composite Behavior Analysis
```markdown
Task: Create `tmp_plans/MODELS/composite_behavior_efficiency.md`

1. Define optimal benchmark:
   V*(s) = max_π E[Σ_{t=0}^∞ δ^t u(c_t) | s_0 = s, policy = π]
   
2. Compute greedy policy value:
   V_greedy(s) = max_a {immediate_reward(a) + δ * E[V_greedy(s')]}
   
3. Bound efficiency loss:
   - Best case: When local optimum = global optimum
   - Worst case: Agent trapped in low-value region
   - Average case: Monte Carlo simulation results

4. Identify improvement heuristics:
   - Limited lookahead (2-3 steps)
   - Periodic exploration phases
   - Memory of profitable trade partners
```

### Week 1: Documentation Remediation

#### Create Missing Economic Models
```bash
# Create formal model documents
touch tmp_plans/MODELS/spatial_discounting.md
touch tmp_plans/MODELS/bilateral_exchange_protocol.md
touch tmp_plans/MODELS/composite_behavior_analysis.md
touch tmp_plans/MODELS/perception_economics.md
touch tmp_plans/MODELS/renewable_resources.md

# Each document must contain:
# 1. Mathematical model (LaTeX equations)
# 2. Assumptions (numbered list)
# 3. Predictions (testable hypotheses)
# 4. Implementation mapping (model → code)
# 5. Validation tests (how to verify)
```

#### Economic Correctness Checklist
```markdown
For each behavior module, verify:

[ ] Utility maximization
    - Agent chooses highest-value action given constraints
    - Ties broken deterministically (by resource/agent id)
    
[ ] Constraint satisfaction  
    - Budget constraint (can't trade what you don't have)
    - Spatial constraint (can't collect distant resources instantly)
    - Capacity constraint (inventory limits)
    
[ ] Equilibrium properties
    - Define what equilibrium means for this behavior
    - Prove existence (or document non-existence)
    - Prove uniqueness (or characterize multiple equilibria)
    
[ ] Welfare properties
    - Pareto efficiency (no waste)
    - Individual rationality (no agent worse off)
    - Stability (no group wants to deviate)
```

### Week 2: Implementation Preparation

#### Test Suite Design
```python
# tests/economic/test_spatial_discounting.py
def test_exponential_discount_switching_point():
    """
    Given two resources at different distances with different values,
    verify agent switches at theoretically predicted distance.
    """
    pass

def test_maximum_foraging_distance():
    """
    Verify agent won't travel beyond distance where 
    discounted value < opportunity cost.
    """
    pass

# tests/economic/test_exchange_protocol.py  
def test_bilateral_exchange_reaches_contract_curve():
    """
    After sufficient trades, verify allocation is on contract curve
    (MRS_agent1 = MRS_agent2).
    """
    pass

def test_no_beneficial_trades_remain():
    """
    At equilibrium, verify no mutually beneficial trades exist.
    """
    pass

# tests/economic/test_composite_efficiency.py
def test_greedy_efficiency_bounded():
    """
    Verify greedy policy achieves at least X% of optimal value
    across test scenarios.
    """
    pass
```

#### Performance Benchmarks
```python
# benchmarks/economic_scenarios.py
def benchmark_spatial_foraging():
    """
    Measure:
    - Steps to equilibrium distribution
    - Resource collection efficiency
    - Distance traveled per unit collected
    """
    pass

def benchmark_bilateral_exchange():
    """
    Measure:
    - Trades to reach core allocation
    - Welfare improvement per trade
    - Computational time vs. number of agents
    """
    pass

def benchmark_composite_behavior():
    """
    Measure:
    - Total welfare vs. separate behaviors
    - Decision time complexity
    - Convergence properties
    """
    pass
```

---

## Part VIII: Critical Decision Points

### Decision 1: Distance Discount Function Form

**Options**:
1. **Exponential** (current): `exp(-k * d)` - Assumes constant hazard rate
2. **Hyperbolic**: `1 / (1 + k * d)` - Matches behavioral economics findings
3. **Linear**: `max(0, 1 - k * d)` - Simplest, finite support
4. **Threshold**: `1 if d ≤ d_max else 0` - Binary decision

**Recommendation**: Document why exponential chosen, provide sensitivity analysis showing results robust to functional form choice.

### Decision 2: Trade Matching Protocol

**Options**:
1. **Stable matching** - Gale-Shapley algorithm, guarantees stability
2. **Random matching** - Simple, may be inefficient  
3. **Sequential** - Deterministic order, first-mover advantage
4. **Simultaneous** - All trades execute if mutually beneficial

**Recommendation**: Start with **sequential** (deterministic), document limitations, implement stable matching as enhancement.

### Decision 3: Perception Model

**Options**:
1. **Fixed radius** - Simple, exogenous parameter
2. **Endogenous** - Optimal information acquisition
3. **Resource-dependent** - Higher-value resources "visible" from farther
4. **Probabilistic** - Detection probability decreases with distance

**Recommendation**: Keep **fixed radius** for initial implementation, but document economic interpretation (bounded rationality, cognitive limits).

---

## Part IX: Success Criteria Updates

### Economic Correctness (Expanded)
- [ ] All behaviors have formal mathematical models
- [ ] Distance discounting derived from first principles
- [ ] Exchange protocol handles all edge cases
- [ ] Composite behavior efficiency quantified
- [ ] Equilibrium existence/uniqueness proven or documented
- [ ] Welfare metrics implemented and validated

### Testing Coverage (New Requirements)
- [ ] Unit tests for each economic assumption
- [ ] Integration tests for equilibrium convergence  
- [ ] Performance benchmarks for efficiency
- [ ] Sensitivity analysis for key parameters
- [ ] Validation against theoretical predictions

### Documentation Completeness
- [ ] Every economic parameter has interpretation
- [ ] All assumptions explicitly stated
- [ ] Limitations acknowledged with impact assessment
- [ ] References to relevant economic literature
- [ ] Mapping from theory to implementation clear

---

## Part X: Final Recommendations

### Immediate Actions (Before Any Coding)

1. **Complete theoretical models** (Week 0)
   - All documents in `tmp_plans/MODELS/` written
   - Peer review by economic theory expert
   - Sign-off that models are coherent

2. **Design test suite** (Week 1, Day 1-2)
   - Write test specifications (not code)
   - Define success criteria for each test
   - Identify which tests are "must pass" vs. "nice to have"

3. **Create minimal working example** (Week 1, Day 3-5)
   - Single behavior in isolation
   - Verify economic correctness
   - Use as template for other behaviors

### Risk Mitigations

**For Theoretical Incoherence**:
- Don't start coding until models documented
- Each behavior references specific economic papers
- Regular review checkpoints with theory expert

**For Equilibrium Non-Existence**:
- Define what "good enough" convergence means
- Implement detection for oscillation/cycles
- Document when equilibrium not guaranteed

**For Unbounded Efficiency Loss**:
- Compute bounds for specific scenarios
- Implement safeguards (e.g., periodic optimal recalculation)
- Make efficiency metrics visible in GUI

### Long-term Enhancements

After core implementation stable:
1. **Market mechanisms** - Centralized price discovery
2. **Learning agents** - Adaptive behavior based on history
3. **Incomplete information** - Private values, signaling
4. **Network effects** - Reputation, repeated interaction
5. **Institutional rules** - Property rights, contracts

---

## Conclusion

The refactor plan has solid structure but needs **theoretical foundation** before implementation. The identified gaps are not just documentation issues—they represent fundamental questions about how economic theory maps to spatial, discrete-time simulation.

**Critical Path**:
1. Formalize models (Week 0)
2. Design tests (Week 1, Days 1-2)  
3. Minimal implementation (Week 1, Days 3-5)
4. Then follow original plan phases

Without this theoretical groundwork, the implementation risks creating a spatial simulation that *looks* economic but violates core theoretical principles—undermining the educational mission.
