# Idle Iktah Potion Automation
## Project Specification for Codex / VS Code

## 1. Project Goal

Build a small macOS automation tool that controls **Idle Iktah through Apple iPhone Mirroring**.

The automation should repeatedly exploit the game's potion conservation mechanic:

- Craft **39 cheap potions**
- Switch to **Haste Tea**
- Craft **1 Haste Tea** as the 40th potion
- Switch back to the cheap potion
- Repeat

The tool should interact with the mirrored iPhone UI using mouse control and screenshots. It should not require modifying the game, accessing internal game data, or interacting with the iPhone app directly.

The first version should prioritize:

- simplicity
- reliability
- easy calibration
- easy debugging
- easy stopping
- minimal dependencies
- clear state-based logic

Do not overengineer V1.

Current implementation note:

- Startup attempts to activate iPhone Mirroring via AppleScript.
- Startup waits using `startup_delay_seconds`, activates iPhone Mirroring with `open -a` plus System Events, then waits `focus_settle_delay_seconds` before the first click.
- Before cycle 1, the script opens Swap and selects the cheap potion so the selected potion is initialized.
- This still assumes the base Alchemy screen is visible with Play/Swap available.

---

# 2. Target Environment

## Hardware / OS

- Mac laptop
- iPhone
- Apple iPhone Mirroring
- Idle Iktah running on the mirrored iPhone

## Development Environment

- VS Code
- Python 3.11+ recommended
- Codex used as coding assistant

## Suggested Python Dependencies

Start with:

```bash
pip install pyautogui pillow
```

Optional later:

```bash
pip install opencv-python
```

Use OpenCV only if template matching becomes necessary.

---

# 3. User Workflow to Automate

The full loop is:

```text
Base alchemy screen with Play/Swap visible
        |
        v
Click Swap
        |
        v
Potion selector opens
        |
        v
Click cheap potion
        |
        v
Long-press Play
        |
        v
Quantity popup appears
        |
        v
Click 39
        |
        v
Wait for 39 cheap potions to finish
        |
        v
Click Swap
        |
        v
Potion selector opens
        |
        v
Click Haste Tea
        |
        v
Long-press Play
        |
        v
Quantity popup appears
        |
        v
Click 1
        |
        v
Wait for Haste Tea to finish
        |
        v
Click Swap
        |
        v
Potion selector opens
        |
        v
Click cheap potion
        |
        v
Repeat
```

---

# 4. Known UI Elements

There are six primary clickable locations required for the automation.

```text
PLAY
SWAP
MAKE_39
MAKE_1
CHEAP_POTION
HASTE_TEA
```

These coordinates must not be hard-coded permanently.

The user should calibrate them based on the current size and position of the iPhone Mirroring window.

---

# 5. UI States from the Supplied Screenshots

## State A — Cheap Potion Ready

The cheap potion is selected and no crafting is occurring.

Visible characteristics:

- Play button displays a triangle: `▶`
- Swap button is immediately to the right of Play
- Cheap potion ingredients are visible on the right side
- No active countdown is present

Required action:

```text
Long-press PLAY
```

Expected result:

```text
Quantity popup opens
```

---

## State B — Quantity Popup

The popup title is:

```text
Make how many?
```

The popup includes preset quantities.

Relevant buttons:

```text
1
39
```

When the cheap potion is selected:

```text
Click 39
```

When Haste Tea is selected:

```text
Click 1
```

Selecting a quantity automatically begins crafting.

No separate confirmation click is needed.

---

## State C — Cheap Potion Crafting

While the 39 cheap potions are being made:

- Play changes to Pause: `⏸`
- a remaining count appears near the button
- the number decreases
- the progress bar animates

Observed example:

```text
1 potion = 0.74 seconds
```

Therefore:

```text
39 × 0.74 = 28.86 seconds
```

A simple V1 may wait approximately:

```text
30.5 seconds
```

However, the preferred later implementation is to detect when the Play button returns.

---

## State D — Potion Selection Popup

Pressing Swap opens:

```text
Non-Combat Potions
```

The potion grid is shown.

Known positions from the current UI layout:

- cheap potion = top-left potion
- Haste Tea = bottom-right potion

These should still be calibrated instead of relying on absolute screenshot coordinates.

Required action after the cheap batch:

```text
Click HASTE_TEA
```

Required action after Haste Tea finishes:

```text
Click CHEAP_POTION
```

---

## State E — Haste Tea Ready

After Haste Tea is selected:

- Haste Tea ingredients appear on the right
- Play button displays `▶`
- example crafting time shown: `3.7 seconds`

Required action:

```text
Long-press PLAY
```

Then:

```text
Click 1
```

---

## State F — Haste Tea Crafting

Craft exactly one Haste Tea.

Observed crafting time:

```text
3.7 seconds
```

Simple V1 delay:

```text
4.5 seconds
```

Preferred later behavior:

```text
Wait until Play button reappears
```

Then switch back to the cheap potion.

---

# 6. Important Interaction Detail: Long Press

A normal click on Play is not sufficient to open the quantity popup.

The automation must perform a real click-and-hold.

Suggested implementation:

```python
import time
import pyautogui


def long_click(point, duration=0.8):
    pyautogui.moveTo(*point, duration=0.15)
    pyautogui.mouseDown()
    time.sleep(duration)
    pyautogui.mouseUp()
```

The long-press duration may need calibration.

Start with:

```text
0.8 seconds
```

Potential range:

```text
0.6–1.0 seconds
```

---

# 7. Recommended Project Architecture

Use a small, explicit project structure.

```text
idle-iktah-automation/
|
├── README.md
├── requirements.txt
├── config.json
├── main.py
├── calibration.py
├── automation.py
├── screen.py
├── state.py
├── logger.py
|
├── templates/
│   ├── play_button.png
│   ├── pause_button.png
│   ├── quantity_popup.png
│   └── potion_selector.png
|
└── logs/
```

For V1, not every file must contain complex logic.

The separation exists so the project can grow cleanly.

---

# 8. Responsibilities of Each File

## `main.py`

Application entry point.

Responsibilities:

- load configuration
- wait for user to start
- run automation loop
- count completed cycles
- catch stop conditions
- handle fatal errors cleanly

Example responsibilities:

```python
load_config()
wait_for_start()
run_loop()
```

---

## `calibration.py`

Used to record UI positions.

The user manually positions the mouse over each required button and presses Enter.

Required calibration points:

```text
PLAY
SWAP
MAKE_39
MAKE_1
CHEAP_POTION
HASTE_TEA
```

Store coordinates in:

```text
config.json
```

Example:

```json
{
  "play": [812, 743],
  "swap": [915, 743],
  "make_39": [905, 521],
  "make_1": [814, 412],
  "cheap_potion": [833, 351],
  "haste_tea": [1116, 692],
  "long_press_seconds": 0.8,
  "cheap_potion_wait_seconds": 30.5,
  "haste_tea_wait_seconds": 4.5
}
```

These numbers are examples only.

The real values must come from calibration.

---

## `automation.py`

Contains mouse interaction logic.

Suggested functions:

```python
click(point)
long_click(point)
open_quantity_menu()
select_quantity_39()
select_quantity_1()
open_potion_selector()
select_cheap_potion()
select_haste_tea()
make_39_cheap()
make_1_haste()
run_cycle()
```

---

## `screen.py`

Contains screenshot and visual detection logic.

This can be minimal in V1.

Later responsibilities:

```python
is_play_visible()
is_pause_visible()
is_quantity_popup_visible()
is_potion_selector_visible()
wait_until_finished()
```

Do not add OCR unless actually necessary.

---

## `state.py`

Optional but recommended once V1 works.

Define clear states such as:

```python
from enum import Enum


class GameState(Enum):
    CHEAP_READY = "cheap_ready"
    QUANTITY_POPUP = "quantity_popup"
    CHEAP_CRAFTING = "cheap_crafting"
    POTION_SELECTOR = "potion_selector"
    HASTE_READY = "haste_ready"
    HASTE_CRAFTING = "haste_crafting"
    UNKNOWN = "unknown"
```

---

## `logger.py`

Optional helper for consistent logging.

Each action should eventually produce logs such as:

```text
[16:40:01] Cycle 12 started
[16:40:02] Opened quantity menu
[16:40:03] Selected quantity 39
[16:40:33] Cheap potion crafting finished
[16:40:34] Selected Haste Tea
[16:40:35] Selected quantity 1
[16:40:40] Haste Tea finished
[16:40:41] Returned to cheap potion
[16:40:41] Cycle 12 completed
```

---

# 9. V1 Scope

V1 should be a deterministic coordinate-based macro.

Do not start with computer vision.

The purpose of V1 is to prove that the complete loop works.

## V1 Workflow

```python
def run_cycle():
    make_39_cheap()
    wait_for_cheap_batch()
    select_haste_tea()
    make_1_haste()
    wait_for_haste()
    select_cheap_potion()
```

Example implementation:

```python
import time
import pyautogui


def click(point):
    pyautogui.click(*point)


def long_click(point, duration=0.8):
    pyautogui.moveTo(*point, duration=0.15)
    pyautogui.mouseDown()
    time.sleep(duration)
    pyautogui.mouseUp()


def run_cycle(config):
    # Make 39 cheap potions
    long_click(config["play"], config["long_press_seconds"])
    time.sleep(0.5)

    click(config["make_39"])

    time.sleep(config["cheap_potion_wait_seconds"])

    # Switch to Haste Tea
    click(config["swap"])
    time.sleep(0.5)

    click(config["haste_tea"])
    time.sleep(0.5)

    # Make exactly one Haste Tea
    long_click(config["play"], config["long_press_seconds"])
    time.sleep(0.5)

    click(config["make_1"])

    time.sleep(config["haste_tea_wait_seconds"])

    # Return to cheap potion
    click(config["swap"])
    time.sleep(0.5)

    click(config["cheap_potion"])
    time.sleep(0.5)
```

---

# 10. V1 Main Loop

Example:

```python
import time
import pyautogui

from automation import run_cycle
from config import load_config


def main():
    config = load_config()

    pyautogui.FAILSAFE = True

    print("Idle Iktah automation")
    print("Starting in 5 seconds.")
    print("Move the mouse to the top-left corner to emergency-stop.")

    time.sleep(5)

    cycle = 0

    while True:
        cycle += 1

        print(f"Starting cycle {cycle}")

        run_cycle(config)

        print(f"Completed cycle {cycle}")


if __name__ == "__main__":
    main()
```

---

# 11. Calibration System

Calibration is important because the iPhone Mirroring window may move or resize.

Create an interactive script.

Example flow:

```text
Calibration

1. Open Idle Iktah on the cheap potion screen.
2. Hover over PLAY.
3. Press Enter.

Saved PLAY = (x, y)

4. Hover over SWAP.
5. Press Enter.

Saved SWAP = (x, y)

6. Long-press Play manually to open "Make how many?"
7. Hover over 39.
8. Press Enter.

Saved MAKE_39 = (x, y)

9. Hover over 1.
10. Press Enter.

Saved MAKE_1 = (x, y)

11. Close the quantity popup.
12. Open the potion selector manually.
13. Hover over the cheap potion.
14. Press Enter.

Saved CHEAP_POTION = (x, y)

15. Hover over Haste Tea.
16. Press Enter.

Saved HASTE_TEA = (x, y)
```

Suggested helper:

```python
import pyautogui


def capture_position(name):
    input(f"Hover over {name}, then press Enter...")
    position = pyautogui.position()
    print(f"{name}: {position}")
    return [position.x, position.y]
```

Then write the result to `config.json`.

---

# 12. Safety Requirements

GUI automation can click unintended locations if the window moves.

Safety features are therefore mandatory.

## 12.1 PyAutoGUI Failsafe

Enable:

```python
pyautogui.FAILSAFE = True
```

Moving the mouse rapidly to the top-left corner should terminate the automation.

---

## 12.2 Startup Delay

Always wait before beginning.

Example:

```python
print("Starting in 5 seconds...")
time.sleep(5)
```

This gives the user time to focus the iPhone Mirroring window.

---

## 12.3 Maximum Cycle Option

Do not require infinite operation.

Support:

```bash
python main.py --cycles 10
```

Possible values:

```text
1
10
50
100
infinite
```

A finite run mode is useful for testing.

---

## 12.4 Stop Between Actions

Avoid zero-delay clicking.

Use small delays such as:

```text
0.3–0.7 seconds
```

between UI transitions.

---

## 12.5 Unexpected State Handling

Later versions should stop rather than guess.

For example:

```python
if state == UNKNOWN:
    stop_automation()
```

Never continue blindly if the expected screen is missing.

---

# 13. V2: Visual State Detection

Once V1 is working, replace fixed crafting delays with screenshot-based state detection.

The most useful visual difference is:

```text
Ready:
▶

Crafting:
⏸
```

The automation does not need to OCR the remaining quantity.

Instead:

```text
start crafting
    |
    v
pause button visible
    |
    v
wait
    |
    v
play button visible again
    |
    v
crafting finished
```

---

# 14. Recommended Detection Area

Do not search the whole screen.

Only capture a small rectangular region around the Play/Pause button.

Advantages:

- faster
- fewer false matches
- easier template matching
- less sensitivity to unrelated animations

Conceptual code:

```python
PLAY_REGION = (
    left,
    top,
    width,
    height
)

screenshot = pyautogui.screenshot(region=PLAY_REGION)
```

---

# 15. Template Matching

A later version can store cropped images:

```text
templates/play_button.png
templates/pause_button.png
```

Possible implementation:

```python
location = pyautogui.locateOnScreen(
    "templates/play_button.png",
    confidence=0.90,
    region=PLAY_REGION
)
```

Note:

`confidence=` generally requires OpenCV.

Install if needed:

```bash
pip install opencv-python
```

Do not introduce OpenCV before the basic macro works.

---

# 16. `wait_until_finished()`

Target behavior:

```python
def wait_until_finished(timeout=120):
    start = time.time()

    while time.time() - start < timeout:
        if is_play_visible():
            return True

        time.sleep(0.4)

    return False
```

Usage:

```python
click(config["make_39"])

if not wait_until_finished():
    raise RuntimeError("Cheap potion crafting did not finish in time")
```

Same function can be reused after crafting Haste Tea.

---

# 17. Avoid OCR Unless Necessary

The crafting screen displays remaining counts such as:

```text
34
33
32
...
```

Do not attempt to OCR these numbers initially.

There is no need.

The Play/Pause state alone indicates whether crafting is active.

This makes the implementation much simpler.

---

# 18. Future State Machine

After V1 works, model the automation as a finite-state machine.

Suggested states:

```text
CHEAP_READY
QUANTITY_MENU_FOR_CHEAP
CHEAP_CRAFTING
POTION_SELECTOR_FOR_HASTE
HASTE_READY
QUANTITY_MENU_FOR_HASTE
HASTE_CRAFTING
POTION_SELECTOR_FOR_CHEAP
UNKNOWN
```

Transitions:

```text
CHEAP_READY
    -> long press Play

QUANTITY_MENU_FOR_CHEAP
    -> click 39

CHEAP_CRAFTING
    -> wait until Play returns

POTION_SELECTOR_FOR_HASTE
    -> click Haste Tea

HASTE_READY
    -> long press Play

QUANTITY_MENU_FOR_HASTE
    -> click 1

HASTE_CRAFTING
    -> wait until Play returns

POTION_SELECTOR_FOR_CHEAP
    -> click cheap potion

CHEAP_READY
    -> repeat
```

---

# 19. Why Use a State Machine

A simple macro assumes every click succeeded.

Example bad approach:

```python
click()
sleep()
click()
sleep()
click()
sleep()
```

If one click fails, every following click may happen on the wrong UI.

A state-aware version instead asks:

```text
What screen am I currently on?
```

before deciding what action to take.

This allows recovery or safe shutdown.

---

# 20. State Validation

Before important clicks, later versions should verify the expected screen.

Examples:

Before clicking 39:

```text
Confirm quantity popup is visible.
```

Before clicking Haste Tea:

```text
Confirm potion selector is visible.
```

Before long-pressing Play:

```text
Confirm Play button is visible.
```

If verification fails:

```text
STOP
LOG ERROR
DO NOT CLICK RANDOMLY
```

---

# 21. Logging

Use Python's built-in `logging` module.

Example:

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
```

Log:

- program start
- calibration loaded
- cycle start
- each major click
- crafting start
- crafting finish
- potion selection
- completed cycle
- errors
- user stop
- timeout

---

# 22. Configuration

Avoid scattering constants throughout the code.

Use one configuration file.

Example:

```json
{
  "coordinates": {
    "play": [0, 0],
    "swap": [0, 0],
    "make_39": [0, 0],
    "make_1": [0, 0],
    "cheap_potion": [0, 0],
    "haste_tea": [0, 0]
  },
  "timing": {
    "long_press_seconds": 0.8,
    "transition_delay_seconds": 0.5,
    "cheap_potion_wait_seconds": 30.5,
    "haste_tea_wait_seconds": 4.5
  }
}
```

---

# 23. Potential Coordinate Improvement

Absolute screen coordinates are acceptable for V1.

However, a more robust design could store coordinates relative to the iPhone Mirroring window.

Example:

```text
Window top-left = (500, 120)

Play inside window = (110, 710)

Actual screen click:

x = window_left + 110
y = window_top + 710
```

This would allow the whole mirroring window to move while preserving button positions.

This is not required for V1.

---

# 24. Optional GUI

Do not build this until the command-line version is reliable.

Possible later interface:

```text
+--------------------------------+
| Idle Iktah Potion Automation   |
|                                |
| Status: Crafting cheap potion  |
|                                |
| Completed cycles: 27           |
| Haste Teas made: 27            |
|                                |
| [ Start ]       [ Stop ]       |
|                                |
| [ Calibrate ]                  |
+--------------------------------+
```

Possible framework:

```text
tkinter
```

Prefer tkinter because it is built into Python and sufficient for this project.

---

# 25. Suggested CLI

Eventually support:

```bash
python main.py
```

Default:

```text
run indefinitely
```

Alternative:

```bash
python main.py --cycles 20
```

Calibration:

```bash
python calibration.py
```

Debug:

```bash
python main.py --cycles 1 --debug
```

---

# 26. Error Handling

Examples of errors that should terminate the run:

```text
Calibration missing
Play button not detected
Potion selector not detected
Quantity popup not detected
Crafting timeout
User activates emergency stop
Screenshot permission unavailable
Mouse control permission unavailable
```

Do not silently continue after an unexpected UI state.

---

# 27. macOS Permissions

The automation may require macOS permissions.

Likely permissions:

## Accessibility

Needed so Python / Terminal / VS Code can control the mouse.

Possible location:

```text
System Settings
-> Privacy & Security
-> Accessibility
```

Allow the application being used to run the Python script.

This might be:

- Terminal
- iTerm
- VS Code
- Python

depending on how the script is launched.

## Screen Recording

Needed if screenshot-based detection is introduced.

Possible location:

```text
System Settings
-> Privacy & Security
-> Screen Recording
```

---

# 28. V1 Implementation Milestones

## Milestone 1 — Mouse Control Test

Create a script that:

1. waits 3 seconds
2. prints current mouse position
3. clicks one harmless location

Confirm PyAutoGUI controls iPhone Mirroring correctly.

---

## Milestone 2 — Long-Press Test

Test only:

```text
Long-press Play
```

Success condition:

```text
"Make how many?" popup appears
```

Do not automate anything else yet.

---

## Milestone 3 — Calibration

Build `calibration.py`.

Capture:

```text
PLAY
SWAP
MAKE_39
MAKE_1
CHEAP_POTION
HASTE_TEA
```

Save to `config.json`.

---

## Milestone 4 — Make 39 Cheap Potions

Automate:

```text
Long-press Play
-> click 39
```

Stop there.

Verify it reliably starts a batch of 39.

---

## Milestone 5 — Switch Potion

After the user manually waits for completion, automate:

```text
Swap
-> Haste Tea
```

Verify correct potion selection.

---

## Milestone 6 — Make One Haste Tea

Automate:

```text
Long-press Play
-> click 1
```

Verify exactly one Haste Tea is crafted.

---

## Milestone 7 — Return to Cheap Potion

Automate:

```text
Swap
-> cheap potion
```

Verify the original potion becomes selected.

---

## Milestone 8 — One Complete Cycle

Combine all actions.

Run:

```text
39 cheap
-> Haste Tea
-> 1 Haste Tea
-> cheap potion
```

Stop after one complete cycle.

---

## Milestone 9 — Multiple Cycles

Run:

```text
5 cycles
```

Observe for failures.

Then:

```text
20 cycles
```

Only after this should infinite looping be considered.

---

## Milestone 10 — Visual Completion Detection

Replace:

```python
time.sleep(30.5)
```

with:

```python
wait_until_finished()
```

using Play/Pause visual detection.

Repeat for Haste Tea.

---

# 29. Acceptance Criteria for V1

V1 is considered complete when:

- calibration works
- user can save all six coordinates
- long-press reliably opens quantity menu
- automation selects 39
- automation waits for cheap crafting
- automation selects Haste Tea
- automation selects quantity 1
- automation waits for Haste Tea
- automation switches back to the cheap potion
- automation can complete at least 10 cycles without manual interaction
- emergency stop works
- no OCR is required
- errors are logged instead of ignored

---

# 30. Acceptance Criteria for V2

V2 is considered complete when:

- fixed crafting delays are removed
- Play/Pause state is detected visually
- quantity popup is optionally validated
- potion selector is optionally validated
- unexpected states stop the automation
- the script is resilient to minor timing variation
- failures produce useful logs

---

# 31. Things Not to Build Yet

Do not add these during the first implementation:

- OCR
- machine learning
- object detection
- Selenium
- browser automation
- an iOS app
- direct game memory manipulation
- network interception
- complex database
- cloud infrastructure
- Docker
- web server
- mobile app
- large GUI framework

None are required.

---

# 32. Possible Later Improvements

After the core automation is reliable:

## Automatic window detection

Find the iPhone Mirroring window automatically.

## Relative coordinates

Store button positions relative to the window instead of the entire monitor.

## Template-based buttons

Find Play, Swap, and popup controls based on images.

## Potion verification

Confirm the correct potion was selected before crafting.

## Cycle statistics

Track:

```text
cycles completed
Haste Teas created
runtime
average cycle duration
errors
```

## Auto recovery

If a known safe state is detected, return to the expected workflow.

Example:

```text
Potion selector unexpectedly open
-> inspect current phase
-> choose expected potion
```

Only implement this after detection is reliable.

---

# 33. Suggested Development Philosophy

Keep actions explicit.

Good:

```python
select_haste_tea()
wait_until_ready()
make_one_haste()
```

Avoid:

```python
do_stuff()
```

Keep each function small enough that failures can be traced.

Prioritize:

```text
correctness > cleverness
```

The project is small.

The goal is not to demonstrate complicated engineering.

The goal is to build a reliable automation tool.

---

# 34. Recommended Initial Implementation

Start with exactly these files:

```text
idle-iktah-automation/
├── main.py
├── automation.py
├── calibration.py
├── config.json
├── requirements.txt
└── README.md
```

Do not create `screen.py` or state-machine code until the basic loop works.

---

# 35. Initial `requirements.txt`

```text
pyautogui
pillow
```

Later:

```text
opencv-python
```

only when visual detection is added.

---

# 36. Initial `automation.py` Skeleton

```python
import time

import pyautogui


def click(point):
    pyautogui.click(*point)


def long_click(point, duration):
    pyautogui.moveTo(*point, duration=0.15)
    pyautogui.mouseDown()
    time.sleep(duration)
    pyautogui.mouseUp()


def make_39_cheap(config):
    coords = config["coordinates"]
    timing = config["timing"]

    long_click(
        coords["play"],
        timing["long_press_seconds"],
    )

    time.sleep(timing["transition_delay_seconds"])

    click(coords["make_39"])


def select_haste_tea(config):
    coords = config["coordinates"]
    timing = config["timing"]

    click(coords["swap"])

    time.sleep(timing["transition_delay_seconds"])

    click(coords["haste_tea"])


def make_1_haste(config):
    coords = config["coordinates"]
    timing = config["timing"]

    long_click(
        coords["play"],
        timing["long_press_seconds"],
    )

    time.sleep(timing["transition_delay_seconds"])

    click(coords["make_1"])


def select_cheap_potion(config):
    coords = config["coordinates"]
    timing = config["timing"]

    click(coords["swap"])

    time.sleep(timing["transition_delay_seconds"])

    click(coords["cheap_potion"])


def run_cycle(config):
    timing = config["timing"]

    make_39_cheap(config)

    time.sleep(timing["cheap_potion_wait_seconds"])

    select_haste_tea(config)

    time.sleep(timing["transition_delay_seconds"])

    make_1_haste(config)

    time.sleep(timing["haste_tea_wait_seconds"])

    select_cheap_potion(config)

    time.sleep(timing["transition_delay_seconds"])
```

---

# 37. Initial `main.py` Skeleton

```python
import argparse
import json
import time

import pyautogui

from automation import run_cycle


def load_config(path="config.json"):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--cycles",
        type=int,
        default=None,
        help="Number of cycles to run. Omit for infinite.",
    )

    return parser.parse_args()


def main():
    args = parse_args()
    config = load_config()

    pyautogui.FAILSAFE = True

    print("Idle Iktah Potion Automation")
    print("Move mouse to the top-left corner for emergency stop.")
    print("Starting in 5 seconds...")

    time.sleep(5)

    cycle = 0

    while args.cycles is None or cycle < args.cycles:
        cycle += 1

        print(f"Starting cycle {cycle}")

        run_cycle(config)

        print(f"Completed cycle {cycle}")


if __name__ == "__main__":
    main()
```

---

# 38. Initial `calibration.py` Skeleton

```python
import json

import pyautogui


def capture_position(name):
    input(f"Hover over {name}, then press Enter...")

    point = pyautogui.position()

    print(f"{name}: ({point.x}, {point.y})")

    return [point.x, point.y]


def main():
    print("Idle Iktah Calibration")
    print()
    print("Keep the iPhone Mirroring window in the position")
    print("you intend to use during automation.")
    print()

    coordinates = {}

    coordinates["play"] = capture_position("PLAY")
    coordinates["swap"] = capture_position("SWAP")

    print()
    print("Manually open the 'Make how many?' popup.")
    print()

    coordinates["make_39"] = capture_position("39")
    coordinates["make_1"] = capture_position("1")

    print()
    print("Manually close the quantity popup and open the potion selector.")
    print()

    coordinates["cheap_potion"] = capture_position("CHEAP POTION")
    coordinates["haste_tea"] = capture_position("HASTE TEA")

    config = {
        "coordinates": coordinates,
        "timing": {
            "long_press_seconds": 0.8,
            "transition_delay_seconds": 0.5,
            "cheap_potion_wait_seconds": 30.5,
            "haste_tea_wait_seconds": 4.5,
        },
    }

    with open("config.json", "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)

    print()
    print("Calibration saved to config.json")


if __name__ == "__main__":
    main()
```

---

# 39. Development Instructions for Codex

When implementing this project:

1. Start from the minimum V1 architecture.
2. Do not add visual detection until the coordinate macro works.
3. Keep all mouse coordinates in `config.json`.
4. Keep timing values configurable.
5. Keep mouse actions in small reusable functions.
6. Enable PyAutoGUI failsafe.
7. Add useful console logging.
8. Test with one cycle before multiple cycles.
9. Do not add dependencies without a clear reason.
10. Prefer stopping on uncertainty instead of making an unsafe click.
11. Do not assume screen coordinates from the supplied screenshots match the Mac.
12. Treat the supplied screenshots only as UI/state references.
13. Keep functions clear and explicit.
14. Do not build a GUI until the CLI version is stable.
15. Once V1 is reliable, implement Play/Pause visual detection as the first major robustness improvement.

---

# 40. Recommended First Codex Task

Give Codex the following task after adding this specification to the repository:

```text
Read the project specification.

Implement only Milestones 1–3:

1. Create the basic Python project structure.
2. Add requirements.txt with pyautogui and pillow.
3. Implement calibration.py so the user can capture and save:
   - play
   - swap
   - make_39
   - make_1
   - cheap_potion
   - haste_tea
4. Store positions and timing configuration in config.json.
5. Add a simple script or test mode that loads config.json and prints the
   recorded coordinates.
6. Add clear setup instructions to README.md.
7. Enable PyAutoGUI failsafe where appropriate.

Do not implement the full automation loop yet.
Do not add OpenCV, OCR, a GUI, Docker, or unnecessary abstractions.

After implementation, explain the files created and tell me exactly how
to test calibration.
```

After calibration works, the next Codex task should be:

```text
Implement Milestones 4–8 from the specification.

Build the first complete coordinate-based automation cycle:

39 cheap potions
-> wait
-> Haste Tea
-> 1 potion
-> wait
-> cheap potion

Support --cycles N so I can test one cycle before running several.

Do not add visual recognition yet.

Add logging for each major action and stop cleanly on PyAutoGUI failsafe.
```

Then, only after the coordinate-based workflow is proven reliable:

```text
Implement Milestone 10.

Replace fixed potion-crafting waits with visual Play/Pause detection.

Only inspect a small region around the Play/Pause button.

Use template matching rather than OCR.

Add a timeout and stop the automation if the expected state does not
appear.

Keep the existing fixed-delay mode as an optional fallback while the new
detection logic is being tested.
```

---

# 41. End Goal

The final tool should behave like this:

```text
$ python main.py --cycles 10

Idle Iktah Potion Automation
Starting in 5 seconds...

Cycle 1
  Opening cheap potion quantity menu
  Selecting 39
  Crafting...
  Cheap batch complete
  Opening potion selector
  Selecting Haste Tea
  Opening quantity menu
  Selecting 1
  Crafting...
  Haste Tea complete
  Returning to cheap potion
Cycle 1 complete

Cycle 2
...
```

The user should be able to leave the mirrored Idle Iktah window open and let the automation repeat the sequence without manually performing each potion swap.

The architecture should remain simple enough that if the game UI changes, the user can recalibrate coordinates or replace a small template instead of rewriting the project.
