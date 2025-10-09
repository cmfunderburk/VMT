# VMT EconSim: Strategic Plan for Educational Realignment

**Project Name**: VMT EconSim Platform
**Document Purpose**: To synthesize recent insights from user notes (`tmp_plans/MODELS/me/a.md`) and expert economic reviews into a unified, actionable "big picture" plan. This document respects the current development pause for economic validation and charts a clear path toward the project's core educational mission.

---

## Core Understanding

### 1. Problem & Success Definition

**Problem**: The VMT EconSim platform has a sophisticated simulation engine, but a gap exists between its implicit economic models and explicit, verifiable economic theory. To fulfill its educational mission, the platform must first **formally document and validate its existing spatial economic models**. Following validation, the architecture must be refactored to make these models **explicit and modular**. Only then can we build a targeted "Educational Scenarios" interface that clearly demonstrates fundamental microeconomic principles to students.

**Core Mission**: To create a deterministic, visually intuitive educational tool that teaches microeconomic theory. Success is achieved when students can predict agent behavior based on economic principles alone, and the simulation's logic is a direct, verifiable implementation of those principles.

**Success Metrics** (Updated):

- **V-01 (Validation)**: Complete the formal documentation and validation tests for all three core utility functions as outlined in `Opus_econ_model_review.md`.
- **A-01 (Architecture)**: Refactor the `unified_decision.py` monolith into distinct, testable `behavior` modules (`forage.py`, `bilateral_exchange.py`) that explicitly represent the validated economic models.
- **E-01 (Education)**: Implement a new "Educational Scenarios" tab in the GUI, featuring the "Choice and Utility," "Bilateral Exchange," and "Forage-and-Exchange" scenarios.
- **E-02 (Clarity)**: In blind tests using the new Educational Scenarios, a user can correctly identify the underlying utility function and predict agent behavior with >90% accuracy.
- **R-01 (Reproducibility)**: All educational scenarios and validation tests are fully deterministic and reproducible from a fixed seed.

### 2. Key User Scenarios (Post-Validation)

**S-01: The "Aha!" Moment for Utility Theory**
- **Flow**: A student opens the "Educational Scenarios" tab and selects "Choice and Utility." They see a single agent on a small grid. Using a dropdown, they switch the agent's utility function from Cobb-Douglas to Perfect Substitutes. They immediately observe the agent's behavior change from collecting a mix of goods to focusing exclusively on the closest one.
- **Success**: The student gains an intuitive, visual understanding of how utility functions directly translate to behavior.

**S-02: Discovering Gains from Trade**
- **Flow**: An instructor selects the "Bilateral Exchange" scenario. Two agents appear with initial endowments. The agents are not moving. The instructor explains their preferences and asks the class to predict if a trade will occur. They unpause the simulation, and the agents trade, with their post-trade utility displayed on the GUI, showing a clear welfare improvement for both.
- **Success**: The concept of Pareto improvement is demonstrated concretely and visually.

**S-03: The Developer's Confidence**
- **Flow**: A developer needs to debug an agent's decision. Instead of tracing through the complex `unified_decision.py`, they open `src/econsim/simulation/agent/behaviors/forage.py`. The file contains the pure, validated logic for single-agent utility maximization. They can write a unit test against this module directly.
- **Success**: The new architecture is more modular, easier to understand, test, and maintain, directly reflecting the documented economic models.

### 3. System Sketch (Future State)

```markdown
┌───────────────────┐    ┌────────────────────┐    ┌──────────────────┐
│ Economic Models   │    │ Behavior Modules   │    │  Decision Engine │
│ (Formal Docs)     │───>│ (forage.py,      ) │───>│   (Orchestrator) │
│ • Opus_review.md  │    │ (exchange.py, etc.)│    │ • Selects Behavior│
│ • Spatial_...md   │    │ • Explicit Logic   │    │ • Passes State    │
└───────────────────┘    └────────────────────┘    └──────────────────┘
         ▲                       │                       │
         │ Validation            ▼                       ▼
┌───────────────────┐    ┌────────────────────┐    ┌──────────────────┐
│ Validation Tests  │    │ Agent Actions      │    │ Executor         │
│ (tests/validation)│<───┤ (Move, Collect...) │───>│ (Applies Actions)│
└───────────────────┘    └────────────────────┘    └──────────────────┘
```

**Data Flow**: The formally documented **Economic Models** are implemented as explicit **Behavior Modules**. The main **Decision Engine** selects the appropriate behavior for an agent based on its state and mode. The chosen behavior module returns a decision, which is then executed. **Validation Tests** ensure the behavior modules correctly implement the documented models.

### 4. Risk Radar

**R-01: Incomplete Validation (High Impact, Med Likelihood)**
- **Risk**: We resume coding before the economic models are fully documented and validated, rebuilding on a shaky foundation.
- **Mitigation**: Strictly adhere to the "Development Pause." The validation phase is complete only when the formal models and corresponding tests outlined in `Opus_econ_model_review.md` are implemented and passing.

**R-02: Over-Engineering the Refactor (Med Impact, Med Likelihood)**
- **Risk**: The `behaviors` refactor becomes too abstract or complex, hindering rather than helping clarity.
- **Mitigation**: Start with the simplest possible refactor: move existing logic for foraging and trading into their respective `behavior` files with minimal changes. Improve the interfaces iteratively.

**R-03: Educational Scenarios Lack Clarity (High Impact, Low Likelihood)**
- **Risk**: The new scenarios fail to make the economic concepts visually obvious.
- **Mitigation**: Design the scenarios with a "less is more" philosophy. Use small grids (5x5), few agents (1-3), and prominent GUI elements to display utility and inventory. The goal is clarity, not complexity.

---

## Implementation Roadmap

This roadmap is sequential. Each phase is a prerequisite for the next.

### **Phase 0: Economic Model Validation (CURRENT PHASE)**

**Goal**: To formally document and empirically validate the economic models currently implemented in the simulation. **All other development is paused.**

**Tasks**:
1.  Follow the action plan in `tmp_plans/FINAL/Opus_econ_model_review.md`.
2.  Create explicit mathematical model documents for each utility function in a spatial context.
3.  Implement a new suite of validation tests (`tests/validation/`) that verify the simulation's behavior against the predictions of the formal models.
4.  Do not proceed until this phase is declared complete.

### **Phase 1: Architectural Refactor for Clarity (Post-Validation)**

**Goal**: To refactor the decision-making logic to explicitly reflect the newly validated economic models.

**Tasks**:
1.  Create a new directory: `src/econsim/simulation/agent/behaviors/`.
2.  Create `forage.py`: Isolate the logic for single-agent, distance-discounted utility maximization from `unified_decision.py` and move it here.
3.  Create `bilateral_exchange.py`: Isolate the logic for evaluating and proposing trades from `unified_decision.py` and move it here.
4.  Refactor `unified_decision.py` to act as an orchestrator. It will now call the appropriate functions from the `behaviors` modules based on the agent's state (e.g., `decide_forage_only` calls logic in `forage.py`).
5.  Ensure all existing unit and integration tests pass after the refactor.

### **Phase 2: Educational Scenario Implementation (Post-Refactor)**

**Goal**: To build a new, dedicated interface for teaching core microeconomic concepts using the clear, validated, and modular architecture.

**Tasks**:
1.  **GUI Development**:
    *   Add a new "Educational Scenarios" tab to the main launcher GUI.
    *   This tab will present a simple gallery of the new scenarios.
2.  **Scenario 1: "Choice and Utility"**
    *   Create a scenario configuration with a single agent on a 5x5 grid.
    *   Add GUI controls (e.g., dropdowns) to change the agent's utility function and preference parameters in real-time.
    *   Display the agent's current utility and inventory prominently.
3.  **Scenario 2: "Bilateral Exchange"**
    *   Create a scenario with two agents on a 5x5 grid with initial endowments and no collectible resources.
    *   Display each agent's utility, demonstrating Pareto improvements post-trade.
4.  **Scenario 3: "Bilateral Forage-and-Exchange"**
    *   Create a scenario with three agents on a 5x5 grid with collectible resources.
    *   This demonstrates the interplay between individual optimization (foraging) and social optimization (trade).

### **Phase 3: Future Work**

-   **Market Exchange**: Design and implement a `market_exchange.py` behavior.
-   **Debug Recorder**: Re-prioritize and implement the `DebugRecorder` system, which will benefit greatly from the modular behavior architecture.
-   **Curriculum Expansion**: Expand the educational scenarios to cover more advanced topics like game theory and externalities.

---

## Decision Log

**D-01: Adopt a Phased Approach**
- **Decision**: The project will proceed in three distinct, sequential phases: Validation, Refactoring, and Educational Implementation.
- **Rationale**: This approach mitigates the primary risk of building on an unverified foundation. It ensures that the core educational features are built on solid, well-understood, and explicitly coded economic models. Your notes in `a.md` provide the vision for Phases 1 and 2, while the expert reviews provide the necessary rigor for Phase 0. This plan unifies them.
- **Consequences**: This delays the implementation of new user-facing features, but dramatically increases the integrity and long-term value of the platform.

**Next Steps**:
1.  Continue executing **Phase 0: Economic Model Validation**.
2.  Once validation is complete, this document will serve as the foundational plan for the subsequent development phases.
