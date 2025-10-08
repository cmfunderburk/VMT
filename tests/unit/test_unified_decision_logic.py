"""Unit tests for unified decision engine logic.

This module tests the core decision logic functions in the unified decision engine,
including perception helpers, bilateral trade evaluation, decision algorithms, and
the main entry point function.

Tests cover:
- Perception helpers (find_nearby_resources, find_nearby_agents)
- Bilateral trade evaluation (find_beneficial_bilateral_trade, find_best_trading_partner)
- Decision algorithms (decide_forage_only, decide_bilateral_exchange_only, decide_dual_mode)
- Entry point (make_agent_decision)
- Carrying capacity limits and speculative withdrawal
"""

from unittest.mock import Mock

import pytest

from econsim.simulation.agent.unified_decision import (
    # Action construction
    ResourceInfo,
    _has_carrying_goods,
    _has_home_goods,
    # Helper functions
    _has_trading_partner,
    _is_at_home,
    _is_co_located,
    _is_inventory_full,
    decide_bilateral_exchange_only,
    decide_dual_mode,
    # Decision algorithms
    decide_forage_only,
    find_beneficial_bilateral_trade,
    find_best_trading_partner,
    find_nearby_agents,
    # Perception helpers
    find_nearby_resources,
    # Entry point
    make_agent_decision,
)
from econsim.simulation.agent.utility_functions import (
    CARRYING_CAPACITY,
    MIN_TRADE_UTILITY_GAIN,
    PERCEPTION_RADIUS,
    CobbDouglasUtility,
)
from econsim.simulation.constants import AgentMode


class TestPerceptionHelpers:
    """Test perception helper functions."""

    def test_find_nearby_resources_respects_perception_radius(self):
        """Test that find_nearby_resources respects perception radius."""
        # Create mock agent
        agent = Mock()
        agent.x = 10
        agent.y = 10

        # Create mock grid with resources at different distances
        grid = Mock()
        grid.iter_resources.return_value = [
            (10, 10, "A"),  # Distance 0 (at agent)
            (12, 10, "B"),  # Distance 2 (within radius)
            (18, 10, "A"),  # Distance 8 (at radius boundary)
            (19, 10, "B"),  # Distance 9 (beyond radius)
            (20, 10, "A"),  # Distance 10 (beyond radius)
        ]

        nearby = find_nearby_resources(agent, grid)

        # Should only include resources within perception radius
        assert len(nearby) == 3
        assert all(r.distance <= PERCEPTION_RADIUS for r in nearby)

    def test_find_nearby_resources_sorts_by_distance(self):
        """Test that find_nearby_resources sorts by distance (nearest first)."""
        # Create mock agent
        agent = Mock()
        agent.x = 10
        agent.y = 10

        # Create mock grid with resources at different distances
        grid = Mock()
        grid.iter_resources.return_value = [
            (15, 10, "A"),  # Distance 5
            (10, 10, "B"),  # Distance 0
            (12, 10, "A"),  # Distance 2
            (13, 10, "B"),  # Distance 3
        ]

        nearby = find_nearby_resources(agent, grid)

        # Should be sorted by distance (nearest first)
        distances = [r.distance for r in nearby]
        assert distances == sorted(distances)
        assert distances[0] == 0  # Nearest resource
        assert distances[-1] == 5  # Farthest resource

    def test_find_nearby_resources_deterministic_sorting(self):
        """Test that find_nearby_resources uses deterministic sorting for ties."""
        # Create mock agent
        agent = Mock()
        agent.x = 10
        agent.y = 10

        # Create mock grid with resources at same distance
        grid = Mock()
        grid.iter_resources.return_value = [
            (12, 12, "A"),  # Distance 4, position (12, 12)
            (12, 10, "B"),  # Distance 2, position (12, 10)
            (12, 11, "A"),  # Distance 3, position (12, 11)
            (11, 12, "B"),  # Distance 3, position (11, 12)
        ]

        nearby = find_nearby_resources(agent, grid)

        # Should be sorted by distance, then by position for determinism
        assert nearby[0].distance == 2
        assert nearby[1].distance == 3
        assert nearby[2].distance == 3
        assert nearby[3].distance == 4

        # For same distance, should be sorted by position
        assert nearby[1].x == 11  # (11, 12) comes before (12, 11)
        assert nearby[2].x == 12

    def test_find_nearby_agents_excludes_self(self):
        """Test that find_nearby_agents excludes the observing agent."""
        # Create mock observing agent
        observer = Mock()
        observer.id = 1
        observer.x = 10
        observer.y = 10

        # Create mock other agents
        other1 = Mock()
        other1.id = 2
        other1.x = 12
        other1.y = 10
        other1.trading_partner = None
        other1.carrying_inventory = {"good1": 1}

        other2 = Mock()
        other2.id = 3
        other2.x = 14
        other2.y = 10
        other2.trading_partner = None
        other2.carrying_inventory = {"good2": 1}

        all_agents = [observer, other1, other2]

        nearby = find_nearby_agents(observer, all_agents)

        # Should exclude self and include only other agents
        assert len(nearby) == 2
        assert all(a.agent_id != observer.id for a in nearby)
        assert {a.agent_id for a in nearby} == {2, 3}

    def test_find_nearby_agents_respects_perception_radius(self):
        """Test that find_nearby_agents respects perception radius."""
        # Create mock observing agent
        observer = Mock()
        observer.id = 1
        observer.x = 10
        observer.y = 10

        # Create mock other agents at different distances
        agents = []
        for i, (x, y) in enumerate([(10, 10), (12, 10), (18, 10), (19, 10)]):
            agent = Mock()
            agent.id = i + 2
            agent.x = x
            agent.y = y
            agent.trading_partner = None
            agent.carrying_inventory = {"good1": 1}
            agents.append(agent)

        all_agents = [observer] + agents

        nearby = find_nearby_agents(observer, all_agents)

        # Should only include agents within perception radius
        assert len(nearby) == 3  # Excludes the one beyond radius
        assert all(a.distance <= PERCEPTION_RADIUS for a in nearby)

    def test_find_nearby_agents_sorts_by_distance(self):
        """Test that find_nearby_agents sorts by distance (nearest first)."""
        # Create mock observing agent
        observer = Mock()
        observer.id = 1
        observer.x = 10
        observer.y = 10

        # Create mock other agents at different distances
        agents = []
        for i, (x, y) in enumerate([(15, 10), (10, 10), (12, 10), (13, 10)]):
            agent = Mock()
            agent.id = i + 2
            agent.x = x
            agent.y = y
            agent.trading_partner = None
            agent.carrying_inventory = {"good1": 1}
            agents.append(agent)

        all_agents = [observer] + agents

        nearby = find_nearby_agents(observer, all_agents)

        # Should be sorted by distance (nearest first)
        distances = [a.distance for a in nearby]
        assert distances == sorted(distances)
        assert distances[0] == 0  # Nearest agent
        assert distances[-1] == 5  # Farthest agent


class TestBilateralTradeEvaluation:
    """Test bilateral trade evaluation functions."""

    def test_find_beneficial_bilateral_trade_finds_pareto_improvements(self):
        """Test that find_beneficial_bilateral_trade finds Pareto improvements."""
        # Create agents with complementary preferences
        agent1 = Mock()
        agent1.id = 1
        agent1.carrying_inventory = {"good1": 2, "good2": 0}
        agent1.utility_function = CobbDouglasUtility(0.8, 0.2)  # Prefers good1

        agent2 = Mock()
        agent2.id = 2
        agent2.carrying_inventory = {"good1": 0, "good2": 2}
        agent2.utility_function = CobbDouglasUtility(0.2, 0.8)  # Prefers good2

        # Mock home inventories
        agent1.home_inventory = {"good1": 0, "good2": 0}
        agent2.home_inventory = {"good1": 0, "good2": 0}

        trade = find_beneficial_bilateral_trade(agent1, agent2)

        # Should find a beneficial trade
        assert trade is not None
        assert trade.is_pareto_improvement
        assert trade.agent_utility_gain > MIN_TRADE_UTILITY_GAIN
        assert trade.partner_utility_gain > MIN_TRADE_UTILITY_GAIN

    def test_find_beneficial_bilateral_trade_returns_none_for_unprofitable_trades(self):
        """Test that find_beneficial_bilateral_trade returns None for unprofitable trades."""
        # Create agents with same preferences (no benefit from trade)
        agent1 = Mock()
        agent1.id = 1
        agent1.carrying_inventory = {"good1": 1, "good2": 0}
        agent1.utility_function = CobbDouglasUtility(0.5, 0.5)

        agent2 = Mock()
        agent2.id = 2
        agent2.carrying_inventory = {"good1": 0, "good2": 1}
        agent2.utility_function = CobbDouglasUtility(0.5, 0.5)  # Same preferences

        # Mock home inventories
        agent1.home_inventory = {"good1": 0, "good2": 0}
        agent2.home_inventory = {"good1": 0, "good2": 0}

        trade = find_beneficial_bilateral_trade(agent1, agent2)

        # Should not find a beneficial trade
        assert trade is None

    def test_find_beneficial_bilateral_trade_only_proposes_1_to_1_trades(self):
        """Test that find_beneficial_bilateral_trade only proposes 1:1 trades."""
        # Create agents with complementary preferences
        agent1 = Mock()
        agent1.id = 1
        agent1.carrying_inventory = {"good1": 3, "good2": 0}
        agent1.utility_function = CobbDouglasUtility(0.8, 0.2)

        agent2 = Mock()
        agent2.id = 2
        agent2.carrying_inventory = {"good1": 0, "good2": 3}
        agent2.utility_function = CobbDouglasUtility(0.2, 0.8)

        # Mock home inventories
        agent1.home_inventory = {"good1": 0, "good2": 0}
        agent2.home_inventory = {"good1": 0, "good2": 0}

        trade = find_beneficial_bilateral_trade(agent1, agent2)

        # Should find a beneficial trade
        assert trade is not None

        # Should only propose 1:1 trades
        assert sum(trade.agent_gives.values()) == 1
        assert sum(trade.agent_receives.values()) == 1
        assert sum(trade.agent_gives.values()) == 1
        assert sum(trade.agent_receives.values()) == 1

    def test_find_best_trading_partner_applies_lowest_id_tiebreaking(self):
        """Test that find_best_trading_partner applies lowest-ID tiebreaking."""
        # Create agent seeking partner
        agent = Mock()
        agent.id = 1
        agent.carrying_inventory = {"good1": 1, "good2": 0}
        agent.utility_function = CobbDouglasUtility(0.2, 0.8)
        agent.home_inventory = {"good1": 0, "good2": 0}

        # Create multiple potential partners with same utility gain
        partners = []
        for i in range(3, 6):  # IDs 3, 4, 5
            partner = Mock()
            partner.id = i
            partner.carrying_inventory = {"good1": 0, "good2": 1}
            partner.utility_function = CobbDouglasUtility(0.8, 0.2)
            partner.home_inventory = {"good1": 0, "good2": 0}
            partners.append(partner)

        # Create AgentInfo objects
        nearby_agents = []
        for partner in partners:
            agent_info = Mock()
            agent_info.agent_id = partner.id
            agent_info.is_paired = False
            agent_info.has_goods = True
            agent_info.agent_ref = partner
            nearby_agents.append(agent_info)

        best_partner = find_best_trading_partner(agent, nearby_agents)

        # Should select partner with lowest ID (ID 3)
        assert best_partner.agent_id == 3


class TestDecisionAlgorithms:
    """Test decision algorithm functions."""

    def test_decide_forage_only_inventory_full_at_home_deposits(self):
        """Test that decide_forage_only deposits when inventory full at home."""
        # Create agent with full inventory at home
        agent = Mock()
        agent.id = 1
        agent.x = 10
        agent.y = 10
        agent.home_x = 10
        agent.home_y = 10
        agent.carrying_inventory = {"good1": CARRYING_CAPACITY}
        agent.home_inventory = {"good1": 0, "good2": 0}  # Need this for utility calculations
        agent.utility_function = CobbDouglasUtility(0.5, 0.5)  # Need this for utility calculations

        # Mock deposit_to_home to actually clear carrying inventory
        def mock_deposit(goods):
            agent.carrying_inventory = {"good1": 0}

        agent.deposit_to_home = Mock(side_effect=mock_deposit)

        # Create nearby resources
        nearby_resources = [
            ResourceInfo(x=12, y=10, resource_type="A", good_type="good1", quantity=1, distance=2)
        ]

        action = decide_forage_only(agent, nearby_resources, None, 1)

        # Should deposit goods
        agent.deposit_to_home.assert_called_once()

        # Should continue to find new resource
        assert action.mode == AgentMode.FORAGE
        assert action.target == (12, 10)

    def test_decide_forage_only_inventory_full_away_returns_home(self):
        """Test that decide_forage_only returns home when inventory full away."""
        # Create agent with full inventory away from home
        agent = Mock()
        agent.id = 1
        agent.x = 10
        agent.y = 10
        agent.home_x = 0
        agent.home_y = 0
        agent.carrying_inventory = {"good1": CARRYING_CAPACITY}

        nearby_resources = []

        action = decide_forage_only(agent, nearby_resources, None, 1)

        # Should return home
        assert action.mode == AgentMode.RETURN_HOME
        assert action.target == (0, 0)
        assert "inventory full" in action.reason

    def test_decide_forage_only_finds_best_resource(self):
        """Test that decide_forage_only finds and moves toward best resource."""
        # Create agent with empty carrying
        agent = Mock()
        agent.id = 1
        agent.x = 10
        agent.y = 10
        agent.carrying_inventory = {"good1": 0, "good2": 0}
        agent.utility_function = CobbDouglasUtility(0.5, 0.5)
        agent.home_inventory = {"good1": 0, "good2": 0}

        # Create nearby resources
        nearby_resources = [
            ResourceInfo(x=12, y=10, resource_type="A", good_type="good1", quantity=1, distance=2),
            ResourceInfo(x=15, y=10, resource_type="B", good_type="good2", quantity=1, distance=5),
        ]

        action = decide_forage_only(agent, nearby_resources, None, 1)

        # Should move toward resource
        assert action.mode == AgentMode.FORAGE
        assert action.target in [(12, 10), (15, 10)]

    def test_decide_forage_only_idle_when_no_resources(self):
        """Test that decide_forage_only returns idle when no resources available."""
        # Create agent with empty carrying
        agent = Mock()
        agent.id = 1
        agent.x = 10
        agent.y = 10
        agent.carrying_inventory = {"good1": 0, "good2": 0}

        nearby_resources = []

        action = decide_forage_only(agent, nearby_resources, None, 1)

        # Should be idle
        assert action.mode == AgentMode.IDLE
        assert "no resources available" in action.reason

    def test_decide_bilateral_exchange_only_speculative_withdrawal(self):
        """Test speculative withdrawal in bilateral exchange mode."""
        # Create agent with empty carrying but home goods at home
        agent = Mock()
        agent.id = 1
        agent.x = 10
        agent.y = 10
        agent.home_x = 10
        agent.home_y = 10
        agent.carrying_inventory = {"good1": 0, "good2": 0}
        agent.home_inventory = {"good1": 2, "good2": 1}
        agent.trading_partner = None
        agent.withdraw_from_home = Mock()

        nearby_agents = []

        action = decide_bilateral_exchange_only(agent, nearby_agents, None, 1)

        # Should withdraw goods speculatively
        agent.withdraw_from_home.assert_called_once()

        # Should be idle (no trading partners)
        assert action.mode == AgentMode.IDLE
        assert "withdrew goods but no trading partners available" in action.reason

    def test_decide_bilateral_exchange_only_returns_home_to_withdraw(self):
        """Test that decide_bilateral_exchange_only returns home to withdraw when away."""
        # Create agent with empty carrying but home goods away from home
        agent = Mock()
        agent.id = 1
        agent.x = 10
        agent.y = 10
        agent.home_x = 0
        agent.home_y = 0
        agent.carrying_inventory = {"good1": 0, "good2": 0}
        agent.home_inventory = {"good1": 2, "good2": 1}
        agent.trading_partner = None

        nearby_agents = []

        action = decide_bilateral_exchange_only(agent, nearby_agents, None, 1)

        # Should return home to withdraw
        assert action.mode == AgentMode.RETURN_HOME
        assert action.target == (0, 0)
        assert "returning home to withdraw goods for trading" in action.reason

    def test_decide_dual_mode_forage_priority_over_trading(self):
        """Test that decide_dual_mode prioritizes foraging over trading when carrying empty."""
        # Create agent with empty carrying
        agent = Mock()
        agent.id = 1
        agent.x = 10
        agent.y = 10
        agent.carrying_inventory = {"good1": 0, "good2": 0}
        agent.utility_function = CobbDouglasUtility(0.5, 0.5)
        agent.home_inventory = {"good1": 0, "good2": 0}
        agent.trading_partner = None

        # Create nearby resources and agents
        nearby_resources = [
            ResourceInfo(x=12, y=10, resource_type="A", good_type="good1", quantity=1, distance=2)
        ]

        nearby_agents = []  # No trading partners

        action = decide_dual_mode(agent, nearby_resources, nearby_agents, None, 1)

        # Should forage (priority over trading)
        assert action.mode == AgentMode.FORAGE
        assert action.target == (12, 10)

    def test_decide_dual_mode_speculative_withdrawal_fallback(self):
        """Test speculative withdrawal in dual mode (fallback only)."""
        # Create agent with empty carrying, no resources, but home goods at home
        agent = Mock()
        agent.id = 1
        agent.x = 10
        agent.y = 10
        agent.home_x = 10
        agent.home_y = 10
        agent.carrying_inventory = {"good1": 0, "good2": 0}
        agent.home_inventory = {"good1": 2, "good2": 1}
        agent.trading_partner = None
        agent.withdraw_from_home = Mock()

        nearby_resources = []  # No resources available
        nearby_agents = []  # No trading partners

        action = decide_dual_mode(agent, nearby_resources, nearby_agents, None, 1)

        # Should withdraw goods speculatively (fallback)
        agent.withdraw_from_home.assert_called_once()

        # Should be idle (no trading partners)
        assert action.mode == AgentMode.IDLE
        assert "withdrew goods but no trading partners available" in action.reason


class TestEntryPoint:
    """Test the main entry point function."""

    def test_make_agent_decision_dispatches_to_dual_mode(self):
        """Test that make_agent_decision dispatches to dual mode when both features enabled."""
        # Create mock agent
        agent = Mock()
        agent.id = 1
        agent.x = 10
        agent.y = 10
        agent.home_x = 10
        agent.home_y = 10
        agent.carrying_inventory = {"good1": 0, "good2": 0}
        agent.home_inventory = {"good1": 0, "good2": 0}
        agent.utility_function = CobbDouglasUtility(0.5, 0.5)
        agent.trading_partner = None  # No trading partner

        # Create mock grid and agents
        grid = Mock()
        grid.iter_resources.return_value = []

        all_agents = []

        # Create mock features with both enabled
        features = Mock()
        features.forage_enabled = True
        features.trade_execution_enabled = True

        action = make_agent_decision(agent, grid, all_agents, features, None, 1)

        # Should be idle (no opportunities)
        assert action.mode == AgentMode.IDLE
        assert "no opportunities available" in action.reason

    def test_make_agent_decision_dispatches_to_forage_only(self):
        """Test that make_agent_decision dispatches to forage-only when only forage enabled."""
        # Create mock agent
        agent = Mock()
        agent.id = 1
        agent.x = 10
        agent.y = 10
        agent.carrying_inventory = {"good1": 0, "good2": 0}

        # Create mock grid
        grid = Mock()
        grid.iter_resources.return_value = []

        all_agents = []

        # Create mock features with only forage enabled
        features = Mock()
        features.forage_enabled = True
        features.trade_execution_enabled = False

        action = make_agent_decision(agent, grid, all_agents, features, None, 1)

        # Should be idle (no resources)
        assert action.mode == AgentMode.IDLE
        assert "no resources available" in action.reason

    def test_make_agent_decision_dispatches_to_bilateral_exchange_only(self):
        """Test that make_agent_decision dispatches to bilateral exchange when only trade enabled."""
        # Create mock agent
        agent = Mock()
        agent.id = 1
        agent.x = 10
        agent.y = 10
        agent.home_x = 10
        agent.home_y = 10
        agent.carrying_inventory = {"good1": 0, "good2": 0}
        agent.home_inventory = {"good1": 0, "good2": 0}
        agent.utility_function = CobbDouglasUtility(0.5, 0.5)
        agent.trading_partner = None  # No trading partner

        # Create mock grid and agents
        grid = Mock()
        grid.iter_resources.return_value = []

        all_agents = []

        # Create mock features with only trade enabled
        features = Mock()
        features.forage_enabled = False
        features.trade_execution_enabled = True

        action = make_agent_decision(agent, grid, all_agents, features, None, 1)

        # Should be idle (no goods to trade)
        assert action.mode == AgentMode.IDLE
        assert "no goods to trade" in action.reason

    def test_make_agent_decision_dispatches_to_idle(self):
        """Test that make_agent_decision dispatches to idle when both features disabled."""
        # Create mock agent
        agent = Mock()
        agent.id = 1
        agent.x = 10
        agent.y = 10

        # Create mock grid and agents
        grid = Mock()
        grid.iter_resources.return_value = []

        all_agents = []

        # Create mock features with both disabled
        features = Mock()
        features.forage_enabled = False
        features.trade_execution_enabled = False

        action = make_agent_decision(agent, grid, all_agents, features, None, 1)

        # Should be idle
        assert action.mode == AgentMode.IDLE
        assert "all mechanisms disabled" in action.reason


class TestCarryingCapacity:
    """Test carrying capacity limits and related functionality."""

    def test_carrying_capacity_limit_100000_units(self):
        """Test that carrying capacity is set to 100,000 units."""
        assert CARRYING_CAPACITY == 100000

    def test_is_inventory_full_at_capacity(self):
        """Test that _is_inventory_full returns True at carrying capacity."""
        # Create agent at carrying capacity
        agent = Mock()
        agent.carrying_inventory = {"good1": CARRYING_CAPACITY}

        assert _is_inventory_full(agent)

    def test_is_inventory_full_below_capacity(self):
        """Test that _is_inventory_full returns False below carrying capacity."""
        # Create agent below carrying capacity
        agent = Mock()
        agent.carrying_inventory = {"good1": CARRYING_CAPACITY - 1}

        assert not _is_inventory_full(agent)

    def test_is_inventory_full_above_capacity(self):
        """Test that _is_inventory_full returns True above carrying capacity."""
        # Create agent above carrying capacity
        agent = Mock()
        agent.carrying_inventory = {"good1": CARRYING_CAPACITY + 1}

        assert _is_inventory_full(agent)

    def test_deposit_triggered_at_capacity(self):
        """Test that deposit is triggered when at carrying capacity and at home."""
        # Create agent at carrying capacity at home
        agent = Mock()
        agent.id = 1
        agent.x = 10
        agent.y = 10
        agent.home_x = 10
        agent.home_y = 10
        agent.carrying_inventory = {"good1": CARRYING_CAPACITY}
        agent.deposit_to_home = Mock()

        nearby_resources = []

        action = decide_forage_only(agent, nearby_resources, None, 1)

        # Should deposit goods
        agent.deposit_to_home.assert_called_once()


class TestHelperFunctions:
    """Test helper functions for decision logic."""

    def test_has_trading_partner(self):
        """Test _has_trading_partner helper function."""
        # Agent with trading partner
        agent_with_partner = Mock()
        agent_with_partner.trading_partner = Mock()  # Non-None trading partner

        assert _has_trading_partner(agent_with_partner)

        # Agent without trading partner
        agent_without_partner = Mock()
        agent_without_partner.trading_partner = None

        assert not _has_trading_partner(agent_without_partner)

    def test_is_co_located(self):
        """Test _is_co_located helper function."""
        agent1 = Mock()
        agent1.x = 10
        agent1.y = 10

        agent2 = Mock()
        agent2.x = 10
        agent2.y = 10

        assert _is_co_located(agent1, agent2)

        agent2.x = 11
        assert not _is_co_located(agent1, agent2)

    def test_has_carrying_goods(self):
        """Test _has_carrying_goods helper function."""
        # Agent with goods
        agent_with_goods = Mock()
        agent_with_goods.carrying_inventory = {"good1": 1, "good2": 0}

        assert _has_carrying_goods(agent_with_goods)

        # Agent without goods
        agent_without_goods = Mock()
        agent_without_goods.carrying_inventory = {"good1": 0, "good2": 0}

        assert not _has_carrying_goods(agent_without_goods)

    def test_has_home_goods(self):
        """Test _has_home_goods helper function."""
        # Agent with home goods
        agent_with_goods = Mock()
        agent_with_goods.home_inventory = {"good1": 1, "good2": 0}

        assert _has_home_goods(agent_with_goods)

        # Agent without home goods
        agent_without_goods = Mock()
        agent_without_goods.home_inventory = {"good1": 0, "good2": 0}

        assert not _has_home_goods(agent_without_goods)

    def test_is_at_home(self):
        """Test _is_at_home helper function."""
        # Agent at home
        agent_at_home = Mock()
        agent_at_home.x = 10
        agent_at_home.y = 10
        agent_at_home.home_x = 10
        agent_at_home.home_y = 10

        assert _is_at_home(agent_at_home)

        # Agent away from home
        agent_away = Mock()
        agent_away.x = 10
        agent_away.y = 10
        agent_away.home_x = 0
        agent_away.home_y = 0

        assert not _is_at_home(agent_away)


if __name__ == "__main__":
    pytest.main([__file__])
