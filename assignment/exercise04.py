"""
Use analog input with photocell
"""

import time
import machine
import json
import os
import sys

is_micropython = sys.implementation.name == "micropython"

if not is_micropython:
    import os.path


led = machine.Pin("LED", machine.Pin.OUT)
adc = machine.ADC(28)

blink_period = 0.1

def get_params(param_file: str) -> dict:
    """Reads parameters from a JSON file."""

    if not is_regular_file(param_file):
        raise OSError(f"File {param_file} not found")

    with open(param_file) as f:
        params = json.load(f)

    return params

def is_regular_file(path: str) -> bool:
    """Checks if a regular file exists."""

    if not is_micropython:
        return os.path.isfile(path)

    S_IFREG = 0x8000

    try:
        return os.stat(path)[0] & S_IFREG != 0
    except OSError:
        return False

params = get_params("exercise04.json")
max_bright = params.get("max_bright")
min_bright = params.get("min_bright")

while True:
    value = adc.read_u16()
    #print(value)
    # %% need to clip duty cycle to range [0, 1]

    duty_cycle = (value - min_bright) / (max_bright - min_bright)
    # this equation will give values outside the range [0, 1]
    
    # %% clip duty cycle to range [0, 1]
    if duty_cycle < 0:
        duty_cycle = 0
    elif duty_cycle > 1:
        duty_cycle = 1
        
    print(duty_cycle)

    led.high()
    time.sleep(blink_period * duty_cycle)
    led.low()
    time.sleep(blink_period * (1 - duty_cycle))
