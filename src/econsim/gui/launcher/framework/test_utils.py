"""
Shared utilities for manual tests.
"""

from PyQt6.QtWidgets import QComboBox, QHBoxLayout, QLabel


def create_speed_control(parent, on_speed_changed_callback):
    """Create a speed control layout with dropdown and callback."""
    speed_layout = QHBoxLayout()
    speed_layout.addWidget(QLabel("Test Speed:"))

    speed_combo = QComboBox()
    speed_combo.addItems(
        ["1 turn/second", "3 turns/second", "10 turns/second", "20 turns/second", "Unlimited"]
    )
    speed_combo.setCurrentIndex(4)  # Default to Unlimited
    speed_combo.currentIndexChanged.connect(on_speed_changed_callback)

    speed_layout.addWidget(speed_combo)

    return speed_layout, speed_combo


def get_timer_interval(speed_index):
    """Get timer interval in milliseconds based on speed index.

    Note: 0ms interval means the timer fires as fast as possible,
    limited only by simulation step performance (no artificial throttle).
    """
    speed_map = {
        0: 1000,  # 1 turn/second = 1000ms
        1: 333,  # 3 turns/second = 333ms
        2: 100,  # 10 turns/second = 100ms
        3: 50,  # 20 turns/second = 50ms
        4: 0,  # Unlimited = 0ms (as fast as possible)
    }
    return speed_map.get(speed_index, 1000)


def get_estimated_duration(speed_index, total_turns=900):
    """Get estimated test duration in seconds.

    Returns None for unlimited speed (can't estimate accurately).
    """
    interval_ms = get_timer_interval(speed_index)
    if interval_ms == 0:
        return None  # Unlimited - can't estimate
    return (total_turns * interval_ms) / 1000


def format_duration(seconds):
    """Format duration for display.

    Returns special string for None (unlimited speed).
    """
    if seconds is None:
        return "as fast as possible"
    if seconds < 60:
        return f"{seconds:.1f} seconds"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f} minutes"
    else:
        hours = seconds / 3600
        return f"{hours:.1f} hours"
