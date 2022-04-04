
import os.path, typing as t
import xml.etree.ElementTree as et
from core.strucs import driverTypes
from core.utils import utils


class hostGpioXml(object):

   XML_FILE_PATH = "conf/hosts-gpio.xml"

   def __init__(self):
      if not os.path.exists(hostGpioXml.XML_FILE_PATH):
         raise FileNotFoundError(f"XmlConfNotFound: {hostGpioXml.XML_FILE_PATH}")
      hostname = utils.etc_hostname()
      self.xmldoc = et.parse(hostGpioXml.XML_FILE_PATH)
      xpath = f"host[@name=\"{hostname}\"]"
      self.hostgpio = et.parse(xpath)

   def drivers(self, _type=driverTypes.MQTT) -> t.List[et.Element]:
      xpath = f"gpio/driver[@type=\"{_type}\"]"
      arr: t.List[et.Element] = self.hostgpio.findall(xpath)
      return arr

   def driver_bus_by_type(self, _type: str) -> t.List[et.Element]:
      xpath = f"gpio/driver/bus[@type=\"{_type}\"]"
      arr: t.List[et.Element] = self.hostgpio.findall(xpath)
      return arr

   def host_name(self):
      xml = self.hostgpio.getroot()
      if xml is None:
         return ""
      # -- do --
      return xml.attrib["name"]
