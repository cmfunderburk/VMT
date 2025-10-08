"""GUI package for VMT EconSim

Provides all GUI components including launcher, widgets, analysis displays,
and embedded pygame components. This package consolidates all user interface
functionality under a single hierarchy.

The GUI package is organized into functional areas:
- launcher: Test launcher GUI (migrated from tools/launcher)
- widgets: Reusable GUI widgets (migrated from tools/widgets)
- analysis: Economic analysis displays (migrated from gui/)
- embedded: Embedded pygame components (migrated from gui/)
"""

# Import from local modules (new structure)
from .analysis import *
from .embedded import *
from .launcher import *
from .widgets import *

__all__ = [
    # Launcher components
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
    # Widget components
    "ConfigEditor",
    "BatchRunner",
    # Analysis components
    "EconomicAnalysisWidget",
]
