import argparse

import pyautogui

from config import (
    ACTION_CLICK_NAMES,
    INITIAL_CLICK_NAMES,
    default_config,
    save_config,
)


def capture_position(label):
    input(f"Hover over {label}, then press Enter...")
    point = pyautogui.position()
    print(f"Saved {label}: ({point.x}, {point.y})")
    return [point.x, point.y]


def to_relative(anchor, point):
    return [int(point[0] - anchor[0]), int(point[1] - anchor[1])]


def parse_args():
    parser = argparse.ArgumentParser(description="Calibrate Bloom Festival clicks.")
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Reset config.json to blank placeholder coordinates and exit.",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    if args.reset:
        save_config(default_config())
        print("Reset config.json to blank placeholder coordinates.")
        return

    pyautogui.FAILSAFE = True

    print("Bloom Festival Automation Calibration")
    print()
    print("Do not click while capturing coordinates.")
    print("Hover the requested target and press Enter.")
    print("Move the mouse to the top-left corner to emergency-stop.")
    print()

    anchor = capture_position("your stable square/reference button")

    print()
    print("Capture the 3 one-time initial navigation clicks.")
    print()

    absolute_coordinates = {}
    for index, name in enumerate(INITIAL_CLICK_NAMES, start=1):
        absolute_coordinates[name] = capture_position(f"INITIAL CLICK {index}")

    print()
    print("Capture the repeat loop: START, 13 action clicks, then OK.")
    print()

    absolute_coordinates["start"] = capture_position("START BUTTON")

    for index, name in enumerate(ACTION_CLICK_NAMES, start=1):
        absolute_coordinates[name] = capture_position(f"ACTION CLICK {index}")

    absolute_coordinates["ok"] = capture_position("OK BUTTON")

    config = {
        "coordinate_mode": "relative_to_reference_anchor",
        "reference_anchor_screen": anchor,
        "coordinates": {
            name: to_relative(anchor, point)
            for name, point in absolute_coordinates.items()
        },
        "timing": default_config()["timing"],
    }

    save_config(config)

    print()
    print("Calibration saved to config.json")
    print("Coordinates were stored relative to the captured reference anchor.")


if __name__ == "__main__":
    main()
