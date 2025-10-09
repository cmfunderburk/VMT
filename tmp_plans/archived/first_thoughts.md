# Economic Models

## Two-Agent Behaviors

### Overall Behavior

#### Cobb-Douglas Example
- `U = ((x + epsilon)^alpha * (y + epsilon)) ^beta` where alpha = (beta - 1)
- Distance discounting: `U = U * exp(-k * d^2)` where k is a constant and d is the distance between the two agents.
  - Foraging example:
    - Agent Bundle: (1, 9)
    - Agent alpha: 0.9
    - One manhattan distance away, there is 1 x; and in a different square 1 manhattan distance away, there is 1 y.
    - Agent calculates distance-discounted marginal utility of x and y.
      - MU_x = dU/dx = alpha * (x + epsilon)^(alpha - 1) * (y + epsilon)^beta * exp(-k * d^2)
      - MU_y = dU/dy = beta * (x + epsilon)^alpha * (y + epsilon)^(beta - 1) * exp(-k * d^2)
    - Since MU_x > MU_y, the agent will select x and move to that square
    - Once the agent arrives, agent collects x.
  - Bilateral exchange example, agents not yet co-located or paired, but within each other's perception radius:
    - Agent 1 Bundle: (1, 9); Agent 1 is at (0, 0)
    - Agent 2 Bundle: (9, 1); Agent 2 is at (3, 2)
    - Agent 1 alpha: 0.9
    - Agent 2 alpha: 0.1
    - Each agent scans its perception radius and finds the other agent.
    - Agents pair and move toward each other to co-locate.
    - Once colocated, agents check for a Pareto improvement.
        - Agents evaluate a 1-for-1 exchange of x for y. If it is a Pareto improvement, they exchange goods.
        - If not, they evaluate a 1-for-1 exchange of y for x. If it is a Pareto improvement, they exchange goods.
        - If not, they unpair and go about their business.
  - Market exchange example, agents within marketplace area:
    - Note to self: need to review Vernon Smith's work, particularly Rationality in Economics: Constructivist and Ecological Forms
        - In Rationality and Economics, he discusses how to design experimental market setups so that agents can learn about market prices.
        - The difficulty lies in implementing this into a spatial, discrete-time simulation.
          - Suppose we have 10 agents, each with Cobb-Douglas utility but different alpha values.
          - We initialize each agent's home with a random bundle of x and y.
          - Each agent withdraws goods from their home and moves to the marketplace.
          - CRITICAL PROBLEM ARISES: how do agents determine the price of x and y?
            - Suppose we have a "simple" reservation price mechanism:
              - Each agent submits its reservation price for x and y.
              - 


