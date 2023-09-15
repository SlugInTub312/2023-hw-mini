
## Exercise 01:

1. Before running the program, I think the program will take approximately 10 seconds to run. There is a delay of 0.1 seconds and there are 2 delays in the loop that runs N = 50 times.
50 * 0.1 * 2 = 10
The program printed out: LED task done in 10.003 sec
My answer was very close to the actual time it took to run the program - only off by 0.003 seconds.

2. The “int” and “float” notation provides hints about the expected data types of variables and function arguments. Type hints help document the expected type of the variable/function argument to make it clear that the variable/function argument is of that specific data type. 
<br /><br />N: int = 50 means the variable N is declared as an integer with value of 50
<br />delay: float = 0.1 means the variable delay is declared as a float with value of 0.1
<br /><br />However, MicroPython won’t enforce type hints/function and variable type annotations and can still run if removed or incorrect. It’s primarily used for human readability and potentially for use with code analysis tools.

3. time.ticks_diff(toc, tic) implements modular (or more specifically, ring) arithmetic to produce correct results even for wrap-around values. Using toc-tic may produce incorrect results in the case of wrap-around.
<br />ex: When using toc-tic on a 12-hour clock, after the 13th hour, it’ll seem that only 1 hour has passed which is incorrect.
<br />Therefore, time.ticks_diff(toc, tic) is a more robust and platform independent method of calculating time differences.

## Exercise 02:

1. I think that we use a file for parameter storage instead of accepting the parameters as user input because it will allow for persistent storage of configuration settings across system reboots or power cycles - embedded system configurations need to survive restarts.
Additionally, users can easily change parameters without recompiling or reprogramming the embedded system which can be advantageous if the system needs to adapt to different scenarios or configurations.

2. We might prefer to use a JSON file to store parameters instead of hard-coding values in the Python script because if configuration settings / backend databases migrate or change, the Python script may break / not run. Putting parameters in a configuration file will provide for greater flexibility and maintainability compared to hard-coding values directly.
Additionally, sensitive or confidential configuration data such as API keys or passwords can be stored in a separate, restricted-access JSON file, enhancing security if needed.

3. The exercise02.py file appears to be designed to run in both MicroPython and regular Python environments. While os.path.isfile() is a standard Python function, it is not available in MicroPython. By encapsulating the file existence check in the is_regular_file() function, file checks are performed in a way that works consistently across both environments.
If it is for Python, we will check the file path using os.path.isfile(path) and if it is MicroPython, the file check is performed in a different way since os.path.isfile(path) is not supported. (MicroPython does not have all of the extensive libraries that Python has — will give error: Module Not Found)

## Exercise 03:

1. The more we increased the “sample_ms” in exercise3.json on the Pico, the more inaccurate the system was at decoding the morse code. It appears that it is having more and more trouble distinguishing between dots and dashes (short and long presses) since the sampling time is too high. 

## Exercise 04:

Using the photocell assuming that shining a flashlight on the photocell at a reasonable distance (not too close because then it’ll be covered by the shadow/device) is considered “in bright light” and covered by cupped hand on all sides as “in dark room,” the max_bright and min_bright values are:
<br />max_bright = 45000
<br />min_bright = 100
