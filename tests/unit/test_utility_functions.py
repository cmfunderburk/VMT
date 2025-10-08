"""Unit tests for utility functions module.

Tests the unified decision engine's utility function architecture including
abstract base class, concrete implementations, factory function, and helper functions.
"""

import math

import pytest

from econsim.simulation.agent.utility_functions import (
    CARRYING_CAPACITY,
    DISTANCE_DISCOUNT_FACTOR,
    EPSILON_UTILITY,
    MIN_TRADE_UTILITY_GAIN,
    PERCEPTION_RADIUS,
    CobbDouglasUtility,
    PerfectComplementsUtility,
    PerfectSubstitutesUtility,
    UtilityFunction,
    apply_distance_discount,
    calculate_agent_utility,
    calculate_marginal_utility,
    calculate_resource_net_utility,
    create_utility_function,
    get_agent_total_bundle,
)


class TestUtilityFunctionAbstractBase:
    """Test that UtilityFunction abstract base class cannot be instantiated."""

    def test_cannot_instantiate_abstract_base(self):
        """Test that UtilityFunction abstract base class raises TypeError."""
        with pytest.raises(TypeError):
            UtilityFunction()


class TestCobbDouglasUtility:
    """Test CobbDouglasUtility class implementation."""

    def test_constructor_validation_alpha_range(self):
        """Test constructor validates alpha is in (0, 1)."""
        # Valid alpha values
        CobbDouglasUtility(0.1)
        CobbDouglasUtility(0.5)
        CobbDouglasUtility(0.9)

        # Invalid alpha values
        with pytest.raises(ValueError, match="Alpha must be in \\(0, 1\\)"):
            CobbDouglasUtility(0.0)

        with pytest.raises(ValueError, match="Alpha must be in \\(0, 1\\)"):
            CobbDouglasUtility(1.0)

        with pytest.raises(ValueError, match="Alpha must be in \\(0, 1\\)"):
            CobbDouglasUtility(-0.1)

        with pytest.raises(ValueError, match="Alpha must be in \\(0, 1\\)"):
            CobbDouglasUtility(1.1)

    def test_constructor_validation_alpha_beta_sum(self):
        """Test constructor validates alpha + beta = 1."""
        # Valid combinations
        CobbDouglasUtility(0.3, 0.7)
        CobbDouglasUtility(0.5, 0.5)

        # Invalid combinations
        with pytest.raises(ValueError, match="Alpha \\+ beta must equal 1"):
            CobbDouglasUtility(0.3, 0.6)

        with pytest.raises(ValueError, match="Alpha \\+ beta must equal 1"):
            CobbDouglasUtility(0.5, 0.3)

    def test_constructor_default_beta(self):
        """Test constructor defaults beta to 1 - alpha."""
        util = CobbDouglasUtility(0.3)
        assert util.alpha == 0.3
        assert util.beta == 0.7

    def test_calculate_utility_various_bundles(self):
        """Test utility calculation with various bundles."""
        util = CobbDouglasUtility(0.5, 0.5)

        # Test with epsilon bootstrap
        bundle1 = {"good1": 0, "good2": 0}
        utility1 = util.calculate_utility(bundle1)
        expected1 = (EPSILON_UTILITY**0.5) * (EPSILON_UTILITY**0.5)
        assert abs(utility1 - expected1) < 1e-9

        # Test with positive quantities
        bundle2 = {"good1": 4, "good2": 9}
        utility2 = util.calculate_utility(bundle2)
        x = 4 + EPSILON_UTILITY
        y = 9 + EPSILON_UTILITY
        expected2 = (x**0.5) * (y**0.5)
        assert abs(utility2 - expected2) < 1e-9

        # Test with missing goods (should default to 0)
        bundle3 = {"good1": 2}
        utility3 = util.calculate_utility(bundle3)
        x = 2 + EPSILON_UTILITY
        y = 0 + EPSILON_UTILITY
        expected3 = (x**0.5) * (y**0.5)
        assert abs(utility3 - expected3) < 1e-9

    def test_calculate_marginal_utility_diminishing_returns(self):
        """Test that marginal utility shows diminishing returns."""
        util = CobbDouglasUtility(0.5, 0.5)
        bundle = {"good1": 4, "good2": 4}

        # First unit should have higher marginal utility than second unit
        mu1 = util.calculate_marginal_utility(bundle, "good1", 1)
        mu2 = util.calculate_marginal_utility(bundle, "good1", 1)  # Same bundle, should be same

        # Add first unit and test second unit
        bundle_after_first = {"good1": 5, "good2": 4}
        mu_second = util.calculate_marginal_utility(bundle_after_first, "good1", 1)

        # Second unit should have lower marginal utility (diminishing returns)
        assert mu_second < mu1

    def test_get_preference_type(self):
        """Test preference type identifier."""
        util = CobbDouglasUtility(0.5)
        assert util.get_preference_type() == "cobb_douglas"


class TestPerfectSubstitutesUtility:
    """Test PerfectSubstitutesUtility class implementation."""

    def test_constructor_validation_positive_weights(self):
        """Test constructor validates both weights are positive."""
        # Valid weights
        PerfectSubstitutesUtility(1.0, 2.0)
        PerfectSubstitutesUtility(0.5, 0.3)

        # Invalid weights
        with pytest.raises(ValueError, match="Both weights must be positive"):
            PerfectSubstitutesUtility(0.0, 1.0)

        with pytest.raises(ValueError, match="Both weights must be positive"):
            PerfectSubstitutesUtility(1.0, 0.0)

        with pytest.raises(ValueError, match="Both weights must be positive"):
            PerfectSubstitutesUtility(-1.0, 1.0)

    def test_calculate_utility_linear(self):
        """Test utility calculation is linear."""
        util = PerfectSubstitutesUtility(2.0, 3.0)

        # Test linear utility
        bundle1 = {"good1": 2, "good2": 1}
        utility1 = util.calculate_utility(bundle1)
        expected1 = 2.0 * (2 + EPSILON_UTILITY) + 3.0 * (1 + EPSILON_UTILITY)
        assert abs(utility1 - expected1) < 1e-9

        # Test with missing goods
        bundle2 = {"good1": 3}
        utility2 = util.calculate_utility(bundle2)
        expected2 = 2.0 * (3 + EPSILON_UTILITY) + 3.0 * EPSILON_UTILITY
        assert abs(utility2 - expected2) < 1e-9

    def test_calculate_marginal_utility_constant(self):
        """Test that marginal utility is constant."""
        util = PerfectSubstitutesUtility(2.0, 3.0)

        # Marginal utility should be constant regardless of current bundle
        bundle1 = {"good1": 1, "good2": 1}
        bundle2 = {"good1": 10, "good2": 10}

        mu1_good1 = util.calculate_marginal_utility(bundle1, "good1", 1)
        mu2_good1 = util.calculate_marginal_utility(bundle2, "good1", 1)
        assert abs(mu1_good1 - mu2_good1) < 1e-9
        assert abs(mu1_good1 - 2.0) < 1e-9

        mu1_good2 = util.calculate_marginal_utility(bundle1, "good2", 1)
        mu2_good2 = util.calculate_marginal_utility(bundle2, "good2", 1)
        assert abs(mu1_good2 - mu2_good2) < 1e-9
        assert abs(mu1_good2 - 3.0) < 1e-9

    def test_calculate_marginal_utility_unknown_good(self):
        """Test marginal utility for unknown good returns 0."""
        util = PerfectSubstitutesUtility(2.0, 3.0)
        bundle = {"good1": 1, "good2": 1}

        mu = util.calculate_marginal_utility(bundle, "unknown_good", 1)
        assert mu == 0.0

    def test_get_preference_type(self):
        """Test preference type identifier."""
        util = PerfectSubstitutesUtility(1.0, 2.0)
        assert util.get_preference_type() == "perfect_substitutes"


class TestPerfectComplementsUtility:
    """Test PerfectComplementsUtility class implementation."""

    def test_constructor_validation_positive_factors(self):
        """Test constructor validates both scaling factors are positive."""
        # Valid factors
        PerfectComplementsUtility(1.0, 2.0)
        PerfectComplementsUtility(0.5, 0.3)

        # Invalid factors
        with pytest.raises(ValueError, match="Both scaling factors must be positive"):
            PerfectComplementsUtility(0.0, 1.0)

        with pytest.raises(ValueError, match="Both scaling factors must be positive"):
            PerfectComplementsUtility(1.0, 0.0)

        with pytest.raises(ValueError, match="Both scaling factors must be positive"):
            PerfectComplementsUtility(-1.0, 1.0)

    def test_calculate_utility_min_function(self):
        """Test utility calculation uses min function."""
        util = PerfectComplementsUtility(1.0, 2.0)

        # Test min function behavior
        bundle1 = {"good1": 4, "good2": 3}  # min(1*4, 2*3) = min(4, 6) = 4
        utility1 = util.calculate_utility(bundle1)
        expected1 = min(1.0 * (4 + EPSILON_UTILITY), 2.0 * (3 + EPSILON_UTILITY))
        assert abs(utility1 - expected1) < 1e-9

        bundle2 = {"good1": 2, "good2": 4}  # min(1*2, 2*4) = min(2, 8) = 2
        utility2 = util.calculate_utility(bundle2)
        expected2 = min(1.0 * (2 + EPSILON_UTILITY), 2.0 * (4 + EPSILON_UTILITY))
        assert abs(utility2 - expected2) < 1e-9

    def test_calculate_marginal_utility_kinked_behavior(self):
        """Test marginal utility shows kinked behavior."""
        util = PerfectComplementsUtility(1.0, 1.0)  # Equal scaling for simplicity

        # With epsilon bootstrap, both goods get EPSILON_UTILITY added
        # Bundle (2,2) becomes (2+ε, 2+ε), so min(2+ε, 2+ε) = 2+ε
        # Adding 1 to good1: (3+ε, 2+ε), so min(3+ε, 2+ε) = 2+ε, marginal utility = 0
        # Adding 1 to good2: (2+ε, 3+ε), so min(2+ε, 3+ε) = 2+ε, marginal utility = 0
        # Both should be 0 because they're perfectly balanced with epsilon

        bundle_balanced = {"good1": 2, "good2": 2}
        mu_balanced_good1 = util.calculate_marginal_utility(bundle_balanced, "good1", 1)
        mu_balanced_good2 = util.calculate_marginal_utility(bundle_balanced, "good2", 1)

        # Both should be 0 because goods are balanced (with epsilon)
        assert mu_balanced_good1 == 0.0
        assert mu_balanced_good2 == 0.0

        # Test case where one good is clearly limiting
        # Bundle (1, 3): min(1+ε, 3+ε) = 1+ε, adding to good1 should increase utility
        bundle_limiting_good1 = {"good1": 1, "good2": 3}
        mu_limiting_good1 = util.calculate_marginal_utility(bundle_limiting_good1, "good1", 1)
        assert mu_limiting_good1 > 0

        # Adding to good2 (already in excess) should not increase utility
        mu_limiting_good2 = util.calculate_marginal_utility(bundle_limiting_good1, "good2", 1)
        assert mu_limiting_good2 == 0.0

        # Test case where good2 is limiting
        bundle_limiting_good2 = {"good1": 3, "good2": 1}
        mu_limiting_good2_from_bundle = util.calculate_marginal_utility(
            bundle_limiting_good2, "good2", 1
        )
        assert mu_limiting_good2_from_bundle > 0

        mu_limiting_good1_from_bundle = util.calculate_marginal_utility(
            bundle_limiting_good2, "good1", 1
        )
        assert mu_limiting_good1_from_bundle == 0.0

    def test_get_preference_type(self):
        """Test preference type identifier."""
        util = PerfectComplementsUtility(1.0, 2.0)
        assert util.get_preference_type() == "perfect_complements"


class TestCreateUtilityFunctionFactory:
    """Test utility function factory function."""

    def test_create_cobb_douglas_defaults(self):
        """Test creating Cobb-Douglas utility with defaults."""
        util = create_utility_function("cobb_douglas")
        assert isinstance(util, CobbDouglasUtility)
        assert util.alpha == 0.5
        assert util.beta == 0.5

    def test_create_cobb_douglas_custom_params(self):
        """Test creating Cobb-Douglas utility with custom parameters."""
        util = create_utility_function("cobb_douglas", alpha=0.3, beta=0.7)
        assert isinstance(util, CobbDouglasUtility)
        assert util.alpha == 0.3
        assert util.beta == 0.7

    def test_create_perfect_substitutes_defaults(self):
        """Test creating Perfect Substitutes utility with defaults."""
        util = create_utility_function("perfect_substitutes")
        assert isinstance(util, PerfectSubstitutesUtility)
        assert util.alpha == 1.0
        assert util.beta == 1.0

    def test_create_perfect_substitutes_custom_params(self):
        """Test creating Perfect Substitutes utility with custom parameters."""
        util = create_utility_function("perfect_substitutes", alpha=2.0, beta=3.0)
        assert isinstance(util, PerfectSubstitutesUtility)
        assert util.alpha == 2.0
        assert util.beta == 3.0

    def test_create_perfect_complements_defaults(self):
        """Test creating Perfect Complements utility with defaults."""
        util = create_utility_function("perfect_complements")
        assert isinstance(util, PerfectComplementsUtility)
        assert util.alpha == 1.0
        assert util.beta == 1.0

    def test_create_perfect_complements_custom_params(self):
        """Test creating Perfect Complements utility with custom parameters."""
        util = create_utility_function("perfect_complements", alpha=1.0, beta=2.0)
        assert isinstance(util, PerfectComplementsUtility)
        assert util.alpha == 1.0
        assert util.beta == 2.0

    def test_unsupported_preference_type(self):
        """Test factory raises ValueError for unsupported preference type."""
        with pytest.raises(ValueError, match="Unsupported preference type"):
            create_utility_function("unknown_type")


class TestEconomicConstants:
    """Test economic constants are properly defined."""

    def test_epsilon_utility(self):
        """Test EPSILON_UTILITY constant."""
        assert EPSILON_UTILITY == 0.01
        assert EPSILON_UTILITY > 0

    def test_distance_discount_factor(self):
        """Test DISTANCE_DISCOUNT_FACTOR constant."""
        assert DISTANCE_DISCOUNT_FACTOR == 0.15
        assert DISTANCE_DISCOUNT_FACTOR > 0

    def test_min_trade_utility_gain(self):
        """Test MIN_TRADE_UTILITY_GAIN constant."""
        assert MIN_TRADE_UTILITY_GAIN == 1e-5
        assert MIN_TRADE_UTILITY_GAIN > 0

    def test_perception_radius(self):
        """Test PERCEPTION_RADIUS constant."""
        assert PERCEPTION_RADIUS == 8
        assert PERCEPTION_RADIUS > 0

    def test_carrying_capacity(self):
        """Test CARRYING_CAPACITY constant."""
        assert CARRYING_CAPACITY == 100000
        assert CARRYING_CAPACITY > 0


class TestHelperFunctions:
    """Test economic helper functions."""

    def test_apply_distance_discount_reduces_utility(self):
        """Test distance discount reduces utility with distance."""
        utility_gain = 10.0

        # No distance should return original utility
        discounted_0 = apply_distance_discount(utility_gain, 0)
        assert abs(discounted_0 - utility_gain) < 1e-9

        # Distance should reduce utility
        discounted_1 = apply_distance_discount(utility_gain, 1)
        discounted_2 = apply_distance_discount(utility_gain, 2)

        assert discounted_1 < utility_gain
        assert discounted_2 < discounted_1
        assert discounted_2 < utility_gain

    def test_apply_distance_discount_exponential(self):
        """Test distance discount follows exponential formula."""
        utility_gain = 10.0
        distance = 2

        expected = utility_gain * math.exp(-DISTANCE_DISCOUNT_FACTOR * distance)
        actual = apply_distance_discount(utility_gain, distance)

        assert abs(actual - expected) < 1e-9

    def test_apply_distance_discount_never_negative(self):
        """Test distance discount never makes utility negative."""
        utility_gain = 1.0

        for distance in range(0, 100):
            discounted = apply_distance_discount(utility_gain, distance)
            assert discounted >= 0


# Mock agent class for testing helper functions
class MockAgent:
    """Mock agent class for testing utility helper functions."""

    def __init__(self, carrying=None, home_inventory=None, utility_function=None):
        self.carrying_inventory = carrying or {"good1": 0, "good2": 0}
        self.home_inventory = home_inventory or {"good1": 0, "good2": 0}
        self.utility_function = utility_function or CobbDouglasUtility(0.5)


class TestAgentUtilityHelpers:
    """Test agent utility helper functions."""

    def test_get_agent_total_bundle_combines_inventories(self):
        """Test get_agent_total_bundle combines carrying and home correctly."""
        agent = MockAgent(
            carrying={"good1": 3, "good2": 2}, home_inventory={"good1": 1, "good2": 4}
        )

        total_bundle = get_agent_total_bundle(agent)

        assert total_bundle == {"good1": 4, "good2": 6}

    def test_get_agent_total_bundle_missing_goods(self):
        """Test get_agent_total_bundle handles missing goods."""
        agent = MockAgent(
            carrying={"good1": 3}, home_inventory={"good2": 2}  # good2 missing  # good1 missing
        )

        total_bundle = get_agent_total_bundle(agent)

        assert total_bundle == {"good1": 3, "good2": 2}

    def test_calculate_agent_utility_uses_utility_function(self):
        """Test calculate_agent_utility uses agent's utility function."""
        utility_func = CobbDouglasUtility(0.5)
        agent = MockAgent(
            carrying={"good1": 4, "good2": 4},
            home_inventory={"good1": 1, "good2": 1},
            utility_function=utility_func,
        )

        # Should use total bundle (5, 5) for utility calculation
        utility = calculate_agent_utility(agent)

        # Calculate expected utility manually
        expected_bundle = {"good1": 5, "good2": 5}
        expected_utility = utility_func.calculate_utility(expected_bundle)

        assert abs(utility - expected_utility) < 1e-9

    def test_calculate_marginal_utility_uses_utility_function(self):
        """Test calculate_marginal_utility uses agent's utility function."""
        utility_func = PerfectSubstitutesUtility(2.0, 3.0)
        agent = MockAgent(
            carrying={"good1": 2, "good2": 1},
            home_inventory={"good1": 1, "good2": 2},
            utility_function=utility_func,
        )

        # Should use total bundle (3, 3) for marginal utility calculation
        marginal_utility = calculate_marginal_utility(agent, "good1", 1)

        # For perfect substitutes, marginal utility should be constant
        expected_mu = 2.0  # alpha for good1
        assert abs(marginal_utility - expected_mu) < 1e-9


# Mock resource class for testing
class MockResource:
    """Mock resource class for testing."""

    def __init__(self, good_type, quantity, distance):
        self.good_type = good_type
        self.quantity = quantity
        self.distance = distance


class TestResourceNetUtility:
    """Test calculate_resource_net_utility function."""

    def test_calculate_resource_net_utility_combines_effects(self):
        """Test calculate_resource_net_utility combines marginal utility and distance discount."""
        utility_func = PerfectSubstitutesUtility(2.0, 1.0)  # good1 has higher marginal utility
        agent = MockAgent(
            carrying={"good1": 1, "good2": 1},
            home_inventory={"good1": 0, "good2": 0},
            utility_function=utility_func,
        )

        resource = MockResource("good1", 1, 2)

        # Calculate expected values
        raw_utility = utility_func.calculate_marginal_utility({"good1": 1, "good2": 1}, "good1", 1)
        expected_net_utility = apply_distance_discount(raw_utility, 2)

        actual_net_utility = calculate_resource_net_utility(agent, resource)

        assert abs(actual_net_utility - expected_net_utility) < 1e-9

    def test_calculate_resource_net_utility_positive_when_beneficial(self):
        """Test calculate_resource_net_utility returns positive when resource is beneficial."""
        utility_func = PerfectSubstitutesUtility(2.0, 1.0)
        agent = MockAgent(
            carrying={"good1": 0, "good2": 0},
            home_inventory={"good1": 0, "good2": 0},
            utility_function=utility_func,
        )

        resource = MockResource("good1", 1, 1)  # Close resource with high marginal utility

        net_utility = calculate_resource_net_utility(agent, resource)

        assert net_utility > 0

    def test_calculate_resource_net_utility_decreases_with_distance(self):
        """Test calculate_resource_net_utility decreases with distance."""
        utility_func = PerfectSubstitutesUtility(2.0, 1.0)
        agent = MockAgent(
            carrying={"good1": 1, "good2": 1},
            home_inventory={"good1": 0, "good2": 0},
            utility_function=utility_func,
        )

        resource_close = MockResource("good1", 1, 1)
        resource_far = MockResource("good1", 1, 5)

        net_utility_close = calculate_resource_net_utility(agent, resource_close)
        net_utility_far = calculate_resource_net_utility(agent, resource_far)

        assert net_utility_close > net_utility_far
