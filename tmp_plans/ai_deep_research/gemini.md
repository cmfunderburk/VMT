# Spatial Microeconomics Platform — Final, Comprehensive Implementation Plan

*(Foundational → Advanced; theory-first, visualization-first; designed to resolve all gaps flagged in your two review files while aligning with your mission statement.)*

---

## 0) North-Star & Guardrails

**North-Star:** Immediate, visual demonstrations of *preference relations ⇄ choice functions ⇄ utility representations* on an NxN grid, then systematic ascent through consumer theory, exchange, search, information economics, game theory, GE, and mechanism design—always with spatial frictions, dashboards, and testable claims.

**Pedagogical guardrails**

* Every feature has: (a) a crisp economic statement, (b) a visible spatial manifestation, (c) a statistic/plot that confirms the statement.
* Prefer the **dual** (preferences/choice) first; utility representations are *derived* (Afriat, Debreu) and kept honest via revealed-preference tests.

**Engineering guardrails**

* Single source of truth for units/topology; one pathfinding oracle; one action-valuation interface; explicit update/collision policy; reproducible scenarios; deterministic seeds.

---

## 1) Platform Skeleton & “Coupling Contract”

*(Addresses: missing spatial-economic coupling; units; topology; Manhattan vs shortest-path; undefined update order; inconsistent visibility; absent analytics.)*

### 1.1 Coupling Contract (write first; ~1–2 pp)

**Deliverable:** `docs/spatial_econ_coupling.md` mapping **State → Decision → Movement → Outcome → Logging** with units.

* **State (with units):**
  Grid cell = `CELL_SIZE` (m), step = `STEP_DURATION` (s), topology = {bounded|torus}. Obstacles set `Ω_wall`. Resources: stock/respawn τ (steps). Agents: preferences/choice rules; perception policy; inventory vector.
* **Decision:** argmax over actions with **travel-time-adjusted ΔU**.
* **Movement:** `find_path()` returns geodesic length L (steps); `next_step_toward()` is the sole move oracle.
* **Outcome:** new position; trade executed? resource collected?
* **Logging:** per-cell visits, extractions, trade events; per-tick utilities; welfare; Gini; encounter distances; path optimality.

### 1.2 Units, Topology, and Oracles (code)

* `simulation/constants.py`: `CELL_SIZE`, `STEP_DURATION`, `DISTANCE_DISCOUNT_PER_SECOND`, `TOPOLOGY`.
* Distance cost: **exponential in travel time**: multiply payoffs by `exp(-ρ * L * STEP_DURATION)`. Calibrate ρ to time preference; see §8 references.
* **Pathfinding & LOS:** One grid graph for (a) shortest paths (movement) and (b) perception (graph radius or line-of-sight). No Manhattan in valuation.
* **Update Order:** Two-phase tick (decide → resolve), with **per-tick shuffled agent order** to avoid bias; agents are non-blocking (can co-locate) but resource claims are atomic.

### 1.3 Spatial Analytics & Dashboards (MVP)

* Heatmaps: cell visits, extractions, trades.
* Curves: encounter counts by distance (spatial decay); welfare over time; Gini over time; path-optimality rate; unreachable-target rate.
* Scenario metadata: seed, params, commit hash.

**Acceptance tests (foundational)**

* With a wall inserted, valuation flips to nearer reachable target; unreachable targets never chosen.
* Encounter distance histogram decays with distance; path-optimality ~100%; unreachable-target rate = 0.

---

## 2) Preferences ⇄ Choices ⇄ Utilities (Dual Foundations)

*(Addresses: educational baseline; consistency between theory and code.)*

### 2.1 Preference & Choice Primitives

* **Preference object** `≽`: complete, transitive, continuous assumptions flagged explicitly (or relaxed scenario variants).
* **Choice correspondence** `C(B)` from feasible sets B observed on the grid (menus are spatial: “what’s reachable within r or L steps?”).
* **Utility representation** only when warranted by axioms (Debreu). Keep an option to run **utility-free** modules (revealed-preference focus).

### 2.2 Classroom-ready demos

* **Revealed preference on a grid:** show WARP/SARP tests pass/fail from observed choices as visibility/menus change.
* **Afriat theorem demo:** recover a utility rationalizing observed choice data; display one level set overlay on the grid.

**Acceptance tests**

* Synthetic choice data constructed to satisfy WARP is rationalizable; violating dataset fails reconstruction (expected).

**Key references:** Mas-Colell et al., Ch. 1–3; Varian *Microeconomic Analysis* Ch. 1–2; Afriat (1967), Debreu (1954).

---

## 3) Spatial Foraging: Travel-Time-Adjusted Choice

*(Addresses: inconsistent distance costs; composite action stub.)*

### 3.1 Action-valuation interface (single choke point)

`estimate_value(agent, action)` returns expected ΔU:

* **Forage(resource r):** `u(consumption|r) * exp(-ρ·L_r·Δt)`, optionally downweight by competition risk π_losing(r).
* **Explore:** expected value of information (EVI) proxy; tunable.
* **Idle/return-home:** baseline (for opportunity-cost comparisons).
* **Trade(partner p):** see §4.

### 3.2 Options for distance frictions

* **A. Exponential (default):** memoryless, composable over paths. *Pros:* tractable; aligns with time discounting. *Cons:* may over-penalize long but high-value trips.
* **B. Linear:** cost = κ·L. *Pros:* transparent. *Cons:* can violate intertemporal consistency.
* **C. Hyperbolic:** stronger near-field sensitivity. *Pros:* captures present-bias. *Cons:* dynamic inconsistency (advanced module).

**Recommendation:** A as default; expose B/C as toggles for pedagogy.

**Acceptance tests**

* Switch-point demo: a far, high-value resource vs a near, low-value resource—observed threshold matches theoretical inequality.

**Key references:** Exponential discounting (Samuelson); spatial decay empirics (gravity models).

---

## 4) Exchange in Space: Rendezvous, Protocols, and Efficiency

*(Addresses: “co-located only” assumption; rendezvous undefined; sequencing/conflicts.)*

### 4.1 Rendezvous mechanics

* New action: `move_to_trade(partner, meet_point)`.
* **Meet point rules (options):** midpoint on geodesic; nearest feasible to midpoint; one-sided travel (one agent waits).

  * *Midpoint pros:* fairness; symmetric travel. *Cons:* extra coordination.
  * *One-sided pros:* simplest. *Cons:* asymmetric burden.

**Recommendation:** start with **one-sided** (initiator travels), add midpoint later as toggle. Include **timeout** and **busy/commit** states.

### 4.2 Trade protocol (conflict resolution)

* **Baseline:** first-come-first-served (by arrival or random tie-break).
* **Advanced toggles:** surplus auction (highest ΔW wins); random matching; serial dictatorship.

**Pros/Cons (education):** FCFS shows frictions; auctions teach surplus maximization & thickness.

### 4.3 Surplus & stopping rule

* Two-good exchange: execute trade until **MRS_i ≈ MRS_j** (contract curve); log ΔU_i, ΔU_j, ΔW.
* Risk/failure: success probability `Pr(success|L)=exp(-λL)` discounting expected surplus.

**Acceptance tests**

* Two-agent Edgeworth demo: trades stop near contract curve; further marginal trade fails Pareto test.
* Three-agent congestion test: FCFS vs auction changes who trades first and aggregate surplus as expected.

**Key references:** Edgeworth box, contract curve; Nash bargaining (for equal-split heuristic); search & matching (Diamond-Mortensen-Pissarides) for meeting frictions.

---

## 5) Information & Perception (Endogenous or Exogenous)

*(Addresses: binary radius; occlusion; search cost.)*

### 5.1 Visibility policy

* **Graph-radius r with LOS** (default): BFS up to cost r; walls occlude.
* Mark items `{visible, reachable}`; valuation excludes unreachable by default.

### 5.2 Endogenous search (advanced toggle)

* Choose r* = argmax E[V(r)] − cost(r).

  * **Heuristic:** if best option < threshold, increase r next tick; nominal search cost = fraction of a step.

**Pros/Cons:** Great for information economics modules; skip by default for early lessons.

**Acceptance tests**

* Wall occlusion unit: behind-wall resources not “seen.”
* Endogenous search expands radius when local options poor; shrinks otherwise.

**Key references:** Stigler (1961) economics of information; rational inattention (Sims).

---

## 6) Resource Processes & Renewable Dynamics

*(Addresses: unspecified spawn/respawn semantics; units.)*

### 6.1 Spatial distributions (configurable)

* **IID uniform** (MVP), **clustered (Neyman-Scott)**, or **fixed patches**. Parameters have units: density per cell, cluster size.

### 6.2 Renewal timing

* **In-place respawn** after τ steps (deterministic) or geometric with mean τ (stochastic). Units: steps = Δt · seconds.

### 6.3 Optional renewable micro-policy

* Rule of thumb: harvest if `MU_now > δ·E[MU_future]·P(available)`; use to craft **commons** demonstrations.

**Acceptance tests**

* Measured harvest rate ≈ capacity under saturation; commons scenario shows over-extraction without governance.

**Key references:** Clark (bioeconomic harvesting), common-pool resources (Ostrom).

---

## 7) Update Order, Concurrency, and Collisions

*(Addresses: unspecified executor policy; spatial bias.)*

* **Two-phase tick:** decide → resolve with randomized order.
* Agents pass through; resource claims are atomic at resolution stage; ties broken randomly.
* Busy flags prevent double commitments; rendezvous timeouts free agents.

**Acceptance tests**

* Race to single resource splits wins ~50/50 over many runs; no systematic bias by agent id or position.

---

## 8) Composite Policy: Complete `_estimate_action_value`

*(Addresses: stubbed composite valuation; local-vs-global myopia.)*

* Compare **Forage**, **Trade**, **Explore**, **Idle/Return** using the unified formula (Sections 3–5).
* Optional **opportunity-cost proxy**: typical forage ΔU per step × travel time, to downweight long trips.
* Debug logging: show option list with ΔU components to support classroom “why did it do that?” discussions.

**Acceptance tests**

* Choice reversals occur at predicted parameter thresholds (ρ, τ, r, density).

---

## 9) Tests & Validation Suite (Economic + Spatial)

*(Addresses: missing equilibrium tests; welfare metrics absent.)*

### 9.1 Economic correctness

* `test_edgeworth_convergence.py`: MRS equalization; no Pareto-improving trades remain.
* `test_spatial_foraging_equilibrium.py`: no profitable relocation given distance costs.
* `test_revealed_preference.py`: WARP/SARP pass/fail as constructed.

### 9.2 Spatial mechanics

* `test_path_vs_valuation.py`: valuation uses geodesic length; path optimality 100%.
* `test_occlusion.py`: visibility respects walls.
* `test_executor_fairness.py`: race fairness Monte Carlo.

### 9.3 Welfare & dashboards

* Utilitarian welfare ↑ when exchange enabled; Gini reacts in expected direction for inequity scenarios; encounter-distance curve decays.

---

## 10) Documentation & Pedagogical Scaffolding

*(Addresses: theory docs; parameter meaning; scenario clarity.)*

* **Theory notes per module** (`docs/modules/*`): equations, assumptions, predictions, limitations, references.
* **Instructor notes**: learning objectives, knobs to turn, expected plots & interpretations.
* **Scenario notebooks**: “Revealed Preference 101,” “Edgeworth in Space,” “Search & Rendezvous,” “Commons.”

---

## 11) Advanced Roadmap (toggleable modules)

1. **General Equilibrium (GE) on a grid**

   * Walrasian tâtonnement visualization for small exchange economies; excess demand heatmaps.
   * References: Mas-Colell; Arrow–Debreu; Scarf algorithms.

2. **Discrete Choice & Demand Estimation**

   * Random utility (McFadden); Hotelling line / Salop circle spatial competition overlays.
   * References: McFadden (1974); Hotelling (1929); Salop (1979).

3. **Game Theory & Strategic Movement**

   * Potential games on grids; congestion games; best-response dynamics movies.
   * References: Osborne–Rubinstein.

4. **Search & Matching Markets**

   * Directed vs random search; market thickness; vacancy/meeting rates; rendezvous as matching technology.
   * References: Diamond–Mortensen–Pissarides.

5. **Mechanism Design & Auctions**

   * Single-item and double auctions on a map; VCG-style demonstrations (small, didactic).
   * References: Myerson; Vickrey–Clarke–Groves.

---

## 12) Gap-by-Gap Fixes (from your two reviews) — with Alternatives

| Gap / Inconsistency                         | Recommended Solution(s)                                                              | Alternatives (Pros/Cons)                                      |
| ------------------------------------------- | ------------------------------------------------------------------------------------ | ------------------------------------------------------------- |
| Spatial–economic coupling implicit          | **Coupling Contract**, unitized constants, single movement oracle, unified valuation | None (this is required)                                       |
| Distance cost inconsistent / Manhattan used | Replace with **shortest-path travel-time discount**                                  | Linear/hyperbolic discount (pedagogy toggles)                 |
| Exchange mobility undefined                 | **Rendezvous action**, commit/timeout, travel-adjusted ΔU                            | Teleport-trade (only for basic demos; mark as simplification) |
| Partner conflicts / sequencing              | FCFS baseline; add **auction** toggle; busy/commit flags                             | Random matching (simpler, less efficient pedagogy)            |
| Perception radius naïve                     | Graph-radius with **LOS**; unreachable flagged/excluded                              | Omniscient radius (only for beginner demos)                   |
| Resource spawn/respawn vague                | IID/clustered presets; τ in steps; in-place respawn default                          | Mobile respawn elsewhere (harder to reason pedagogically)     |
| Update order / collisions                   | Two-phase with shuffle; atomic claims; unit tests                                    | Fully simultaneous w/ complex resolution (overkill early)     |
| Composite valuation stub                    | Complete `_estimate_action_value` using unified ΔU                                   | Policy-gradient/RL later (research mode)                      |
| Missing spatial analytics                   | Heatmaps, decay curves, welfare & Gini, path optimality                              | —                                                             |
| Missing equilibrium/welfare tests           | Edgeworth & spatial equilibrium tests; Pareto checks; welfare suite                  | —                                                             |

---

## 13) Milestoned Build Plan (Foundational → Advanced)

**Milestone A (Foundations, 1–2 sprints)**
A1 Coupling Contract doc + constants/units/topology
A2 Pathfinding & LOS unified; Manhattan removed from valuation
A3 Two-phase executor + fairness & collision policy
A4 Analytics MVP (heatmaps, path-optimality, encounter decay)
A5 Tests: path/valuation, occlusion, executor fairness

**Milestone B (Core Econ Behaviors, 2 sprints)**
B1 Preference/choice primitives + revealed-preference demos
B2 Foraging with travel-time discount + composite valuation completed
B3 Rendezvous & FCFS trade protocol; Edgeworth stopping rule
B4 Welfare & Gini metrics; Edgeworth equilibrium tests

**Milestone C (World Dynamics & Information, 1–2 sprints)**
C1 Resource distributions & respawn semantics (τ)
C2 Optional endogenous perception (toggle)
C3 Commons demo scenario; sensitivity dashboards

**Milestone D (Pedagogy & Docs, 1 sprint)**
D1 Theory notes per module with references
D2 Instructor scenarios & notebooks
D3 Trace logging for “why did it do that?” explanations

**Milestone E (Advanced toggles, ongoing)**
Auctions toggle; Hotelling/Salop overlays; GE mini-module; search/matching switches

---

## 14) Success Criteria (Go/No-Go)

* **Economic:** In Edgeworth demos, trades cease with |MRS_i − MRS_j| < ε; exchange raises utilitarian welfare; spatial foraging shows no profitable deviation given costs.
* **Spatial:** Encounter distances show decay; path optimality ~100%; unreachable-target attempts = 0.
* **Pedagogical:** Instructors can (a) predict outcomes from parameters, (b) point to dashboard evidence within 60 seconds, (c) toggle simplifications for different levels.
* **Engineering:** All tests green; deterministic seeds; scenarios reproducible; params unit-documented.

---

## 15) Targeted Bibliography (for in-code and doc references)

* **Core Micro / Preferences & Choice:** Mas-Colell, Whinston & Green (1995) *Microeconomic Theory*; Varian (1992) *Microeconomic Analysis*; Kreps (2013) *Microeconomic Foundations I*.
* **Revealed Preference & Utility Representation:** Afriat (1967) “The Construction of Utility Functions”; Debreu (1954) “Representation of a Preference Ordering.”
* **Consumer/Exchange:** Edgeworth box & contract curve (standard texts); Nash bargaining (1950).
* **Information & Search:** Stigler (1961) “Economics of Information”; Sims (2003) Rational Inattention; Diamond (1982), Mortensen & Pissarides (1994) matching/search.
* **Spatial Economics & IO:** Hotelling (1929) line; Salop (1979) circle; McFadden (1974) discrete choice; Berry-Levinsohn-Pakes (1995) demand.
* **Renewable Resources & Commons:** Clark (1990) *Mathematical Bioeconomics*; Ostrom (1990) *Governing the Commons*.
* **General Equilibrium:** Arrow–Debreu (1954); Scarf algorithms for tâtonnement.

---

### Final Notes

* Wherever I proposed a **new abstraction** (rendezvous, auctions toggle, endogenous perception), I included the necessity (to align spatial reality with theory), **pros/cons**, and a default (simple, teachable) baseline.
* The plan is deliberately **theory-first** (dual framework), **spatially coherent** (one oracle and unit system), and **dashboard-backed** so learners see every claim in the data.
* If you want, I can turn sections 1.1, 3.1, 4.1–4.3, and 9 into ready-to-drop Markdown files and test stubs next.
