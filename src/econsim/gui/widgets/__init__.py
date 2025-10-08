"""Reusable GUI widgets for VMT tools.

This package contains GUI components that can be used across different
VMT tools and applications. These widgets were migrated from tools/widgets
for proper architectural separation and reusability.

Components:
-----------
- ConfigEditor: Live configuration editing with validation and presets
- BatchRunner: Batch test execution with progress tracking
"""

# Import from local modules (new structure) with PyQt6 fallback
try:
    from .batch_runner import BatchRunner
    from .config_editor import ConfigEditor

    _widgets_available = True
except ImportError:
    # PyQt6 not available - create fallback objects
    ConfigEditor = None
    BatchRunner = None
    _widgets_available = False

__all__ = ["ConfigEditor", "BatchRunner"]
