
import os
from core.machine import ENV_x86_64

if os.uname()[4] == ENV_x86_64:
   from core.rpisim.GPIO import GPIO as gpio
else:
   import RPi.GPIO as gpio
