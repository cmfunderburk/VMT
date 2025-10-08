import os

import pytest

# Modern simulation feature flags
SIMULATION_FEATURE_FLAGS = ["ECONSIM_FORAGE_ENABLED", "ECONSIM_TRADE_DRAFT", "ECONSIM_TRADE_EXEC"]


@pytest.fixture(autouse=True)
def reset_simulation_feature_flags():  # type: ignore[no-untyped-def]
    """Reset simulation feature flags to defaults between tests.

    Modern feature flag management using SimulationFeatures.from_environment().
    Ensures tests start with known default state and cleanup any flag changes.

    Default state:
    - ECONSIM_FORAGE_ENABLED: enabled (default when absent)
    - ECONSIM_TRADE_DRAFT: disabled (explicit opt-in)
    - ECONSIM_TRADE_EXEC: disabled (explicit opt-in)
    """
    # Store original values
    original_values = {}
    for flag in SIMULATION_FEATURE_FLAGS:
        original_values[flag] = os.environ.get(flag)

    # Clear all flags to ensure clean defaults
    for flag in SIMULATION_FEATURE_FLAGS:
        if flag in os.environ:
            del os.environ[flag]

    yield

    # Restore original values
    for flag in SIMULATION_FEATURE_FLAGS:
        if flag in os.environ:
            del os.environ[flag]
        if original_values[flag] is not None:
            os.environ[flag] = original_values[flag]
