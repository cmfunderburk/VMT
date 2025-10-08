# Simulation Package
# Core simulation domain and components

# Import compatibility layer - allows gradual migration
# New structure imports - all components migrated
from .agent import Agent, set_agent_mode
from .config import SimConfig
from .constants import (
    DEFAULT_DISTANCE_SCALING_FACTOR,
    EPSILON_UTILITY,
    UTILITY_SCALE_FACTOR,
    AgentMode,
    default_PERCEPTION_RADIUS,
)
from .coordinator import Simulation, SimulationCoordinator
from .executor import OptimizedStepExecutor
from .executor import UnifiedStepExecutor as StepExecutor
from .features import SimulationFeatures
