# Project Structure Refactor Plan

This document outlines a proposed refactoring of the project structure to better align with the modular, behavior-driven agent design discussed in `tmp_plans/MODELS/me/a.md`. The goal is to create a clearer separation of concerns, making the codebase easier to understand, maintain, and extend for future educational scenarios.

## High-Level Goals

1.  **Modular Agent Behaviors**: Isolate distinct agent decision models (Foraging, Bilateral Exchange, Market Exchange) into their own modules.
2.  **Clearer World Representation**: Separate grid management, resource logic, and spatial helpers.
3.  **Decouple Simulation Core from GUI**: Ensure the simulation can run headless and the GUI is only a presentation layer.
4.  **Centralized Logging**: Consolidate logging infrastructure.

## Proposed Directory Structure

Here is the target directory structure for the `src/econsim/` directory. This builds upon the ideas in `a.md` and recent discussions.

```
src/econsim/
├── simulation/
│   ├── agent/
│   │   ├── core.py               # Core Agent class, state, inventory
│   │   ├── utility_functions.py  # Utility function implementations (Cobb-Douglas, Perfect Substitutes, Perfect Complements, etc.)
│   │   ├── behaviors/
│   │       ├── forage.py             # Logic for single-agent utility maximization (resource collection)
│   │       ├── bilateral_exchange.py # Logic for two-agent trading
│   │       ├── market_behaviors/     # Directory for future market-level models
│   │       │       └── __init__.py
│   │   └── unified_decision.py   # Top-level decision-making, scans for potential targets and passes data to individual decision modules when relevant; determines which individual behavior modules are used (allows forage-only, bilateral-exchange-only, market-only, none, or any behavior-in-combination depending on user settings)
│   │
│   ├── world/
│   │   ├── grid.py               # The spatial grid, agent/resource locations
│   │   ├── resources.py          # Resource properties and spawning logic
│   │   ├── spatial.py            # Spatial indexing and search (replaces density_grid.py)
│   │   └── helpers/              # Utility functions for world operations (e.g., distance calcs)
│   │       └── __init__.py
│   │
│   ├── executor.py             # Executes agent decisions and updates world state
│   ├── coordinator.py          # Main simulation loop orchestrator
│   └── features.py             # Feature flags
│
├── gui/
│   ├── main_window.py          # Main application window and layout
│   ├── grid_widget.py          # The visual grid rendering component
│   ├── controls.py             # UI controls (buttons, sliders, dropdowns)
│   └── launcher/
│       ├── __init__.py
│       └── educational_scenarios.py # New tab for educational scenarios
│
├── logging/
│   ├── config.py               # Logging setup and configuration
│   └── handlers.py             # Custom logging handlers if needed
│
└── main.py                     # Application entry point
```

## Component Responsibilities

### `simulation/agent/`
- **`core.py`**: Defines the `Agent` class, including its state (inventory, position, utility function) but *not* its decision-making logic.
- **`forage.py`**: Contains functions that evaluate foraging options based on distance-discounted marginal utility.
- **`bilateral_exchange.py`**: Contains functions to identify and evaluate potential trades between two agents.
- **`market_behaviors/`**: A placeholder for more complex, multi-agent market simulations.
- **`unified_decision.py`**: The "brain" that integrates the different behavioral modules. It will take an agent and the world state, and based on the agent's mode (or simulation parameters), it will call the appropriate functions from `forage.py` or `bilateral_exchange.py` to determine the agent's action.

### `simulation/world/`
- **`grid.py`**: Manages the 2D grid data structure.
- **`resources.py`**: Defines resource types and handles their spawning and depletion.
- **`spatial.py`**: A dedicated module for efficient spatial queries, like finding agents or resources within a certain radius. This will likely contain the `AgentSpatialGrid` logic.
- **`helpers/`**: A package for pure utility functions related to the world, such as Manhattan distance calculations or coordinate validation.

### `gui/`
- This package will be responsible for all visualization. It will read from the simulation state but not modify it directly.
- The new **`launcher/educational_scenarios.py`** will implement the UI for the "Educational Scenarios" tab as described in `a.md`.

### `logging/`
- A centralized place to configure the application's logging.

## Next Steps

1.  Create the new directory and file structure.
2.  Begin migrating existing code into the new structure, starting with `agent/core.py` and the `world/` components.
3.  Refactor `unified_decision.py` to call out to the new `forage.py` and `bilateral_exchange.py` modules, removing the old `modes.py` logic.
4.  Implement the new "Educational Scenarios" tab in the GUI.
