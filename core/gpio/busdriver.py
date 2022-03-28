
import queue
import typing as t, threading, time
import xml.etree.ElementTree as et
from core.hostgpioxml import hostGpioXml
from core.strucs import argsParser


LOOP_DELAYms = 2000


class busDriver(threading.Thread):

   @staticmethod
   def init_start(mqtt_que: queue.SimpleQueue):
      pass

   def __init__(self, _type: str, mqtt_que: queue.SimpleQueue):
      self.bustype = _type
      self.mqtt_que = mqtt_que
      thread_name = f"omms_{self.bustype.lower()}_gpio_thread"
      super().__init__(name=thread_name)
      self.xmldoc = hostGpioXml()
      self.driver_buses: t.List[et.Element] = \
         self.xmldoc.driver_bus_by_type(self.bustype.lower())
      # -- runtime info --
      self.busid: int = 0
      self.nodeid: int = 0

   def print_info(self):
      print(f"\n\t[ busDriverThread: {self.name} ]\n")

   def run(self) -> None:
      pass

   def loop_delay_secs(self, dts_ms: int) -> float:
      diff = self.epoch_ms() - dts_ms
      return (LOOP_DELAYms - diff) / 1000

   def epoch_ms(self) -> int:
      return int(time.time_ns() / 1000000)

   def __process_bus_node_cmds__(self, bus_ap: argsParser
      , node_ap: argsParser, bnode_pins: t.List[et.Element]):
      pass

   def __init_bus_node_pins__(self):
      pass

   def __on_each_bus__(self, busxml: et.Element):
      bus_ap: argsParser = argsParser(busxml)
      self.busid = int(bus_ap.get_item("id"))
      # -- for each busnode on the bus --
      def on_node(slf, node):
         try:
            node_ap: argsParser = argsParser(node)
            slf.nodeid = int(node_ap.get_item("id"))
            node_pins: t.List[et.Element] = node.findall("pins/pin")
            slf.__process_bus_node_cmds__(bus_ap, node_ap, node_pins)
         except Exception as e:
            print(e)
      # -- on each bus node --
      for bnode in busxml.findall("node"):
         on_node(self, bnode)
   # - - - -

   def insert_into_mqtt_que(self, obj: object):
      self.mqtt_que.put(obj)
