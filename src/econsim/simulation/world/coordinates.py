"""Coordinate utilities for grid and spatial operations.

Provides coordinate type definitions and utility functions for grid-based
simulation operations including bounds checking and coordinate validation.
"""

from __future__ import annotations

# Type definitions
Coord = tuple[int, int]
Cell = tuple[int, int]  # Grid coordinate (x, y) - alias for compatibility


def validate_coordinate(x: int, y: int, width: int, height: int) -> None:
    """Validate that coordinates are within grid bounds.

    Args:
        x: X coordinate
        y: Y coordinate
        width: Grid width
        height: Grid height

    Raises:
        ValueError: If coordinates are out of bounds
    """
    if not (0 <= x < width and 0 <= y < height):
        raise ValueError(f"Coordinate ({x},{y}) out of bounds for {width}x{height} grid")


def manhattan_distance(x1: int, y1: int, x2: int, y2: int) -> int:
    """Calculate Manhattan distance between two coordinates.

    Args:
        x1, y1: First coordinate
        x2, y2: Second coordinate

    Returns:
        Manhattan distance between the coordinates
    """
    return abs(x1 - x2) + abs(y1 - y2)


def is_adjacent(x1: int, y1: int, x2: int, y2: int) -> bool:
    """Check if two coordinates are adjacent (Manhattan distance of 1).

    Args:
        x1, y1: First coordinate
        x2, y2: Second coordinate

    Returns:
        True if coordinates are adjacent, False otherwise
    """
    return manhattan_distance(x1, y1, x2, y2) == 1


def normalize_coordinate(x: int, y: int, width: int, height: int) -> tuple[int, int]:
    """Normalize coordinates to be within grid bounds using modulo.

    Args:
        x, y: Coordinates to normalize
        width: Grid width
        height: Grid height

    Returns:
        Normalized coordinates within bounds
    """
    return (x % width, y % height)


__all__ = [
    "Coord",
    "Cell",
    "validate_coordinate",
    "manhattan_distance",
    "is_adjacent",
    "normalize_coordinate",
]
