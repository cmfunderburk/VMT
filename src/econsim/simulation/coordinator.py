"""Simulation coordinator orchestrating agent and grid progression.

Manages per-tick simulation steps with support for deterministic decision-making,
bilateral trading, unified target selection, and spatial optimization. Maintains
single-threaded execution with optional resource respawn and metrics collection.

Execution Modes:
* Deterministic: Unified target selection with distance-discounted utility
* Legacy: Random walk movement for regression comparison
* Trading: Feature-flagged bilateral exchange with intent enumeration

Step Sequence:
1. Agent target selection (resource vs trading partner)
2. Movement toward targets with spatial collision handling
3. Resource collection and trade intent enumeration/execution
4. Home deposit logic and mode transitions
5. Respawn and metrics hooks
"""

from __future__ import annotations

import random
import random as _random
from dataclasses import dataclass, field
from typing import Any

try:  # Local import guard (optional config not always present yet)
    from .config import SimConfig  # type: ignore
except Exception:  # pragma: no cover
    SimConfig = Any  # fallback for type checkers


# Import from new structure (these modules exist in the new architecture)
# Legacy bilateral trading system removed - replaced by V2 unified decision engine

from .agent.core import Agent
from .constants import AgentMode
from .world.grid import Grid
# RespawnScheduler import removed - now initialized in executor

# Observer system removed - replaced by comprehensive delta system


def _debug_log_mode_change(
    agent: Agent, old_mode: AgentMode, new_mode: AgentMode, reason: str = "", step: int = 0
) -> None:
    """Log agent mode transitions - observer system removed."""
    # Observer system removed - mode changes are now recorded by comprehensive delta system
    pass


@dataclass(slots=True)
class SimulationCoordinator:
    """Core simulation engine coordinating agents, grid, and economic interactions.

    Manages deterministic stepping with configurable behavioral systems including
    resource foraging, bilateral trading, and spatial agent interactions.
    Provides factory construction and runtime configuration capabilities.
    """

    grid: Grid
    _initial_agents: list[Agent]  # Initial agent list (before executor takes ownership)
    _steps: int = 0
    config: Any | None = None  # SimConfig when available
    _cached_feature_flags: Any | None = None  # Cached feature flags to avoid recreating every step
    _rng: _random.Random | None = None  # Internal RNG (hooks, future stochastic systems)
    # respawn_scheduler moved to executor (now accessed via property proxy)
    _respawn_interval: int | None = (
        1  # How frequently to invoke respawn (1 => every step default; None/<=0 => disabled)
    )
    # Legacy trade system removed - replaced by V2 unified decision engine
    executed_trade: Any | None = None
    # Cached spatial index for performance optimization
    _spatial_index: Any | None = None
    # Last executed trade cell highlight bookkeeping (GUI render hint; purely observational)
    _last_trade_highlight: tuple[int, int, int] | None = None  # (x,y,expire_step)
    # Performance tracking for debug logging
    _step_times: list[float] = field(default_factory=list)
    # Step execution system (Phase 2: Step Decomposition)
    _step_executor: Any = field(default=None)
    # Pre-step resource snapshot for collection metrics (not part of determinism hash)
    pre_step_resource_count: int | None = None
    # Captured aggregated step metrics (non-deterministic hash; for testing/diagnostics)
    last_step_metrics: dict[str, Any] | None = None
    # O(1) agent lookup index (performance optimization)
    _agent_by_id: dict[int, Agent] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Initialize internal RNG from config seed if available."""
        if self.config is not None and self._rng is None:
            seed = getattr(self.config, "seed", 0)
            self._rng = _random.Random(int(seed))

        # Build agent lookup index for O(1) access
        self.rebuild_agent_index()

        # Observer system removed - comprehensive delta system handles all recording

    def configure_behavior(self, features: Any) -> None:
        """Update behavior configuration for current step.

        Args:
            features: SimulationFeatures object with current phase behavior
        """
        self._cached_feature_flags = features

    def step(self, rng: random.Random) -> None:
        """Advance simulation by one step using optimized step executor.

        Uses OptimizedStepExecutor to eliminate handler dispatch overhead while
        maintaining deterministic behavior and performance characteristics.

        Args:
            rng: External RNG for backward compatibility with existing code patterns
        """
        # Initialize optimized step executor on first use
        if self._step_executor is None:
            self._initialize_optimized_step_executor()

        # Snapshot pre-step resource count for collection metrics (decision/unified modes)
        try:
            self.pre_step_resource_count = self.grid.resource_count()
        except Exception:
            self.pre_step_resource_count = None

        # Execute step through optimized executor (no context creation overhead)
        self._step_executor.execute_step(rng)

        # Raw data architecture: Events are recorded directly by handlers via observer.record_*() calls
        # No event buffer needed - zero overhead recording during simulation

        # Update step counter (handlers assume previous self._steps during execution)
        self._steps += 1

        # Optional lightweight FPS debug (will migrate to MetricsHandler once implemented)
        # (FPS debug moved to MetricsHandler metrics; print removed to avoid duplication)

        # Expire highlight if past lifetime
        if self._last_trade_highlight is not None:
            _, _, expire = self._last_trade_highlight
            if self._steps >= expire:
                self._last_trade_highlight = None

        # Observer system removed - comprehensive delta system handles all recording

        # Clear transient cross-handler scratch data
        if hasattr(self, "_transient_foraged_ids"):
            try:
                delattr(self, "_transient_foraged_ids")
            except Exception:
                pass
        # Reset snapshot for next step
        self.pre_step_resource_count = None

    def _initialize_optimized_step_executor(self) -> None:
        """Initialize the optimized step executor for high performance.

        Uses OptimizedStepExecutor to eliminate handler dispatch overhead
        while maintaining exact behavioral compatibility.
        """
        from .executor import UnifiedStepExecutor as StepExecutor

        self._step_executor = StepExecutor(self, self._initial_agents)

    # Legacy handler architecture removed - OptimizedStepExecutor is the only execution path

    @property
    def steps(self) -> int:
        return self._steps

    @property
    def agents(self) -> list[Agent]:
        """Get agents list (read-only proxy to executor's canonical state).
        
        Returns executor's agent list if executor exists, otherwise returns
        the initial agent list stored during configuration.
        """
        if self._step_executor is not None:
            return self._step_executor.agents
        return self._initial_agents

    @property
    def respawn_scheduler(self) -> Any | None:
        """Get respawn scheduler (read-only proxy to executor's component).
        
        Returns executor's respawn scheduler if executor exists, otherwise None.
        Executor owns runtime components.
        """
        if self._step_executor is not None:
            return self._step_executor.respawn_scheduler
        return None

    def serialize(self) -> dict[str, Any]:
        """Export simulation state to JSON-serializable dict."""
        return {
            "grid": self.grid.serialize(),
            "agents": [a.serialize() for a in self.agents],
            "steps": self._steps,
        }

    # --- Factory Constructor -----------------------------------------------
    @staticmethod
    def _generate_random_positions(
        count: int, grid_size: tuple[int, int], seed: int
    ) -> list[tuple[int, int]]:
        """Generate random agent spawn positions with best-effort uniqueness.

        Attempts to generate unique positions but allows duplicates if grid is saturated
        (count > grid cells) or after max attempts to prevent infinite loops.

        Args:
            count: Number of positions to generate
            grid_size: Grid dimensions (width, height)
            seed: RNG seed for deterministic generation

        Returns:
            List of (x, y) position tuples (may contain duplicates if necessary)
        """
        import random as _random

        grid_w, grid_h = grid_size
        pos_rng = _random.Random(seed)
        positions: set[tuple[int, int]] = set()

        # Best effort: try to generate unique positions (max 1000 attempts per position)
        max_attempts_per_position = 1000
        attempts = 0

        while len(positions) < count and attempts < count * max_attempts_per_position:
            x = pos_rng.randint(0, grid_w - 1)
            y = pos_rng.randint(0, grid_h - 1)
            positions.add((x, y))
            attempts += 1

        # If we couldn't get enough unique positions, fill remainder with random positions
        # (allows duplicates to prevent infinite loop)
        while len(positions) < count:
            x = pos_rng.randint(0, grid_w - 1)
            y = pos_rng.randint(0, grid_h - 1)
            positions.add((x, y))
            # Force add even if duplicate by converting to list and appending
            if len(positions) < count:
                result = list(positions)
                while len(result) < count:
                    x = pos_rng.randint(0, grid_w - 1)
                    y = pos_rng.randint(0, grid_h - 1)
                    result.append((x, y))
                return result

        return list(positions)

    @classmethod
    def from_config(
        cls,
        config: Any,  # SimConfig (forward reference; kept Any to avoid circular import issues for type checkers)
        *,
        agent_positions: list[tuple[int, int]] | None = None,
    ) -> SimulationCoordinator:
        """Create simulation from configuration with optional agent positions.

        If agent_positions is None, generates random positions for config.agent_count agents.
        If agent_positions is provided, must have exactly config.agent_count elements.

        Args:
            config: SimConfig instance with validated parameters
            agent_positions: Optional explicit spawn coordinates. If provided, must match
                config.agent_count length exactly.

        Returns:
            Configured simulation with attached hooks based on config flags

        Raises:
            ValueError: If agent_positions length doesn't match config.agent_count
        """
        config.validate()

        # Generate positions if not provided, or validate if provided
        if agent_positions is None:
            agent_positions = cls._generate_random_positions(
                config.agent_count, config.grid_size, config.seed
            )
        else:
            # Validate that provided positions match config agent_count
            if len(agent_positions) != config.agent_count:
                raise ValueError(
                    f"agent_positions length ({len(agent_positions)}) must match "
                    f"config.agent_count ({config.agent_count})"
                )

        # Build grid with initial resources
        grid = Grid(config.grid_size[0], config.grid_size[1], config.initial_resources)

        agents: list[Agent] = []
        if agent_positions:
            # Create agents with utility functions (no legacy preference system)
            for idx, (x, y) in enumerate(agent_positions):
                from .agent.utility_functions import create_utility_function

                utility_func = create_utility_function("cobb_douglas", alpha=0.5, beta=0.5)
                agents.append(
                    Agent(
                        id=idx,
                        x=int(x),
                        y=int(y),
                        home_x=int(x),
                        home_y=int(y),
                        utility_function=utility_func,
                    )
                )

        sim = cls(grid=grid, _initial_agents=agents, config=config)

        # Internal RNG (deterministic) always seeded for future systems
        sim._rng = _random.Random(int(config.seed))

        # Respawn scheduler initialization moved to executor (runtime component ownership)

        return sim

    # --- Runtime Configuration -------------------------------------------
    def set_respawn_interval(self, interval: int | None) -> None:
        """Adjust how often the respawn scheduler is invoked.

        interval = 1  => every step (default)
        interval = N>1 => every Nth step
        interval None or <=0 => disable respawn without detaching scheduler
        Deterministic: purely arithmetic on step counter.
        """
        if interval is None or interval <= 0:
            self._respawn_interval = None
        else:
            self._respawn_interval = int(interval)

    def _invalidate_spatial_index(self) -> None:
        """Invalidate cached spatial index (e.g., when grid size changes)."""
        self._spatial_index = None

    def rebuild_agent_index(self) -> None:
        """Rebuild agent ID lookup index for O(1) access.

        Call this whenever the agents list is modified (initialization, test setup).
        Public API for executor to trigger index synchronization.
        """
        self._agent_by_id = {agent.id: agent for agent in self.agents}

    # Legacy bilateral exchange movement method removed - replaced by V2 unified decision engine

    def _find_agent_by_id(self, agent_id: int) -> Agent | None:
        """Find an agent by ID using O(1) lookup, returning None if not found."""
        return self._agent_by_id.get(agent_id)

    # Legacy unified selection pass method removed - replaced by V2 unified decision engine


# Backward compatibility alias
Simulation = SimulationCoordinator

__all__ = ["SimulationCoordinator", "Simulation"]
