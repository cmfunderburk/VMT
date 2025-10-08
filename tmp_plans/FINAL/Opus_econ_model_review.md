# Economic Model Validation Guide for VMT EconSim Platform

## Executive Summary

Based on my review of your codebase, you have successfully implemented three core utility functions
with economically sound behavior in a **spatial, discrete-time simulation**. However, there's a
critical gap: you lack **explicit mathematical models** that bridge classical microeconomic theory
with your spatial implementation. This guide provides a structured approach to document and validate
your economic models.

## Current Implementation Status

### What You've Built

#### 1. **Three Utility Functions** (Economically Sound)

- **Cobb-Douglas**: `U = (x + 0.01)^α * (y + 0.01)^β`

  - Implements diminishing marginal utility correctly
  - Agents balance consumption according to α:β ratio
  - Location: `src/econsim/simulation/agent/utility_functions.py:95`

- **Perfect Substitutes**: `U = αx + βy`

  - Linear preferences, agents focus on "cheaper" (closer) good
  - Location: `src/econsim/simulation/agent/utility_functions.py:148`

- **Perfect Complements (Leontief)**: `U = min(αx, βy)`

  - Fixed proportions, agents maintain strict ratios
  - Location: `src/econsim/simulation/agent/utility_functions.py:191`

#### 2. **Spatial Economic Framework**

- **Distance Discounting**: `value = MU * exp(-0.15 * distance)`
- **Dual Inventory System**: Total bundle = carrying + home (economically correct)
- **Bilateral Trade**: 1-for-1 exchanges with Pareto improvement requirement
- **Two-Phase Execution**: Deterministic decision collection → coordinated execution

### Key Deviations from Classical Theory

| Classical Economics                            | Your Implementation          | Validation Impact                       |
| ---------------------------------------------- | ---------------------------- | --------------------------------------- |
| Continuous choice sets                         | Discrete grid locations      | Test with finite resource distributions |
| Explicit budget constraint (`px*x + py*y ≤ M`) | Implicit time/distance costs | Model spatial costs as "prices"         |
| Walrasian auctioneer                           | Bilateral negotiation        | No market-clearing guarantee            |
| Instantaneous transactions                     | Movement takes time          | Distance = transaction cost             |
| Perfect information                            | Perception radius = 8        | Local optimization only                 |

## Validation Framework

### Phase 1: Document Your Actual Models (Not Textbook Models)

For each utility function, create a document that specifies:

#### Template Structure

```markdown
# Economic Model: [Utility Type] in Spatial Grid

## 1. Mathematical Specification
- Utility function: U(x,y) = ...
- Parameters: α = ..., β = ..., ε = ...
- Domain: x,y ∈ ℕ (discrete units)

## 2. Decision Problem
At each time t, agent chooses action a to maximize:
  max_a { EU(a) } where EU(a) = ΔU(a) * exp(-k * distance(a))
  
Subject to:
  - Perception constraint: distance ≤ 8
  - Carrying capacity: total ≤ 100,000
  - Movement constraint: 1 Manhattan unit per step

## 3. Theoretical Predictions
Given scenario X, agent should:
  - Choose resource A when...
  - Switch to resource B when...
  - Accept trade when...

## 4. Validation Tests
- Test 1: Equal distance choice → predict based on MU
- Test 2: Distance-preference tradeoff → predict switching point
- Test 3: Trade equilibrium → predict final allocation
```

### Phase 2: Create Validation Scenarios

#### Essential Test Scenarios

##### 1. **Pure Preference Revelation** (No Distance Effects)

```python
# Setup: Two resources at EQUAL distance
# Agent: Cobb-Douglas (α=0.7, β=0.3)
# Prediction: Collect goods in 7:3 ratio
# Success: Final ratio within 10% of prediction
```

##### 2. **Distance-Preference Tradeoff**

```python
# Setup: Preferred good far (d=10), other good close (d=2)
# Agent: Cobb-Douglas (α=0.7, β=0.3)
# Prediction: Calculate switching point using:
#   MU_x * exp(-0.15*10) < MU_y * exp(-0.15*2)
# Success: Agent switches within ±5 steps of prediction
```

##### 3. **Bilateral Trade Equilibrium**

```python
# Setup: Two agents, complementary endowments
# Agent A: CD(α=0.8), bundle (10,2)
# Agent B: CD(α=0.2), bundle (2,10)
# Prediction: Trade until MRS_A ≈ MRS_B ≈ 1
# Success: Final allocation Pareto-optimal
```

##### 4. **Spatial Pattern Differentiation** (R-07 Validation)

```python
# Setup: Identical resource distribution, 3 agent types
# Measure: Movement entropy, inventory ratios, clustering
# Prediction: Statistically distinct spatial patterns
# Success: p < 0.05 for pattern differences
```

## Immediate Action Plan

### Week 1: Foundation (4-6 hours)

1. **Pick Cobb-Douglas** as your first model (most intuitive)
2. **Write explicit model** using template above
3. **Implement "Pure Preference Revelation"** scenario
4. **Run test**, document results in `ECONOMIC_MODEL_COBB_DOUGLAS.md`
5. **Identify ONE deviation** between theory and simulation

### Week 2: Distance Complexity (8 hours)

1. Add **spatial budget constraint formulation**
2. Implement **"Distance-Preference Tradeoff"** scenario
3. Test with varying distance discount factors (0.05, 0.15, 0.30)
4. Document which produces most realistic behavior

### Week 3: Trading Models (8 hours)

1. Write **bilateral exchange model**
2. Implement **"Trade Equilibrium"** scenario
3. Test all utility function pairs (CD-CD, PS-PS, PC-PC, mixed)
4. Document convergence patterns

### Week 4: Cross-Validation (10 hours)

1. Complete models for **Perfect Substitutes** and **Perfect Complements**
2. Run all scenarios for all utility types
3. Create **comparison matrix** of behaviors
4. Validate **R-07**: "measurably distinct behaviors"

### Week 5: Documentation & Publication (8 hours)

1. Consolidate findings into **`VALIDATION_RESULTS.md`**
2. Create **educator-friendly explanations**
3. Generate **visual proof** (screenshots/videos)
4. Package for **academic review**

## Critical Success Metrics

From your initial_planning.md:

- **R-01**: Predict agent behavior with 95% accuracy ✓ (achievable with explicit models)
- **R-06**: Reproduce theoretical predictions ✓ (validation scenarios above)
- **R-07**: Measurably distinct behaviors ✓ (spatial pattern metrics)

## Key Files to Reference

### For Implementation Details:

- Decision logic: `src/econsim/simulation/agent/unified_decision.py:1130`
- Utility calculations: `src/econsim/simulation/agent/utility_functions.py:336`
- Trade evaluation: `src/econsim/simulation/agent/unified_decision.py:279`

### For Testing:

- Economic coherence: test_trade_economic_coherence.py
- Determinism: `tests/integration/test_determinism_trades.py`

### For Context:

- Educational mission: initial_planning.md
- Detailed review: sonnet45_econ_model_review.md

## Common Pitfalls to Avoid

1. **Don't force textbook models** - Your spatial constraints create a different economic
   environment
2. **Don't ignore epsilon effects** - The 0.01 bootstrap affects behavior at low inventories
3. **Don't assume continuous optimization** - Discrete choices create step functions
4. **Don't forget determinism** - Same seed must produce identical results

## Expected Outcomes

After completing this validation process, you will have:

1. **6 formal model documents** (3 utility functions + spatial + trade + validation suite)
2. **15+ validated scenarios** with quantitative predictions
3. **Statistical proof** of R-07 (measurably distinct behaviors)
4. **Publication-ready** documentation for educational adoption
5. **Confidence** that your simulation is economically sound

## Next Session Focus

Start with **one simple test**:

1. Create a 10x10 grid
2. Place one Cobb-Douglas agent (α=0.5, β=0.5) at (5,5)
3. Place Resource A at (3,5) and Resource B at (7,5) (equal distance = 2)
4. Run for 20 steps
5. Verify agent collects both goods equally (±10%)
6. Document in `ECONOMIC_MODEL_VALIDATION_001.md`

This single test will reveal if your implementation matches theory and guide further validation
efforts.

______________________________________________________________________

*Remember: You're not validating against textbook economics—you're documenting the **spatial
microeconomic model you've actually built** and proving it behaves consistently and educationally.*
