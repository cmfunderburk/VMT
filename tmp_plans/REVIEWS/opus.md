# Economic Model: Cobb-Douglas Agent in Spatial Grid

## 1. Utility Specification

### 1.1 Mathematical Foundation
- Utility over discrete bundles (stocks):  
  $$
  U(x,y) = (x + \varepsilon)^{\alpha} (y + \varepsilon)^{\beta},\qquad \alpha,\beta>0
  $$
  with $\varepsilon=0.01$ (bootstrap to avoid log(0) issues), typically $\alpha+\beta=1$.

### 1.2 Economic Interpretation
- **Diminishing marginal utility**: Each additional unit provides less satisfaction
- **Smooth substitution**: Agents willing to trade off between goods
- **Balanced consumption**: Optimal bundle proportions determined by $\alpha:\beta$ ratio
- **Bootstrap rationale**: Small $\varepsilon$ ensures utility defined at zero inventory without distorting preferences

### 1.3 Marginal Utilities
$$
MU_x = \frac{\partial U}{\partial x} = \alpha (x+\varepsilon)^{\alpha-1}(y+\varepsilon)^{\beta}
$$
$$
MU_y = \frac{\partial U}{\partial y} = \beta (x+\varepsilon)^{\alpha}(y+\varepsilon)^{\beta-1}
$$

### 1.4 Marginal Rate of Substitution
$$
MRS_{xy} = \frac{MU_x}{MU_y} = \frac{\alpha}{\beta} \cdot \frac{y+\varepsilon}{x+\varepsilon}
$$

## 2. Spatial Economic Framework

### 2.1 Distance Discounting
- Effective utility when acquiring resource at distance $d$:
  $$
  U_{\text{effective}} = \Delta U \cdot e^{-k d}
  $$
  where $\Delta U = U(\text{bundle after}) - U(\text{bundle before})$
  
- Current implementation: $k = 0.15$ (`DISTANCE_DISCOUNT_FACTOR`)

### 2.2 Economic Interpretation of Distance
- **Transaction cost proxy**: Distance represents time/effort cost
- **Implicit price**: $p_{\text{implicit}} = 1/e^{-kd}$ increases with distance
- **Behavioral implication**: Agents prefer closer resources, all else equal

### 2.3 Decision Rule
Choose good $x$ over good $y$ if:
$$
MU_x \cdot e^{-k d_x} > MU_y \cdot e^{-k d_y}
$$

## 3. Spatial Budget Constraint

### 3.1 Classical vs Spatial
| Classical Economics | Your Spatial Implementation |
|-------------------|---------------------------|
| $p_x \cdot x + p_y \cdot y \leq M$ | Time/movement constraints |
| Explicit prices | Distance-based implicit costs |
| Simultaneous choice | Sequential decisions |
| Perfect information | Perception radius = 8 |

### 3.2 Implicit Budget Formulation
In your simulation, the budget constraint is:
- **Time constraint**: One action per simulation step
- **Movement constraint**: Manhattan distance, 1 unit per step
- **Perception constraint**: Can only see/interact within radius 8
- **Capacity constraint**: Total carrying ≤ 100,000 (effectively non-binding)

### 3.3 Effective Constraint
The binding constraint is typically time/distance, making the effective optimization:
$$
\max_{t \in T} \sum_{t=1}^{T} U(x_t, y_t) \cdot e^{-k \cdot d_t}
$$
where $T$ is the time horizon and $d_t$ is distance traveled at time $t$.

## 4. Agent Decision Process

### 4.1 Information Set
At each step $t$, agent observes:
- Own inventory: $(x_t, y_t)$ where total = carrying + home
- Visible resources: $\{r_i : \text{distance}(r_i, \text{agent}) \leq 8\}$
- Nearby agents for potential trades

### 4.2 Action Space
1. **Move toward resource** (if perceive any)
2. **Collect resource** (if adjacent)
3. **Trade with partner** (if beneficial trade exists)
4. **Return home** (if carrying inventory full)
5. **Deposit at home** (if at home with items)
6. **Idle** (if no beneficial action)

### 4.3 Decision Algorithm
```
1. Calculate total bundle = carrying + home
2. For each visible resource r:
   a. Compute ΔU from collecting r
   b. Apply distance discount: EU(r) = ΔU * exp(-k * distance(r))
3. For each nearby agent a:
   a. Enumerate possible 1-for-1 trades
   b. Check if both agents gain utility (Pareto improvement)
4. Select action with highest expected utility
5. Apply deterministic tiebreak (lowest ID)
```

## 5. Theoretical Predictions

### 5.1 Long-Run Bundle Ratio
Without spatial constraints, Cobb-Douglas agents converge to:
$$
\frac{y^*}{x^*} = \frac{\beta}{\alpha}
$$

### 5.2 Switching Distance
Agent switches from collecting good $x$ to good $y$ when:
$$
\Delta d^* = d_x - d_y = \frac{1}{k}\ln\left(\frac{MU_x}{MU_y}\right)
$$

For balanced preferences ($\alpha = \beta = 0.5$):
$$
\Delta d^* = \frac{1}{k}\ln\left(\frac{y+\varepsilon}{x+\varepsilon}\right)
$$

### 5.3 Trade Acceptance Condition
Accept trade of good $i$ for good $j$ if:
$$
U(x-\delta_i, y+\delta_j) > U(x,y) + \text{MIN\_TRADE\_UTILITY\_GAIN}
$$
where $\delta_i = \delta_j = 1$ (1-for-1 trades only)

## 6. Validation Scenarios

### 6.1 Scenario A: Pure Preference Revelation
**Setup**: Two resources at equal distance (d=5)
- Agent: CD($\alpha=0.7, \beta=0.3$), starting at (0,0)
- Resource A at (5,0), Resource B at (0,5)
- Grid: 10x10, no other agents

**Prediction**: Over 100 steps, collect ratio converges to:
$$
\frac{\text{good2 collected}}{\text{good1 collected}} \approx \frac{0.3}{0.7} = 0.43
$$

**Success Criteria**: Ratio within 10% of prediction

### 6.2 Scenario B: Distance-Preference Tradeoff
**Setup**: Preferred good farther away
- Agent: CD($\alpha=0.7, \beta=0.3$)
- Resource A (good1) at distance 10
- Resource B (good2) at distance 2

**Prediction**: Switch to good2 when:
$$
MU_{\text{good1}} \cdot e^{-0.15 \cdot 10} < MU_{\text{good2}} \cdot e^{-0.15 \cdot 2}
$$

Solving for inventory levels:
- Switch occurs around $(x,y) \approx (3,1)$

**Success Criteria**: Switch within ±1 unit of prediction

### 6.3 Scenario C: Bilateral Trade Equilibrium
**Setup**: Two CD agents with complementary endowments
- Agent A: CD($\alpha=0.8, \beta=0.2$), starts with (2,10)
- Agent B: CD($\alpha=0.2, \beta=0.8$), starts with (10,2)
- Co-located (no movement needed)

**Prediction**: Trade until MRS approximately equal:
$$
MRS_A \approx MRS_B \approx 1 \text{ (for 1:1 trades)}
$$

Final allocation near:
- Agent A: $(7,5)$
- Agent B: $(5,7)$

**Success Criteria**: 
- Both agents gain utility (Pareto improvement)
- Final MRS within 20% of equality

## 7. Implementation Mapping

### 7.1 Core Components
- **Utility calculation**: [`CobbDouglasUtility.calculate()`](src/econsim/simulation/agent/utility_functions.py:95)
- **Decision engine**: [`make_agent_decision()`](src/econsim/simulation/agent/unified_decision.py:1130)
- **Distance evaluation**: `evaluate_resource_options()` in unified_decision.py
- **Trade evaluation**: [`find_beneficial_bilateral_trade()`](src/econsim/simulation/agent/unified_decision.py:279)
- **Executor**: [`UnifiedStepExecutor`](src/econsim/simulation/executor.py:34)

### 7.2 Configuration Parameters
```python
# Factory pattern (required)
from econsim.simulation.agent.utility_functions import create_utility_function
utility = create_utility_function("cobb_douglas", alpha=0.5, beta=0.5)

# Distance discount (hardcoded)
DISTANCE_DISCOUNT_FACTOR = 0.15  # In unified_decision.py

# Trade threshold
MIN_TRADE_UTILITY_GAIN = 0.001  # Minimum Pareto improvement
```

### 7.3 Dual Inventory System
```python
# Total bundle for utility calculation
total_bundle = agent.get_total_bundle()  # carrying + home

# But trade execution from carrying only
can_trade = agent.carrying_inventory[good] >= 1
```

## 8. Validation Test Suite

### 8.1 Unit Tests
```python
# tests/validation/test_cobb_douglas_theory.py

def test_marginal_utilities():
    """Verify MU calculations match theory."""
    utility = create_utility_function("cobb_douglas", alpha=0.6, beta=0.4)
    bundle = {"good1": 10, "good2": 10}
    
    # Theoretical MU_x = 0.6 * (10.01)^(-0.4) * (10.01)^0.4
    expected_mu_x = 0.6 * 10.01**(-0.4) * 10.01**0.4
    
    # Calculate via finite difference
    u_base = utility.calculate(bundle)
    bundle["good1"] += 1
    u_plus = utility.calculate(bundle)
    actual_mu_x = u_plus - u_base
    
    assert abs(actual_mu_x - expected_mu_x) < 0.01

def test_switching_distance():
    """Verify distance switching point matches theory."""
    k = 0.15
    bundle = {"good1": 5, "good2": 2}
    utility = create_utility_function("cobb_douglas", alpha=0.5, beta=0.5)
    
    # Calculate MRS
    mrs = (2 + 0.01) / (5 + 0.01)  # Simplified for α=β=0.5
    
    # Theoretical switching distance
    delta_d_star = np.log(1/mrs) / k
    
    # Test via simulation...
```

### 8.2 Integration Tests
```python
# tests/validation/test_cobb_douglas_scenarios.py

def test_pure_preference_revelation():
    """Scenario A: Equal distance resource choice."""
    config = {
        "grid_width": 10,
        "grid_height": 10,
        "agents": [{"utility": "cobb_douglas", "alpha": 0.7, "beta": 0.3}],
        "resources": [
            {"type": "A", "x": 5, "y": 0},  # good1
            {"type": "B", "x": 0, "y": 5},  # good2
        ]
    }
    
    results = run_simulation(config, steps=100)
    
    # Check final ratio
    final_inventory = results.agents[0].get_total_bundle()
    ratio = final_inventory["good2"] / max(final_inventory["good1"], 1)
    expected_ratio = 0.3 / 0.7
    
    assert abs(ratio - expected_ratio) / expected_ratio < 0.1
```

### 8.3 Statistical Validation (R-07)
```python
def test_behavioral_distinctiveness():
    """Verify CD behavior measurably different from PS/PC."""
    # Run 100 simulations for each utility type
    cd_metrics = run_batch("cobb_douglas", n=100)
    ps_metrics = run_batch("perfect_substitutes", n=100) 
    pc_metrics = run_batch("perfect_complements", n=100)
    
    # Test movement entropy
    f_stat, p_value = stats.f_oneway(
        cd_metrics["movement_entropy"],
        ps_metrics["movement_entropy"],
        pc_metrics["movement_entropy"]
    )
    
    assert p_value < 0.05, "Behaviors not statistically distinct"
```

## 9. Metrics and Pass Criteria

### 9.1 Quantitative Metrics
| Metric | Formula | Pass Threshold |
|--------|---------|----------------|
| Bundle Ratio Error | $\|\frac{y/x - \beta/\alpha}{\beta/\alpha}\|$ | < 10% |
| Switching Distance Error | $\|d_{\text{observed}} - d^*\| / d^*$ | < 20% |
| Utility Gain per Step | $\Delta U / \text{steps}$ | > 0 (monotonic) |
| Trade Efficiency | Trades executed / beneficial trades | > 80% |
| Determinism | Hash(seed=X) identical across runs | 100% match |

### 9.2 Qualitative Validation
- Visual inspection via `make visualtest`
- Agents exhibit "balanced shopping" behavior
- Smooth transitions between resource targets
- Willing to trade when imbalanced

## 10. Known Deviations and Limitations

### 10.1 Model Simplifications
1. **No budget constraint**: Agents can collect indefinitely (capacity = 100,000)
2. **No consumption**: Utility over stocks, not flows
3. **Discrete resources**: Integer quantities only (no fractional goods)
4. **Sequential decisions**: Not simultaneous optimization

### 10.2 Implementation Artifacts
1. **Epsilon effects**: At very low inventories, $\varepsilon=0.01$ slightly biases toward balanced collection
2. **Distance discretization**: Manhattan grid creates non-smooth switching boundaries
3. **Perception limits**: Local optimization only (can't see global optimum)

### 10.3 Future Extensions
- Add explicit prices for market equilibrium studies
- Implement consumption with regenerating utility
- Allow fractional trades for smoother convergence
- Add intertemporal optimization with discounting

## 11. References and Links

### 11.1 Theoretical Foundation
- Varian, H. (2014). *Intermediate Microeconomics*, Ch. 4-6 (Utility and Choice)
- MWG (1995). *Microeconomic Theory*, Ch. 3 (Classical Demand Theory)

### 11.2 Spatial Economics
- Fujita & Thisse (2002). *Economics of Agglomeration* (distance costs)
- Hotelling (1929). "Stability in Competition" (spatial models)

### 11.3 Project Documentation
- [`initial_planning.md`](initial_planning.md) - Educational mission and goals
- [`Spatial_Economic_Theory_Framework.md`](tmp_plans/FINAL/Spatial_Economic_Theory_Framework.md) - Comprehensive theory
- [`DEBUG_RECORDING_ARCHITECTURE.md`](tmp_plans/CRITICAL/DEBUG_RECORDING_ARCHITECTURE.md) - Recording system

### 11.4 Implementation Files
- Decision logic: `src/econsim/simulation/agent/unified_decision.py`
- Utility functions: `src/econsim/simulation/agent/utility_functions.py`
- Test suite: `tests/unit/test_trade_economic_coherence.py`

## 12. Validation Checklist

- [ ] Document mathematical model explicitly
- [ ] Derive analytical predictions for simple cases
- [ ] Implement unit tests for marginal utilities
- [ ] Create integration tests for each scenario
- [ ] Verify determinism with recording on/off
- [ ] Run statistical validation (R-07 metric)
- [ ] Visual validation via `make visualtest`
- [ ] Document all deviations from theory
- [ ] Peer review by economics expert
- [ ] Create educator-friendly summary

---

**Document Status**: Draft v2.0  
**Next Review**: After Scenario A implementation  
**Owner**: cmfunderburk  
**Last Updated**: October 2025