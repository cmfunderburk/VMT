"""Economic Agent – Unified Decision Engine Integration.

Canonical agent implementation used by the unified decision engine. Legacy
component-based architecture has been removed; this is the single agent
implementation with no backward-compatibility shims.

Key properties:
- Utility function (pluggable via factory) governs economic behavior
- Dual inventory (carrying + home) with total-bundle utility evaluation
- Deterministic state (no hidden dynamic components)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from ..constants import AgentMode
from .utility_functions import UtilityFunction

if TYPE_CHECKING:
    from econsim.simulation.agent.core import Agent

Position = tuple[int, int]


@dataclass(slots=True)
class Agent:
    """Economic agent integrated with unified decision engine.

    Features:
    - Pluggable utility functions (Cobb-Douglas, Perfect Substitutes, Perfect Complements)
    - Direct inventory management methods (deposit_to_home, withdraw_from_home)
    - Total-bundle utility evaluation (carrying + home)
    - Minimal surface area for deterministic simulation
    """

    # Core identity and position
    id: int
    x: int
    y: int

    # Utility function for economic decision-making
    utility_function: UtilityFunction

    # Home position (defaults to spawn location)
    home_x: int
    home_y: int

    # Behavioral state
    mode: AgentMode = AgentMode.FORAGE
    target: Position | None = None

    # Inventory system
    carrying_inventory: dict[str, int] = field(default_factory=lambda: {"good1": 0, "good2": 0})
    home_inventory: dict[str, int] = field(default_factory=lambda: {"good1": 0, "good2": 0})

    # Trading partner state (simplified from legacy system)
    trading_partner: Agent | None = None

    def __post_init__(self) -> None:
        """Initialize derived fields and validate state."""
        # Validate inventories have required goods
        for inventory in [self.carrying_inventory, self.home_inventory]:
            for good in ["good1", "good2"]:
                if good not in inventory:
                    inventory[good] = 0

    # ============================================================================
    # UTILITY FUNCTION INTEGRATION
    # ============================================================================

    def get_total_bundle(self) -> dict[str, int]:
        """Get agent's total resource bundle (carrying + home inventory).

        Economic interpretation: Utility should be based on total accumulated
        resources, not just what's currently being carried. This ensures
        consistent utility calculations across decision-making and trade evaluation.

        Returns:
            Total bundle: {"good1": total_good1, "good2": total_good2}
        """
        total_bundle: dict[str, int] = {}
        for good in ["good1", "good2"]:
            carrying = self.carrying_inventory.get(good, 0)
            stored = self.home_inventory.get(good, 0)
            total_bundle[good] = carrying + stored
        return total_bundle

    def calculate_current_utility(self) -> float:
        """Calculate agent's current utility from total resources.

        Uses agent's utility function to evaluate total wealth (carrying + home).
        This is the primary utility calculation method used by the decision engine.

        Returns:
            Current utility value based on total resources
        """
        total_bundle = self.get_total_bundle()
        return self.utility_function.calculate_utility(total_bundle)

    def is_inventory_full(self) -> bool:
        """Check if agent's carrying inventory is at capacity.

        Uses CARRYING_CAPACITY constant (100,000 units) to determine if agent
        has reached maximum carrying capacity. This is used by decision logic
        to trigger deposit behavior.

        Returns:
            True if carrying inventory is at or above capacity
        """
        from .utility_functions import CARRYING_CAPACITY

        total_carrying = sum(self.carrying_inventory.values())
        return total_carrying >= CARRYING_CAPACITY

    # ============================================================================
    # INVENTORY MANAGEMENT METHODS
    # ============================================================================

    def deposit_to_home(self, goods: dict[str, int] | None = None) -> None:
        """Deposit goods from carrying inventory to home inventory.

        **Agent method** (not special action) because:
        - Single-entity state change (only affects this agent's inventories)
        - No executor coordination needed (pure data structure operation)
        - Natural agent capability (like move() or collect_resource())

        Called directly by decision logic when inventory full and at home.

        Args:
            goods: Resources to deposit {"good1": quantity, "good2": quantity}
                  If None, deposits ALL carrying inventory

        Raises:
            ValueError: If agent not at home or insufficient carrying inventory
        """
        if not (self.x == self.home_x and self.y == self.home_y):
            raise ValueError(f"Agent {self.id} cannot deposit - not at home")

        # Default to depositing all carrying inventory
        if goods is None:
            goods = self.carrying_inventory.copy()

        # Validate and transfer goods
        for good, quantity in goods.items():
            if quantity <= 0:
                continue

            carrying_qty = self.carrying_inventory.get(good, 0)
            if carrying_qty < quantity:
                raise ValueError(
                    f"Agent {self.id} cannot deposit {quantity} {good} - "
                    f"only carrying {carrying_qty}"
                )

            # Transfer from carrying to home (pure state change)
            self.carrying_inventory[good] = carrying_qty - quantity
            self.home_inventory[good] = self.home_inventory.get(good, 0) + quantity

    def withdraw_from_home(self, goods: dict[str, int] | None = None) -> None:
        """Withdraw goods from home inventory to carrying inventory.

        **Agent method** (not special action) because:
        - Single-entity state change (only affects this agent's inventories)
        - No executor coordination needed (pure data structure operation)
        - Prerequisite for decision-making (not outcome to execute later)

        Called directly by decision logic as bootstrap for bilateral exchange mode:
        enables trade evaluation when carrying empty but home has tradeable goods.

        Args:
            goods: Resources to withdraw {"good1": quantity, "good2": quantity}
                  If None, withdraws ALL home inventory

        Raises:
            ValueError: If agent not at home or insufficient home inventory
        """
        if not (self.x == self.home_x and self.y == self.home_y):
            raise ValueError(f"Agent {self.id} cannot withdraw - not at home")

        # Default to withdrawing all home inventory
        if goods is None:
            goods = self.home_inventory.copy()

        # Validate and transfer goods
        for good, quantity in goods.items():
            if quantity <= 0:
                continue

            home_qty = self.home_inventory.get(good, 0)
            if home_qty < quantity:
                raise ValueError(
                    f"Agent {self.id} cannot withdraw {quantity} {good} - "
                    f"only have {home_qty} at home"
                )

            # Transfer from home to carrying (pure state change)
            self.home_inventory[good] = home_qty - quantity
            self.carrying_inventory[good] = self.carrying_inventory.get(good, 0) + quantity

    # ============================================================================
    # CONVENIENCE METHODS
    # ============================================================================

    def at_home(self) -> bool:
        """Check if agent is currently at their home position."""
        return self.x == self.home_x and self.y == self.home_y

    def carrying_total(self) -> int:
        """Return total number of goods currently being carried."""
        return sum(self.carrying_inventory.values())

    def home_inventory_total(self) -> int:
        """Return total number of goods in home inventory."""
        return sum(self.home_inventory.values())

    def has_carrying_goods(self) -> bool:
        """Check if agent has goods in carrying inventory."""
        return any(quantity > 0 for quantity in self.carrying_inventory.values())

    def has_home_goods(self) -> bool:
        """Check if agent has goods in home inventory."""
        return any(quantity > 0 for quantity in self.home_inventory.values())

    def is_co_located_with(self, other: Agent) -> bool:
        """Check if this agent is on the same tile as another agent."""
        return self.x == other.x and self.y == other.y

    # ============================================================================
    # SERIALIZATION (for debugging and persistence)
    # ============================================================================

    def serialize(self) -> dict[str, Any]:
        """Serialize agent state to dictionary for persistence and debugging."""
        return {
            "id": self.id,
            "x": self.x,
            "y": self.y,
            "home": (self.home_x, self.home_y),
            "mode": self.mode.value,
            "target": self.target,
            "carrying_inventory": dict(self.carrying_inventory),
            "home_inventory": dict(self.home_inventory),
            "utility_function": {
                "type": self.utility_function.get_preference_type(),
                "parameters": self._get_utility_function_parameters(),
            },
            "trading_partner_id": self.trading_partner.id if self.trading_partner else None,
        }

    def _get_utility_function_parameters(self) -> dict[str, Any]:
        """Get utility function parameters for serialization."""
        params: dict[str, Any] = {}
        if hasattr(self.utility_function, "alpha"):
            params["alpha"] = self.utility_function.alpha  # type: ignore
            if hasattr(self.utility_function, "beta"):
                params["beta"] = self.utility_function.beta  # type: ignore
        return params


__all__ = ["Agent", "Position"]
