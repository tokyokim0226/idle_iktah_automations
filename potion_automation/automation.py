import logging

from config import resolve_point
from safety import raise_if_stop_requested, sleep


def require_pyautogui():
    try:
        import pyautogui
    except ModuleNotFoundError as error:
        raise ModuleNotFoundError(
            "pyautogui is not installed. Run: pip install -r requirements.txt"
        ) from error

    return pyautogui


def click(config, name):
    raise_if_stop_requested()
    pyautogui = require_pyautogui()
    point = resolve_point(config, name)
    timing = config["timing"]
    mouse_move_seconds = float(timing.get("mouse_move_seconds", 0.15))
    pre_click_delay_seconds = float(timing.get("pre_click_delay_seconds", 0.1))
    click_hold_seconds = float(timing.get("click_hold_seconds", 0.08))

    logging.info("Clicking %s at %s", name, point)
    pyautogui.moveTo(*point, duration=mouse_move_seconds)
    sleep(pre_click_delay_seconds)
    raise_if_stop_requested()
    pyautogui.mouseDown(*point, button="left")
    sleep(click_hold_seconds)
    pyautogui.mouseUp(*point, button="left")
    raise_if_stop_requested()


def long_click(config, name, duration):
    raise_if_stop_requested()
    pyautogui = require_pyautogui()
    point = resolve_point(config, name)
    timing = config["timing"]
    mouse_move_seconds = float(timing.get("long_click_mouse_move_seconds", 0.15))
    pre_hold_delay_seconds = float(timing.get("long_click_pre_hold_delay_seconds", 0.25))

    logging.info("Long-clicking %s at %s for %.2fs", name, point, duration)
    pyautogui.moveTo(*point, duration=mouse_move_seconds)
    sleep(pre_hold_delay_seconds)

    try:
        pyautogui.mouseDown(button="left")
        sleep(duration)
    finally:
        pyautogui.mouseUp(button="left")
    raise_if_stop_requested()


def test_long_click(config, name, duration):
    pyautogui = require_pyautogui()
    point = resolve_point(config, name)
    logging.info("Testing long-click on %s at %s", name, point)
    logging.info("Move starts now; press will begin after a short pause.")
    pyautogui.moveTo(*point, duration=0.25)
    sleep(1.0)
    long_click(config, name, duration)


def test_current_click():
    pyautogui = require_pyautogui()
    point = pyautogui.position()
    logging.info("Testing click at current cursor position: (%s, %s)", point.x, point.y)
    sleep(1.0)
    pyautogui.mouseDown(button="left")
    sleep(0.08)
    pyautogui.mouseUp(button="left")


def test_current_long_click(duration):
    pyautogui = require_pyautogui()
    point = pyautogui.position()
    logging.info(
        "Testing long-click at current cursor position: (%s, %s) for %.2fs",
        point.x,
        point.y,
        duration,
    )
    sleep(1.0)
    try:
        pyautogui.mouseDown(button="left")
        sleep(duration)
    finally:
        pyautogui.mouseUp(button="left")


def pause(config, key):
    seconds = float(config["timing"][key])
    logging.info("Waiting %.2fs", seconds)
    sleep(seconds)


def transition_pause(config):
    pause(config, "transition_delay_seconds")


def make_39_cheap(config):
    timing = config["timing"]
    logging.info("Opening cheap potion quantity menu")
    long_click(config, "play", float(timing["long_press_seconds"]))
    transition_pause(config)

    logging.info("Selecting quantity 39")
    click(config, "make_39")


def select_haste_tea(config):
    logging.info("Opening potion selector")
    click(config, "swap")
    transition_pause(config)

    logging.info("Selecting Haste Tea")
    click(config, "haste_tea")
    transition_pause(config)


def make_1_haste(config):
    timing = config["timing"]
    logging.info("Opening Haste Tea quantity menu")
    long_click(config, "play", float(timing["long_press_seconds"]))
    transition_pause(config)

    logging.info("Selecting quantity 1")
    click(config, "make_1")


def select_cheap_potion(config):
    logging.info("Opening potion selector")
    click(config, "swap")
    transition_pause(config)

    logging.info("Returning to cheap potion")
    click(config, "cheap_potion")
    transition_pause(config)


def initialize_cheap_potion(config):
    logging.info("Initializing run by selecting cheap potion")
    select_cheap_potion(config)


def run_cycle(config):
    make_39_cheap(config)

    logging.info("Crafting cheap potion batch")
    pause(config, "cheap_potion_wait_seconds")

    select_haste_tea(config)
    make_1_haste(config)

    logging.info("Crafting Haste Tea")
    pause(config, "haste_tea_wait_seconds")

    select_cheap_potion(config)
    pause(config, "cycle_buffer_seconds")
