EconSim VMT — Model Inventory and Validation Guide (2025‑10‑08)

Purpose

- Provide a clear inventory of implemented models and mechanisms in the current codebase.
- Highlight behavioral implications and gaps vs. canonical economic models.
- Propose concrete, formal economic models to write down and use as validation baselines for
  simulations.

Scope Summary

- Micro focus: two goods, utility‑maximizing agents, spatial grid, bilateral 1‑for‑1 barter,
  deterministic execution.
- Key modules referenced:
  - Utility functions: src/econsim/simulation/agent/utility_functions.py:50
  - Decision engine: src/econsim/simulation/agent/unified_decision.py:1
  - Agent core: src/econsim/simulation/agent/core.py:27
  - Step executor (two‑phase): src/econsim/simulation/executor.py:35
  - Grid world (resources): src/econsim/simulation/world/grid.py:1
  - Features/flags: src/econsim/simulation/features.py:34
  - Coordinator/factory: src/econsim/simulation/coordinator.py:43

Current Implementations (What exists today)

- Utility functions (pluggable, factory pattern)
  - Cobb‑Douglas U = (x+ε)^α (y+ε)^β with α∈(0,1), α+β=1; ε=0.01 for zero bootstrap.
    - Class: src/econsim/simulation/agent/utility_functions.py:95
  - Perfect Substitutes U = αx + βy, α,β>0.
    - Class: src/econsim/simulation/agent/utility_functions.py:148
  - Perfect Complements (Leontief) U = min(αx, βy), α,β>0.
    - Class: src/econsim/simulation/agent/utility_functions.py:191
  - Factory creator: `create_utility_function(type, **kwargs)`
    - src/econsim/simulation/agent/utility_functions.py:336
- Spatial cost integration
  - Distance discount applied to marginal utility for resource targeting: net = ΔU · exp(−k·d)
    - Function: `apply_distance_discount` (k=0.15 constant),
      src/econsim/simulation/agent/utility_functions.py:420
    - Perception radius: 8 Manhattan steps, src/econsim/simulation/agent/utility_functions.py:46
- Agent architecture
  - Dual inventory: carrying + home; utility computed on total bundle (carrying+home).
    - Methods: `deposit_to_home`, `withdraw_from_home` (single‑agent ops)
      - src/econsim/simulation/agent/core.py:121, src/econsim/simulation/agent/core.py:161
  - Mode and targeting fields; trading partner pointer.
    - Dataclass: src/econsim/simulation/agent/core.py:27
  - Carrying capacity: 100,000 (effectively unconstrained),
    src/econsim/simulation/agent/utility_functions.py:47
- Decision engine (deterministic, two‑phase via executor)
  - Entrypoint: `make_agent_decision` selects among forage, trade, dual, idle.
    - src/econsim/simulation/agent/unified_decision.py:1076
  - Foraging: choose resource with max distance‑discounted marginal utility; collect if co‑located.
    - `_find_best_resource`: src/econsim/simulation/agent/unified_decision.py:609
  - Bilateral exchange: partner seek/maintain; evaluate Pareto‑improving 1‑for‑1 swaps using total
    bundle.
    - `find_beneficial_bilateral_trade`: src/econsim/simulation/agent/unified_decision.py:255
    - Utility delta from hypothesized trade uses total bundle (carrying+home):
      `_calculate_trade_utility_gain`.
  - Pairing/unpairing and move‑toward logic (with co‑movement of partners in executor).
- Executor (two‑phase execution)
  - Phase 1: collect decisions; Phase 2: execute special actions (`collect`, `trade`, `pair`,
    `unpair`).
    - src/econsim/simulation/executor.py:74
  - Movement: Manhattan for solo; coordinated convergence for paired agents.
    - src/econsim/simulation/executor.py:230
  - Trade execution: atomic swap of carrying inventories; executes only once via lower‑ID rule.
    - src/econsim/simulation/executor.py:240
- World and resources
  - Grid stores single resource per cell; type is string; deterministic iteration provided.
    - src/econsim/simulation/world/grid.py:1
  - Decision’s `ResourceInfo.from_resource` maps type "A"→good1, else→good2.
    - src/econsim/simulation/agent/unified_decision.py:81
- Feature flags (env‑driven)
  - `ECONSIM_FORAGE_ENABLED`, `ECONSIM_TRADE_DRAFT`, `ECONSIM_TRADE_EXEC`.
    - src/econsim/simulation/features.py:34

Key Behavioral Notes (How it behaves)

- Determinism
  - Fixed seed usage; sorted perception results; lower‑ID tiebreaks in movement/trade/pairing.
- Utility evaluation domain
  - Utility and trade evaluation use total bundle (carrying+home). Execution constraints apply to
    carrying only.
- Foraging priority
  - Dual mode prioritizes: deposit if full and at home → return to deposit if full → maintain
    partnership and trade if possible → forage best net‑utility resource → speculative withdraw to
    enable trade → fallbacks.
  - Carrying capacity is effectively non‑binding; distance discount and perception drive choices.
- Trade structure
  - 1‑for‑1 barter only. Trade accepted if both agents get ΔU > min threshold (1e‑5) under their own
    preferences, computed against total bundles.
  - Implies implicit fixed relative price p2/p1 = 1; no negotiation, no multi‑unit trades, no price
    system.
- Movement
  - Manhattan movement; special pairing movement tries to converge partners quickly (coordinated
    step selection).

Differences vs Canonical Economic Models (Gaps to keep in mind)

- No prices or budgets
  - Current system is pure barter with 1:1 exchange; there is no Walrasian tatonnement, no price
    vectors, no budget sets.
- No consumption timing
  - Utility is computed on stock (carrying+home). There is no per‑period consumption choice; no
    intertemporal utility or discounting; inventory is a direct source of utility.
- Spatial frictions folded into utility heuristics
  - Distance enters as multiplicative exponential discount on marginal utility of a target
    (resembling travel cost), not as an explicit constraint set or cost function in a formal
    optimization.
- Perception‑limited information
  - Agents see only within radius 8; canonical models often assume full information (unless
    explicitly modeling search).
- Discrete, binary resources and effectively unbounded carrying
  - Canonical consumer theory typically works with continuous bundles and budget constraints; here,
    resources are discrete pickups and capacity is effectively infinite.
- Type mapping ambiguity
  - `ResourceInfo.from_resource` treats any non‑"A" cell as good2. Tests sometimes use types like
    "food"/"wood". For foraging scenarios, stick to "A"/"B" or ensure mapping is explicit.
- Distance factor configurability
  - Config exposes `distance_scaling_factor`, but decision logic uses a fixed 0.15
    `DISTANCE_DISCOUNT_FACTOR` constant. Aligning these would improve theoretical control for
    validation.

What to Validate Against (Explicit economic models to write down)

1. Single‑Agent Foraging with No Spatial Cost (k=0)

- Model: Static utility accumulation with utility function U(x,y). At each step choose which good to
  increment by 1 to maximize ΔU. No budget; stock utility.
- Formalization:
  - State s_t = (x_t, y_t). Choice c_t ∈ {collect good1, collect good2, idle}.
  - Transition: s\_{t+1} = s_t + e_i for chosen i.
  - Objective (myopic): choose i maximizing MU_i(s_t) = U(s_t + e_i) − U(s_t).
- Predictions:
  - Cobb‑Douglas: tends to balance toward α:β proportions (x:y ≈ β:α) in the long run.
  - Perfect Substitutes: always take the higher α vs β good.
  - Perfect Complements: collect to equalize αx ≈ βy; excess of either has no marginal value when
    min() binds.
- Validation metrics:
  - Directional error of chosen good vs. argmax MU_i.
  - Bundle ratio error to target ratio (CD: y/x vs β/α; PC: |αx − βy|).

2. Single‑Agent Foraging with Spatial Cost (k>0)

- Model: Same as above but net marginal utility includes travel cost via exponential discount:
  net_i(d) = MU_i · exp(−k·d_i).
- Formalization:
  - As above, with distance d_i to nearest available unit of good i.
  - Choose argmax_i net_i(d_i).
- Predictions:
  - Larger k shifts choices toward closer resources even when MU is smaller; high k can reverse
    preferences vs. MU alone.
- Validation metrics:
  - Net MU argmax agreement rate.
  - Sensitivity curves: vary k and measure switching thresholds where choices flip.

3. Two‑Agent Exchange on Edgeworth Box with Fixed Price Ratio 1

- Model: Two‑good, two‑agent pure exchange economy with fixed price ratio p2/p1=1 (equivalent to
  1‑for‑1 barter). Agents accept a one‑unit swap if both have ΔU>0 at current bundles.
- Formalization:
  - Trade feasibility condition matches MRS bracket: MRS_A > 1 > MRS_B at current bundles.
    - Cobb‑Douglas MRS_i = (α_i/β_i)·(y_i/x_i).
    - Perfect Substitutes MRS is constant α/β (trade possible only if constants straddle 1;
      quantities don’t matter).
    - Perfect Complements: MRS undefined at the kink; effectively only trades reducing |αx − βy| are
      beneficial.
  - Trade proceeds along the 45° direction in the Edgeworth box (due to 1:1 units) until no more
    mutually beneficial swaps exist or constraints bind.
- Predictions:
  - CD/CD: Converge to a neighborhood where both agents’ MRS ≈ 1 (within discretization), subject to
    endowment and integer constraints.
  - CD/PS: If PS has α/β>1 while CD’s MRS\<1 at endowment, trades flow from CD’s good2 to PS’s good1
    until one side’s carrying/home constraints or discreteness block further gains.
  - PS/PS: Trade only if α/β ratios differ across agents and straddle 1; otherwise indifference → no
    trade.
  - PC/\*: Trades that move bundles toward αx=βy are beneficial for the PC agent; mutual gain
    depends on the other’s preferences.
- Validation metrics:
  - Check ΔU>0 for both parties on executed trades (should always hold by construction).
  - Track MRS_A and MRS_B sign conditions at execution; verify bracket condition frequency.
  - Distance (in L1 steps) from contract‑curve neighborhood under CD/CD with 1:1 price; expect
    approach within a tolerance band dictated by discretization.

4. Mixed Mode (Forage + Trade)

- Model: Forage generates stochastic endowments given spatial layout; then 1:1 exchange re‑allocates
  locally when mutually beneficial.
- Formalization:
  - Alternate steps of resource acquisition and occasional pair/meeting/trade sequences; no
    intertemporal consumption.
- Predictions:
  - For balanced CD agents, home+carrying bundles tend to align with their α:β proportions, with
    exchanges smoothing imbalances induced by uneven resource availability.
- Validation metrics:
  - Post‑trade bundle ratios vs. α:β target across agents.
  - Share of idled steps due to no nearby partners vs. perception limits.

How to Map Simulation Variables to Economic Variables

- Goods: `good1` ↔ x, `good2` ↔ y (Agent total bundle = carrying + home).
- Spatial cost: approximate as per‑unit travel disutility c(d) with net marginal benefit MU_i ·
  exp(−k·d). For k=0, this collapses to standard MU.
- Prices: not modeled; 1:1 exchange implies fixed relative price = 1.
- Budget/Endowment: endowment evolves via foraging; no explicit budget constraint beyond carrying
  capacity.
- Consumption: not present; utility is over stocks. For validation, treat per‑step objective as
  myopic ΔU maximization rather than intertemporal choice.

Concrete Validation Experiments to Run (and what to expect)

- CD Forage (k=0)
  - Setup: Two agents at home, grid with both types uniformly within radius; set k=0 by modifying
    constant or stubbing distance to 0.
  - Expect: Each agent’s total bundle ratio y/x → β/α over time; mis‑collection events minimal.
- PS Forage (k=0)
  - Expect: Always collects only the higher‑α good; no switching.
- PC Forage (k=0)
  - Expect: Collects whichever good closes the gap |αx − βy| fastest; oscillations limited by
    discrete pickups.
- CD‑CD Exchange
  - Endow agents with opposing imbalances; place them co‑located; enable trade only.
  - Expect: Series of trades while MRS_A>1>MRS_B; stop when MRS_A≈1≈MRS_B or stock constraints
    block.
- PS‑PS Exchange (α/β on opposite sides of 1)
  - Expect: Trades flow until one side runs out of the less‑valued good; if both α/β>1 or \<1, no
    trade.
- PC‑CD Exchange
  - Expect: Trades that move PC toward αx=βy; CD’s participation depends on its MRS relative to 1 at
    those points.

Code/Config Observations and Recommendations (to ease validation)

- Align distance factor with config
  - Today: decision uses hardcoded k=0.15. Recommendation: read `SimConfig.distance_scaling_factor`
    and/or expose via features/flags to let you set k=0 for clean theory checks.
- Resource type mapping clarity
  - Decision maps "A"→good1, else→good2. Use only "A"/"B" in grids during forage validations, or
    extend mapping to explicit names ("food"/"wood").
- Explicit MRS helpers (optional)
  - Add small helper to compute MRS for each utility class to simplify instrumentation in tests.
- Stock vs. flow utility
  - If you later want consumption‑based validation, introduce “consume at home” and compute utility
    on consumed flow rather than stocks; for now, validate on stock utility as implemented.

References in Code (quick jump points)

- Utility classes and helpers: src/econsim/simulation/agent/utility_functions.py:50
- Decision entrypoint and trade logic: src/econsim/simulation/agent/unified_decision.py:1,
  src/econsim/simulation/agent/unified_decision.py:255
- Agent inventory ops: src/econsim/simulation/agent/core.py:121,
  src/econsim/simulation/agent/core.py:161
- Executor (two‑phase, movement, trade exec): src/econsim/simulation/executor.py:74,
  src/econsim/simulation/executor.py:240
- Grid API (resources): src/econsim/simulation/world/grid.py:1
- Feature flags: src/econsim/simulation/features.py:34
- Simulation factory: src/econsim/simulation/coordinator.py:240

Initial Planning Alignment (what’s done vs. planned)

- Phase 3 goals largely achieved:
  - Pluggable utility architecture and three core preference types implemented.
  - Deterministic decision engine with two‑phase execution.
  - Tests cover utility correctness and basic trade coherence.
- Next validation goals from `initial_planning.md`:
  - Demand theory, equilibrium computation, and validation against analytical results.
  - Educational scenario expansion with explicit theory checks.

Suggested Next Documentation to Draft (to aid future coding)

- Formal one‑pagers per model:
  - “Foraging as Myopic ΔU Maximization (k=0)” — definitions, lemmas, expected dynamics for
    CD/PS/PC.
  - “Edgeworth Exchange under Fixed Price 1” — MRS conditions, discrete trade paths, stopping
    criteria, expected neighborhoods.
  - “Spatial Cost Model” — justify exponential discount as travel disutility proxy; show decision
    rule equivalence to maximizing MU·exp(−k·d).
- Validation playbook
  - Parameter tables to reproduce expected behaviors; minimal scenarios for each preference type and
    exchange pairing.

Open Risks / Nuances to Track

- Discreteness and integer effects can prevent exact convergence to contract curve; define tolerance
  bands in validations.
- Using total bundle for trade valuation while executing on carrying can block otherwise beneficial
  trades if goods are at home; the code accounts for executability by enumerating only carried
  units, but the theoretical evaluation is on total stocks — keep that distinction clear in
  writeups.
- Perception radius and movement rules can limit realized trades vs. theory with full information;
  use co‑location setups for pure exchange validations.

Quick How‑To (run patterns with current code)

- Forage‑only: set `ECONSIM_FORAGE_ENABLED=1`, ensure `ECONSIM_TRADE_EXEC=0`.
- Trade‑only: set `ECONSIM_TRADE_EXEC=1`, place agents co‑located, use empty grid.
- Dual: enable both; tune resource layout to drive mixed dynamics.
- Entrypoints and tests to mimic:
  - Integration tests: tests/integration/test_unified_decision_integration_v2.py:1
  - Economic coherence tests: tests/unit/test_trade_economic_coherence.py:1

End
