"""
Simulation Factory - Standardized simulation creation from configurations.

Handles resource generation, agent positioning, and preference factories.
"""

import random

from econsim.simulation.config import SimConfig
from econsim.simulation.coordinator import SimulationCoordinator

from .test_configs import TestConfiguration


class SimulationFactory:
    """Standardized simulation creation from test configurations."""

    @staticmethod
    def create_simulation(test_config: TestConfiguration) -> SimulationCoordinator:
        """Create simulation from test configuration."""

        # Generate resources using test-specific seed
        resources = SimulationFactory._generate_resources(test_config)

        # Generate agent positions
        agent_positions = SimulationFactory._generate_agent_positions(test_config)

        # Build simulation config
        sim_config = SimConfig(
            grid_size=test_config.grid_size,
            initial_resources=resources,
            agent_count=test_config.agent_count,
            seed=test_config.seed,
            enable_respawn=True,
            enable_metrics=True,
            perception_radius=test_config.perception_radius,
            respawn_target_density=test_config.resource_density,
            respawn_rate=0.25,  # Standard rate from existing tests
            distance_scaling_factor=getattr(test_config, "distance_scaling_factor", 0.0),
            viewport_size=test_config.viewport_size,
            name=test_config.name,  # Pass test name for file naming
        )

        # Create and return simulation
        return SimulationCoordinator.from_config(sim_config, agent_positions=agent_positions)

    @staticmethod
    def _generate_resources(test_config: TestConfiguration) -> list:
        """Generate resources based on test configuration."""
        grid_w, grid_h = test_config.grid_size
        resource_count = int(grid_w * grid_h * test_config.resource_density)

        resource_rng = random.Random(test_config.seed)
        resources = []
        for _ in range(resource_count):
            x = resource_rng.randint(0, grid_w - 1)
            y = resource_rng.randint(0, grid_h - 1)
            resource_type = resource_rng.choice(["A", "B"])
            resources.append((x, y, resource_type))

        return resources

    @staticmethod
    def _generate_agent_positions(test_config: TestConfiguration) -> list:
        """Generate non-overlapping agent positions."""
        grid_w, grid_h = test_config.grid_size

        # Use config seed for positions (ensures different layouts with different seeds)
        pos_rng = random.Random(test_config.seed)

        positions = set()
        while len(positions) < test_config.agent_count:
            x = pos_rng.randint(0, grid_w - 1)
            y = pos_rng.randint(0, grid_h - 1)
            positions.add((x, y))

        return list(positions)
