"""
use two simultaneously running threads to:

* read Photocell periodically and save to JSON file
* code similar to your project01.py in a second thread simultaneously
"""

import machine
import time
import random
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

def random_time_interval(tmin: float, tmax: float) -> float:
    """return a random time interval between max and min"""
    return random.uniform(tmin, tmax)

def write_json(json_filename: str, data: dict) -> None:
    """Writes data to a JSON file.

    Parameters
    ----------

    json_filename: str
        The name of the file to write to. This will overwrite any existing file.

    data: dict
        Dictionary data to write to the file.
    """

    with open(json_filename, "a") as f:
        json.dump(data, f)
        
def blinker(N: int, led: Pin) -> None:
    # %% let user know game started / is over

    for _ in range(N):
        led.high()
        time.sleep(0.1)
        led.low()
        time.sleep(0.1)
        
def scorer(t: list[int | None]) -> None:
    # %% collate results
    misses = t.count(None)
    total_flashes = len(t)
    non_misses = total_flashes - misses
    
    print(f"You missed the light {misses} / {len(t)} times")

    t_good = [x for x in t if x is not None]

    print(t_good)

    # add key, value to this dict to store the minimum, maximum, average response time
    # and score (non-misses / total flashes) i.e. the score a floating point number
    # is in range [0..1]
    if t_good:
        min_response_time = min(t_good)
        max_response_time = max(t_good)
        average_response_time = sum(t_good) / len(t_good)
        score = non_misses / total_flashes
    else:
        min_response_time = 0
        max_response_time = 0
        average_response_time = 0
        score = 0.0
    
    # dictionary to store the results
    data = {
        "min_response_time": min_response_time,
        "max_response_time": max_response_time,
        "average_response_time": average_response_time,
        "score": score,
    }

    # %% make dynamic filename and write JSON

    now: tuple[int] = time.localtime()

    now_str = "-".join(map(str, now[:3])) + "T" + "_".join(map(str, now[3:6]))
    filename = f"proj2-{now_str}.json"

    print("write", filename)

    write_json(filename, data)

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

    write_json(filename, data)


def blinker_response_game(N: int) -> None:
    # %% setup input and output pins
    led = machine.Pin("LED", machine.Pin.OUT)
    button1 = machine.Pin(16, machine.Pin.IN, machine.Pin.PULL_UP)
    button2 = machine.Pin(20, machine.Pin.IN, machine.Pin.PULL_UP)

    sample_ms, on_ms = get_params("project02.json")

    t1: list[float | None] = []
    t2: list[float | None] = []

    blinker(3, led)

    for i in range(N):
        time.sleep(random_time_interval(0.5, 5.0))

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

    blinker(5, led)

    scorer(t1)
    scorer(t2)


_thread.start_new_thread(photocell_logger, (10, 0.5))
blinker_response_game(5)

