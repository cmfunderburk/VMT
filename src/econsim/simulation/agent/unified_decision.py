"""Unified Decision Engine for Economic Agents.

This module implements the unified decision engine that replaces the legacy decision logic
with a clean, economic-theory-based approach. The design follows these key principles:

1. **Use agent properties directly** - No wrapper structures for agent state
2. **Two-phase execution** - Phase 1: decisions, Phase 2: coordination
3. **Agent methods vs special actions** - Single-entity vs multi-entity operations
4. **Total bundle utility** - Always use carrying + home for utility calculations
5. **Deterministic decisions** - RNG reserved for future stochastic extensions
6. **Pluggable utility functions** - Abstract base class with concrete implementations
7. **Economic correctness** - Each utility function implements standard economic theory

The decision engine provides a single entry point `make_agent_decision()` that dispatches
to appropriate decision modes based on enabled simulation features:
- `decide_forage_only()` - Resource collection and deposit
- `decide_bilateral_exchange_only()` - Partner seeking and trading
- `decide_dual_mode()` - Combined foraging and trading
- `decide_idle()` - All mechanisms disabled

All decisions are currently deterministic utility maximizers. The RNG parameter is
unused but reserved for future stochastic extensions (bounded rationality, exploration
noise, probabilistic trade acceptance).

Architecture:
- Minimal data structures for external entities (ResourceInfo, AgentInfo)
- Economic utility functions in separate module (utility_functions.py)
- Direct agent property access (no perception wrappers)
- Special actions for executor-coordinated events (collect, trade, pair, unpair)
- Agent methods for single-entity state changes (deposit_to_home, withdraw_from_home)
"""

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Optional

from ..constants import AgentMode
from ..world.coordinates import manhattan_distance

if TYPE_CHECKING:
    from econsim.simulation.agent.core import Agent
    from econsim.simulation.features import SimulationFeatures
    from econsim.simulation.world.grid import Grid


# ============================================================================
# EXTERNAL ENTITY DESCRIPTORS (New Abstractions - Justified)
# ============================================================================


@dataclass(slots=True)
class ResourceInfo:
    """Lightweight descriptor for grid resources.

    Justified: Resources are grid entities, not agent properties.
    This avoids coupling decision logic to Grid implementation.
    """

    x: int  # Grid x-coordinate
    y: int  # Grid y-coordinate
    resource_type: str  # "A" or "B"
    good_type: str  # "good1" or "good2"
    quantity: int  # Available quantity (currently 1 per resource)
    distance: int  # Manhattan distance from agent

    @classmethod
    def from_resource(
        cls, x: int, y: int, resource_type: str, agent_x: int, agent_y: int
    ) -> "ResourceInfo":
        """Create ResourceInfo from grid resource coordinates and type.

        Args:
            x: Resource x-coordinate
            y: Resource y-coordinate
            resource_type: "A" or "B"
            agent_x: Observing agent's x-coordinate
            agent_y: Observing agent's y-coordinate

        Returns:
            ResourceInfo descriptor
        """
        distance = manhattan_distance(x, y, agent_x, agent_y)
        good_type = "good1" if resource_type == "A" else "good2"
        return cls(
            x=x,
            y=y,
            resource_type=resource_type,
            good_type=good_type,
            quantity=1,  # Current grid implementation has binary resources
            distance=distance,
        )


@dataclass(slots=True)
class AgentInfo:
    """Lightweight descriptor for other agents.

    Justified: Describes agents in environment, avoids circular references.
    """

    agent_id: int  # Agent ID
    x: int  # Grid x-coordinate
    y: int  # Grid y-coordinate
    distance: int  # Manhattan distance
    is_paired: bool  # Whether agent is already paired
    has_goods: bool  # Whether agent has goods to trade
    agent_ref: "Agent"  # Reference for integration

    @classmethod
    def from_agent(cls, other: "Agent", observer: "Agent") -> "AgentInfo":
        """Create AgentInfo from another agent.

        Args:
            other: Agent to describe
            observer: Agent making the observation

        Returns:
            AgentInfo descriptor
        """
        distance = manhattan_distance(other.x, other.y, observer.x, observer.y)

        # Check if agent is paired (has a trading partner)
        has_partner = other.trading_partner is not None

        # Check if agent has goods in carrying inventory
        has_goods = any(quantity > 0 for quantity in other.carrying_inventory.values())

        return cls(
            agent_id=other.id,
            x=other.x,
            y=other.y,
            distance=distance,
            is_paired=has_partner,
            has_goods=has_goods,
            agent_ref=other,
        )


# ============================================================================
# DECISION OUTPUT (New Abstraction - Justified)
# ============================================================================


@dataclass(slots=True)
class BilateralTrade:
    """Bilateral trade specification.

    Justified: Trade proposals are new domain concepts, not existing properties.
    """

    agent_gives: dict[str, int]  # Resources agent gives up
    agent_receives: dict[str, int]  # Resources agent receives
    partner_id: int  # Trading partner ID
    agent_utility_gain: float  # Agent's utility improvement
    partner_utility_gain: float  # Partner's utility improvement
    is_pareto_improvement: bool  # True if both agents benefit


@dataclass(slots=True)
class AgentAction:
    """Decision engine output - specifies agent's next action.

    Justified: Decision results need structured return type for executor integration.

    **Special Actions vs Agent Methods**:

    Special actions are **executor-coordinated events** that require multi-entity
    or global state management:
    - "collect" - Updates grid resource AND agent inventory atomically
    - "trade" - Updates TWO agents' inventories in atomic transaction
    - "pair" - Creates bidirectional trading_partner link between agents
    - "unpair" - Safely breaks bidirectional partnership link

    Agent methods are **single-agent state mutations** called directly by decision logic:
    - agent.deposit_to_home(goods) - Transfers carrying → home inventory
    - agent.withdraw_from_home(goods) - Transfers home → carrying inventory
    - agent.move(dx, dy) - Updates agent position

    **Key distinction**: If it affects multiple entities or requires executor coordination,
    it's a special action. If it's a pure agent state change, it's a method.
    """

    mode: AgentMode  # Target mode (FORAGE, MOVE_TO_PARTNER, etc.)
    target: tuple[int, int] | None  # Target coordinates
    special_action: str | None  # "collect", "trade", "pair", "unpair"
    trade: BilateralTrade | None  # Trade to execute (if applicable)
    partner_id: int | None  # Partner to pair with (if applicable)
    resource_target: ResourceInfo | None  # Resource being targeted (for debugging)
    reason: str = ""  # Human-readable explanation
    decision_metadata: dict[str, Any] = field(default_factory=dict)  # Debug info


# ============================================================================
# PERCEPTION HELPERS (Minimal Abstraction Layer)
# ============================================================================

# Import economic constants and helpers from utility_functions module
from .utility_functions import (
    CARRYING_CAPACITY,
    MIN_TRADE_UTILITY_GAIN,
    PERCEPTION_RADIUS,
    calculate_agent_utility,
    calculate_resource_net_utility,  # type: ignore
    get_agent_total_bundle,
)


def find_nearby_resources(agent: "Agent", grid: "Grid") -> list["ResourceInfo"]:
    """Find all resources within perception radius.

    Scans all resources in the grid and filters by distance and availability.
    Returns resources sorted by distance (nearest first) for deterministic behavior.

    Args:
        agent: Observing agent
        grid: World grid containing resources

    Returns:
        List of ResourceInfo descriptors, sorted by distance (nearest first),
        then by position for determinism
    """
    nearby = []

    # Scan all resources in grid
    for x, y, resource_type in grid.iter_resources():
        distance = manhattan_distance(x, y, agent.x, agent.y)

        # Filter by perception radius and availability (quantity > 0)
        if distance <= PERCEPTION_RADIUS:
            resource_info = ResourceInfo.from_resource(x, y, resource_type, agent.x, agent.y)
            nearby.append(resource_info)  # type: ignore

    # Sort by distance (nearest first), then by position for determinism
    nearby.sort(key=lambda r: (r.distance, r.x, r.y))  # type: ignore

    return nearby  # type: ignore


def find_nearby_agents(agent: "Agent", all_agents: list["Agent"]) -> list["AgentInfo"]:
    """Find all agents within perception radius.

    Scans all agents in simulation and filters by distance, excluding self.
    Returns agents sorted by distance (nearest first) for deterministic behavior.

    Args:
        agent: Observing agent
        all_agents: All agents in simulation

    Returns:
        List of AgentInfo descriptors, sorted by distance (nearest first),
        then by ID for determinism
    """
    nearby = []

    # Scan all agents in simulation
    for other in all_agents:
        # Skip self
        if other.id == agent.id:
            continue

        distance = manhattan_distance(other.x, other.y, agent.x, agent.y)

        # Filter by perception radius
        if distance <= PERCEPTION_RADIUS:
            agent_info = AgentInfo.from_agent(other, agent)
            nearby.append(agent_info)  # type: ignore

    # Sort by distance, then by ID for determinism
    nearby.sort(key=lambda a: (a.distance, a.agent_id))  # type: ignore

    return nearby  # type: ignore


# ============================================================================
# BILATERAL TRADE EVALUATION
# ============================================================================


def find_beneficial_bilateral_trade(agent: "Agent", partner: "Agent") -> Optional["BilateralTrade"]:
    """Find single best bilateral trade between agents.

    **Trade Structure**: All trades are strictly 1-for-1 exchanges (1 unit of good A
    for 1 unit of good B). This simplification maintains clear economic interpretation
    while avoiding complexity of multi-unit negotiation.

    **Economic Logic**: Agents evaluate trades based on total wealth (carrying + home)
    but can only execute trades from carrying inventory. This handles the edge case
    where a theoretically beneficial trade cannot be executed due to goods being
    stored at home rather than carried.

    Args:
        agent: First agent (initiator)
        partner: Second agent (responder)

    Returns:
        BilateralTrade if mutually beneficial AND executable trade exists, else None
    """
    # Check what goods are actually available for trading (carrying inventory only)
    agent_carrying = agent.carrying_inventory
    partner_carrying = partner.carrying_inventory

    best_trade = None
    best_joint_gain = 0.0

    # Enumerate all possible 1-for-1 trades (only from carrying inventory)
    for agent_gives_good in agent_carrying:
        if agent_carrying[agent_gives_good] <= 0:
            continue

        for partner_gives_good in partner_carrying:
            if partner_carrying[partner_gives_good] <= 0:
                continue

            # Can't trade same good for same good
            if agent_gives_good == partner_gives_good:
                continue

            # Calculate utility gains for both parties
            agent_utility_gain = _calculate_trade_utility_gain(
                agent, agent_gives_good, partner_gives_good
            )
            partner_utility_gain = _calculate_trade_utility_gain(
                partner, partner_gives_good, agent_gives_good
            )

            # Only consider Pareto improvements
            if (
                agent_utility_gain > MIN_TRADE_UTILITY_GAIN
                and partner_utility_gain > MIN_TRADE_UTILITY_GAIN
            ):

                joint_gain = agent_utility_gain + partner_utility_gain

                if joint_gain > best_joint_gain:
                    best_joint_gain = joint_gain
                    best_trade = BilateralTrade(
                        agent_gives={agent_gives_good: 1},
                        agent_receives={partner_gives_good: 1},
                        partner_id=partner.id,
                        agent_utility_gain=agent_utility_gain,
                        partner_utility_gain=partner_utility_gain,
                        is_pareto_improvement=True,
                    )

    return best_trade


def _calculate_trade_utility_gain(agent: "Agent", gives_good: str, receives_good: str) -> float:
    """Calculate utility change from trading one resource for another.

    **Correct Economic Behavior**: Uses total bundle (carrying + home) for utility
    evaluation because agents know their total wealth and make decisions based on
    overall portfolio impact. The trade execution only affects carrying inventory,
    but the economic value is assessed against total holdings.

    This is economically sound: if I have 10 good1 at home + 1 good1 carrying,
    trading away the carried good1 reduces my total from 11→10, which is the
    correct opportunity cost for the trade decision.

    Args:
        agent: Agent making the trade
        gives_good: Good being given up (from carrying inventory)
        receives_good: Good being received (to carrying inventory)

    Returns:
        Utility change (positive = beneficial, negative = harmful)
    """
    current_utility = calculate_agent_utility(agent)

    # Start with current total bundle
    post_trade_bundle = get_agent_total_bundle(agent)

    # Apply trade to total bundle
    post_trade_bundle[gives_good] = post_trade_bundle.get(gives_good, 0) - 1
    post_trade_bundle[receives_good] = post_trade_bundle.get(receives_good, 0) + 1

    post_trade_utility = agent.utility_function.calculate_utility(post_trade_bundle)  # type: ignore

    return post_trade_utility - current_utility  # type: ignore


def find_best_trading_partner(
    agent: "Agent", nearby_agents: list["AgentInfo"]
) -> Optional["AgentInfo"]:
    """Find best trading partner from nearby agents.

    **Partnership Tiebreaking**: When multiple agents offer equal utility gains,
    select the agent with the lowest ID. This ensures deterministic behavior and
    prevents partnership conflicts.

    Args:
        agent: Agent seeking partner
        nearby_agents: List of nearby agent descriptors

    Returns:
        Best partner if beneficial trade exists, else None
    """
    # Early exit: Can't trade if initiating agent has no goods
    if not _has_carrying_goods(agent):
        return None

    best_partner = None
    best_trade_gain = 0.0

    for candidate in nearby_agents:
        # Skip if already paired or no goods
        if candidate.is_paired or not candidate.has_goods:
            continue

        # Evaluate potential trade
        trade = find_beneficial_bilateral_trade(agent, candidate.agent_ref)

        if trade and trade.agent_utility_gain > best_trade_gain:
            best_trade_gain = trade.agent_utility_gain
            best_partner = candidate

    # Deterministic tiebreaking by lowest ID
    if best_partner and best_trade_gain > MIN_TRADE_UTILITY_GAIN:
        # Check for ties
        ties = []
        for candidate in nearby_agents:
            if candidate.is_paired or not candidate.has_goods:
                continue
            trade = find_beneficial_bilateral_trade(agent, candidate.agent_ref)
            if trade and abs(trade.agent_utility_gain - best_trade_gain) < 1e-9:
                ties.append(candidate)  # type: ignore

        if len(ties) > 1:  # type: ignore
            # Resolve by lowest ID (ensures deterministic pairing order)
            best_partner = min(ties, key=lambda c: c.agent_id)  # type: ignore

    return best_partner  # type: ignore


# ============================================================================
# ACTION CONSTRUCTION HELPERS
# ============================================================================


def _find_best_resource(agent: "Agent", nearby_resources: list["ResourceInfo"]) -> Optional["ResourceInfo"]:  # type: ignore
    """Find resource with highest distance-discounted utility.

    Calculates net utility (marginal utility minus distance discount) for each
    resource and returns the one with highest positive utility.

    Args:
        agent: Agent evaluating resources
        nearby_resources: List of nearby resource descriptors

    Returns:
        ResourceInfo with highest positive net utility, or None if none beneficial
    """
    if not nearby_resources:
        return None

    best_resource = None
    best_utility = 0.0

    for resource in nearby_resources:
        net_utility = calculate_resource_net_utility(agent, resource)  # type: ignore

        if net_utility > best_utility:
            best_utility = net_utility
            best_resource = resource

    return best_resource if best_utility > 0 else None


def _move_to_resource_action(agent: "Agent", resource: "ResourceInfo", step: int) -> "AgentAction":  # type: ignore
    """Construct action to move toward resource.

    Calculates greedy movement toward resource. If agent is already at resource,
    sets special_action="collect" for executor coordination.

    Args:
        agent: Agent taking action
        resource: Target resource descriptor
        step: Current simulation step

    Returns:
        AgentAction with FORAGE mode and appropriate special_action
    """
    # Check if at resource
    if agent.x == resource.x and agent.y == resource.y:
        special_action = "collect"
    else:
        special_action = None

    return AgentAction(
        mode=AgentMode.FORAGE,
        target=(resource.x, resource.y),
        special_action=special_action,
        trade=None,
        partner_id=None,
        resource_target=resource,
        reason=f"pursuing resource at ({resource.x}, {resource.y})",
    )


def _move_to_partner_action(agent: "Agent", partner: "Agent", step: int) -> "AgentAction":  # type: ignore
    """Construct action to move toward trading partner.

    Calculates greedy movement toward partner for continued partnership.

    Args:
        agent: Agent taking action
        partner: Trading partner agent
        step: Current simulation step

    Returns:
        AgentAction with MOVE_TO_PARTNER mode
    """
    return AgentAction(
        mode=AgentMode.MOVE_TO_PARTNER,
        target=(partner.x, partner.y),
        special_action=None,
        trade=None,
        partner_id=partner.id,
        resource_target=None,
        reason=f"moving toward partner {partner.id}",
    )


def _initiate_pairing_action(agent: "Agent", partner_info: "AgentInfo", step: int) -> "AgentAction":  # type: ignore
    """Construct action to initiate pairing with trading partner.

    Calculates movement toward partner and sets special_action="pair" for
    executor coordination of bidirectional partnership creation.

    Args:
        agent: Agent taking action
        partner_info: Target partner descriptor
        step: Current simulation step

    Returns:
        AgentAction with MOVE_TO_PARTNER mode and special_action="pair"
    """
    partner = partner_info.agent_ref

    return AgentAction(
        mode=AgentMode.MOVE_TO_PARTNER,
        target=(partner.x, partner.y),
        special_action="pair",
        trade=None,
        partner_id=partner.id,
        resource_target=None,
        reason=f"pairing with agent {partner.id}",
    )


def _return_home_action(agent: "Agent", step: int, reason: str = "") -> "AgentAction":  # type: ignore
    """Construct action to return home.

    Calculates movement toward home location. If already at home, sets
    target=None. Note: This function NEVER returns special_action="deposit".
    Deposits are handled as direct agent method calls within decision functions,
    not as executor-coordinated special actions.

    Args:
        agent: Agent taking action
        step: Current simulation step
        reason: Human-readable explanation for action

    Returns:
        AgentAction with RETURN_HOME mode
    """
    at_home = agent.x == agent.home_x and agent.y == agent.home_y  # type: ignore

    if at_home:
        # Already home - no movement needed
        # Note: Any required deposits should be handled by caller via agent.deposit_to_home()
        target = None
    else:
        # Set target to home location
        target = (agent.home_x, agent.home_y)  # type: ignore

    return AgentAction(
        mode=AgentMode.RETURN_HOME,
        target=target,
        special_action=None,  # Never "deposit" - handled by direct method calls
        trade=None,
        partner_id=None,
        resource_target=None,
        reason=reason or "returning home",
    )  # type: ignore


# ============================================================================
# DECISION ALGORITHMS
# ============================================================================


def decide_forage_only(
    agent: "Agent",
    nearby_resources: list["ResourceInfo"],
    rng: Any,  # UNUSED: Reserved for future stochastic extensions
    step: int,
) -> "AgentAction":  # type: ignore
    """Forage-only mode: collect resources and return home.

    Currently implements deterministic utility maximization. The `rng` parameter
    is unused but reserved for future stochastic decision-making.

    **Carrying Capacity**: Set to 100,000 units (effectively unlimited for typical
    scenarios, but provides future constraint point if needed).

    Priority order:
    1. Carrying inventory full + at home → deposit and continue
    2. Carrying inventory full + away → return home
    3. Find resource to collect
    4. No resources available → idle

    NOTE: Deposit uses agent.deposit_to_home() method (agent-local state change),
    not special action (which would be executor-coordinated event).

    Args:
        agent: Agent making decision
        nearby_resources: List of nearby resource descriptors
        rng: Random number generator (UNUSED - reserved for future extensions)
        step: Current simulation step

    Returns:
        AgentAction specifying next action
    """
    # Check inventory state
    inventory_full = _is_inventory_full(agent)
    at_home = _is_at_home(agent)

    # Priority 1: Full inventory at home → deposit directly and continue
    if inventory_full and at_home:
        # Call agent method directly - pure state change, no executor coordination
        all_goods = agent.carrying_inventory.copy()
        agent.deposit_to_home(all_goods)  # type: ignore
        # After deposit, recalculate inventory status
        inventory_full = _is_inventory_full(agent)

    # Priority 2: Full inventory away from home → return to deposit
    if inventory_full:  # Still full (didn't deposit above)
        return _return_home_action(agent, step, reason="inventory full - returning to deposit")

    # Priority 3: Find resource to collect
    best_resource = _find_best_resource(agent, nearby_resources)

    if best_resource:
        return _move_to_resource_action(agent, best_resource, step)

    # Priority 4: No resources → idle
    return AgentAction(
        mode=AgentMode.IDLE,
        target=None,
        special_action=None,
        trade=None,
        partner_id=None,
        resource_target=None,
        reason="no resources available",
    )  # type: ignore


def _is_inventory_full(agent: "Agent") -> bool:
    """Check if agent's carrying inventory is full.

    Uses CARRYING_CAPACITY constant to determine if agent has reached
    maximum carrying capacity.

    Args:
        agent: Agent to check

    Returns:
        True if carrying inventory is at or above capacity
    """
    total_carrying = sum(agent.carrying_inventory.values())
    return total_carrying >= CARRYING_CAPACITY


def _is_at_home(agent: "Agent") -> bool:
    """Check if agent is at home location.

    Args:
        agent: Agent to check

    Returns:
        True if agent is at home coordinates
    """
    return agent.x == agent.home_x and agent.y == agent.home_y  # type: ignore


def decide_bilateral_exchange_only(
    agent: "Agent",
    nearby_agents: list["AgentInfo"],
    rng: Any,  # UNUSED: Reserved for future stochastic extensions
    step: int,
) -> "AgentAction":  # type: ignore
    """Bilateral exchange only mode: seek partners and trade.

    Currently implements deterministic utility maximization. The `rng` parameter
    is unused but reserved for future stochastic decision-making.

    **Withdrawal Strategy**: Speculative - agents withdraw all home goods when
    carrying is empty, enabling immediate trade evaluation without waiting for
    confirmed opportunities.

    Priority order:
    1. Has partner + co-located → trade (or unpair if no beneficial trade)
    2. Has partner + distant → move toward
    3. No partner + has carrying goods → seek partner
    4. No partner + empty carrying + home goods + at home → withdraw speculatively
    5. No partner + empty carrying + home goods + away → return home to withdraw
    6. No goods anywhere → idle

    NOTE: Withdrawal uses agent.withdraw_from_home() method (agent-local), not
    special action. This is a prerequisite for trade evaluation, not an executor event.

    Args:
        agent: Agent making decision
        nearby_agents: List of nearby agent descriptors
        rng: Random number generator (UNUSED - reserved for future extensions)
        step: Current simulation step

    Returns:
        AgentAction specifying next action
    """
    # Check for existing partner (use agent property directly)
    if _has_trading_partner(agent):
        partner = _get_trading_partner(agent)

        # Check if agent has goods to trade - dissolve partnership if not
        if not _has_carrying_goods(agent):
            return AgentAction(
                mode=AgentMode.FORAGE,
                target=None,
                special_action="unpair",  # Executor-coordinated: two agents
                trade=None,
                partner_id=None,
                resource_target=None,
                reason="no goods to trade - dissolving partnership",
            )  # type: ignore

        # Co-located check
        if _is_co_located(agent, partner):
            trade = find_beneficial_bilateral_trade(agent, partner)

            if trade:
                # Special action "trade" - executor coordinates atomic inventory swap
                return AgentAction(
                    mode=AgentMode.MOVE_TO_PARTNER,
                    target=(partner.x, partner.y),
                    special_action="trade",  # Executor-coordinated: two agents
                    trade=trade,
                    partner_id=partner.id,
                    resource_target=None,
                    reason="executing trade",
                )  # type: ignore
            else:
                # Special action "unpair" - executor breaks bidirectional link
                return AgentAction(
                    mode=AgentMode.FORAGE,
                    target=None,
                    special_action="unpair",  # Executor-coordinated: two agents
                    trade=None,
                    partner_id=None,
                    resource_target=None,
                    reason="unpairing - no beneficial trade",
                )  # type: ignore
        else:
            # Move toward partner
            return _move_to_partner_action(agent, partner, step)

    # Check carrying inventory status
    has_carrying_goods = _has_carrying_goods(agent)
    has_home_goods = _has_home_goods(agent)
    at_home = _is_at_home(agent)

    # Priority 3: Seek new partner if has carrying goods
    if has_carrying_goods:
        best_partner = find_best_trading_partner(agent, nearby_agents)

        if best_partner:
            return _initiate_pairing_action(agent, best_partner, step)

    # Priority 4: Withdraw bootstrap - enable trading when carrying empty but home full
    if not has_carrying_goods and has_home_goods:
        if at_home:
            # Call agent method directly - prerequisite for trade evaluation
            # Agent-local state change, no executor coordination needed
            all_home_goods = agent.home_inventory.copy()  # type: ignore
            agent.withdraw_from_home(all_home_goods)  # type: ignore

            # After withdrawal, immediately try to find partner
            best_partner = find_best_trading_partner(agent, nearby_agents)
            if best_partner:
                return _initiate_pairing_action(agent, best_partner, step)

            # No partner available after withdrawal, idle
            return AgentAction(
                mode=AgentMode.IDLE,
                target=None,
                special_action=None,
                trade=None,
                partner_id=None,
                resource_target=None,
                reason="withdrew goods but no trading partners available",
            )  # type: ignore
        else:
            # Return home to withdraw
            return _return_home_action(
                agent, step, reason="returning home to withdraw goods for trading"
            )

    # Priority 6: No goods anywhere → idle
    return AgentAction(
        mode=AgentMode.IDLE,
        target=None,
        special_action=None,
        trade=None,
        partner_id=None,
        resource_target=None,
        reason="no goods to trade",
    )  # type: ignore


def _has_trading_partner(agent: "Agent") -> bool:
    """Check if agent has an existing trading partner.

    Args:
        agent: Agent to check

    Returns:
        True if agent has a trading partner
    """
    return agent.trading_partner is not None  # type: ignore


def _get_trading_partner(agent: "Agent") -> "Agent":
    """Get agent's current trading partner.

    Args:
        agent: Agent to get partner for

    Returns:
        Trading partner agent

    Raises:
        ValueError: If agent has no trading partner
    """
    if not _has_trading_partner(agent):
        raise ValueError(f"Agent {agent.id} has no trading partner")

    # This would need to be implemented to find the partner agent by ID
    # For now, we'll assume the partner is accessible via agent.trading_partner
    return agent.trading_partner  # type: ignore


def _is_co_located(agent: "Agent", partner: "Agent") -> bool:
    """Check if agent and partner are at the same location.

    Args:
        agent: First agent
        partner: Second agent

    Returns:
        True if agents are at the same coordinates
    """
    return agent.x == partner.x and agent.y == partner.y


def _has_carrying_goods(agent: "Agent") -> bool:
    """Check if agent has goods in carrying inventory.

    Args:
        agent: Agent to check

    Returns:
        True if carrying inventory has any goods
    """
    return any(quantity > 0 for quantity in agent.carrying_inventory.values())


def _has_home_goods(agent: "Agent") -> bool:
    """Check if agent has goods in home inventory.

    Args:
        agent: Agent to check

    Returns:
        True if home inventory has any goods
    """
    return any(quantity > 0 for quantity in agent.home_inventory.values())  # type: ignore


def decide_dual_mode(
    agent: "Agent",
    nearby_resources: list["ResourceInfo"],
    nearby_agents: list["AgentInfo"],
    rng: Any,  # UNUSED: Reserved for future stochastic extensions
    step: int,
) -> "AgentAction":  # type: ignore
    """Dual mode: forage + bilateral exchange.

    Currently implements deterministic utility maximization. The `rng` parameter
    is unused but reserved for future stochastic decision-making.

    **Carrying Capacity**: Set to 100,000 units (effectively unlimited for typical
    scenarios, but provides future constraint point if needed).

    **Withdrawal Strategy**: Speculative - agents withdraw home goods when carrying
    is empty to enable trade evaluation, regardless of confirmed trade opportunities.

    Priority order:
    1. Full inventory + at home → deposit and continue
    2. Full inventory + away → return home to deposit
    3. Has existing trading partner → continue partnership (move/trade/unpair)
    4. Empty carrying + resources available → forage for resources (PRIORITY)
    5. Has carrying goods + partner available → seek partner
    6. Empty carrying + no resources + home goods + at home → withdraw speculatively
    7. Empty carrying + no resources + home goods + away → return to withdraw
    8. No opportunities → idle

    NOTE: Deposit/withdrawal use agent methods (agent-local), not special actions.
    Trade/pair/unpair are special actions (executor-coordinated).

    Args:
        agent: Agent making decision
        nearby_resources: List of nearby resource descriptors
        nearby_agents: List of nearby agent descriptors
        rng: Random number generator (UNUSED - reserved for future extensions)
        step: Current simulation step

    Returns:
        AgentAction specifying next action
    """
    # Check agent state
    inventory_full = _is_inventory_full(agent)
    has_carrying_goods = _has_carrying_goods(agent)
    has_home_goods = _has_home_goods(agent)
    at_home = _is_at_home(agent)

    # Priority 1: Full inventory at home → deposit directly and continue
    if inventory_full and at_home:
        # Call agent method directly - pure state change
        all_goods = agent.carrying_inventory.copy()  # type: ignore
        agent.deposit_to_home(all_goods)  # type: ignore
        # After deposit, recalculate inventory status
        inventory_full = _is_inventory_full(agent)
        has_carrying_goods = _has_carrying_goods(agent)

    # Priority 2: Full inventory away from home → return to deposit
    if inventory_full:  # Still full (didn't deposit above)
        return _return_home_action(agent, step, reason="inventory full - returning to deposit")

    # Priority 3: Check for existing trading partner (only if can actually trade)
    if _has_trading_partner(agent):
        partner = _get_trading_partner(agent)

        # Check if agent has goods to trade - dissolve partnership if not
        if not _has_carrying_goods(agent):
            return AgentAction(
                mode=AgentMode.FORAGE,
                target=None,
                special_action="unpair",  # Executor-coordinated
                trade=None,
                partner_id=None,
                resource_target=None,
                reason="no goods to trade - dissolving partnership",
            )  # type: ignore

        # Co-located with partner
        if _is_co_located(agent, partner):
            trade = find_beneficial_bilateral_trade(agent, partner)

            if trade:
                # Special action "trade" - executor coordinates atomic swap
                return AgentAction(
                    mode=AgentMode.MOVE_TO_PARTNER,
                    target=(partner.x, partner.y),
                    special_action="trade",  # Executor-coordinated
                    trade=trade,
                    partner_id=partner.id,
                    resource_target=None,
                    reason="executing beneficial trade",
                )  # type: ignore
            else:
                # Special action "unpair" - executor breaks link
                return AgentAction(
                    mode=AgentMode.FORAGE,
                    target=None,
                    special_action="unpair",  # Executor-coordinated
                    trade=None,
                    partner_id=None,
                    resource_target=None,
                    reason="no beneficial trade - unpairing",
                )  # type: ignore
        else:
            # Move toward partner
            return _move_to_partner_action(agent, partner, step)

    # Priority 4: Seek trading partner (if has carrying goods)
    if has_carrying_goods:
        best_partner = find_best_trading_partner(agent, nearby_agents)

        if best_partner:
            return _initiate_pairing_action(agent, best_partner, step)

    # Priority 5: Forage (always try to forage if resources available)
    best_resource = _find_best_resource(agent, nearby_resources)

    if best_resource:
        return _move_to_resource_action(agent, best_resource, step)

    # Priority 6: Withdraw bootstrap (fallback when no forage opportunities)
    if not has_carrying_goods and has_home_goods:
        if at_home:
            # Call agent method directly - prerequisite for trade evaluation
            all_home_goods = agent.home_inventory.copy()  # type: ignore
            agent.withdraw_from_home(all_home_goods)  # type: ignore

            # After withdrawal, try to find partner
            best_partner = find_best_trading_partner(agent, nearby_agents)
            if best_partner:
                return _initiate_pairing_action(agent, best_partner, step)

            # No partner after withdrawal, idle
            return AgentAction(
                mode=AgentMode.IDLE,
                target=None,
                special_action=None,
                trade=None,
                partner_id=None,
                resource_target=None,
                reason="withdrew goods but no trading partners available",
            )  # type: ignore
        else:
            # Return home to withdraw
            return _return_home_action(
                agent, step, reason="no forage opportunities - returning to withdraw for trading"
            )

    # Priority 7: Return home (fallback when carrying goods and no other targets)
    if has_carrying_goods and not at_home:
        return _return_home_action(
            agent, step, reason="carrying goods with no targets - returning home to deposit"
        )

    # Priority 8: No opportunities → idle
    return AgentAction(
        mode=AgentMode.IDLE,
        target=None,
        special_action=None,
        trade=None,
        partner_id=None,
        resource_target=None,
        reason="no opportunities available",
    )  # type: ignore


def decide_idle(agent: "Agent", step: int) -> "AgentAction":  # type: ignore
    """Idle mode: all mechanisms disabled.

    This function is called when:
    1. Both forage and trade mechanisms are disabled (features off), OR
    2. Active modes delegate when no opportunities available

    NOTE: Deposit/withdrawal logic is handled within active decision modes
    (forage/trade/dual) where they have specific contexts (e.g., "inventory full"
    or "withdraw bootstrap"). Idle mode does not manage inventory transfers.

    **Design decision**: Explicit delegation from active modes rather than
    automatic wrapper fallback. This makes control flow clear and testable.

    Args:
        agent: Agent making decision (unused but required for interface consistency)
        step: Current simulation step (unused but required for interface consistency)

    Returns:
        AgentAction with IDLE mode and appropriate reason
    """
    return AgentAction(
        mode=AgentMode.IDLE,
        target=None,
        special_action=None,
        trade=None,
        partner_id=None,
        resource_target=None,
        reason="all mechanisms disabled",
    )  # type: ignore


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================


def make_agent_decision(
    agent: "Agent",
    grid: "Grid",
    all_agents: list["Agent"],
    features: "SimulationFeatures",
    rng: Any,  # UNUSED: Reserved for future stochastic extensions
    step: int,
) -> "AgentAction":  # type: ignore
    """Single entry point for all agent decisions.

    All decisions are currently **deterministic utility maximizers**. The `rng`
    parameter is unused but reserved for future stochastic extensions (e.g.,
    bounded rationality, exploration noise, probabilistic trade acceptance).

    Simplified: Passes agent + nearby lists, not wrapped perception objects.

    Args:
        agent: Agent making decision
        grid: World grid
        all_agents: All agents in simulation
        features: Feature flags
        rng: Random number generator (UNUSED - reserved for future extensions)
        step: Current simulation step

    Returns:
        AgentAction specifying next action
    """
    # V2 system: Scan for nearby entities based on enabled mechanisms
    # Use forage_enabled flag (still valid) but not legacy trade flags
    nearby_resources = find_nearby_resources(agent, grid) if features.forage_enabled else []
    nearby_agents = find_nearby_agents(agent, all_agents)  # Always scan for agents

    # V2 system: Dispatch based on enabled mechanisms
    # Use forage_enabled flag and determine trading based on phase logic
    if features.forage_enabled and features.trade_execution_enabled:
        return decide_dual_mode(agent, nearby_resources, nearby_agents, rng, step)  # type: ignore
    elif features.forage_enabled:
        return decide_forage_only(agent, nearby_resources, rng, step)
    elif features.trade_execution_enabled:
        return decide_bilateral_exchange_only(agent, nearby_agents, rng, step)  # type: ignore
    else:
        return decide_idle(agent, step)
