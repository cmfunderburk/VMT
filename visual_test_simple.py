#!/usr/bin/env python3
"""Visual Test - Simple Auto-Launch at 20 FPS

Automatically launches High Density Local test (ID=3) with visual debugging at comfortable viewing speed.
"""

import sys
import os
import random
from datetime import datetime

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def main():
    """Launch High Density Local test with visual debugging at 20 FPS."""
    print("👁️  Auto-launching High Density Local test for visual debugging at 20 FPS...")
    
    try:
        # Set debug mode environment variable to enable auto-close
        os.environ['ECONSIM_DEBUG_TARGET_ARROWS'] = '1'
        
        # Initialize QApplication first
        from PyQt6.QtWidgets import QApplication
        app = QApplication(sys.argv)
        
        # Apply dark mode styling (same as launcher)
        from econsim.gui.launcher.style import PlatformStyler
        PlatformStyler.configure_application(app)
        
        from econsim.gui.launcher.test_runner import create_test_runner
        from econsim.gui.launcher.framework.test_configs import TestConfiguration
        
        # Create and run test
        runner = create_test_runner()
        print("✅ TestRunner initialized")
        
        # Generate random seed for pseudorandom starting positions
        # Use current time to ensure different seed each run
        now = datetime.now()
        random_seed = int(now.timestamp() * 1_000_000)
        
        print("🚀 Launching Test ID 3: High Density Local (with random seed)")
        print(f"   Seed: {random_seed} (for pseudorandom starting positions)")
        print("   Grid: 15x15, Agents: 30, Resource Density: 80%, Perception: 5")
        print("   Speed: Default 20 turns/second for comfortable visual observation")
        print("   Watch console for target debug logs")
        print("   Observe GUI for target arrow behavior")
        print()
        
        # Create custom config based on Test 3 but with random seed
        config = TestConfiguration(
            id=3,
            name="High Density Local (Random)",
            description="Tests crowding behavior with many agents and short perception (random seed)",
            grid_size=(15, 15),
            agent_count=30,
            resource_density=0.8,
            perception_radius=5,
            preference_mix="mixed",
            seed=random_seed
        )
        
        # Launch with custom config
        runner.run_config(config)
        
        print("✅ Test launched! GUI window should be open.")
        print("🔍 Look for debug output with these patterns:")
        print("   🎯 Target changes: Agent assignments") 
        print("   🔄 Target kept: Agents maintaining targets")
        print("   🧺 Collection events: When targets get cleared")
        print("   🏠 Return home: When agents target home")
        print("\n💡 GUI running at default 20 turns/second - close window or press Ctrl+C to exit")
        
        # Run the Qt event loop
        return app.exec()
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(main())