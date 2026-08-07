import json
from pathlib import Path


DEFAULT_CONFIG_PATH = Path(__file__).with_name("config.json")

REQUIRED_COORDINATES = (
    "play",
    "swap",
    "make_39",
    "make_1",
    "cheap_potion",
    "haste_tea",
)


DEFAULT_TIMING = {
    "startup_delay_seconds": 5.0,
    "focus_settle_delay_seconds": 1.5,
    "mouse_move_seconds": 0.15,
    "pre_click_delay_seconds": 0.1,
    "click_hold_seconds": 0.08,
    "long_click_mouse_move_seconds": 0.15,
    "long_click_pre_hold_delay_seconds": 0.25,
    "long_press_seconds": 0.8,
    "transition_delay_seconds": 0.5,
    "cheap_potion_wait_seconds": 30.5,
    "haste_tea_wait_seconds": 4.5,
    "cycle_buffer_seconds": 1.0,
}


def default_config():
    return {
        "coordinate_mode": "relative_to_reference_anchor",
        "reference_anchor_screen": [0, 0],
        "coordinates": {name: [0, 0] for name in REQUIRED_COORDINATES},
        "timing": dict(DEFAULT_TIMING),
    }


def load_config(path=DEFAULT_CONFIG_PATH):
    config_path = Path(path)

    if not config_path.exists():
        raise FileNotFoundError(
            f"Config not found at {config_path}. Run calibration.py first."
        )

    with config_path.open("r", encoding="utf-8") as config_file:
        config = json.load(config_file)

    validate_config(config)
    return config


def save_config(config, path=DEFAULT_CONFIG_PATH):
    config_path = Path(path)

    with config_path.open("w", encoding="utf-8") as config_file:
        json.dump(config, config_file, indent=2)
        config_file.write("\n")


def validate_config(config):
    if "coordinates" not in config:
        raise ValueError("Config is missing 'coordinates'. Run calibration.py again.")

    missing = [
        name for name in REQUIRED_COORDINATES if name not in config["coordinates"]
    ]
    if missing:
        names = ", ".join(missing)
        raise ValueError(f"Config is missing coordinates: {names}")

    if "timing" not in config:
        raise ValueError("Config is missing 'timing'. Run calibration.py again.")


def is_calibrated(config):
    if config.get("coordinate_mode") in (
        "relative_to_reference_anchor",
        "relative_to_window_anchor",
    ):
        if get_reference_anchor(config) == (0, 0):
            return False

    return any(config["coordinates"][name] != [0, 0] for name in REQUIRED_COORDINATES)


def get_reference_anchor(config):
    anchor = config.get("reference_anchor_screen")
    if anchor is None:
        anchor = config.get("window_anchor_screen", [0, 0])
    return int(anchor[0]), int(anchor[1])


def set_reference_anchor(config, anchor):
    config["reference_anchor_screen"] = [int(anchor[0]), int(anchor[1])]
    config.pop("window_anchor_screen", None)
    config["coordinate_mode"] = "relative_to_reference_anchor"


def resolve_point(config, name):
    point = config["coordinates"][name]

    if config.get("coordinate_mode") in (
        "relative_to_reference_anchor",
        "relative_to_window_anchor",
    ):
        anchor_x, anchor_y = get_reference_anchor(config)
        return int(anchor_x + point[0]), int(anchor_y + point[1])

    return int(point[0]), int(point[1])


def describe_config(config):
    lines = []
    lines.append(f"coordinate_mode: {config.get('coordinate_mode', 'absolute')}")
    lines.append(f"reference_anchor_screen: {list(get_reference_anchor(config))}")
    lines.append("coordinates:")

    for name in REQUIRED_COORDINATES:
        lines.append(f"  {name}: {config['coordinates'][name]}")

    lines.append("timing:")
    for name, value in sorted(config["timing"].items()):
        lines.append(f"  {name}: {value}")

    return "\n".join(lines)
