"""VMT Launcher Entry Point

Provides the main entry point for the VMT launcher application.
"""

from __future__ import annotations

import sys

from .runner import main

if __name__ == "__main__":
    sys.exit(main())
