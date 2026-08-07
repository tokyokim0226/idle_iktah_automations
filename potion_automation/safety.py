import logging
import threading
import time


_stop_event = threading.Event()
_listener = None


class AutomationStopped(RuntimeError):
    pass


def request_stop():
    _stop_event.set()


def stop_requested():
    return _stop_event.is_set()


def raise_if_stop_requested():
    if stop_requested():
        raise AutomationStopped("Stop requested")


def sleep(seconds, interval=0.05):
    end_time = time.time() + float(seconds)
    while time.time() < end_time:
        raise_if_stop_requested()
        time.sleep(min(interval, end_time - time.time()))
    raise_if_stop_requested()


def start_escape_listener():
    global _listener

    if _listener is not None:
        return

    try:
        from pynput import keyboard
    except ModuleNotFoundError as error:
        raise ModuleNotFoundError("pynput is not installed. Run: uv sync") from error

    def on_press(key):
        if key == keyboard.Key.esc:
            logging.warning("Escape pressed. Stopping automation.")
            request_stop()
            return False

        return True

    _listener = keyboard.Listener(on_press=on_press)
    _listener.daemon = True
    _listener.start()
    logging.info("Escape kill switch enabled")
