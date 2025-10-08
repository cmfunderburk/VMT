"""Centralized Utility Functions for Economic Agents.

This module provides a pluggable architecture for utility functions used by the unified
decision engine. Each utility function implements standard economic theory and provides
a consistent interface for utility and marginal utility calculations.

Design Principles:
1. **Abstract Base Class** - Consistent interface across all utility functions
2. **Economic Correctness** - Each function implements standard economic theory
3. **Extensibility** - Easy to add new utility functions (CES, Stone-Geary, etc.)
4. **Type Safety** - Abstract base class ensures consistent interface
5. **Testing** - Isolated utility function testing
6. **Economic Clarity** - Each utility function is a separate class with clear interpretation

Supported Utility Functions:
- Cobb-Douglas: U = (x + ε)^α * (y + ε)^β (diminishing marginal utility, smooth substitution)
- Perfect Substitutes: U = αx + βy (linear utility, constant marginal utility)
- Perfect Complements: U = min(αx, βy) (fixed proportions, kinked utility)

Economic Constants:
- EPSILON_UTILITY: Bootstrap utility for zero quantities (prevents log(0) issues)
- DISTANCE_DISCOUNT_FACTOR: Exponential distance discount rate for spatial costs
- MIN_TRADE_UTILITY_GAIN: Minimum utility improvement threshold for trades
- PERCEPTION_RADIUS: Manhattan distance for resource/agent detection
- CARRYING_CAPACITY: Maximum carrying inventory (currently 100,000 units)

The module also provides helper functions for agent utility calculations:
- get_agent_total_bundle(): Combines carrying + home inventories
- calculate_agent_utility(): Uses agent's utility function on total wealth
- calculate_marginal_utility(): Evaluates utility gain from additional resources
- apply_distance_discount(): Models spatial costs in resource evaluation
- calculate_resource_net_utility(): Combines marginal utility and distance discount
"""

import math
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from econsim.simulation.agent.core import Agent

# Economic constants
EPSILON_UTILITY = 0.01  # Bootstrap utility for zero quantities
DISTANCE_DISCOUNT_FACTOR = 0.15  # Exponential distance discount rate
MIN_TRADE_UTILITY_GAIN = 1e-5  # Minimum utility improvement for trades
PERCEPTION_RADIUS = 8  # Manhattan distance perception radius
CARRYING_CAPACITY = 100000  # Maximum carrying inventory (effectively unlimited)


class UtilityFunction(ABC):
    """Abstract base class for utility functions.

    This architecture allows pluggable utility functions while maintaining
    consistent interfaces for the decision engine.
    """

    @abstractmethod
    def calculate_utility(self, bundle: dict[str, int]) -> float:
        """Calculate utility for a resource bundle.

        Args:
            bundle: Resource quantities {"good1": x, "good2": y, ...}

        Returns:
            Utility value (always >= 0)
        """
        pass

    @abstractmethod
    def calculate_marginal_utility(
        self, bundle: dict[str, int], additional_good: str, additional_quantity: int = 1
    ) -> float:
        """Calculate utility gain from acquiring additional resources.

        Args:
            bundle: Current resource bundle
            additional_good: Good type to add
            additional_quantity: Amount to add (default: 1)

        Returns:
            Utility improvement (positive = beneficial)
        """
        pass

    @abstractmethod
    def get_preference_type(self) -> str:
        """Return the preference type identifier.

        Returns:
            String identifier (e.g., "cobb_douglas", "perfect_substitutes")
        """
        pass


class CobbDouglasUtility(UtilityFunction):
    """Cobb-Douglas utility: U = (x + ε)^α * (y + ε)^β

    Standard economic utility function with diminishing marginal utility
    and smooth substitution between goods.
    """

    def __init__(self, alpha: float, beta: float | None = None):
        """Initialize Cobb-Douglas preferences.

        Args:
            alpha: Preference weight for good1 (0 < alpha < 1)
            beta: Preference weight for good2 (defaults to 1-alpha)

        Raises:
            ValueError: If alpha not in (0, 1) or alpha + beta ≠ 1
        """
        if not (0 < alpha < 1):
            raise ValueError(f"Alpha must be in (0, 1), got {alpha}")

        if beta is None:
            beta_val = 1 - alpha
        else:
            beta_val = beta
            if abs(alpha + beta_val - 1.0) > 1e-9:
                raise ValueError(f"Alpha + beta must equal 1, got {alpha + beta_val}")

        self.alpha = alpha
        self.beta = float(beta_val)

    def calculate_utility(self, bundle: dict[str, int]) -> float:
        """Calculate Cobb-Douglas utility."""
        x = bundle.get("good1", 0) + EPSILON_UTILITY
        y = bundle.get("good2", 0) + EPSILON_UTILITY
        return (x**self.alpha) * (y**self.beta)

    def calculate_marginal_utility(
        self, bundle: dict[str, int], additional_good: str, additional_quantity: int = 1
    ) -> float:
        """Calculate marginal utility for Cobb-Douglas."""
        current_utility = self.calculate_utility(bundle)

        # Add additional quantity
        new_bundle = bundle.copy()
        new_bundle[additional_good] = new_bundle.get(additional_good, 0) + additional_quantity

        new_utility = self.calculate_utility(new_bundle)
        return new_utility - current_utility

    def get_preference_type(self) -> str:
        return "cobb_douglas"


class PerfectSubstitutesUtility(UtilityFunction):
    """Perfect substitutes utility: U = αx + βy

    Linear utility function where goods are perfect substitutes.
    Agents are indifferent between goods at the ratio β/α.
    """

    def __init__(self, alpha: float, beta: float):
        """Initialize perfect substitutes preferences.

        Args:
            alpha: Marginal utility of good1
            beta: Marginal utility of good2

        Raises:
            ValueError: If either weight is non-positive
        """
        if alpha <= 0 or beta <= 0:
            raise ValueError(f"Both weights must be positive, got α={alpha}, β={beta}")

        self.alpha = alpha
        self.beta = beta

    def calculate_utility(self, bundle: dict[str, int]) -> float:
        """Calculate perfect substitutes utility."""
        x = bundle.get("good1", 0) + EPSILON_UTILITY
        y = bundle.get("good2", 0) + EPSILON_UTILITY
        return self.alpha * x + self.beta * y

    def calculate_marginal_utility(
        self, bundle: dict[str, int], additional_good: str, additional_quantity: int = 1
    ) -> float:
        """Calculate marginal utility for perfect substitutes (constant)."""
        if additional_good == "good1":
            return self.alpha * additional_quantity
        elif additional_good == "good2":
            return self.beta * additional_quantity
        else:
            return 0.0

    def get_preference_type(self) -> str:
        return "perfect_substitutes"


class PerfectComplementsUtility(UtilityFunction):
    """Perfect complements (Leontief) utility: U = min(αx, βy)

    Utility function where goods must be consumed in fixed proportions.
    Excess of either good provides no additional utility.
    """

    def __init__(self, alpha: float, beta: float):
        """Initialize perfect complements preferences.

        Args:
            alpha: Scaling factor for good1 (units per "bundle")
            beta: Scaling factor for good2 (units per "bundle")

        Raises:
            ValueError: If either scaling factor is non-positive
        """
        if alpha <= 0 or beta <= 0:
            raise ValueError(f"Both scaling factors must be positive, got α={alpha}, β={beta}")

        self.alpha = alpha
        self.beta = beta

    def calculate_utility(self, bundle: dict[str, int]) -> float:
        """Calculate perfect complements utility."""
        x = bundle.get("good1", 0) + EPSILON_UTILITY
        y = bundle.get("good2", 0) + EPSILON_UTILITY
        return min(self.alpha * x, self.beta * y)

    def calculate_marginal_utility(
        self, bundle: dict[str, int], additional_good: str, additional_quantity: int = 1
    ) -> float:
        """Calculate marginal utility for perfect complements."""
        current_utility = self.calculate_utility(bundle)

        # Add additional quantity
        new_bundle = bundle.copy()
        new_bundle[additional_good] = new_bundle.get(additional_good, 0) + additional_quantity

        new_utility = self.calculate_utility(new_bundle)
        return new_utility - current_utility

    def get_preference_type(self) -> str:
        return "perfect_complements"


# ============================================================================
# UTILITY FUNCTION FACTORY
# ============================================================================


def create_utility_function(preference_type: str, **kwargs: float) -> UtilityFunction:
    """Factory function to create utility functions.

    Args:
        preference_type: Type of utility function ("cobb_douglas", "perfect_substitutes", "perfect_complements")
        **kwargs: Parameters specific to utility function type

    Returns:
        Configured UtilityFunction instance

    Raises:
        ValueError: If preference_type is not supported
    """
    if preference_type == "cobb_douglas":
        alpha = kwargs.get("alpha", 0.5)
        beta = kwargs.get("beta")
        return CobbDouglasUtility(alpha, beta)

    elif preference_type == "perfect_substitutes":
        alpha = kwargs.get("alpha", 1.0)
        beta = kwargs.get("beta", 1.0)
        return PerfectSubstitutesUtility(alpha, beta)

    elif preference_type == "perfect_complements":
        alpha = kwargs.get("alpha", 1.0)
        beta = kwargs.get("beta", 1.0)
        return PerfectComplementsUtility(alpha, beta)

    else:
        raise ValueError(f"Unsupported preference type: {preference_type}")


# ============================================================================
# AGENT UTILITY HELPERS
# ============================================================================


def get_agent_total_bundle(agent: "Agent") -> dict[str, int]:
    """Get agent's total resource bundle (carrying + home inventory).

    Economic interpretation: Utility should be based on total accumulated
    resources, not just what's currently being carried.

    Args:
        agent: Agent to get bundle for

    Returns:
        Total bundle: {"good1": total_good1, "good2": total_good2}
    """
    total_bundle = {}
    for good in ["good1", "good2"]:
        carrying = agent.carrying_inventory.get(good, 0)
        stored = agent.home_inventory.get(good, 0)
        total_bundle[good] = carrying + stored
    return total_bundle


def calculate_agent_utility(agent: "Agent") -> float:
    """Calculate agent's current utility from total resources.

    Uses agent's utility function to evaluate total wealth (carrying + home).

    Args:
        agent: Agent to calculate utility for

    Returns:
        Current utility value based on total resources
    """
    total_bundle = get_agent_total_bundle(agent)
    # Note: agent.utility_function will be added in Phase 3.1
    return agent.utility_function.calculate_utility(total_bundle)  # type: ignore


def calculate_marginal_utility(
    agent: "Agent", additional_good: str, additional_quantity: int = 1
) -> float:
    """Calculate utility gain from acquiring additional resources.

    Uses agent's utility function to evaluate marginal utility.

    Args:
        agent: Agent to calculate for
        additional_good: Good type to add ("good1" or "good2")
        additional_quantity: Amount to add (default: 1)

    Returns:
        Utility improvement (positive means beneficial)
    """
    total_bundle = get_agent_total_bundle(agent)
    # Note: agent.utility_function will be added in Phase 3.1
    return agent.utility_function.calculate_marginal_utility(
        total_bundle, additional_good, additional_quantity
    )  # type: ignore


def apply_distance_discount(utility_gain: float, distance: int) -> float:
    """Apply exponential distance discount to utility gain.

    Models spatial cost: farther resources are less attractive due to
    movement costs.

    Args:
        utility_gain: Raw utility improvement
        distance: Manhattan distance to resource

    Returns:
        Distance-discounted utility (always <= utility_gain)
    """
    return utility_gain * math.exp(-DISTANCE_DISCOUNT_FACTOR * distance)


def calculate_resource_net_utility(agent: "Agent", resource) -> float:
    """Calculate distance-discounted utility for a resource target.

    Combines marginal utility and distance discount in one call.

    Args:
        agent: Agent evaluating resource
        resource: Resource to evaluate (ResourceInfo object)

    Returns:
        Net utility (positive means worth pursuing)
    """
    # Note: resource parameter is ResourceInfo from unified_decision.py
    raw_utility = calculate_marginal_utility(
        agent,
        resource.good_type,  # type: ignore
        resource.quantity,  # type: ignore
    )
    return apply_distance_discount(raw_utility, resource.distance)  # type: ignore
