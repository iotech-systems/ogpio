
import os, re
from core.hostgpioxml import hostGpioXml


ENV_x86_64 = "x86_64"


gpioconf = hostGpioXml()
ETC_HOSTNAME = gpioconf.host_name()
if ETC_HOSTNAME == "ETC_HOSTNAME":
   with open("/etc/hostname", "r") as f:
      ETC_HOSTNAME = f.read().strip()


print(f"\n\tETC_HOSTNAME: {ETC_HOSTNAME}\n")


class ttyUSBFinder(object):

   def __init__(self):
      pass

   def find_by_path(self, path: str) -> [None, str]:
      cmd = f"ls /dev/serial/by-path/ -la | grep {path}"
      buff = os.popen(cmd).read()
      patt = r"(ttyUSB[0-9]{1,2})"
      m = re.search(patt, buff)
      dev = m.group() if (m is not None) and (len(m.groups()) == 1) else None
      if dev is None:
         return dev
      # -- return dev path --
      return f"/dev/{dev}"
      # -- run --
