Need to figure out how to present the material.

1. Add a new tab to the launcher -- "Educational Scenarios"
  - Displays like the Test Gallery
    - Scenarios:
      1. Choice and Utility
        - One agent -- inventory and utility displayed on GUI
        - 5x5 grid
        - Chooseable utility function (drop down)
        - Chooseable preference parameters (drop down)
        - Resources spawn at random locations in the grid
        - User can adjust parameters and see behavior differences  
      2. Bilateral Exchange
        - Two agents -- inventory and utility displayed on GUI
        - 5x5 grid
        - No resources on grid; agents have endowments
        - User can adjust parameters and see behavior differences
      3. Bilateral Forage-and-Exchange
        - Three agents -- inventory and utility displayed on GUI
        - 5x5 grid
        - Resources spawn at random locations in the grid
        - User can adjust parameters and see behavior differences

--

Choice and Utility model should demonstrate:
  1. Agent switching between resources based on distance-discounted marginal utility
  2. Switching points based on distance discounting
  3. Resources collected in proportion to preference parameters

Bilateral Exchange model should demonstrate:
  1. Agents only exchange if they both benefit (rational behavior)
  2. Exchange occurs at (or near, in the discrete case) the contract curve
  3. Trade improves welfare

Bilateral Forage-and-Exchange model should demonstrate:
  1. Agents forage for resources based on distance-discounted marginal utility
  2. Agents exchange resources based on preference parameters
  3. Simple narrow-self-interest U-max foraging may not be optimal when exchange is possible

--

All this said -- the direction we need to go in code is to be sure we have *separate* models for the different types of interactions.

1. Single-agent utility maximization (forage)
2. Bilateral exchange (verify working in 2 and 3-agent cases before expanding to 4+ agents)
3. Bilateral forage-and-exchange (need to decide logic for combining forage and exchange behavior)

To do this, we will create a new folder in simulation/agent/ that will contain the models for each of these.
  agent/
    behaviors/
      forage.py (to demonstrate single-agent utility maximization, but should be generic enough to be reused for other models)
      bilateral_exchange.py
      market_exchange.py (not-yet-started)
        - this may need to be its own folder, with its own modules for different types of market exchange.
    __init__..py
    unified_decision.py
    modes.py (this + unified_decision will need to be rewritten/replaced to use the behaviors/ modules)
    utility_functions.py

This new structure will determine agent decisions, which will then be executed by the coordinator/executor.
    
