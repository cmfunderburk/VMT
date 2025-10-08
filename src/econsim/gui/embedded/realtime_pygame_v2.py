"""Realtime Pygame Widget for V2 Simulation Rendering

Dedicated pygame widget for rendering live V2 simulation state in real-time.
Compatible with the new unified decision engine and V2 agent architecture.
"""

from __future__ import annotations

from typing import Any

import pygame
from PyQt6.QtCore import QRect, QTimer
from PyQt6.QtGui import QImage, QPainter
from PyQt6.QtWidgets import QWidget


class RealtimePygameWidgetV2(QWidget):
    """Pygame widget for real-time V2 simulation rendering."""

    SURFACE_SIZE = (600, 600)
    FRAME_INTERVAL_MS = 16  # ~60 FPS target

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        live_simulation: Any | None = None,
    ) -> None:
        super().__init__(parent)

        # DEBUG: Widget creation tracking (commented out for production)
        # print("🎮 DEBUG: RealtimePygameWidgetV2 created!")

        # Store live simulation for direct rendering
        self.live_simulation: Any | None = live_simulation

        # Widget state
        self._surface: pygame.Surface | None = None
        self._closed = False
        self._frame = 0

        # Sprite management
        self._sprites: dict[str, pygame.Surface] = {}
        self._agent_sprite_map: dict[int, str] = {}  # agent_id -> sprite_key

        # Initialize pygame if needed
        self._init_pygame()

        # Load sprites
        self._load_sprites()

        # Setup rendering timer
        self._timer = QTimer()
        self._timer.timeout.connect(self._render_frame)
        self._timer.start(self.FRAME_INTERVAL_MS)

    def _init_pygame(self) -> None:
        """Initialize pygame if not already initialized."""
        if not pygame.get_init():
            pygame.init()

    def _load_sprites(self) -> None:
        """Load sprites for rendering."""
        try:
            import os

            # Get the project root directory (go up from source/econsim/gui/embedded/)
            project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../"))

            # Load agent sprites from sprite packs
            agent_sprite_files = [
                os.path.join(project_root, "vmt_sprites_pack_1", "agent_red_64.png"),
                os.path.join(project_root, "vmt_sprites_pack_1", "agent_blue_64.png"),
                os.path.join(project_root, "vmt_sprites_pack_2", "agent_green_64.png"),
                os.path.join(project_root, "vmt_sprites_pack_2", "agent_purple_64.png"),
                os.path.join(project_root, "vmt_sprites_pack_2", "agent_explorer_64.png"),
                os.path.join(project_root, "vmt_sprites_pack_2", "agent_farmer_64.png"),
                os.path.join(project_root, "vmt_sprites_pack_2", "agent_miner_64.png"),
                os.path.join(project_root, "vmt_sprites_pack_2", "agent_trader_64.png"),
            ]

            for i, sprite_path in enumerate(agent_sprite_files):
                # Load sprite without conversion to avoid "No video mode has been set" error
                sprite = pygame.image.load(sprite_path)
                # Store original sprite - will be scaled dynamically during rendering
                self._sprites[f"agent_{i}"] = sprite

            # Load resource sprites - map V2 simulation resource types to sprite files
            resource_mapping = {
                "A": os.path.join(
                    project_root, "vmt_sprites_pack_1", "resource_food_64.png"
                ),  # Map A to food sprite (good1)
                "B": os.path.join(
                    project_root, "vmt_sprites_pack_1", "resource_stone_64.png"
                ),  # Map B to stone sprite (good2)
            }

            for resource_type, sprite_path in resource_mapping.items():
                # Load sprite without conversion to avoid "No video mode has been set" error
                sprite = pygame.image.load(sprite_path)
                # Store original sprite - will be scaled dynamically during rendering
                self._sprites[f"resource_{resource_type}"] = sprite

            # Load home sprite
            home_sprite_path = os.path.join(project_root, "vmt_sprites_pack_1", "home_64.png")
            # Load sprite without conversion to avoid "No video mode has been set" error
            home_sprite = pygame.image.load(home_sprite_path)
            # Store original sprite - will be scaled dynamically during rendering
            self._sprites["home"] = home_sprite

        except Exception as e:
            # DEBUG: Sprite loading errors (commented out for production)
            # print(f"Warning: Error loading sprites: {e}")
            raise e

    def _assign_agent_sprites(self, agent_count: int) -> None:
        """Assign sprites to agents based on their IDs."""
        for agent_id in range(agent_count):
            sprite_index = agent_id % len(
                [k for k in self._sprites.keys() if k.startswith("agent_")]
            )
            self._agent_sprite_map[agent_id] = f"agent_{sprite_index}"

    def _render_frame(self) -> None:
        """Render one frame of the simulation."""
        if getattr(self, "_closed", False):
            return
        surf = getattr(self, "_surface", None)
        if surf is None:
            return
        try:
            import pygame as _pg_guard2

            if not _pg_guard2.get_init():
                return
        except Exception:
            return

        # Optional fast headless bypass for CI stress
        import os as _os_fast

        if _os_fast.environ.get("ECONSIM_HEADLESS_RENDER") == "1":
            return

        # DEBUG: Track render frame calls (commented out for production)
        # if self._frame % 60 == 0:  # Print every 60 frames (about once per second at 60 FPS)
        #     print(f"🎮 DEBUG: _render_frame() called - frame {self._frame}")
        #     if self.live_simulation:
        #         print(f"🎮 DEBUG: Live simulation available with {len(self.live_simulation.agents)} agents")
        #         # Check if agent positions are changing
        #         if len(self.live_simulation.agents) > 0:
        #             agent = self.live_simulation.agents[0]
        #             print(f"🎮 DEBUG: Agent 0 position: ({agent.x}, {agent.y}), target: {getattr(agent, 'target', None)}")
        #     else:
        #         print("🎮 DEBUG: No live simulation available")

        # Clear background to a lighter, more neutral color
        surf.fill((45, 45, 50))

        # Render live simulation state
        if self.live_simulation:
            try:
                self._render_live_simulation(surf)
            except Exception:
                # DEBUG: Rendering errors (commented out for production)
                # print(f"Warning: Error rendering live simulation: {e}")
                pass

        self._frame += 1

        # Force widget to repaint
        self.update()

    def _render_live_simulation(self, surf: pygame.Surface) -> None:
        """Render the current state of the live V2 simulation."""
        if not self.live_simulation:
            # DEBUG: No simulation warning (commented out for production)
            # print("🎮 DEBUG: No live simulation to render")
            return

        # DEBUG: Track what we're rendering (commented out for production)
        # if self._frame % 60 == 0:  # Print every 60 frames
        #     print(f"🎮 DEBUG: _render_live_simulation() called - rendering {len(self.live_simulation.agents)} agents")

        # Get grid dimensions
        grid_width = self.live_simulation.grid.width
        grid_height = self.live_simulation.grid.height

        # Determine cell size to fit grid in surface with proper centering
        w, h = self.SURFACE_SIZE

        # Calculate cell size to fit grid while maintaining aspect ratio
        cell_w = w // grid_width
        cell_h = h // grid_height
        cell_size = min(cell_w, cell_h)

        # Ensure minimum cell size for visibility
        cell_size = max(8, cell_size)

        # Calculate total grid size with the chosen cell size
        grid_pixel_width = grid_width * cell_size
        grid_pixel_height = grid_height * cell_size

        # Calculate centering offsets
        offset_x = (w - grid_pixel_width) // 2
        offset_y = (h - grid_pixel_height) // 2

        # Draw grid background
        self._draw_grid_background(surf, grid_width, grid_height, cell_size, offset_x, offset_y)

        # Assign sprites to agents if needed
        self._assign_agent_sprites(len(self.live_simulation.agents))

        # Draw resources using the correct grid interface
        for x, y, resource_type in self.live_simulation.grid.iter_resources():
            sprite_key = f"resource_{resource_type}"
            original_sprite = self._sprites.get(sprite_key)
            if original_sprite:
                # Scale sprite to fill 80% of the cell
                sprite_size = int(cell_size * 0.8)
                sprite = pygame.transform.scale(original_sprite, (sprite_size, sprite_size))
                # Center sprite within the cell
                sprite_x = offset_x + x * cell_size + (cell_size - sprite_size) // 2
                sprite_y = offset_y + y * cell_size + (cell_size - sprite_size) // 2
                surf.blit(sprite, (sprite_x, sprite_y))

        # Draw homes (agent starting positions)
        for agent in self.live_simulation.agents:
            if hasattr(agent, "home_x") and hasattr(agent, "home_y"):
                original_home_sprite = self._sprites.get("home")
                if original_home_sprite:
                    # Scale home sprite to fill 90% of the cell (homes are slightly larger)
                    home_size = int(cell_size * 0.9)
                    home_sprite = pygame.transform.scale(
                        original_home_sprite, (home_size, home_size)
                    )
                    # Center home sprite within the cell
                    home_x = offset_x + agent.home_x * cell_size + (cell_size - home_size) // 2
                    home_y = offset_y + agent.home_y * cell_size + (cell_size - home_size) // 2
                    surf.blit(home_sprite, (home_x, home_y))

        # Draw agents
        for agent in self.live_simulation.agents:
            sprite_key = self._agent_sprite_map.get(agent.id, "agent_0")
            original_sprite = self._sprites.get(sprite_key)
            if original_sprite:
                # Scale agent sprite to fill 85% of the cell (agents are prominent)
                agent_size = int(cell_size * 0.85)
                sprite = pygame.transform.scale(original_sprite, (agent_size, agent_size))
                # Center agent sprite within the cell
                agent_x = offset_x + agent.x * cell_size + (cell_size - agent_size) // 2
                agent_y = offset_y + agent.y * cell_size + (cell_size - agent_size) // 2
                surf.blit(sprite, (agent_x, agent_y))

        # Draw target arrows
        self._draw_target_arrows(surf, cell_size, offset_x, offset_y)

    def _draw_grid_background(
        self,
        surf: pygame.Surface,
        grid_width: int,
        grid_height: int,
        cell_size: int,
        offset_x: int,
        offset_y: int,
    ) -> None:
        """Draw a subtle grid background to show cell boundaries."""
        # Draw grid lines
        grid_color = (80, 80, 90)  # More visible grid lines

        # Vertical lines
        for x in range(grid_width + 1):
            line_x = offset_x + x * cell_size
            pygame.draw.line(
                surf,
                grid_color,
                (line_x, offset_y),
                (line_x, offset_y + grid_height * cell_size),
                1,
            )

        # Horizontal lines
        for y in range(grid_height + 1):
            line_y = offset_y + y * cell_size
            pygame.draw.line(
                surf, grid_color, (offset_x, line_y), (offset_x + grid_width * cell_size, line_y), 1
            )

    def _draw_target_arrows(
        self, surf: pygame.Surface, cell_size: int, offset_x: int, offset_y: int
    ) -> None:
        """Draw target arrows from agents to their targets."""
        if not self.live_simulation:
            return

        for agent in self.live_simulation.agents:
            # Get agent's current target (V2 agents use 'target' property)
            target = None
            if hasattr(agent, "target") and agent.target:
                target = agent.target

            if target is None:
                continue

            # Determine if target is a resource or another agent
            is_resource = False
            target_x, target_y = None, None

            if hasattr(target, "__len__") and len(target) == 2:
                target_x, target_y = target
                # Check if there's a resource at this position
                if self.live_simulation.grid.has_resource(target_x, target_y):
                    is_resource = True

            if target_x is None or target_y is None:
                continue

            # Draw arrow with centering offsets
            start_x = offset_x + agent.x * cell_size + cell_size // 2
            start_y = offset_y + agent.y * cell_size + cell_size // 2
            end_x = offset_x + target_x * cell_size + cell_size // 2
            end_y = offset_y + target_y * cell_size + cell_size // 2

            # Choose arrow color
            arrow_color = (
                (255, 255, 0) if is_resource else (0, 200, 200)
            )  # Yellow for resources, Teal for agents

            # Draw arrow line
            pygame.draw.line(surf, arrow_color, (start_x, start_y), (end_x, end_y), 2)

            # Draw arrowhead
            self._draw_arrowhead(surf, arrow_color, (start_x, start_y), (end_x, end_y))

    def _draw_arrowhead(self, surf: pygame.Surface, color: tuple, start: tuple, end: tuple) -> None:
        """Draw an arrowhead at the end of an arrow."""
        import math

        start_x, start_y = start
        end_x, end_y = end

        # Calculate arrow direction
        dx = end_x - start_x
        dy = end_y - start_y
        length = math.sqrt(dx * dx + dy * dy)

        if length == 0:
            return

        # Normalize direction
        dx /= length
        dy /= length

        # Arrowhead size
        arrow_size = 8

        # Calculate arrowhead points
        angle = math.pi / 6  # 30 degrees
        cos_angle = math.cos(angle)
        sin_angle = math.sin(angle)

        # Left arrowhead point
        left_x = end_x - arrow_size * (dx * cos_angle + dy * sin_angle)
        left_y = end_y - arrow_size * (dy * cos_angle - dx * sin_angle)

        # Right arrowhead point
        right_x = end_x - arrow_size * (dx * cos_angle - dy * sin_angle)
        right_y = end_y - arrow_size * (dy * cos_angle + dx * sin_angle)

        # Draw arrowhead triangle
        points = [(end_x, end_y), (left_x, left_y), (right_x, right_y)]
        pygame.draw.polygon(surf, color, points)

    def update_simulation(self, simulation: Any) -> None:
        """Update the live simulation reference."""
        # DEBUG: Simulation update tracking (commented out for production)
        # print(f"🎮 DEBUG: update_simulation() called with {len(simulation.agents)} agents")
        # if len(simulation.agents) > 0:
        #     agent = simulation.agents[0]
        #     print(f"🎮 DEBUG: Agent 0 position: ({agent.x}, {agent.y}), target: {getattr(agent, 'target', None)}")
        self.live_simulation = simulation

    def paintEvent(self, event) -> None:
        """Handle paint events by rendering to Qt widget."""
        if not hasattr(self, "_surface") or self._surface is None:
            # Initialize pygame surface
            self._surface = pygame.Surface(self.SURFACE_SIZE)
            self._surface.fill((45, 45, 50))

        # Convert pygame surface to QImage
        try:
            import pygame as _pg_guard

            if _pg_guard.get_init():
                # Get pygame surface as string
                raw_data = pygame.image.tostring(self._surface, "RGBA")
                # Create QImage from raw data
                qimage = QImage(
                    raw_data,
                    self.SURFACE_SIZE[0],
                    self.SURFACE_SIZE[1],
                    QImage.Format.Format_RGBA8888,
                )

                # Paint to widget
                painter = QPainter(self)
                painter.drawImage(QRect(0, 0, self.width(), self.height()), qimage)
                painter.end()

        except Exception:
            # DEBUG: Paint event errors (commented out for production)
            # print(f"Warning: Error in paintEvent: {e}")
            pass

    def closeEvent(self, event) -> None:
        """Handle widget close event."""
        try:
            self._closed = True
            if hasattr(self, "_timer"):
                self._timer.stop()
            if hasattr(self, "_surface"):
                self._surface = None
        except Exception:
            pass
        super().closeEvent(event)
