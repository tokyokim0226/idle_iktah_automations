# Idle Iktah Potion Automation

Coordinate-based macOS automation for the Idle Iktah potion loop through Apple iPhone Mirroring.

V1 intentionally uses calibrated mouse positions and fixed waits. It does not use OCR, OpenCV, template matching, or direct game data. Startup attempts to focus iPhone Mirroring via AppleScript.

## Current Startup Behavior

Before the first cycle, the script:

1. waits `startup_delay_seconds`
2. activates iPhone Mirroring unless `--no-auto-focus` is used, using `open -a` and System Events
3. waits `focus_settle_delay_seconds` after activation
4. opens the potion selector
5. selects the cheap potion
6. starts cycle 1

This means a run can start from the base Alchemy screen as long as Play/Swap are visible. The selected potion does not need to already be the cheap potion.

Safety note: pressing `Esc` requests a clean stop between clicks or during waits. PyAutoGUI's top-left failsafe is still enabled.

## Setup With uv

```bash
cd potion_automation
uv sync
```

macOS may require Accessibility permission for the app running Python, such as Terminal, iTerm, VS Code, or Python.

## Calibration

Run:

```bash
uv run python calibration.py
```

During calibration, do not click the target buttons. Hover over the requested location and press Enter.

The first captured point is your reference anchor. Use a stable, easy-to-find square button in the mirrored UI. Button coordinates are stored relative to that anchor, so if the window moves but keeps the same size, run with `--reanchor` instead of recalibrating every button.

Calibration captures:

- `play`
- `swap`
- `make_39`
- `make_1`
- `cheap_potion`
- `haste_tea`

For `make_39` and `make_1`, manually long-press Play first so the "Make how many?" popup is visible.

For `cheap_potion` and `haste_tea`, manually close the quantity popup and open the potion selector. Cheap potion is top-left. Haste Tea is bottom-right.

## Check Config

```bash
uv run python main.py --print-config
```

Calibration is saved in `config.json`.

To reset saved coordinates:

```bash
uv run python calibration.py --reset
```

## Run One Cycle

Start on the base alchemy screen with Play/Swap visible. The script selects the cheap potion before cycle 1.

```bash
uv run python main.py --cycles 1
```

The script waits 5 seconds before clicking. Move the mouse to the top-left corner of the screen to emergency-stop.

The first click has an additional post-focus buffer controlled by `focus_settle_delay_seconds`.

## Test Long-Press Only

Start on the base screen with the Play triangle visible.

```bash
uv run python main.py --test-long-press play --long-press-seconds 1.2
```

If the quantity popup does not open, try:

```bash
uv run python main.py --test-long-press play --long-press-seconds 1.6
```

If the cursor lands in the wrong place, rerun calibration or use `--reanchor`.

To remove coordinate calibration from the test, hover over Play yourself before
the startup delay ends:

```bash
uv run python main.py --test-current-long-press --long-press-seconds 1.6
```

To test a normal click wherever the cursor is:

```bash
uv run python main.py --test-current-click
```

## Run Multiple Cycles

```bash
uv run python main.py --cycles 5
```

After the coordinate-based loop is proven reliable, test larger runs.

## Re-anchor After Moving The Window

If the iPhone Mirroring window moved but did not resize:

```bash
uv run python main.py --reanchor --cycles 1
```

Hover over the same square/reference button used during calibration and press Enter. The saved anchor is updated before the automation starts.

This keeps the existing relative button offsets and only changes the starting anchor.

## Timing

Timing is stored in `config.json`:

- `long_press_seconds`
- `focus_settle_delay_seconds`
- `mouse_move_seconds`
- `pre_click_delay_seconds`
- `click_hold_seconds`
- `long_click_mouse_move_seconds`
- `long_click_pre_hold_delay_seconds`
- `transition_delay_seconds`
- `cheap_potion_wait_seconds`
- `haste_tea_wait_seconds`
- `cycle_buffer_seconds`

For now, crafting completion uses fixed waits. Later versions can replace this with Play/Pause screenshot detection.
