
from core.machine import ttyUSBFinder

o: ttyUSBFinder = ttyUSBFinder()
x = o.find_by_path("0-usb-0:1.1.4:1.0-port0")
print(x)
