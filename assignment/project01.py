"""
Response time - single-threaded
"""

from machine import Pin
import time
import random
import json
import os
import sys

is_micropython = sys.implementation.name == "micropython"

if not is_micropython:
    import os.path

def get_params(param_file: str) -> tuple[int, float, int]:
    """Reads parameters from a JSON file."""

    if not is_regular_file(param_file):
        raise OSError(f"File {param_file} not found")

    with open(param_file, "r") as f:
        params = json.load(f)

    return params["N"], params["sample_ms"], params["on_ms"]

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


def blinker(N: int, led: Pin) -> None:
    # %% let user know game started / is over

    for _ in range(N):
        led.high()
        time.sleep(0.1)
        led.low()
        time.sleep(0.1)


def write_json(json_filename: str, data: dict) -> None:
    """Writes data to a JSON file.

    Parameters
    ----------

    json_filename: str
        The name of the file to write to. This will overwrite any existing file.

    data: dict
        Dictionary data to write to the file.
    """

    with open(json_filename, "w") as f:
        json.dump(data, f)


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
    filename = f"proj1-{now_str}.json"

    print("write", filename)

    write_json(filename, data)


if __name__ == "__main__":
    # using "if __name__" allows us to reuse functions in other script files
    N, sample_ms, on_ms = get_params("project01.json")
    led = Pin("LED", Pin.OUT)
    button = Pin(16, Pin.IN, Pin.PULL_UP)

    t: list[int | None] = []

    blinker(3, led)

    for i in range(N):
        time.sleep(random_time_interval(0.5, 5.0))

        led.high()

        tic = time.ticks_ms()
        t0 = None
        while time.ticks_diff(time.ticks_ms(), tic) < on_ms:
            if button.value() == 0:
                t0 = time.ticks_diff(time.ticks_ms(), tic)
                led.low()
                break
        t.append(t0)

        led.low()

    blinker(5, led)

    scorer(t)

