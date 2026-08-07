import argparse
import logging
import subprocess

from automation import run_cycle, run_initial_navigation, test_click
from config import (
    DEFAULT_CONFIG_PATH,
    REQUIRED_COORDINATES,
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
        raise ModuleNotFoundError("pyautogui is not installed. Run: uv sync") from error

    return pyautogui


def parse_args():
    parser = argparse.ArgumentParser(
        description="Coordinate-based Bloom Festival automation."
    )
    parser.add_argument(
        "--config",
        default=DEFAULT_CONFIG_PATH,
        help="Path to config.json. Defaults to bloom_festival/config.json.",
    )
    parser.add_argument(
        "--cycles",
        type=int,
        default=1,
        help="Number of repeat cycles to run. Defaults to 1.",
    )
    parser.add_argument(
        "--infinite",
        action="store_true",
        help="Run until interrupted or PyAutoGUI failsafe is triggered.",
    )
    parser.add_argument(
        "--skip-initial",
        action="store_true",
        help="Skip the one-time 3-click initial navigation.",
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
        "--focus-app",
        default="iPhone Mirroring",
        help="macOS app/process name to activate before clicking.",
    )
    parser.add_argument(
        "--focus-only",
        action="store_true",
        help="Only try to focus the target app, report the frontmost app, then exit.",
    )
    parser.add_argument(
        "--no-auto-focus",
        action="store_true",
        help="Do not try to activate iPhone Mirroring before clicking.",
    )
    parser.add_argument(
        "--test-click",
        choices=REQUIRED_COORDINATES,
        help="Click one calibrated point, then exit.",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging.",
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


def prepare_focus(args, config):
    startup_delay = float(config["timing"].get("startup_delay_seconds", 5.0))

    logging.info("Starting in %.1f seconds...", startup_delay)
    sleep(startup_delay)

    if args.no_auto_focus:
        return

    logging.info("Activating %s", args.focus_app)
    frontmost = focus_app(args.focus_app)
    if frontmost != args.focus_app:
        logging.warning(
            "Expected %s to be frontmost, but frontmost app is %s",
            args.focus_app,
            frontmost,
        )

    focus_settle_delay = float(config["timing"].get("focus_settle_delay_seconds", 1.5))
    if focus_settle_delay > 0:
        logging.info(
            "Waiting %.1f seconds after activating %s",
            focus_settle_delay,
            args.focus_app,
        )
        sleep(focus_settle_delay)


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

    if args.cycles < 1 and not args.infinite:
        raise ValueError("--cycles must be at least 1 unless --infinite is used.")

    if not is_calibrated(config):
        raise ValueError("Config is not calibrated yet. Run calibration.py first.")

    pyautogui = require_pyautogui()
    pyautogui.FAILSAFE = True
    start_escape_listener()

    logging.info("Bloom Festival Automation")
    logging.info("Move mouse to the top-left corner for emergency stop.")

    try:
        prepare_focus(args, config)

        if args.focus_only:
            logging.info("Focus-only test complete")
            return

        if args.test_click:
            test_click(config, args.test_click)
            logging.info("Test click complete")
            return

        if not args.skip_initial:
            run_initial_navigation(config)

        cycle = 0
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
    except (OSError, subprocess.CalledProcessError) as error:
        logging.error("Focus command failed: %s", error)


if __name__ == "__main__":
    main()
