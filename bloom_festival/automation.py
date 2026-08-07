import logging

from config import ACTION_CLICK_NAMES, INITIAL_CLICK_NAMES, resolve_point
from safety import raise_if_stop_requested, sleep


def require_pyautogui():
    try:
        import pyautogui
    except ModuleNotFoundError as error:
        raise ModuleNotFoundError(
            "pyautogui is not installed. Run: uv sync"
        ) from error

    return pyautogui


def click(config, name):
    raise_if_stop_requested()
    pyautogui = require_pyautogui()
    point = resolve_point(config, name)
    timing = config["timing"]
    mouse_move_seconds = float(timing.get("mouse_move_seconds", 0.03))
    pre_click_delay_seconds = float(timing.get("pre_click_delay_seconds", 0.02))
    click_hold_seconds = float(timing.get("click_hold_seconds", 0.03))

    logging.info("Clicking %s at %s", name, point)
    pyautogui.moveTo(*point, duration=mouse_move_seconds)
    sleep(pre_click_delay_seconds)
    raise_if_stop_requested()
    pyautogui.mouseDown(*point, button="left")
    sleep(click_hold_seconds)
    pyautogui.mouseUp(*point, button="left")
    raise_if_stop_requested()


def pause(config, key):
    seconds = float(config["timing"][key])
    if seconds > 0:
        logging.info("Waiting %.2fs", seconds)
        sleep(seconds)


def transition_pause(config):
    pause(config, "transition_delay_seconds")


def run_initial_navigation(config):
    logging.info("Running one-time initial navigation")
    for name in INITIAL_CLICK_NAMES:
        click(config, name)
        transition_pause(config)


def run_cycle(config):
    logging.info("Clicking start")
    click(config, "start")
    transition_pause(config)

    for name in ACTION_CLICK_NAMES:
        click(config, name)
        transition_pause(config)

    logging.info("Clicking ok")
    click(config, "ok")
    pause(config, "cycle_buffer_seconds")


def test_click(config, name):
    click(config, name)
