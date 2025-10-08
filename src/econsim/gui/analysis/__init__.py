"""Economic analysis displays for VMT EconSim.

This package contains GUI components for displaying and analyzing economic
data from simulation runs. These components were migrated from the main
gui package for better organization.

Components:
-----------
- EconomicAnalysisWidget: Displays economic data from comprehensive simulation deltas
"""

# Import from local modules (new structure) with PyQt6 fallback
try:
    from .economic_analysis_widget import EconomicAnalysisWidget

    _analysis_available = True
except ImportError:
    # PyQt6 not available - create fallback object
    EconomicAnalysisWidget = None
    _analysis_available = False

__all__ = ["EconomicAnalysisWidget"]
