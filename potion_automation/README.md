# Idle Iktah Potion Automation

Small macOS automation script for the Idle Iktah potion loop through Apple iPhone Mirroring.

The script uses calibrated mouse coordinates, fixed waits, and PyAutoGUI. It tries to focus iPhone Mirroring automatically before clicking, selects the cheap potion before cycle 1, then runs the potion loop.

## What It Does

Each cycle:

```text
select cheap potion at startup
long-press Play
click 39
wait for cheap batch
click Swap
click Haste Tea
long-press Play
click 1
wait for Haste Tea
click Swap
click cheap potion
```

The automation needs control of your real mouse while running.

## Requirements

- macOS
- Apple iPhone Mirroring
- Python 3.11+
- `uv`

macOS permissions may be required for the app running Python, such as Terminal, iTerm, VS Code, or Python:

```text
System Settings -> Privacy & Security -> Accessibility
```

macOS may also ask for Automation permission when the script activates iPhone Mirroring.
The Escape kill switch may also require Input Monitoring permission on some macOS setups.

## Setup

```bash
cd /Users/tylerk0226/idle_iktah/potion_automation
uv sync
```

This creates `.venv` and installs dependencies from `pyproject.toml` / `uv.lock`.

## Calibrate From Scratch

```bash
uv run python calibration.py
```

Calibration saves local coordinates to `config.json`. That file is ignored by Git because it is specific to your screen/window.

During calibration:

- Do not click target buttons unless the script tells you to manually open a popup.
- Hover over each requested point and press Enter.
- Use the same stable square/reference button as the first point every time.
- For `39` and `1`, manually long-press Play first so the quantity popup is visible.
- For `cheap_potion` and `haste_tea`, manually open the potion selector.

## Run One Cycle

Start from the base Alchemy screen with Play/Swap visible. The currently selected potion can be wrong; the script selects the cheap potion before cycle 1.

```bash
uv run python main.py --cycles 1
```

The script:

- waits `startup_delay_seconds`
- activates iPhone Mirroring
- waits `focus_settle_delay_seconds` after activation
- selects the cheap potion
- runs one complete cycle

Emergency stop: move the mouse to the top-left corner of the screen.

Escape stop: press `Esc` to stop between clicks or during waits.

## Run Multiple Cycles

```bash
uv run python main.py --cycles 5
```

Use small runs first. After one cycle works, try 3 or 5 before larger counts.

Run until stopped:

```bash
uv run python main.py --infinite
```

## Re-anchor After Moving The Window

If iPhone Mirroring moved but did not resize:

```bash
uv run python main.py --reanchor --cycles 1
```

Hover over the same reference button used during calibration and press Enter. The script updates only the anchor point; all saved relative offsets stay the same.

Re-anchor without running a cycle:

```bash
uv run python main.py --reanchor --print-config
```

## Reset Calibration

```bash
uv run python calibration.py --reset
```

This resets `config.json` to placeholder coordinates. Run full calibration again afterward.

## Useful Checks

Print current config:

```bash
uv run python main.py --print-config
```

Test calibrated Play long-press only:

```bash
uv run python main.py --test-long-press play --long-press-seconds 1.2
```

Test current cursor click, ignoring calibration:

```bash
uv run python main.py --test-current-click
```

Test current cursor long-press, ignoring calibration:

```bash
uv run python main.py --test-current-long-press --long-press-seconds 1.6
```

## Timing Knobs

Timing lives in local `config.json`:

- `startup_delay_seconds`: countdown before activating iPhone Mirroring
- `focus_settle_delay_seconds`: wait after activating iPhone Mirroring before the first click
- `mouse_move_seconds`: how long the cursor takes to move to normal clicks
- `pre_click_delay_seconds`: tiny pause after moving before a normal click
- `click_hold_seconds`: how long a normal click stays held down
- `long_click_mouse_move_seconds`: cursor move time before long-pressing Play
- `long_click_pre_hold_delay_seconds`: pause after moving before holding Play
- `long_press_seconds`: hold duration for Play
- `transition_delay_seconds`: small delay between UI changes
- `cheap_potion_wait_seconds`: fixed wait after selecting 39
- `haste_tea_wait_seconds`: fixed wait after selecting 1
- `cycle_buffer_seconds`: wait between completed cycles

## Auto-Focus

By default, the script runs AppleScript to activate:

```text
iPhone Mirroring
```

It uses `open -a` plus macOS System Events, then logs the frontmost app. If the log does not say `Frontmost app is now: iPhone Mirroring`, macOS did not switch focus.

Test focus without clicking:

```bash
uv run python main.py --focus-only
```

Disable this:

```bash
uv run python main.py --no-auto-focus --cycles 1
```

Override the app name:

```bash
uv run python main.py --focus-app "iPhone Mirroring" --cycles 1
```
