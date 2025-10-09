# Single-Agent Utility Maximization in Spatial Grid

**Model Type**: Foundation - Single Agent Utility Demonstration  
**Created**: October 8, 2025  
**Status**: Mathematical Specification (Pre-Implementation)
**Purpose**: Establish spatial-utility relationship through rigorous mathematical foundations

---

## Overview

This document provides the complete mathematical specification for single-agent utility-maximizing behavior in a discrete spatial grid environment. It bridges classical microeconomic theory (utility maximization, marginal utility, indifference curves) with spatial implementation (distance costs, discrete goods, grid-based movement).

**Educational Goal**: Students should be able to predict agent behavior from utility functions alone, understanding how preferences interact with spatial costs.

---

## 0.0 Default Grid Setup for Demonstrations

  - 5x5 grid.
  - Agent spawns at (1,1).
  - Preference parameters are normalized to 1 (alpha + beta = 1).
  - Epsilon is 0.001.
  - Distance discount constant is configurable, default is 0.
  - Perception radius is configurable, default is 8.

---

## 1. Agent Decision Problem (Spatial Context)

### 1.1 State Space

At each discrete timestep $t$, an agent at position $(x_a, y_a)$ observes:

- **Resource locations**: Sets of resources within perception radius $R$
  - Good 1 (Resource A) at positions: $\{(x_i^A, y_i^A)\}_{i=1}^{N_A}$
  - Good 2 (Resource B) at positions: $\{(x_j^B, y_j^B)\}_{j=1}^{N_B}$
  
- **Current inventory bundle**: $(q_1, q_2)$ where:
  - $q_1 = q_1^{\text{carry}} + q_1^{\text{home}}$ (total Good 1)
  - $q_2 = q_2^{\text{carry}} + q_2^{\text{home}}$ (total Good 2)
  
- **Constraints**:
  - Carry capacity: $q_k^{\text{carry}} \leq C_{\text{max}}$ (default: 10 units)
  - Perception radius: $d_{\text{Manhattan}}(\text{agent}, \text{resource}) \leq R$ (default: 8 units)
  - Movement speed: 1 grid cell per timestep (Manhattan distance)

### 1.2 Action Space

Available actions $a \in \mathcal{A}$:

1. **Move**: $(x_a, y_a) \to (x_a + 1, y_a)$ or $(x_a, y_a) \to (x_a, y_a + 1)$
2. **Collect**: Harvest 1 unit of resource at current position (if resource present and resource is current target)
3. **Deposit**: Transfer goods from carry inventory to home storage (if at home and carry inventory is full)
4. **Withdraw**: Transfer goods from home storage to carry inventory (not relevant for pure foraging agents)
5. **Return to/Idle at Home**: If no potential target resource remains in perception radius, return to home, deposit all goods, and wait for new resources to appear

**Note**: Current implementation uses composite actions where "collect" implicitly includes pathfinding to resource location.

### 1.3 Decision Rule (Utility Maximization with Distance Discounting)

The agent chooses action $a^*$ to maximize **distance-discounted marginal utility**:

$$
a^* = \arg\max_{a \in \mathcal{A}} \left\{ \Delta U(a) \cdot \exp(-k \cdot d(a)) \right\}
$$

where:

- $\Delta U(a) = U(q + \Delta q(a)) - U(q)$ is the **marginal utility gain** from action $a$
- $U(\cdot)$ is the agent's utility function (specified below)
- $\Delta q(a)$ is the expected change in bundle from action $a$
- $d(a)$ is the **Manhattan distance** to target location: $d(a) = |x_{\text{target}} - x_a| + |y_{\text{target}} - y_a|$
- $k = 0.15$ is the **distance discount constant** (tuned for educational scenarios)

**Interpretation**: 
- Agent values resources by marginal utility gain
- Distance acts as exponential "friction" reducing value
- At distance $d = 4.6$ units, value is discounted by 50% ($e^{-0.15 \cdot 4.6} \approx 0.5$)
- Beyond perception radius $R = 8$, resources invisible (infinite effective distance)

---

## 2. Utility Functions

All utility functions evaluate the agent's **total bundle** $(q_1, q_2)$, which includes both carrying inventory and home storage.

### 2.1 Cobb-Douglas Utility

$$
U_{\text{CD}}(q_1, q_2) = (q_1 + \varepsilon)^\alpha \cdot (q_2 + \varepsilon)^\beta
$$

**Parameters**:
- $\alpha, \beta > 0$ with $\alpha + \beta = 1$ (normalized preference weights)
- $\varepsilon = 0.001$ (epsilon parameter, prevents divide-by-zero)

**Properties**:
- **Diminishing marginal utility**: More of a good → lower marginal value
- **Complementarity**: Prefers balanced consumption (neither good at zero)
- **Substitutability**: Willing to trade goods at varying rates

**Marginal Utilities**:
$$
MU_1(q_1, q_2) = \frac{\partial U}{\partial q_1} = \alpha \cdot \frac{U(q_1, q_2)}{q_1 + \varepsilon}
$$

$$
MU_2(q_1, q_2) = \frac{\partial U}{\partial q_2} = \beta \cdot \frac{U(q_1, q_2)}{q_2 + \varepsilon}
$$

**Marginal Rate of Substitution (MRS)**:
$$
MRS_{1,2} = \frac{MU_1}{MU_2} = \frac{\alpha}{\beta} \cdot \frac{q_2 + \varepsilon}{q_1 + \varepsilon}
$$

**Behavioral Predictions**:
- High $\alpha$ (e.g., 0.7): Strong preference for Good 1
- Balanced bundle: $\alpha = \beta = 0.5 \Rightarrow$ equal preference at equal quantities
- Low quantities: Epsilon dominates, MRS $\approx \frac{\alpha}{\beta}$
- High quantities: MRS $\approx \frac{\alpha}{\beta} \cdot \frac{q_2}{q_1}$

**Why Epsilon?**: 
- Prevents $MU \to \infty$ as $q_k \to 0$ (mathematical stability)
- Ensures finite marginal values for planning decisions
- Small enough ($0.001$) to not distort preferences at educational scales (typical bundles: 5-20 units)

---

### 2.2 Perfect Substitutes Utility

$$
U_{\text{PS}}(q_1, q_2) = \alpha \cdot q_1 + \beta \cdot q_2
$$

**Parameters**:
- $\alpha, \beta > 0$ (relative values of goods)
- Often normalized: $\alpha + \beta = 1$ (optional)

**Properties**:
- **Linear indifference curves**: Constant tradeoff rate
- **Corner solutions**: May consume only one good
- **No complementarity**: Goods are independent

**Marginal Utilities**:
$$
MU_1(q_1, q_2) = \alpha \quad \text{(constant)}
$$

$$
MU_2(q_1, q_2) = \beta \quad \text{(constant)}
$$

**Marginal Rate of Substitution**:
$$
MRS_{1,2} = \frac{\alpha}{\beta} \quad \text{(constant)}
$$

**Behavioral Predictions**:
- **If $\alpha > \beta$**: Always prefer Good 1 (collect exclusively if distances equal)
- **If $\beta > \alpha$**: Always prefer Good 2 (collect exclusively if distances equal)
- **If $\alpha = \beta$**: Indifferent between goods (distance determines choice)
- **Distance interaction**: With discounting $e^{-k \cdot d}$, closer resource always chosen if $\alpha \approx \beta$

**Educational Use**:
- Simplest case: Demonstrates pure preference without diminishing returns
- Shows role of distance discounting clearly (no bundle-state effects)
- Corner solutions illustrate specialization

---

### 2.3 Perfect Complements (Leontief) Utility

$$
U_{\text{PC}}(q_1, q_2) = \min(\alpha \cdot q_1, \beta \cdot q_2)
$$

**Parameters**:
- $\alpha, \beta > 0$ (required consumption ratios)
- Ratio $\frac{\alpha}{\beta}$ determines optimal bundle proportion

**Properties**:
- **Right-angle indifference curves**: No substitution possible
- **Fixed proportions**: Goods consumed in ratio $\frac{q_1}{q_2} = \frac{\beta}{\alpha}$
- **Waste aversion**: Excess of either good provides zero marginal utility

**Marginal Utilities** (Non-Trivial):

Let $\text{binding} = \arg\min(\alpha \cdot q_1, \beta \cdot q_2)$

$$
MU_1(q_1, q_2) = 
\begin{cases}
\alpha & \text{if } \alpha \cdot q_1 < \beta \cdot q_2 \text{ (Good 1 binding)} \\
0 & \text{if } \alpha \cdot q_1 > \beta \cdot q_2 \text{ (Good 1 in excess)} \\
\text{undefined} & \text{if } \alpha \cdot q_1 = \beta \cdot q_2 \text{ (at kink)}
\end{cases}
$$

$$
MU_2(q_1, q_2) = 
\begin{cases}
\beta & \text{if } \beta \cdot q_2 < \alpha \cdot q_1 \text{ (Good 2 binding)} \\
0 & \text{if } \beta \cdot q_2 > \alpha \cdot q_1 \text{ (Good 2 in excess)} \\
\text{undefined} & \text{if } \beta \cdot q_2 = \alpha \cdot q_1 \text{ (at kink)}
\end{cases}
$$

**Behavioral Predictions**:
- **Balanced bundle** $(\frac{\beta}{\alpha} \cdot q_1 = q_2)$: Agent seeks whichever good is binding
- **Excess of Good 1**: $MU_1 = 0$, agent only collects Good 2
- **Excess of Good 2**: $MU_2 = 0$, agent only collects Good 1
- **Converges to optimal ratio**: Over time, bundle approaches $\frac{q_1}{q_2} = \frac{\beta}{\alpha}$

**Implementation Note** (Current Code: `src/econsim/simulation/agent/utility_functions.py:191`):
```python
class PerfectComplementsUtility(UtilityFunction):
    def marginal_utility(self, bundle, good_name):
        q1, q2 = bundle
        binding = min(self.alpha * q1, self.beta * q2)
        
        if good_name == "good1":
            return self.alpha if (self.alpha * q1 <= binding + 1e-6) else 0.0
        else:  # good_name == "good2"
            return self.beta if (self.beta * q2 <= binding + 1e-6) else 0.0
```

**Educational Use**:
- Demonstrates complementarity: Must consume together
- Shows "waste aversion" behavior (ignoring excess goods)
- Illustrates convergence to optimal proportions

---

## 3. Distance Discounting and Spatial Economics

### 3.1 Exponential Distance Discount

The distance discount factor models **travel cost** as:

$$
\text{discount}(d) = e^{-k \cdot d}
$$

where:
- $d$ = Manhattan distance to target
- $k = 0.15$ (calibrated constant)

**Properties**:
- At $d = 0$: $\text{discount} = 1.0$ (no penalty)
- At $d = 4.6$: $\text{discount} \approx 0.5$ (50% reduction)
- At $d = 8$: $\text{discount} \approx 0.30$ (70% reduction)
- At $d = 15$: $\text{discount} \approx 0.10$ (90% reduction)

### 3.2 Distance-Value Tradeoff

Given two resources at distances $d_A$ and $d_B$ with marginal utilities $MU_A$ and $MU_B$:

**Agent chooses A over B if**:
$$
MU_A \cdot e^{-k \cdot d_A} > MU_B \cdot e^{-k \cdot d_B}
$$

**Critical distance difference** (where preference switches):
$$
d_B - d_A > \frac{1}{k} \ln\left(\frac{MU_A}{MU_B}\right)
$$

**Example**: 
- $MU_A = 2.0$, $MU_B = 1.0$, $k = 0.15$
- Switching point: $d_B - d_A > \frac{1}{0.15} \ln(2) \approx 4.6$ units
- If Good A is 5+ units farther than Good B, agent prefers B despite lower MU

### 3.3 Perception Radius as Information Constraint

Resources beyond perception radius $R$ are **invisible** to the agent:

$$
\text{Visible resources} = \{r \mid d(r, \text{agent}) \leq R\}
$$

**Economic Implications**:
- **Bounded rationality**: Agent cannot optimize over full grid
- **Local optima**: May miss globally better resources
- **Exploration vs exploitation**: Must balance known vs unknown regions

**Default**: $R = 8$ Manhattan units (covers $\approx 200$ grid cells in dense packing)

---

## 4. Analytical Predictions for Validation

### 4.1 Scenario: Equal Distance Choice (Pure Preference Test)

**Setup**:
```python
# Agent configuration
position = (10, 10)
bundle = (5, 5)
utility_function = CobbDouglas(alpha=0.7, beta=0.3)

# Resource configuration
resource_A = (10, 15)  # Distance: 5 Manhattan units
resource_B = (15, 10)  # Distance: 5 Manhattan units
```

**Analytical Calculation**:

1. **Marginal Utilities**:
   - $U(5, 5) = (5.001)^{0.7} \cdot (5.001)^{0.3} = 5.001$ (Cobb-Douglas property)
   - $MU_1 = 0.7 \cdot \frac{5.001}{5.001} = 0.7$
   - $MU_2 = 0.3 \cdot \frac{5.001}{5.001} = 0.3$

2. **Distance-Discounted Values**:
   - $V_A = 0.7 \cdot e^{-0.15 \cdot 5} = 0.7 \cdot 0.472 = 0.330$
   - $V_B = 0.3 \cdot e^{-0.15 \cdot 5} = 0.3 \cdot 0.472 = 0.142$

3. **Prediction**: Agent chooses Resource A (higher discounted value)

**Success Criterion**: Agent moves toward Resource A on next timestep

---

### 4.2 Scenario: Distance-Preference Tradeoff

**Setup**:
```python
# Agent configuration
position = (10, 10)
bundle = (10, 10)
utility_function = CobbDouglas(alpha=0.5, beta=0.5)

# Resource configuration
resource_A = (10, 12)  # Distance: 2 units
resource_B = (10, 10 + d_B)  # Distance: d_B (variable)
```

**Analytical Calculation**:

1. **Marginal Utilities** (balanced bundle):
   - $MU_1 = 0.5 \cdot \frac{U}{10.001} = 0.0499$
   - $MU_2 = 0.5 \cdot \frac{U}{10.001} = 0.0499$
   - Equal marginal utilities → distance determines choice

2. **Switching Point**:
   - Agent switches from A to B when: $e^{-0.15 \cdot 2} = e^{-0.15 \cdot d_B}$
   - Solving: $d_B = 2$ (equal distance → indifferent)
   - For $d_B < 2$: Choose B
   - For $d_B > 2$: Choose A

3. **Distance Sweep Prediction**:

| $d_B$ | $V_A$ | $V_B$ | Choice |
|-------|-------|-------|--------|
| 1     | 0.037 | 0.046 | B      |
| 2     | 0.037 | 0.037 | Tie*   |
| 3     | 0.037 | 0.030 | A      |
| 5     | 0.037 | 0.024 | A      |
| 10    | 0.037 | 0.011 | A      |

*Tie resolved by agent ID (deterministic tiebreaker)

**Success Criterion**: Behavioral transition occurs at predicted distance

---

### 4.3 Scenario: Parameter Sensitivity (Preference Sweep)

**Setup**:
```python
# Agent configuration
position = (10, 10)
bundle = (10, 10)
# Variable: alpha from 0.1 to 0.9 (beta = 1 - alpha)

# Resource configuration (equal distance)
resource_A = (10, 15)  # Distance: 5 units
resource_B = (15, 10)  # Distance: 5 units
```

**Analytical Predictions**:

| $\alpha$ | $MU_1$ | $MU_2$ | $V_A$ | $V_B$ | Choice |
|----------|--------|--------|-------|-------|--------|
| 0.1      | 0.010  | 0.090  | 0.005 | 0.042 | B      |
| 0.3      | 0.030  | 0.070  | 0.014 | 0.033 | B      |
| 0.5      | 0.050  | 0.050  | 0.024 | 0.024 | Tie    |
| 0.7      | 0.070  | 0.030  | 0.033 | 0.014 | A      |
| 0.9      | 0.090  | 0.010  | 0.042 | 0.005 | A      |

Distance discount: $e^{-0.15 \cdot 5} = 0.472$ (constant for both)

**Success Criterion**: 
- Agent transitions from B → A as $\alpha$ increases through 0.5
- Exact switching point at $\alpha = 0.5$ (or deterministic tiebreaker)

---

### 4.4 Scenario: Perfect Substitutes - Corner Solution

**Setup**:
```python
# Agent configuration
position = (10, 10)
bundle = (0, 0)
utility_function = PerfectSubstitutes(alpha=0.8, beta=0.2)

# Resource configuration (equal distance)
resource_A = (10, 15)  # Distance: 5 units
resource_B = (15, 10)  # Distance: 5 units
```

**Analytical Calculation**:

1. **Marginal Utilities** (constant):
   - $MU_1 = 0.8$
   - $MU_2 = 0.2$

2. **Distance-Discounted Values**:
   - $V_A = 0.8 \cdot 0.472 = 0.378$
   - $V_B = 0.2 \cdot 0.472 = 0.094$

3. **Prediction**: Agent exclusively collects Good 1 (4x higher value)

**Long-term Behavior**: 
- Bundle evolves as $(n, 0)$ where $n$ increases over time
- No diminishing returns → never switches to Good 2
- Pure specialization (corner solution)

**Success Criterion**: Agent collects only Good 1 for 100+ timesteps

---

### 4.5 Scenario: Perfect Complements - Ratio Convergence

**Setup**:
```python
# Agent configuration
position = (10, 10)
bundle = (0, 0)
utility_function = PerfectComplements(alpha=1.0, beta=2.0)
# Optimal ratio: q1/q2 = beta/alpha = 2.0 (need 2 units of Good 2 per 1 unit of Good 1)

# Resource configuration (equal distance)
resource_A = (10, 15)  # Distance: 5 units (Good 1)
resource_B = (15, 10)  # Distance: 5 units (Good 2)
```

**Analytical Predictions**:

| Timestep | Bundle $(q_1, q_2)$ | $\alpha q_1$ | $\beta q_2$ | Binding | Next Target |
|----------|---------------------|--------------|-------------|---------|-------------|
| 0        | (0, 0)              | 0            | 0           | Tie     | Either*     |
| 10       | (1, 0)              | 1.0          | 0.0         | Good 2  | B           |
| 20       | (1, 1)              | 1.0          | 2.0         | Good 1  | A           |
| 30       | (2, 1)              | 2.0          | 2.0         | Tie     | Either*     |
| 40       | (2, 2)              | 2.0          | 4.0         | Good 1  | A           |
| 50       | (3, 2)              | 3.0          | 4.0         | Good 1  | A           |
| 60       | (4, 2)              | 4.0          | 4.0         | Tie     | Either*     |

*Tie resolved by deterministic tiebreaker (agent ID or first in sorted list)

**Convergence Property**: 
- Ratio oscillates around $\frac{q_2}{q_1} = 2.0$
- Never deviates more than $\pm 1$ unit from optimal
- Demonstrates self-correcting behavior

**Success Criterion**: After 100 timesteps, ratio within $[1.8, 2.2]$

---

## 5. Implementation Validation Tests

### 5.1 Test Structure

All validation tests should follow this pattern:

```python
# tests/validation/test_single_agent_utility.py

def test_scenario_name():
    """One-line description of economic principle tested"""
    
    # 1. Setup: Create deterministic scenario
    scenario = create_validation_scenario(
        agent_params={"utility_function": ...},
        resource_layout=...,
        seed=42  # Reproducible
    )
    
    # 2. Prediction: Calculate analytical expectation
    expected_action = calculate_analytical_prediction(scenario)
    
    # 3. Execution: Run simulation
    actual_action = scenario.step()
    
    # 4. Validation: Compare with tolerance
    assert actions_match(expected_action, actual_action, tolerance=0.01)
    
    # 5. Documentation: Log for educational use
    log_prediction_vs_actual(scenario, expected_action, actual_action)
```

### 5.2 Required Test Coverage

- [x] **Equal distance choice** (Scenario 4.1)
- [x] **Distance-preference tradeoff** (Scenario 4.2)
- [x] **Parameter sensitivity sweep** (Scenario 4.3)
- [x] **Perfect substitutes corner solution** (Scenario 4.4)
- [x] **Perfect complements ratio convergence** (Scenario 4.5)
- [ ] **Perception radius boundary** (resource just inside/outside radius)
- [ ] **Carry capacity constraint** (agent at max capacity ignores distant resources)
- [ ] **Home deposit behavior** (agent returns home when carry inventory full)

### 5.3 Success Metrics

**Quantitative**:
- 95%+ test scenarios match analytical predictions
- Prediction error < 5% in distance-discounted value calculations
- No divergence from predicted behavior over 1000-step runs

**Qualitative** (Visual Validation):
- Agent trajectories match utility-gradient flow
- Parameter changes produce immediate behavioral response
- Students can predict next action from displayed utility values

---

## 6. Interactive Parameter Manipulation GUI (Phase 1.2)

### 6.1 GUI Components

**Primary Controls** (Real-time adjustment):

1. **Utility Function Selector**:
   - Dropdown: `[Cobb-Douglas | Perfect Substitutes | Perfect Complements]`
   - Updates agent's utility function on change

2. **Preference Parameter Sliders**:
   - **Alpha (α)**: Range `[0.01, 0.99]`, default `0.5`, step `0.01`
   - **Beta (β)**: Auto-calculated as `1 - α` (display only, grayed out)
   - Real-time update on drag (throttled to 100ms)

3. **Distance Discount Slider**:
   - **k**: Range `[0.0, 0.5]`, default `0.15`, step `0.01`
   - Label: "Distance Discount (k)" with tooltip explaining exponential effect

4. **Epsilon Slider** (Advanced):
   - **ε**: Range `[0.001, 0.1]`, default `0.001`, step `0.001`
   - Warning icon: "Changing epsilon affects marginal utility calculations"
   - Collapsible under "Advanced Parameters"

**Visualization Panel** (Read-only displays):

5. **Marginal Utility Display**:
   - Live calculation: $MU_1 = \text{...}$, $MU_2 = \text{...}$
   - Updates every frame based on current bundle

6. **Indifference Curve Overlay** (Grid View):
   - Semi-transparent curves showing utility contours
   - Current bundle position marked
   - Dynamically redrawn on parameter change

7. **Distance-Discounted Value Indicators**:
   - For each visible resource, display:
     - Raw marginal utility: $MU_k$
     - Distance: $d$
     - Discounted value: $MU_k \cdot e^{-k \cdot d}$
   - Visual: Color-coded arrows (green = high value, red = low value)

8. **Predicted Action Arrow**:
   - Large arrow showing analytically predicted next move
   - Color: Blue (prediction) vs Green (actual chosen action)
   - Validation: Arrows should match in 95%+ of cases

### 6.2 GUI Layout (Mockup)

```
┌─────────────────────────────────────────────────────────────┐
│  Single-Agent Utility Demonstration                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌───────────────────────────────┐  ┌──────────────────┐   │
│  │                               │  │ Controls         │   │
│  │                               │  │                  │   │
│  │      Spatial Grid View        │  │ Utility Type:    │   │
│  │                               │  │ [Cobb-Douglas ▼] │   │
│  │  [Agent] [Resources]          │  │                  │   │
│  │                               │  │ Alpha (α): 0.70  │   │
│  │  [Indifference curves]        │  │ ├────●─────┤     │   │
│  │                               │  │                  │   │
│  │  [Predicted action: →]        │  │ Beta (β): 0.30   │   │
│  │  [Actual action: →]           │  │ (auto-calc)      │   │
│  │                               │  │                  │   │
│  └───────────────────────────────┘  │ Distance (k):    │   │
│                                     │ 0.15             │   │
│  ┌───────────────────────────────┐  │ ├────●─────┤     │   │
│  │ Marginal Utility Display      │  │                  │   │
│  │ MU₁ = 0.700 | MU₂ = 0.300     │  │ ▼ Advanced       │   │
│  │                               │  │                  │   │
│  │ Resource A: distance=5        │  │ [Reset] [Export] │   │
│  │   Value = 0.330 🟢            │  └──────────────────┘   │
│  │                               │                         │
│  │ Resource B: distance=5        │                         │
│  │   Value = 0.142 🟡            │                         │
│  └───────────────────────────────┘                         │
└─────────────────────────────────────────────────────────────┘
```

### 6.3 Integration with Existing Codebase

**New Files**:
```
src/econsim/gui/widgets/
├── parameter_controls.py          # Slider controls for utility parameters
├── utility_display.py             # Real-time MU and value calculations
└── indifference_curve_renderer.py # Overlay for grid view
```

**Modified Files**:
```
src/econsim/gui/embedded/realtime_pygame_v2.py
  - Add parameter control panel to sidebar
  - Hook slider updates to agent.utility_function
  - Render prediction vs actual arrows

src/econsim/simulation/agent/core.py
  - Add method: update_utility_function(new_function)
  - Ensure thread-safe parameter updates

visual_test_simple.py
  - Add launch mode: "--interactive-demo"
  - Preload single-agent scenario
```

### 6.4 Technical Specifications

**Update Frequency**:
- Slider changes: Debounced to 100ms (prevent thrashing)
- Display updates: Every frame (30-60 FPS)
- Analytical predictions: Recalculated on parameter change

**Performance Requirements**:
- Slider drag → visual update latency < 100ms
- No dropped frames during parameter adjustment
- Indifference curve rendering: < 10ms per frame

**Data Export**:
- Button: "Export Scenario"
- Generates JSON file with:
  - Agent configuration (utility function, parameters)
  - Resource layout
  - Analytical predictions
  - Actual behavior log
- Used for documentation and test case creation

### 6.5 Educational Workflow

**Intended Use**:

1. **Student loads scenario** (e.g., "Equal Distance Choice")
2. **System displays**:
   - Agent and resources on grid
   - Current utility parameters
   - Predicted next action (blue arrow)
3. **Student adjusts alpha slider** (e.g., 0.7 → 0.3)
4. **System updates in real-time**:
   - Marginal utilities recalculated
   - Predicted arrow changes direction
   - Indifference curves shift
5. **Student clicks "Step"** to see actual behavior
6. **System validates**: Predicted arrow turns green if match, red if mismatch

**Learning Objectives**:
- Understand: Utility parameters determine preferences
- Visualize: Distance costs modify resource values
- Predict: Agent behavior from utility function alone
- Validate: Economic theory matches implementation

---

## 7. Open Questions and Future Extensions

### 7.1 Theoretical Questions

1. **Epsilon Sensitivity**: How does $\varepsilon \in [0.001, 0.1]$ affect long-run behavior? Is there an optimal value?

2. **Distance Discount Calibration**: Is $k = 0.15$ empirically justified? Should it vary by scenario?

3. **Perception Radius Economics**: Can we formalize the "information value" of increased perception radius?

4. **Multi-Good Generalization**: How do formulas extend to 3+ goods? (Future: heterogeneous resources)

### 7.2 Implementation Extensions

1. **Stochastic Utility**: Add noise term $\eta \sim N(0, \sigma^2)$ to model uncertainty

2. **Dynamic Preferences**: Allow $\alpha(t)$ to change over time (e.g., satiation effects)

3. **Risk Aversion**: Incorporate utility curvature into distance discounting

4. **Spatial Heterogeneity**: Variable $k$ by terrain type (e.g., rough terrain = higher k)

### 7.3 Validation Enhancements

1. **Continuous Movement**: Currently discrete grid; extend to sub-cell positioning?

2. **Partial Resource Collection**: Allow fractional unit collection (currently integer-only)

3. **Dynamic Resource Respawn**: Reappearing resources during simulation

4. **Multi-Agent Crowding**: Resource contention (blocked by other agents)

---

## 8. References and Further Reading

**Classical Microeconomic Theory**:
- Mas-Colell, Whinston, Green (1995): *Microeconomic Theory* - Chapters 1-3 (Utility, Consumer Choice)
- Varian (2014): *Intermediate Microeconomics* - Chapters 3-5 (Preferences, Utility, Choice)

**Spatial Economics**:
- Fujita, Krugman, Venables (1999): *The Spatial Economy* - Chapter 2 (Distance and Trade)
- von Thünen (1826): *The Isolated State* - Original spatial cost model

**Computational Economics**:
- Tesfatsion, Judd (2006): *Handbook of Computational Economics* - Agent-based modeling
- Shoham, Leyton-Brown (2008): *Multiagent Systems* - Decision-making in spatial environments

**Implementation References**:
- Current codebase: `src/econsim/simulation/agent/utility_functions.py` (Lines 95, 148, 191)
- Decision logic: `src/econsim/simulation/agent/unified_decision.py` (Line 1130)
- Distance calculations: `src/econsim/simulation/world/spatial.py` (AgentSpatialGrid)

---

## 9. Validation Checklist

Before proceeding to Phase 1.2 GUI implementation:

- [ ] Mathematical specifications reviewed by economics expert
- [ ] All analytical predictions computed and documented
- [ ] Epsilon value ($\varepsilon = 0.001$) justified in context of typical bundle sizes
- [ ] Distance discount constant ($k = 0.15$) validated against educational scenarios
- [ ] Test scenarios (4.1-4.5) implemented and passing
- [ ] Edge cases identified and handled (zero quantities, perception boundaries, etc.)
- [ ] Documentation accessible to non-experts (educational goal)

---

**Document Status**: ✅ Complete (Phase 1.1)  
**Next Phase**: Implement interactive GUI (Phase 1.2) and validation tests (Phase 1.3)  
**Owner**: VMT Development Team  
**Last Updated**: October 8, 2025
