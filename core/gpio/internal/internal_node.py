
import typing as t, time
import xml.etree.ElementTree as et
from core.strucs import argsParser
from core.gpio.bus.busnode import busNode
from core.gpio.anygpio import gpio
from core.utils import utils


class internalNode(busNode):

   def __init__(self, nodexml: et.Element, busargs: argsParser):
      super().__init__()
      self.nodexml = nodexml
      self.busargs = busargs
      self.selfargs = argsParser(self.nodexml)

   def init_node(self, **kwargs):
      pass

   def init_node_pins(self, **kwargs):
      try:
         pins: t.List[et.Element] = self.nodexml.findall("pins/pin")
         for pin in pins:
            self.__init_pin__(pin)
            time.sleep(0.20)
      except Exception as e:
         print(e)

   def __init_pin__(self, pin):
      pinid = int(pin.attrib["id"])
      tmpval = pin.attrib["onstart"]
      direction = pin.attrib["direction"]
      if direction.upper() == "OUT":
         gpio.setup(pinid, gpio.OUT)
      onstart: bool = utils.pin_bool_val(tmpval)
      tmpval = pin.attrib["inverted"]
      if tmpval.upper() in ["Y", "YES"]:
         onstart = (not onstart)
      gpio.output(int(pinid), int(onstart))
