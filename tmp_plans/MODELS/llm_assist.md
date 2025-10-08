# Economic Model: Cobb‑Douglas (spatial)

## 1. Utility specification
- Utility over discrete bundles (stocks):  
  $$
  U(x,y) = (x + \varepsilon)^{\alpha} (y + \varepsilon)^{\beta},\qquad \alpha,\beta>0
  $$
  with $\varepsilon=0.01$ (bootstrap), typically $\alpha+\beta=1$.

## 2. Distance discounting (implemented)
- Effective utility when acquiring a resource at distance $d$ uses exponential discount:
  $$
  U_{\text{disc}} = U \cdot e^{-k d}
  $$
  Decision rule (marginal utility per unit, distance discounted):
  $$
  \text{Choose good }x\ \text{if}\quad MU_x \, e^{-k d_x} \;>\; MU_y \, e^{-k d_y}
  $$
  where
  $$
  MU_x = \frac{\partial U}{\partial x} = \alpha (x+\varepsilon)^{\alpha-1}(y+\varepsilon)^{\beta}.
  $$

## 3. Switching / indifference distance
- Solve for $\Delta d^{*} = d_x - d_y \quad\text{(indifference)}$:
  $$
  \Delta d^{*} = \frac{1}{k}\ln\!\left(\frac{MU_x}{MU_y}\right)
  $$

## 4. Decision problem (algorithmic mapping)
- At each step agent:
  1. Reads total bundle = `carrying + home` (see [`Agent.get_total_bundle()`](/src/econsim/simulation/agent/core.py) in code).  
  2. Enumerates visible resources via spatial grid (use `AgentSpatialGrid` in [src/econsim/simulation/world/spatial.py](src/econsim/simulation/world/spatial.py)).  
  3. Computes distance‑discounted MU for each candidate and picks max. (Implemented in [`make_agent_decision`](src/econsim/simulation/agent/unified_decision.py).)  
- Determinism: sort candidates and tiebreak on lowest `agent.id` per project rules.

## 5. Validation scenarios (minimal)
- Scenario A — Equal distance, different α: place two resources at equal distance. Prediction: collect in proportion $\alpha:\beta$ over many picks.
- Scenario B — Distance tradeoff: preferred good further away. Compute $\Delta d^{*}$ and verify switch occurs near predicted differential.
- Scenario C — Foraging + trade: two agents swapped imbalanced bundles within perception radius; verify Pareto‑improving 1‑for‑1 trades per code (`unified_decision.py: trade evaluation`).

## 6. Metrics & pass criteria
- Bundle ratio error: $|\,\frac{y}{x}-\frac{\beta}{\alpha}\,|$ within tolerance (e.g., 10%).
- Switching step error: observed switch within ±5 steps of analytic $\Delta d^{*}$ prediction.
- Determinism: same seed + recording off/on produces identical traces (see debug recorder docs in `tmp_plans/CRITICAL/DEBUG_RECORDING_ARCHITECTURE.md`).

## 7. Mapping to code
- Decision engine: [`make_agent_decision`](src/econsim/simulation/agent/unified_decision.py)  
- Utility factory: [`create_utility_function`](src/econsim/simulation/agent/utility_functions.py)  
- Two‑phase execution: [`UnifiedStepExecutor`](src/econsim/simulation/executor.py)  
- Use `visual_test_simple.py` and `make visualtest` to visually validate behavior.

## 8. Small checklist to implement tests
- [ ] Add unit test that computes MU_x and MU_y formulas and verifies sign/direction for sample bundles.  
- [ ] Create controlled scenario files (single agent, two resources) and an integration test under `tests/validation/`.  
- [ ] Add analytic expectation assertions and run `make test-unit`.
