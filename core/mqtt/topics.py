
import typing as t
import xml.etree.ElementTree as et
from core.gpio.gpioUtils import gpioUtils
from core.xmlattribs import channelElm
from core.strucs import argsParser


class topicKeys(object):

   CHANNEL_CMD = "CHANNEL_CMD"
   GPIO_CONF = "GPIO_CONF"


# __sub_channel_root__ = "omms/[hostname]/gpio/channels/[00-99]"
__sub_channel_root__ = "omms/%s/gpio/channels/%02d"
__sub_channel_topics__ = {topicKeys.CHANNEL_CMD: f"{__sub_channel_root__}/cmd"
   , topicKeys.GPIO_CONF: f"{__sub_channel_root__}/conf"}

# __sub_modbus_root__ = "omms/[hostname]/gpio/modbus/[000-255: modbus address]/relays/[00-99]: relay id"
__sub_modbus_root__ = "omms/%s/gpio/modbus/%03d/relays/%02d"
__sub_modbus_topics__ = {topicKeys.CHANNEL_CMD: f"{__sub_modbus_root__}/cmd"
   , topicKeys.GPIO_CONF: f"{__sub_modbus_root__}/conf"}


class topics(object):

   @staticmethod
   def system_topics(gpio_chns: et.Element, gpio_modbus: et.Element) -> []:
      arrout = []
      # -- create channel topics --
      channels = gpio_chns.find("channels")
      host = channels.attrib["hostname"]
      __channels: t.List[et.Element] = channels.findall("channel")
      for channel in __channels:
         channel_id = int(channel.attrib[channelElm.ID])
         _ts_gpio = topics.sub_channel_topics(host, channel_id)
         arrout.extend(_ts_gpio)
      # -- create modbus topics --
      __devices: t.List[et.Element] = gpio_modbus.findall("devices")
      for device in __devices:
         print(device)
      # -- return full topic list --
      return arrout

   @staticmethod
   def create_pin_topic_list(driver: et.Element, hostname: str) -> []:
      # -- create topics object --
      _topics_ = topics()
      # -- bus type; get enabled buses --
      _tout: [] = []
      xpath = "bus[@enabled=\"1\"]"
      buses: t.List[et.Element] = driver.findall(xpath)
      for bus in buses:
         _t = _topics_.__per_bus__(hostname, bus)
         _tout.extend(_t)
      # -- return topic list --
      return _tout

   @staticmethod
   def sub_channel_topics(host: str, cid: int) -> []:
      arrout = []
      # -- build gpio channel topics --
      for key in __sub_channel_topics__.keys():
         topic = __sub_channel_topics__[key]
         arrout.append((topic % (host, cid), 0))
      # -- return topics array --
      return arrout

   @staticmethod
   def sub_modbus_topics(host, modbus_address, relay_id) -> []:
      arrout = []
      # -- build gpio modbus topics --
      for key in __sub_modbus_topics__.keys():
         topic = __sub_modbus_topics__[key]
         arrout.append((topic % (host, modbus_address, relay_id), 0))
      return arrout

   @staticmethod
   def pub_topic_channel_pin_event(host: str, chn_id: int, pin_id: int, event: str):
      return f"omms/%s/gpio/channels/%02d/pins/%02d/event/%s" % (host, chn_id, pin_id, event)

   @staticmethod
   def pub_topic_modbus_relay_event(host: str, chn_id: int, pin_id: int, event: str):
      return f"omms/%s/gpio/channels/%02d/pins/%02d/event/%s" % (host, chn_id, pin_id, event)

   def __per_bus__(self, hostname, bus: et.Element):
      # -- basic info --
      _tout: [] = []
      bus_ap: argsParser = argsParser(bus)
      busid = int(bus_ap.dictionary["id"])
      bustype = bus.attrib["type"]
      # -- per node --
      nodes = bus.findall("node")
      for node in nodes:
         arr = self.__per_node__(hostname, bustype, busid, node)
         _tout.extend(arr)
      # -- --
      return _tout

   """
      btype = kwargs["bustype"]
      bid = int(kwargs["busid"])
      nodeid = int(kwargs["nodeid"])
      pinid = int(kwargs["pinid"])
   """
   def __per_node__(self, hostname: str, bustype, busid: int, node: et.Element):
      try:
         _tout = []
         node_ap: argsParser = argsParser(node)
         pins: t.List[et.Element] = node.findall("pins/pin")
         # -- for each pin --
         for pin in pins:
            pinid = int(pin.attrib["id"])
            adr = int(node_ap.dictionary["address"])
            pin_topic = gpioUtils.pin_topic(hostname, bustype, busid, adr, pinid)
            _tout.append((pin_topic, 0))
         # -- return topic list --
         return _tout
      except Exception as e:
         print(e)
