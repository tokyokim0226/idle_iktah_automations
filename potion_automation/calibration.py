import argparse

import pyautogui

from config import default_config, save_config


def capture_position(label):
    input(f"Hover over {label}, then press Enter...")
    point = pyautogui.position()
    print(f"Saved {label}: ({point.x}, {point.y})")
    return [point.x, point.y]


def to_relative(anchor, point):
    return [int(point[0] - anchor[0]), int(point[1] - anchor[1])]


def parse_args():
    parser = argparse.ArgumentParser(description="Calibrate Idle Iktah coordinates.")
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

    print("Idle Iktah Potion Automation Calibration")
    print()
    print("Do not click while capturing coordinates.")
    print("Hover the mouse over each requested location, then press Enter.")
    print("Move the mouse to the top-left corner to emergency-stop.")
    print()
    print("Keep the iPhone Mirroring window at the size you plan to use.")
    print("Use the same stable square/reference button as the first point every time.")
    print()

    anchor = capture_position("your stable square/reference button")

    print()
    print("Base screen: cheap potion selected, Play and Swap visible.")
    print()

    absolute_coordinates = {}
    absolute_coordinates["play"] = capture_position("PLAY")
    absolute_coordinates["swap"] = capture_position("SWAP")

    print()
    print("Manually long-press PLAY to open the 'Make how many?' popup.")
    print("Then capture the quantity buttons.")
    print()

    absolute_coordinates["make_39"] = capture_position("39")
    absolute_coordinates["make_1"] = capture_position("1")

    print()
    print("Manually close the quantity popup and open the potion selector.")
    print("Cheap potion is top-left. Haste Tea is bottom-right.")
    print()

    absolute_coordinates["cheap_potion"] = capture_position("CHEAP POTION")
    absolute_coordinates["haste_tea"] = capture_position("HASTE TEA")

    relative_coordinates = {
        name: to_relative(anchor, point)
        for name, point in absolute_coordinates.items()
    }

    config = {
        "coordinate_mode": "relative_to_reference_anchor",
        "reference_anchor_screen": anchor,
        "coordinates": relative_coordinates,
        "timing": default_config()["timing"],
    }

    save_config(config)

    print()
    print("Calibration saved to config.json")
    print("Coordinates were stored relative to the captured reference anchor.")


if __name__ == "__main__":
    main()
