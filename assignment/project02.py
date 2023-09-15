"""
use two simultaneously running threads to:

* read Photocell periodically and save to JSON file
* code similar to your project01.py in a second thread simultaneously
"""

import machine
import time
import _thread
import json
import os
import sys

import project01

# project01.py also needs to be copied to the Pico

is_micropython = sys.implementation.name == "micropython"

if not is_micropython:
    import os.path

def get_params(param_file: str) -> tuple[float, int]:
    """Reads parameters from a JSON file."""

    if not is_regular_file(param_file):
        raise OSError(f"File {param_file} not found")

    with open(param_file, "r") as f:
        params = json.load(f)

    return params["sample_ms"], params["on_ms"]

def is_regular_file(path: str) -> bool:
    """Checks if a regular file exists."""

    if not is_micropython:
        return os.path.isfile(path)

    S_IFREG = 0x8000

    try:
        return bool(os.stat(path)[0] & S_IFREG)
    except OSError:
        return False


def photocell_logger(N: int, sample_interval_s: float) -> None:
    """
    get raw uint16 values from photocell N times and save to JSON file

    Parameters
    ----------

    N: int
        number of samples to take
    """

    print("start light measurement thread")

    adc = machine.ADC(28)

    values: list[int] = []

    start_time: tuple[int] = time.localtime()

    for _ in range(N):
        values.append(adc.read_u16())
        time.sleep(sample_interval_s)

    end_time: tuple[int] = time.localtime()
    # please also log the end_time and sample interval in the JSON file
    #  i.e. two additional key, value in the dict

    data = {
        "light_uint16": values,
        "start_time": start_time,
    }

    now: tuple[int] = time.localtime()

    now_str = "-".join(map(str, now[:3])) + "T" + "_".join(map(str, now[3:6]))
    filename = f"proj2-light-{now_str}.json"

    print("light measurement done: write", filename)

    project01.write_json(filename, data)


def blinker_response_game(N: int) -> None:
    # %% setup input and output pins
    led = machine.Pin("LED", machine.Pin.OUT)
    button1 = machine.Pin(16, machine.Pin.IN, machine.Pin.PULL_UP)
    button2 = machine.Pin(20, machine.Pin.IN, machine.Pin.PULL_UP)

    sample_ms, on_ms = get_params("project02.json")

    t1: list[float | None] = []
    t2: list[float | None] = []

    project01.blinker(3, led)

    for i in range(N):
        time.sleep(project01.random_time_interval(0.5, 5.0))

        led.high()

        tic = time.ticks_ms()
        t01 = None
        t02 = None
        while time.ticks_diff(time.ticks_ms(), tic) < on_ms:
            if button1.value() == 0:
                t01 = time.ticks_diff(time.ticks_ms(), tic)
                led.low()
            if button2.value() == 0:
                t02 = time.ticks_diff(time.ticks_ms(), tic)
                break
        t1.append(t01)
        t2.append(t02)

        led.low()

    project01.blinker(5, led)

    project01.scorer(t1)
    project01.scorer(t2)


_thread.start_new_thread(photocell_logger, (10, 0.5))
blinker_response_game(5)

