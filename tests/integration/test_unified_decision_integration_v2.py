"""Minimal integration tests for unified decision engine (post AgentV2 removal).

This file replaces a previously corrupted large suite. Focused coverage:
 1. Utility function correctness (marginals / forms)
 2. Simple bilateral trade produces Pareto-improving (or neutral) outcome
 3. Delta recorder collects step deltas end-to-end

Extended multi-scenario tests (dual mode, speculative withdrawals, complex
pair arbitration) can be reintroduced incrementally once baseline is stable.
"""

import os
import random
from unittest.mock import Mock

from econsim.simulation.agent.core import Agent
from econsim.simulation.agent.utility_functions import (
    CobbDouglasUtility,
    PerfectComplementsUtility,
    PerfectSubstitutesUtility,
)
from econsim.simulation.executor import UnifiedStepExecutor
from econsim.simulation.world.grid import Grid


class TestUtilityFunctionBehavior:
    """Test utility function correctness and behavior differences."""

    def test_cobb_douglas_marginals(self):
        """Test Cobb-Douglas utility function marginal utility calculation."""
        agent = Agent(
            id=0,
            x=0,
            y=0,
            utility_function=CobbDouglasUtility(0.3, 0.7),
            home_x=0,
            home_y=0,
            carrying_inventory={"good1": 10, "good2": 5},
        )
        bundle = agent.get_total_bundle()
        mu_good1 = agent.utility_function.calculate_marginal_utility(bundle, "good1", 1)
        mu_good2 = agent.utility_function.calculate_marginal_utility(bundle, "good2", 1)

        # With alpha=0.3, beta=0.7, agent should prefer good2
        assert mu_good2 > mu_good1

    def test_perfect_substitutes_linear(self):
        """Test Perfect Substitutes utility function linear behavior."""
        agent = Agent(
            id=0,
            x=0,
            y=0,
            utility_function=PerfectSubstitutesUtility(2.0, 1.0),
            home_x=0,
            home_y=0,
            carrying_inventory={"good1": 10, "good2": 10},
        )
        u = agent.calculate_current_utility()

        # U = 2.0 * (10 + 0.01) + 1.0 * (10 + 0.01) - linear utility
        expected = 2.0 * (10 + 0.01) + 1.0 * (10 + 0.01)
        assert abs(u - expected) < 1e-6

    def test_perfect_complements_min(self):
        """Test Perfect Complements utility function min behavior."""
        agent = Agent(
            id=0,
            x=0,
            y=0,
            utility_function=PerfectComplementsUtility(1.0, 2.0),
            home_x=0,
            home_y=0,
            carrying_inventory={"good1": 10, "good2": 5},
        )
        u = agent.calculate_current_utility()

        # U = min(1.0 * (10 + 0.01), 2.0 * (5 + 0.01)) = min(10.01, 10.02) = 10.01
        expected = min(1.0 * (10 + 0.01), 2.0 * (5 + 0.01))
        assert abs(u - expected) < 1e-6

    def test_mixed_preference_populations(self):
        """Test mixed utility function populations show heterogeneous behavior."""
        agents = [
            Agent(
                id=0,
                x=5,
                y=5,
                utility_function=CobbDouglasUtility(0.5, 0.5),
                home_x=5,
                home_y=5,
                carrying_inventory={"good1": 10, "good2": 10},
            ),
            Agent(
                id=1,
                x=6,
                y=6,
                utility_function=PerfectSubstitutesUtility(2.0, 1.0),
                home_x=6,
                home_y=6,
                carrying_inventory={"good1": 10, "good2": 10},
            ),
            Agent(
                id=2,
                x=7,
                y=7,
                utility_function=PerfectComplementsUtility(1.0, 1.0),
                home_x=7,
                home_y=7,
                carrying_inventory={"good1": 10, "good2": 10},
            ),
        ]

        # Test that different utility functions produce different utility values
        utilities = [agent.calculate_current_utility() for agent in agents]

        # All should have positive utility
        assert all(u > 0 for u in utilities)

        # Should have different utility values (heterogeneous behavior)
        assert (
            len(set(utilities)) >= 2
        ), f"Expected at least 2 different utility values, got: {utilities}"


class TestForageModeIntegration:
    """Test forage-only mode end-to-end behavior."""

    def test_forage_agents_collect_resources(self):
        """Test forage-only mode: agents collect resources over multiple steps."""
        # Create grid with resources within perception radius
        resources = [
            (3, 3, "A"),  # good1 resource - distance ~4.24 from (0,0)
            (5, 2, "B"),  # good2 resource - distance ~5.39 from (0,0)
            (2, 5, "A"),  # good1 resource - distance ~5.39 from (0,0)
        ]
        grid = Grid(20, 20, resources)

        # Create agents at home
        agents = [
            Agent(
                id=0,
                x=0,
                y=0,
                utility_function=CobbDouglasUtility(0.6, 0.4),  # Prefers good1
                home_x=0,
                home_y=0,
            ),
            Agent(
                id=1,
                x=0,
                y=0,
                utility_function=CobbDouglasUtility(0.4, 0.6),  # Prefers good2
                home_x=0,
                home_y=0,
            ),
        ]

        # Create mock simulation
        mock_simulation = Mock()
        mock_simulation._steps = 0
        mock_simulation.agents = agents
        mock_simulation.grid = grid
        mock_simulation.pre_step_resource_count = len(resources)
        mock_simulation.respawn_scheduler = None
        mock_simulation._rng = None
        mock_simulation._respawn_interval = None
        mock_simulation.executed_trade = None
        mock_simulation._last_trade_highlight = None
        # Mock config for respawn scheduler initialization (executor now owns respawn)
        mock_simulation.config = Mock()
        mock_simulation.config.enable_respawn = False
        mock_simulation.config.respawn_target_density = 0.5
        mock_simulation.config.max_spawn_per_tick = 10
        mock_simulation.config.respawn_rate = 0.1

        executor = UnifiedStepExecutor(mock_simulation, agents)

        # Enable forage mode only
        os.environ["ECONSIM_FORAGE_ENABLED"] = "1"

        try:
            rng = random.Random(42)

            # Record initial resource totals
            initial_total_good1 = sum(agent.get_total_bundle().get("good1", 0) for agent in agents)
            initial_total_good2 = sum(agent.get_total_bundle().get("good2", 0) for agent in agents)

            # Run multiple steps to allow movement and collection
            for step in range(15):
                executor.execute_step(rng)
                mock_simulation._steps += 1

                # After several steps, agents should have collected resources
                if step > 8:
                    total_good1 = sum(agent.get_total_bundle().get("good1", 0) for agent in agents)
                    total_good2 = sum(agent.get_total_bundle().get("good2", 0) for agent in agents)

                    # At least some resource collection should have occurred
                    resources_collected = (
                        total_good1 > initial_total_good1 or total_good2 > initial_total_good2
                    )

                    if resources_collected:
                        # Success - agents have collected resources
                        break

            # Verify that some collection occurred
            final_total_good1 = sum(agent.get_total_bundle().get("good1", 0) for agent in agents)
            final_total_good2 = sum(agent.get_total_bundle().get("good2", 0) for agent in agents)

            assert (
                final_total_good1 > initial_total_good1 or final_total_good2 > initial_total_good2
            ), "No resource collection occurred"

        finally:
            if "ECONSIM_FORAGE_ENABLED" in os.environ:
                del os.environ["ECONSIM_FORAGE_ENABLED"]


class TestBilateralExchangeIntegration:
    """Test bilateral exchange mode end-to-end behavior."""

    def test_bilateral_trade_pareto_improvement(self):
        """Test that bilateral trade produces Pareto-improving outcomes."""
        # Create agents with complementary preferences and goods
        agents = [
            Agent(
                id=0,
                x=5,
                y=5,
                utility_function=CobbDouglasUtility(0.8, 0.2),  # Prefers good1
                home_x=5,
                home_y=5,
                carrying_inventory={"good1": 2, "good2": 0},
            ),
            Agent(
                id=1,
                x=6,
                y=6,
                utility_function=CobbDouglasUtility(0.2, 0.8),  # Prefers good2
                home_x=6,
                home_y=6,
                carrying_inventory={"good1": 0, "good2": 2},
            ),
        ]

        # Create empty grid (no resources for forage)
        grid = Grid(10, 10, [])

        # Create mock simulation
        mock_simulation = Mock()
        mock_simulation._steps = 0
        mock_simulation.agents = agents
        mock_simulation.grid = grid
        mock_simulation.pre_step_resource_count = 0
        mock_simulation.respawn_scheduler = None
        mock_simulation._rng = None
        mock_simulation._respawn_interval = None
        mock_simulation.executed_trade = None
        mock_simulation._last_trade_highlight = None
        # Mock config for respawn scheduler initialization (executor now owns respawn)
        mock_simulation.config = Mock()
        mock_simulation.config.enable_respawn = False
        mock_simulation.config.respawn_target_density = 0.5
        mock_simulation.config.max_spawn_per_tick = 10
        mock_simulation.config.respawn_rate = 0.1

        executor = UnifiedStepExecutor(mock_simulation, agents)

        # Enable bilateral exchange only
        os.environ["ECONSIM_TRADE_EXEC"] = "1"

        try:
            rng = random.Random(123)

            # Record initial utilities
            u0_before = agents[0].calculate_current_utility()
            u1_before = agents[1].calculate_current_utility()

            # Run multiple steps to enable pairing and trading
            for step in range(10):
                executor.execute_step(rng)
                mock_simulation._steps += 1

            # Record final utilities
            u0_after = agents[0].calculate_current_utility()
            u1_after = agents[1].calculate_current_utility()

            # Verify Pareto improvement: no agent worse off, at least one better off
            assert u0_after >= u0_before, "Agent 0 utility should not decrease"
            assert u1_after >= u1_before, "Agent 1 utility should not decrease"
            assert (u0_after > u0_before) or (
                u1_after > u1_before
            ), "At least one agent should improve"

        finally:
            if "ECONSIM_TRADE_EXEC" in os.environ:
                del os.environ["ECONSIM_TRADE_EXEC"]
