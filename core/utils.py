
import os.path
import paho.mqtt.client as mqtt
import xml.etree.ElementTree as et
from core.machine import ttyUSBFinder
from core.strucs import argsParser


FLD_CMDS = "cmds"
with open("/etc/hostname", "r") as f:
   ETC_HOSTNAME = f.read().strip()


class utils(object):

   @staticmethod
   def save_channel_cmd(msg: mqtt.MQTTMessage):
      # -- rpi3-3relay/gpio/25/settings/cmd --
      try:
         arr = msg.topic.split("/")
         if arr[1] != "gpio":
            pass
         # host = arr[0]
         pin = arr[2]
         if not os.path.exists(FLD_CMDS):
            raise FileNotFoundError(FLD_CMDS)
         buff = msg.payload.decode(encoding="UTF-8")
         file_name = f"pin{pin}_cmd.json"
         with open(f"cmds/{file_name}", "w+") as f:
            f.write(buff)
      except IOError as e:
         print(e)
      except Exception as e:
         print(e)

   @staticmethod
   def etc_hostname():
      return ETC_HOSTNAME

   @staticmethod
   def pin_bool_val(anyval) -> bool:
      if anyval not in ["on", "off", "1", "0", 1, 0]:
         return False
      if anyval in ["off", "0", 0]:
         return False
      if anyval in ["on", "1", 1]:
         return True

   @staticmethod
   def conf_xml(path: str) -> et.ElementTree:
      if not os.path.exists(path):
         raise FileNotFoundError(path)
      xmldoc = et.parse(path)
      return xmldoc

   @staticmethod
   def ttyusb(ap: argsParser):
      ttydev = ap.get_item("port")
      path = ap.get_item("path")
      if ttydev == "":
         finder: ttyUSBFinder = ttyUSBFinder()
         ttydev = finder.find_by_path(path)
      if ttydev in [None, False]:
         raise SystemError(f"CanNotLocateUSBDevice:[ {ttydev} : {path} ]")
      print(f"\tusing ttydev:[ {ttydev} : {path} ]")
      return ttydev
