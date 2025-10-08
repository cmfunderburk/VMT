"""Unit tests for SimulationCoordinator.

Tests coordinator initialization, agent index management, and state ownership patterns.
"""

import pytest

from econsim.simulation.agent.core import Agent
from econsim.simulation.agent.utility_functions import CobbDouglasUtility
from econsim.simulation.coordinator import SimulationCoordinator
from econsim.simulation.world.grid import Grid


class TestCoordinatorAgentIndexing:
    """Test agent index management in SimulationCoordinator."""

    def test_coordinator_index_builds_on_init(self):
        """Test that agent index is built correctly during coordinator initialization.
        
        This test verifies that rebuild_agent_index() is called during __post_init__
        and creates a proper _agent_by_id dictionary for O(1) lookups.
        """
        # Create agents with specific IDs
        agents = [
            Agent(
                id=0,
                x=5,
                y=5,
                utility_function=CobbDouglasUtility(0.5, 0.5),
                home_x=5,
                home_y=5,
            ),
            Agent(
                id=1,
                x=10,
                y=10,
                utility_function=CobbDouglasUtility(0.6, 0.4),
                home_x=10,
                home_y=10,
            ),
            Agent(
                id=2,
                x=15,
                y=15,
                utility_function=CobbDouglasUtility(0.7, 0.3),
                home_x=15,
                home_y=15,
            ),
        ]

        # Create grid
        grid = Grid(20, 20, [])

        # Create coordinator (this triggers __post_init__ which calls rebuild_agent_index)
        coordinator = SimulationCoordinator(grid=grid, _initial_agents=agents)

        # Verify the index was built correctly
        assert len(coordinator._agent_by_id) == 3
        assert 0 in coordinator._agent_by_id
        assert 1 in coordinator._agent_by_id
        assert 2 in coordinator._agent_by_id

        # Verify each ID maps to the correct agent
        assert coordinator._agent_by_id[0] is agents[0]
        assert coordinator._agent_by_id[1] is agents[1]
        assert coordinator._agent_by_id[2] is agents[2]

    def test_find_agent_by_id_lookup(self):
        """Test that _find_agent_by_id uses the index for O(1) lookups."""
        agents = [
            Agent(
                id=10,
                x=0,
                y=0,
                utility_function=CobbDouglasUtility(0.5, 0.5),
                home_x=0,
                home_y=0,
            ),
            Agent(
                id=20,
                x=5,
                y=5,
                utility_function=CobbDouglasUtility(0.5, 0.5),
                home_x=5,
                home_y=5,
            ),
        ]

        grid = Grid(10, 10, [])
        coordinator = SimulationCoordinator(grid=grid, _initial_agents=agents)

        # Test successful lookups
        found_agent_10 = coordinator._find_agent_by_id(10)
        assert found_agent_10 is not None
        assert found_agent_10.id == 10
        assert found_agent_10 is agents[0]

        found_agent_20 = coordinator._find_agent_by_id(20)
        assert found_agent_20 is not None
        assert found_agent_20.id == 20
        assert found_agent_20 is agents[1]

        # Test lookup for non-existent agent returns None
        not_found = coordinator._find_agent_by_id(999)
        assert not_found is None

    def test_rebuild_agent_index_updates_mapping(self):
        """Test that rebuild_agent_index() can be called to update the index.
        
        This verifies the public API that the executor would use if agent lifecycle
        were implemented (Phase 2.3, currently skipped).
        """
        # Start with initial agents
        agents = [
            Agent(
                id=0,
                x=0,
                y=0,
                utility_function=CobbDouglasUtility(0.5, 0.5),
                home_x=0,
                home_y=0,
            ),
        ]

        grid = Grid(10, 10, [])
        coordinator = SimulationCoordinator(grid=grid, _initial_agents=agents)

        # Verify initial state
        assert len(coordinator._agent_by_id) == 1
        assert coordinator._find_agent_by_id(0) is agents[0]

        # Simulate what executor would do if it modified the agent list
        # (In real implementation, executor owns agents and would modify executor.agents)
        new_agent = Agent(
            id=1,
            x=5,
            y=5,
            utility_function=CobbDouglasUtility(0.5, 0.5),
            home_x=5,
            home_y=5,
        )
        
        # For this test, we manually modify _initial_agents to simulate the scenario
        # In production, executor would modify executor.agents and call rebuild_agent_index()
        coordinator._initial_agents.append(new_agent)

        # Call rebuild_agent_index (public API for executor)
        coordinator.rebuild_agent_index()

        # Verify index was updated
        assert len(coordinator._agent_by_id) == 2
        assert coordinator._find_agent_by_id(0) is agents[0]
        assert coordinator._find_agent_by_id(1) is new_agent

    def test_agents_property_returns_executor_agents_when_executor_exists(self):
        """Test that agents property proxies to executor's agents after step() is called.
        
        This verifies the Phase 2 refactor where coordinator provides read-only
        access to executor's canonical agent list.
        """
        agents = [
            Agent(
                id=0,
                x=0,
                y=0,
                utility_function=CobbDouglasUtility(0.5, 0.5),
                home_x=0,
                home_y=0,
            ),
        ]

        grid = Grid(10, 10, [])
        coordinator = SimulationCoordinator(grid=grid, _initial_agents=agents)

        # Before step() is called, executor doesn't exist yet
        assert coordinator._step_executor is None
        # agents property should return initial agents
        assert coordinator.agents is coordinator._initial_agents

        # After step() is called, executor is created
        import random
        rng = random.Random(42)
        coordinator.step(rng)

        # Now executor exists
        assert coordinator._step_executor is not None
        # agents property should proxy to executor's agents
        assert coordinator.agents is coordinator._step_executor.agents

    def test_agents_property_is_read_only(self):
        """Test that agents property cannot be assigned (no setter exists).
        
        This verifies Phase 2.1 requirement: removed @agents.setter to make
        agents a read-only proxy.
        """
        agents = [
            Agent(
                id=0,
                x=0,
                y=0,
                utility_function=CobbDouglasUtility(0.5, 0.5),
                home_x=0,
                home_y=0,
            ),
        ]

        grid = Grid(10, 10, [])
        coordinator = SimulationCoordinator(grid=grid, _initial_agents=agents)

        # Attempting to assign to agents property should raise AttributeError
        new_agents = []
        with pytest.raises(AttributeError, match="can't set attribute|property.*has no setter"):
            coordinator.agents = new_agents


class TestCoordinatorInitialization:
    """Test coordinator initialization patterns."""

    def test_from_config_initializes_index(self):
        """Test that from_config() creates coordinator with initialized index."""
        from econsim.simulation.config import SimConfig

        config = SimConfig(
            grid_size=(10, 10),
            initial_resources=[],
            agent_count=2,
            seed=42,
        )

        # Provide agent positions for initialization
        agent_positions = [(0, 0), (5, 5)]

        coordinator = SimulationCoordinator.from_config(config, agent_positions=agent_positions)

        # Verify agents were created
        assert len(coordinator._initial_agents) == 2

        # Verify index was built during initialization
        assert len(coordinator._agent_by_id) == 2
        assert coordinator._find_agent_by_id(0) is not None
        assert coordinator._find_agent_by_id(1) is not None

    def test_coordinator_respawn_scheduler_proxied_to_executor(self):
        """Test that respawn_scheduler property proxies to executor (Phase 2.4).
        
        This verifies that RespawnScheduler ownership moved to executor,
        with coordinator providing read-only access.
        """
        agents = [
            Agent(
                id=0,
                x=0,
                y=0,
                utility_function=CobbDouglasUtility(0.5, 0.5),
                home_x=0,
                home_y=0,
            ),
        ]

        grid = Grid(10, 10, [])
        coordinator = SimulationCoordinator(grid=grid, _initial_agents=agents)

        # Before executor is created, respawn_scheduler property returns None
        assert coordinator.respawn_scheduler is None

        # After step() creates executor
        import random
        rng = random.Random(42)
        coordinator.step(rng)

        # respawn_scheduler property should proxy to executor's respawn_scheduler
        # (In test setup, respawn is disabled, so executor.respawn_scheduler is None)
        assert coordinator.respawn_scheduler is coordinator._step_executor.respawn_scheduler
