
import os.path, typing as t
import xml.etree.ElementTree as et
from core.strucs import driverTypes


with open("/etc/hostname", "r") as f:
   ETC_HOSTNAME = f.read().strip()


class hostGpioXml(object):

   XML_FILE_PATH = "conf/hostsgpio.xml"

   def __init__(self):
      if not os.path.exists(hostGpioXml.XML_FILE_PATH):
         raise FileNotFoundError(f"XmlConfNotFound: {hostGpioXml.XML_FILE_PATH}")
      doc: et.ElementTree = et.parse(hostGpioXml.XML_FILE_PATH)
      self.xmldoc: [None, et.ElementTree] = None
      if doc is None:
         pass
      self.xmldoc = doc.getroot()
      xpath = f"host[@name=\"{ETC_HOSTNAME}\"]"
      self.hostgpio = self.xmldoc.find(xpath)
      if self.hostgpio is None:
         print(f"NoHostGpioFound: {ETC_HOSTNAME}")

   def drivers(self, _type=driverTypes.MQTT) -> t.List[et.Element]:
      xpath = f"gpio/driver[@type=\"{_type}\"]"
      arr: t.List[et.Element] = self.hostgpio.findall(xpath)
      return arr

   def driver_bus_by_type(self, _type: str) -> t.List[et.Element]:
      xpath = f"gpio/driver/bus[@type=\"{_type}\"]"
      arr: t.List[et.Element] = self.hostgpio.findall(xpath)
      return arr

   def host_name(self):
      if self.hostgpio is None:
         return ""
      # -- do --
      return self.hostgpio["name"]
