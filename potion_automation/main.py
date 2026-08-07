import argparse
import logging
import subprocess

from automation import (
    initialize_cheap_potion,
    run_cycle,
    test_current_click,
    test_current_long_click,
    test_long_click,
)
from config import (
    DEFAULT_CONFIG_PATH,
    describe_config,
    is_calibrated,
    load_config,
    save_config,
    set_reference_anchor,
)
from safety import AutomationStopped, sleep, start_escape_listener


def require_pyautogui():
    try:
        import pyautogui
    except ModuleNotFoundError as error:
        raise ModuleNotFoundError(
            "pyautogui is not installed. Run: pip install -r requirements.txt"
        ) from error

    return pyautogui


def parse_args():
    parser = argparse.ArgumentParser(
        description="Coordinate-based Idle Iktah potion automation."
    )
    parser.add_argument(
        "--config",
        default=DEFAULT_CONFIG_PATH,
        help="Path to config.json. Defaults to potion_automation/config.json.",
    )
    parser.add_argument(
        "--cycles",
        type=int,
        default=1,
        help="Number of full cycles to run. Defaults to 1.",
    )
    parser.add_argument(
        "--infinite",
        action="store_true",
        help="Run until interrupted or PyAutoGUI failsafe is triggered.",
    )
    parser.add_argument(
        "--print-config",
        action="store_true",
        help="Load config and print recorded coordinates/timing without clicking.",
    )
    parser.add_argument(
        "--reanchor",
        action="store_true",
        help="Capture a new reference anchor before running.",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging.",
    )
    parser.add_argument(
        "--focus-app",
        default="iPhone Mirroring",
        help="macOS app/process name to activate before clicking. Defaults to iPhone Mirroring.",
    )
    parser.add_argument(
        "--focus-only",
        action="store_true",
        help="Only try to focus the target app, report the frontmost app, then exit.",
    )
    parser.add_argument(
        "--no-auto-focus",
        action="store_true",
        help="Do not try to activate iPhone Mirroring before the startup countdown.",
    )
    parser.add_argument(
        "--test-long-press",
        choices=("play",),
        help="Only test a long-press on the selected calibrated point, then exit.",
    )
    parser.add_argument(
        "--test-current-click",
        action="store_true",
        help="Click wherever the cursor is when the startup delay ends, then exit.",
    )
    parser.add_argument(
        "--test-current-long-press",
        action="store_true",
        help="Long-press wherever the cursor is when the startup delay ends, then exit.",
    )
    parser.add_argument(
        "--long-press-seconds",
        type=float,
        default=None,
        help="Override long-press duration for this run.",
    )
    return parser.parse_args()


def setup_logging(debug=False):
    logging.basicConfig(
        level=logging.DEBUG if debug else logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        datefmt="%H:%M:%S",
    )


def capture_new_anchor():
    pyautogui = require_pyautogui()
    input("Hover over the same square/reference button used for calibration, then press Enter...")
    point = pyautogui.position()
    return [point.x, point.y]


def run_osascript(script):
    return subprocess.run(
        ["osascript", "-e", script],
        check=True,
        capture_output=True,
        text=True,
    )


def frontmost_app_name():
    result = run_osascript(
        'tell application "System Events" to get name of first application process whose frontmost is true'
    )
    return result.stdout.strip()


def focus_app(app_name):
    subprocess.run(["open", "-a", app_name], check=True)
    sleep(0.2)

    script = f'''
tell application "System Events"
    repeat 20 times
        if exists process "{app_name}" then
            set frontmost of process "{app_name}" to true
            exit repeat
        end if
        delay 0.1
    end repeat
end tell
'''
    run_osascript(script)

    frontmost = frontmost_app_name()
    logging.info("Frontmost app is now: %s", frontmost)
    return frontmost


def main():
    args = parse_args()
    setup_logging(args.debug)

    config = load_config(args.config)

    if args.reanchor:
        anchor = capture_new_anchor()
        set_reference_anchor(config, anchor)
        save_config(config, args.config)
        logging.info("Updated reference anchor to %s", anchor)

    if args.print_config:
        print(describe_config(config))
        return

    if args.long_press_seconds is not None:
        config["timing"]["long_press_seconds"] = args.long_press_seconds

    pyautogui = require_pyautogui()
    pyautogui.FAILSAFE = True
    start_escape_listener()

    needs_calibration = not (args.test_current_click or args.test_current_long_press)

    if args.cycles < 1 and not args.infinite:
        raise ValueError("--cycles must be at least 1 unless --infinite is used.")

    if needs_calibration and not is_calibrated(config):
        raise ValueError("Config is not calibrated yet. Run calibration.py first.")

    startup_delay = float(config["timing"].get("startup_delay_seconds", 5.0))

    logging.info("Idle Iktah Potion Automation")
    logging.info("Move mouse to the top-left corner for emergency stop.")

    logging.info("Starting in %.1f seconds...", startup_delay)
    sleep(startup_delay)

    if not args.no_auto_focus:
        try:
            logging.info("Activating %s", args.focus_app)
            frontmost = focus_app(args.focus_app)
            if frontmost != args.focus_app:
                logging.warning(
                    "Expected %s to be frontmost, but frontmost app is %s",
                    args.focus_app,
                    frontmost,
                )

            focus_settle_delay = float(
                config["timing"].get(
                    "focus_settle_delay_seconds",
                    config["timing"].get("initial_click_delay_seconds", 1.5),
                )
            )
            if focus_settle_delay > 0:
                logging.info(
                    "Waiting %.1f seconds after activating %s",
                    focus_settle_delay,
                    args.focus_app,
                )
                sleep(focus_settle_delay)
        except (OSError, subprocess.CalledProcessError) as error:
            logging.warning("Could not activate %s: %s", args.focus_app, error)

    if args.focus_only:
        logging.info("Focus-only test complete")
        return

    if args.test_current_click:
        test_current_click()
        logging.info("Current-position click test complete")
        return

    if args.test_current_long_press:
        duration = float(config["timing"]["long_press_seconds"])
        test_current_long_click(duration)
        logging.info("Current-position long-press test complete")
        return

    if args.test_long_press:
        duration = float(config["timing"]["long_press_seconds"])
        test_long_click(config, args.test_long_press, duration)
        logging.info("Long-press test complete")
        return

    cycle = 0

    try:
        initialize_cheap_potion(config)

        while args.infinite or cycle < args.cycles:
            cycle += 1
            logging.info("Cycle %s started", cycle)
            run_cycle(config)
            logging.info("Cycle %s completed", cycle)
    except pyautogui.FailSafeException:
        logging.warning("Emergency stop triggered by PyAutoGUI failsafe.")
    except KeyboardInterrupt:
        logging.warning("Stopped by keyboard interrupt.")
    except AutomationStopped:
        logging.warning("Stopped by Escape kill switch.")


if __name__ == "__main__":
    main()
