# Debug Recording Architecture - Patch V1: Full Playback Support

**Date:** October 7, 2025\
**Status:** Proposed Revision\
**Parent Document:** [DEBUG_RECORDING_ARCHITECTURE.md](DEBUG_RECORDING_ARCHITECTURE.md)

______________________________________________________________________

## Executive Summary

**Problem Identified:** The current architecture focuses exclusively on **debug logs** (decision
records, trade records) but lacks support for **full simulation playback** equivalent to
`realtime_pygame_v2.py` visual rendering.

**Core Gap:** Users cannot visually replay a recorded simulation in the GUI to observe agent
movements, resource depletion, and spatial patterns over time—they can only query decision data.

**Proposed Solution:** Extend the recording system with a **dual-output model**:

1. **Debug Database (`.vmtrec`)** - SQLite-based decision logs (existing design)
2. **Playback Stream (`.vmtplay`)** - Frame-by-frame state snapshots for visual replay

This patch outlines the architectural changes needed to support both use cases without compromising
the pure observer pattern.

______________________________________________________________________

## Table of Contents

1. [Core Requirements](#1-core-requirements)
2. [Architectural Changes](#2-architectural-changes)
3. [Data Schema Extensions](#3-data-schema-extensions)
4. [Recording Modes](#4-recording-modes)
5. [Playback System Design](#5-playback-system-design)
6. [Implementation Changes](#6-implementation-changes)
7. [Performance Impact](#7-performance-impact)
8. [Migration Path](#8-migration-path)

______________________________________________________________________

## 1. Core Requirements

### What Full Playback Needs

To replicate `realtime_pygame_v2.py` visual rendering in a replay, we need:

1. **Complete World State Per Step:**

   - All agent positions (x, y)
   - All agent inventories (carrying + home)
   - All agent partnerships (if applicable)
   - All resource positions and remaining quantities
   - Grid state (if dynamic elements exist)

2. **Visual Rendering Capability:**

   - Same sprite-based rendering as live simulation
   - Timeline scrubber (jump to any step instantly)
   - Play/pause/step-forward/step-backward controls
   - Speed control (1x, 2x, 5x, 10x)

3. **Educational Use Cases:**

   - Students can watch recorded runs to understand agent behavior
   - Teachers can create "reference runs" showing ideal economic outcomes
   - Developers can visually debug spatial issues (agents stuck, resource starvation)

4. **Compatibility with Debug Logs:**

   - When playback paused at step N, can inspect agent decisions from `.vmtrec`
   - Click agent → see "why did this agent move here?" decision log
   - Unified viewer: visual playback + decision inspector

### What Debug Logs Need (Unchanged)

- Fast queries for agent decision history
- Trade network analysis
- Utility progression plots
- Automated freeze detection
- No requirement for complete state snapshots every step (too expensive)

______________________________________________________________________

## 2. Architectural Changes

### 2.1 Dual Recording Modes

**Current Design (Debug Only):**

```
SimulationObserver
    ↓
DebugRecorder (SQLite .vmtrec)
    ↓ Writes
Decisions + Trades (sparse, query-optimized)
```

**Revised Design (Dual Output):**

```
SimulationObserver
    ├─→ DebugRecorder (SQLite .vmtrec) [OPTIONAL]
    │       ↓ Writes
    │   Decisions + Trades + Metadata
    │
    └─→ PlaybackRecorder (.vmtplay) [OPTIONAL]
            ↓ Writes
        Complete World State Every Step
```

**Key Insight:** These are **independent** recording streams controlled by separate flags:

```bash
# Both enabled (default for debugging)
ECONSIM_DEBUG_RECORDING=1 ECONSIM_PLAYBACK_RECORDING=1 make visualtest

# Only playback (for creating educational videos)
ECONSIM_DEBUG_RECORDING=0 ECONSIM_PLAYBACK_RECORDING=1 make visualtest

# Only debug logs (for performance analysis)
ECONSIM_DEBUG_RECORDING=1 ECONSIM_PLAYBACK_RECORDING=0 make perf

# Neither (fastest execution)
ECONSIM_DEBUG_RECORDING=0 ECONSIM_PLAYBACK_RECORDING=0 make visualtest
```

### 2.2 Observer Refactoring

**Current `SimulationObserver` (Simplified):**

```python
class SimulationObserver(SimulationCoordinator):
    def __init__(self, coordinator: SimulationCoordinator, recorder: DebugRecorder):
        self._coordinator = coordinator
        self._recorder = recorder
        self._wrap_step_method()
```

**Revised `SimulationObserver` (Multi-Recorder):**

```python
class SimulationObserver(SimulationCoordinator):
    def __init__(self, 
                 coordinator: SimulationCoordinator, 
                 debug_recorder: Optional[DebugRecorder] = None,
                 playback_recorder: Optional[PlaybackRecorder] = None):
        self._coordinator = coordinator
        self._debug_recorder = debug_recorder
        self._playback_recorder = playback_recorder
        self._wrap_step_method()
    
    def _on_step_end(self, step: int):
        """Capture data for both recorders if enabled."""
        # Debug recording (sparse, decision-focused)
        if self._debug_recorder:
            for agent in self._coordinator.executor.agents:
                decision = self._extract_decision_record(agent, step)
                self._debug_recorder.record_decision(step, decision)
        
        # Playback recording (complete state, every step)
        if self._playback_recorder:
            snapshot = self._capture_full_world_state(step)
            self._playback_recorder.record_frame(step, snapshot)
```

### 2.3 Auto-Enable Function Update

**Current Signature:**

```python
def auto_enable_recording(coordinator: SimulationCoordinator) -> SimulationCoordinator:
    # Only creates DebugRecorder
```

**Revised Signature:**

```python
def auto_enable_recording(
    coordinator: SimulationCoordinator,
    enable_debug: Optional[bool] = None,
    enable_playback: Optional[bool] = None
) -> SimulationCoordinator:
    """
    Wrap coordinator with recording capabilities.
    
    Args:
        coordinator: Unwrapped coordinator
        enable_debug: Override for ECONSIM_DEBUG_RECORDING env var
        enable_playback: Override for ECONSIM_PLAYBACK_RECORDING env var
    
    Returns:
        Original coordinator (if both disabled) or SimulationObserver
    """
    features = SimulationFeatures.from_environment()
    
    # Read environment or use overrides
    debug_enabled = enable_debug if enable_debug is not None else features.debug_recording_enabled
    playback_enabled = enable_playback if enable_playback is not None else features.playback_recording_enabled
    
    # If neither enabled, return unwrapped
    if not debug_enabled and not playback_enabled:
        return coordinator
    
    # Create recorders based on flags
    debug_recorder = None
    playback_recorder = None
    
    if debug_enabled:
        debug_path = generate_recording_filename(coordinator, suffix=".vmtrec")
        debug_recorder = DebugRecorder(debug_path, level=features.debug_recording_level)
        print(f"Debug recording enabled: {debug_path}")
    
    if playback_enabled:
        playback_path = generate_recording_filename(coordinator, suffix=".vmtplay")
        playback_recorder = PlaybackRecorder(playback_path)
        print(f"Playback recording enabled: {playback_path}")
    
    # Wrap coordinator with both recorders
    observer = SimulationObserver(coordinator, debug_recorder, playback_recorder)
    return observer
```

______________________________________________________________________

## 3. Data Schema Extensions

### 3.1 Playback File Format (`.vmtplay`)

**Technology Choice:** **MessagePack-based binary format** (not SQLite)

**Rationale:**

- SQLite is optimized for queries, not sequential frame streaming
- Playback needs fast sequential read (step 0 → step 1000)
- MessagePack provides compact binary serialization (~60% smaller than JSON)
- Simpler to implement frame seeking (fixed-size frames or frame index)

**File Structure:**

```
┌─────────────────────────────────────────────────┐
│ HEADER (MessagePack)                            │
│ - version: "1.0"                                │
│ - seed: 12345                                   │
│ - scenario_name: "HDL"                          │
│ - grid_width: 50                                │
│ - grid_height: 50                               │
│ - total_steps: 1000                             │
│ - frame_index_offset: 12345 (byte position)    │
├─────────────────────────────────────────────────┤
│ FRAME 0 (MessagePack)                           │
│ - step: 0                                       │
│ - agents: [...]                                 │
│ - resources: [...]                              │
├─────────────────────────────────────────────────┤
│ FRAME 1 (MessagePack)                           │
├─────────────────────────────────────────────────┤
│ ...                                             │
├─────────────────────────────────────────────────┤
│ FRAME 999 (MessagePack)                         │
├─────────────────────────────────────────────────┤
│ FRAME INDEX (MessagePack)                       │
│ - [step_0_offset, step_1_offset, ..., step_999]│
└─────────────────────────────────────────────────┘
```

**Frame Schema:**

```python
@dataclass
class PlaybackFrame:
    step: int
    agents: List[PlaybackAgentState]
    resources: List[PlaybackResourceState]

@dataclass
class PlaybackAgentState:
    id: int
    x: int
    y: int
    carrying_inventory: Dict[str, int]
    home_inventory: Dict[str, int]
    home_x: int
    home_y: int
    partner_id: Optional[int]
    utility: float  # For overlay display
    utility_function_type: str  # For sprite selection (if needed)

@dataclass
class PlaybackResourceState:
    x: int
    y: int
    resource_type: str
    remaining_quantity: int
```

### 3.2 Frame Index for Fast Seeking

**Problem:** Reading frames sequentially from step 0 to step 500 is slow for large simulations.

**Solution:** Write a frame index at end of file with byte offsets:

```python
# After recording all frames, write index
frame_index = [frame_0_offset, frame_1_offset, ..., frame_N_offset]
index_offset = file.tell()
file.write(msgpack.packb(frame_index))

# Write index location in header
file.seek(HEADER_FRAME_INDEX_OFFSET_POSITION)
file.write(msgpack.packb(index_offset))
```

**Playback Seeking:**

```python
class PlaybackReader:
    def seek_to_step(self, step: int) -> PlaybackFrame:
        """Jump directly to a step without reading all frames."""
        frame_offset = self.frame_index[step]
        self.file.seek(frame_offset)
        frame_data = self.file.read(FRAME_SIZE)  # Or read until next frame
        return msgpack.unpackb(frame_data, raw=False)
```

______________________________________________________________________

## 4. Recording Modes

### 4.1 Configuration Matrix

| Debug | Playback | Use Case             | Files Generated        | Overhead |
| ----- | -------- | -------------------- | ---------------------- | -------- |
| ❌    | ❌       | Production runs      | None                   | 0%       |
| ✅    | ❌       | Performance analysis | `.vmtrec`              | \<15%    |
| ❌    | ✅       | Educational videos   | `.vmtplay`             | \<25%    |
| ✅    | ✅       | Full debugging       | `.vmtrec` + `.vmtplay` | \<35%    |

**Default Modes by Context:**

```python
# tests/conftest.py - Only debug logs (tests don't need playback)
ECONSIM_DEBUG_RECORDING=1 ECONSIM_PLAYBACK_RECORDING=0

# visual_test_simple.py - Both enabled (visual test benefits from playback)
ECONSIM_DEBUG_RECORDING=1 ECONSIM_PLAYBACK_RECORDING=1

# gui/launcher/ - Both enabled (educational context)
ECONSIM_DEBUG_RECORDING=1 ECONSIM_PLAYBACK_RECORDING=1

# make perf - Only debug logs (measure overhead of debug recording)
ECONSIM_DEBUG_RECORDING=1 ECONSIM_PLAYBACK_RECORDING=0
```

### 4.2 Environment Variables

**New Variables:**

```bash
# Playback recording control
ECONSIM_PLAYBACK_RECORDING=1        # Enable playback recording (default: 0 in tests, 1 in GUI)
ECONSIM_PLAYBACK_RECORDING_DIR=./sim_runs  # Output directory
ECONSIM_PLAYBACK_COMPRESSION=1      # Use zlib compression on frames (default: 1)
```

**Existing Variables (Unchanged):**

```bash
ECONSIM_DEBUG_RECORDING=1           # Enable debug recording
ECONSIM_DEBUG_RECORDING_LEVEL=ECONOMIC  # Detail level
ECONSIM_DEBUG_RECORDING_DIR=./sim_runs
```

______________________________________________________________________

## 5. Playback System Design

### 5.1 PlaybackRecorder Class

```python
class PlaybackRecorder:
    """Records complete world state for visual playback."""
    
    def __init__(self, filepath: str, compression: bool = True):
        self.filepath = filepath
        self.compression = compression
        self.file = open(filepath, 'wb')
        self.frame_offsets = []
        self.step_count = 0
        
        # Write placeholder header (update at close)
        self._write_header_placeholder()
    
    def record_metadata(self, config: dict):
        """Store simulation configuration in header."""
        self.metadata = config
    
    def record_frame(self, step: int, frame: PlaybackFrame):
        """Write a single frame to file."""
        frame_offset = self.file.tell()
        self.frame_offsets.append(frame_offset)
        
        # Serialize frame
        frame_data = msgpack.packb(asdict(frame))
        
        # Optional compression
        if self.compression:
            frame_data = zlib.compress(frame_data)
        
        # Write frame length + data (for variable-length frames)
        self.file.write(struct.pack('<I', len(frame_data)))
        self.file.write(frame_data)
        
        self.step_count += 1
    
    def close(self):
        """Finalize recording with frame index and header."""
        # Write frame index at end
        index_offset = self.file.tell()
        index_data = msgpack.packb(self.frame_offsets)
        self.file.write(index_data)
        
        # Update header with index location
        self.file.seek(0)
        header = {
            'version': '1.0',
            'metadata': self.metadata,
            'total_steps': self.step_count,
            'frame_index_offset': index_offset,
            'compression': self.compression
        }
        header_data = msgpack.packb(header)
        self.file.write(struct.pack('<I', len(header_data)))
        self.file.write(header_data)
        
        self.file.close()
```

### 5.2 PlaybackReader Class

```python
class PlaybackReader:
    """Read playback files for visual replay."""
    
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.file = open(filepath, 'rb')
        self._load_header()
        self._load_frame_index()
    
    def _load_header(self):
        """Read header from file."""
        header_len = struct.unpack('<I', self.file.read(4))[0]
        header_data = self.file.read(header_len)
        self.header = msgpack.unpackb(header_data, raw=False)
        self.compression = self.header.get('compression', False)
    
    def _load_frame_index(self):
        """Read frame index from end of file."""
        index_offset = self.header['frame_index_offset']
        self.file.seek(index_offset)
        index_data = self.file.read()
        self.frame_index = msgpack.unpackb(index_data, raw=False)
    
    def get_frame(self, step: int) -> PlaybackFrame:
        """Read a specific frame by step number."""
        if step >= len(self.frame_index):
            raise ValueError(f"Step {step} out of range (max: {len(self.frame_index)-1})")
        
        # Seek to frame
        frame_offset = self.frame_index[step]
        self.file.seek(frame_offset)
        
        # Read frame length and data
        frame_len = struct.unpack('<I', self.file.read(4))[0]
        frame_data = self.file.read(frame_len)
        
        # Decompress if needed
        if self.compression:
            frame_data = zlib.decompress(frame_data)
        
        # Deserialize
        frame_dict = msgpack.unpackb(frame_data, raw=False)
        return PlaybackFrame(**frame_dict)
    
    def __len__(self):
        """Total number of frames."""
        return len(self.frame_index)
    
    def close(self):
        self.file.close()
```

### 5.3 Playback GUI Integration

**New Module:** `src/econsim/gui/playback_viewer.py`

```python
class PlaybackViewer:
    """
    Visual playback of recorded simulations.
    
    Similar to realtime_pygame_v2.py but reads from .vmtplay file.
    """
    
    def __init__(self, playback_file: str, debug_file: Optional[str] = None):
        self.reader = PlaybackReader(playback_file)
        self.debug_recording = None
        
        # Load debug recording if available
        if debug_file and Path(debug_file).exists():
            self.debug_recording = SimulationRecording.load(debug_file)
        
        self.current_step = 0
        self.playing = False
        self.playback_speed = 1.0  # 1x speed
        
        self._init_pygame()
    
    def _init_pygame(self):
        """Initialize pygame similar to realtime_pygame_v2.py"""
        pygame.init()
        self.screen = pygame.display.set_mode((800, 800))
        pygame.display.set_caption("VMT Simulation Playback")
        self.clock = pygame.time.Clock()
        
        # Load sprites (same as visual_test_simple.py)
        self.sprites = load_sprites()
    
    def run(self):
        """Main playback loop."""
        running = True
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                # Keyboard controls
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.playing = not self.playing
                    elif event.key == pygame.K_RIGHT:
                        self.step_forward()
                    elif event.key == pygame.K_LEFT:
                        self.step_backward()
                    elif event.key == pygame.K_UP:
                        self.playback_speed = min(10.0, self.playback_speed * 2)
                    elif event.key == pygame.K_DOWN:
                        self.playback_speed = max(0.1, self.playback_speed / 2)
                
                # Mouse click on agent (show decision inspector)
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self._handle_agent_click(event.pos)
            
            # Auto-advance if playing
            if self.playing:
                self.step_forward()
            
            # Render current frame
            self._render_frame()
            
            # Control playback speed
            self.clock.tick(30 * self.playback_speed)
        
        self.reader.close()
        pygame.quit()
    
    def _render_frame(self):
        """Render the current frame."""
        frame = self.reader.get_frame(self.current_step)
        
        self.screen.fill((255, 255, 255))
        
        # Draw resources
        for resource in frame.resources:
            sprite = self.sprites[f"resource_{resource.resource_type}"]
            self.screen.blit(sprite, (resource.x * TILE_SIZE, resource.y * TILE_SIZE))
        
        # Draw agents
        for agent in frame.agents:
            sprite = self.sprites["agent_default"]
            self.screen.blit(sprite, (agent.x * TILE_SIZE, agent.y * TILE_SIZE))
        
        # Draw UI overlay
        self._draw_ui_overlay()
        
        pygame.display.flip()
    
    def _draw_ui_overlay(self):
        """Draw playback controls and info."""
        font = pygame.font.Font(None, 24)
        
        # Step counter
        step_text = font.render(f"Step: {self.current_step}/{len(self.reader)}", True, (0, 0, 0))
        self.screen.blit(step_text, (10, 10))
        
        # Play/Pause indicator
        status = "Playing" if self.playing else "Paused"
        status_text = font.render(status, True, (0, 0, 0))
        self.screen.blit(status_text, (10, 40))
        
        # Speed indicator
        speed_text = font.render(f"Speed: {self.playback_speed}x", True, (0, 0, 0))
        self.screen.blit(speed_text, (10, 70))
    
    def _handle_agent_click(self, mouse_pos: Tuple[int, int]):
        """Show decision inspector when agent is clicked."""
        if not self.debug_recording:
            return
        
        # Convert mouse position to grid coordinates
        grid_x, grid_y = mouse_pos[0] // TILE_SIZE, mouse_pos[1] // TILE_SIZE
        
        # Find agent at this position
        frame = self.reader.get_frame(self.current_step)
        clicked_agent = None
        for agent in frame.agents:
            if agent.x == grid_x and agent.y == grid_y:
                clicked_agent = agent
                break
        
        if clicked_agent:
            # Query decision from debug recording
            decisions = self.debug_recording.decisions_at_step(self.current_step)
            agent_decision = next((d for d in decisions if d.agent_id == clicked_agent.id), None)
            
            if agent_decision:
                self._show_decision_popup(clicked_agent, agent_decision)
    
    def step_forward(self):
        """Advance one step."""
        self.current_step = min(len(self.reader) - 1, self.current_step + 1)
    
    def step_backward(self):
        """Go back one step."""
        self.current_step = max(0, self.current_step - 1)
```

**Launch Command:**

```bash
# Play back a recording
vmt-playback sim_runs/251007_14-23-45-HDL-11111.vmtplay

# Play back with debug inspection
vmt-playback sim_runs/251007_14-23-45-HDL-11111.vmtplay \
             --debug sim_runs/251007_14-23-45-HDL-11111.vmtrec
```

______________________________________________________________________

## 6. Implementation Changes

### 6.1 Modified Files

**Core Recording System:**

- `src/econsim/simulation/debug/observer.py` - Add `PlaybackRecorder` support
- `src/econsim/simulation/debug/auto_enable.py` - Dual-recorder logic
- `src/econsim/simulation/debug/__init__.py` - Export playback classes

**New Files:**

- `src/econsim/simulation/debug/playback_recorder.py` - `PlaybackRecorder` class
- `src/econsim/simulation/debug/playback_reader.py` - `PlaybackReader` class
- `src/econsim/simulation/debug/playback_schema.py` - `PlaybackFrame`, `PlaybackAgentState`, etc.
- `src/econsim/gui/playback_viewer.py` - Visual playback GUI

**Configuration:**

- `src/econsim/simulation/features.py` - Add playback recording flags

**Infrastructure:**

- `visual_test_simple.py` - Enable both recorders by default
- `tests/conftest.py` - Enable debug only (not playback in tests)
- `gui/launcher/scenario_runner.py` - Enable both recorders

**Entry Points:**

- `src/econsim/main.py` - Add `vmt-playback` command

### 6.2 SimulationFeatures Extensions

```python
@dataclass
class SimulationFeatures:
    # Existing fields
    debug_recording_enabled: bool
    debug_recording_level: RecordingLevel
    debug_recording_dir: str
    
    # NEW: Playback recording fields
    playback_recording_enabled: bool
    playback_recording_dir: str
    playback_compression: bool
    
    @classmethod
    def from_environment(cls) -> "SimulationFeatures":
        """Load configuration from environment variables."""
        return cls(
            # Existing
            debug_recording_enabled=bool(int(os.getenv("ECONSIM_DEBUG_RECORDING", "1"))),
            debug_recording_level=RecordingLevel[os.getenv("ECONSIM_DEBUG_RECORDING_LEVEL", "ECONOMIC")],
            debug_recording_dir=os.getenv("ECONSIM_DEBUG_RECORDING_DIR", "./sim_runs"),
            
            # NEW
            playback_recording_enabled=bool(int(os.getenv("ECONSIM_PLAYBACK_RECORDING", "0"))),
            playback_recording_dir=os.getenv("ECONSIM_PLAYBACK_RECORDING_DIR", "./sim_runs"),
            playback_compression=bool(int(os.getenv("ECONSIM_PLAYBACK_COMPRESSION", "1"))),
        )
```

### 6.3 Entry Point Addition

**In `src/econsim/main.py`:**

```python
def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest='command')
    
    # Existing commands
    run_parser = subparsers.add_parser('run')
    # ... existing run command setup
    
    # NEW: Playback command
    playback_parser = subparsers.add_parser('playback', help='Play back a recorded simulation')
    playback_parser.add_argument('playback_file', help='Path to .vmtplay file')
    playback_parser.add_argument('--debug', help='Path to .vmtrec file (optional)')
    
    args = parser.parse_args()
    
    if args.command == 'playback':
        from econsim.gui.playback_viewer import PlaybackViewer
        viewer = PlaybackViewer(args.playback_file, args.debug)
        viewer.run()
    elif args.command == 'run':
        # ... existing run logic
```

**Makefile Addition:**

```makefile
# Play back last recording
playback:
 @LATEST=$$(ls -t sim_runs/*.vmtplay 2>/dev/null | head -n1); \
 if [ -z "$$LATEST" ]; then \
  echo "No playback files found in sim_runs/"; \
  exit 1; \
 fi; \
 DEBUG_FILE=$${LATEST%.vmtplay}.vmtrec; \
 if [ -f "$$DEBUG_FILE" ]; then \
  vmt-playback "$$LATEST" --debug "$$DEBUG_FILE"; \
 else \
  vmt-playback "$$LATEST"; \
 fi
```

______________________________________________________________________

## 7. Performance Impact

### 7.1 Recording Overhead Estimates

**Frame Size Calculation (100 agents, 50x50 grid, 100 resources):**

```python
# Per-agent state
agent_size = (
    4 +  # id (int32)
    8 +  # x, y (2 × int32)
    50 + # carrying_inventory (5 goods × 10 bytes avg)
    50 + # home_inventory
    8 +  # home_x, home_y
    4 +  # partner_id (optional)
    8 +  # utility (float64)
    20   # utility_function_type (string)
) = ~152 bytes/agent

# Per-resource state
resource_size = (
    8 +  # x, y
    20 + # resource_type (string)
    4    # remaining_quantity
) = ~32 bytes/resource

# Total frame size
frame_size = (100 agents × 152) + (100 resources × 32) = ~18.4 KB/frame

# 1000-step simulation
total_size = 18.4 KB × 1000 = ~18.4 MB (uncompressed)

# With zlib compression (typical 60% reduction)
compressed_size = 18.4 MB × 0.4 = ~7.4 MB
```

**Overhead Comparison:**

| Mode          | File Size (1000 steps) | Write Time Overhead | Memory Usage |
| ------------- | ---------------------- | ------------------- | ------------ |
| Debug only    | 1-5 MB                 | \<15%               | ~10 MB       |
| Playback only | 7-20 MB                | \<25%               | ~20 MB       |
| Both          | 8-25 MB                | \<35%               | ~30 MB       |

### 7.2 Optimization Strategies

**1. Frame Delta Compression**

Instead of storing complete state every frame, store deltas:

```python
# Frame 0: Full state
# Frame 1: Only changed agents/resources
# Frame 2: Only changed agents/resources
# ...
# Frame 100: Full state (keyframe)
```

**Impact:** 50-70% size reduction, ~10% write overhead reduction

**2. Lazy Agent State**

Don't serialize inventory if it hasn't changed:

```python
@dataclass
class PlaybackAgentState:
    id: int
    x: int
    y: int
    carrying_inventory: Optional[Dict[str, int]] = None  # None = unchanged
    home_inventory: Optional[Dict[str, int]] = None
```

**3. Async Writing**

Write frames to disk in background thread:

```python
class PlaybackRecorder:
    def record_frame(self, step: int, frame: PlaybackFrame):
        """Queue frame for async write."""
        self.write_queue.put((step, frame))
        # Background thread handles disk I/O
```

**Impact:** Eliminates write overhead from simulation thread (0% overhead during simulation)

______________________________________________________________________

## 8. Migration Path

### Phase 1: Core Playback Infrastructure (Week 1-2)

- [ ] Implement `PlaybackRecorder` class
- [ ] Implement `PlaybackReader` class
- [ ] Define `PlaybackFrame` schema
- [ ] Add frame index system
- [ ] Unit tests for recorder/reader

### Phase 2: Observer Integration (Week 2-3)

- [ ] Refactor `SimulationObserver` for dual recorders
- [ ] Update `auto_enable_recording()` function
- [ ] Add `SimulationFeatures` playback fields
- [ ] Integration tests (record + read back)

### Phase 3: Playback GUI (Week 3-4)

- [ ] Implement `PlaybackViewer` class
- [ ] Add timeline scrubber UI
- [ ] Add play/pause/step controls
- [ ] Add speed control
- [ ] Agent click → decision inspector integration

### Phase 4: Infrastructure Updates (Week 4)

- [ ] Update `visual_test_simple.py`
- [ ] Update `tests/conftest.py`
- [ ] Update `gui/launcher/scenario_runner.py`
- [ ] Add `vmt-playback` command
- [ ] Add `make playback` target
- [ ] Documentation updates

### Phase 5: Optimization (Week 5)

- [ ] Implement delta compression
- [ ] Add async writing
- [ ] Performance benchmarking
- [ ] Memory profiling

______________________________________________________________________

## Summary

This patch extends the debug recording architecture with **full simulation playback** capability
while maintaining the pure observer pattern. Key additions:

✅ **Dual recording modes:** Debug logs (`.vmtrec`) + Playback stream (`.vmtplay`)\
✅ **Independent control:** Enable either, both, or neither via env vars\
✅ **Complete state capture:** Frame-by-frame snapshots for visual replay\
✅ **Fast seeking:** Frame index enables instant jump to any step\
✅ **Visual playback GUI:** Equivalent to `realtime_pygame_v2.py` rendering\
✅ **Debug integration:** Click agent in playback → inspect decision from `.vmtrec`\
✅ **Acceptable overhead:** \<35% with both enabled, \<25% playback-only\
✅ **Educational value:** Students can watch recorded runs for learning

**Compatibility Preserved:**

- Zero simulation code changes (pure observer pattern maintained)
- All existing debug recording features unchanged
- Optional feature (playback defaults to OFF in test contexts)

**Next Steps:** Implement Phase 1 (core playback infrastructure) and validate with visual test
scenario.
