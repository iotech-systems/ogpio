
import typing as t
import xml.etree.ElementTree as et
from core.utils import utils


RELAYS_CONFXML_PATH = "conf/relays.xml_delete"


class relaysBot(object):

   def __init__(self, confxml_path: str):
      self.confxml_path = confxml_path
      self.xmldoc: et.ElementTree = utils.conf_xml(self.confxml_path)
      self.devices: [t.List[et.Element], None] = None

   def load_conf(self):
      xpath = "modbus/devices/device"
      self.devices = self.xmldoc.findall(xpath)

   def run(self):
      self.__start__()

   def __start__(self):
      for device in self.devices:
         self.__per_device__(device)

   def __per_device__(self, device: et.Element):
      self.__mqtt_subscribe__()

   def __mqtt_subscribe__(self):
      xpath = "modbus/devices/device/controller/broker"
      xml = self.xmldoc.find(xpath)
      ip = xml.attrib["ip"]
      uid = xml.attrib["uid"]
      pwd = xml.attrib["pwd"]


   def __on_mqtt_message__(self, clt, udata, msg):
      pass
