Economic Models in the VMT EconSim Platform: A Guide for Validation This guide provides an overview
of the current economic models implemented in your simulation, their theoretical underpinnings, and
a structured approach to defining and validating them against formal economic principles.

1. Current State of Economic Models in the Simulation Your simulation currently implements three
   standard microeconomic utility functions, which form the basis of your agents' decision-making.
   The core logic for these models is found in src/econsim/simulation/agent/utility_functions.py and
   their application in src/econsim/simulation/agent/unified_decision.py.

Implemented Utility Functions: Cobb-Douglas Utility: U = (x + ε)^α * (y + ε)^β

Implementation: This is implemented in the CobbDouglasUtility class. It correctly models diminishing
marginal utility and smooth substitution between goods.

Behavior: Agents with these preferences will try to maintain a balanced consumption of both goods,
as seen in your "Pure Cobb-Douglas" test configuration (TEST_5_COBB_DOUGLAS).

Perfect Substitutes Utility: U = αx + βy

Implementation: Implemented as PerfectSubstitutesUtility. This function models a linear trade-off
between goods.

Behavior: Agents with these preferences will typically focus on acquiring the good that provides the
highest marginal utility per unit of effort (or distance), as seen in your "Pure Perfect
Substitutes" test (TEST_7_PERFECT_SUBSTITUTES).

Perfect Complements (Leontief) Utility: U = min(αx, βy)

Implementation: Implemented as PerfectComplementsUtility. This models goods that are consumed in
fixed proportions.

Behavior: Agents will seek to acquire goods in a fixed ratio, and having an excess of one good
provides no additional utility. This is reflected in the "Pure Leontief" test (TEST_6_LEONTIEF).

Agent Decision-Making: Your unified_decision.py file outlines how these utility functions are used
in practice. Key aspects include:

Utility Maximization: Agents make decisions to maximize their utility. This is a foundational
principle of microeconomics.

Dual Inventory System: Agents have both a carrying_inventory and a home_inventory. Utility is
calculated based on the total bundle (the sum of both inventories), which is the correct approach
from an economic perspective.

Distance Discounting: The value of a resource is discounted by its distance from the agent, using an
exponential distance discount factor. This is a good way to model the "cost" of acquiring a resource
in a spatial simulation.

Bilateral Trade: The simulation includes a mechanism for bilateral trade between agents, where
trades are only executed if they are Pareto improvements (i.e., at least one agent is better off,
and no agent is worse off).

2. Connecting Simulation to Formal Economic Theory The current implementation is a solid foundation,
   but there are some differences between the simulation and a formal economic model that are
   important to acknowledge for validation.

Aspect

Simulation Implementation

Formal Economic Model

How to Bridge the Gap

Budget/Constraint

Implicit (time, distance)

Explicit (income, prices)

Model time and distance as the "prices" of goods. For example, the cost of acquiring a good is the
time it takes to travel to it and collect it.

Prices

None

Central to most models

Prices can be emergent properties of the simulation (e.g., the ratio at which agents are willing to
trade).

Choice Set

Discrete (the set of visible resources and trade partners)

Continuous (all possible bundles)

This is a reasonable simplification for a grid-based world. The key is to ensure that the agent's
choice from the discrete set is still the one that maximizes its utility.

3. A Guide to Defining and Validating Economic Models Here is a step-by-step guide to help you
   formalize the economic models for validation, in line with your goals in initial_planning.md.

Step 1: Define the Agent's Problem For each utility function, start by formally writing down the
agent's optimization problem. In general, this will be:

Maximize U(x, y)

Subject to the constraints of the simulation (e.g., time, distance, availability of resources).

Step 2: Derive Expected Behaviors From the optimization problem, derive the expected behaviors of
the agents. This will be different for each utility function.

Cobb-Douglas: Agents should spend a fraction α of their "budget" on good x and a fraction β on good
y. In the simulation, this means they should balance their collection efforts according to their
preferences.

Perfect Substitutes: Agents should only pursue the good that gives them the highest "bang for the
buck" (i.e., the highest marginal utility per unit of cost/distance).

Perfect Complements: Agents should collect goods in a fixed ratio. If they have an excess of one
good, their next action should always be to acquire the other good.

Step 3: Create Validation Scenarios Design specific, simple scenarios in the simulation to test
these expected behaviors. The existing test configurations are a good starting point, but you might
want to create even more controlled experiments.

Example Scenarios:

Scenario 1: The Two-Good Choice: Place one of each resource type at equal distances from an agent.
The agent's choice will reveal its preferences.

Scenario 2: The Diminishing Returns Test: Place a cluster of one resource type and a single resource
of another type further away. A Cobb-Douglas agent should eventually switch to the further resource
as the marginal utility of the closer resource diminishes.

Scenario 3: The Trading Post: Place two agents with different initial endowments and complementary
preferences next to each other. They should immediately trade to a Pareto-optimal allocation.

Step 4: Compare Simulation to Theory Run the validation scenarios and compare the observed behavior
to the expected behavior you derived in Step 2. If there are discrepancies, they could be due to:

A bug in the simulation code.

An aspect of the simulation that is not captured in the formal model (e.g., competition from other
agents).

A misunderstanding of the economic theory.

This process will allow you to either validate your simulation or refine your understanding of the
economic models at play.

4. Example: A Deeper Dive into Cobb-Douglas Let's apply this process to the Cobb-Douglas model.

The Agent's Problem: An agent with utility U = x^α * y^(1-α) wants to maximize this utility by
choosing which resource to collect. The "cost" of a resource is the distance to it.

Expected Behavior: The agent will choose the resource that provides the highest marginal utility,
discounted by distance. The marginal utility of a good decreases as the agent accumulates more of
it.

Validation Scenario:

Create a 10x10 grid.

Place one agent at (5, 5) with a Cobb-Douglas utility function (α = 0.8). This agent strongly
prefers good 'A'.

Place a resource of type 'A' (good1) at (5, 6) (distance 1).

Place a resource of type 'B' (good2) at (5, 4) (distance 1).

Predicted Outcome: The agent should initially choose resource 'A'. As it collects more 'A', the
marginal utility of 'A' will decrease. Eventually, the distance-discounted marginal utility of 'B'
will become higher, and the agent should switch to collecting 'B', even though it has a lower
preference for it.

5. Next Steps and Advanced Models Your initial_planning.md document outlines a vision that goes
   beyond simple consumer choice to include market equilibrium, game theory, and information
   economics. The validation process described above will be crucial as you add these more complex
   models.

For example, when you move to market equilibrium, you can validate your model by checking if it
converges to the theoretical equilibrium prices and quantities. For game theory, you can set up
classic games like the Prisoner's Dilemma and see if your agents' strategies match the Nash
Equilibrium.

By taking the time to explicitly write down the economic models you are simulating, you will be able
to create a more robust and educationally valuable platform.
