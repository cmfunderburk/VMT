"""VMT Launcher GUI package (migrated from tools/launcher).

This package provides the test launcher GUI functionality, migrated from
the tools/launcher directory to consolidate all GUI components under the
gui hierarchy.

Public APIs maintain backward compatibility with the original tools/launcher
package while providing the new import path.
"""

# Import from local modules (new structure)
from .app_window import LauncherWindow, VMTLauncherWindow, create_launcher_window
from .cards import CustomTestCardWidget, TestCard, TestCardModel, TestCardWidget, build_card_models
from .comparison import ComparisonController
from .data import DataLocationResolver
from .discovery import CustomTestDiscovery
from .executor import TestExecutor
from .gallery import TestGallery
from .registry import TestRegistry
from .style import PlatformStyler
from .tabs import AbstractTab, CustomTestsTab, LauncherTabs
from .test_runner import TestRunner, create_test_runner
from .types import (
    CustomTestInfo,
    ExecutionRecord,
    ExecutionResult,
    RegistryValidationResult,
    TestConfiguration,
)
from .widgets import TestGalleryWidget

__all__ = [
    "PlatformStyler",
    "DataLocationResolver",
    "CustomTestDiscovery",
    "CustomTestInfo",
    "TestConfiguration",
    "ExecutionResult",
    "ExecutionRecord",
    "RegistryValidationResult",
    "TestRegistry",
    "ComparisonController",
    "TestExecutor",
    "build_card_models",
    "TestCard",
    "TestCardModel",
    "TestGallery",
    "LauncherTabs",
    "AbstractTab",
    "CustomTestsTab",
    "TestGalleryWidget",
    "LauncherWindow",
    "create_launcher_window",
    "VMTLauncherWindow",
    "TestRunner",
    "create_test_runner",
]

__version_placeholder__ = "0.1.0-dev-scaffold"
