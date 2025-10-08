"""Canonical Agent unit tests (renamed from test_agent_v2)."""

import pytest

from econsim.simulation.agent.core import Agent
from econsim.simulation.agent.utility_functions import (
    CobbDouglasUtility,
    PerfectComplementsUtility,
    PerfectSubstitutesUtility,
)
from econsim.simulation.constants import AgentMode


class TestAgentBasic:
    def test_agent_creation_defaults(self):
        utility = CobbDouglasUtility(0.6, 0.4)
        agent = Agent(id=1, x=10, y=20, utility_function=utility, home_x=10, home_y=20)
        assert (agent.id, agent.x, agent.y) == (1, 10, 20)
        assert (agent.home_x, agent.home_y) == (10, 20)
        assert agent.mode == AgentMode.FORAGE
        assert agent.target is None
        assert agent.carrying_inventory == {"good1": 0, "good2": 0}
        assert agent.home_inventory == {"good1": 0, "good2": 0}
        assert agent.trading_partner is None

    def test_agent_creation_with_inventories(self):
        utility = PerfectSubstitutesUtility(1.0, 2.0)
        agent = Agent(
            id=2,
            x=5,
            y=15,
            utility_function=utility,
            home_x=0,
            home_y=0,
            carrying_inventory={"good1": 10, "good2": 5},
            home_inventory={"good1": 20, "good2": 15},
        )
        assert agent.carrying_inventory == {"good1": 10, "good2": 5}
        assert agent.home_inventory == {"good1": 20, "good2": 15}

    def test_utility_function_attribute(self):
        u = CobbDouglasUtility(0.5, 0.5)
        agent = Agent(id=7, x=0, y=0, utility_function=u, home_x=0, home_y=0)
        assert agent.utility_function is u


class TestAgentUtilityIntegration:
    def test_total_bundle(self):
        utility = CobbDouglasUtility(0.5, 0.5)
        agent = Agent(
            id=1,
            x=0,
            y=0,
            utility_function=utility,
            home_x=0,
            home_y=0,
            carrying_inventory={"good1": 10, "good2": 5},
            home_inventory={"good1": 20, "good2": 15},
        )
        assert agent.get_total_bundle() == {"good1": 30, "good2": 20}

    def test_cobb_douglas_utility_value(self):
        utility = CobbDouglasUtility(0.5, 0.5)
        agent = Agent(
            id=1,
            x=0,
            y=0,
            utility_function=utility,
            home_x=0,
            home_y=0,
            carrying_inventory={"good1": 10, "good2": 5},
            home_inventory={"good1": 20, "good2": 15},
        )
        val = agent.calculate_current_utility()
        assert 24.0 < val < 25.0

    def test_inventory_capacity_flag(self):
        utility = PerfectComplementsUtility(1.0, 1.0)
        agent = Agent(id=3, x=0, y=0, utility_function=utility, home_x=0, home_y=0)
        assert not agent.is_inventory_full()
        agent.carrying_inventory = {"good1": 50000, "good2": 50000}
        assert agent.is_inventory_full()


class TestAgentInventoryManagement:
    def _make(self, carrying=None, home=None):
        return Agent(
            id=11,
            x=10,
            y=20,
            utility_function=CobbDouglasUtility(0.6, 0.4),
            home_x=10,
            home_y=20,
            carrying_inventory=carrying or {"good1": 0, "good2": 0},
            home_inventory=home or {"good1": 0, "good2": 0},
        )

    def test_deposit_partial(self):
        a = self._make(carrying={"good1": 10, "good2": 5}, home={"good1": 20, "good2": 15})
        a.deposit_to_home({"good1": 5, "good2": 2})
        assert a.carrying_inventory == {"good1": 5, "good2": 3}
        assert a.home_inventory == {"good1": 25, "good2": 17}

    def test_deposit_all(self):
        a = self._make(carrying={"good1": 10, "good2": 5}, home={"good1": 20, "good2": 15})
        a.deposit_to_home()
        assert a.carrying_inventory == {"good1": 0, "good2": 0}
        assert a.home_inventory == {"good1": 30, "good2": 20}

    def test_deposit_not_at_home_error(self):
        a = Agent(
            id=99,
            x=10,
            y=20,
            utility_function=CobbDouglasUtility(0.5, 0.5),
            home_x=0,
            home_y=0,
            carrying_inventory={"good1": 10, "good2": 5},
        )
        with pytest.raises(ValueError, match="cannot deposit - not at home"):
            a.deposit_to_home({"good1": 5})

    def test_deposit_insufficient_error(self):
        a = self._make(carrying={"good1": 5, "good2": 3})
        with pytest.raises(ValueError, match="cannot deposit 10 good1 - only carrying 5"):
            a.deposit_to_home({"good1": 10})

    def test_withdraw_partial(self):
        a = self._make(carrying={"good1": 5, "good2": 3}, home={"good1": 25, "good2": 17})
        a.withdraw_from_home({"good1": 10, "good2": 5})
        assert a.carrying_inventory == {"good1": 15, "good2": 8}
        assert a.home_inventory == {"good1": 15, "good2": 12}

    def test_withdraw_all(self):
        a = self._make(carrying={"good1": 5, "good2": 3}, home={"good1": 25, "good2": 17})
        a.withdraw_from_home()
        assert a.carrying_inventory == {"good1": 30, "good2": 20}
        assert a.home_inventory == {"good1": 0, "good2": 0}

    def test_withdraw_not_at_home_error(self):
        a = Agent(
            id=55,
            x=10,
            y=20,
            utility_function=CobbDouglasUtility(0.5, 0.5),
            home_x=0,
            home_y=0,
            home_inventory={"good1": 25, "good2": 17},
        )
        with pytest.raises(ValueError, match="cannot withdraw - not at home"):
            a.withdraw_from_home({"good1": 10})

    def test_withdraw_insufficient_error(self):
        a = self._make(carrying={"good1": 0, "good2": 0}, home={"good1": 5, "good2": 3})
        with pytest.raises(ValueError, match="cannot withdraw 10 good1 - only have 5"):
            a.withdraw_from_home({"good1": 10})


class TestAgentConvenienceMethods:
    def test_at_home_flag(self):
        a = Agent(
            id=1, x=10, y=20, utility_function=CobbDouglasUtility(0.5, 0.5), home_x=10, home_y=20
        )
        assert a.at_home()
        a.x = 11
        assert not a.at_home()

    def test_carrying_total(self):
        a = Agent(
            id=1,
            x=0,
            y=0,
            utility_function=PerfectSubstitutesUtility(1.0, 2.0),
            home_x=0,
            home_y=0,
            carrying_inventory={"good1": 10, "good2": 5},
        )
        assert a.carrying_total() == 15

    def test_home_inventory_total(self):
        a = Agent(
            id=1,
            x=0,
            y=0,
            utility_function=PerfectComplementsUtility(1.0, 1.0),
            home_x=0,
            home_y=0,
            home_inventory={"good1": 20, "good2": 15},
        )
        assert a.home_inventory_total() == 35

    def test_goods_flags(self):
        a = Agent(id=1, x=0, y=0, utility_function=CobbDouglasUtility(0.6, 0.4), home_x=0, home_y=0)
        assert not a.has_carrying_goods()
        assert not a.has_home_goods()
        a.carrying_inventory["good1"] = 5
        a.home_inventory["good2"] = 3
        assert a.has_carrying_goods()
        assert a.has_home_goods()

    def test_is_co_located_with(self):
        a1 = Agent(
            id=1, x=10, y=20, utility_function=CobbDouglasUtility(0.5, 0.5), home_x=0, home_y=0
        )
        a2 = Agent(
            id=2,
            x=10,
            y=20,
            utility_function=PerfectSubstitutesUtility(1.0, 1.0),
            home_x=5,
            home_y=15,
        )
        assert a1.is_co_located_with(a2)
        a2.x = 11
        assert not a1.is_co_located_with(a2)


class TestAgentSerialization:
    def test_serialize_roundtrip_fields(self):
        a = Agent(
            id=1,
            x=10,
            y=20,
            utility_function=CobbDouglasUtility(0.6, 0.4),
            home_x=0,
            home_y=0,
            mode=AgentMode.FORAGE,
            target=(15, 25),
            carrying_inventory={"good1": 10, "good2": 5},
            home_inventory={"good1": 20, "good2": 15},
        )
        data = a.serialize()
        assert data["id"] == 1
        assert data["x"] == 10 and data["y"] == 20
        assert data["home"] == (0, 0)
        assert data["mode"] == "forage"
        assert data["target"] == (15, 25)
        assert data["carrying_inventory"] == {"good1": 10, "good2": 5}
        assert data["home_inventory"] == {"good1": 20, "good2": 15}
        assert data["utility_function"]["type"] == "cobb_douglas"
        assert data["utility_function"]["parameters"]["alpha"] == 0.6
        assert data["utility_function"]["parameters"]["beta"] == 0.4
        assert data["trading_partner_id"] is None
