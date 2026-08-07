# Bloom Festival Automation

Coordinate-based macOS automation for a Bloom Festival loop through Apple iPhone Mirroring.

The script focuses iPhone Mirroring, performs 3 initial navigation clicks once, then repeats:

```text
click start
click 13 calibrated locations
click ok
```

## Setup

```bash
cd /Users/tylerk0226/idle_iktah/bloom_festival
uv sync
```

Grant Accessibility permission to the app running Python if macOS asks:

```text
System Settings -> Privacy & Security -> Accessibility
```

macOS may also ask for Automation permission when the script activates iPhone Mirroring.
The Escape kill switch may also require Input Monitoring permission on some macOS setups.

## Calibrate

```bash
uv run python calibration.py
```

Use a stable square/reference button as the first captured point. For each prompt, hover the requested target and press Enter.

Calibration captures:

- 3 one-time initial navigation clicks
- start button
- 13 action click locations
- ok button

The script saves local calibration to `config.json`, which is ignored by Git.

## Run

Run one repeat cycle after the initial navigation:

```bash
uv run python main.py --cycles 1
```

Run more cycles:

```bash
uv run python main.py --cycles 5
```

Run without the 3 initial navigation clicks:

```bash
uv run python main.py --skip-initial --cycles 5
```

Emergency stop: move the mouse to the top-left corner of the screen.

Escape stop: press `Esc` to stop between clicks or during waits.

## Re-anchor

If iPhone Mirroring moved but did not resize:

```bash
uv run python main.py --reanchor --cycles 1
```

Hover over the same reference button used during calibration and press Enter.

Re-anchor without running:

```bash
uv run python main.py --reanchor --print-config
```

## Reset Calibration

```bash
uv run python calibration.py --reset
```

## Useful Checks

Print config:

```bash
uv run python main.py --print-config
```

Test focus without clicking:

```bash
uv run python main.py --focus-only
```

Test one calibrated click:

```bash
uv run python main.py --test-click start
```

Available test click names include `initial_1`, `initial_2`, `initial_3`, `start`, `action_01` through `action_13`, and `ok`.

## Timing

Timing lives in local `config.json`:

- `startup_delay_seconds`: countdown before activating iPhone Mirroring
- `focus_settle_delay_seconds`: wait after activating iPhone Mirroring
- `mouse_move_seconds`: how long the cursor takes to move to each click
- `pre_click_delay_seconds`: tiny pause after moving before pressing
- `click_hold_seconds`: how long the mouse button stays down
- `transition_delay_seconds`: wait between clicks
- `cycle_buffer_seconds`: wait after clicking ok
