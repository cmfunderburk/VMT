"""Unified Decision Engine Executor (V2).

This module provides the UnifiedStepExecutor class that integrates with the new
unified decision engine architecture. It implements two-phase execution:

Phase 1 (Decision Collection): All agents make decisions using the unified decision
engine. Agent methods (deposit_to_home, withdraw_from_home) are called directly
as decision prerequisites. No global state changes occur.

Phase 2 (Action Execution): All special actions (collect, trade, pair, unpair)
are executed with proper coordination. Agent modes and targets are updated.

Design Principles:
- Two-phase execution maintains determinism (all decisions see same world state)
- Agent methods vs special actions: single-entity vs multi-entity operations
- Direct integration with unified decision engine
- Maintains compatibility with existing metrics and respawn systems
- Performance optimized with minimal overhead
"""

from __future__ import annotations

import random
from typing import TYPE_CHECKING

from .agent.core import Agent
from .agent.unified_decision import AgentAction, make_agent_decision
from .features import SimulationFeatures
from .world.coordinates import manhattan_distance

if TYPE_CHECKING:
    pass


class UnifiedStepExecutor:
    """Unified decision engine executor with two-phase execution.

    Integrates with the new unified decision architecture while maintaining
    compatibility with existing simulation systems (metrics, respawn, etc.).

    Two-Phase Execution:
    Phase 1: Collect all agent decisions (deterministic - no global state changes)
    Phase 2: Execute all actions (coordinated state changes)

    This ensures deterministic behavior: decision N cannot see state changes
    from decision N-1, since all decisions are made against the same world state.
    """

    def __init__(self, simulation, agents: list[Agent]):
        """Initialize unified step executor.

        Args:
            simulation: Reference to the main simulation instance
            agents: Initial list of agents (executor owns canonical runtime state)
        """
        self.simulation = simulation
        self.agents = agents  # Canonical agent list (executor owns runtime state)

        # Initialize respawn scheduler if configured (executor owns runtime components)
        self.respawn_scheduler = None
        if simulation.config and getattr(simulation.config, "enable_respawn", False):
            from .world.respawn import RespawnScheduler
            
            self.respawn_scheduler = RespawnScheduler(
                target_density=float(simulation.config.respawn_target_density),
                max_spawn_per_tick=int(simulation.config.max_spawn_per_tick),
                respawn_rate=float(simulation.config.respawn_rate),
            )

        # Cache feature flags once per simulation
        self._cached_features: SimulationFeatures | None = None
        self._features_dirty = True

    def execute_step(self, rng: random.Random) -> None:
        """Execute one simulation step using unified decision engine.

        Implements two-phase execution:
        1. Decision Collection: All agents make decisions using unified decision engine
        2. Action Execution: Execute all special actions with proper coordination

        Args:
            rng: External RNG for backward compatibility
        """
        # Direct variable access - no object creation
        step_num = self.simulation._steps + 1

        # Use configured features from coordinator (V2 system)
        features = self.simulation._cached_feature_flags
        if features is None:
            # Fallback to environment-based features if not configured
            features = SimulationFeatures.from_environment()

        # Execute unified decision engine (two-phase execution)
        self._execute_unified_decisions(rng, features, step_num)

        # Execute remaining phases (movement, collection, respawn)
        self._execute_movement(step_num, rng, features)
        self._execute_collection(step_num, features)
        self._execute_respawn(step_num, rng)

    def _execute_unified_decisions(
        self, rng: random.Random, features: SimulationFeatures, step_num: int
    ) -> None:
        """Execute unified decision engine with two-phase execution.

        **Two-Phase Execution**:
        Phase 1: Collect all agent decisions (deterministic - no global state changes)
        Phase 2: Execute all actions (coordinated state changes)

        This ensures deterministic behavior: decision N cannot see state changes
        from decision N-1, since all decisions are made against the same world state.

        NOTE: Agent methods (deposit_to_home, withdraw_from_home) are called during
        Phase 1 (decision collection) because they're prerequisites for decision-making,
        not outcomes to execute later.

        Args:
            rng: Random number generator
            features: Simulation feature flags
            step_num: Current step number
        """
        # PHASE 1: Collect all agent decisions (deterministic evaluation)
        # Agent methods like deposit_to_home() are called here as decision prerequisites
        agent_actions: list[tuple[Agent, AgentAction]] = []

        for agent in self.agents:
            action = make_agent_decision(
                agent, self.simulation.grid, self.agents, features, rng, step_num
            )
            agent_actions.append((agent, action))

        # PHASE 2: Execute all actions (coordinated state changes)
        # Only executor-coordinated special actions are handled here
        for agent, action in agent_actions:
            self._execute_agent_action(agent, action, step_num)

    def _execute_agent_action(self, agent: Agent, action: AgentAction, step_num: int) -> None:
        """Execute an AgentAction (update agent state).

        NOTE: Only executor-coordinated special actions are handled here. Agent methods
        like deposit_to_home() and withdraw_from_home() are called directly within
        decision logic, not here.

        **Special Actions (Executor-Coordinated)**:
        - "collect" - Multi-entity: grid resource + agent inventory
        - "trade" - Multi-entity: atomic swap between two agents
        - "pair" - Multi-entity: bidirectional partnership link
        - "unpair" - Multi-entity: safe bidirectional unlink

        **Agent Methods (Called in Decision Logic)**:
        - agent.deposit_to_home() - Single-entity: agent's own inventories
        - agent.withdraw_from_home() - Single-entity: agent's own inventories

        Args:
            agent: Agent to update
            action: Action to execute
            step_num: Current step number
        """
        # Update mode
        if action.mode != agent.mode:
            agent.mode = action.mode

        # Update target
        agent.target = action.target

        # Handle special actions (executor-coordinated events only)
        if action.special_action == "collect":
            self._execute_resource_collection(agent, action, step_num)
        elif action.special_action == "trade":
            self._execute_bilateral_trade(agent, action, step_num)
        elif action.special_action == "pair":
            self._execute_pairing(agent, action, step_num)
        elif action.special_action == "unpair":
            self._execute_unpairing(agent, action, step_num)

    def _execute_resource_collection(
        self, agent: Agent, action: AgentAction, step_num: int
    ) -> None:
        """Execute resource collection special action.

        Validates agent is at resource location, resource exists and has quantity > 0,
        calculates collectible amount, transfers resource to agent carrying inventory,
        and updates resource quantity on grid.

        Args:
            agent: Agent collecting resource
            action: Action containing resource target
            step_num: Current step number
        """
        if action.resource_target is None:
            return

        resource = action.resource_target

        # Validate agent at resource location
        if agent.x != resource.x or agent.y != resource.y:
            return

        # Check if resource exists on grid (binary resource model)
        if not self.simulation.grid.has_resource(resource.x, resource.y):
            return

        # Verify resource type matches and take it
        actual_type = self.simulation.grid.take_resource_type(resource.x, resource.y)
        if actual_type is None or actual_type != resource.resource_type:
            # Put it back if we took it but type doesn't match
            if actual_type is not None:
                self.simulation.grid.add_resource(resource.x, resource.y, actual_type)
            return

        # Calculate collectible amount (limited by carrying capacity)
        from .agent.utility_functions import CARRYING_CAPACITY

        current_carrying = sum(agent.carrying_inventory.values())
        available_capacity = CARRYING_CAPACITY - current_carrying

        if available_capacity <= 0:
            # Put resource back since we can't collect
            self.simulation.grid.add_resource(resource.x, resource.y, resource.resource_type)
            return

        # Collect 1 unit (binary resource model)
        collectible_amount = 1

        # Transfer resource to agent carrying inventory
        good_type = resource.good_type
        agent.carrying_inventory[good_type] = (
            agent.carrying_inventory.get(good_type, 0) + collectible_amount
        )

    def _execute_bilateral_trade(self, agent: Agent, action: AgentAction, step_num: int) -> None:
        """Execute bilateral trade special action.

        Performs atomic swap between two agents' carrying inventories.
        Validates both agents have required goods and executes the trade.
        Prevents duplicate execution by only allowing the lower ID agent to execute.

        Args:
            agent: Agent initiating trade
            action: Action containing trade details
            step_num: Current step number
        """
        if action.trade is None:
            return

        trade = action.trade
        partner_id = trade.partner_id

        # Prevent duplicate execution: only allow lower ID agent to execute
        if agent.id > partner_id:
            return

        # Find partner agent using O(1) lookup
        partner = self.simulation._find_agent_by_id(partner_id)

        if partner is None:
            return

        # Validate agents are co-located (distance 0 required for trade)
        distance = manhattan_distance(agent.x, agent.y, partner.x, partner.y)
        if distance != 0:
            return

        # Validate both agents have required goods in carrying inventory
        for good, quantity in trade.agent_gives.items():
            if agent.carrying_inventory.get(good, 0) < quantity:
                return

        for good, quantity in trade.agent_receives.items():
            if partner.carrying_inventory.get(good, 0) < quantity:
                return

        # Perform atomic swap
        for good, quantity in trade.agent_gives.items():
            agent.carrying_inventory[good] = agent.carrying_inventory.get(good, 0) - quantity
            partner.carrying_inventory[good] = partner.carrying_inventory.get(good, 0) + quantity

        for good, quantity in trade.agent_receives.items():
            partner.carrying_inventory[good] = partner.carrying_inventory.get(good, 0) - quantity
            agent.carrying_inventory[good] = agent.carrying_inventory.get(good, 0) + quantity

        # Store executed trade for visualization
        self.simulation.executed_trade = trade

        # Highlight for renderer (12 step lifetime consistent with legacy)
        self.simulation._last_trade_highlight = (
            int(agent.x),
            int(agent.y),
            self.simulation._steps + 12,
        )

    def _execute_pairing(self, agent: Agent, action: AgentAction, step_num: int) -> None:
        """Execute pairing special action with conflict resolution.

        Creates bidirectional trading partner link between two agents.
        Existing partnerships are respected - agents cannot steal partners.
        If multiple agents try to pair with the same target in one step,
        lower ID wins (deterministic tiebreaker).

        Args:
            agent: Agent initiating pairing
            action: Action containing partner ID
            step_num: Current step number
        """
        if action.partner_id is None:
            return

        # Don't allow pairing if this agent is already paired
        if agent.trading_partner is not None:
            return

        # Find partner agent using O(1) lookup
        partner = self.simulation._find_agent_by_id(action.partner_id)

        if partner is None:
            return

        # Respect existing partnerships - cannot steal partners
        if partner.trading_partner is not None:
            # Partner is already paired with someone else - pairing fails
            return

        # No conflicts - form partnership
        # Note: If multiple agents try to pair with same partner in one step,
        # only the first one to execute will succeed (others will see partner
        # is already paired). Since we process agents in ID order during
        # Phase 2 execution, lower ID agent wins automatically.
        agent.trading_partner = partner
        partner.trading_partner = agent

    def _execute_unpairing(self, agent: Agent, action: AgentAction, step_num: int) -> None:
        """Execute unpairing special action.

        Safely breaks bidirectional partnership link.

        Args:
            agent: Agent initiating unpairing
            action: Action (partner_id not used for unpairing)
            step_num: Current step number
        """
        if agent.trading_partner is not None:
            partner = agent.trading_partner
            # Clear bidirectional link
            agent.trading_partner = None
            if partner.trading_partner == agent:
                partner.trading_partner = None

    def _execute_movement_toward_partner(self, agent: Agent, partner: Agent) -> None:
        """Execute coordinated movement for paired agents toward each other.

        Both agents move toward each other using Manhattan distance, with special
        handling for diagonal and immediate adjacency cases.

        Args:
            agent: Agent to move
            partner: Trading partner
        """
        dx = partner.x - agent.x
        dy = partner.y - agent.y
        manhattan_dist = manhattan_distance(agent.x, agent.y, partner.x, partner.y)

        if manhattan_dist == 0:
            # Already co-located, no movement needed
            return
        elif manhattan_dist == 1:
            # Adjacent agents: only higher ID moves to avoid swapping places
            # Lower ID agent stays put, higher ID agent moves to co-locate
            if agent.id > partner.id:
                # Higher ID agent moves to lower ID agent's position (co-location)
                if dx != 0:
                    agent.x += 1 if dx > 0 else -1
                elif dy != 0:
                    agent.y += 1 if dy > 0 else -1
            # Lower ID agent does not move (stays in place)
        elif manhattan_dist == 2 and abs(dx) == 1 and abs(dy) == 1:
            # Diagonally adjacent - need to meet at orthogonal square
            # Lower ID agent moves first in X direction (deterministic)
            if agent.id < partner.id:
                # Lower ID agent picks the meeting direction (X-first for determinism)
                if dx != 0:
                    agent.x += 1 if dx > 0 else -1
            else:
                # Higher ID agent moves to meet at the square the lower ID agent will occupy
                # Since lower ID moved in X direction, higher ID moves in Y to meet
                if dy != 0:
                    agent.y += 1 if dy > 0 else -1
        else:
            # Distance > 2 or not diagonal - both agents move toward each other
            # Each agent moves one step in Manhattan direction with largest difference
            if abs(dx) >= abs(dy) and dx != 0:
                # Move in X direction (larger or equal difference)
                agent.x += 1 if dx > 0 else -1
            elif dy != 0:
                # Move in Y direction
                agent.y += 1 if dy > 0 else -1

    def _execute_movement(
        self, step_num: int, rng: random.Random, features: SimulationFeatures
    ) -> None:
        """Execute movement logic for unified decision engine with coordinated partner movement.

        Movement rules:
        - Trading partners: Coordinated movement with diagonal/adjacency handling
        - Non-partners: Manhattan movement (one axis per step, largest difference first)
        - Trades execute only at distance 0 (co-located)
        """
        # Track which agents have already moved (to avoid double-processing pairs)
        moved_agents = set()

        for agent in self.agents:
            if agent.id in moved_agents or agent.target is None:
                continue

            target_x, target_y = agent.target

            if agent.trading_partner is not None:
                # Coordinated movement for trading partners
                partner = agent.trading_partner

                # Verify this is actually movement toward the partner
                if (target_x, target_y) == (partner.x, partner.y):
                    # Move both agents toward each other simultaneously
                    self._execute_movement_toward_partner(agent, partner)
                    if partner.id not in moved_agents:  # Partner hasn't been processed yet
                        self._execute_movement_toward_partner(partner, agent)

                    # Mark both as processed
                    moved_agents.add(agent.id)
                    moved_agents.add(partner.id)
                else:
                    # Moving toward different target, use regular movement
                    self._execute_manhattan_movement(agent, target_x, target_y)
                    moved_agents.add(agent.id)
            else:
                # Regular Manhattan movement for unpaired agents
                self._execute_manhattan_movement(agent, target_x, target_y)
                moved_agents.add(agent.id)

    def _execute_manhattan_movement(self, agent: Agent, target_x: int, target_y: int) -> None:
        """Execute Manhattan movement for unpaired agents (one axis per step).

        Args:
            agent: Agent to move
            target_x: Target X coordinate
            target_y: Target Y coordinate
        """
        dx = target_x - agent.x
        dy = target_y - agent.y

        # Move in direction with largest difference first (Manhattan movement)
        if abs(dx) >= abs(dy) and dx != 0:
            # Move in X direction
            agent.x += 1 if dx > 0 else -1
        elif dy != 0:
            # Move in Y direction
            agent.y += 1 if dy > 0 else -1

    def _execute_collection(self, step_num: int, features: SimulationFeatures) -> None:
        """Placeholder for collection phase (collection handled by unified decisions).

        Collection is now handled by the unified decision engine through special actions.
        This method exists for structural consistency but performs no operations.
        """
        # Collection happens in _execute_resource_collection during decision execution phase
        pass

    def _execute_respawn(self, step_num: int, rng: random.Random) -> None:
        """Execute respawn logic for resources.

        Args:
            step_num: Current step number
            rng: Random number generator
        """
        sim = self.simulation
        scheduler = self.respawn_scheduler  # Executor owns respawn scheduler

        # Check if respawn is configured
        if scheduler is None or sim._rng is None:
            return

        interval = sim._respawn_interval
        if not interval or interval <= 0:
            return

        # Check if this is a respawn step
        prev_steps = sim._steps
        if (prev_steps % interval) != 0:
            return

        # Execute respawn
        try:
            scheduler.step(sim.grid, sim._rng, step_index=prev_steps)
        except Exception:  # pragma: no cover
            # Silently fail - respawn is not critical to simulation integrity
            pass


# Backward compatibility aliases
UnifiedOptimizedStepExecutor = UnifiedStepExecutor
StepExecutor = UnifiedStepExecutor
OptimizedStepExecutor = UnifiedStepExecutor

__all__ = [
    "UnifiedStepExecutor",
    "UnifiedOptimizedStepExecutor",
    "StepExecutor",
    "OptimizedStepExecutor",
]
