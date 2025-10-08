"""
Base Test Framework - Abstract base classes for manual tests.

Provides common functionality extracted from existing tests.
"""

import os
import random
import sys
import time
from pathlib import Path
from typing import Any

from PyQt6.QtWidgets import QVBoxLayout, QWidget

from .debug_orchestrator import DebugOrchestrator
from .phase_manager import PhaseManager
from .simulation_factory import SimulationFactory
from .test_configs import TestConfiguration
from .ui_components import TestLayout


class BaseManualTest(QWidget):
    """Abstract base class for all manual tests with common functionality."""

    def __init__(self, config: TestConfiguration):
        super().__init__()
        self.config = config
        self.simulation = None
        self.current_turn = 0
        self.phase = 1
        self.ext_rng = random.Random(config.seed)  # External RNG seeded from config

        # Phase manager (will be set by subclasses or default to standard phases)
        self.phase_manager = None

        # Turn rate tracking for speed display
        from time import perf_counter

        self.turn_rate_start_time = perf_counter()
        self.turn_rate_start_turn = 0
        self.current_turn_rate = 0.0  # Actual turns/second

        # Note: Delta playback mode removed - GUI now uses live simulation only

        # Setup common components
        self.setup_ui()
        self.setup_debug_orchestrator()
        self.setup_timers()

        # Keep delta_file_path for filename generation
        self.delta_file_path: str | None = None

        # Store batch mode flag for use in showEvent

        self.batch_mode = os.environ.get("ECONSIM_BATCH_UNLIMITED_SPEED") == "1"
        if self.batch_mode:
            print("🚀 Batch mode detected - Will auto-start after GUI is shown")

    def setup_ui(self):
        """Create standardized layout (viewport + control panel; debug panel removed)."""
        self.setWindowTitle(f"Manual Test {self.config.id}: {self.config.name}")
        # Narrower width now that the debug panel is removed
        self.setGeometry(100, 100, 900, 700)

        # Create main layout using TestLayout component
        self.test_layout = TestLayout(self.config)
        # TestLayout is now a QWidget, so we need to add it as a widget, not set it as a layout
        layout = QVBoxLayout()
        layout.addWidget(self.test_layout)
        self.setLayout(layout)

        # Connect control panel signals
        self.test_layout.control_panel.start_button.clicked.connect(self.start_test)
        self.test_layout.control_panel.speed_combo.currentIndexChanged.connect(
            self.on_speed_changed
        )

    def setup_debug_orchestrator(self):
        """Configure debug logging for this test."""
        self.debug_orchestrator = DebugOrchestrator(self.config)

        # Debug timer is handled by the debug panel

    def setup_timers(self):
        """Setup timers for playback controls."""
        # No continuous timer needed - updates happen on step changes via callbacks
        pass

    def showEvent(self, event):
        """Override showEvent to auto-start in batch mode after GUI is visible."""
        super().showEvent(event)

        # Auto-start if in batch mode and not already started
        if self.batch_mode and not hasattr(self, "_auto_start_attempted"):
            self._auto_start_attempted = True
            print("🚀 GUI is now visible - Auto-starting test in batch mode...")
            # Use QTimer to allow the GUI to fully render
            from PyQt6.QtCore import QTimer

            self.auto_start_timer = QTimer(self)  # Store as instance variable with parent
            self.auto_start_timer.setSingleShot(True)
            self.auto_start_timer.timeout.connect(self.auto_start_test)
            self.auto_start_timer.start(1000)  # Start after 1 second
            print("🔧 Auto-start timer created and started")

    def auto_start_test(self):
        """Auto-start the test in batch mode by calling start_test directly."""
        print("🚀 Auto-starting test in batch mode...")
        try:
            # Check if the UI is properly set up
            if hasattr(self, "test_layout") and hasattr(self.test_layout, "control_panel"):
                button = self.test_layout.control_panel.start_button
                print(f"🔧 Button state: enabled={button.isEnabled()}, text='{button.text()}'")

                # Ensure button is enabled before starting
                if not button.isEnabled():
                    button.setEnabled(True)
                    print("🔧 Enabled start button for auto-start")

                # Call start_test method directly
                self.start_test()
                print("✅ Auto-start test initiated successfully")
            else:
                print("❌ Auto-start failed - UI components not ready")
        except Exception as e:
            print(f"❌ Auto-start failed with error: {e}")
            import traceback

            traceback.print_exc()

    def start_test(self):
        """Start test - either live simulation or headless with delta recording."""
        try:
            # Always run live simulation - delta recording is now handled automatically by the simulation
            self.log_status("🎮 Starting live simulation (delta recording enabled by default)...")
            self.create_live_simulation()
            self.setup_live_simulation_mode()

            # Start the simulation immediately at the selected speed
            self.start_live_simulation_immediately()

            print(f"✅ Test {self.config.id} started! Live simulation running")
            print("📁 Delta recording running in background - check sim_runs/ for recorded data")
            print("🎮 Use speed controls to adjust simulation speed!")

        except Exception as e:
            print(f"❌ Error in test workflow: {e}")
            import traceback

            traceback.print_exc()

    def simulation_step(self):
        """Execute one simulation step and handle phase transitions."""
        if not self.simulation:
            return

        # Check if test is complete BEFORE processing next turn
        total_turns = self.get_total_turns()
        if self.current_turn >= total_turns:
            # Test already complete, stop test timer (pygame continues rendering)
            if self.step_timer.isActive():
                self.step_timer.stop()
                print(f"⏹️  Test timer stopped - test complete at {total_turns} turns")
            return

        # Increment turn counter
        self.current_turn += 1

        # Calculate actual turn rate (updated every 10 turns for smoothness)
        if self.current_turn % 10 == 0:
            from time import perf_counter

            current_time = perf_counter()
            elapsed = current_time - self.turn_rate_start_time
            if elapsed > 0:
                turns_elapsed = self.current_turn - self.turn_rate_start_turn
                self.current_turn_rate = turns_elapsed / elapsed
                # Reset tracking window
                self.turn_rate_start_time = current_time
                self.turn_rate_start_turn = self.current_turn

        # Check for phase transitions (implemented by subclasses)
        self.check_phase_transition()

        # Configure simulation behavior for current phase (new approach)
        if hasattr(self, "phase_manager"):
            current_features = self.phase_manager.get_current_features(self.current_turn)
            self.simulation.configure_behavior(current_features)

        # Execute simulation step
        self.simulation.step(self.ext_rng)

        # Update realtime widget if in live mode
        if hasattr(self, "pygame_widget") and hasattr(self.pygame_widget, "update_simulation"):
            self.pygame_widget.update_simulation(self.simulation)

        # Update display
        self.update_display()

        # Log periodic status and economic metrics
        if self.current_turn % 50 == 0:
            agent_count = len(self.simulation.agents)
            resource_count = len(list(self.simulation.grid.iter_resources()))

            # Calculate performance metrics like the main simulation does
            steps_per_sec = 60.0  # Default fallback
            frame_ms = 16.7  # Default fallback

            if hasattr(self.simulation, "_step_times") and len(self.simulation._step_times) >= 2:
                time_window = self.simulation._step_times[-1] - self.simulation._step_times[0]
                if time_window > 0:
                    steps_per_sec = (len(self.simulation._step_times) - 1) / time_window
                    frame_ms = (time_window / (len(self.simulation._step_times) - 1)) * 1000

            # Resource flow analysis
            resource_by_type = {"good1": 0, "good2": 0}
            for resource in self.simulation.grid.iter_resources():
                _, _, res_type = resource
                resource_by_type[str(res_type)] = resource_by_type.get(str(res_type), 0) + 1

            # Agent inventory analysis
            total_carrying = {"good1": 0, "good2": 0}
            total_home_inventory = {"good1": 0, "good2": 0}
            for agent in self.simulation.agents:
                for res_type, count in agent.carrying_inventory.items():
                    total_carrying[res_type] = total_carrying.get(res_type, 0) + count
                for res_type, count in agent.home_inventory.items():
                    total_home_inventory[res_type] = total_home_inventory.get(res_type, 0) + count

            # Spatial analytics (legacy debug logging removed - observer system handles structured logging)
            agent_positions = [(agent.x, agent.y) for agent in self.simulation.agents]

            # Calculate center of mass
            if agent_positions:
                center_x = sum(pos[0] for pos in agent_positions) / len(agent_positions)
                center_y = sum(pos[1] for pos in agent_positions) / len(agent_positions)

                # Calculate average distance from center (clustering metric)
                total_distance = sum(
                    ((pos[0] - center_x) ** 2 + (pos[1] - center_y) ** 2) ** 0.5
                    for pos in agent_positions
                )
                avg_distance_from_center = total_distance / len(agent_positions)

                # Calculate average inter-agent distance (sample first 5 agents for performance)
                sample_agents = self.simulation.agents[: min(5, len(self.simulation.agents))]
                inter_distances = []
                for i, agent1 in enumerate(sample_agents):
                    for agent2 in sample_agents[i + 1 :]:
                        dist = ((agent1.x - agent2.x) ** 2 + (agent1.y - agent2.y) ** 2) ** 0.5
                        inter_distances.append(dist)

                avg_inter_distance = (
                    sum(inter_distances) / len(inter_distances) if inter_distances else 0
                )

        # Check if we just completed the final turn
        total_turns = self.get_total_turns()
        if self.current_turn >= total_turns:
            self.step_timer.stop()

            print("🔧 Test logging session complete (observer system)")

            # Finalize delta recording before showing completion message
            self.cleanup_simulation()

            self.test_layout.control_panel.start_button.setText("Test Completed!")
            self.test_layout.control_panel.status_text.setText(
                f"🎉 Test completed! All {total_turns} turns executed with phase transitions."
            )
            print("=" * 60)
            print(f"🎉 TEST COMPLETED SUCCESSFULLY! ({total_turns} turns)")
            print("All phases executed. Check the behavior observations above.")
            print("=" * 60)

            # Auto-exit if running in batch mode or debug mode
            import os

            if os.environ.get("ECONSIM_BATCH_UNLIMITED_SPEED") == "1":
                print("🚀 Batch mode - Auto-exiting after completion")
                # Use QTimer to allow GUI to finish processing before exit
                from PyQt6.QtCore import QTimer

                self.exit_timer = QTimer(self)  # Store as instance variable with parent
                self.exit_timer.setSingleShot(True)
                self.exit_timer.timeout.connect(self.batch_mode_exit)
                self.exit_timer.start(3000)  # Exit after 3 second delay
            elif os.environ.get("ECONSIM_DEBUG_TARGET_ARROWS") == "1":
                print("🎯 Debug mode - Auto-closing window after completion")
                # Use QTimer to allow GUI to finish processing before closing
                from PyQt6.QtCore import QTimer

                self.debug_exit_timer = QTimer(self)  # Store as instance variable with parent
                self.debug_exit_timer.setSingleShot(True)
                self.debug_exit_timer.timeout.connect(self.debug_mode_close)
                self.debug_exit_timer.start(2000)  # Close after 2 second delay
                print("🔧 Auto-exit timer created and started")

    def batch_mode_exit(self):
        """Exit the application when in batch mode."""
        print("🚀 Batch mode - Exiting application NOW")
        print("🔧 Closing window...")
        self.close()

        print("🔧 Quitting QApplication...")
        from PyQt6.QtWidgets import QApplication

        app = QApplication.instance()
        if app:
            app.quit()
            print("🔧 QApplication quit() called")
        else:
            print("⚠️  No QApplication instance found")

        print("🔧 Calling sys.exit(0)...")

        sys.exit(0)

    def debug_mode_close(self):
        """Close the window when in debug mode (gentler than full exit)."""
        print("🎯 Debug mode - Closing test window")
        print("🔧 Target arrow debugging complete - window closing...")
        self.close()

        # For debug mode, we just close the window rather than exiting the entire application
        # This allows the Qt application to continue running and exit gracefully when the
        # last window closes, or the user can manually exit from the terminal
        print("✅ Debug window closed - simulation data recorded to sim_runs/")

    def check_phase_transition(self):
        """Check if we need to transition to a new phase. Override in subclasses."""
        pass

    def get_total_turns(self) -> int:
        """Get the total number of turns for this test. Override in subclasses."""
        return 900  # Default for legacy tests

    def update_display(self):
        """Update the UI display with current simulation state."""
        if not self.simulation:
            return

        agent_count = len(self.simulation.agents)
        resource_count = len(list(self.simulation.grid.iter_resources()))

        # Update control panel with turn rate
        self.test_layout.control_panel.update_display(
            turn=self.current_turn,
            phase=self.phase,
            agent_count=agent_count,
            resource_count=resource_count,
            phase_manager=getattr(self, "phase_manager", None),
            turn_rate=self.current_turn_rate,
        )

    def on_speed_changed(self, index):
        """Handle speed selection change."""
        from .test_utils import get_timer_interval

        speed_names = [
            "1 turn/sec",
            "3 turns/sec",
            "10 turns/sec",
            "20 turns/sec",
            "UNLIMITED (as fast as possible)",
        ]
        interval = get_timer_interval(index)

        if hasattr(self, "step_timer") and self.step_timer.isActive():
            # Update running timer interval
            self.step_timer.setInterval(interval)
            if interval == 0:
                print("⏱️  Speed changed to: UNLIMITED - running as fast as possible!")
            else:
                print(f"⏱️  Speed changed to: {speed_names[index]} (interval: {interval}ms)")

        # Update status display to reflect new speed
        self.update_display()

    def run_headless_simulation_with_deltas(self):
        """Run simulation headless with visual delta recording."""
        # Create sim_runs directory if it doesn't exist
        sim_runs_dir = Path("sim_runs")
        sim_runs_dir.mkdir(exist_ok=True)

        # Generate delta file path with format: {shortdate}{short24hourtime}{testname}
        now = time.localtime()
        short_date = f"{now.tm_year:04d}{now.tm_mon:02d}{now.tm_mday:02d}"
        short_time = f"{now.tm_hour:02d}{now.tm_min:02d}{now.tm_sec:02d}"
        test_name = self.config.name.replace(" ", "_").replace(":", "").replace("/", "_")

        filename = f"{short_date}{short_time}_{test_name}.dat"
        self.delta_file_path = str(sim_runs_dir / filename)

        # Generate agent positions
        agent_positions = self._generate_agent_positions()

        # Note: Delta recording removed - will be replaced by DebugRecorder
        print("🎬 Running simulation (recording system to be implemented)")

        # Create simulation using the factory
        simulation = SimulationFactory.create_simulation(self.config)

        # Run simulation
        total_turns = self.get_total_turns()
        start_time = time.time()

        print(f"🎬 Running simulation for {total_turns} steps...")

        for step in range(1, total_turns + 1):
            # Configure simulation behavior for current phase (new approach)
            if hasattr(self, "phase_manager") and self.phase_manager:
                current_features = self.phase_manager.get_current_features(step)
                simulation.configure_behavior(current_features)
            else:
                # Fallback: create standard phase manager if none exists
                from .phase_manager import PhaseManager

                self.phase_manager = PhaseManager.create_standard_phases()
                current_features = self.phase_manager.get_current_features(step)
                simulation.configure_behavior(current_features)

            # Check for phase transitions and log them
            if hasattr(self, "phase_manager") and self.phase_manager:
                transition = self.phase_manager.check_transition(
                    step, getattr(self, "current_phase", 1)
                )
                if transition:
                    print(f"  🔄 Phase transition at step {step}: {transition.description}")
                    self.current_phase = transition.new_phase

            # Step simulation
            simulation.step(random.Random(self.config.seed + step))

            # Progress update
            if step % 100 == 0:
                print(f"  📊 Step {step}/{total_turns}")

        end_time = time.time()
        print(f"✅ Headless simulation completed: {end_time - start_time:.2f}s")

    def load_delta_file(self):
        """Stub: Delta playback removed. TODO: Implement with DebugRecorder."""
        print("⚠️  Delta playback not available (removed in October 2025)")
        print("    Will be re-implemented with new DebugRecorder system")

        # Create pygame widget for live simulation mode
        if not hasattr(self, "pygame_widget") or not self.pygame_widget:
            # Always use live simulation mode
            from econsim.gui.embedded.realtime_pygame_v2 import RealtimePygameWidgetV2

            self.pygame_widget = RealtimePygameWidgetV2(live_simulation=self.simulation)
            print("🎮 Using live simulation mode")

            self.pygame_widget.setFixedSize(self.config.viewport_size, self.config.viewport_size)

            # Replace placeholder in layout
            self.test_layout.replace_viewport(self.pygame_widget)
        else:
            # Update existing widget to live mode
            from econsim.gui.embedded.realtime_pygame_v2 import RealtimePygameWidgetV2

            old_widget = self.pygame_widget
            self.pygame_widget = RealtimePygameWidgetV2(live_simulation=self.simulation)
            self.pygame_widget.setFixedSize(self.config.viewport_size, self.config.viewport_size)
            self.test_layout.replace_viewport(self.pygame_widget)
            print("🎮 Switched to live simulation mode")

    def setup_playback_controls(self):
        """Stub: Playback controls removed. TODO: Implement with DebugRecorder."""
        print("⚠️  Playback controls not available (delta recorder removed)")
        # Note: This method is stubbed out - playback will be re-implemented with DebugRecorder

    def create_live_simulation(self):
        """Create the simulation object for live mode."""
        from econsim.gui.launcher.framework.simulation_factory import SimulationFactory

        # Generate agent positions
        agent_positions = self._generate_agent_positions()

        # Create simulation using the factory
        self.simulation = SimulationFactory.create_simulation(self.config)

        print("🎮 Live simulation object created")

    def setup_live_simulation_mode(self):
        """Setup live simulation mode with realtime pygame widget."""
        # Create pygame widget for live simulation rendering - use V2 pygame widget
        if not hasattr(self, "pygame_widget") or not self.pygame_widget:
            from econsim.gui.embedded.realtime_pygame_v2 import RealtimePygameWidgetV2

            self.pygame_widget = RealtimePygameWidgetV2(live_simulation=self.simulation)
            self.pygame_widget.setFixedSize(self.config.viewport_size, self.config.viewport_size)

            # Replace placeholder in layout
            self.test_layout.replace_viewport(self.pygame_widget)
            print("🎮 Using live simulation mode")

        # Hide playback controls (not needed for live mode)
        if hasattr(self.test_layout, "playback_controls"):
            self.test_layout.hide_playback_controls()

        # Setup live simulation controls
        self.setup_live_simulation_controls()

        print("🎮 Live simulation mode ready - use speed controls to watch live simulation")

    def cleanup_simulation(self):
        """Cleanup simulation resources."""
        if hasattr(self, "simulation") and self.simulation:
            print("🧹 Simulation cleanup completed")

    def setup_live_simulation_controls(self):
        """Setup controls for live simulation mode."""
        # Connect speed control to live simulation
        if hasattr(self.test_layout, "control_panel"):
            control_panel = self.test_layout.control_panel
            if hasattr(control_panel, "speed_combo"):
                # Disconnect any existing connections
                try:
                    control_panel.speed_combo.currentIndexChanged.disconnect()
                except TypeError:
                    pass  # No connections to disconnect

                # Connect to live simulation speed control
                control_panel.speed_combo.currentIndexChanged.connect(self.on_live_speed_changed)

        # Setup step timer for live simulation
        if not hasattr(self, "step_timer"):
            from PyQt6.QtCore import QTimer

            self.step_timer = QTimer()
            self.step_timer.timeout.connect(self.simulation_step)

        # Set initial speed from dropdown
        if hasattr(self.test_layout, "control_panel"):
            speed_index = self.test_layout.control_panel.speed_combo.currentIndex()
            self.on_live_speed_changed(speed_index)

        # Start button already connected to start_test, which now handles live mode

    def start_live_simulation_immediately(self):
        """Start the live simulation immediately at the selected speed."""
        if not self.simulation:
            print("❌ No simulation available to start")
            return

        if hasattr(self, "step_timer"):
            # Get current speed setting
            if hasattr(self.test_layout, "control_panel"):
                speed_index = self.test_layout.control_panel.speed_combo.currentIndex()
                from .test_utils import get_timer_interval

                interval = get_timer_interval(speed_index)

                if interval > 0:
                    self.step_timer.start(interval)
                    print(f"▶️  Live simulation started at {interval}ms interval")
                else:
                    # Unlimited speed - run as fast as possible
                    self.step_timer.start(1)  # 1ms interval for maximum speed
                    print("▶️  Live simulation started at unlimited speed")
            else:
                print("❌ No control panel available")
        else:
            print("❌ No step timer available")

    def on_live_speed_changed(self, index):
        """Handle speed selection change for live simulation."""
        from .test_utils import get_timer_interval

        speed_names = [
            "1 turn/sec",
            "3 turns/sec",
            "10 turns/sec",
            "20 turns/sec",
            "UNLIMITED (as fast as possible)",
        ]
        interval = get_timer_interval(index)

        if hasattr(self, "step_timer") and self.step_timer.isActive():
            # Update running timer interval
            self.step_timer.setInterval(interval)
            if interval == 0:
                print("⏱️  Speed changed to: UNLIMITED - running as fast as possible!")
            else:
                print(f"⏱️  Speed changed to: {speed_names[index]} (interval: {interval}ms)")

        # Update status display to reflect new speed
        self.update_display()

    def playback_timer_tick(self):
        """Stub: Playback removed."""
        pass

    def toggle_playback(self):
        """Stub: Playback removed."""
        pass

    def rewind_playback(self):
        """Stub: Playback removed."""
        pass

    def fast_forward_playback(self):
        """Stub: Playback removed."""
        pass

    def on_playback_speed_changed(self, index: int):
        """Stub: Playback removed."""
        pass

    def on_comprehensive_step_changed(self, step: int):
        """Stub: Playback removed."""
        pass

    def on_comprehensive_state_changed(self, visual_state):
        """Stub: Playback removed."""
        pass

    def get_economic_analysis(self, step: int | None = None) -> dict[str, Any]:
        """Stub: Economic analysis removed (delta recorder removed)."""
        return {}

    def get_agent_analysis(self, agent_id: int, step: int | None = None) -> dict[str, Any]:
        """Stub: Agent analysis removed (delta recorder removed)."""
        return {}

    def show_economic_analysis(self):
        """Stub: Economic analysis removed (delta recorder removed)."""
        print("⚠️  Economic analysis not available (delta recorder removed)")

    def get_current_phase_info(self, turn: int) -> tuple[int, str]:
        """Get current phase information for a given turn.

        Returns:
            Tuple of (phase_number, phase_description)
        """
        if self.phase_manager:
            phase_info = self.phase_manager.get_current_phase_info(turn)
            if phase_info:
                return phase_info.number, phase_info.description
            else:
                return 1, "Default (both enabled)"
        else:
            # Fallback: create standard phase manager if none exists
            from .phase_manager import PhaseManager

            self.phase_manager = PhaseManager.create_standard_phases()
            phase_info = self.phase_manager.get_current_phase_info(turn)
            if phase_info:
                return phase_info.number, phase_info.description
            else:
                return 1, "Default (both enabled)"

    def update_playback_display(self):
        """Stub: Playback display removed (delta recorder removed)."""
        pass

    def _generate_agent_positions(self):
        """Generate agent positions for the simulation."""
        agent_positions = []
        rng = random.Random(self.config.seed)

        for i in range(self.config.agent_count):
            x = rng.randint(0, self.config.grid_size[0] - 1)
            y = rng.randint(0, self.config.grid_size[1] - 1)
            agent_positions.append((x, y))

        return agent_positions

    def log_status(self, message: str):
        """Log status message and update UI."""
        print(message)
        if hasattr(self, "test_layout") and hasattr(self.test_layout, "control_panel"):
            self.test_layout.control_panel.status_text.setText(message)


class StandardPhaseTest(BaseManualTest):
    """Standard 6-phase test with common phase transitions."""

    def __init__(self, config: TestConfiguration):
        super().__init__(config)
        # Use custom phases if provided, otherwise use standard phases
        if config.custom_phases:
            self.phase_manager = PhaseManager(config.custom_phases)
        else:
            self.phase_manager = PhaseManager.create_standard_phases()

    def check_phase_transition(self):
        """Check for phase transitions."""
        transition = self.phase_manager.check_transition(self.current_turn, self.phase)
        if transition:
            self.phase = transition.new_phase

    def get_total_turns(self) -> int:
        """Get the total number of turns from phase manager."""
        return self.phase_manager.get_total_turns()


class CustomPhaseTest(BaseManualTest):
    """For tests with custom phase schedules."""

    def __init__(self, config: TestConfiguration):
        super().__init__(config)
        # Custom phases are required for this test type
        if not config.custom_phases:
            raise ValueError("CustomPhaseTest requires custom_phases in TestConfiguration")
        self.phase_manager = PhaseManager(config.custom_phases)

    def check_phase_transition(self):
        """Check for custom phase transitions."""
        transition = self.phase_manager.check_transition(self.current_turn, self.phase)
        if transition:
            self.phase = transition.new_phase
