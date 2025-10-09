# Critical Review: Economic Model Documentation Gaps and Inconsistencies

**Reviewer**: AI Coding Assistant  
**Date**: October 8, 2025  
**Documents Reviewed**:
- `1_single_agent_utility_spatial.md` (748 lines)
- `2_bilateral_pure_exchange.md` (1178 lines)  
- `3_bilateral_forage_exchange.md` (883 lines)

**Status**: 🔴 Multiple critical issues found - Implementation blocked until resolved

---

## Executive Summary

The three model documents provide substantial theoretical foundations, but contain **critical inconsistencies** and **implementation gaps** that must be resolved before proceeding to coding. Key issues:

1. **Parameter inconsistencies** across documents (epsilon values differ)
2. **Agent specification errors** (preference descriptions contradict parameters)
3. **Mathematical errors** in equilibrium calculations (welfare comparisons inconsistent)
4. **Missing implementation details** (trade coordination, travel costs, meeting points)
5. **Incomplete validation framework** (no tests implemented, unclear success criteria)

**Recommendation**: Address all Category A (Critical) issues before any implementation work begins.

---

## Category A: Critical Inconsistencies (Must Fix Before Implementation)

### A.1 Epsilon Parameter Mismatch

**Issue**: Inconsistent epsilon values across documents and with code.

| Location | Epsilon Value | Line Reference |
|----------|---------------|----------------|
| Doc 1 (text) | ε = 0.001 | Line 89 |
| Doc 1 (code comment) | ε = 0.01 | Line 89 (in formula description) |
| Doc 2 | ε = 0.01 | Throughout |
| Doc 3 | ε = 0.01 | Line 60 |
| Actual code | ε = 0.01 | `utility_functions.py` |

**Evidence from Document 1**:
```
Line 89: ε = 0.001 (epsilon parameter, prevents divide-by-zero)
Line 119: Small enough ($0.001$) to not distort preferences at educational scales
```

But then in the same document:
```
Line 303: U(5, 5) = (5.01)^{0.7} · (5.01)^{0.3} = 5.01 (uses ε = 0.01)
```

**Impact**: 
- Analytical predictions will not match implementation if epsilon differs
- Student confusion when comparing equations to code
- Potential for actual bugs if epsilon is changed

**Remediation**:
1. Standardize on **ε = 0.01** across all documents (matches code)
2. Update Document 1, Section 2.1 to use 0.01
3. Recalculate all examples in Document 1 with correct epsilon
4. Add explicit note: "Epsilon value is implementation constant, do not change without full system validation"

---

### A.2 Agent Preference Specification Error (Document 3)

**Issue**: Agent descriptions contradict their utility function parameters.

**Document 3, Lines 26-38**:
```
Agent 1 (Prefers Good 2, Located Near Good 1):
- Utility function: U_1(q_1, q_2) = (q_1 + ε)^0.7 · (q_2 + ε)^0.3
  - α_1 = 0.7, β_1 = 0.3 (prefers Good 1, but not strongly)
```

**Analysis**:
- **Header says**: "Prefers Good 2"
- **Parameters show**: α₁ = 0.7 (prefers Good 1)
- **Comment says**: "prefers Good 1, but not strongly"

This is internally contradictory. With α₁ = 0.7, β₁ = 0.3, Agent 1 **definitely prefers Good 1** (70% weight).

**Same Issue for Agent 2** (Lines 33-38):
```
Agent 2 (Prefers Good 1, Located Near Good 2):
- Utility function: U_2(q_1, q_2) = (q_1 + ε)^0.3 · (q_2 + ε)^0.7
  - α_2 = 0.3, β_2 = 0.7 (prefers Good 2, but not strongly)
```

Header says "Prefers Good 1" but β₂ = 0.7 means prefers Good 2.

**Correct Economic Setup Should Be**:
- **Agent 1**: Prefers Good 1 (α=0.7), located near Good 1 sources → **No trade tension!**
- **Agent 2**: Prefers Good 2 (β=0.7), located near Good 2 sources → **No trade tension!**

This setup creates **aligned preferences and locations**, reducing gains from trade. The educational lesson (specialization creates trade opportunities) is weakened.

**Remediation Options**:

**Option 1: Fix Headers** (minimal change)
- Change headers to match parameters
- Agent 1: "Prefers Good 1, Located Near Good 1"
- Agent 2: "Prefers Good 2, Located Near Good 2"
- Accept reduced trade gains as educational scenario

**Option 2: Reverse Preferences** (stronger trade scenario)
- Keep headers as intended
- Change parameters:
  - Agent 1: α₁ = 0.3, β₁ = 0.7 (prefers Good 2, located near Good 1)
  - Agent 2: α₂ = 0.7, β₂ = 0.3 (prefers Good 1, located near Good 2)
- This creates **misaligned preferences and locations** → maximum gains from trade
- Better educational demonstration

**Recommendation**: **Option 2** - Reverse utility parameters to match headers. This creates the "wrong good" specialization that drives trade.

---

### A.3 Total Endowment Inconsistency (Documents 2 vs 3)

**Issue**: Total goods in economy differ between pure exchange and forage-exchange models.

**Document 2** (Pure Exchange):
```
Line 132-133:
Total Economy:
- Ω₁ = 20 + 5 = 25 (total Good 1)
- Ω₂ = 5 + 20 = 25 (total Good 2)
```

**Document 3** (Forage-Exchange):
```
Line 248-249:
With resource constraint: q_1^1 + q_1^2 = 12 and q_2^1 + q_2^2 = 12 (total available)
```

Total is 12 in Document 3, but this appears in equilibrium calculations for bundles starting at (10,2) and (2,10).

**Analysis**:
- Document 2: Starts with 25 units total (fixed endowments)
- Document 3: Implies 12 units total after foraging
- These are different scenarios, but should use consistent magnitudes for comparability

**Impact**:
- Cannot compare equilibrium predictions across documents
- Trade sequence lengths differ due to different total quantities
- Student confusion when comparing scenarios

**Remediation**:
1. Choose standard total: **20 units of each good** (nice round number)
2. Document 2: Change endowments to (15, 5) and (5, 15) → Total = 20
3. Document 3: Target post-foraging bundles of (8, 2) and (2, 8) → Total = 10 for each agent
4. Recalculate all equilibrium predictions with consistent totals

---

### A.4 Mathematical Error: Welfare Comparison (Document 2)

**Issue**: Discrete equilibrium has higher welfare than continuous optimum, which is mathematically impossible.

**Document 2, Lines 495-497**:
```
**Surprising Result**: Discrete equilibrium has **higher total welfare** than continuous optimum!

Continuous optimum: W ≈ 28.3
Discrete equilibrium: W = 29.95
```

**Analysis**:
This violates basic optimization theory. The continuous optimum should **always** be at least as good as discrete equilibrium (relaxed constraints).

**Root Cause** (identified in document):
```
Line 667-669:
**Explanation**: My continuous calculation assumed an allocation on the contract curve 
that made Agent 2 worse off (outside the core). The discrete process respects 
individual rationality at every step...
```

The document acknowledges this error but doesn't fix the calculations.

**Correct Approach**:
1. Continuous optimum **within the core** (both agents better off than endowment)
2. Must satisfy: U₁(q¹) ≥ U₁(e¹) AND U₂(q²) ≥ U₂(e²)
3. Recalculate continuous optimum with core constraint
4. Verify: W_continuous ≥ W_discrete (equality only if discrete happens to hit continuous exactly)

**Remediation**:
1. Recalculate Section 3.5 "Finding Allocation in the Core"
2. Use numerical optimization to find:
   - max(U₁ + U₂) subject to MRS₁ = MRS₂ AND both agents gain
3. Update all welfare comparisons
4. Remove "Surprising Result" claim (it was an error)

---

### A.5 Contract Curve Equation Error (Document 2)

**Issue**: Contract curve calculation has algebraic errors.

**Document 2, Lines 222-246** shows derivation:
```
Cross-multiplying:
49 q₂¹ (25 - q₁¹) = 9 q₁¹ (25 - q₂¹)

[several steps]

Contract Curve Equation (implicit form):
40 q₁¹ q₂¹ + 225 q₁¹ - 1225 q₂¹ = 0
```

**Verification** (expanding 49 q₂¹ (25 - q₁¹) = 9 q₁¹ (25 - q₂¹)):
- Left: 1225 q₂¹ - 49 q₁¹ q₂¹
- Right: 225 q₁¹ - 9 q₁¹ q₂¹
- Equation: 1225 q₂¹ - 49 q₁¹ q₂¹ = 225 q₁¹ - 9 q₁¹ q₂¹
- Rearranging: 40 q₁¹ q₂¹ + 225 q₁¹ - 1225 q₂¹ = 0 ✓

**Actually, the algebra is correct!** But the solution:
```
Line 249-250:
q₂¹ = (225 q₁¹) / (1225 - 40 q₁¹)
```

Let me verify by substituting back... Actually, this needs numerical verification with specific values to check if equilibrium predictions are correct.

**Remediation**:
1. Numerically verify contract curve equation at several points
2. Plot curve to ensure it's reasonable (should be monotonic decreasing in Edgeworth box)
3. Check endpoint behavior (q₁¹ → 0 and q₁¹ → 25)

---

## Category B: Implementation Gaps (Needed for Coding)

### B.1 Missing: Trade Coordination Mechanism

**Issue**: Documents describe what should happen but not **how** agents coordinate.

**Key Questions Unanswered**:

1. **Simultaneous Trade Intent**:
   - What if both agents want to initiate trade at same timestep?
   - Who moves first? How is this resolved deterministically?
   - Does agent with lower ID get priority?

2. **Meeting Point Determination**:
   - Document 3 mentions "midpoint $(10, 10)$" (line 297) but no algorithm
   - What if agents are moving? Is meeting point recalculated each step?
   - What if one agent moves away before trade executes?

3. **Trade Execution Timing**:
   - Are trades instantaneous or require both agents at same location?
   - Can agents trade while moving or must be stationary?
   - What happens if perception radius lost during approach?

**Current Implementation Status** (from workspace rules):
```
Phase 2: Action Execution (Coordinated)
Execute all special actions (collect, trade, pair, unpair) with proper coordination.
```

But no specification of **what coordination means** for trade.

**Remediation**:
1. Add "Trade Coordination Protocol" section to Document 3
2. Specify exact sequence:
   ```
   Step 1: Both agents detect mutual Pareto improvement
   Step 2: Calculate meeting point (midpoint for symmetry)
   Step 3: Both agents set target to meeting point
   Step 4: When both within perception radius, execute trade
   Step 5: Trade is atomic (both inventories update simultaneously)
   ```
3. Deterministic tiebreaker: Lower agent ID initiates if simultaneous

---

### B.2 Missing: Travel Cost Model

**Issue**: All three documents mention travel costs but none provide implementation specification.

**Document 1**: No travel cost for resource collection (only distance discounting)
**Document 2**: 
```
Line 598-609: Travel Cost Model (mentioned but not implemented)
Net Gain from Trade = ΔUᵢ - k_travel · d_travel
```

**Document 3**:
```
Line 318-321: Theoretical Fix (Future Enhancement)
k_travel converts distance to utility loss (e.g., 0.01 utility per unit distance)
```

**Critical Gap**: Without travel cost, agents will trade even when travel distance >> trade gain.

**Example Problem**:
- Trade gain: ΔU = 0.05 utility
- Travel distance: 50 units (each agent travels 25 to midpoint)
- If travel cost = 0: Trade occurs
- If travel cost = 0.01 per unit: Cost = 50 × 0.01 = 0.50 > 0.05 → Trade should NOT occur

**Current Behavior**: Travel cost ignored → unrealistic trades at extreme distances

**Remediation Options**:

**Option 1: Defer Travel Costs** (simplest for Phase 2)
- Document that travel costs are ignored in initial implementation
- Add to "Known Limitations" section
- Plan as Phase 2.1b enhancement

**Option 2: Implement Simple Travel Cost** (more realistic)
- Add parameter: `TRAVEL_COST_PER_UNIT = 0.005` (calibrate)
- Modify trade decision:
  ```python
  def should_trade(agent1, agent2, trade_gain, distance):
      travel_cost = distance * TRAVEL_COST_PER_UNIT
      return trade_gain > travel_cost
  ```
- Add to both agent decisions (both must gain > travel cost)

**Recommendation**: **Option 1** for initial implementation, clearly document as limitation, implement Option 2 in Phase 2.1b after basic trade working.

---

### B.3 Missing: Perception Radius Edge Cases

**Issue**: Documents state $R = 8$ but don't handle boundary conditions.

**Unanswered Questions**:
1. **Agents exactly at boundary**: Distance = 8, can they perceive each other?
   - Use `≤` or `<` comparison?
   - Current code likely uses `≤`, but docs should specify

2. **Agent moves out of range during trade**: 
   - Trade initiated when distance = 7
   - Agent 2 moves away, distance becomes 9
   - Does trade cancel or complete?

3. **Asymmetric perception**:
   - Document mentions "Agent-specific perception radii" as future (Doc 2, line 1042)
   - But if implemented, who initiates trade when only one can see?

**Remediation**:
1. Specify: "Within perception if `manhattan_distance(a1, a2) <= R`" (inclusive)
2. Add "Trade Cancellation Rule": If distance > R after initiation, trade cancels
3. Add validation test: `test_perception_boundary_trade()`

---

### B.4 Missing: Pareto Improvement Verification Code

**Issue**: Documents describe Pareto check mathematically but no code specification.

**Document 3, Lines 619-636** shows desired logic:
```python
def should_trade(agent_1, agent_2, good_offered_1, good_offered_2, amount):
    """Check if trade creates Pareto improvement"""
    # [code shown]
    return (u1_after > u1_before) and (u2_after > u2_before)
```

**Gap**: This is in "Implementation Considerations (Future Work)" section, not actual implementation.

**Current Implementation Status**: Unknown if this check exists in `unified_decision.py`

**Remediation**:
1. Search current codebase: Does Pareto check exist?
2. If yes: Document it in all three model docs
3. If no: Implement it before Phase 2 validation
4. Add test: `test_pareto_improvement_check_prevents_harmful_trades()`

---

### B.5 Missing: Equilibrium Detection

**Issue**: How do agents know when to stop trading?

**Documents describe equilibrium conditions** (MRS equality) but not detection mechanism.

**Options**:

**Option A: Implicit Equilibrium**
- Agents continue checking for Pareto improvements
- When none found, trading stops naturally
- No explicit equilibrium detection needed

**Option B: Explicit Equilibrium Check**
- Calculate: `|MRS₁ - MRS₂| < tolerance`
- If true: Mark equilibrium reached, disable trade checks
- More efficient but requires threshold tuning

**Current Behavior**: Likely Option A (implicit)

**Remediation**:
1. Document: "Equilibrium is implicit - trading stops when no Pareto improvements exist"
2. Add validation test: `test_no_trades_at_equilibrium()` (exists in plan but not implemented)
3. Add debug output: "No beneficial trades found, equilibrium reached"

---

## Category C: Theoretical Questions (Need Expert Review)

### C.1 Discrete Exchange Convergence

**Question**: Does sequential 1-for-1 exchange provably reach the contract curve?

**Document 2, Lines 699-706** discusses this:
```
Convergence Guarantee: 
- For Cobb-Douglas utilities, discrete equilibrium is at most 1 trade away from 
  the closest integer allocation on the contract curve.
- As total endowment Ω → ∞, discrete equilibrium converges to continuous optimum.
```

**Gap**: No proof provided. This is a claim, not a theorem.

**Remediation**:
1. Literature review: Has this been proven for Cobb-Douglas case?
2. If yes: Cite theorem and provide reference
3. If no: Either prove it or weaken claim to "empirically observed in our tests"
4. Consider adding numerical convergence study (vary Ω from 10 to 1000)

---

### C.2 Distance Discount Calibration

**Question**: Is $k = 0.15$ empirically justified?

**All three documents state**: $k = 0.15$ (distance discount constant)

**Document 1, Line 241**: "calibrated constant" - but no calibration study shown

**Evidence for 0.15**:
- At distance 4.6: discount ≈ 0.5 (50% reduction)
- At distance 8 (perception radius): discount ≈ 0.30 (70% reduction)

**Gap**: Why these specific values? What educational scenarios were tested?

**Remediation**:
1. Document calibration rationale:
   - "Chosen so agents explore ~8 units (perception radius) with 30% value retention"
   - "Prevents agents from ignoring distant resources entirely"
2. Add sensitivity analysis: Test k ∈ [0.05, 0.30]
3. Plot: Agent specialization vs k (higher k → stronger specialization)

---

### C.3 Optimal Exchange Ratio Formula

**Question**: What is the optimal exchange ratio for variable-ratio trades?

**Document 3, Lines 692-700** proposes:
```
Exchange Ratio = ΔQ₂/ΔQ₁ = MU₁/MU₂
```

But which agent's MU ratio? Or average?

**Options**:
1. **Arithmetic mean**: $(MRS_1 + MRS_2) / 2$
2. **Geometric mean**: $\sqrt{MRS_1 \cdot MRS_2}$
3. **Nash bargaining solution**: Maximizes product of utility gains
4. **Midpoint**: Ratio halfway between agents' acceptable bounds

**Gap**: No economic theory cited for which is correct.

**Remediation**:
1. Literature review: What does bargaining theory recommend?
2. Test all four options numerically
3. Compare: Which reaches equilibrium fastest? Most symmetric gains?
4. Document chosen method with justification

---

## Category D: Validation Framework Gaps

### D.1 No Tests Implemented

**Issue**: All three documents have validation test specifications but status is:

**Document 1, Lines 499-507**: 
```
- [x] Equal distance choice (Scenario 4.1)
- [x] Distance-preference tradeoff (Scenario 4.2)
...
```
Marked as complete but no actual test files exist!

**Document 2, Lines 1151-1164**: All checkboxes empty `[ ]`
**Document 3, Lines 794-808**: All checkboxes empty `[ ]`

**Gap**: Cannot validate theory without tests.

**Remediation**:
1. Create test file structure:
   ```
   tests/validation/
   ├── test_single_agent_utility.py
   ├── test_bilateral_pure_exchange.py
   └── test_bilateral_forage_exchange.py
   ```
2. Implement at minimum:
   - One test from each document (smoke test)
   - `test_equal_distance_choice()` from Doc 1
   - `test_pure_exchange_reaches_equilibrium()` from Doc 2
   - `test_complementary_preferences_lead_to_trade()` from Doc 3
3. Update checkboxes as tests pass

---

### D.2 Unclear Success Criteria

**Issue**: What does "matches prediction" mean quantitatively?

**Document 1, Line 508**:
```
Success Metrics:
- 95%+ test scenarios match analytical predictions
```

But what is a "match"?
- Exact bundle equality?
- Within ±1 unit?
- Within 5% utility?

**Document 2, Line 919**:
```
Success Criterion:
- Final bundles within ±1 unit of predicted equilibrium
```

This is specific, but other criteria are vague.

**Remediation**:
1. Define "prediction match" precisely for each test type:
   - **Choice predictions**: Agent chooses predicted resource (exact)
   - **Bundle predictions**: Final bundle within ±1 unit of prediction
   - **Utility predictions**: Final utility within 5% of prediction
   - **Trade count**: Within ±1 of predicted count
2. Add tolerance constants to test suite:
   ```python
   BUNDLE_TOLERANCE = 1  # units
   UTILITY_TOLERANCE = 0.05  # 5%
   TRADE_COUNT_TOLERANCE = 1
   ```

---

### D.3 Missing Performance Benchmarks

**Issue**: Documents focus on correctness but not computational performance.

**Questions**:
- How long should equilibrium convergence take? (timesteps and wall-clock)
- What's acceptable frame rate during trade coordination?
- Memory usage limits for contract curve calculations?

**Remediation**:
1. Add "Performance Requirements" section to each document:
   ```markdown
   ## Performance Benchmarks
   
   ### Computational:
   - Trade decision (Pareto check): < 1ms per agent pair
   - Equilibrium convergence: < 100 timesteps for 2 agents
   - Contract curve calculation: < 100ms for 2 agents
   
   ### Visual:
   - GUI update latency: < 100ms after parameter change
   - Frame rate during trade: ≥ 20 FPS (50ms per frame)
   ```
2. Add performance tests to validation suite

---

## Category E: Educational Clarity Issues

### E.1 Inconsistent Notation

**Issue**: Same concepts use different notation across documents.

**Examples**:
- Bundle representation:
  - Doc 1: $(q_1, q_2)$ - total bundle
  - Doc 2: $q^1 = (q_1^1, q_2^1)$ - superscript for agent, subscript for good
  - Doc 3: Mix of both

- Marginal utility:
  - Doc 1: $MU_1(q_1, q_2)$ - function notation
  - Doc 2: $MU_1^1$ - MU of good 1 for agent 1
  - Doc 3: $MU_1^1$ - same as Doc 2

**Impact**: Student confusion when reading multiple documents.

**Remediation**:
1. Standardize notation across all three documents:
   ```
   - Agent i: i ∈ {1, 2}
   - Good k: k ∈ {1, 2}
   - Bundle for agent i: q^i = (q_1^i, q_2^i)
   - Utility for agent i: U_i(q^i)
   - Marginal utility of good k for agent i: MU_k^i
   ```
2. Add "Notation Guide" section to each document
3. Create master notation reference in MODELS folder

---

### E.2 Missing Visual Aids

**Issue**: Complex spatial scenarios lack diagrams.

**Document 3** describes spatial setup but no diagram:
```
Lines 44-56: Resource cluster positions
Lines 289-299: Meeting point scenarios
```

Students would benefit from:
- Grid diagram showing agent homes and resource clusters
- Trade path diagram showing movement to meeting point
- Contract curve graph for Document 2

**Remediation**:
1. Create diagrams (can use ASCII art or mermaid.js):
   ```
   Doc 1: Resource selection diagram (distance discounting)
   Doc 2: Edgeworth box with contract curve
   Doc 3: Spatial trade scenario (grid with agents and resources)
   ```
2. Link to existing visual test: `make visualtest` should demonstrate each scenario

---

## Recommended Action Plan

### Phase 1: Fix Critical Issues (This Week)

**Priority 1: Parameter Consistency**
- [ ] Standardize epsilon to 0.01 across all documents
- [ ] Fix Agent preference specification error in Document 3
- [ ] Recalculate all examples with correct parameters

**Priority 2: Mathematical Corrections**
- [ ] Fix welfare comparison in Document 2 (continuous vs discrete)
- [ ] Verify contract curve equation numerically
- [ ] Recalculate equilibrium bundles with core constraints

**Priority 3: Notation Standardization**
- [ ] Create master notation guide
- [ ] Update all three documents to use consistent notation

### Phase 2: Fill Implementation Gaps (Next Week)

**Priority 1: Trade Coordination**
- [ ] Specify meeting point algorithm
- [ ] Define trade execution sequence
- [ ] Document deterministic tiebreakers

**Priority 2: Travel Cost Model**
- [ ] Decide: Defer or implement simple version?
- [ ] Document decision and rationale
- [ ] If implemented, specify parameter calibration

**Priority 3: Validation Framework**
- [ ] Create test file structure
- [ ] Implement one smoke test per document
- [ ] Define success criteria precisely

### Phase 3: Expert Review (Before Implementation)

**Questions for Economics Expert**:
1. Discrete exchange convergence: Provable or empirical?
2. Optimal exchange ratio formula: Which is theoretically sound?
3. Distance discount calibration: Is there an empirical basis?

**Questions for Implementation Team**:
1. Does Pareto improvement check exist in current code?
2. How are simultaneous trade intents currently resolved?
3. What are performance constraints for trade coordination?

---

## Discussion Questions

I've identified 5 critical issues (Category A) that block implementation. Before I propose detailed solutions, I'd like to discuss:

### Question 1: Agent Preferences in Document 3 (Most Critical)

The preference specification error fundamentally changes the economic scenario:

**Current (incorrect)**: Agents specialize in their preferred goods → small gains from trade
**Intended (I think)**: Agents specialize in non-preferred goods → large gains from trade

Which scenario do you want for the educational demonstration? 

- **Option A**: "Comparative advantage from location alone" (agents get wrong good)
- **Option B**: "Aligned preferences and locations" (agents get right good)

Option A is more pedagogically interesting (shows spatial constraints create trade).

### Question 2: Travel Cost Implementation

Should travel costs be:

- **Deferred**: Document as known limitation, implement in Phase 2.1b
- **Simple model**: Add fixed cost per unit distance now
- **Utility-based**: Travel time reduces utility directly (complex)

My recommendation: Defer to Phase 2.1b, clearly document as limitation. Agree?

### Question 3: Validation Priority

With limited time, which validation tests are most critical:

- **Option A**: One comprehensive test per document (broad coverage)
- **Option B**: Multiple tests for Document 1 only (deep validation)
- **Option C**: Focus on Document 3 (most complex, used for multi-agent)

My recommendation: Option C - Document 3 is foundation for all multi-agent work.

### Question 4: Contract Curve Visualization

Document 2 describes contract curve overlay (lines 628-643) but implementation seems complex. Should we:

- **Option A**: Implement full contract curve visualization (educationally valuable)
- **Option B**: Defer to Phase 2.3 (after basic trade working)
- **Option C**: Skip visualization, rely on numerical validation

My recommendation: Option B - defer until basic trade validated.

---

## Next Steps

After you review this document and we discuss the questions above, I propose:

1. **Fix critical issues** (Category A) - I can implement corrections
2. **Document implementation gaps** (Category B) - Create specification documents
3. **Submit theoretical questions** to expert reviewer
4. **Create validation test structure** - Starting with Document 3

Estimated time: 2-3 days for Category A fixes, 1 week for Category B specifications.

Should I proceed with creating detailed correction patches for the documents?

